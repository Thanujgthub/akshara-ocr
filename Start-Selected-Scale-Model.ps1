param([string]$RunDirectory = 'D:/OCR/runs/word-efficient-v3')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$runDirectory = $RunDirectory
$runStatus = Get-Content -LiteralPath "$runDirectory/status.json" -Raw | ConvertFrom-Json
if ($runStatus.status -ne 'completed') { throw 'Research is still active or needs attention. Wait for final testing; no unfinished checkpoint will be served.' }
$selection = Get-Content -LiteralPath "$runDirectory/selection.json" -Raw | ConvertFrom-Json
if ($selection.adapter) { $env:INDIC_OCR_ADAPTER = $selection.adapter } else { $env:INDIC_OCR_ADAPTER = '' }
$env:OCR_RESEARCH_CONFIG = "$runDirectory/configs/full.json"
$env:OCR_RESEARCH_RUN = $runDirectory
$env:INDIC_OCR_REPO = 'D:/OCR/models/indic-ocr'
$env:INDIC_OCR_REVISION = 'cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25'
$env:PYTHONIOENCODING = 'utf-8'
Write-Host "Serving validation-selected variant: $($selection.variant). Read the final report for statistical evidence."
Write-Host 'Stop the existing local server first if port 8765 is already in use. Page recognition remains experimental.'
& 'D:/OCR/runtime/venv/Scripts/python.exe' -m uvicorn ocr.server:app --host 127.0.0.1 --port 8765
