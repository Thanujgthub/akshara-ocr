import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from ocr.metrics import compare,corpus
from ocr.data import audit,splits,read_tsv
from ocr.model import predict

class ToolkitTests(unittest.TestCase):
    def test_grapheme_metric(self):
        self.assertEqual(compare('తెలుగు','తెలుగు')['cer'],0)
        self.assertEqual(compare('కి','కు')['grapheme_edits'],1)
        self.assertEqual(compare('తే','తె')['cer'],1)
    def test_punctuation_digits_preserved(self):
        self.assertGreater(compare('123.','123')['cer'],0)
    def test_empty_reference(self):
        self.assertIsNone(compare('','x')['cer'])
        self.assertEqual(compare('','x')['grapheme_edits'],1)
    def test_nfc(self):
        self.assertEqual(compare('é','e\u0301')['cer'],0)
        self.assertFalse(compare('é','e\u0301')['raw_exact'])
    def test_corpus_empty_and_duplicate(self):
        with self.assertRaises(ValueError):corpus([])
        row={'example_id':'a','reference':'తెలుగు','prediction':'తెలుగు'}
        with self.assertRaises(ValueError):corpus([row,row])
    def test_audit(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            Image.new('RGB',(20,20),'white').save(root/'a.png')
            (root/'a.txt').write_text('తెలుగు',encoding='utf-8')
            (root/'b.png').write_bytes((root/'a.png').read_bytes())
            (root/'b.txt').write_text('తెలుగు',encoding='utf-8')
            Image.new('RGB',(23,20),'black').save(root/'missing.png')
            (root/'broken.png').write_bytes(b'broken')
            rows,rejected=audit(root,'test','CC-BY-4.0')
            self.assertEqual(len(rows),1)
            self.assertEqual(len(rejected),3)
            self.assertEqual(rows[0]['transcription_raw'],'తెలుగు')
    def test_group_splits_deterministic(self):
        rows=[{'example_id':str(i),'group_id':str(i//2),'original_sha256':str(i),'granularity':'page'} for i in range(20)]
        a,deficit=splits(rows,validation=4,test=4,minimum_train=12)
        b,_=splits(list(reversed(rows)),validation=4,test=4,minimum_train=12)
        self.assertEqual({k:{r['example_id'] for r in v} for k,v in a.items()},{k:{r['example_id'] for r in v} for k,v in b.items()})
        groups=[{r['group_id'] for r in a[k]} for k in a]
        self.assertFalse(groups[0]&groups[1] or groups[1]&groups[2] or groups[0]&groups[2])
        self.assertEqual(sum(deficit.values()),0)
    def test_shortfall(self):
        result,deficit=splits([])
        self.assertEqual(deficit,{'train':1000,'validation':500,'test':500})
    def test_duplicate_split_rejected(self):
        row={'example_id':'a','original_sha256':'same','group_id':'g','granularity':'page'}
        with self.assertRaises(ValueError):splits([row,{**row,'example_id':'b'}])
    def test_tsv_preserves_text(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'labels.txt';p.write_text('a.png\tతెలుగు భాష\n',encoding='utf-8')
            self.assertEqual(read_tsv(p)['a.png'],'తెలుగు భాష')
            p.write_text('a.png\t\n',encoding='utf-8')
            with self.assertRaises(ValueError):read_tsv(p)
    def test_no_fake_inference(self):
        import os
        from unittest.mock import patch
        with patch.dict(os.environ,{'INDIC_OCR_REPO':''}):
            with self.assertRaises(RuntimeError):predict(Path('not-a-file.png'))
    def test_download_requires_approval(self):
        from ocr.download import download
        with self.assertRaises(ValueError):
            download({'download_url':'https://example.com/a.zip'},Path('unused.zip'))
    def test_mixed_granularity_rejected(self):
        rows=[{'example_id':'a','group_id':'a','original_sha256':'a','granularity':'page'},
              {'example_id':'b','group_id':'b','original_sha256':'b','granularity':'word'}]
        with self.assertRaises(ValueError):splits(rows)

if __name__=='__main__':unittest.main()
