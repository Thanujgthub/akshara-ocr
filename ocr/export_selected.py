"""Versioned, integrity-verified selected-model exports after the capped study.

Copies the locked selection into a separate artifact; never changes selection,
best-validation adapters, resumable checkpoints or the coordinator's legacy ZIP.
No model loading or inference. Software/file integrity, not an accuracy verifier.
"""
import argparse
import hashlib
import json
import os
import shutil
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from .checkpoint_io import sha
from .portable_paths import resolve_path
from .research_io import save


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def copy_verified(source, target):
    source, target=Path(source),Path(target)
    if source.is_symlink():raise RuntimeError('Do not export symlinked source artifacts')
    expected=sha(source);target.parent.mkdir(parents=True,exist_ok=True)
    with source.open('rb') as incoming,target.open('xb') as outgoing:
        shutil.copyfileobj(incoming,outgoing,1024*1024)
        outgoing.flush();os.fsync(outgoing.fileno())
    if sha(source)!=expected or sha(target)!=expected:raise RuntimeError('Source changed or copied bytes failed verification')


def verify_export(folder):
    folder=Path(folder).resolve();index=read(folder/'checksums.json')
    for relative,expected in index.items():
        file=(folder/relative).resolve()
        if not file.is_relative_to(folder) or not file.is_file() or sha(file)!=expected:
            raise RuntimeError('Selected export integrity failure: '+relative)
    metadata=read(folder/'metadata.json')
    if sha(folder/'selection.json')!=metadata['selection_sha256']:
        raise RuntimeError('Export differs from its locked selection reference')
    selection=read(folder/'selection.json');summary=read(folder/'final-summary.json');protocol=read(folder/'protocol.json')
    if selection['variant']!=metadata['variant'] or selection['adapter']!=metadata['source_adapter'] or summary['selection']!=selection:
        raise RuntimeError('Exported selected-model references are inconsistent')
    if sha(folder/'model-provenance.json')!=metadata['original_provenance_sha256']:
        raise RuntimeError('Exported original-model provenance reference differs')
    for relative,expected in metadata['source_adapter_hashes'].items():
        if sha(folder/'adapter'/relative)!=expected:raise RuntimeError('Selected adapter copy differs from source reference')
    supplement=folder/'selected-analysis.json'
    if supplement.exists():
        analysis=read(supplement)
        if analysis['selection_sha256']!=metadata['selection_sha256'] or analysis['selection']!=metadata['variant'] or analysis['final_manifest_sha256']!=protocol['manifests']['final-test']['sha256']:
            raise RuntimeError('Exported reporting supplement differs from locked selection/final inputs')
    return metadata


