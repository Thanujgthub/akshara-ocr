import unittest
from unittest.mock import patch
from ocr.windows_memory import GIB, assess, snapshot


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
