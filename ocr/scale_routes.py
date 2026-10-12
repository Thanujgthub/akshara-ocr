"""Local-only live scale-up monitor; never exposes final-test examples during selection."""
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from .study_routes import read
router=APIRouter();ROOT=Path('D:/OCR/runs/word-scale-v2')

@router.get('/api/research-v2')
def status():
    state=read(ROOT/'status.json') or {'status':'not_started','stage':'waiting'}
    active=Path(state.get('experiment_directory',str(ROOT)))
    if not active.resolve().is_relative_to(ROOT.resolve()):active=ROOT
    log=Path('D:/OCR/full-word-audit.log')
    protocol=read(ROOT/'protocol.json');curation=read(ROOT/'curation-protocol.json')
    if protocol and curation:
        protocol={**protocol,'manifests':{**protocol['manifests'],'train':curation['manifests']['train-curated'],'validation':curation['manifests']['validation-curated']}}
    return {'status':state,'protocol':protocol,'curation':curation,'selection':read(ROOT/'selection.json'),
            'progress':read(active/'training_progress.json'),'evaluation':read(active/'progress.json'),
            'experiments':read(ROOT/'experiments.json'),'final':read(ROOT/'final-summary.json') if state['status']=='completed' else None,
            'audit_tail':log.read_text(encoding='utf-8',errors='replace')[-1200:] if log.exists() else '',
            'failure':read(ROOT/'failure.json') if state['status']=='failed' else None}

@router.get('/research-v2',response_class=HTMLResponse)
def monitor():
    return (Path(__file__).parent/'scale_monitor.html').read_text(encoding='utf-8')