def export_selected(root, parent=None, provenance=None):
    root=Path(root).resolve()
    if read(root/'status.json').get('status')!='completed':
        raise RuntimeError('Complete the study before exporting its selected model')
    selection=read(root/'selection.json');summary=read(root/'final-summary.json');protocol=read(root/'protocol.json')
    if summary['selection']!=selection:raise RuntimeError('Final summary differs from locked selection')
    counts={name:value['count'] for name,value in protocol['manifests'].items()}
    if not 0<counts['train']<=25000 or counts['validation']!=5000 or counts['final-test']!=3000 or summary['counts']!=counts:
        raise RuntimeError('Frozen capped protocol differs')
    for name,value in protocol['manifests'].items():
        if sha(root/(name+'.jsonl'))!=value['sha256']:raise RuntimeError('Frozen manifest changed')
    complete=read(root/'full/training_complete.json')
    if complete['manifest_examples']!=counts['train'] or complete['config'].get('maximum_epochs')!=1:
        raise RuntimeError('One-epoch training evidence missing or inconsistent')
    if set(summary['final_metrics'])!={'original','pilot','candidate'} or any(value['examples']!=3000 for value in summary['final_metrics'].values()):
        raise RuntimeError('Sealed comparison evidence is incomplete')
    adapter=resolve_path(selection['adapter']).resolve() if selection['adapter'] else None
    if selection['variant'] not in {'original','pilot','candidate'} or (adapter is None)!=(selection['variant']=='original'):
        raise RuntimeError('Selected variant/adapter reference is inconsistent')
    if adapter and not all((adapter/name).is_file() for name in ['adapter_model.safetensors','adapter_config.json']):
        raise RuntimeError('Selected adapter files missing; no fallback')
    provenance=Path(provenance) if provenance else Path(__file__).resolve().parents[1]/'reports/model_provenance.json'
    if len(read(provenance).get('files',[]))!=31:raise RuntimeError('Original31-file provenance reference missing')
    parent=Path(parent) if parent else root/'selected-exports';parent.mkdir(parents=True,exist_ok=True)
    name='selected-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:12]
    staging=parent/('.partial-'+name);staging.mkdir()
    final=parent/name;archive=parent/(name+'.zip');pending_zip=parent/('.partial-'+name+'.zip.tmp')
    source_adapter_hashes={}
    if adapter:
        for file in sorted(adapter.rglob('*')):
            if file.is_file():
                relative=file.relative_to(adapter).as_posix();copy_verified(file,staging/'adapter'/relative);source_adapter_hashes[relative]=sha(file)
    sources={'selection.json':root/'selection.json','protocol.json':root/'protocol.json',
             'final-summary.json':root/'final-summary.json','training_complete.json':root/'full/training_complete.json',
             'best.json':root/'full/best.json','full-config.json':root/'configs/full.json',
             'model-provenance.json':provenance}
    supplement=root/'reports/final-selected-analysis-v1.json'
    if supplement.exists():
        analysis=read(supplement)
        if analysis['selection_sha256']!=sha(root/'selection.json') or analysis['final_manifest_sha256']!=protocol['manifests']['final-test']['sha256'] or analysis['selection']!=selection['variant']:
            raise RuntimeError('Reporting supplement differs from locked selection/frozen final inputs')
        sources['selected-analysis.json']=supplement
    for relative,source in sources.items():copy_verified(source,staging/relative)
    metadata={'created_utc':datetime.now(timezone.utc).isoformat(),'role':'final-selected-artifact',
              'selection_sha256':sha(root/'selection.json'),'source_adapter':selection['adapter'],
              'original_provenance_sha256':sha(provenance),
              'source_adapter_hashes':source_adapter_hashes,'adapter_relative_path':'adapter' if adapter else None,
              'variant':selection['variant'],'counts':counts,'original_checkpoint':'Requires exact original licensed IndicOCR snapshot; base weights are not redistributed.',
              'model_revision':'cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25','scope':'Word crops only; API/browser parity is a separate pending check.'}
    save(staging/'metadata.json',metadata)
    index={file.relative_to(staging).as_posix():sha(file) for file in sorted(staging.rglob('*')) if file.is_file()}
    save(staging/'checksums.json',index);verify_export(staging)
    files=[file for file in sorted(staging.rglob('*')) if file.is_file()]
    with zipfile.ZipFile(pending_zip,'w',zipfile.ZIP_DEFLATED) as zipped:
        for file in files:zipped.write(file,file.relative_to(staging).as_posix())
    with pending_zip.open('rb+') as stream:os.fsync(stream.fileno())
    with zipfile.ZipFile(pending_zip) as zipped:
        if zipped.testzip() is not None:raise RuntimeError('Selected-model ZIP CRC verification failed')
        for relative,expected in index.items():
            digest=hashlib.sha256()
            with zipped.open(relative) as stream:
                for data in iter(lambda:stream.read(65536),b''):digest.update(data)
            if digest.hexdigest()!=expected:raise RuntimeError('Archived bytes differ from verified export')
    if final.exists() or archive.exists():raise FileExistsError('Never overwrite an earlier selected export')
    os.replace(staging,final);os.replace(pending_zip,archive);verify_export(final)
    receipt={'directory':name,'zip':archive.name,'checksums_sha256':sha(final/'checksums.json'),
             'zip_sha256':sha(archive),'selection_sha256':metadata['selection_sha256'],'variant':selection['variant']}
    save(parent/'latest.json',receipt)
    return final,archive,receipt


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',default='D:/OCR/runs/word-efficient-v3');parser.add_argument('--output-parent')
    args=parser.parse_args();folder,archive,receipt=export_selected(args.run,args.output_parent)
    print(json.dumps({'folder':str(folder),'archive':str(archive),'receipt':receipt},indent=2))


if __name__=='__main__':main()
