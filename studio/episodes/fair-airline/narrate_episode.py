"""Episode-only spoken forms and Short 1/2/3 aliases for the house narrator.

Run with .venv/bin/python; synthesis still uses studio/tools/narrate.py.
--forms-only writes the reviewable spoken script without loading MLX.
"""
import json
import re
import sys
from pathlib import Path

EP = Path(__file__).resolve().parent
sys.path.insert(0, str(EP.parents[1] / 'tools'))
import narrate as house

base_speak, base_scenes = house.speak, house.scenes


def speak(token, episode=None):
    if episode != 'fair-airline':
        return base_speak(token, episode)
    token = re.sub(r'\b((?:19|20)\d{2})[–-]((?:19|20)\d{2})\b',
                   lambda m: house.year(int(m[1])) + ' to ' + house.year(int(m[2])), token)
    token = re.sub(r'\b((?:19|20)\d{2})\b', lambda m: house.year(int(m[1])), token)
    names = {'UA': 'United', 'WN': 'Southwest', 'DEN': 'Denver', 'LAX': 'Los Angeles',
             'DOT': 'D O T', 'BTS': 'B T S', 'PP': 'percentage points'}
    for written, spoken in names.items():
        token = re.sub(r'\b' + written + r'\b', spoken, token)
    token = token.replace('%', ' percent').replace('→', ' to ')
    token = re.sub(r'(?<!\d)(\d+(?:\.\d+)?)[–-](\d+(?:\.\d+)?)(?!\d)', r'\1 to \2', token)
    return base_speak(token, episode)


def scenes(text):
    parsed = base_scenes(text)
    return {(section, re.sub(r'^Short ([123]):', lambda m: 'Short ' + 'ABC'[int(m[1])-1] + ':', heading)): lines
            for (section, heading), lines in parsed.items()}


house.speak, house.scenes = speak, scenes


def forms():
    sections = {}
    for (_, heading), lines in scenes((EP / 'STORY.md').read_text()).items():
        match = house.SCENE_ID.match(heading)
        if match:
            sections[match[1]] = [{'index': i, 'written': house.TAG.sub('', line).strip(),
                                  'spoken': house.spoken_form(line, EP.name)[0]}
                                 for i, line in enumerate(lines)]
    (EP / 'SPOKEN_FORMS.json').write_text(json.dumps({'status': 'pre-lock draft', 'voice': 'af_heart',
        'speed': 1.0, 'scenes': sections}, indent=2, ensure_ascii=False) + '\n')
    print('Spoken forms:', len(sections), 'sections,', sum(map(len, sections.values())), 'lines')


if __name__ == '__main__':
    forms()
    if '--forms-only' not in sys.argv:
        house.main([str(EP), *sys.argv[1:]])
