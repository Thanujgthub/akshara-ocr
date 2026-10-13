"""Compare actual API outputs with saved validation outputs after study selection.

This is a software compatibility check on a declared validation subset, not a new
accuracy benchmark or a second sealed-test evaluation. Never loads another GPU model.
"""
import argparse
import json
import time
import urllib.request
import uuid
from pathlib import Path

from .checkpoint_io import sha
from .research_io import save


def request_prediction(url, image, variant):
    boundary = 'akshara-' + uuid.uuid4().hex
    parts = []
    for name, value in [('mode', 'word'), ('variant', variant)]:
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="crop.png"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode())
    parts.extend([image.read_bytes(), f'\r\n--{boundary}--\r\n'.encode()])
    request = urllib.request.Request(url.rstrip('/') + '/api/predict', data=b''.join(parts), headers={'Content-Type': 'multipart/form-data; boundary=' + boundary})
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.loads(response.read())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', default='D:/OCR/runs/word-efficient-v3')
    parser.add_argument('--data', default='D:/OCR/research-v2')
    parser.add_argument('--url', default='http://127.0.0.1:8765')
    parser.add_argument('--output', required=True)
    parser.add_argument('--limit', type=int, default=32)
    args = parser.parse_args()
    root, data, out = Path(args.run), Path(args.data).resolve(), Path(args.output)
    if out.exists():
        raise RuntimeError('Use a fresh parity output directory; preserve earlier results')
    if not 0 < args.limit <= 5000:
        raise ValueError('Declare a validation subset of1..5000 examples')
    state = json.loads((root / 'status.json').read_text(encoding='utf-8'))
    if state['status'] != 'completed' or not (root / 'final-summary.json').exists():
        raise RuntimeError('Finish the study and stop GPU workers before API parity')
    selection = json.loads((root / 'selection.json').read_text(encoding='utf-8'))
    final = json.loads((root / 'final-summary.json').read_text(encoding='utf-8'))
    if final['selection'] != selection:
        raise RuntimeError('Final report differs from locked validation selection')
    protocol = json.loads((root / 'protocol.json').read_text(encoding='utf-8'))
    manifest = root / 'validation.jsonl'
    if sha(manifest) != protocol['manifests']['validation']['sha256']:
        raise RuntimeError('Frozen validation manifest changed')
    with urllib.request.urlopen(args.url.rstrip('/') + '/api/health', timeout=10) as response:
        health = json.loads(response.read())
    if health['training_active'] or not health['model_ready']:
        raise RuntimeError('API is unavailable or GPU study remains active')
    rows = [json.loads(line) for line in manifest.read_text(encoding='utf-8').splitlines()][:args.limit]
    paths = {'original': root / 'experiments/curated-efficient-original'}
    if selection['variant'] == 'pilot':
        paths['selected'] = root / 'experiments/curated-efficient-pilot'
    elif selection['variant'] == 'candidate':
        best = json.loads((root / 'full/best.json').read_text(encoding='utf-8'))
        paths['selected'] = root / f"full/epoch-{best['epoch']}/validation"
    else:
        paths['selected'] = paths['original']
    expected = {name: {r['example_id']: r for r in map(json.loads, (folder / 'predictions.jsonl').read_text(encoding='utf-8').splitlines())} for name, folder in paths.items()}
    out.mkdir(parents=True)
    mismatches = []
    with (out / 'raw-api-outputs.jsonl').open('w', encoding='utf-8') as output:
        for row in rows:
            image = (data / row['local_relative_path']).resolve()
            if not image.is_relative_to(data) or sha(image) != row['original_sha256']:
                raise RuntimeError('Validation crop path or bytes changed')
            for name, variant in [('original', 'original'), ('selected', 'adapted')]:
                started = time.perf_counter()
                result = request_prediction(args.url, image, variant)
                saved = expected[name][row['example_id']]
                matches = result['markdown'] == saved['prediction'] and result.get('generated_token_ids') == saved.get('generated_token_ids') and result.get('truncated') == saved.get('truncated')
                adapter = result.get('model', {}).get('adapter')
                intended = selection['adapter'] if name == 'selected' else None
                if (Path(adapter).resolve() if adapter else None) != (Path(intended).resolve() if intended else None):
                    matches = False
                record = {'example_id': row['example_id'], 'variant': name, 'latency_seconds': time.perf_counter() - started, 'exact_raw_token_truncation_and_adapter_parity': matches, 'response': result}
                output.write(json.dumps(record, ensure_ascii=False) + '\n'); output.flush()
                if not matches:
                    mismatches.append({'example_id': row['example_id'], 'variant': name})
    report = {'passed': not mismatches, 'validation_examples': len(rows), 'api_requests': 2 * len(rows), 'selection': selection['variant'], 'selection_sha256': sha(root / 'selection.json'), 'validation_manifest_sha256': sha(manifest), 'mismatches': mismatches, 'scope': 'Actual original/selected API versus saved validation output on the first declared N validation examples; no final-test replay and no whole-page claim.'}
    save(out / 'parity.json', report)
    print(json.dumps(report, indent=2))
    if mismatches:
        raise RuntimeError('API parity failed; preserve raw evidence and repair before deployment')


if __name__ == '__main__':
    main()
