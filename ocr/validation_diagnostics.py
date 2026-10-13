"""CPU-only, immutable validation diagnosis; never consumes final-test predictions.

This records observed disagreements, not verified spelling corrections. All image
and label review is explicitly pending until a human reviews the source evidence.
"""
import argparse
import hashlib
import json
import unicodedata
from collections import Counter
from pathlib import Path

import regex
from PIL import Image, ImageDraw, ImageFont, ImageOps
from .metrics import compare
from .research_io import save
from .research_policy import flags, length_bin

ROOT = Path('D:/OCR/runs/word-scale-v2')
DATA = Path('D:/OCR/research-v2')


def rows(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def aligned_edits(reference, prediction):
    """Deterministic minimum-edit alignment of NFC extended graphemes.

    Substitution, deletion, insertion is the tie priority. Ambiguous alignments
    can produce different confusion pairs, so these are descriptive candidates.
    """
    a, b = [regex.findall(r'\X', unicodedata.normalize('NFC', s)) for s in (reference, prediction)]
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1): d[i][0] = i
    for j in range(len(b) + 1): d[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            d[i][j] = min(d[i-1][j-1] + (a[i-1] != b[j-1]), d[i-1][j]+1, d[i][j-1]+1)
    edits = []; i, j = len(a), len(b)
    while i or j:
        if i and j and d[i][j] == d[i-1][j-1] + (a[i-1] != b[j-1]):
            if a[i-1] != b[j-1]: edits.append({'operation': 'substitution', 'reference': a[i-1], 'prediction': b[j-1]})
            i -= 1; j -= 1
        elif i and d[i][j] == d[i-1][j]+1:
            edits.append({'operation': 'deletion', 'reference': a[i-1], 'prediction': ''}); i -= 1
        else:
            edits.append({'operation': 'insertion', 'reference': '', 'prediction': b[j-1]}); j -= 1
    return list(reversed(edits))


def matched(manifest, predictions):
    expected = {r['example_id']: r for r in manifest}
    if len(expected) != len(manifest): raise ValueError('Duplicate manifest IDs')
    actual = {r['example_id']: r for r in predictions}
    if len(actual) != len(predictions) or set(actual) != set(expected):
        raise ValueError('Incomplete, duplicate or mismatched validation predictions')
    for eid, row in actual.items():
        if row['reference'] != expected[eid]['transcription_raw']:
            raise ValueError('Reference changed: ' + eid)
    return actual


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output):
    manifest_path = ROOT/'trial-validation-curated.jsonl'
    protocol = json.loads((ROOT/'curation-protocol.json').read_text(encoding='utf-8'))
    if digest(manifest_path) != protocol['manifests']['trial-validation-curated']['sha256']:
        raise RuntimeError('Frozen validation manifest hash changed')
    manifest = rows(manifest_path)
    if any(r['split'] != 'validation' for r in manifest): raise RuntimeError('Validation-only input required')
    sources = {
        'official_original': ROOT/'experiments/curated-original-official-official',
        'literal_original': ROOT/'experiments/curated-original-telugu_literal-official',
        'literal_control': ROOT/'trials/control/epoch-1/validation',
    }
    predictions = {name: matched(manifest, rows(folder/'predictions.jsonl')) for name,folder in sources.items()}
    queue = []; confusions = Counter(); categories = Counter(); transitions = Counter()
    for row in manifest:
        eid = row['example_id']; ref = row['transcription_raw']
        outputs = {name: values[eid] for name,values in predictions.items()}
        metrics = {name: compare(ref, record['prediction']) for name,record in outputs.items()}
        base = metrics['literal_original']['grapheme_edits']; new = metrics['literal_control']['grapheme_edits']
        transition = 'fewer_edits' if new < base else 'more_edits' if new > base else 'same_edits'
        transitions[transition] += 1
        if all(m['raw_exact'] for m in metrics.values()): continue
        observed = set()
        for name, record in outputs.items():
            f = flags(record['prediction'], record.get('truncated', False), record.get('image_quality'))
            observed.update(f['uncertainty_flags'])
            if metrics[name]['grapheme_edits']: observed.add('recognition_disagreement')
        if length_bin(ref) == '1-3': observed.add('short_word')
        if any(unicodedata.category(c) == 'Nd' for c in ref + ''.join(v['prediction'] for v in outputs.values())):
            observed.add('numeral_present_review')
        edits = aligned_edits(ref, outputs['literal_control']['prediction'])
        assert len(edits) == new
        for edit in edits: confusions[(edit['operation'],edit['reference'],edit['prediction'])] += 1
        for category in observed: categories[category] += 1
        queue.append({
            'example_id': eid, 'reference': ref, 'source_label_status': row['label_status'],
            'human_review_status': 'pending', 'eligible_for_training': False, 'split': 'validation',
            'original_sha256': row['original_sha256'], 'local_relative_path': row['local_relative_path'],
            'group_id': row['leakage_group'], 'license_ref': row['license_ref'],
            'observed_categories': sorted(observed), 'transition': transition,
            'metrics': metrics, 'control_alignment': edits,
            'outputs': {name: {k:v for k,v in record.items() if k in (
                'prediction','reference_token_ids','generated_token_ids','truncated','image_quality','latency_seconds')}
                for name,record in outputs.items()},
        })
    queue.sort(key=lambda r: (
        -int('non_telugu_letters' in r['observed_categories'] or 'refusal' in r['observed_categories']),
        -int(r['transition'] == 'more_edits'), -r['metrics']['literal_control']['grapheme_edits'], r['example_id']))
    output.mkdir(parents=True, exist_ok=False)
    (output/'review-queue.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in queue),encoding='utf-8')
    contracts = {name:json.loads((folder/'contract.json').read_text(encoding='utf-8')) for name,folder in sources.items()}
    summary = {
        'validation_examples': len(manifest), 'review_examples': len(queue),
        'observed_categories': dict(categories), 'matched_literal_control_transitions': dict(transitions),
        'control_confusion_candidates': [dict(operation=k[0],reference=k[1],prediction=k[2],count=n)
            for k,n in confusions.most_common(40)],
        'input_hashes': {str(p):digest(p) for p in [manifest_path,*[f/'predictions.jsonl' for f in sources.values()]]},
        'contracts': contracts, 'final_test_opened': False,
        'limitations': ['Validation only; exploratory diagnosis, not a new accuracy benchmark.',
            'Source labels are not all human verified. Disagreements may be label or crop errors.',
            'Alignments are deterministic minimum edits, not unique causal explanations.',
            'No spelling, numeral, Unicode or label corrections applied. No examples added to training.',
            'Original-model prompt and control-model differences must be separated when interpreting outcomes.'],
    }
    save(output/'summary.json',summary)
    # Visual evidence retains the original aspect ratio and complete source crop.
    sample = queue[:12]; cell_w, cell_h = 600, 220
    sheet = Image.new('RGB',(cell_w*2,cell_h*((len(sample)+1)//2)),'#f5f2fa')
    draw = ImageDraw.Draw(sheet); font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
    for i,row in enumerate(sample):
        path = (DATA/row['local_relative_path']).resolve()
        if not path.is_relative_to((DATA/'images').resolve()): raise RuntimeError('Unexpected image path')
        if digest(path) != row['original_sha256']: raise RuntimeError('Image hash changed: '+row['example_id'])
        with Image.open(path) as im: thumb = ImageOps.contain(ImageOps.exif_transpose(im).convert('RGB'),(570,155))
        x,y = (i%2)*cell_w,(i//2)*cell_h
        sheet.paste(thumb,(x+15+(570-thumb.width)//2,y+40+(155-thumb.height)//2))
        draw.text((x+15,y+8),f"{i+1}. {row['example_id']}",fill='#242032',font=font)
        draw.text((x+15,y+199),f"{row['transition']} | control edits={row['metrics']['literal_control']['grapheme_edits']}",fill='#604686',font=font)
    sheet.save(output/'validation-crops.png')
    report = '# Validation error diagnosis\n\nSame 287 frozen eligible validation words. No final-test examples were opened. Labels remain source ground truth, not newly human verified.\n\n'
    report += f"Review queue: {len(queue)} examples with at least one disagreement. Literal-policy control transitions versus original: {dict(transitions)}. Fewer edits does not by itself prove a statistically supported gain.\n\n"
    report += 'Each row retains source image hash, exact reference/raw outputs, generated and reference token IDs, deterministic grapheme edit alignment, image quality and original prompt/preprocessing contracts. Queue ordering prioritizes wrong-script/refusal candidates, regressions and large disagreements. Validation examples stay held out.\n\n'
    report += '| Crop | Source reference | Official original | Literal original | Literal control |\n|---|---|---|---|---|\n'
    def cell(s): return s.replace('|','\\|').replace('\n',' ↵ ').replace('<','&lt;').replace('>','&gt;')
    for i,r in enumerate(sample):
        report += f"|{i+1}|{cell(r['reference'])}|{cell(r['outputs']['official_original']['prediction'])}|{cell(r['outputs']['literal_original']['prediction'])}|{cell(r['outputs']['literal_control']['prediction'])}|\n"
    report += '\n![Original validation crops](validation-crops.png)\n\nAlignment/confusion candidates are descriptive. They must never become an automatic replacement dictionary. Wrong source labels and multiword crops require separate human review; do not repair frozen evaluation labels after viewing errors.\n\nDataset attribution: IIIT Hyderabad; Gongidi & Jawahar, IIIT-INDIC-HW-WORDS, ICDAR 2021; CC BY 4.0, https://ilocr.iiit.ac.in/dataset/23/. Contact sheet resizes images to fit and adds identifiers; source crops and labels are unchanged. IndicOCR: Bodhan AI / AI4Bharat; original model license preserved in the project.\n'
    (output/'diagnosis.md').write_text(report,encoding='utf-8')
    return summary


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--output',required=True); a = p.parse_args()
    result = run(Path(a.output)); print(json.dumps({k:result[k] for k in ('validation_examples','review_examples','observed_categories','matched_literal_control_transitions')}))
