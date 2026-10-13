param(
  [Parameter(Mandatory=$true)][string]$ProjectRoot,
  [string]$TransferRoot = ''
)
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path $ProjectRoot).Path
foreach ($name in @('AGENTS.md','PROJECT_STATE.md','WORK_LOG.md','CODEX_CLI_HANDOFF.md','CODEX_CLI_PROMPT.md','COLAB_MIGRATION.md')) {
  $path = Join-Path $ProjectRoot $name
  if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing handoff file: $path" }
}
$git = git -C $ProjectRoot rev-parse HEAD
if (-not $git) { throw 'The handoff directory is not a Git checkout.' }
Write-Host "Project revision: $git"
git -C $ProjectRoot status --short
$python = $env:OCR_HANDOFF_PYTHON
if (-not $python) { $python = 'D:\OCR\runtime\venv\Scripts\python.exe' }
if (Test-Path -LiteralPath $python) {
  & $python -m unittest discover -s (Join-Path $ProjectRoot 'tests') -q
  if ($LASTEXITCODE -ne 0) { throw 'Software tests failed.' }
} else {
  Write-Warning "Python runtime not found at $python; run tests after configuring the new environment."
}
if ($TransferRoot) {
  $index = Join-Path $TransferRoot 'transfer-index.json'
  if (-not (Test-Path -LiteralPath $index -PathType Leaf)) { throw "Missing transfer index: $index" }
  $record = Get-Content -LiteralPath $index -Raw | ConvertFrom-Json
  foreach ($archive in $record.archives) {
    $path = Join-Path $TransferRoot $archive.file
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing transfer archive: $path" }
    $actual = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $archive.sha256) { throw "Transfer hash mismatch: $path" }
  }
  Write-Host "Transfer archives verified: $($record.archives.Count)"
}
Write-Host 'Codex CLI handoff verification passed.'
