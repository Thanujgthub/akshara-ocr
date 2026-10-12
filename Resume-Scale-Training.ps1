$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:PYTHONIOENCODING = 'utf-8'
$ocrResearchPython = 'D:/OCR/runtime/venv/Scripts/python.exe'
Write-Host 'Resuming existing research checkpoints. A second active pipeline is refused.'
Write-Host 'Monitor: http://127.0.0.1:8765/research-v2 (start Start-Akshara.ps1 separately).'
& $ocrResearchPython -u -m ocr.run_scale
if ($LASTEXITCODE -ne 0) { throw 'Research needs attention. Inspect D:/OCR/runs/word-scale-v2/failure.json and the active experiment log.' }
