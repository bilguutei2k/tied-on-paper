"""Assemble narrated drafts: the long film and the shorts, with captions.

    python3 studio/tools/assemble.py studio/episodes/<id> [film short-a ...] [--jobs 4]

Reads EDIT.json (which lines play over which scene, and the word that starts
each animation beat) and renders/audio/narration.json (from narrate.py). For
each shot it lays the lines out with fixed gaps, turns the cues into a timemap
and renders the scene with studio/render/render.mjs --timemap. The shots are
joined with hard cuts; a "wipe" shot gets the design system's panel wipe (a
Night or Paper panel across the frame in 450 ms, centred on the cut). The
narration is placed on one track and normalised to -14 LUFS (-1 dBTP), the
level YouTube plays at. Writes renders/draft/<deliverable>.mp4, a matching
.srt caption file and <deliverable>.json with every shot's timing and hashes.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RENDER = ROOT / "studio/render/render.mjs"
FPS = 30
SIZE = {"landscape": (1920, 1080), "vertical": (1080, 1920)}
PANEL = {"paper": "0x1C1916", "night": "0xF3EBDD"}      # the panel contrasts with the incoming scene
RATE = 24000
PUNCT = "\"'“”‘’.,:;?!()"


def find_word(line, word, nth=1):
    target = word.strip(PUNCT).lower()
    seen = 0
    for w in line["words"]:
        if w["w"].strip(PUNCT).lower() == target:
            seen += 1
            if seen == nth:
                return w
    raise KeyError("word %r not in line: %s" % (word, line["written"]))


def plan_shot(shot, narration, edit):
    """Line start times within the shot, its duration, and the timemap anchors."""
    scene_id, indices = shot["lines"]
    lines = [narration["scenes"][scene_id]["lines"][i] for i in indices]
    # Optional half-open written-word ranges split long lines without editing
    # STORY.md, synthesising fragments, or changing the narration cache.
    if "word_ranges" in shot:
        if len(shot["word_ranges"]) != len(lines):
            raise ValueError("word_ranges must match the shot's lines")
        lines = [slice_line(line, bounds) if bounds is not None else line
                 for line, bounds in zip(lines, shot["word_ranges"])]
    t, starts = shot.get("lead", edit["lead"]), []
    for i, line in enumerate(lines):
        starts.append(t)
        t += line["duration"] + (edit["gap"] if i + 1 < len(lines) else 0)
    duration = t + shot.get("tail", edit["tail"])
    reveals = []
    for cue in shot.get("reveals", []):
        at = duration + 1 if cue.get("hidden") else cue_time(cue, lines, starts)
        reveals.append({"selector": cue["selector"], "at": round(max(0, at), 3),
                        **({"hide_after": True} if cue.get("hide_after") else {})})
    if "hold" in shot:                                  # a still: the scene frozen at one moment (a recap)
        return {"lines": lines, "starts": starts, "duration": round(duration, 3),
                "anchors": [[shot["hold"], 0.0], [shot["hold"] + 0.05, round(duration + 60, 3)]],
                "reveals": reveals}
    anchors = []
    for cue in shot["cues"]:
        at = round(max(0.0, cue_time(cue, lines, starts)), 3)
        if "jump_from" in cue:
            # A named-state cut skips its unused reveal-clock hold. Equal
            # output timestamps make the cut exact without rushing motion.
            anchors.append([cue["jump_from"], at])
        anchors.append([cue["t"], at])
    if "end_t" in shot:
        # Finish this reveal, then hold below the next state's clock boundary.
        anchors.append([shot["end_t"], round(duration + 60, 3)])
    if anchors[0][1] > 0:
        anchors.insert(0, [anchors[0][0], 0.0])
    for a, b in zip(anchors, anchors[1:]):
        if b[1] < a[1] or b[0] < a[0]:
            raise ValueError("%s: cues out of order at scene t=%s" % (shot["scene"], b[0]))
    return {"lines": lines, "starts": starts, "duration": round(duration, 3), "anchors": anchors, "reveals": reveals}


def cue_time(cue, lines, starts):
    line = lines[cue["line"]]
    return starts[cue["line"]] + (find_word(line, cue["word"], cue.get("nth", 1))["start"]
                                 if "word" in cue else 0) + cue.get("offset", 0)


def slice_line(line, bounds):
    """Slice audio and captions at the same boundary between written words."""
    a, b = bounds
    words = line["words"]
    if not (isinstance(a, int) and isinstance(b, int) and 0 <= a < b <= len(words)):
        raise ValueError("invalid written-word range %r" % (bounds,))
    # Midpoints preserve inter-word silence across adjacent slices, without
    # dropping the attack of a consonant or overlapping PCM samples.
    start = (words[a - 1]["end"] + words[a]["start"]) / 2 if a else 0
    end = (words[b - 1]["end"] + words[b]["start"]) / 2 if b < len(words) else line["duration"]
    if end <= start:
        raise ValueError("word range has no timed audio: %r" % (bounds,))
    selected = [{**w, "start": round(max(0, w["start"] - start), 3),
                 "end": round(min(end - start, w["end"] - start), 3)} for w in words[a:b]]
    return {**line, "written": text_of(selected), "words": selected,
            "duration": end - start, "audio_range": [start, end]}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def render_shot(job):
    page, fmt, timemap, out = job
    tm = out.with_suffix(".timemap.json")
    tm.write_text(json.dumps(timemap) + "\n")
    dependencies = [page, RENDER]
    for relative in re.findall(r'(?:src|href)="([^"?#]+)"', page.read_text()):
        dependency = page.parent / relative
        if dependency.is_file():
            dependencies.append(dependency)
    key = hashlib.sha256(("".join(sha(p) for p in dependencies) + fmt + json.dumps(timemap)).encode()).hexdigest()
    stamp = out.with_suffix(".key")
    if out.exists() and stamp.exists() and stamp.read_text() == key:
        return out, "cached"
    subprocess.run(["node", str(RENDER), str(page), "--video", "--format", fmt, "--timemap", str(tm), "--out", str(out)],
                   check=True, capture_output=True, text=True)
    stamp.write_text(key)
    return out, json.loads(out.with_suffix(".mp4.json").read_text())["captured"]


def read_wav(path, audio_range=None):
    with wave.open(str(path)) as f:
        assert f.getframerate() == RATE and f.getnchannels() == 1 and f.getsampwidth() == 2
        if audio_range is None:
            return f.readframes(f.getnframes())
        start, end = (round(t * RATE) for t in audio_range)
        f.setpos(start)
        return f.readframes(end - start)


def build_audio(placements, duration, out):
    track = bytearray(2 * int(round(duration * RATE)))
    for at, pcm in placements:
        i = 2 * int(round(at * RATE))
        pcm = pcm[: max(0, len(track) - i)]
        track[i:i + len(pcm)] = pcm
    with wave.open(str(out), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(bytes(track))


def loudness_measure(path, true_peak=-1):
    probe = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-vn", "-af",
                            "loudnorm=I=-14:TP=%s:LRA=11:print_format=json" % true_peak, "-f", "null", "-"],
                           capture_output=True, text=True, check=True).stderr
    return json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])


def loudnorm_filter(wav, true_peak=-1, correction=0):
    m = loudness_measure(wav, true_peak)
    return ("loudnorm=I=-14:TP=%s:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true"
            % (true_peak, m["input_i"], m["input_tp"], m["input_lra"], m["input_thresh"], float(m["target_offset"]) + correction))


def calibrate_audio(final, voice, total, true_peak):
    """Check the encoded AAC, correcting dynamic loudnorm's residual offset.

    Each retry uses the original PCM and copies the picture stream. The
    requested true-peak headroom is retained through every normalization.
    """
    correction, gain = 0, 0
    for attempt in range(8):
        m = loudness_measure(final, true_peak)
        level, peak = float(m["input_i"]), float(m["input_tp"])
        if abs(level + 14) <= .15 and peak <= -1:
            return {"integrated_lufs": level, "true_peak_dbtp": peak}
        if attempt == 7:
            raise ValueError("Encoded audio outside target: %.2f LUFS / %.2f dBTP" % (level, peak))
        delta = -14 - level
        if delta < 0 or delta <= -1.1 - peak:
            # Use available encoded-peak headroom for a small, exact gain.
            gain += delta
        else:
            # A doubled residual can overshoot dynamic loudnorm's useful
            # offset range and make a peak-limited track quieter on retries.
            correction += delta
        if peak > -1:
            true_peak -= peak + 1.2
        temp = final.with_name(final.stem + ".normalizing.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final), "-i", str(voice),
                        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-af",
                        loudnorm_filter(voice, true_peak, correction) + ",volume=%sdB,aresample=48000" % gain,
                        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", "%.3f" % total,
                        "-movflags", "+faststart", str(temp)], check=True)
        temp.replace(final)


def wipe_graph(cuts, fmt, wipe, total):
    """Filter graph from [0:v] to [v]: at each cut a solid panel enters from the left, covers the cut, and
    leaves to the right, easing out like the system's settle curve."""
    w, h = SIZE[fmt]
    half, parts, last = wipe / 2, [], "[0:v]"
    ease = lambda p: "(1-pow(1-(%s),3))" % p
    for k, (t, color) in enumerate(cuts):
        a, b = t - half, t + half
        x = "if(lt(t,%.4f),-%d+%d*%s,%d*%s)" % (t, w, w, ease("(t-%.4f)/%.4f" % (a, half)), w, ease("(t-%.4f)/%.4f" % (t, half)))
        parts.append("color=c=%s:s=%dx%d:r=%d:d=%.3f[p%d]" % (color, w, h, FPS, total, k))
        parts.append("%s[p%d]overlay=x='%s':y=0:enable='between(t,%.4f,%.4f)'[w%d]" % (last, k, x, a, b, k))
        last = "[w%d]" % k
    parts.append("%snull[v]" % last)
    return ";".join(parts)


