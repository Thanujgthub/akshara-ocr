"""Local-only data audit. No remote image dereferencing or invented labels."""
from pathlib import Path
import hashlib
import json
import random
import unicodedata
from PIL import Image, ImageOps

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def visual_hash(image):
    gray = ImageOps.grayscale(ImageOps.exif_transpose(image)).resize((9,8))
    values = list(gray.getdata())
    return sum((values[y*9+x] > values[y*9+x+1]) << (y*8+x) for y in range(8) for x in range(8))

def audit(root, source, license_ref, granularity='page', labels=None):
    root = Path(root).resolve()
    pairs, rejected, hashes, near = [], [], {}, []
    for path in sorted(root.rglob('*')):
        if path.suffix.lower() not in {'.jpg','.jpeg','.png','.webp'}:
            continue
        rel = path.relative_to(root).as_posix()
        if not path.resolve().is_relative_to(root):
            rejected.append({'path':rel,'reason':'path escapes root'}); continue
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                image.load()
                vh = visual_hash(image)
        except Exception as e:
            rejected.append({'path':rel,'reason':'corrupt image: '+type(e).__name__}); continue
        label_path = path.with_suffix('.txt')
        text = labels.get(rel) if labels is not None else label_path.read_text(encoding='utf-8') if label_path.exists() else None
        if not text or not text.strip():
            rejected.append({'path':rel,'reason':'missing/empty label'}); continue
        if not any('\u0c00' <= c <= '\u0c7f' for c in text):
            rejected.append({'path':rel,'reason':'no Telugu characters; manual language review required'}); continue
        digest = sha256(path)
        if digest in hashes:
            rejected.append({'path':rel,'reason':'exact duplicate','of':hashes[digest]}); continue
        hashes[digest] = rel
        # Conservative candidate grouping: false positives can reduce split availability.
        matches = [i for i, (prev, _) in enumerate(near) if bin(prev ^ vh).count('1') <= 4]
        group = pairs[matches[0]]['group_id'] if matches else source+':'+path.stem
        if matches:
            groups = {pairs[i]['group_id'] for i in matches}
            for old in pairs:
                if old['group_id'] in groups:
                    old['group_id'] = group
        near.append((vh, rel))
        pairs.append({'example_id':source+':'+rel,'source_dataset':source,'source_split':'imported',
            'source_image_id':rel,'local_relative_path':rel,'original_sha256':digest,'group_id':group,
            'granularity':granularity,'script':'Telugu','domain':'handwritten-unverified',
            'transcription_raw':text,'transcription_nfc':unicodedata.normalize('NFC',text),
            'label_status':'source-supplied-unreviewed','annotation_version':'original',
            'license_ref':license_ref,'split':None,'near_duplicate_candidate':bool(matches)})
    return pairs, rejected

def read_tsv(path):
    labels = {}
    for i, line in enumerate(Path(path).read_text(encoding='utf-8-sig').splitlines(), 1):
        if not line.strip(): continue
        parts = line.split('\t', 1)
        if len(parts) != 2 or not parts[1].strip():
            raise ValueError('Missing tab-separated label at line '+str(i))
        key = Path(parts[0].replace('\\','/')).as_posix()
        if key in labels: raise ValueError('Duplicate image label: '+key)
        labels[key] = parts[1]
    return labels

def splits(records, seed=42, validation=500, test=500, minimum_train=1000):
    if len({r['example_id'] for r in records}) != len(records):
        raise ValueError('Duplicate example IDs')
    if len({r['original_sha256'] for r in records}) != len(records):
        raise ValueError('Exact duplicates must be removed before splitting')
    if len({r['granularity'] for r in records}) > 1:
        raise ValueError('Split each granularity separately')
    groups = {}
    for r in records: groups.setdefault(r['group_id'], []).append(r)
    keys = sorted(groups)
    random.Random(seed).shuffle(keys)
    result = {'train':[], 'validation':[], 'test':[]}
    for key in keys:
        split = 'test' if len(result['test']) < test else 'validation' if len(result['validation']) < validation else 'train'
        result[split].extend({**r,'split':split} for r in groups[key])
    targets = {'train':minimum_train,'validation':validation,'test':test}
    shortfalls = {k:max(0, v-len(result[k])) for k,v in targets.items()}
    return result, shortfalls

def write_jsonl(path, rows):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
