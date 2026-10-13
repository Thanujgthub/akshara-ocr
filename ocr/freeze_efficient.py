"""Select capped whole-component splits from existing audited pools, without downloads."""
import argparse,hashlib,json,random,time,unicodedata,zipfile
from collections import Counter,defaultdict
from pathlib import Path
from PIL import Image,ImageOps
from .freeze_scale import read,write
from .audit_archives import digest_file,inspect_image
from .research_policy import crop_review_reasons,uniform_visible_input
from .research_io import save

OLD=Path('D:/OCR/runs/word-scale-v2')
DATA=Path('D:/OCR/research-v2')
PILOT=Path('D:/OCR/runs/word-pilot-v1')
ROOT=Path('D:/OCR/runs/word-efficient-v3')
SEED=20261013


def exact_components(groups,target,seed):
    """Deterministic 0/1 subset sum. Never split a leakage component to fill a count."""
    items=sorted(groups.items());random.Random(seed).shuffle(items)
    reachable=1;mask=(1<<(target+1))-1;parent={}
    for i,(_,members) in enumerate(items):
        size=len(members)
        if not size or size>target:continue
        added=((reachable<<size)&mask)&~reachable
        pending=added
        while pending:
            bit=pending&-pending;count=bit.bit_length()-1
            parent[count]=(count-size,i);pending-=bit
        reachable|=added
        if reachable&(1<<target):break
    actual=target if reachable&(1<<target) else reachable.bit_length()-1
    selected=[];count=actual
    while count:
        count,i=parent[count];selected.append(items[i])
    rows=[r for _,members in sorted(selected) for r in members]
    assert len(rows)==actual
    return rows


def check_isolation(splits):
    for field in ['example_id','leakage_group','group_id','original_sha256','pixel_sha256']:
        names=list(splits)
        for i,a in enumerate(names):
            for b in names[i+1:]:
                if {r[field] for r in splits[a]}&{r[field] for r in splits[b]}:
                    raise RuntimeError(f'Split overlap: {field} {a}/{b}')


def exposed_ids():
    ids=set();sources=[]
    for path in [PILOT/f'{s}.jsonl' for s in ['train','validation','test']]+[OLD/'trial-train-curated.jsonl']:
        ids.update(r['example_id'] for r in read(path));sources.append(str(path))
    for path in Path('D:/OCR/runs').rglob('predictions.jsonl'):
        if ROOT in path.parents:continue
        # Identity only; historical test references/predictions do not influence settings.
        ids.update(r['example_id'] for r in read(path));sources.append(str(path))
    def walk(value):
        if isinstance(value,dict):
            if isinstance(value.get('example_id'),str):ids.add(value['example_id'])
            for v in value.values():walk(v)
        elif isinstance(value,list):
            for v in value:walk(v)
    for folder in Path('D:/OCR/runs').glob('probe*'):
        for path in folder.rglob('*.json'):
            try:walk(json.loads(path.read_text(encoding='utf-8')));sources.append(str(path))
            except (ValueError,UnicodeError):continue
    return ids,sources


