from pathlib import Path
import argparse
import json
from .data import audit, read_tsv, splits, write_jsonl, sha256
from .metrics import corpus

def main():
    parser=argparse.ArgumentParser(description='Akshara local OCR toolkit')
    sub=parser.add_subparsers(dest='command',required=True)
    a=sub.add_parser('audit'); a.add_argument('--root',required=True);a.add_argument('--source',required=True);a.add_argument('--license-ref',required=True);a.add_argument('--granularity',choices=['page','line','block','word'],default='page');a.add_argument('--labels-tsv');a.add_argument('--output',required=True)
    s=sub.add_parser('split');s.add_argument('--manifest',required=True);s.add_argument('--output',required=True);s.add_argument('--seed',type=int,default=42);s.add_argument('--validation',type=int,default=500);s.add_argument('--test',type=int,default=500);s.add_argument('--minimum-train',type=int,default=1000)
    e=sub.add_parser('evaluate');e.add_argument('--input',required=True);e.add_argument('--output',required=True)
    p=sub.add_parser('predict');p.add_argument('--image',required=True);p.add_argument('--output',required=True);p.add_argument('--mode',choices=['word','page'],default='page');p.add_argument('--variant',choices=['adapted','original'],default='adapted')
    args=parser.parse_args()
    if args.command=='audit':
        rows,rejected=audit(args.root,args.source,args.license_ref,args.granularity,read_tsv(args.labels_tsv) if args.labels_tsv else None)
        write_jsonl(args.output,rows);Path(args.output+'.audit.json').write_text(json.dumps({'usable_source_pairs':len(rows),'human_verified_pairs':0,'rejected':rejected,'warning':'Human review required for language/domain/label correctness. Near duplicates grouped conservatively; writer-disjointness not established.'},ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({'usable_source_pairs':len(rows),'rejected':len(rejected)}))
    elif args.command=='split':
        rows=[json.loads(l) for l in Path(args.manifest).read_text(encoding='utf-8').splitlines() if l.strip()]
        result,shortfalls=splits(rows,args.seed,args.validation,args.test,args.minimum_train)
        out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
        hashes={}
        for name,items in result.items():
            path=out/(name+'.jsonl');write_jsonl(path,items);hashes[name]=sha256(path)
        report={'seed':args.seed,'counts':{k:len(v) for k,v in result.items()},'shortfalls':shortfalls,'sha256':hashes,'writer_disjoint':False}
        (out/'freeze.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
    elif args.command=='evaluate':
        rows=[json.loads(l) for l in Path(args.input).read_text(encoding='utf-8').splitlines() if l.strip()]
        result=corpus(rows);out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='per_example'}))
    elif args.command=='predict':
        from .model import predict
        result=predict(Path(args.image),args.mode,args.variant);out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__': main()
