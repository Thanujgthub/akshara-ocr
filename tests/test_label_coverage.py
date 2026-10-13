import unittest
from ocr.label_coverage import analyze


class CoverageTests(unittest.TestCase):
    def test_digits_scripts_and_combining_marks_are_observed_not_repaired(self):
        texts=['తెలుగు ౯9','కై','ಕನ್ನಡ','\u0c3f','\ufffd']
        records=[{'transcription_raw':s} for s in texts]
        r=analyze(records);self.assertEqual(r['counts']['numeral_examples'],1)
        self.assertEqual({x['codepoint'] for x in r['digit_codepoints']},{'U+0C6F','U+0039'})
        self.assertEqual(r['counts']['non_telugu_letter_examples'],1)
        self.assertEqual(r['counts']['leading_combining_cluster'],1)
        self.assertEqual(r['counts']['control_or_replacement_candidate'],1)
        self.assertEqual(r['counts']['nfc_changes'],1)
        self.assertEqual([r['transcription_raw'] for r in records],texts)


if __name__=='__main__':unittest.main()
