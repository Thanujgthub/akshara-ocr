"""Verify a downloaded selected release and serve the unchanged local OCR API.

Does not train, convert precision, overwrite weights, or resume any checkpoint.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SELECTION = '32e18a5c4a29f3855bf323f51944a7ccae53659f60982d3d40b284960e63f00b'
ADAPTER = '7d64d5371be010c0c1fe15936b44f1e1539c2c52b80d2e3c957b53c4c91ea1e9'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def checked_path(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Checksum path escapes release root')
    return path


def verify_release(base, release):
    checksums = json.loads((release / 'checksums.json').read_text(encoding='utf-8'))
    if checksums.get('selection.json') != SELECTION or checksums.get('adapter/adapter_model.safetensors') != ADAPTER:
        raise ValueError('This is not the locked Akshara release')
    for name, expected in checksums.items():
        if digest(checked_path(release, name)) != expected:
            raise ValueError('Release checksum mismatch: ' + name)
    provenance = json.loads((release / 'model-provenance.json').read_text(encoding='utf-8'))
    if provenance['revision'] != 'cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25' or len(provenance['files']) != 31:
        raise ValueError('Unexpected original model provenance')
    for item in provenance['files']:
        if digest(checked_path(base, item['file'])) != item['sha256']:
            raise ValueError('Original model checksum mismatch: ' + item['file'])
    return {'release_files_verified': len(checksums), 'original_files_verified': 31,
            'selection_sha256': SELECTION, 'adapter_sha256': ADAPTER}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base', type=Path, required=True)
    p.add_argument('--release', type=Path, required=True)
    p.add_argument('--port', type=int, default=8765)
    p.add_argument('--verify-only', action='store_true')
    args = p.parse_args()
    base, release = args.base.resolve(), args.release.resolve()
    print(json.dumps(verify_release(base, release)), flush=True)
    if args.verify_only:
        return
    import torch
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported(including_emulation=False):
        raise SystemExit('Native CUDA BF16 is required. No precision conversion or CPU fallback was attempted.')
    import socket
    with socket.socket() as sock:
        try:
            sock.bind(('127.0.0.1', args.port))
        except OSError:
            raise SystemExit('Port already owned; inspect the existing service before launching another.')
    runtime = ROOT / '.runtime-tmp' / 'portable-selected'
    runtime.mkdir(parents=True, exist_ok=True)
    (runtime / 'status.json').write_text(json.dumps({'status': 'completed', 'stage': 'Frozen selected release; no training'}), encoding='utf-8')
    os.environ.update(INDIC_OCR_REPO=str(base), INDIC_OCR_REVISION='cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25',
                      INDIC_OCR_ADAPTER=str(release / 'adapter'), OCR_RESEARCH_CONFIG=str(release / 'full-config.json'),
                      OCR_RESEARCH_RUN=str(runtime), OCR_DEVICE='cuda', TEMP=str(runtime), TMP=str(runtime))
    os.chdir(ROOT)
    import uvicorn
    uvicorn.run('ocr.server:app', host='127.0.0.1', port=args.port)


if __name__ == '__main__':
    main()
