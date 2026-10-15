import io
import os
import tempfile
import logging
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from fastapi import FastAPI, UploadFile, HTTPException, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .model import available, predict, loaded
app=FastAPI(title='Akshara OCR API',version='0.1.0')

@app.get('/favicon.ico', include_in_schema=False)
def favicon():
    return Response(status_code=204)

origins=os.environ.get('OCR_ALLOWED_ORIGINS','http://127.0.0.1:8765,http://localhost:8765').split(',')
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_methods=['GET','POST'],allow_headers=['Content-Type'],allow_credentials=False)

def gpu_worker_active():
    """Preflight workers can be live while the prior coordinator state says failed."""
    import psutil
    for process in psutil.process_iter(['cmdline']):
        try:
            command=process.info.get('cmdline') or []
            if '-m' not in command:continue
            index=command.index('-m')+1
            if index>=len(command):continue
            module=command[index]
            if module=='ocr.colab_benchmark':return True
            if module=='ocr.scale_experiment' and index+1<len(command) and command[index+1] in {'train','smoke','evaluate'}:
                return True
        except psutil.Error:continue
    return False

def study_busy():
    from .study_routes import ROOT,read
    return (read(ROOT/'status.json') or {}).get('status')=='running' or any(
        (read(Path('D:/OCR/runs')/name/'status.json') or {}).get('status') in {'running','preparing','prepared'}
        for name in ['word-scale-v2','word-efficient-v3']) or gpu_worker_active()

@app.get('/api/health')
def health():
    return {'status':'ok','model_ready':available() and not study_busy(),'model_load_verified':loaded(),'training_active':study_busy(),'note':'Inference waits until the local GPU study completes.'}

@app.post('/api/predict')
def predict_page(file:UploadFile,mode:str=Form('page'),variant:str=Form('adapted')):
    if study_busy():raise HTTPException(409,'Inference is paused for study preparation, training or testing. Open Study progress for the current stage.')
    if mode not in {'page','word'}: raise HTTPException(422,'Mode must be page or word')
    if variant not in {'adapted','original'}:raise HTTPException(422,'Variant must be adapted or original')
    if not available(): raise HTTPException(503,'Model unavailable. Configure INDIC_OCR_REPO with an authorized snapshot and install official dependencies.')
    content=file.file.read(20*1024*1024+1)
    if len(content)>20*1024*1024: raise HTTPException(413,'Maximum file size is 20 MB')
    try:
        with Image.open(io.BytesIO(content)) as im:
            if im.format not in {'JPEG','PNG','WEBP'}: raise ValueError('Unsupported image format')
            if im.width*im.height>40_000_000: raise ValueError('Image exceeds 40 megapixels')
            im.verify()
    except (UnidentifiedImageError,OSError,ValueError,Image.DecompressionBombError) as e:
        raise HTTPException(422,'Invalid or unsupported image: '+str(e))
    try:
        with tempfile.TemporaryDirectory(prefix='akshara-') as directory:
            path=Path(directory)/'page.png'
            with Image.open(io.BytesIO(content)) as im:
                from PIL import ImageOps
                ImageOps.exif_transpose(im).convert('RGB').save(path)
            return predict(path,mode,variant)
    except Exception:
        logging.getLogger('akshara').exception('Local OCR inference failed')
        raise HTTPException(503,'Model inference failed. Check server environment and official checkpoint compatibility; no fallback text was generated.')

from .study_routes import router
app.include_router(router)
from .scale_routes import router as scale_router
app.include_router(scale_router)
from .review_routes import router as review_router
app.include_router(review_router)
app.mount('/',StaticFiles(directory=str(Path(__file__).resolve().parents[1]/'dist'),html=True),name='website')
