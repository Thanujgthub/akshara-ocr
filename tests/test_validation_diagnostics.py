import unittest
from ocr.metrics import compare
from ocr.validation_diagnostics import aligned_edits, matched


class DiagnosisTests(unittest.TestCase):
    def test_minimum_grapheme_edits_preserve_vowel_conjunct_and_digits(self):
        for ref,pred in [('కై','కై'),('క్షీ','క్షు'),('౯, 9!','9, ౯!'),('అమ్మ','అమ'),('తెలుగు',''),('','తెలుగు')]:
            self.assertEqual(len(aligned_edits(ref,pred)),compare(ref,pred)['grapheme_edits'])
        self.assertEqual(aligned_edits('కై','కై'),[])
        self.assertEqual(aligned_edits('క్షీ','క్షు'),[{'operation':'substitution','reference':'క్షీ','prediction':'క్షు'}])
        digits=aligned_edits('౯','9')
        self.assertEqual(digits,[{'operation':'substitution','reference':'౯','prediction':'9'}])

    def test_alignment_deterministic_ties(self):
        self.assertEqual(aligned_edits('aba','bab'),aligned_edits('aba','bab'))
        self.assertEqual(len(aligned_edits('aba','bab')),2)

    def test_diagnosis_rejects_changed_or_incomplete_references(self):
        manifest=[{'example_id':'a','transcription_raw':'తెలుగు'}]
        good=[{'example_id':'a','reference':'తెలుగు','prediction':'తెలుగు'}]
        self.assertEqual(set(matched(manifest,good)),{'a'})
        for bad in [[],good+good,[{**good[0],'reference':'తేలుగు'}],[{**good[0],'example_id':'b'}]]:
            with self.assertRaises(ValueError):matched(manifest,bad)


if __name__=='__main__':unittest.main()
