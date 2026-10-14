"""Reporting-only raw/NFC metrics and paired original/selected uncertainty.

Runs after locked selection and completed sealed evaluation. Never runs inference,
changes selection, repairs text or overwrites the existing scientific records.
"""
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from .checkpoint_io import sha
from .metrics import compare, distance
from .research_io import save


def components(record):
    result=compare(record['reference'],record['prediction'])
    result['raw_word_edits']=distance(record['reference'].split(),record['prediction'].split())
    result['raw_reference_words']=len(record['reference'].split())
    return result


def aggregate(records):
    if not records or len({r['example_id'] for r in records})!=len(records):
        raise ValueError('Need nonempty unique prediction records')
    rows=[components(r) for r in records]
    def ratio(numerator,denominator):
        denominator=sum(row[denominator] for row in rows)
        return sum(row[numerator] for row in rows)/denominator if denominator else None
    return {'examples':len(rows),'raw_micro_cer':ratio('raw_grapheme_edits','raw_reference_graphemes'),
            'nfc_micro_cer':ratio('grapheme_edits','reference_graphemes'),
            'raw_micro_wer':ratio('raw_word_edits','raw_reference_words'),
            'nfc_micro_wer':ratio('word_edits','reference_words'),
            'raw_exact_match':sum(row['raw_exact'] for row in rows)/len(rows),
            'nfc_exact_match':sum(row['nfc_exact'] for row in rows)/len(rows)}


def paired_selected(original,selected,reps=2000):
    if reps<40:raise ValueError('Need at least40 bootstrap replicates')
    ids=[r['example_id'] for r in original]
    if not ids or len(ids)!=len(set(ids)) or ids!=[r['example_id'] for r in selected]:
        raise ValueError('Paired input IDs/order differ or duplicate')
    groups=defaultdict(lambda:[0]*11)
    for base,adapted in zip(original,selected):
        if base['reference']!=adapted['reference'] or base.get('group_id') is None or base['group_id']!=adapted.get('group_id'):
            raise ValueError('Paired reference/component grouping differs')
        b,a=components(base),components(adapted)
        values=[b['raw_grapheme_edits']-a['raw_grapheme_edits'],b['grapheme_edits']-a['grapheme_edits'],
                b['raw_word_edits']-a['raw_word_edits'],b['word_edits']-a['word_edits'],
                int(a['raw_exact'])-int(b['raw_exact']),int(a['nfc_exact'])-int(b['nfc_exact']),
                b['raw_reference_graphemes'],b['reference_graphemes'],b['raw_reference_words'],b['reference_words'],1]
        for i,value in enumerate(values):groups[base['group_id']][i]+=value
    names=['raw_cer_reduction','nfc_cer_reduction','raw_wer_reduction','nfc_wer_reduction','raw_exact_gain','nfc_exact_gain']
    denominators=[6,7,8,9,10,10];vectors=list(groups.values());rng=random.Random(42)
    totals=[sum(vector[i] for vector in vectors) for i in range(11)]
    point={name:totals[i]/totals[d] if totals[d] else None for i,(name,d) in enumerate(zip(names,denominators))}
    samples={name:[] for name in names}
    for _ in range(reps):
        totals=[0]*11
        for __ in vectors:
            vector=rng.choice(vectors)
            for i,value in enumerate(vector):totals[i]+=value
        for i,(name,d) in enumerate(zip(names,denominators)):
            if totals[d]:samples[name].append(totals[i]/totals[d])
    intervals={}
    for name,values in samples.items():
        values.sort();n=len(values)
        intervals[name]=[values[int(.025*n)],values[min(n-1,int(.975*n))]] if n else None
    return {'examples':len(original),'paired_groups':len(groups),'repetitions':reps,'seed':42,
            'point_differences':point,'intervals_95':intervals,
            'valid_repetitions_by_metric':{name:len(values) for name,values in samples.items()},
            'group_identity':'Frozen source-document / duplicate components; writer identity unknown.',
            'warnings':['Single-group intervals are degenerate and do not establish sampling uncertainty.'] if len(groups)<2 else [],
            'interpretation':'Reporting only. Positive error reduction/exact gain favors selected output on this sealed sample; selection remains locked.'}


def report(root,output):
    root,output=Path(root),Path(output)
    if output.exists():raise FileExistsError('Preserve earlier reports; use a fresh output path')
    def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
    if read(root/'status.json').get('status')!='completed':
        raise RuntimeError('Finish locked-selection sealed evaluation before reading final outputs')
    selection=read(root/'selection.json');selection_hash=sha(root/'selection.json');summary_hash=sha(root/'final-summary.json');summary=read(root/'final-summary.json')
    if summary['selection']!=selection:raise RuntimeError('Final report differs from locked selection')
    protocol=read(root/'protocol.json');manifest=root/'final-test.jsonl'
    if protocol['manifests']['final-test']['count']!=3000 or sha(manifest)!=protocol['manifests']['final-test']['sha256']:
        raise RuntimeError('Frozen final manifest differs')
    with manifest.open(encoding='utf-8') as stream:gold=[json.loads(line) for line in stream if line.strip()]
    if len(gold)!=3000 or len({r['example_id'] for r in gold})!=3000:raise RuntimeError('Final input count/identity mismatch')
    gold={r['example_id']:r for r in gold};predictions={};hashes={}
    for variant in ['original','pilot','candidate']:
        path=root/'final'/variant/'predictions.jsonl';hashes[variant]=sha(path)
        with path.open(encoding='utf-8') as stream:rows=[json.loads(line) for line in stream if line.strip()]
        if len(rows)!=3000 or {r['example_id'] for r in rows}!=set(gold):raise RuntimeError('Sealed prediction identity mismatch')
        for row in rows:
            frozen=gold[row['example_id']]
            if row['reference']!=frozen['transcription_raw'] or row['group_id']!=frozen['leakage_group']:
                raise RuntimeError('Prediction reference/group differs from frozen manifest')
        predictions[variant]=rows
    variant=selection['variant']
    if variant not in predictions:raise RuntimeError('Unknown locked selection variant')
    result={'selection':variant,'selection_sha256':selection_hash,'final_summary_sha256':summary_hash,'final_manifest_sha256':sha(manifest),
            'prediction_sha256':hashes,'raw_nfc_final_metrics':{name:aggregate(rows) for name,rows in predictions.items()},
            'paired_original_selected':paired_selected(predictions['original'],predictions[variant]),
            'normalization':'Raw strings preserved. NFC used only for named NFC metrics. WER uses str.split(); punctuation/digits preserved.',
            'scope':'Sealed word-crop reporting only; no inference rerun, selection change or confidence calibration.',
            'limitations':summary['limitations']}
    if sha(root/'selection.json')!=selection_hash or sha(root/'final-summary.json')!=summary_hash or sha(manifest)!=protocol['manifests']['final-test']['sha256'] or any(sha(root/'final'/name/'predictions.jsonl')!=digest for name,digest in hashes.items()):
        raise RuntimeError('Locked selection/raw outputs changed during reporting')
    if output.exists():raise FileExistsError('Report path appeared during analysis')
    save(output,result);return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',default='D:/OCR/runs/word-efficient-v3');parser.add_argument('--output',required=True)
    args=parser.parse_args();result=report(args.run,args.output)
    print(json.dumps({'selection':result['selection'],'paired_groups':result['paired_original_selected']['paired_groups'],'output':args.output}))


if __name__=='__main__':main()
