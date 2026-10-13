$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$selectedRun = 'D:/OCR/runs/word-efficient-v3'
$selectedState = Get-Content -LiteralPath "$selectedRun/status.json" -Raw | ConvertFrom-Json
if ($selectedState.status -ne 'completed') { throw 'Finish the capped study before loading its selected model into the API.' }
$selectedModel = Get-Content -LiteralPath "$selectedRun/selection.json" -Raw | ConvertFrom-Json
if (-not (Test-Path -LiteralPath "$selectedRun/final-summary.json")) { throw 'Final study evidence is missing.' }
if ($selectedModel.adapter -and -not (Test-Path -LiteralPath $selectedModel.adapter)) { throw 'Selected adapter is missing; do not fall back silently.' }
if (Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue) { throw 'An API already owns port8765. Verify and stop only that API before launching the selected model.' }
$env:PYTHONIOENCODING = 'utf-8'
$env:INDIC_OCR_REPO = 'D:/OCR/models/indic-ocr'
$env:INDIC_OCR_REVISION = 'cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25'
$env:INDIC_OCR_ADAPTER = $selectedModel.adapter
$env:OCR_RESEARCH_CONFIG = "$selectedRun/configs/full.json"
$env:OCR_RUN_ROOT = $selectedRun
$env:OCR_DATA_ROOT = 'D:/OCR/research-v2'
$env:OCR_RESEARCH_RUN = $selectedRun
$env:OCR_SELECTED_VARIANT = $selectedModel.variant
Write-Host "Validation-selected model: $($selectedModel.variant). Open http://127.0.0.1:8765"
& 'D:/OCR/runtime/venv/Scripts/python.exe' -m uvicorn ocr.server:app --host 127.0.0.1 --port 8765