def text_of(words):
    return " ".join(w["w"] for w in words)


def split_cue(words, limit):
    """Split words into pieces of at most `limit` characters, at the comma (or else the space) that best
    balances each split."""
    if len(text_of(words)) <= limit or len(words) < 2:
        return [words]
    def cost(i):
        left, right = len(text_of(words[:i])), len(text_of(words[i:]))
        return abs(left - right) - (12 if re.search(r"[,;:]\W*$", words[i - 1]["w"]) else 0)
    i = min(range(1, len(words)), key=cost)
    return split_cue(words[:i], limit) + split_cue(words[i:], limit)


def wrap(words, width):
    """One line, or two balanced lines of at most `width` characters where possible."""
    if len(text_of(words)) <= width:
        return text_of(words)
    i = min(range(1, len(words)), key=lambda i: max(len(text_of(words[:i])), len(text_of(words[i:]))))
    return text_of(words[:i]) + "\n" + text_of(words[i:])


def captions(timed_lines, path, width=42, strict=False):
    """SRT captions: sentences, merged when short and split at commas when long, at most two lines of
    `width` characters each, timed from the spoken words."""
    def fmt(s):
        ms = int(round(s * 1000))
        return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)
    cues = []
    for offset, line in timed_lines:
        sentences, current = [], []
        for w in line["words"]:
            current.append(w)
            if re.search(r"[.?!]\W*$", w["w"]):
                sentences.append(current)
                current = []
        if current:
            sentences.append(current)
        merged = []
        for s in sentences:
            if merged and len(text_of(merged[-1] + s)) <= width:
                merged[-1] = merged[-1] + s
            else:
                merged.append(s)
        for s in merged:
            for piece in split_cue(s, 2 * width - 2):
                # A <=82-character chunk can still have no word boundary
                # that fits two 42-character rows. Keep strict captions within
                # the row limit without changing the legacy caption path.
                pieces = (split_cue(piece, width) if strict and
                          any(len(row) > width for row in wrap(piece, width).splitlines()) else [piece])
                cues.extend((offset, part) for part in pieces)
    entries = [[offset + chunk[0]["start"], offset + chunk[-1]["end"], wrap(chunk, width)] for offset, chunk in cues]
    for a, b in ([] if strict else zip(entries, entries[1:])):
        a[1] = max(a[1], min(a[0] + 1.0, b[0]))
        if b[0] - a[1] < 0.25:
            a[1] = b[0]
    path.write_text("".join("%d\n%s --> %s\n%s\n\n" % (i + 1, fmt(a), fmt(b), t) for i, (a, b, t) in enumerate(entries)))
    return len(entries)


