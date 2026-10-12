$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:PYTHONIOENCODING = 'utf-8'
if (-not $env:INDIC_OCR_REPO) { $env:INDIC_OCR_REPO = 'D:/OCR/models/indic-ocr' }
if (-not $env:INDIC_OCR_REVISION) { $env:INDIC_OCR_REVISION = 'cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25' }
if (-not $env:INDIC_OCR_ADAPTER) { $env:INDIC_OCR_ADAPTER = 'D:/OCR/runs/word-pilot-v1/trained/adapter' }
$ocrPython = 'D:/OCR/runtime/venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $ocrPython)) { throw 'Set up the Python 3.12 CUDA environment described in README.md first.' }
Write-Host 'Open http://127.0.0.1:8765 — Ctrl+C stops the local server.'
& $ocrPython -m uvicorn ocr.server:app --host 127.0.0.1 --port 8765
