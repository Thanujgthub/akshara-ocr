import json,tempfile,unittest
from pathlib import Path
from ocr.checkpoint_io import save_checkpoint,recovery_folder,sync_recovery,sha
from ocr.portable_paths import resolve_path,run_lock
from unittest.mock import patch


class FakeModel:
    def save_pretrained(self,folder):
        folder.mkdir();(folder/'adapter_model.safetensors').write_bytes(b'test-fixture-not-a-model')
        (folder/'adapter_config.json').write_text('{}')


class FakeTorch:
    @staticmethod
    def save(state,path):path.write_text(json.dumps(state))


class ColabRecoveryTests(unittest.TestCase):
    def test_atomic_versioning_durable_copy_and_corrupt_latest_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/'run';drive=Path(td)/'drive'
            first=save_checkpoint(root,1,FakeModel(),{'signature':'same','updates':1,'epoch':0,'next_index':4},FakeTorch())
            original=sha(first/'state.pt')
            second=save_checkpoint(root,2,FakeModel(),{'signature':'same','updates':2,'epoch':0,'next_index':8},FakeTorch())
            self.assertTrue(sync_recovery(root,drive));self.assertEqual(recovery_folder(drive).name,second.name)
            (second/'state.pt').write_text('corrupt')
            self.assertEqual(recovery_folder(root),first);self.assertEqual(sha(first/'state.pt'),original)
            duplicate=save_checkpoint(root,1,FakeModel(),{'signature':'same','updates':1,'epoch':0,'next_index':4},FakeTorch())
            self.assertNotEqual(duplicate,first);self.assertTrue(first.exists())
            (root/'resume.json').unlink()
            self.assertEqual(recovery_folder(root,expected_signature='same'),duplicate)

    def test_failed_write_preserves_last_committed_checkpoint(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);first=save_checkpoint(root,1,FakeModel(),{'signature':'s','updates':1},FakeTorch())
            pointer=(root/'resume.json').read_bytes()
            class FailingTorch:
                @staticmethod
                def save(state,path):raise OSError('simulated disk failure')
            with self.assertRaises(OSError):save_checkpoint(root,2,FakeModel(),{'signature':'s','updates':2},FailingTorch())
            self.assertEqual((root/'resume.json').read_bytes(),pointer);self.assertEqual(recovery_folder(root),first)

    def test_relocation_preserves_original_config_strings(self):
        cfg={'initial_adapter':'D:\\OCR\\runs\\pilot\\adapter'}
        with patch.dict('os.environ',{'OCR_PATH_MAP':json.dumps({'D:/OCR/runs':'/content/runs'})}):
            self.assertEqual(resolve_path(cfg['initial_adapter']).as_posix(),'/content/runs/pilot/adapter')
        self.assertEqual(cfg['initial_adapter'],'D:\\OCR\\runs\\pilot\\adapter')

    def test_process_lock_rejects_duplicate_owner(self):
        with tempfile.TemporaryDirectory() as td:
            with run_lock(Path(td)/'run.lock'):
                with self.assertRaises(RuntimeError):
                    with run_lock(Path(td)/'run.lock'):pass
