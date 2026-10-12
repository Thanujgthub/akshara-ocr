"""Paired, source-document bootstrap analysis of the frozen word pilot."""
import json,random,statistics,difflib,regex
from collections import defaultdict
from pathlib import Path
from ocr.experiment import save
from ocr.metrics import compare
ROOT=Path('D:/OCR/runs/word-pilot-v1')
def rows(path):return [json.loads(s) for s in Path(path).read_text(encoding='utf-8').splitlines() if s.strip()]
def percentile(values,p):
    values=sorted(values);pos=(len(values)-1)*p;lo=int(pos);hi=min(lo+1,len(values)-1)
    return values[lo]+(values[hi]-values[lo])*(pos-lo)
def main():
    manifest={r['example_id']:r for r in rows(ROOT/'test.jsonl')}
    baseline=rows(ROOT/'baseline-test/predictions.jsonl');adapted=rows(ROOT/'adapted-test/predictions.jsonl')
    base={r['example_id']:r for r in baseline};adapt={r['example_id']:r for r in adapted}
    if set(base)!=set(manifest) or set(adapt)!=set(manifest):raise RuntimeError('Incomplete or different test sets')
    groups=defaultdict(lambda:[0,0,0]);improved=worsened=unchanged=0;failures=[]
    lengths=defaultdict(lambda:[0,0,0,0]);severity=defaultdict(int)
    for eid,row in manifest.items():
        b=compare(row['transcription_raw'],base[eid]['prediction']);a=compare(row['transcription_raw'],adapt[eid]['prediction'])
        value=groups[row['group_id']];value[0]+=b['grapheme_edits'];value[1]+=a['grapheme_edits'];value[2]+=a['reference_graphemes']
        bucket='1-3 graphemes' if a['reference_graphemes']<=3 else '4-6 graphemes' if a['reference_graphemes']<=6 else '7+ graphemes'
        value=lengths[bucket];value[0]+=1;value[1]+=b['grapheme_edits'];value[2]+=a['grapheme_edits'];value[3]+=a['reference_graphemes']
        severity['exact' if a['cer']==0 else 'CER <=25%' if a['cer']<=.25 else 'CER <=50%' if a['cer']<=.5 else 'CER >50%']+=1
        improved+=a['grapheme_edits']<b['grapheme_edits'];worsened+=a['grapheme_edits']>b['grapheme_edits'];unchanged+=a['grapheme_edits']==b['grapheme_edits']
        if a['cer'] and a['cer']>0:
            gold=regex.findall(r'\X',row['transcription_nfc']);pred=regex.findall(r'\X',adapt[eid]['prediction'])
            diff=[{'operation':tag,'reference':''.join(gold[i:j]),'prediction':''.join(pred[k:l])} for tag,i,j,k,l in difflib.SequenceMatcher(None,gold,pred,autojunk=False).get_opcodes()]
            failures.append({'example_id':eid,'reference':row['transcription_raw'],'baseline':base[eid]['prediction'],'adapted':adapt[eid]['prediction'],'cer':a['cer'],'path':row['local_relative_path'],'visual_diff':diff})
    rng=random.Random(42);values=list(groups.values());boot=[]
    for _ in range(2000):
        sampled=rng.choices(values,k=len(values));n=sum(v[2] for v in sampled)
        b=sum(v[0] for v in sampled)/n;a=sum(v[1] for v in sampled)/n
        boot.append((b,a,b-a))
    intervals={name:[percentile([v[i] for v in boot],.025),percentile([v[i] for v in boot],.975)] for i,name in enumerate(['baseline_cer','adapted_cer','absolute_cer_reduction'])}
    report={'examples':len(manifest),'source_document_groups':len(groups),'bootstrap_replicates':2000,'seed':42,
        'confidence_intervals_95':intervals,'bootstrap_unit':'source-document candidate group, not verified writer',
        'improved_words':improved,'worsened_words':worsened,'unchanged_words':unchanged,
        'by_length':{k:{'count':v[0],'baseline_cer':v[1]/v[3],'adapted_cer':v[2]/v[3]} for k,v in lengths.items()},
        'adapted_error_severity':dict(severity),
        'per_source_document':{k:{'baseline_cer':v[0]/v[2],'adapted_cer':v[1]/v[2],'reference_graphemes':v[2]} for k,v in groups.items()},
        'latency':{name:{'median_seconds':statistics.median(r['latency_seconds'] for r in records),
        'p95_seconds':percentile([r['latency_seconds'] for r in records],.95)} for name,records in [('baseline',baseline),('adapted',adapted)]},
        'largest_adapted_errors':sorted(failures,key=lambda r:r['cer'],reverse=True)[:12]}
    save(ROOT/'analysis.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='largest_adapted_errors'},ensure_ascii=False))
if __name__=='__main__':main()
