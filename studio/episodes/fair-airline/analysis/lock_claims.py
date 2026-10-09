#!/usr/bin/env python3
"""Record an explicitly supplied owner lock, then independently recheck it.

Do not run for a preview. TITLE.json is the sole title configuration. This
command does not publish, push, synthesize speech, or alter analytical values.
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

EP = Path(__file__).resolve().parent.parent
ROOT = EP.parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--approver', required=True)
    parser.add_argument('--date', required=True)
    parser.add_argument('--title')
    args = parser.parse_args()
    if not args.approver.strip():
        parser.error('approver must be nonempty')
    try:
        date = datetime.date.fromisoformat(args.date)
        assert date.isoformat() == args.date
    except (ValueError, AssertionError):
        parser.error('date must be YYYY-MM-DD')
    title = args.title if args.title is not None else json.loads((EP/'TITLE.json').read_text())['title']
    if not title.strip() or '\n' in title or '\r' in title:
        parser.error('title must be one nonempty line')
    changed = ['CLAIMS.json', 'TITLE.json', 'STORY.md', 'analysis/claims_check.json',
               'companion/index.html', 'renders/companion/page.html', 'renders/audio/narration.json', 'PUBLIC_README.md',
               'HANDOFF.md', 'NARRATED_BUILD.md', 'scenes/README.md', 'analysis/upload-metadata.json']
    if (EP/'EPISODE.md').exists():
        changed.append('EPISODE.md')
    saved = {name: (EP/name).read_bytes() if (EP/name).exists() else None for name in changed}
    try:
        ledger = json.loads(saved['CLAIMS.json'])
        approval = {'by': args.approver.strip(), 'date': args.date, 'gate': 'publication',
                    'note': 'Channel owner approved the script and all claims for publication.'}
        # House ledger has per-claim approvals; the same note also summarizes this lock.
        ledger['approved'] = approval
        for claim in ledger['claims']:
            claim['status'] = 'verified'
            claim['approved'] = approval.copy()
        (EP/'CLAIMS.json').write_text(json.dumps(ledger, indent=2, ensure_ascii=False)+'\n')
        (EP/'TITLE.json').write_text(json.dumps({'title':title.strip()}, indent=2, ensure_ascii=False)+'\n')
        story = (EP/'STORY.md').read_text()
        story = re.sub(r'^# [^\n]+', lambda _: '# '+title.strip(), story, count=1)
        story = re.sub(r'Status:.*?(?=\n## )',
                       f'Status: script and claims locked by {args.approver.strip()} on {args.date}.\nTitle follows TITLE.json. Publishing remains a separate owner action.\n',
                       story, count=1, flags=re.S)
        (EP/'STORY.md').write_text(story)
        if (EP/'EPISODE.md').exists():
            p=EP/'EPISODE.md'
            p.write_text(re.sub(r'^# [^\n]+', lambda _: '# '+title.strip(), p.read_text(), count=1))
        for name in ['PUBLIC_README.md', 'HANDOFF.md', 'NARRATED_BUILD.md', 'scenes/README.md']:
            p=EP/name
            if p.exists():
                text=p.read_text()
                suffix={'PUBLIC_README.md': ': do near-equal airline averages survive a common basket?', 'HANDOFF.md': ' — claims locked; publishing approval PENDING', 'NARRATED_BUILD.md': ' — narrated build', 'scenes/README.md': ' — animated scenes'}[name]
                text=re.sub(r'^# [^\n]+', lambda _: '# '+title.strip()+suffix, text, count=1)
                if name=='PUBLIC_README.md':
                    text=text.replace('The current owner claim/title lock\nand publication approval are **PENDING**; this file prepares the public release.', 'The owner claim/title lock is recorded in CLAIMS.json. Publication approval\nis still a separate owner action.')
                p.write_text(text)
        python = ROOT/'ideation/.venv/bin/python'
        if not python.exists():
            python = Path(sys.executable)
        subprocess.run([str(python), str(EP/'analysis/verify_claims.py')], check=True)
        subprocess.run(['python3', str(ROOT/'studio/tools/story_check.py'), str(EP)], check=True)
        subprocess.run(['python3', str(EP/'companion/build.py')], check=True)
        subprocess.run(['python3', str(EP/'analysis/build_upload_metadata.py')], check=True)
        subprocess.run(['python3', str(EP/'analysis/refresh_narration_metadata.py')], check=True)
    except BaseException:
        for name, raw in saved.items():
            path=EP/name
            if raw is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
        raise
    print('Claims and title locked; verification and story checks passed. No publication performed.')


if __name__ == '__main__':
    main()
