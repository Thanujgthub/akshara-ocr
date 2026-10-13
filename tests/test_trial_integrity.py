import json,tempfile,unittest
from pathlib import Path
from ocr.trial_integrity import resource_scope,audit


class IntegrityTests(unittest.TestCase):
    def test_reused_predictions_cannot_establish_complete_peak(self):
        r=resource_scope({'elapsed_seconds_this_process':.04},[{'latency_seconds':2},{'latency_seconds':3}])
        self.assertTrue(r['prediction_reuse_evidence']);self.assertFalse(r['validation_peak_comparable'])
        self.assertFalse(r['scores_changed'])
        r=resource_scope({'elapsed_seconds_this_process':8},[{'latency_seconds':2},{'latency_seconds':3}])
        self.assertFalse(r['prediction_reuse_evidence']);self.assertIsNone(r['validation_peak_comparable'])
        self.assertIsNone(resource_scope({},[{}])['generation_latency_sum_seconds'])

    def test_audit_hashes_completed_only_and_does_not_rewrite_results(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);folder=root/'trials/done';evaluation=folder/'epoch-1/validation';evaluation.mkdir(parents=True)
            (root/'trials/active').mkdir()
            for p,v in [(folder/'training_complete.json',{}),(folder/'best.json',{'epoch':1}),
                        (evaluation/'metrics.json',{'examples':1,'elapsed_seconds_this_process':.01})]:
                p.write_text(json.dumps(v),encoding='utf-8')
            pred=evaluation/'predictions.jsonl';pred.write_text(json.dumps({'latency_seconds':2,'reference':'తెలుగు','prediction':'తెలుగు'})+'\n',encoding='utf-8')
            before={p:p.read_bytes() for p in folder.rglob('*') if p.is_file()}
            r=audit(root,root/'audit.json');self.assertEqual(r['skipped_incomplete_trials'],['active'])
            for p,b in before.items():self.assertEqual(p.read_bytes(),b)
            self.assertTrue((evaluation/'resource-scope.json').exists())
            self.assertIn('predictions.jsonl',' '.join(r['completed_trials']['done']['files']))
            with self.assertRaises(FileExistsError):audit(root,root/'audit.json')
