"""Seal scale-up manifests using full audit components, never pilot test labels for selection."""
import json,hashlib,random,zipfile,unicodedata
from collections import defaultdict,Counter
from pathlib import Path
from ocr.audit_archives import digest_file,dump

ROOT=Path('D:/OCR/runs/word-scale-v2');DATA=Path('D:/OCR/research-v2');PILOT=Path('D:/OCR/runs/word-pilot-v1')
def read(p):return [json.loads(s) for s in Path(p).read_text(encoding='utf-8').splitlines() if s.strip()]
def write(p,rows):
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():raise RuntimeError('Refusing to replace frozen manifest '+str(p))
    p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
    return {'count':len(rows),'sha256':digest_file(p)}

def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    if (ROOT/'protocol.json').exists():return
    if not (DATA/'audit_summary.json').exists():raise RuntimeError('Full audit not finished')
    rows=sum([read(DATA/f'manifests/word_{s}.jsonl') for s in ['train','validation','test']],[])
    # Reconstruct union graph independently of auditor output schema.
    parents={r['example_id']:r['example_id'] for r in rows}
    def find(x):
        while parents[x]!=x:parents[x]=parents[parents[x]];x=parents[x]
        return x
    def union(a,b):parents[find(b)]=find(a)
    first={}
    for r in rows:
        for key in [('document',r['group_id']),('bytes',r['original_sha256']),('pixels',r['pixel_sha256'])]:
            if key in first:union(r['example_id'],first[key])
            else:first[key]=r['example_id']
        for e in r['near_duplicate_candidates']:union(r['example_id'],e)
    old=sum([read(PILOT/f'{s}.jsonl') for s in ['train','validation','test']],[])
    oldgroups={r['group_id'] for r in old};oldhash={r['original_sha256'] for r in old}
    oldhold=read(PILOT/'validation.jsonl')+read(PILOT/'test.jsonl')
    holdgroups={r['group_id'] for r in oldhold};holdhash={r['original_sha256'] for r in oldhold}
    # Inspect every original label record, including repeated path keys discarded by legacy parser.
    conflicts=set();label_inventory=[]
    for archive in ['trainIIIT.zip','valIIIT.zip','testIIIT.zip']:
        with zipfile.ZipFile(Path('D:/OCR')/archive) as z:
            name=next(n for n in z.namelist() if n.count('/')==1 and n.endswith('_gt.txt'))
            prefix=name.split('/')[0]+'/';seen={};same=0;malformed=0;count=0
            for line in z.read(name).decode('utf-8-sig').splitlines():
                count+=1;parts=line.split('\t',1)
                if len(parts)!=2:malformed+=1;continue
                key=prefix+parts[0].replace('\\','/');text=parts[1]
                if key in seen:
                    if seen[key]!=text:conflicts.add((archive,key))
                    else:same+=1
                seen[key]=text
            label_inventory.append({'archive':archive,'records':count,'unique_paths':len(seen),'identical_repeated_paths':same,'malformed_lines':malformed,'conflicting_paths':sum(a==archive for a,k in conflicts)})
    groups=defaultdict(list)
    for r in rows:r['leakage_group']=find(r['example_id']);groups[r['leakage_group']].append(r)
    quarantine=[];train=[];val=[];final_groups=[];unused=[]
    for gid,group in sorted(groups.items()):
        origins={r['source_split'] for r in group}
        conflict=any((r['archive'],r['source_image_id']) in conflicts for r in group)
        protected=any(r['group_id'] in holdgroups or r['original_sha256'] in holdhash for r in group)
        exposed=any(r['group_id'] in oldgroups or r['original_sha256'] in oldhash for r in group)
        # Foreign-letter labels, control characters and conflicts require human review, not repair.
        label_problem=any(any(unicodedata.category(c).startswith('L') and not '\u0c00'<=c<='\u0c7f' for c in r['transcription_raw']) or any(unicodedata.category(c)=='Cc' for c in r['transcription_raw']) for r in group)
        if conflict or label_problem:
            for r in group:quarantine.append({**r,'quarantine_reason':'conflicting_path_labels' if conflict else 'mixed_script_or_control_label_review'})
            continue
        # Keep only one representative of exact pixel duplicates, after graph allocation.
        unique={}
        for r in sorted(group,key=lambda x:x['example_id']):unique.setdefault(r['pixel_sha256'],r)
        group=list(unique.values())
        if 'test' in origins:
            if not exposed:final_groups.append(group)
            else:unused.extend(group)
        elif 'validation' in origins or protected:val.extend(group)
        else:train.extend(group)
    random.Random(20261013).shuffle(final_groups);final=[]
    for group in final_groups:
        if len(final)<1000:final.extend(group)
        else:unused.extend(group)
    if len(train)<10000 or len(final)<500:raise RuntimeError(f'Insufficient eligible data after leakage grouping: train={len(train)}, independent final={len(final)}; do not relax protections silently')
    random.Random(20261013).shuffle(val);validation=[];usedgroups=set()
    # At least 1,000 validation words, with whole components.
    for r in val:
        if len(validation)>=1000 and r['leakage_group'] not in usedgroups:continue
        usedgroups.add(r['leakage_group']);validation.append(r)
    # Include remaining siblings of chosen validation components.
    validation=[r for r in val if r['leakage_group'] in usedgroups]
    splitrows={'train':train,'validation':validation,'final-test':final}
    for field in ['leakage_group','group_id','original_sha256','pixel_sha256']:
        sets=[{r[field] for r in rr} for rr in splitrows.values()]
        if sets[0]&sets[1] or sets[0]&sets[2] or sets[1]&sets[2]:raise RuntimeError('Leakage check failed: '+field)
    manifests={s:write(ROOT/f'{s}.jsonl',rr) for s,rr in splitrows.items()}
    write(ROOT/'quarantine.jsonl',quarantine);write(ROOT/'unused-holdout.jsonl',unused)
    # Fixed short-trial subsets from training and validation only.
    tt=list(train);random.Random(42).shuffle(tt)
    vv=list(validation);random.Random(42).shuffle(vv)
    manifests['trial-train']=write(ROOT/'trial-train.jsonl',tt[:1000])
    manifests['trial-validation']=write(ROOT/'trial-validation.jsonl',vv[:300])
    dump(ROOT/'label_inventory.json',label_inventory)
    dump(ROOT/'protocol.json',{'manifests':manifests,'seed':42,'split_seed':20261013,
        'full_audit_sha256':digest_file(DATA/'audit_summary.json'),
        'pilot_manifest_hashes':{s:digest_file(PILOT/f'{s}.jsonl') for s in ['train','validation','test']},
        'final_test_policy':'New final test: unseen pilot source-document and exact/near-duplicate components from official test source. Locked until validation selection completed.',
        'writer_identity':'unknown; source-document candidate grouping only','pretraining_overlap':'unknown',
        'label_quality':'All source label records technically checked; human image/transcript review is NOT complete.',
        'attribution':'IIIT Hyderabad, Gongidi & Jawahar, IIIT-INDIC-HW-WORDS (ICDAR 2021), CC BY 4.0; https://ilocr.iiit.ac.in/dataset/23/',
        'scope':'isolated handwritten words; no sentence/page accuracy claim','quarantined':len(quarantine),
        'unused_holdout':len(unused),'maximum_full_epochs':2,
        'selection':'validation NFC CER primary; ties raw exact match; no final-test-guided selection'})
    print(json.dumps({'manifests':manifests,'quarantined':len(quarantine)}),flush=True)
if __name__=='__main__':main()
