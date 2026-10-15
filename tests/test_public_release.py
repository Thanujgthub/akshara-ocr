"""Publication boundaries: frozen identity, no overwrite and no path escape."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from scripts.serve_selected import checked_path, verify_release


class PublicationTests(unittest.TestCase):
    def test_checksum_path_cannot_escape_release(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                checked_path(Path(d), '../outside')

    def test_other_adapter_cannot_be_served_as_selected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / 'checksums.json').write_text('{}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'not the locked'):
                verify_release(p, p)

    @unittest.skipUnless(shutil.which('node'), 'Node required for static publication build')
    def test_public_build_has_snapshot_and_never_overwrites(self):
        root = Path(__file__).resolve().parents[1]
        temp_root = root / '.runtime-tmp'
        temp_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_root) as d:
            output = Path(d) / 'site'
            command = ['node', str(root / 'scripts/build_public_site.mjs'), str(output)]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            status = json.loads((output / 'published-study-status.json').read_text())
            self.assertEqual(status['status']['status'], 'completed')
            self.assertEqual(status['protocol']['manifests']['train']['count'], 25000)
            self.assertEqual(status['final']['final_metrics']['candidate']['raw_exact_match'], .762)
            self.assertIn('staticHosting: true', (output / 'deployment-config.js').read_text())
            self.assertFalse((output / 'ocr').exists())
            self.assertFalse((output / '.git').exists())
            before = (output / 'index.html').read_bytes()
            second = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual((output / 'index.html').read_bytes(), before)
