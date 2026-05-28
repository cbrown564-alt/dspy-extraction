# Standalone Gan GPT D1 full validation (299 records). Detached-friendly launcher with logging.
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false
Set-Location "C:\Users\cbrow\Code\dspy-extraction"

$experiment = "configs/experiments/gan_s0_date_stage_d1_det_events_full_validation_gpt4_1_mini.json"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $PWD "runs\overnight_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir "gan_gpt_d1_full_$timestamp.log"
$pidPath = Join-Path $logDir "gan_gpt_d1_full_$timestamp.pid"

function Write-Log {
    param([string]$Message)
    $line = "$(Get-Date -Format o) $Message"
    Write-Host $line
    $line | Out-File -FilePath $logPath -Append -Encoding utf8
}

Write-Log "Gan GPT D1 full validation started"
Write-Log "Config: $experiment"
Write-Log "Log: $logPath"
Write-Log "PID file: $pidPath"
$PID | Set-Content -Path $pidPath -Encoding utf8

$env:PYTHONUNBUFFERED = "1"
$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
& uv run python scripts/run_experiment.py --experiment $experiment --env-file .env 2>&1 |
    ForEach-Object {
        $_ | Out-File -FilePath $logPath -Append -Encoding utf8
        Write-Host $_
    }
$exitCode = $LASTEXITCODE
$ErrorActionPreference = $previousErrorActionPreference

Write-Log "===== EXIT $exitCode ====="
exit $exitCode
