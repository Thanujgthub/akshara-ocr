"""Label-blind conservative training quarantine; preserve every prior manifest."""
import json,random
from collections import Counter
from pathlib import Path
from ocr.freeze_scale import ROOT,read,write
from ocr.research_policy import crop_review_reasons
from ocr.scale_experiment import save

def main():
    if (ROOT/'curation-protocol.json').exists():return
    manifests={};counts={};queue=[]
    for split in ['train','validation','trial-validation']:
        rows=read(ROOT/f'{split}.jsonl');clean=[]
        for row in rows:
            reasons=crop_review_reasons(row)
            if reasons:queue.append({**row,'review_reasons':reasons,'human_review_status':'pending','original_split':split})
            else:clean.append(row)
        manifests[split+'-curated']=write(ROOT/f'{split}-curated.jsonl',clean);counts[split]={'input':len(rows),'eligible':len(clean),'quarantined':len(rows)-len(clean)}
    train=read(ROOT/'train-curated.jsonl');random.Random(42).shuffle(train)
    manifests['trial-train-curated']=write(ROOT/'trial-train-curated.jsonl',train[:1000])
    write(ROOT/'crop-review-quarantine.jsonl',queue)
    save(ROOT/'curation-protocol.json',{'manifests':manifests,'counts':counts,'reasons':dict(Counter(s for r in queue for s in r['review_reasons'])),
        'policy':'Fixed label-blind conservative word training filter: height <=300 px, both dimensions >=8 px, official-clamp + 4px-margin image tokens <=800. Large crops require human alignment review; they are NOT all claimed wrong.',
        'evidence':'Inspected train/images/1/513/1.jpg: many printed and handwritten words under a single unrelated word label. Pilot validation example 4abb2d... similarly includes printed/handwritten form content with mismatched reference.',
        'test_policy':'Original sealed final-test manifest stays unchanged. Resource abstentions count as errors; suspect-crop subgroup reported separately.',
        'human_review':'pending; no labels repaired or images recropped automatically'})
    print(json.dumps(counts),flush=True)
if __name__=='__main__':main()
