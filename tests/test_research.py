import unittest
import regex
from PIL import Image
from ocr.metrics import compare
from ocr.research_policy import flags,formatting_candidate,quality,augment

class ResearchTests(unittest.TestCase):
    def test_telugu_clusters_and_digits(self):
        for text in ['కి','కీ','క్షి','స్త్రీ','౯','9','ం','ః','?']:
            self.assertEqual(len(regex.findall(r'\X',text)),1,text)
        self.assertEqual(compare('౯','9')['grapheme_edits'],1)
        self.assertEqual(compare('క్షి','క్షీ')['grapheme_edits'],1)
        self.assertEqual(compare('కై','కై')['cer'],0)
        self.assertFalse(compare('కై','కై')['raw_exact'])
    def test_no_silent_cleanup(self):
        self.assertEqual(formatting_candidate('$$౯$$')['text'],'$$౯$$')
        self.assertEqual(formatting_candidate('$$౯$$',True)['text'],'౯')
        self.assertEqual(formatting_candidate('$$\\text{౯}$$',True)['operations'],[])
    def test_failure_flags(self):
        self.assertTrue(flags('ಒಂದ್ಲಿ')['script_contamination'])
        self.assertTrue(flags('[No text or transcription provided]')['refusal'])
        self.assertTrue(flags('తెలుగు తెలుగు తెలుగు')['repeat_candidate'])
        self.assertFalse(flags('తెలుగు ౯ 9.')['script_contamination'])
        self.assertIsNone(flags('తెలుగు')['confidence'])
    def test_blank_not_a_hallucinated_transcription(self):
        q=quality(Image.new('RGB',(100,40),'white'))
        self.assertTrue(q['uniform_pixels'])
        self.assertIn('uniform_image_review',flags('తెలుగు',image_quality=q)['uncertainty_flags'])
    def test_augmentation_deterministic_and_nonempty(self):
        import random
        im=Image.new('RGB',(100,40),'white')
        a=augment(im,random.Random(42));b=augment(im,random.Random(42))
        self.assertEqual(a.tobytes(),b.tobytes())
        self.assertGreater(a.width*a.height,0)
    def test_paired_groups_no_false_gain(self):
        from ocr.scale_analysis import paired
        rows=[{'example_id':str(i),'group_id':str(i//2),'reference':'తెలుగు','prediction':'తెలుగు'} for i in range(10)]
        result=paired(rows,rows,reps=100)
        self.assertEqual(result['cer_reduction_95'],[0,0])
        self.assertFalse(result['cer_improvement_supported'])
        with self.assertRaises(ValueError):paired(rows,list(reversed(rows)),reps=100)
    def test_analysis_does_not_import_training_runtime(self):
        import subprocess,sys
        code = "import sys; from ocr.scale_analysis import paired; assert 'ocr.scale_experiment' not in sys.modules; assert 'torch' not in sys.modules"
        subprocess.run([sys.executable,'-c',code],check=True)
    def test_malformed_table_not_transcription(self):
        self.assertTrue(flags('<table><tr><td>తెలుగు</td></tr></table>')['malformed_output'])
    def test_exact_uniform_gate_preserves_faint_marks(self):
        from ocr.research_policy import uniform_visible_input
        im=Image.new('RGB',(30,20),'white')
        self.assertTrue(uniform_visible_input(im))
        im.putpixel((15,10),(254,254,254))
        self.assertFalse(uniform_visible_input(im))
    def test_uniform_input_does_not_load_or_call_model(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from ocr import model
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'uniform.png';Image.new('RGB',(30,20),'white').save(path)
            with patch.object(model,'available',return_value=True),patch.object(model,'_run') as run:
                result=model.predict(path,'word')
                run.assert_not_called()
                self.assertEqual(result['markdown'],'');self.assertEqual(result['abstention'],'uniform_pixels')
                self.assertIsNone(result['model']);self.assertTrue(result['review_required'])

if __name__=='__main__':unittest.main()
