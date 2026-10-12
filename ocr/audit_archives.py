"""Audit supplied archives, freeze source-disjoint research manifests without extracting arbitrary ZIP paths."""
from pathlib import Path
import argparse, hashlib, io, json, random, time, unicodedata, zipfile
from collections import Counter, defaultdict
from PIL import Image, ImageOps

def digest_file(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

def dump(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')

def inspect_image(data):
    with Image.open(io.BytesIO(data)) as im:
        im.load(); im=ImageOps.exif_transpose(im).convert('RGB'); size=im.size
        gray=im.convert('L').resize((9,8));v=list(gray.getdata())
        dh=sum(int(v[y*9+x]>v[y*9+x+1])<<(y*8+x) for y in range(8) for x in range(8))
        pixel=hashlib.sha256(str(size).encode()+im.tobytes()).hexdigest()
    return size,dh,pixel

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',default='D:/OCR');p.add_argument('--output',default='D:/OCR/research');p.add_argument('--word-limit',type=int,default=0);p.add_argument('--words-only',action='store_true');p.add_argument('--retain-duplicates',action='store_true');a=p.parse_args()
    root,out=Path(a.root),Path(a.output);out.mkdir(parents=True,exist_ok=True)
    rows=[];rejected=[];inventories=[];seen={};pixel_seen={};bands=defaultdict(list);started=time.time()
    for archive in ['Page_Level_Telugu_Training_Set.zip','Page_Level_Telugu_Test_Set.zip','trainIIIT.zip','valIIIT.zip','testIIIT.zip']:
        if a.words_only and 'IIIT' not in archive:continue
        path=root/archive; print('Auditing '+archive,flush=True)
        sha=digest_file(path)
        with zipfile.ZipFile(path) as z:
            names=z.namelist(); images=[n for n in names if n.lower().endswith(('.jpg','.jpeg','.png'))]
            gran='word' if 'IIIT' in archive else 'page'; source='iiit-words' if gran=='word' else 'plhwtr-1'
            source_split={'trainIIIT.zip':'train','valIIIT.zip':'validation','testIIIT.zip':'test'}.get(archive,'external-test' if 'Test_Set' in archive else 'labeled-pool')
            if gran=='word':
                label_name=next(n for n in names if n.count('/')==1 and n.endswith('_gt.txt'))
                prefix=label_name.split('/')[0]+'/'
                labels={prefix:None};labels={}
                for line in z.read(label_name).decode('utf-8-sig').splitlines():
                    parts=line.split('\t',1)
                    if len(parts)==2:labels[prefix+parts[0].replace('\\','/')]=parts[1]
            else:
                label_names={n for n in names if n.endswith('.txt')}
                labels={n:z.read(str(Path(n).with_suffix('.txt')).replace('\\','/')).decode('utf-8-sig') for n in images if str(Path(n).with_suffix('.txt')).replace('\\','/') in label_names}
            inventory={'archive':archive,'sha256':sha,'images':len(images),'labels':len(labels),'granularity':gran,'source_split':source_split,'verified':0}
            inventories.append(inventory)
            dump(out/'archive_inventory.json',inventories)
            if source_split=='external-test':
                print('External unlabeled test excluded from metrics: '+str(len(images)),flush=True);continue
            candidates=sorted(labels)
            random.Random(42).shuffle(candidates)
            if gran=='word' and a.word_limit:candidates=candidates[:a.word_limit]
            for idx,name in enumerate(candidates):
                text=labels[name]
                if not text.strip() or not any('\u0c00'<=c<='\u0c7f' for c in text):
                    rejected.append({'archive':archive,'image':name,'reason':'empty/non-Telugu label'});continue
                try:
                    data=z.read(name);size,dh,pixel=inspect_image(data)
                except Exception as e:
                    rejected.append({'archive':archive,'image':name,'reason':str(e)});continue
                h=hashlib.sha256(data).hexdigest();eid=source+':'+name
                if not a.retain_duplicates and (h in seen or pixel in pixel_seen):
                    rejected.append({'archive':archive,'image':name,'reason':'exact bytes/pixels duplicate','of':seen.get(h,pixel_seen.get(pixel))});continue
                seen[h]=eid;pixel_seen[pixel]=eid
                # Group all sibling word crops from each source page. First numeric component is
                # retained as a writer candidate, not claimed to be verified writer metadata.
                group=source+':'+('/'.join(name.split('/')[2:-1]) if gran=='word' else Path(name).stem)
                candidates_near=set()
                for band in range(4):candidates_near.update(bands[(gran,band,(dh>>(band*16))&65535)])
                near=[]
                for j in candidates_near:
                    r=rows[j]
                    if (dh^int(r['dhash'],16)).bit_count()<=3 and abs(size[0]/size[1]-r['width']/r['height'])<0.08:
                        near.append(r['example_id'])
                record={'example_id':eid,'source_dataset':source,'source_split':source_split,'source_image_id':name,
                    'archive':archive,'original_sha256':h,'pixel_sha256':pixel,'group_id':group,'granularity':gran,
                    'script':'Telugu','domain':'handwritten','transcription_raw':text,'transcription_nfc':unicodedata.normalize('NFC',text),
                    'label_status':'source-ground-truth','annotation_version':'original','license_ref':'CC-BY-4.0' if gran=='word' else 'PLHWTR-project-research-only-unclarified',
                    'width':size[0],'height':size[1],'dhash':f'{dh:016x}','near_duplicate_candidates':near,
                    'local_relative_path':f'images/{gran}/{h}.jpg'}
                for band in range(4):bands[(gran,band,(dh>>(band*16))&65535)].append(len(rows))
                rows.append(record);dest=out/record['local_relative_path'];dest.parent.mkdir(parents=True,exist_ok=True)
                if not dest.exists():dest.write_bytes(data)
                inventory['verified']+=1
                if idx%1000==0:print(f'{archive}: {idx}/{len(candidates)} examined, {inventory["verified"]} usable',flush=True)
            dump(out/'archive_inventory.json',inventories)
        print(f'Finished {archive}: {inventory["verified"]} verified',flush=True)
    # Union source documents and near duplicates before assigning any splits.
    parents={r['example_id']:r['example_id'] for r in rows}
    def find(x):
        while parents[x]!=x:parents[x]=parents[parents[x]];x=parents[x]
        return x
    def union(x,y):parents[find(y)]=find(x)
    group_first={};exact_first={}
    for r in rows:
        g=r['group_id'];e=r['example_id']
        if g in group_first:union(e,group_first[g])
        else:group_first[g]=e
        for key in [r['original_sha256'],r['pixel_sha256']]:
            if key in exact_first:union(e,exact_first[key])
            else:exact_first[key]=e
        for other in r['near_duplicate_candidates']:union(e,other)
    groups=defaultdict(list)
    for r in rows:groups[(r['granularity'],find(r['example_id']))].append(r)
    assignments=defaultdict(list);overlap_groups=0
    for gran in ['page','word']:
        gs=[v for (g,_),v in groups.items() if g==gran]
        random.Random(42).shuffle(gs)
        if gran=='page':
            counts=Counter()
            for group in gs:
                split='test' if counts['test']<500 else 'validation' if counts['validation']<500 else 'train'
                for r in group:r['split']=split;r['leakage_group']=find(r['example_id']);assignments[gran+'_'+split].append(r)
                counts[split]+=len(group)
        else:
            for group in gs:
                origins={r['source_split'] for r in group}
                # Holdout precedence: remove cross-split groups from training and retain together.
                if len(origins)>1:overlap_groups+=1
                split='test' if 'test' in origins else 'validation' if 'validation' in origins else 'train'
                for r in group:r['split']=split;assignments[gran+'_'+split].append(r)
    freeze={}
    for name,items in assignments.items():
        target=out/'manifests'/(name+'.jsonl');target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in items),encoding='utf-8')
        freeze[name]={'count':len(items),'sha256':digest_file(target)}
    summary={'archives':inventories,'frozen_splits':freeze,'rejected_count':len(rejected),'word_cross_split_groups_reassigned':overlap_groups,
       'writer_disjointness':'unverified; source-document and near-duplicate groups kept together',
       'near_duplicate_method':'64-bit dHash <=3 and aspect-ratio difference <0.08; conservative candidates unioned',
       'page_license_status':'terms clarification still needed before training; audit only',
       'elapsed_seconds':time.time()-started}
    dump(out/'audit_summary.json',summary);dump(out/'rejections.json',rejected)
    print(json.dumps(summary,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
