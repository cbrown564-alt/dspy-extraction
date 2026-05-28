# Spawn the 2026-05-25 ExECT Qwen3.6:35b S1-S5 ladder queue outside the IDE process tree.
$ErrorActionPreference = "Stop"

$repoRoot = "C:\Users\cbrow\Code\dspy-extraction"
$launcher = Join-Path $repoRoot "scripts\run_exect_qwen35b_s1_s5_ladder_today.ps1"

if (-not (Test-Path $launcher)) {
    throw "Launcher not found: $launcher"
}

$proc = Start-Process -FilePath "powershell.exe" `
    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $launcher) `
    -WorkingDirectory $repoRoot `
    -WindowStyle Hidden `
    -PassThru

Write-Host "Detached ExECT Qwen3.6:35b S1-S5 ladder queue started."
Write-Host "  PID: $($proc.Id)"
Write-Host "  Monitor: Get-Content runs\overnight_logs\exect_qwen35b_s1_s5_ladder_today_*.log -Tail 40 -Wait"
Write-Host "  Summary: Get-ChildItem runs\overnight_logs\exect_qwen35b_s1_s5_ladder_today_*.summary.txt | Sort-Object LastWriteTime -Descending | Select-Object -First 1"
