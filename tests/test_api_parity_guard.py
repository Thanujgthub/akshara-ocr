import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ocr.verify_api_parity import main


class ApiParityGuardTests(unittest.TestCase):
    def test_active_study_never_contacts_inference_server(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'status.json').write_text(json.dumps({'status': 'running'}))
            args = ['parity', '--run', str(root), '--output', str(root / 'parity')]
            with patch('sys.argv', args), patch('ocr.verify_api_parity.urllib.request.urlopen') as request:
                with self.assertRaisesRegex(RuntimeError, 'Finish the study'):
                    main()
                request.assert_not_called()
            self.assertFalse((root / 'parity').exists())

    def test_existing_parity_evidence_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            out = root / 'parity'; out.mkdir()
            evidence = out / 'raw-api-outputs.jsonl'
            evidence.write_text('preserved fixture evidence\n')
            args = ['parity', '--run', str(root), '--output', str(out)]
            with patch('sys.argv', args), patch('ocr.verify_api_parity.urllib.request.urlopen') as request:
                with self.assertRaisesRegex(RuntimeError, 'fresh parity output'):
                    main()
                request.assert_not_called()
            self.assertEqual(evidence.read_text(), 'preserved fixture evidence\n')
