# Sequential model-suite ladder: Qwen3.5:9b full validation on frozen S1, S4, and Gan F0.
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false
Set-Location "C:\Users\cbrow\Code\dspy-extraction"

$experiments = @(
  "configs/experiments/exect_s0_s1_validation_full_qwen9b_ollama.json",
  "configs/experiments/exect_s4_validation_full_qwen9b_ollama.json",
  "configs/experiments/gan_s0_expanded_builders_prose_full_validation_qwen9b_ollama.json"
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $PWD "runs\overnight_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir "qwen9b_model_suite_ladder_$timestamp.log"
$summaryPath = Join-Path $logDir "qwen9b_model_suite_ladder_$timestamp.summary.txt"
$pidPath = Join-Path $logDir "qwen9b_model_suite_ladder_$timestamp.pid"

function Write-Log {
  param([string]$Message)
  $line = "$(Get-Date -Format o) $Message"
  Write-Host $line
  $line | Out-File -FilePath $logPath -Append -Encoding utf8
}

Write-Log "Qwen3.5:9b model-suite ladder started ($($experiments.Count) full validations)"
Write-Log "Log: $logPath"
Write-Log "Summary: $summaryPath"
Write-Log "PID file: $pidPath"
$PID | Set-Content -Path $pidPath -Encoding utf8

Write-Log "Ollama status before queue:"
try {
  & ollama ps 2>&1 | ForEach-Object { Write-Log $_ }
} catch {
  Write-Log "WARNING: ollama ps failed; ensure Ollama is running: $_"
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
  Write-Log "Ollama residency after run:"
  try {
    & ollama ps 2>&1 | ForEach-Object { Write-Log $_ }
  } catch {
    Write-Log "ollama ps unavailable: $_"
  }

  if ($experimentExitCode -ne 0) {
    $failed.Add($exp) | Out-Null
    Write-Log "FAILED (continuing queue): $exp"
  } else {
    $succeeded.Add($exp) | Out-Null
  }
}

Write-Log ""
Write-Log "===== QUEUE COMPLETE ====="
Write-Log "Succeeded: $($succeeded.Count)"
foreach ($exp in $succeeded) {
  Write-Log "  OK  $exp"
}
Write-Log "Failed: $($failed.Count)"
foreach ($exp in $failed) {
  Write-Log "  FAIL $exp"
}

@"
Qwen3.5:9b model-suite ladder summary
Started: $timestamp
Log: $logPath
Succeeded ($($succeeded.Count)):
$($succeeded -join "`n")
Failed ($($failed.Count)):
$($failed -join "`n")
"@ | Set-Content -Path $summaryPath -Encoding utf8

if ($failed.Count -gt 0) {
  exit 1
}

exit 0
