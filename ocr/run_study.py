"""Frozen local pilot: 1,000 train / 500 validation / 500 test, one epoch.

Test outputs are generated only after all adaptation decisions are fixed.
Each model process exits before the next loads, bounding laptop memory use.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from ocr.experiment import read_manifest, save

ROOT=Path('D:/OCR/runs/word-pilot-v1')
def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    freeze={}
    for split,count in [('train',1000),('validation',500),('test',500)]:
        path=ROOT/f'{split}.jsonl'
        if not path.exists():
            rows=read_manifest(f'D:/OCR/research/manifests/word_{split}.jsonl',count)
            if len(rows)!=count:raise RuntimeError('Insufficient verified samples')
            path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
        freeze[split]={'count':len(path.read_text(encoding='utf-8').splitlines()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    save(ROOT/'protocol.json',{'splits':freeze,'seed':42,'epochs':1,'learning_rate':1e-5,
        'gradient_accumulation':4,'lora_rank':8,'lora_alpha':16,'lora_dropout':0.05,
        'selection':'single prespecified epoch; no test-guided hyperparameter selection',
        'scope':'word recognition pilot; not page-level benchmark','writer_disjointness':'unverified'})
    jobs=[['train','--manifest',str(ROOT/'train.jsonl'),'--validation',str(ROOT/'validation.jsonl'),'--output',str(ROOT/'trained')],
          ['evaluate','--manifest',str(ROOT/'test.jsonl'),'--output',str(ROOT/'baseline-test')],
          ['evaluate','--manifest',str(ROOT/'test.jsonl'),'--adapter',str(ROOT/'trained/adapter'),'--output',str(ROOT/'adapted-test')]]
    for job in jobs:
        stage=job[0] if job[0]=='train' else Path(job[job.index('--output')+1]).name
        save(ROOT/'status.json',{'stage':stage,'status':'running'})
        subprocess.run([sys.executable,'-m','ocr.experiment',*job],check=True)
    save(ROOT/'status.json',{'stage':'complete','status':'completed'})
if __name__=='__main__':main()
