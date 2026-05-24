$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false
Set-Location "C:\Users\cbrow\Code\dspy-extraction"

$experiment = "configs/experiments/gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation.json"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $PWD "runs\overnight_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir "gan_s0_candidate_builder_gap_v1_full_qwen35b_$timestamp.log"

function Write-Log {
  param([string]$Message)
  $line = "$(Get-Date -Format o) $Message"
  Write-Host $line
  $line | Out-File -FilePath $logPath -Append -Encoding utf8
}

Write-Log "Gan S0 Qwen35b candidate-builder gap v1 full validation run started"
Write-Log "Experiment: $experiment"
Write-Log "Log: $logPath"

Write-Log "Ollama status before run:"
try {
  & ollama ps 2>&1 | ForEach-Object { Write-Log $_ }
} catch {
  Write-Log "WARNING: ollama ps failed; ensure Ollama is running: $_"
}

$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
& uv run python scripts/run_experiment.py --experiment $experiment --env-file .env 2>&1 |
  ForEach-Object {
    $_ | Out-File -FilePath $logPath -Append -Encoding utf8
    Write-Host $_
  }
$experimentExitCode = $LASTEXITCODE
$ErrorActionPreference = $previousErrorActionPreference

Write-Log "Run exited with code $experimentExitCode"
Write-Log "Ollama status after run:"
try {
  & ollama ps 2>&1 | ForEach-Object { Write-Log $_ }
} catch {
  Write-Log "ollama ps unavailable: $_"
}

exit $experimentExitCode
