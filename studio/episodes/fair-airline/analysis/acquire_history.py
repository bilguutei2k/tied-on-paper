#!/usr/bin/env python3
"""Opaque-byte acquisition of the two historical motivation pages in METHOD.

This separate acquisition process is never imported by the simulation process.
It neither decodes page contents nor requests contemporary ranking sources.
"""
import requests
from common import EP, RAW, dump, progress, sha, utc

SOURCES=[
 ('historical-atcr-landing.html','https://www.transportation.gov/airconsumer/february-2016-air-travel-consumer-report',
  {'status':'federal_work_basis_for_agency_text_only; exact_page_terms_unresolved',
   'snapshot_redistribution':False,'terms_url':'https://www.transportation.gov/website-information/website-policies'}),
 ('historical-forbes-2015.html','https://www.forbes.com/sites/michelinemaynard/2015/04/27/the-best-and-worst-airlines-for-summer-2015-vacation-travel/',
  {'status':'third_party_copyright; no_redistribution_permission',
   'snapshot_redistribution':False,'terms_url':'https://www.forbes.com/terms-and-conditions/'})]

def main():
    RAW.mkdir(exist_ok=True,parents=True)
    entries=[]
    for name,url,licence in SOURCES:
        p=RAW/name
        entry=dict(url=url,path=str(p.relative_to(EP)),retrieved_utc=utc(),
                   licence=licence,content_decoded=False)
        try:
            with requests.get(url,stream=True,timeout=(20,40)) as response:
                entry.update(http_status=response.status_code,final_url=response.url,
                             content_type=response.headers.get('Content-Type'))
                response.raise_for_status()
                temporary=p.with_suffix('.partial')
                with temporary.open('wb') as f:
                    for chunk in response.iter_content(2**20):f.write(chunk)
                temporary.replace(p)
            entry.update(status='saved',bytes=p.stat().st_size,sha256=sha(p))
        except requests.RequestException as error:
            entry.update(status='access_failed',error_type=type(error).__name__)
        entries.append(entry)
        progress(f'Historical registered motivation source {name}: {entry["status"]}; opaque byte storage/hashing only, no page decoding. Private snapshot rights recorded separately from reporting-carrier data rights.')
    dump(EP/'data/history-manifest.json',dict(written_utc=utc(),
      purpose='Registered historical 2015 motivation only',sources=entries))
    print({e['path'].split('/')[-1]:e['status'] for e in entries})

if __name__=='__main__':main()
