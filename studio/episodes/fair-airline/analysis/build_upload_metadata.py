#!/usr/bin/env python3
"""Generate upload titles/descriptions from TITLE.json; does not upload."""
import json
from pathlib import Path
EP=Path(__file__).resolve().parent.parent
TITLE=json.loads((EP/'TITLE.json').read_text())['title']
CREDIT='''Data: Bureau of Transportation Statistics, Reporting Carrier On-Time Performance; independent processing.
https://www.transtats.bts.gov/ONTIME/
Monthly source addresses and SHA-256 hashes: episode data/flights-manifest.json in [PUBLIC_REPO_URL]. Raw and flight-level data are not redistributed.
Official annual context: U.S. DOT Air Travel Consumer Reports, February 2024 (revised March 2025), February 2025 and February 2026, Tables 1C/1D. Addresses in PUBLIC_README.md.
Companion: [COMPANION_URL]
Code, methods, failures, amendments, all sensitivities and independent checks: [PUBLIC_REPO_URL]'''
TEXT={
'film':'''National airline punctuality averages can hide the flights in the basket. I compare United-operated and Southwest-operated domestic nonstop flights on the same route, date and two-hour departure window, using common schedule-count weights.

Against each operator's own arrival timetable, United's timely-completion advantage is 6.27 percentage points in 2023–2024 and 8.20 in 2025. Nominal 99% missingness envelopes: 4.60–7.94 and 5.31–11.00 points. Both clear the registered two-point line; the result replicates.

This is a small, Denver-heavy overlap, excluding United Express and other operators. It is not a causal airline-choice effect or a best-airline ranking. Post-hoc shared-allowance checks reduce the gaps to 2.59 / 4.33 points; timetable choices and operating circumstances remain bundled. Two simulation gates failed before the pre-outcome interval redesign. Full caveats and contrary evidence are in the companion and code.''',
'short-a':'''Around 78% on time nationally can look like a tie. On comparable United-operated and Southwest-operated flights, with common weights and each operator's own arrival timetable, the United advantage is 6.27 points in 2023–2024 and 8.20 in 2025. Both nominal 99% missingness envelopes clear the two-point line; the registered result replicates.

The overlap is small and Denver-heavy. United Express is excluded. This is timetable-promise performance, not causal airline-choice advice or a general airline ranking. See the full film: [VIDEO_URL].''',
'short-b':'''Whose arrival promise defines punctuality? In this comparable-flight basket, United schedules about 4.5 more block minutes; actual completed-cell blocks are also longer, about 4.8 minutes in 2023–2024 and 6.2 in 2025.

A shared departure-relative elapsed-time allowance reduces the United arrival gaps to 2.59 / 4.33 points. Southwest also has 10.13 / 13.09 points more observed departures 15+ minutes late, with all scheduled flights as denominator. These are exploratory, post-hoc, not registered checks. They identify neither deliberate padding nor a causal effect. United Express is excluded. Full film: [VIDEO_URL].''',
'short-c':'''One average does not describe every departure time. Exploratory, post-hoc, not registered checks of the same frozen United-operated/Southwest-operated comparison basket show gaps of −0.41 / +1.38 points before 10:00 local scheduled departure, and +11.71 / +12.90 from 16:00 onward (2023–2024 / 2025).

No time-band intervals were computed. Roughly 80% of comparison weight touches Denver; the overlap is small and excludes United Express. This is not morning-flight advice, a universal advantage or a causal airline-choice effect. Full film: [VIDEO_URL].'''
}
rows={name:{'title':TITLE if name in ['film','short-a'] else 'Whose deadline?' if name=='short-b' else 'The gap changes through the day','description':text+'\n\n'+CREDIT,'video':f'renders/final/{name}.mp4','captions':f'renders/final/{name}.srt'} for name,text in TEXT.items()}
assert all(len(x['description'])<=5000 for x in rows.values())
(EP/'analysis/upload-metadata.json').write_text(json.dumps({'publication_approval':'PENDING until separately authorized','outputs':rows},indent=2,ensure_ascii=False)+'\n')
print('Generated four upload descriptions:',{k:len(v['description']) for k,v in rows.items()})
