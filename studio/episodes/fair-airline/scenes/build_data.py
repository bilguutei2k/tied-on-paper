"""Computed results only. The ledger supplies claim IDs/keys, never observations.

claims_check.json is the independent verification RESULT artifact: only its
computed derived_metrics supply design, Denver and grouped time-of-day keys.
No claim stated value, raw record, or external page is copied into scene data.
"""
import hashlib
import json
import os
from pathlib import Path

EP = Path(__file__).resolve().parent.parent

def payload():
    ledger_raw = (EP / 'CLAIMS.json').read_bytes()
    claims = json.loads(ledger_raw)['claims']
    sources = {}
    hashes = {}
    for name in sorted({c['result_file'] for c in claims}):
        assert name in {'analysis/results.json', 'analysis/review_checks/results.json', 'analysis/claims_check.json'}
        raw = (EP / name).read_bytes()
        obj = json.loads(raw)
        if name.endswith('claims_check.json'):
            assert obj['all_pass'] and not obj['discrepancies']
            assert obj['ledger_sha256'] == hashlib.sha256(ledger_raw).hexdigest()
            obj = {'derived_metrics': obj['derived_metrics']}
        sources[name] = obj
        hashes[name] = hashlib.sha256(raw).hexdigest()
    def get(obj, key):
        import re
        for token in re.findall(r'[^.\[\]]+', key):
            obj = obj[int(token)] if isinstance(obj, list) else obj[token]
        return obj
    values, ids, inputs = {}, {}, {}
    for c in claims:
        for item in c.get('values', []):
            key = item['key']
            if c['result_file'].endswith('claims_check.json') and not key.startswith('derived_metrics.'):
                continue
            value = get(sources[c['result_file']], key)
            if key in values:
                assert values[key] == value
            values[key] = value
            ids.setdefault(key, []).append(c['id'])
            inputs[key] = {'file': c['result_file'], 'key': key}
    # Period/window labels are derived from claimed result keys, not typed observations.
    import re
    for alias, key, index in [('year_a_start', 'primary_2023_2024.adjusted_gap_ua_minus_wn_pp.estimate', 0), ('year_a_end', 'primary_2023_2024.adjusted_gap_ua_minus_wn_pp.estimate', 1), ('year_b', 'replication_2025.adjusted_gap_ua_minus_wn_pp.estimate', 0)]:
        name = 'scene.' + alias
        values[name] = int(re.findall(r'\d{4}', key)[index])
        ids[name] = ids[key]
        inputs[name] = {'file': inputs[key]['file'], 'key': key, 'transform': 'period year parsed from registered key'}
    for window, claim in [('1h', 'FA-C021'), ('4h', 'FA-C022'), ('30min', 'FA-C020')]:
        c = next(c for c in claims if c['id'] == claim)
        key = c['values'][0]['key']
        name = 'scene.window_' + window
        values[name] = int(re.search(r'(\d+)(?:h|min)', key).group(1))
        ids[name] = [claim]
        inputs[name] = {'file': c['result_file'], 'key': key, 'transform': 'registered window parsed from key'}
    for label, claim in [('before_10', 'FA-C060'), ('from_16', 'FA-C060')]:
        key = 'derived_metrics.A.time.' + label + '.gap_pp'
        name = 'scene.' + label
        values[name] = int(label.split('_')[-1])
        ids[name] = [claim]
        inputs[name] = {'file': inputs[key]['file'], 'key': key, 'transform': 'local scheduled hour parsed from grouped result key'}
    locked = bool(claims) and all(c['status'] == 'verified' for c in claims)
    preview = os.environ.get('FA_LOCKED_PREVIEW') == '1'
    return dict(locked=locked or preview, preview=preview, title=json.loads((EP/'TITLE.json').read_text())['title'],
                status='locked preview' if preview else 'locked' if locked else 'PRE-LOCK DRAFT · CLAIMS PROPOSED · NUMERICALLY VERIFIED',
                results_sha256=hashes['analysis/results.json'], claims_sha256=hashlib.sha256(ledger_raw).hexdigest(),
                source_sha256=hashes, values=values, claim_ids=ids, inputs=inputs,
                claims={c['id']: {'status': c['status'], 'exploratory': c.get('exploratory', False)} for c in claims})

if __name__ == '__main__':
    data = payload()
    (EP / 'scenes/data.js').write_text('// Generated from computed result artifacts; never ledger stated values.\nwindow.SCENE_DATA = ' + json.dumps(data, ensure_ascii=False, sort_keys=True, indent=1) + ';\n')
    print('Wrote', len(data['values']), 'claim-keyed computed values;', data['status'])
