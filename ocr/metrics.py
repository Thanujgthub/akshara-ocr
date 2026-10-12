"""Primary metric: NFC extended grapheme edit distance; punctuation preserved."""
import unicodedata
import regex

def distance(a, b):
    row = list(range(len(b) + 1))
    for i, value in enumerate(a):
        nxt = [i + 1]
        for j, other in enumerate(b):
            nxt.append(min(nxt[-1] + 1, row[j + 1] + 1, row[j] + (value != other)))
        row = nxt
    return row[-1]

def compare(reference, prediction):
    ref = unicodedata.normalize('NFC', reference)
    pred = unicodedata.normalize('NFC', prediction)
    rg, pg = regex.findall(r'\X', ref), regex.findall(r'\X', pred)
    rw, pw = ref.split(), pred.split()
    edits, word_edits = distance(rg, pg), distance(rw, pw)
    raw_g = regex.findall(r'\X', reference)
    raw_edits = distance(raw_g,regex.findall(r'\X',prediction))
    return {'grapheme_edits': edits, 'reference_graphemes': len(rg),
            'cer': edits / len(rg) if rg else None,
            'word_edits': word_edits, 'reference_words': len(rw),
            'wer': word_edits / len(rw) if rw else None,
            'raw_grapheme_edits':raw_edits,'raw_reference_graphemes':len(raw_g),
            'raw_cer': raw_edits / len(raw_g) if raw_g else None,
            'raw_exact': reference == prediction, 'nfc_exact': ref == pred,
            'whitespace_normalized_exact': ' '.join(ref.split()) == ' '.join(pred.split())}

def corpus(records):
    ids = [r['example_id'] for r in records]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate example IDs in evaluation')
    if not records:
        raise ValueError('Cannot evaluate an empty corpus')
    rows = [{'example_id': r['example_id'], 'source': r.get('source_dataset', 'unknown'),
             'granularity': r.get('granularity', 'unknown'),
             **compare(r['reference'], r['prediction'])} for r in records]
    n = sum(r['reference_graphemes'] for r in rows)
    w = sum(r['reference_words'] for r in rows)
    raw_n = sum(r['raw_reference_graphemes'] for r in rows)
    groups = {}
    for r in records:
        key = r.get('source_dataset', 'unknown') + '/' + r.get('granularity', 'unknown')
        groups.setdefault(key, []).append(r)
    return {'examples': len(rows), 'micro_cer': sum(r['grapheme_edits'] for r in rows)/n if n else None,
            'raw_micro_cer':sum(r['raw_grapheme_edits'] for r in rows)/raw_n if raw_n else None,
            'micro_wer': sum(r['word_edits'] for r in rows)/w if w else None,
            'macro_cer': sum(r['cer'] for r in rows if r['cer'] is not None)/sum(r['cer'] is not None for r in rows) if n else None,
            'raw_exact_match': sum(r['raw_exact'] for r in rows)/len(rows),
            'nfc_exact_match':sum(r['nfc_exact'] for r in rows)/len(rows),
            'normalization': 'NFC; regex extended grapheme clusters; all punctuation/digits retained; WER uses str.split()',
            'by_source_granularity': {key: {'count':len(value), 'raw_exact_match':sum(r['reference']==r['prediction'] for r in value)/len(value)} for key,value in groups.items()},
            'per_example': rows}
