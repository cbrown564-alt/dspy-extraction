# Resume Qwen3.5:9b model-suite ladder after S1 is done: Gan F0 first, then ExECT S4.
# Use when the sequential S1->S4->Gan queue is too slow on S4 before Gan F0.
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false
Set-Location "C:\Users\cbrow\Code\dspy-extraction"

$experiments = @(
  "configs/experiments/gan_s0_expanded_builders_prose_full_validation_qwen9b_ollama.json",
  "configs/experiments/exect_s4_validation_full_qwen9b_ollama.json"
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $PWD "runs\overnight_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir "qwen9b_model_suite_ladder_resume_gan_first_$timestamp.log"
$summaryPath = Join-Path $logDir "qwen9b_model_suite_ladder_resume_gan_first_$timestamp.summary.txt"
$pidPath = Join-Path $logDir "qwen9b_model_suite_ladder_resume_gan_first_$timestamp.pid"

function Write-Log {
  param([string]$Message)
  $line = "$(Get-Date -Format o) $Message"
  Write-Host $line
  $line | Out-File -FilePath $logPath -Append -Encoding utf8
}

Write-Log "Qwen3.5:9b resume ladder (Gan F0 -> S4) started ($($experiments.Count) full validations)"
Write-Log "Prerequisite: exect_s0_s1_validation_full_qwen9b_ollama already completed"
Write-Log "Log: $logPath"
$PID | Set-Content -Path $pidPath -Encoding utf8

Write-Log "Ollama status before queue:"
try {
  & ollama ps 2>&1 | ForEach-Object { Write-Log $_ }
} catch {
  Write-Log "WARNING: ollama ps failed: $_"
}

$failed = New-Object System.Collections.Generic.List[string]
$succeeded = New-Object System.Collections.Generic.List[string]

foreach ($exp in $experiments) {
  Write-Log ""
  Write-Log "===== START $exp ====="
  $env:PYTHONUNBUFFERED = "1"
  $previousErrorActionPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  & uv run python scripts/run_experiment.py --experiment $exp --env-file .env 2>&1 |
    ForEach-Object {
      $_ | Out-File -FilePath $logPath -Append -Encoding utf8
      Write-Host $_
    }
  $experimentExitCode = $LASTEXITCODE
  $ErrorActionPreference = $previousErrorActionPreference

  Write-Log "===== EXIT $experimentExitCode $exp ====="
  try {
    & ollama ps 2>&1 | ForEach-Object { Write-Log $_ }
  } catch {
    Write-Log "ollama ps unavailable: $_"
  }

  if ($experimentExitCode -ne 0) {
    $failed.Add($exp) | Out-Null
  } else {
    $succeeded.Add($exp) | Out-Null
  }
}

@"
Qwen3.5:9b resume ladder (Gan first) summary
Started: $timestamp
Succeeded: $($succeeded.Count)
Failed: $($failed.Count)
"@ | Set-Content -Path $summaryPath -Encoding utf8

exit $(if ($failed.Count -gt 0) { 1 } else { 0 })
