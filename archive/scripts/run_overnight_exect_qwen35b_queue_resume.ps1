# Resume ExECT Qwen3.6:35b ladder from S2 full (after overnight stall at 30/40).
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false
Set-Location "C:\Users\cbrow\Code\dspy-extraction"

$experiments = @(
  "configs/experiments/exect_s2_validation_full_qwen35b_ollama.json",
  "configs/experiments/exect_s3_validation_cap25_qwen35b_ollama.json",
  "configs/experiments/exect_s3_validation_full_qwen35b_ollama.json",
  "configs/experiments/exect_s4_validation_cap25_qwen35b_ollama.json",
  "configs/experiments/exect_s4_validation_full_qwen35b_ollama.json"
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $PWD "runs\overnight_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir "exect_qwen35b_ladder_resume_$timestamp.log"
$summaryPath = Join-Path $logDir "exect_qwen35b_ladder_resume_$timestamp.summary.txt"

function Write-Log {
  param([string]$Message)
  $line = "$(Get-Date -Format o) $Message"
  Write-Host $line
  $line | Out-File -FilePath $logPath -Append -Encoding utf8
}

Write-Log "ExECT Qwen3.6:35b resume queue started (5 experiments from S2 full)"
Write-Log "Log: $logPath"

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
    Write-Log "OK: $exp"
  }
}

Write-Log ""
Write-Log "Resume queue finished. Succeeded: $($succeeded.Count) / $($experiments.Count); Failed: $($failed.Count)"

@(
  "ExECT Qwen3.6:35b resume queue summary",
  "Finished: $(Get-Date -Format o)",
  "Log: $logPath",
  "",
  "Succeeded ($($succeeded.Count)):",
  ($succeeded | ForEach-Object { "  OK   $_" }),
  "",
  "Failed ($($failed.Count)):",
  ($(if ($failed.Count -eq 0) { "  (none)" } else { $failed | ForEach-Object { "  FAIL $_" } }))
) | Set-Content -Path $summaryPath -Encoding utf8

Write-Log "Summary: $summaryPath"

if ($failed.Count -gt 0) {
  exit 1
}
exit 0
