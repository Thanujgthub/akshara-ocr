"""Local human-review queue. Never edits frozen references or trains on submitted edits."""
import hashlib,json,uuid
from datetime import datetime,timezone
from pathlib import Path
from typing import Literal
from fastapi import APIRouter,HTTPException
from fastapi.responses import FileResponse,HTMLResponse
from pydantic import BaseModel,Field
from .study_routes import read

router=APIRouter();ROOT=Path('D:/OCR/runs/word-scale-v2');DATA=Path('D:/OCR/research-v2')
Source=Literal['training-quarantine','validation-errors','scale-validation-errors']

def queue(source):
    path=ROOT/({'training-quarantine':'crop-review-quarantine.jsonl',
                'validation-errors':'pilot-validation-review-queue.jsonl',
                'scale-validation-errors':'diagnostics/control-v2/review-queue.jsonl'}[source])
    if not path.exists():return []
    rows=[json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]
    if source=='training-quarantine':rows=[r for r in rows if r['original_split']=='train']
    if source=='scale-validation-errors':
        if any(r.get('split')!='validation' for r in rows):raise HTTPException(409,'Validation review queue contains an invalid split')
        rows=[{**r,'prediction':r['outputs']['literal_control']['prediction'],'original_split':'validation'} for r in rows]
    return rows

def row_at(source,index):
    rows=queue(source)
    if index<0 or index>=len(rows):raise HTTPException(404,'Review item not found')
    return rows[index],len(rows)

def annotation_folder(source,eid):
    return ROOT/'human-review'/source/hashlib.sha256(eid.encode()).hexdigest()

@router.get('/api/review-v2')
def item(source:Source='training-quarantine',index:int=0):
    row,total=row_at(source,index)
    folder=annotation_folder(source,row['example_id']);versions=sorted(folder.glob('*.json'))
    latest=read(versions[-1]) if versions else None
    reasons=list(row.get('review_reasons',row.get('observed_categories',row.get('uncertainty_flags',[]))))
    if row.get('prediction') is not None:
        from .research_policy import flags
        reasons=sorted(set(reasons+flags(row['prediction'])['uncertainty_flags']))
    return {'source':source,'index':index,'total':total,'example_id':row['example_id'],
            'source_label':row.get('transcription_raw',row.get('reference','')),
            'prediction':row.get('prediction'),'reasons':reasons,
            'source_label_status':row.get('label_status',row.get('source_label_status','source-ground-truth')),
            'matched_outputs':{name:record['prediction'] for name,record in row.get('outputs',{}).items()},
            'image_url':f'/api/review-v2/image?source={source}&index={index}',
            'latest_annotation':latest,'annotation_versions':len(versions),
            'training_policy':'Review is saved separately. No automatic relabeling, recropping, training or changes to frozen manifests. Validation examples remain held out.'}

@router.get('/api/review-v2/image')
def image(source:Source='training-quarantine',index:int=0):
    row,_=row_at(source,index)
    if source!='validation-errors':candidate=(DATA/row['local_relative_path']).resolve();allowed=(DATA/'images').resolve()
    else:candidate=Path(row['image_path']).resolve();allowed=Path('D:/OCR/research/images').resolve()
    if not candidate.is_relative_to(allowed) or not candidate.is_file():raise HTTPException(404,'Image unavailable')
    return FileResponse(candidate)

class Annotation(BaseModel):
    source:Source
    index:int=Field(ge=0)
    example_id:str=Field(min_length=1,max_length=1000)
    decision:Literal['label_matches_image','label_mismatch','multiple_words_or_form','unreadable','needs_recrop','unsure']
    verified_transcript:str=Field(default='',max_length=4000)
    writer_id:str=Field(default='',max_length=200)
    notes:str=Field(default='',max_length=4000)
    human_verified:bool=False

@router.post('/api/review-v2')
def annotate(value:Annotation):
    row,_=row_at(value.source,value.index)
    if row['example_id']!=value.example_id:raise HTTPException(409,'Review item changed; reload before saving')
    if not value.human_verified:raise HTTPException(422,'Confirm that you reviewed the source image yourself')
    folder=annotation_folder(value.source,value.example_id);folder.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc);version=stamp.strftime('%Y%m%dT%H%M%S%fZ')+'-'+uuid.uuid4().hex
    record={**value.model_dump(),'version':version,'created_utc':stamp.isoformat(),
            'original_source_label':row.get('transcription_raw',row.get('reference','')),
            'source_image_sha256':row.get('original_sha256'),
            'status':'human_review_record_only','included_in_training':False,
            'normalization_applied':False,'original_split':row.get('original_split','validation')}
    with (folder/(version+'.json')).open('x',encoding='utf-8') as f:json.dump(record,f,ensure_ascii=False,indent=2)
    return {'saved':True,'version':version,'included_in_training':False,'frozen_data_changed':False}

@router.get('/review-v2',response_class=HTMLResponse)
def page():return (Path(__file__).parent/'review_monitor.html').read_text(encoding='utf-8')
