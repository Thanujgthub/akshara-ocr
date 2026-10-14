"""Synthetic filesystem fixtures only; no model, images, labels or accuracy claims."""
import json
import tempfile
import unittest
from pathlib import Path
from ocr.checkpoint_io import sha
from ocr.export_selected import export_selected,verify_export


class SelectedExportTests(unittest.TestCase):
    def fixture(self,root,completed=True):
        def write(path,value):
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')
        adapter=root/'best-adapter';adapter.mkdir();(adapter/'adapter_model.safetensors').write_bytes(b'filesystem fixture only')
        write(adapter/'adapter_config.json',{'fixture':True})
        counts={'train':25000,'validation':5000,'final-test':3000};manifests={}
        for name,count in counts.items():
            path=root/(name+'.jsonl');path.write_bytes(b'fixture manifest bytes\n');manifests[name]={'count':count,'sha256':sha(path)}
        selection={'variant':'candidate','adapter':str(adapter),'basis':'fixture only'}
        write(root/'status.json',{'status':'completed' if completed else 'running'});write(root/'selection.json',selection)
        write(root/'protocol.json',{'manifests':manifests})
        write(root/'final-summary.json',{'selection':selection,'counts':counts,'final_metrics':{name:{'examples':3000} for name in ['original','pilot','candidate']}})
        write(root/'full/training_complete.json',{'manifest_examples':25000,'config':{'maximum_epochs':1}})
        write(root/'full/best.json',{'epoch':1});write(root/'configs/full.json',{'fixture':'తెలుగు 123'})
        return adapter

    def test_running_study_rejected_without_export_side_effects(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);self.fixture(root,False)
            with self.assertRaises(RuntimeError):export_selected(root)
            self.assertFalse((root/'selected-exports').exists())

    def test_separate_versioned_copies_and_source_bytes_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source=self.fixture(root);before={file:file.read_bytes() for file in root.rglob('*') if file.is_file()}
            folder,archive,receipt=export_selected(root);second,second_archive,_=export_selected(root)
            self.assertNotEqual(folder,second);self.assertTrue(archive.is_file() and second_archive.is_file())
            self.assertEqual(verify_export(folder)['role'],'final-selected-artifact')
            self.assertEqual((folder/'adapter/adapter_model.safetensors').read_bytes(),(source/'adapter_model.safetensors').read_bytes())
            self.assertEqual(receipt['zip_sha256'],sha(archive))
            for file,original in before.items():self.assertEqual(file.read_bytes(),original)

    def test_changed_manifest_or_locked_selection_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);self.fixture(root);(root/'train.jsonl').write_bytes(b'changed')
            with self.assertRaises(RuntimeError):export_selected(root)
            self.assertFalse((root/'selected-exports').exists())

    def test_tampered_export_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);self.fixture(root);folder,_,_=export_selected(root)
            (folder/'adapter/adapter_model.safetensors').write_bytes(b'tampered')
            with self.assertRaises(RuntimeError):verify_export(folder)

    def test_changed_locked_selection_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);self.fixture(root)
            selection=json.loads((root/'selection.json').read_text());selection['basis']='changed'
            (root/'selection.json').write_text(json.dumps(selection))
            with self.assertRaises(RuntimeError):export_selected(root)
            self.assertFalse((root/'selected-exports').exists())

    def test_original_selection_exports_reference_without_adapter_substitution(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);self.fixture(root)
            selection={'variant':'original','adapter':None}
            (root/'selection.json').write_text(json.dumps(selection))
            summary=json.loads((root/'final-summary.json').read_text());summary['selection']=selection
            (root/'final-summary.json').write_text(json.dumps(summary))
            folder,_,_=export_selected(root);metadata=verify_export(folder)
            self.assertIsNone(metadata['adapter_relative_path'])
            self.assertFalse((folder/'adapter').exists())
            self.assertEqual(len(json.loads((folder/'model-provenance.json').read_text())['files']),31)

    def test_bound_reporting_supplement_included(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);self.fixture(root);(root/'reports').mkdir()
            protocol=json.loads((root/'protocol.json').read_text())
            supplement={'selection':'candidate','selection_sha256':sha(root/'selection.json'),
                        'final_manifest_sha256':protocol['manifests']['final-test']['sha256']}
            (root/'reports/final-selected-analysis-v1.json').write_text(json.dumps(supplement))
            folder,_,_=export_selected(root)
            self.assertEqual(json.loads((folder/'selected-analysis.json').read_text()),supplement)
            verify_export(folder)

    def test_mismatched_reporting_supplement_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);self.fixture(root);(root/'reports').mkdir()
            (root/'reports/final-selected-analysis-v1.json').write_text(json.dumps({'selection':'pilot','selection_sha256':'wrong','final_manifest_sha256':'wrong'}))
            with self.assertRaises(RuntimeError):export_selected(root)
            self.assertFalse((root/'selected-exports/latest.json').exists())
