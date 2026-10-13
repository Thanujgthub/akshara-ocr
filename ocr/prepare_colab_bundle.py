"""Package existing selected files only. No downloads, relabeling or split changes."""
import argparse,json,subprocess,zipfile
from pathlib import Path
from .checkpoint_io import sha,file_hashes
from .research_io import save


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',default='D:/OCR/runs/word-efficient-v3');p.add_argument('--data',default='D:/OCR/research-v2');p.add_argument('--model',default='D:/OCR/models/indic-ocr');p.add_argument('--pilot',default='D:/OCR/runs/word-pilot-v1/trained/adapter');p.add_argument('--output',required=True);a=p.parse_args()
    project=Path(__file__).resolve().parents[1];out=Path(a.output);run=Path(a.run);data=Path(a.data);model=Path(a.model);pilot=Path(a.pilot)
    if out.exists() and any(out.iterdir()):raise RuntimeError('Bundle destination must be empty; preserve previous archives')
    out.mkdir(parents=True,exist_ok=True);archives=[]
    def archive(name,entries):
        target=out/name;size=0;count=0
        with zipfile.ZipFile(target,'w',zipfile.ZIP_STORED,allowZip64=True) as z:
            for source,destination in entries:
                z.write(source,destination);size+=source.stat().st_size;count+=1
        archives.append({'file':name,'sha256':sha(target),'bytes':target.stat().st_size,'uncompressed_bytes':size,'files':count})
    names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=project,text=True).splitlines()
    allowed=[]
    for name in names:
        path=Path(name)
        if path.parts[0] in {'ocr','tests','notebooks','configs','reports'} or path.name in {'AGENTS.md','PROJECT_STATE.md','WORK_LOG.md','README.md','requirements.txt','requirements-colab.txt','COLAB_MIGRATION.md'}:
            if '__pycache__' not in path.parts and path.suffix not in {'.pyc','.zip','.pt','.safetensors'}:allowed.append((project/path,'project/'+path.as_posix()))
    archive('akshara-source.zip',allowed)
    provenance=json.loads((project/'reports/model_provenance.json').read_text())
    entries=[]
    for item in provenance['files']:
        path=model/item['file']
        if sha(path)!=item['sha256']:raise RuntimeError('Original provenance mismatch')
        entries.append((path,'inputs/model/'+item['file']))
    # Original shard may exceed1GiB; never split or convert its contents.
    archive('indic-ocr-original.zip',entries)
    pilot_hashes=file_hashes(pilot);save(out/'pilot-checksums.json',pilot_hashes)
    archive('pilot-adapter.zip',[(p,'inputs/pilot/'+p.relative_to(pilot).as_posix()) for p in pilot.rglob('*') if p.is_file()]+[(out/'pilot-checksums.json','inputs/pilot-checksums.json')])
    protocol=json.loads((run/'protocol.json').read_text());images={};records=[]
    for split,expected in protocol['manifests'].items():
        path=run/(split+'.jsonl')
        if sha(path)!=expected['sha256']:raise RuntimeError('Frozen manifest mismatch')
        records.append((path,'inputs/protocol/'+path.name))
        rows=[json.loads(s) for s in path.read_text(encoding='utf-8').splitlines()]
        if len(rows)!=expected['count']:raise RuntimeError('Frozen count mismatch')
        for row in rows:
            rel=row['local_relative_path'];path=(data/rel).resolve()
            if not path.is_relative_to(data.resolve()) or sha(path)!=row['original_sha256']:raise RuntimeError('Selected image mismatch: '+rel)
            images[rel]=path
    for p in run.glob('*.json'):
        if p.name not in {'status.json','failure.json','colab-handoff-hold.json'}:records.append((p,'inputs/protocol/'+p.name))
    archive('frozen-protocol.zip',records)
    chunk=[];size=0;number=1
    for rel,path in sorted(images.items()):
        if chunk and size+path.stat().st_size>1024**3:
            archive(f'selected-images-{number:03d}.zip',chunk);number+=1;chunk=[];size=0
        chunk.append((path,'inputs/data/'+rel));size+=path.stat().st_size
    if chunk:archive(f'selected-images-{number:03d}.zip',chunk)
    save(out/'transfer-index.json',{'archives':archives,'counts':{k:v['count'] for k,v in protocol['manifests'].items()},'source_git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=project,text=True).strip(),'source_dirty_at_bundle':bool(subprocess.check_output(['git','status','--porcelain'],cwd=project,text=True).strip()),'policy':'Private transfer only; source ground truth not fully human verified; no training results or speedup claimed; final labels sealed for selection.'})
    print(json.dumps({'archives':len(archives),'unique_images':len(images),'total_archive_bytes':sum(x['bytes'] for x in archives)},indent=2))

if __name__=='__main__':main()
