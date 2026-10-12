"""Bridge to the authorized model snapshot, following its documented Python API.
No substitute recognizer or guessed tokenizer is loaded.
"""
import os
import sys
import threading
from pathlib import Path
_parser=None
_lock=threading.Lock()

def available():
    repo=os.environ.get('INDIC_OCR_REPO')
    return bool(repo and (Path(repo)/'indic_ocr').exists())

def predict(path):
    global _parser
    repo=os.environ.get('INDIC_OCR_REPO')
    if not available():
        raise RuntimeError('Authorized IndicOCR snapshot unavailable. Accept model terms, download official snapshot, install its dependencies, then set INDIC_OCR_REPO. No model inference has been performed.')
    with _lock:
        if _parser is None:
            sys.path.insert(0,str(Path(repo).resolve()))
            from indic_ocr import IndicOCR
            _parser=IndicOCR.from_pretrained(repo)
        result=_parser.parse(str(path))
        if not isinstance(result,dict) or not isinstance(result.get('markdown'),str):
            raise RuntimeError('Checkpoint output contract changed: expected dict with markdown.')
        return {**result,'review_required':True,'model':{'id':'bodhan-ai/indic-ocr','revision':os.environ.get('INDIC_OCR_REVISION','unrecorded'),'adapter':None},'confidence_note':'Block conf values are layout detection confidence, not transcription confidence.'}
