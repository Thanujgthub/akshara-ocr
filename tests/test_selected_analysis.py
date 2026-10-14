"""Synthetic metric fixtures only; not OCR accuracy evidence."""
import copy
import json
import tempfile
import unicodedata
import unittest
from pathlib import Path
from ocr.selected_analysis import aggregate,paired_selected,report


class SelectedAnalysisTests(unittest.TestCase):
    def row(self,id='a',reference='క',prediction='క',group='g'):
        return {'example_id':id,'reference':reference,'prediction':prediction,'group_id':group}

    def test_raw_and_nfc_word_metrics_differ_without_changing_strings(self):
        reference='కై';prediction=unicodedata.normalize('NFD',reference)
        self.assertNotEqual(reference,prediction)
        rows=[self.row(reference=reference,prediction=prediction)];before=copy.deepcopy(rows)
        result=aggregate(rows)
        self.assertEqual(result['raw_micro_cer'],1);self.assertEqual(result['nfc_micro_cer'],0)
        self.assertEqual(result['raw_micro_wer'],1);self.assertEqual(result['nfc_micro_wer'],0)
        self.assertEqual(result['raw_exact_match'],0);self.assertEqual(result['nfc_exact_match'],1)
        self.assertEqual(rows,before)

    def test_grouped_pair_reductions_exact_gain_and_degeneracy_warning(self):
        baseline=[self.row(prediction='ఖ')];selected=[self.row()]
        result=paired_selected(baseline,selected,100)
        for name,value in result['point_differences'].items():self.assertEqual(value,1)
        for interval in result['intervals_95'].values():self.assertEqual(interval,[1,1])
        self.assertTrue(result['warnings']);self.assertEqual(result['paired_groups'],1)

    def test_paired_inputs_references_and_groups_are_strict(self):
        base=[self.row()]
        for changed in [self.row(id='b'),self.row(reference='ఖ'),self.row(group='other')]:
            with self.assertRaises(ValueError):paired_selected(base,[changed],100)

    def test_duplicate_records_rejected(self):
        with self.assertRaises(ValueError):aggregate([self.row(),self.row()])
        with self.assertRaises(ValueError):paired_selected([self.row(),self.row()],[self.row(),self.row()],100)

    def test_running_study_gate_precedes_final_file_access(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'status.json').write_text(json.dumps({'status':'running'}));out=root/'report.json'
            with self.assertRaises(RuntimeError):report(root,out)
            self.assertFalse(out.exists());self.assertFalse((root/'final').exists())

    def test_existing_report_never_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);out=root/'report.json';out.write_bytes(b'earlier report')
            with self.assertRaises(FileExistsError):report(root,out)
            self.assertEqual(out.read_bytes(),b'earlier report')