def sequence_plans(shots, narration, edit):
    """Keep adjacent fragments of one cached line sample-contiguous.

    Picture cuts land on whole frames. The next PCM fragment starts at the
    previous fragment's exact endpoint, carrying the sub-frame difference
    into word cues and captions instead of inserting silence at the cut.
    This is opt-in; existing episode edits retain their original timing.
    """
    bridges = set()
    if edit.get("bridge_word_ranges"):
        for i, (a, b) in enumerate(zip(shots, shots[1:])):
            if (a["lines"][0] == b["lines"][0] and
                    a["lines"][1][-1] == b["lines"][1][0] and
                    a.get("word_ranges") and b.get("word_ranges") and
                    a["word_ranges"][-1] and b["word_ranges"][0] and
                    a["word_ranges"][-1][1] == b["word_ranges"][0][0]):
                bridges.add(i)
    plans, t, pcm_end = [], 0.0, 0.0
    for i, shot in enumerate(shots):
        effective = dict(shot)
        if i in bridges:
            effective["tail"] = 0
        if i - 1 in bridges:
            effective["lead"] = pcm_end - t
        plan = plan_shot(effective, narration, edit)
        plan.update(start=round(t, 6), shot=shot)
        plan["duration"] = round(plan["duration"] * FPS) / FPS
        pcm_end = t + plan["starts"][-1] + plan["lines"][-1]["duration"]
        t += plan["duration"]
        plans.append(plan)
    return plans


