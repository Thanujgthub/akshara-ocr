"""Local-only live scale-up monitor; never exposes final-test examples during selection."""
from pathlib import Path
import json,statistics,os
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from .study_routes import read
router=APIRouter();ROOT=Path(os.environ.get('OCR_RESEARCH_RUN','D:/OCR/runs/word-efficient-v3' if Path('D:/OCR/runs/word-efficient-v3/status.json').exists() else 'D:/OCR/runs/word-scale-v2'))

def recent_timing(path):
    if not path.exists():return None
    with path.open('rb') as f:
        f.seek(0,2);size=f.tell();f.seek(max(0,size-128000));data=f.read().decode('utf-8',errors='replace')
    records=[]
    for line in data.splitlines():
        try:records.append(json.loads(line))
        except ValueError:continue
    durations=[b['elapsed_seconds']-a['elapsed_seconds'] for a,b in zip(records,records[1:])
               if b.get('epoch')==a.get('epoch') and b['example']==a['example']+1]
    recent=[d for d in durations[-100:] if 0<d<30]
    if not recent:return None
    latest=records[-1];median=statistics.median(recent)
    return {'recent_median_seconds_per_word':median,'samples':len(recent),
            'current_epoch_remaining_seconds_excluding_pauses':max(0,latest['examples_per_epoch']-latest['example'])*median,
            'long_gap_count_in_log_tail':sum(d>=30 for d in durations),
            'scope':'Recent per-word wall durations; excludes long gaps, model load, future validation and later stages. Not a measured GPU-kernel time.'}

@router.get('/api/research-v2')
def status():
    state=read(ROOT/'status.json') or {'status':'not_started','stage':'waiting'}
    active=Path(state.get('experiment_directory',str(ROOT)))
    if not active.resolve().is_relative_to(ROOT.resolve()):active=ROOT
    log=Path('D:/OCR/full-word-audit.log')
    protocol=read(ROOT/'protocol.json');curation=read(ROOT/'curation-protocol.json')
    if protocol and curation:
        protocol={**protocol,'manifests':{**protocol['manifests'],'train':curation['manifests']['train-curated'],'validation':curation['manifests']['validation-curated']}}
    progress=read(active/'training_progress.json');evaluation=read(active/'progress.json')
    if progress and progress.get('example')==progress.get('examples_per_epoch') and not (active/'training_complete.json').exists():
        validation=active/f"epoch-{progress['epoch']}/validation"
        if (validation.parent/'adapter').exists() and not (validation/'metrics.json').exists():
            state={**state,'pipeline_stage':state['stage'],'stage':f"Validation after epoch {progress['epoch']}: {active.name}"}
            progress=None;evaluation=read(validation/'progress.json')
    experiments=read(ROOT/'experiments.json') or []
    for experiment in experiments:
        if experiment['name'].startswith('trial-'):
            folder=ROOT/'trials'/experiment['name'][6:]
            best=read(folder/'best.json')
            if best:experiment['resource_scope']=read(folder/f"epoch-{best['epoch']}/validation/resource-scope.json")
    return {'run_directory':str(ROOT),'status':state,'protocol':protocol,'curation':curation,'selection':read(ROOT/'selection.json'),
            'progress':progress,'evaluation':evaluation,
            'training_timing':recent_timing(active/'training.jsonl'),
            'experiments':experiments,'final':read(ROOT/'final-summary.json') if state['status']=='completed' else None,
            'audit_tail':log.read_text(encoding='utf-8',errors='replace')[-1200:] if log.exists() else '',
            'failure':read(ROOT/'failure.json') if state['status']=='failed' else None}

@router.get('/research-v2',response_class=HTMLResponse)
def monitor():
    return (Path(__file__).parent/'scale_monitor.html').read_text(encoding='utf-8')
