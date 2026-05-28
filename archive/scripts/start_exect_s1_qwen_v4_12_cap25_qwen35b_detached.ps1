# Spawn ExECT S1 v4.12 Qwen cap-25 outside Cursor/IDE terminal trees (Start-Process).
$ErrorActionPreference = "Stop"
$repoRoot = "C:\Users\cbrow\Code\dspy-extraction"
$launcher = Join-Path $repoRoot "scripts\run_exect_s1_qwen_v4_12_cap25_qwen35b.ps1"

if (-not (Test-Path $launcher)) {
    throw "Launcher not found: $launcher"
}

$proc = Start-Process -FilePath "powershell.exe" `
    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $launcher) `
    -WorkingDirectory $repoRoot `
    -WindowStyle Minimized `
    -PassThru

Write-Host "Detached ExECT S1 v4.12 Qwen cap-25 launcher started."
Write-Host "  PID: $($proc.Id)"
Write-Host "  Monitor: Get-Content runs\overnight_logs\exect_s1_qwen_v4_12_cap25_qwen35b_*.log -Tail 20 -Wait"
Write-Host "  Or:      Get-ChildItem runs\overnight_logs\exect_s1_qwen_v4_12_cap25_qwen35b_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1"
