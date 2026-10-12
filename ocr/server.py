import io
import os
import tempfile
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .model import available, predict
app=FastAPI(title='Akshara OCR API',version='0.1.0')
origins=os.environ.get('OCR_ALLOWED_ORIGINS','http://127.0.0.1:8765,http://localhost:8765').split(',')
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_methods=['GET','POST'],allow_headers=['Content-Type'],allow_credentials=False)

@app.get('/api/health')
def health():
    return {'status':'ok','model_ready':available(),'model_load_verified':False,'note':'model_ready indicates snapshot present; actual loading occurs on first prediction'}

@app.post('/api/predict')
def predict_page(file:UploadFile):
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
            return predict(path)
    except Exception:
        raise HTTPException(503,'Model inference failed. Check server environment and official checkpoint compatibility; no fallback text was generated.')

app.mount('/',StaticFiles(directory=str(Path(__file__).resolve().parents[1]/'dist'),html=True),name='website')
