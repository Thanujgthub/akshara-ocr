"""Read-only label coverage on frozen train/validation; no final-test labels."""
import argparse, hashlib, json, unicodedata
from collections import Counter
from pathlib import Path
import regex
from .research_io import save

ROOT = Path('D:/OCR/runs/word-scale-v2')


def analyze(records):
    counts=Counter(); digits=Counter(); foreign=Counter(); lengths=Counter(); labels=Counter()
    for row in records:
        raw=row['transcription_raw']; nfc=unicodedata.normalize('NFC',raw)
        labels[nfc]+=1; counts['examples']+=1
        counts['nfc_changes']+=raw!=nfc
        counts['empty_or_whitespace']+=not raw.strip()
        counts['multiple_whitespace_tokens']+=len(raw.split())>1
        clusters=regex.findall(r'\X',nfc);lengths[str(len(clusters))]+=1
        counts['leading_combining_cluster']+=any(unicodedata.category(g[0]).startswith('M') for g in clusters)
        counts['control_or_replacement_candidate']+=any(unicodedata.category(c)=='Cc' or c=='\ufffd' for c in raw)
        nums=[c for c in raw if unicodedata.category(c)=='Nd'];digits.update(nums)
        counts['numeral_examples']+=bool(nums)
        other=[c for c in raw if unicodedata.category(c).startswith('L') and not '\u0c00'<=c<='\u0c7f']
        foreign.update(other);counts['non_telugu_letter_examples']+=bool(other)
    return {'counts':dict(counts),'unique_nfc_labels':len(labels),
        'digit_codepoints':[{'character':c,'codepoint':f'U+{ord(c):04X}','name':unicodedata.name(c),'occurrences':n} for c,n in sorted(digits.items())],
        'foreign_letter_candidates':[{'character':c,'codepoint':f'U+{ord(c):04X}','name':unicodedata.name(c,'UNKNOWN'),'occurrences':n} for c,n in foreign.most_common()],
        'length_graphemes':dict(sorted(lengths.items(),key=lambda kv:int(kv[0]))),
        'most_frequent_labels':[{'text':s,'examples':n} for s,n in labels.most_common(40)]}


def run(output):
    protocol=json.loads((ROOT/'curation-protocol.json').read_text(encoding='utf-8'));results={};allrows={};hashes={}
    for name in ['train-curated','validation-curated','trial-validation-curated']:
        path=ROOT/(name+'.jsonl');digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest!=protocol['manifests'][name]['sha256']:raise RuntimeError('Frozen manifest changed: '+name)
        records=[json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]
        allrows[name]=records;results[name]=analyze(records);hashes[name]=digest
    train=allrows['train-curated'];val=allrows['validation-curated']
    leakage={field:len({r[field] for r in train}&{r[field] for r in val}) for field in ['example_id','original_sha256','pixel_sha256','leakage_group']}
    if any(leakage.values()):raise RuntimeError('Train/validation overlap found: '+str(leakage))
    result={'coverage':results,'train_validation_shared_identity_counts':leakage,'manifest_hashes':hashes,
        'final_test_opened':False,'labels_modified':False,'human_label_verification':'Not established by this technical audit',
        'interpretation':'Unicode/script and numeral counts identify coverage gaps and review candidates, not automatically erroneous labels. Repeated vocabulary across splits is expected; identity hashes/groups are the leakage checks. Writer IDs and pretraining overlap remain unknown.'}
    if output.exists():raise FileExistsError('Use a new output path; preserve earlier audit')
    save(output,result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
    result=run(Path(a.output));print(json.dumps({k:v['counts'] for k,v in result['coverage'].items()}))
