import unittest
from ocr.freeze_efficient import exact_components,check_isolation


class CappedFreezeTests(unittest.TestCase):
    def test_trainer_refuses_over_cap_and_extra_initial_epochs_before_loading_gpu(self):
        from ocr.scale_experiment import ScaleExperiment
        e=ScaleExperiment.__new__(ScaleExperiment);e.cfg={'maximum_training_examples':25000,'maximum_epochs':1}
        with self.assertRaises(ValueError):e.train_scale([None]*25001,[],None,1)
        with self.assertRaises(ValueError):e.train_scale([None],[],None,2)
    def test_exact_count_never_splits_groups(self):
        groups={str(i):[{'example_id':f'{i}:{j}','leakage_group':str(i)} for j in range(n)] for i,n in enumerate([4,7,3,8,2])}
        rows=exact_components(groups,13,42);self.assertEqual(len(rows),13)
        for key in {r['leakage_group'] for r in rows}:self.assertEqual(sum(r['leakage_group']==key for r in rows),len(groups[key]))
        self.assertEqual(rows,exact_components(groups,13,42))

    def test_shortage_reports_real_count_below_cap(self):
        groups={'a':[{'x':i} for i in range(4)],'b':[{'x':i} for i in range(6)]}
        self.assertEqual(len(exact_components(groups,9,42)),6)
        self.assertEqual(len(exact_components(groups,3,42)),0)

    def test_cross_split_duplicate_or_document_is_rejected(self):
        row={k:'a' for k in ['example_id','leakage_group','group_id','original_sha256','pixel_sha256']}
        other={k:'b' for k in row};check_isolation({'train':[row],'validation':[other]})
        for field in row:
            with self.assertRaises(RuntimeError):check_isolation({'train':[row],'validation':[{**other,field:'a'}]})
