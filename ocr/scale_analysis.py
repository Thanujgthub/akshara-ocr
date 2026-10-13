"""Grouped paired intervals; preserves raw predictions and avoids test-based selection."""
import json,random,math
from pathlib import Path
from collections import defaultdict
from ocr.metrics import compare
from ocr.research_io import save

def load(p):return [json.loads(s) for s in Path(p).read_text(encoding='utf-8').splitlines() if s.strip()]
def paired(base,adapted,reps=2000):
    if [r['example_id'] for r in base]!=[r['example_id'] for r in adapted]:raise ValueError('Paired input mismatch')
    groups=defaultdict(lambda:[0,0,0,0,0,0,0,0])
    for b,a in zip(base,adapted):
        bm=compare(b['reference'],b['prediction']);am=compare(a['reference'],a['prediction'])
        if b['reference']!=a['reference']:raise ValueError('Paired reference mismatch')
        v=groups[b['group_id']]
        for i,x in enumerate([bm['grapheme_edits'],am['grapheme_edits'],bm['reference_graphemes'],bm['word_edits'],am['word_edits'],bm['reference_words'],int(am['raw_exact'])-int(bm['raw_exact']),1]):v[i]+=x
    values=list(groups.values());rng=random.Random(42);cer=[];wer=[];exact=[]
    for _ in range(reps):
        totals=[0]*8
        for __ in values:
            v=rng.choice(values)
            for i,x in enumerate(v):totals[i]+=x
        cer.append((totals[0]-totals[1])/totals[2]);wer.append((totals[3]-totals[4])/totals[5]);exact.append(totals[6]/totals[7])
    def ci(x):
        x.sort();return [x[int(.025*reps)],x[min(reps-1,int(.975*reps))]]
    interval=ci(cer)
    return {'paired_groups':len(values),'examples':len(base),'repetitions':reps,'seed':42,
            'cer_reduction_95':interval,'wer_reduction_95':ci(wer),'raw_exact_gain_95':ci(exact),
            'cer_improvement_supported':interval[0]>0,'group_identity':'source-document / duplicate components; writer identities unverified',
            'interpretation':'Supports CER reduction on this evaluation sample' if interval[0]>0 else 'Inconclusive CER reduction; interval includes no gain or harm'}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--baseline',required=True);p.add_argument('--adapted',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    save(a.output,paired(load(a.baseline),load(a.adapted)))
