"""Bridge to the authorized model snapshot, following its documented Python API.
No substitute recognizer or guessed tokenizer is loaded.
"""
import os
import sys
import threading
from contextlib import nullcontext
from pathlib import Path
_parser=None
_lock=threading.Lock()

def available():
    repo=os.environ.get('INDIC_OCR_REPO')
    return bool(repo and (Path(repo)/'indic_ocr.py').is_file() and (Path(repo)/'weights/ocr/model-00001-of-00001.safetensors').is_file())

def _run(parser,path,mode):
    if mode=='page':return parser.parse(str(path))
    if mode!='word':raise ValueError('Mode must be page or word')
    from PIL import Image
    from idp_recognizer import CropRequest
    from idp_contract import TEXT_PROMPT
    from idp_crops import area_clamp
    backend=parser._ocr.backend;original_config=backend.config
    try:
        backend.config=original_config.merged(max_tokens=64)
        with Image.open(path) as image:
            return {'markdown':backend.transcribe([CropRequest(area_clamp(image.convert('RGB')),TEXT_PROMPT)])[0],'blocks':[]}
    finally:backend.config=original_config

def predict(path,mode='page',variant='adapted'):
    global _parser
    repo=os.environ.get('INDIC_OCR_REPO')
    if not available():
        raise RuntimeError('Authorized IndicOCR snapshot unavailable. Accept model terms, download official snapshot, install its dependencies, then set INDIC_OCR_REPO. No model inference has been performed.')
    with _lock:
        if _parser is None:
            sys.path.insert(0,str(Path(repo).resolve()))
            from indic_ocr import IndicOCR
            import torch
            from transformers import AutoProcessor
            from .stream_load import load_model
            from idp_recognizer import HfRecognizer
            from idp_offline import IndicBlockOCR
            from idp_types import RecognizerConfig
            torch.set_num_threads(4)
            backend=HfRecognizer.__new__(HfRecognizer)
            backend._torch=torch;backend.config=RecognizerConfig(max_tokens=512)
            backend.batch_size=1;backend.ckpt=str(Path(repo)/'weights/ocr')
            backend.processor=AutoProcessor.from_pretrained(backend.ckpt,local_files_only=True)
            backend.processor.tokenizer.padding_side='left'
            backend.model=load_model(backend.ckpt,os.environ.get('OCR_DEVICE','cuda'),torch.bfloat16)
            adapter=os.environ.get('INDIC_OCR_ADAPTER')
            if adapter:
                from peft import PeftModel
                backend.model=PeftModel.from_pretrained(backend.model,adapter)
            backend.model.eval()
            backend.eos_token_id=backend.processor.tokenizer.eos_token_id
            backend.pad_token_id=backend.processor.tokenizer.pad_token_id
            _parser=IndicOCR.from_pretrained(repo,device='cpu',max_new_tokens=512)
            _parser._ocr=IndicBlockOCR(backend=backend,config=backend.config)
        if variant not in {'adapted','original'}:raise ValueError('Unknown model variant')
        model=_parser._ocr.backend.model
        context=model.disable_adapter() if variant=='original' and os.environ.get('INDIC_OCR_ADAPTER') else nullcontext()
        with context:result=_run(_parser,path,mode)
        if not isinstance(result,dict) or not isinstance(result.get('markdown'),str):
            raise RuntimeError('Checkpoint output contract changed: expected dict with markdown.')
        return {**result,'review_required':True,'granularity':mode,'model':{'id':'bodhan-ai/indic-ocr','revision':os.environ.get('INDIC_OCR_REVISION','unrecorded'),'adapter':os.environ.get('INDIC_OCR_ADAPTER') if variant=='adapted' else None},'confidence_note':'Layout scores are not text confidence. Word adaptation does not establish page accuracy.'}

def loaded():
    return _parser is not None
