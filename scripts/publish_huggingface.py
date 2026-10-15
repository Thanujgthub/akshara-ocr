"""Publish prepared selected-model and static-site folders using local HF auth.

No credentials are accepted as command-line arguments. No hardware is purchased.
Existing repositories are deliberately not overwritten by this first-release command.
"""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model-dir', type=Path, required=True)
    p.add_argument('--site-dir', type=Path, required=True)
    args = p.parse_args()
    model, site = args.model_dir.resolve(), args.site_dir.resolve()
    checks = json.loads((model / 'checksums.json').read_text(encoding='utf-8'))
    expected = '7d64d5371be010c0c1fe15936b44f1e1539c2c52b80d2e3c957b53c4c91ea1e9'
    if checks.get('adapter/adapter_model.safetensors') != expected:
        raise SystemExit('Not the selected adapter release')
    for name, checksum in checks.items():
        path = (model / name).resolve()
        if not path.is_relative_to(model) or hashlib.sha256(path.read_bytes()).hexdigest() != checksum:
            raise SystemExit('Selected release checksum failure: ' + name)
    if 'staticHosting: true' not in (site / 'deployment-config.js').read_text():
        raise SystemExit('Site must be built explicitly for static hosting')
    if not (site / 'README.md').read_text(encoding='utf-8').startswith('---\n'):
        raise SystemExit('Prepared Space README metadata missing')
    from huggingface_hub import HfApi
    api = HfApi()
    owner = api.whoami()['name']
    model_id = owner + '/akshara-telugu-handwriting-ocr'
    space_id = owner + '/akshara-ocr-studio'
    # Explicitly refuse replacement of any pre-existing repository.
    api.create_repo(model_id, repo_type='model', private=False, exist_ok=False)
    model_commit = api.upload_folder(repo_id=model_id, repo_type='model', folder_path=model,
                                     commit_message='Release exact validation-selected capped-study adapter')
    print(json.dumps({'model': 'https://huggingface.co/' + model_id, 'commit': model_commit.oid}), flush=True)
    api.create_repo(space_id, repo_type='space', space_sdk='static', private=False, exist_ok=False)
    space_commit = api.upload_folder(repo_id=space_id, repo_type='space', folder_path=site,
                                     commit_message='Publish Akshara studio and measured completed-study report')
    print(json.dumps({'space': 'https://huggingface.co/spaces/' + space_id, 'commit': space_commit.oid}), flush=True)


if __name__ == '__main__':
    main()
