# Spawn Gan GPT temporal full validation outside Cursor/IDE terminal trees (Start-Process).
$ErrorActionPreference = "Stop"
$repoRoot = "C:\Users\cbrow\Code\dspy-extraction"
$launcher = Join-Path $repoRoot "scripts\run_gan_gpt_temporal_full_validation.ps1"

if (-not (Test-Path $launcher)) {
    throw "Launcher not found: $launcher"
}

$proc = Start-Process -FilePath "powershell.exe" `
    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $launcher) `
    -WorkingDirectory $repoRoot `
    -WindowStyle Minimized `
    -PassThru

Write-Host "Detached Gan GPT temporal full validation launcher started."
Write-Host "  PID: $($proc.Id)"
Write-Host "  Monitor: Get-Content runs\overnight_logs\gan_gpt_temporal_full_*.log -Tail 20 -Wait"
Write-Host "  Or:      Get-ChildItem runs\overnight_logs\gan_gpt_temporal_full_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1"
