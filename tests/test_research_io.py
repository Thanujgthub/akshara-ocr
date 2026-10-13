import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from ocr.research_io import save, _transient_windows_lock


def sharing_error():
    error=PermissionError('Windows destination temporarily locked')
    error.winerror=5
    return error


class AtomicJsonTests(unittest.TestCase):
    def test_retry_classification_is_windows_specific(self):
        with patch('ocr.research_io.os.name','nt'):
            self.assertTrue(_transient_windows_lock(sharing_error()))
            self.assertFalse(_transient_windows_lock(PermissionError('permanent permissions')))
        with patch('ocr.research_io.os.name','posix'):
            self.assertFalse(_transient_windows_lock(sharing_error()))

    def test_transient_lock_preserves_old_destination_then_commits_unicode(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'progress.json';path.write_text('{"old":true}',encoding='utf-8')
            import os
            replace=os.replace
            attempts=[]
            def transient(source,destination):
                attempts.append(str(source))
                if len(attempts)<3:
                    self.assertEqual(json.loads(path.read_text()),{'old':True})
                    raise sharing_error()
                replace(source,destination)
            with patch('ocr.research_io.os.replace',side_effect=transient),patch('ocr.research_io.time.sleep'),patch('ocr.research_io._transient_windows_lock',return_value=True):
                save(path,{'text':'తెలుగు 123'})
            self.assertEqual(json.loads(path.read_text(encoding='utf-8')),{'text':'తెలుగు 123'})
            self.assertEqual(len(attempts),3)
            self.assertEqual(len(set(attempts)),1)
            self.assertFalse(list(Path(td).glob('*.tmp')))

    def test_persistent_lock_is_bounded_and_preserves_original_and_pending_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'progress.json';path.write_text('{"old":true}',encoding='utf-8')
            with patch('ocr.research_io.os.replace',side_effect=sharing_error()) as replace,patch('ocr.research_io.time.sleep') as sleep,patch('ocr.research_io._transient_windows_lock',return_value=True):
                with self.assertRaises(PermissionError):save(path,{'new':True})
            self.assertEqual(replace.call_count,40);self.assertEqual(sleep.call_count,39)
            self.assertEqual(json.loads(path.read_text()),{'old':True})
            pending=list(Path(td).glob('*.tmp'));self.assertEqual(len(pending),1)
            self.assertEqual(json.loads(pending[0].read_text()),{'new':True})
