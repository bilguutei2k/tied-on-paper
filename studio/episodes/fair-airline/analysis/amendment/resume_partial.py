#!/usr/bin/env python3
"""Finish interrupted records using sealed functions; do not repeat saved datasets."""
import json
import time
from concurrent.futures import ThreadPoolExecutor
import run_gate as gate


def main():
    gate.check_seal()
    result = json.loads((gate.HERE / 'results.json').read_text())
    assert result['status'] == 'RUNNING'
    st, manifest = gate.load_structure()
    assert manifest['cells_sha256'] == json.loads((gate.HERE / 'structure.json').read_text())['cells_sha256']
    for path in sorted(gate.HERE.glob('bank*-candidate*-scenario*.jsonl')):
        bank, candidate, sid = [int(part.removeprefix(prefix)) for part, prefix in
            zip(path.stem.split('-'), ('bank', 'candidate', 'scenario'))]
        if any(x['bank'] == bank and x['candidate'] == candidate and x['scenario']['id'] == sid
               for x in result['scenarios']):
            continue
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        n = gate.DESIGN['selection_datasets'] if bank == 0 else gate.DESIGN['validation_datasets']
        assert [r['rep'] for r in rows] == list(range(len(rows))) and len(rows) <= n
        initial = len(rows)
        before = gate.sha(path)
        scenario = gate.scenarios()[sid]
        prepared = gate.prepare(st, scenario)
        start = time.perf_counter()
        with path.open('a') as out, ThreadPoolExecutor(max_workers=10) as pool:
            for row in pool.map(lambda rep: gate.one(st, scenario, prepared, bank, rep, candidate), range(initial, n)):
                rows.append(row)
                out.write(json.dumps(row, separators=(',', ':')) + '\n')
        summary = gate.summarize(rows, scenario, prepared[3])
        summary.update(bank=bank, candidate=candidate, seconds=time.perf_counter()-start,
                       timing_scope='resumed portion only', preserved_datasets=initial,
                       preserved_file_sha256=before)
        result['scenarios'].append(summary)
        gate.dump(gate.HERE / 'results.json', result)
        gate.progress(f'Amendment continuation preserved {initial} records in {path.name}; completed remaining {n-initial} with sealed generator/interval functions and ten workers. No algorithm or acceptance change; confirmation outcomes closed.')
        print(json.dumps(dict(file=path.name, preserved=initial, completed=n-initial, passes=summary['passes'])), flush=True)


if __name__ == '__main__':
    main()
