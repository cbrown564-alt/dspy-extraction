$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false
Set-Location "C:\Users\cbrow\Code\dspy-extraction"

$experiment = "configs/experiments/gan_s0_l2_qwen_exact_policy_slice_qwen35b_ollama.json"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $PWD "runs\overnight_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir "gan_s0_l2_qwen_exact_policy_slice_qwen35b_$timestamp.log"

function Write-Log {
  param([string]$Message)
  $line = "$(Get-Date -Format o) $Message"
  Write-Host $line
  $line | Out-File -FilePath $logPath -Append -Encoding utf8
}

Write-Log "Gan S0 Qwen35b L2.1 Exact Policy Slice run started"
Write-Log "Experiment: $experiment"
Write-Log "Log: $logPath"

Write-Log "Ollama status before run:"
try {
  & ollama ps 2>&1 | ForEach-Object { Write-Log $_ }
} catch {
  Write-Log "WARNING: ollama ps failed; ensure Ollama is running: $_"
}

$experimentExitCode = 0
try {
  Write-Log "Starting python run_experiment.py via cmd..."
  cmd /c "uv run python scripts/run_experiment.py --experiment $experiment --env-file .env >> `"$logPath`" 2>&1"
  $experimentExitCode = $LASTEXITCODE
} catch {
  Write-Log "Execution caught PowerShell error: $_"
  $experimentExitCode = 1
}

Write-Log "Run exited with code $experimentExitCode"
Write-Log "Ollama status after run:"
try {
  & ollama ps 2>&1 | ForEach-Object { Write-Log $_ }
} catch {
  Write-Log "ollama ps unavailable: $_"
}

exit $experimentExitCode
