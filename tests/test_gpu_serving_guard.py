"""API concurrency regression fixtures; no GPU model or OCR accuracy test."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from fastapi.testclient import TestClient
from ocr import server


class GpuServingGuardTests(unittest.TestCase):
    def test_failed_study_with_live_preflight_refuses_inference(self):
        client=TestClient(server.app)
        commands=[['python','-u','-m','ocr.colab_benchmark'],
                  ['python','-m','ocr.scale_experiment','smoke'],
                  ['python','-m','ocr.scale_experiment','evaluate'],
                  ['python','-m','ocr.scale_experiment','train']]
        for command in commands:
            with self.subTest(command=command),patch('ocr.study_routes.read',return_value={'status':'failed'}),\
                    patch('psutil.process_iter',return_value=[SimpleNamespace(info={'cmdline':command})]),\
                    patch.object(server,'available',return_value=True),patch.object(server,'loaded',return_value=False),\
                    patch.object(server,'predict') as predict:
                health=client.get('/api/health').json()
                self.assertTrue(health['training_active']);self.assertFalse(health['model_ready'])
                result=client.post('/api/predict',files={'file':('word.png',b'not decoded during GPU work','image/png')},data={'mode':'word'})
                self.assertEqual(result.status_code,409);predict.assert_not_called()

    def test_completed_study_allows_parity_and_does_not_match_shell_text(self):
        processes=[SimpleNamespace(info={'cmdline':['python','-m','ocr.verify_api_parity']}),
                   SimpleNamespace(info={'cmdline':['powershell','-Command','python -m ocr.colab_benchmark']}),
                   SimpleNamespace(info={'cmdline':None})]
        with patch('ocr.study_routes.read',return_value={'status':'completed'}),\
                patch('psutil.process_iter',return_value=processes):
            self.assertFalse(server.study_busy())


if __name__=='__main__':unittest.main()
