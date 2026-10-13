import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from ocr import review_routes

class ReviewTests(unittest.TestCase):
    def test_scale_validation_queue_keeps_split_and_raw_outputs(self):
        with tempfile.TemporaryDirectory() as td,patch.object(review_routes,'ROOT',Path(td)):
            path=Path(td)/'diagnostics/control-v2/review-queue.jsonl';path.parent.mkdir(parents=True)
            row={'example_id':'val:a','split':'validation','reference':'౯ తెలుగు','original_sha256':'known',
                 'observed_categories':['recognition_disagreement'],'outputs':{'literal_control':{'prediction':'9 తెలుగు'},'literal_original':{'prediction':'౯ తెలుగు'}}}
            path.write_text(json.dumps(row,ensure_ascii=False)+'\n',encoding='utf-8')
            app=FastAPI();app.include_router(review_routes.router);client=TestClient(app)
            item=client.get('/api/review-v2?source=scale-validation-errors').json()
            self.assertEqual(item['prediction'],'9 తెలుగు')
            self.assertEqual(item['matched_outputs']['literal_original'],'౯ తెలుగు')
            payload={'source':'scale-validation-errors','index':0,'example_id':'val:a','decision':'unsure','human_verified':True}
            self.assertEqual(client.post('/api/review-v2',json=payload).status_code,200)
            item=client.get('/api/review-v2?source=scale-validation-errors').json()
            self.assertEqual(item['latest_annotation']['original_split'],'validation')
            self.assertFalse(item['latest_annotation']['included_in_training'])
            row['split']='train';path.write_text(json.dumps(row)+'\n',encoding='utf-8')
            self.assertEqual(client.get('/api/review-v2?source=scale-validation-errors').status_code,409)
    def test_review_never_changes_frozen_labels(self):
        with tempfile.TemporaryDirectory() as td,patch.object(review_routes,'ROOT',Path(td)):
            root=Path(td);path=root/'crop-review-quarantine.jsonl'
            row={'example_id':'test:a','original_split':'train','transcription_raw':'౯ తెలుగు','local_relative_path':'images/word/a.jpg','review_reasons':['label_review'],'original_sha256':'known'}
            path.write_text(json.dumps(row,ensure_ascii=False)+'\n',encoding='utf-8');original=path.read_bytes()
            app=FastAPI();app.include_router(review_routes.router);client=TestClient(app)
            item=client.get('/api/review-v2').json()
            self.assertEqual(item['source_label'],'౯ తెలుగు')
            payload={'source':'training-quarantine','index':0,'example_id':'test:a','decision':'label_mismatch','verified_transcript':'౯ కై','human_verified':False}
            self.assertEqual(client.post('/api/review-v2',json=payload).status_code,422)
            payload['human_verified']=True
            self.assertEqual(client.post('/api/review-v2',json={**payload,'example_id':'other'}).status_code,409)
            result=client.post('/api/review-v2',json=payload)
            self.assertEqual(result.status_code,200);self.assertFalse(result.json()['included_in_training'])
            self.assertEqual(path.read_bytes(),original)
            item=client.get('/api/review-v2').json();self.assertEqual(item['latest_annotation']['verified_transcript'],'౯ కై')
            self.assertFalse(item['latest_annotation']['normalization_applied'])
            client.post('/api/review-v2',json={**payload,'notes':'second version'})
            self.assertEqual(client.get('/api/review-v2').json()['annotation_versions'],2)
            self.assertEqual(client.get('/api/review-v2?source=final-test').status_code,422)
            self.assertEqual(client.get('/api/review-v2?index=-1').status_code,404)

if __name__=='__main__':unittest.main()
