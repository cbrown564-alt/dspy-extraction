# Standalone Gan Qwen ReAct temporal-tools regression slice (14 records). Detached-friendly launcher.
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false
Set-Location "C:\Users\cbrow\Code\dspy-extraction"

$experiment = "configs/experiments/gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails.json"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $PWD "runs\overnight_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir "gan_qwen_react_slice_$timestamp.log"
$pidPath = Join-Path $logDir "gan_qwen_react_slice_$timestamp.pid"

function Write-Log {
    param([string]$Message)
    $line = "$(Get-Date -Format o) $Message"
    Write-Host $line
    $line | Out-File -FilePath $logPath -Append -Encoding utf8
}

Write-Log "Gan Qwen ReAct temporal-tools slice started"
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
