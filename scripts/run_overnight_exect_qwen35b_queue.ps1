# Sequential overnight queue: ExECT Qwen3.6:35b ladder Phases 0-2.
# See docs/exect_qwen35b_ladder_replication_plan.md
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false
Set-Location "C:\Users\cbrow\Code\dspy-extraction"

$experiments = @(
  # Phase 0 - contract smokes
  "configs/experiments/exect_s0_s1_smoke_qwen35b_ollama.json",
  "configs/experiments/exect_s2_smoke_qwen35b_ollama.json",
  "configs/experiments/exect_s3_smoke_qwen35b_ollama.json",
  "configs/experiments/exect_s4_smoke_qwen35b_ollama.json",
  # Phase 1 - S1 port fidelity
  "configs/experiments/exect_s0_s1_validation_cap25_qwen35b_ollama.json",
  "configs/experiments/exect_s0_s1_label_policy_regression_slice_qwen35b_ollama.json",
  "configs/experiments/exect_s0_s1_validation_full_qwen35b_ollama.json",
  # Phase 2 - S2 then S3 then S4 cap-25 then full
  "configs/experiments/exect_s2_validation_cap25_qwen35b_ollama.json",
  "configs/experiments/exect_s2_validation_full_qwen35b_ollama.json",
  "configs/experiments/exect_s3_validation_cap25_qwen35b_ollama.json",
  "configs/experiments/exect_s3_validation_full_qwen35b_ollama.json",
  "configs/experiments/exect_s4_validation_cap25_qwen35b_ollama.json",
  "configs/experiments/exect_s4_validation_full_qwen35b_ollama.json"
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $PWD "runs\overnight_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir "exect_qwen35b_ladder_phases_0_1_2_$timestamp.log"
$summaryPath = Join-Path $logDir "exect_qwen35b_ladder_phases_0_1_2_$timestamp.summary.txt"

function Write-Log {
  param([string]$Message)
  $line = "$(Get-Date -Format o) $Message"
  Write-Host $line
  $line | Out-File -FilePath $logPath -Append -Encoding utf8
}

Write-Log "ExECT Qwen3.6:35b ladder queue started (Phases 0-2, $($experiments.Count) experiments)"
Write-Log "Log: $logPath"

if (-not (Test-Path ".env")) {
  Write-Log "WARNING: .env not found in repo root; run_experiment.py may fail without API env if required."
}

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
Write-Log "Queue finished. Succeeded: $($succeeded.Count) / $($experiments.Count); Failed: $($failed.Count)"

@(
  "ExECT Qwen3.6:35b ladder Phases 0-2 summary",
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