def main():
    if (ROOT/'protocol.json').exists():
        protocol=json.loads((ROOT/'protocol.json').read_text(encoding='utf-8'))
        for name,v in protocol['manifests'].items():
            if digest_file(ROOT/(name+'.jsonl'))!=v['sha256']:raise RuntimeError('Frozen v3 manifest changed')
        print(json.dumps({'already_frozen':True,'counts':{n:v['count'] for n,v in protocol['manifests'].items()}}));return
    ROOT.mkdir(parents=True,exist_ok=True);started=time.time()
    save(ROOT/'status.json',{'status':'preparing','stage':'Audit existing pools and freeze capped manifests'})
    oldprotocol=json.loads((OLD/'curation-protocol.json').read_text(encoding='utf-8'))
    pools={'train':OLD/'train-curated.jsonl','validation':OLD/'validation-curated.jsonl','final-test':OLD/'unused-holdout.jsonl'}
    for name,path in pools.items():
        if name!='final-test' and digest_file(path)!=oldprotocol['manifests'][name+'-curated']['sha256']:
            raise RuntimeError('Historical curated manifest changed')
    known_ids,exposure_sources=exposed_ids();docs=set();known_bytes=set();known_pixels=set()
    pixel_labels={};conflicts=set();source_records=0
    for path in sorted((DATA/'manifests').glob('word_*.jsonl')):
        for line in path.open(encoding='utf-8'):
            if not line.strip():continue
            r=json.loads(line);source_records+=1;label=hashlib.sha256(r['transcription_raw'].encode('utf-8')).hexdigest()
            old=pixel_labels.setdefault(r['pixel_sha256'],label)
            if old!=label:conflicts.add(r['pixel_sha256'])
            if r['example_id'] in known_ids:
                docs.add(r['group_id']);known_bytes.add(r['original_sha256']);known_pixels.add(r['pixel_sha256'])
    labels={};label_files={}
    for archive in ['trainIIIT.zip','valIIIT.zip','testIIIT.zip']:
        with zipfile.ZipFile(Path('D:/OCR')/archive) as z:
            name=next(n for n in z.namelist() if n.count('/')==1 and n.endswith('_gt.txt'))
            raw=z.read(name);prefix=name.split('/')[0]+'/';mapping={}
            for line in raw.decode('utf-8-sig').splitlines():
                key,text=line.split('\t',1);key=prefix+key.replace('\\','/')
                if key in mapping and mapping[key]!=text:raise RuntimeError('Conflicting source path labels')
                mapping[key]=text
            labels[archive]=mapping;label_files[archive]={'member':name,'sha256':hashlib.sha256(raw).hexdigest()}
    eligible={};rejected=[];poolcounts={};exposed_groups=set()
    for name,path in pools.items():
        raw=read(path);groups=defaultdict(list);poolcounts[name]=len(raw)
        forbidden=set()
        for r in raw:
            if r['pixel_sha256'] in conflicts:forbidden.add(r['leakage_group'])
            if name=='final-test' and (r['example_id'] in known_ids or r['group_id'] in docs or
                r['original_sha256'] in known_bytes or r['pixel_sha256'] in known_pixels):
                forbidden.add(r['leakage_group']);exposed_groups.add(r['leakage_group'])
        seen=set()
        for r in raw:
            reasons=[];text=r['transcription_raw']
            if r['leakage_group'] in forbidden:reasons.append('prior_exposure_or_conflicting_duplicate_component')
            if r['license_ref']!='CC-BY-4.0' or r['source_dataset']!='iiit-words':reasons.append('license_source_not_verified')
            if labels[r['archive']].get(r['source_image_id'])!=text:reasons.append('source_label_path_mismatch')
            if not text.strip() or any(unicodedata.category(c)=='Cc' or c=='\ufffd' for c in text):reasons.append('invalid_label')
            if any(unicodedata.category(c).startswith('L') and not '\u0c00'<=c<='\u0c7f' for c in text):reasons.append('foreign_label_requires_review')
            reasons+=crop_review_reasons(r)
            if r['pixel_sha256'] in seen:reasons.append('exact_pixel_duplicate')
            if reasons:rejected.append({'example_id':r['example_id'],'pool':name,'reasons':sorted(set(reasons))});continue
            seen.add(r['pixel_sha256'])
            groups[r['leakage_group']].append({**r,'split':name,'transcription_sha256':hashlib.sha256(text.encode('utf-8')).hexdigest(),
                'selection_version':'word-efficient-v3','writer_identity':'unknown','human_label_verification':'source-ground-truth; not newly human verified'})
        eligible[name]=groups
    targets={'train':25000,'validation':5000,'final-test':3000}
    splits={name:exact_components(eligible[name],n,SEED+i) for i,(name,n) in enumerate(targets.items())}
    check_isolation(splits)
    checks=[];failures=[]
    for name,selected in splits.items():
        for i,r in enumerate(selected):
            try:
                path=(DATA/r['local_relative_path']).resolve()
                if not path.is_relative_to((DATA/'images').resolve()):raise ValueError('Image path escapes data root')
                raw=path.read_bytes()
                if hashlib.sha256(raw).hexdigest()!=r['original_sha256']:raise ValueError('Byte hash mismatch')
                size,dh,pixel=inspect_image(raw)
                if pixel!=r['pixel_sha256'] or size!=(r['width'],r['height']):raise ValueError('Pixel/dimension mismatch')
                with Image.open(path) as image:
                    if uniform_visible_input(ImageOps.exif_transpose(image)):raise ValueError('Uniform image')
            except Exception as e:failures.append({'example_id':r['example_id'],'split':name,'error':str(e)})
            if (i+1)%1000==0:print(json.dumps({'audit_split':name,'checked':i+1,'selected':len(selected),'failures':len(failures)}),flush=True)
        checks.append({'split':name,'checked':len(selected)})
    audit={'source_label_records_scanned':source_records,'conflicting_pixel_labels':len(conflicts),'prior_exposed_identity_count':len(known_ids),
        'prior_exposure_sources':exposure_sources,'source_label_files':label_files,'input_manifests':{n:{'path':str(p),'sha256':digest_file(p),'count':poolcounts[n]} for n,p in pools.items()},
        'eligible_pool_counts':{n:sum(map(len,g.values())) for n,g in eligible.items()},'selected_counts':{n:len(v) for n,v in splits.items()},
        'technical_image_checks':checks,'image_failures':failures,'excluded_counts_by_reason':dict(Counter(reason for r in rejected for reason in r['reasons'])),
        'elapsed_seconds':time.time()-started,'human_label_quality':'Technical label/path/Unicode and image/hash verification; full human semantic review incomplete',
        'license':'Official IIIT portal confirms CC BY4.0; https://ilocr.iiit.ac.in/dataset/23/; verified13October2026',
        'historical_final_policy':'Old1,016 final examples not used; new final selected only from unused holdout, excluding all known trained/evaluated/probe identities/components.'}
    save(ROOT/'dataset-audit.json',audit)
    write(ROOT/'excluded.jsonl',rejected)
    if failures:raise RuntimeError('Selected image audit failed; no split manifests frozen. Inspect dataset-audit.json')
    if len(splits['validation'])!=5000 or len(splits['final-test'])!=3000:raise RuntimeError('Exact whole-component heldout targets unavailable; report real counts, do not relax isolation')
    if not 0<len(splits['train'])<=25000:raise RuntimeError('Training cap violated')
    manifests={name:write(ROOT/(name+'.jsonl'),selected) for name,selected in splits.items()}
    save(ROOT/'protocol.json',{'seed':SEED,'manifests':manifests,'training_cap':25000,'maximum_initial_epochs':1,
        'selection':'Whole leakage components, deterministic exact subset sum within preserved outer split roles; exact pixel duplicates excluded.',
        'data_root':str(DATA),'base_model':'D:/OCR/models/indic-ocr','original_revision':'cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25',
        'label_quality':audit['human_label_quality'],'writer_identity':'unknown; source-document and duplicate grouping only','pretraining_overlap':'unknown',
        'final_test_policy':'Sealed after technical audit, no final predictions until validation-only model selection is locked.',
        'attribution':'IIIT Hyderabad; Gongidi & Jawahar, IIIT-INDIC-HW-WORDS, ICDAR2021; CC BY4.0; https://ilocr.iiit.ac.in/dataset/23/'})
    save(ROOT/'status.json',{'status':'prepared','stage':'Capped manifests frozen; baseline comparison and smoke pending'})
    print(json.dumps({'frozen':{n:v['count'] for n,v in manifests.items()},'elapsed_seconds':time.time()-started}),flush=True)


if __name__=='__main__':main()
