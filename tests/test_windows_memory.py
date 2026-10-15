import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from ocr.windows_memory import GIB, assess, snapshot, request_memory_stop


class WindowsMemoryTests(unittest.TestCase):
    def measured(self, headroom, free_ram=12 * GIB):
        return {'commit_total_bytes': 20 * GIB,
                'commit_limit_bytes': 20 * GIB + headroom,
                'commit_headroom_bytes': headroom,
                'available_ram_bytes': free_ram}

    def test_free_ram_cannot_hide_exhausted_commit_capacity(self):
        self.assertFalse(assess(self.measured(GIB))['passed'])
        self.assertTrue(assess(self.measured(10 * GIB, free_ram=GIB))['passed'])

    def test_invalid_measurement_and_invalid_allowances_fail_closed(self):
        measured = self.measured(10 * GIB)
        measured['commit_headroom_bytes'] = GIB
        with self.assertRaises(ValueError):
            assess(measured)
        for value in (0, -1, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                assess(self.measured(10 * GIB), reserve_gib=value)

    def test_other_platform_does_not_fabricate_windows_capacity(self):
        with patch('ocr.windows_memory.os.name', 'posix'):
            with self.assertRaises(RuntimeError):
                snapshot()

    def test_runtime_pressure_requests_existing_safe_stop_and_records_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.assertFalse(request_memory_stop(root, self.measured(3 * GIB)))
            self.assertFalse((root / 'STOP').exists())
            self.assertTrue(request_memory_stop(root, self.measured(GIB)))
            self.assertIn('optimizer/prediction boundary', (root / 'STOP').read_text())
            self.assertEqual(len(list((root / 'recovery').glob('memory-stop-*.json'))), 1)

    def test_runtime_guard_keeps_existing_user_stop_reason(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'STOP').write_text('user requested stop')
            self.assertTrue(request_memory_stop(root, self.measured(GIB)))
            self.assertEqual((root / 'STOP').read_text(), 'user requested stop')
            self.assertFalse((root / 'recovery').exists())

    def test_native_observation_failure_requests_boundary_without_killing_controller(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch('ocr.windows_memory.snapshot', side_effect=OSError('probe unavailable')):
                self.assertTrue(request_memory_stop(root))
            self.assertIn('observation failed', (root / 'STOP').read_text())