def assemble(episode, name, spec, edit, narration, jobs):
    out = episode / "renders/draft"
    shots_dir = out / name
    shots_dir.mkdir(parents=True, exist_ok=True)
    fmt = spec["format"]
    plans = sequence_plans(spec["shots"], narration, edit)
    for k, plan in enumerate(plans):
        plan["file"] = shots_dir / ("%02d-%s.mp4" % (k + 1, plan["shot"]["scene"]))
    total = sum(p["duration"] for p in plans)
    work = [(episode / "scenes" / (p["shot"]["scene"] + ".html"), fmt,
             {"duration": p["duration"], "anchors": p["anchors"],
              **({"narrated": True} if edit.get("settled_visuals") else {}),
              **({"reveals": p["reveals"]} if p["reveals"] else {})}, p["file"]) for p in plans]
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for path, how in pool.map(render_shot, work):
            print("  %s: %s" % (path.name, how if how == "cached" else "%s frames captured" % how))
    listing = shots_dir / "concat.txt"
    listing.write_text("".join("file '%s'\n" % p["file"].name for p in plans))
    joined = shots_dir / "joined.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(joined)],
                   check=True)
    placements, timed = [], []
    for p in plans:
        for start, line in zip(p["starts"], p["lines"]):
            placements.append((p["start"] + start, read_wav(episode / line["wav"], line.get("audio_range"))))
            timed.append((p["start"] + start, line))
    voice = shots_dir / "narration.wav"
    build_audio(placements, total, voice)
    cuts = [(p["start"], PANEL[p["shot"]["bg"]]) for p in plans if p["shot"]["in"] == "wipe"]
    final = out / (name + ".mp4")
    graph = wipe_graph(cuts, fmt, edit["wipe"], total) + ";[1:a]%s,aresample=48000[a]" % loudnorm_filter(voice, edit.get("audio_true_peak", -1))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(joined), "-i", str(voice), "-filter_complex", graph,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", "%.3f" % total,
                    "-movflags", "+faststart", str(final)], check=True)
    audio_qa = calibrate_audio(final, voice, total, edit.get("audio_true_peak", -1)) if edit.get("calibrate_loudness") else None
    n_captions = captions(timed, out / (name + ".srt"), strict=edit.get("strict_captions", False))
    record = {"deliverable": name, "title": spec.get("title"), "format": fmt, "duration": round(total, 3),
              "output_sha256": sha(final), "captions": n_captions, "narration_engine": narration["engine"],
              **({"audio_qa": audio_qa} if audio_qa else {}),
              "status": edit.get("status", "draft"),
              "story_sha256": narration["story_sha256"], "data_js_sha256": sha(episode / "scenes/data.js"),
              "shots": [{"scene": p["shot"]["scene"], "start": p["start"], "duration": p["duration"],
                         "lines": p["shot"]["lines"], "anchors": p["anchors"], "transition_in": p["shot"]["in"],
                         "speech": [{"start": round(p["start"] + start, 6),
                                     "end": round(p["start"] + start + line["duration"], 6),
                                     "written": line["written"]}
                                    for start, line in zip(p["starts"], p["lines"])],
                         **({"word_ranges": p["shot"]["word_ranges"]} if "word_ranges" in p["shot"] else {}),
                         **({"reveals": p["reveals"]} if p["reveals"] else {})} for p in plans]}
    (out / (name + ".json")).write_text(json.dumps(record, indent=1) + "\n")
    print("Wrote %s (%d:%04.1f, %d shots, %d captions)" % (final, total // 60, total % 60, len(plans), n_captions))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("episode", type=Path)
    parser.add_argument("deliverables", nargs="*")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args(argv)
    edit = json.loads((args.episode / "EDIT.json").read_text())
    narration = json.loads((args.episode / "renders/audio/narration.json").read_text())
    story = sha(args.episode / "STORY.md")
    if narration["story_sha256"] != story:
        sys.exit("STORY.md changed since the narration was generated; rerun narrate.py")
    for name in args.deliverables or list(edit["deliverables"]):
        assemble(args.episode, name, edit["deliverables"][name], edit, narration, args.jobs)


if __name__ == "__main__":
    main()
