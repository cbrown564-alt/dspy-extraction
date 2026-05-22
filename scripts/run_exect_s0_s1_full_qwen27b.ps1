# Standalone ExECT S0/S1 full validation (Qwen3.6:27b). Detached-friendly launcher with logging.
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false
Set-Location "C:\Users\cbrow\Code\dspy-extraction"

$experiment = "configs/experiments/exect_s0_s1_validation_full_qwen27b_ollama.json"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $PWD "runs\overnight_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir "exect_s0_s1_full_qwen27b_$timestamp.log"
$pidPath = Join-Path $logDir "exect_s0_s1_full_qwen27b_$timestamp.pid"

function Write-Log {
    param([string]$Message)
    $line = "$(Get-Date -Format o) $Message"
    Write-Host $line
    $line | Out-File -FilePath $logPath -Append -Encoding utf8
}

Write-Log "ExECT S0/S1 full validation Qwen3.6:27b started"
Write-Log "Config: $experiment"
Write-Log "Log: $logPath"
Write-Log "PID file: $pidPath"
$PID | Set-Content -Path $pidPath -Encoding utf8

Write-Log "Ollama status before run:"
try {
    & ollama ps 2>&1 | ForEach-Object { Write-Log $_ }
} catch {
    Write-Log "WARNING: ollama ps failed: $_"
}

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
Write-Log "Ollama status after run:"
try {
    & ollama ps 2>&1 | ForEach-Object { Write-Log $_ }
} catch {
    Write-Log "ollama ps unavailable: $_"
}

exit $exitCode
