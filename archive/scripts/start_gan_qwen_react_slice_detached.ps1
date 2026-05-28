# Spawn Gan Qwen ReAct slice outside Cursor/IDE terminal trees (Start-Process).
$ErrorActionPreference = "Stop"
$repoRoot = "C:\Users\cbrow\Code\dspy-extraction"
$launcher = Join-Path $repoRoot "scripts\run_gan_qwen_react_slice.ps1"

if (-not (Test-Path $launcher)) {
    throw "Launcher not found: $launcher"
}

$proc = Start-Process -FilePath "powershell.exe" `
    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $launcher) `
    -WorkingDirectory $repoRoot `
    -WindowStyle Minimized `
    -PassThru

Write-Host "Detached Gan Qwen ReAct slice launcher started."
Write-Host "  PID: $($proc.Id)"
Write-Host "  Monitor: Get-Content runs\overnight_logs\gan_qwen_react_slice_*.log -Tail 20 -Wait"
