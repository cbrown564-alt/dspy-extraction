# Spawn Gan-first resume ladder (S1 already done). Stop any active 9b ladder first.
$ErrorActionPreference = "Stop"
$repoRoot = "C:\Users\cbrow\Code\dspy-extraction"
$launcher = Join-Path $repoRoot "scripts\run_qwen9b_model_suite_ladder_resume_gan_first.ps1"

if (-not (Test-Path $launcher)) {
    throw "Launcher not found: $launcher"
}

$proc = Start-Process -FilePath "powershell.exe" `
    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $launcher) `
    -WorkingDirectory $repoRoot `
    -WindowStyle Minimized `
    -PassThru

Write-Host "Detached Qwen3.5:9b resume ladder (Gan F0 -> S4) started."
Write-Host "  PID: $($proc.Id)"
Write-Host "  Monitor: Get-Content runs\overnight_logs\qwen9b_model_suite_ladder_resume_gan_first_*.log -Tail 20 -Wait"
