# Spawn Qwen3.5:9b model-suite full ladder outside Cursor/IDE terminal trees (Start-Process).
$ErrorActionPreference = "Stop"
$repoRoot = "C:\Users\cbrow\Code\dspy-extraction"
$launcher = Join-Path $repoRoot "scripts\run_qwen9b_model_suite_ladder.ps1"

if (-not (Test-Path $launcher)) {
    throw "Launcher not found: $launcher"
}

$proc = Start-Process -FilePath "powershell.exe" `
    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $launcher) `
    -WorkingDirectory $repoRoot `
    -WindowStyle Minimized `
    -PassThru

Write-Host "Detached Qwen3.5:9b model-suite ladder started."
Write-Host "  PID: $($proc.Id)"
Write-Host "  Monitor: Get-Content runs\overnight_logs\qwen9b_model_suite_ladder_*.log -Tail 20 -Wait"
