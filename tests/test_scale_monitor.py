import json,tempfile,unittest,hashlib
from pathlib import Path
from unittest.mock import patch
from ocr import scale_routes

class MonitorTests(unittest.TestCase):
    def test_selected_reporting_is_sealed_before_completion(self):
        with tempfile.TemporaryDirectory() as td,patch.object(scale_routes,'read',side_effect=AssertionError('No final report read')):
            self.assertIsNone(scale_routes.selected_analysis(Path(td),{'status':'running'},None,None,None))

    def test_completed_reporting_requires_matching_locked_hashes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'reports').mkdir()
            selection={'variant':'pilot'};summary={'selection':selection};protocol={'manifests':{'final-test':{'sha256':'frozen'}}}
            for name,value in [('selection.json',selection),('final-summary.json',summary)]:
                (root/name).write_text(json.dumps(value),encoding='utf-8')
            report={'selection':'pilot','selection_sha256':hashlib.sha256((root/'selection.json').read_bytes()).hexdigest(),
                    'final_summary_sha256':hashlib.sha256((root/'final-summary.json').read_bytes()).hexdigest(),
                    'final_manifest_sha256':'frozen','paired_original_selected':{}}
            path=root/'reports/final-selected-analysis-v1.json'
            path.write_text(json.dumps(report),encoding='utf-8')
            args=(root,{'status':'completed'},summary,selection,protocol)
            self.assertEqual(scale_routes.selected_analysis(*args),report)
            for key in ('selection','selection_sha256','final_summary_sha256','final_manifest_sha256'):
                changed={**report,key:'mismatch'};path.write_text(json.dumps(changed),encoding='utf-8')
                self.assertIsNone(scale_routes.selected_analysis(*args))
            self.assertIsNone(scale_routes.selected_analysis(root,{'status':'completed'},{'selection':{'variant':'candidate'}},selection,protocol))

    def test_recent_timing_excludes_long_gaps(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'training.jsonl'
            rows=[{'epoch':1,'example':i+1,'examples_per_epoch':10,'elapsed_seconds':elapsed} for i,elapsed in enumerate([1,2,1002,1003])]
            path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
            result=scale_routes.recent_timing(path)
            self.assertEqual(result['recent_median_seconds_per_word'],1)
            self.assertEqual(result['current_epoch_remaining_seconds_excluding_pauses'],6)
            self.assertEqual(result['long_gap_count_in_log_tail'],1)
    def test_monitor_reports_validation_after_training(self):
        with tempfile.TemporaryDirectory() as td,patch.object(scale_routes,'ROOT',Path(td)):
            root=Path(td);active=root/'trials/control';active.mkdir(parents=True)
            (root/'status.json').write_text(json.dumps({'status':'running','stage':'Controlled training trial: control','experiment_directory':str(active)}))
            (active/'training_progress.json').write_text(json.dumps({'epoch':1,'example':1000,'examples_per_epoch':1000}))
            (active/'epoch-1/adapter').mkdir(parents=True)
            (active/'epoch-1/validation').mkdir()
            (active/'epoch-1/validation/progress.json').write_text(json.dumps({'evaluated':20,'total':287}))
            result=scale_routes.status()
            self.assertIn('Validation after epoch 1',result['status']['stage'])
            self.assertIsNone(result['progress']);self.assertEqual(result['evaluation']['evaluated'],20)

if __name__=='__main__':unittest.main()
