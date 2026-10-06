#!/usr/bin/env python3
"""Save source bytes; never decompress or decode confirmation CSV values."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import time
import zipfile
import requests
from common import EP, RAW, dump, progress, sha, utc

ROOT = 'https://www.transtats.bts.gov/'
DOCS = {
    'dictionary.html': ROOT + 'Fields.asp?gnoyr_VQ=FGJ',
    'airport-id.csv': ROOT + 'Download_Lookup.asp?Y11x72=Y_NVecbeg_VQ',
    'airline-id.csv': ROOT + 'Download_Lookup.asp?Y11x72=Y_NVeYVaR_VQ',
    'unique-carrier.csv': ROOT + 'Download_Lookup.asp?Y11x72=Y_haVdhR_PNeeVRef',
    'state-codes.csv': ROOT + 'Download_Lookup.asp?Y11x72=Y_fgNgR_NOe_NiVNgVba',
    'table-profile.html': ROOT + 'TableInfo.asp?gnoyr_VQ=FGJ',
    'historical-atcr.pdf': 'https://www.transportation.gov/sites/dot.gov/files/docs/resources/individuals/aviation-consumer-protection/155801/2016februaryatcr_0.pdf',
    'bts-policy.html': 'https://www.bts.gov/policies',
}
LICENSE = {'status': 'unresolved_source_specific_raw_redistribution_terms',
           'attribution': 'Bureau of Transportation Statistics; independent processing',
           'raw_and_row_level_release': False,
           'basis_note': 'Do not transfer the related marketing-carrier public-domain label to this product.',
           'terms_url': 'https://www.bts.gov/policies'}
PRIOR = {}

def fetch(item):
    name, url = item
    path = RAW / name
    entry = {'url': url, 'path': str(path.relative_to(EP)), 'retrieved_utc': utc(),
             'licence': LICENSE, 'status': 'pending'}
    if path.exists():
        if name in PRIOR:
            entry = {**PRIOR[name], 'verified_utc': utc()}
        else:
            entry.pop('retrieved_utc', None)
            entry['verified_utc'] = utc()
            entry['retrieved_date_utc'] = time.strftime('%Y-%m-%d', time.gmtime(path.stat().st_mtime))
        entry.update(status='saved', bytes=path.stat().st_size, sha256=sha(path))
        return entry
    for attempt in range(3):
        temp = path.with_suffix(path.suffix + '.partial')
        try:
            with requests.get(url, stream=True, timeout=(30, 180)) as r:
                entry.update(http_status=r.status_code, content_type=r.headers.get('Content-Type'),
                             final_url=r.url)
                r.raise_for_status()
                with temp.open('wb') as f:
                    for b in r.iter_content(2**20):
                        f.write(b)
            if name.endswith('.zip'):
                with zipfile.ZipFile(temp) as z:
                    members = [{'name': i.filename, 'bytes_uncompressed': i.file_size,
                                'bytes_compressed': i.compress_size, 'crc32': f'{i.CRC:08x}'}
                               for i in z.infolist()]
                    assert sum(i['name'].lower().endswith('.csv') for i in members) == 1
                    entry['members'] = members
            elif name.endswith('.csv'):
                assert temp.read_bytes().startswith(b'Code,Description'), 'lookup did not return CSV'
            elif name.endswith('.pdf'):
                assert temp.read_bytes()[:4] == b'%PDF', 'not a PDF'
            temp.replace(path)
            path.chmod(0o400)
            entry.update(status='saved', bytes=path.stat().st_size, sha256=sha(path))
            return entry
        except Exception as exc:
            temp.unlink(missing_ok=True)
            entry.update(status='access_failed', error=type(exc).__name__)
            if entry.get('http_status', 0) in (403, 404) or attempt == 2:
                return entry
            time.sleep(attempt + 1)
    return entry

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('stage', choices=['docs', 'flights'])
    ap.add_argument('--workers', type=int, default=10)
    args = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    items = list(DOCS.items()) if args.stage == 'docs' else [
        (f'{year}-{month:02}.zip', ROOT + 'PREZIP/' +
         f'On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{year}_{month}.zip')
        for year in (2023, 2024, 2025) for month in range(1, 13)]
    manifest = {'stage': args.stage, 'outcome_access': False, 'sources': []}
    target = EP / f'data/{args.stage}-manifest.json'
    if target.exists():
        PRIOR.update({e['path'].rsplit('/',1)[-1]:e for e in json.loads(target.read_text())['sources']})
    progress(f'Acquisition {args.stage} started: {len(items)} registered sources; byte storage/hashing only.')
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for entry in pool.map(fetch, items):
            manifest['sources'].append(entry)
            dump(target, manifest)
            progress(f"Acquisition {args.stage}: {PathName(entry['path'])}, {entry['status']}; no outcome decoding.")
    if args.stage == 'flights':
        # Manifest order is numeric source-month order, not download completion order.
        for entry in manifest['sources']:
            if entry['status'] == 'saved' and 'members' not in entry:
                with zipfile.ZipFile(EP / entry['path']) as z:
                    entry['members'] = [{'name': i.filename, 'bytes_uncompressed': i.file_size,
                                         'bytes_compressed': i.compress_size,
                                         'crc32': f'{i.CRC:08x}'} for i in z.infolist()]
    dump(target, manifest)
    counts = {s: sum(e['status'] == s for e in manifest['sources'])
              for s in ('saved', 'access_failed')}
    progress(f'Acquisition {args.stage} finished: {counts}; manifest sealed with hashes only for saved bytes.')
    print({'stage': args.stage, **counts})

def PathName(path):
    return path.rsplit('/', 1)[-1]

if __name__ == '__main__':
    main()
