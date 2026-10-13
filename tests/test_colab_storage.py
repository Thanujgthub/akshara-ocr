import json,tempfile,unittest,zipfile
from pathlib import Path
from ocr.colab_storage import safe_extract,snapshot_run,restore_run
from ocr.checkpoint_io import save_checkpoint,recovery_folder
from test_colab_recovery import FakeModel,FakeTorch


class StorageTests(unittest.TestCase):
    def test_archive_traversal_and_overwrite_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);archive=root/'bad.zip'
            with zipfile.ZipFile(archive,'w') as z:z.writestr('../escape.txt','x')
            with self.assertRaises(RuntimeError):safe_extract(archive,root/'stage')
            self.assertFalse((root/'escape.txt').exists())
            with zipfile.ZipFile(archive,'w') as z:z.writestr('safe.txt','x')
            safe_extract(archive,root/'stage')
            with self.assertRaises(RuntimeError):safe_extract(archive,root/'stage')

    def test_durable_snapshot_restore_and_corrupt_newest_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);run=root/'run';drive=root/'drive'
            save_checkpoint(run/'full',1,FakeModel(),{'signature':'s','updates':1},FakeTorch())
            (run/'predictions.jsonl').write_bytes(b'{"complete":1}\n{"partial":')
            first=snapshot_run(run,drive)
            self.assertEqual((first/'predictions.jsonl').read_bytes(),b'{"complete":1}\n')
            second=snapshot_run(run,drive);(second/'full/resume.json').write_text('corrupt')
            selected=restore_run(drive,root/'restored');self.assertEqual(selected,first)
            self.assertEqual(recovery_folder(root/'restored/full').name,'step-0000001')
            with self.assertRaises(RuntimeError):restore_run(drive,root/'restored')

    def test_latest_pointer_and_restore_snapshot_cycles(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);run=root/'run';drive=root/'drive'
            save_checkpoint(run/'full',1,FakeModel(),{'signature':'s','updates':1},FakeTorch())
            first=snapshot_run(run,drive)
            older=drive/'snapshot-99999999-old';first.rename(older)
            save_checkpoint(run/'full',2,FakeModel(),{'signature':'s','updates':2},FakeTorch())
            newest=snapshot_run(run,drive)
            self.assertEqual(restore_run(drive,root/'restored'),newest)
            self.assertFalse((root/'restored/snapshot-checksums.json').exists())
            # A restored run must remain snapshot-able across multiple sessions.
            third=snapshot_run(root/'restored',drive)
            self.assertEqual(restore_run(drive,root/'twice-restored'),third)
            self.assertEqual(recovery_folder(root/'twice-restored/full').name,'step-0000002')
            # Corrupt pointer: chronological metadata, not random/path-name order.
            (drive/'latest-snapshot.json').write_text('broken')
            self.assertEqual(restore_run(drive,root/'fallback'),third)
