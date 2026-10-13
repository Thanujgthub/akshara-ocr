import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from ocr import scale_routes

class MonitorTests(unittest.TestCase):
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
