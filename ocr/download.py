"""Download a registry-approved archive. Never accepts model terms or bypasses gates."""
import argparse
import hashlib
import json
import os
import urllib.request
from pathlib import Path

def download(record, destination):
    if record.get('approval_status') != 'approved' or not record.get('permitted_scope'):
        raise ValueError('Source not approved. Verify license and permitted project scope first.')
    url=record.get('download_url','')
    if not url.startswith('https://'): raise ValueError('An official HTTPS download URL is required')
    destination=Path(destination)
    if destination.exists(): raise FileExistsError('Refusing to overwrite existing archive')
    destination.parent.mkdir(parents=True,exist_ok=True)
    partial=destination.with_suffix(destination.suffix+'.partial')
    h=hashlib.sha256()
    try:
        with urllib.request.urlopen(url,timeout=60) as response, partial.open('xb') as out:
            if 'text/html' in response.headers.get('Content-Type',''):
                raise ValueError('Download returned HTML; possible access gate')
            while True:
                chunk=response.read(1024*1024)
                if not chunk: break
                out.write(chunk);h.update(chunk)
        digest=h.hexdigest()
        if record.get('published_sha256') and digest != record['published_sha256']:
            raise ValueError('Published checksum mismatch')
        os.replace(partial,destination)
        destination.with_suffix(destination.suffix+'.sha256').write_text(digest,encoding='ascii')
        return digest
    except Exception:
        if partial.exists(): partial.unlink()
        raise

def main():
    p=argparse.ArgumentParser();p.add_argument('--registry',default='data_registry/datasets.json');p.add_argument('--source',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    records=json.loads(Path(a.registry).read_text(encoding='utf-8'))
    source=next(r for r in records if r['id']==a.source)
    print(download(source,a.output))
if __name__=='__main__':main()
