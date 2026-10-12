"""Read-only study dashboard; never launches a second GPU model during training."""
import json,os
from pathlib import Path
from fastapi import APIRouter,HTTPException
from fastapi.responses import FileResponse
router=APIRouter()
ROOT=Path(os.environ.get('OCR_RUN_ROOT','D:/OCR/runs/word-pilot-v1'))
DATA=Path(os.environ.get('OCR_DATA_ROOT','D:/OCR/research'))

def read(path):
    try:return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError,ValueError):return None

def lines(path):
    try:return [json.loads(s) for s in Path(path).read_text(encoding='utf-8').splitlines() if s.strip()]
    except (OSError,ValueError):return []

@router.get('/api/study')
def study():
    baseline=lines(ROOT/'baseline-test/predictions.jsonl')
    adapted=lines(ROOT/'adapted-test/predictions.jsonl')
    base={r['example_id']:r for r in baseline}
    indices={r['example_id']:i for i,r in enumerate(lines(ROOT/'test.jsonl'))}
    samples=[{**r,'baseline':base.get(r['example_id'],{}).get('prediction'),
              'image_url':f"/api/study/image/{indices[r['example_id']]}"} for r in adapted[:12]]
    status=read(ROOT/'status.json')
    analysis=read(ROOT/'analysis.json')
    failure_cases=[{**r,'prediction':r['adapted'],'image_url':f"/api/study/image/{indices[r['example_id']]}"}
        for r in (analysis or {}).get('largest_adapted_errors',[])]
    if status and status.get('stage')=='train' and (ROOT/'trained/training.json').exists():
        status={**status,'stage':'validation'}
    return {'audit':read(DATA/'audit_summary.json'),'protocol':read(ROOT/'protocol.json'),
        'status':status,'progress':read(ROOT/'trained/training_progress.json'),
        'probe':read('D:/OCR/runs/probe-overfit/probe.json'),
        'validation':read(ROOT/'trained/validation/metrics.json'),
        'baseline':read(ROOT/'baseline-test/metrics.json'),'adapted':read(ROOT/'adapted-test/metrics.json'),
        'evaluation_progress':{'baseline':len(baseline),'adapted':len(adapted),'validation':len(lines(ROOT/'trained/validation/predictions.jsonl'))},'samples':samples,
        'analysis':analysis,'failure_cases':failure_cases,
        'failures':[value for p in [ROOT/'trained/failure.json',ROOT/'baseline-test/failure.json',ROOT/'adapted-test/failure.json'] if (value:=read(p))]}

@router.get('/api/study/image/{index}')
def image(index:int):
    rows=lines(ROOT/'test.jsonl')
    if index<0 or index>=len(rows):raise HTTPException(404)
    candidate=(DATA/rows[index]['local_relative_path']).resolve()
    if not candidate.is_relative_to((DATA/'images').resolve()):raise HTTPException(404)
    return FileResponse(candidate)
