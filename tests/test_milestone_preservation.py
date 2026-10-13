import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ocr import run_scale


class MilestonePreservationTests(unittest.TestCase):
    def test_successive_milestones_preserve_handoff_and_history(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            original = '# State\n\n## Latest automated milestone\nold\n\n## Colab handoff\nKeep this recovery state.\n'
            (project / 'PROJECT_STATE.md').write_text(original, encoding='utf-8')
            (project / 'WORK_LOG.md').write_text('', encoding='utf-8')
            with patch.object(run_scale, 'PROJECT', project):
                run_scale.milestone('smoke', root=project / 'run')
                run_scale.milestone('benchmark', root=project / 'run')
            state = (project / 'PROJECT_STATE.md').read_text(encoding='utf-8')
            self.assertTrue(state.startswith(original))
            self.assertIn('"stage": "smoke"', state)
            self.assertIn('"stage": "benchmark"', state)
