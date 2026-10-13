$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:PYTHONIOENCODING = 'utf-8'
$ocrResearchPython = 'D:/OCR/runtime/venv/Scripts/python.exe'
Write-Host 'Resuming the capped research plan. A second active pipeline is refused.'
Write-Host 'Monitor: http://127.0.0.1:8765/research-v2 (start Start-Akshara.ps1 separately).'
& $ocrResearchPython -u -m ocr.run_efficient
if ($LASTEXITCODE -ne 0) { throw 'Research needs attention. Inspect D:/OCR/runs/word-efficient-v3/failure.json and the active experiment log. Do not restart the retired 80,083-example pipeline.' }
