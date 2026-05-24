$ErrorActionPreference = "Stop"
Set-Location "C:\Users\cbrow\Code\dspy-extraction"

$scriptPath = Join-Path $PWD "scripts\run_gan_s0_candidate_builder_gap_v1_full_qwen35b.ps1"
Start-Process -FilePath "powershell.exe" -ArgumentList @(
  "-NoProfile",
  "-ExecutionPolicy",
  "Bypass",
  "-File",
  $scriptPath
) -WorkingDirectory $PWD -WindowStyle Hidden

Write-Host "Detached Gan S0 candidate-builder gap v1 full validation Qwen launcher started."
Write-Host "  Monitor: Get-Content runs\overnight_logs\gan_s0_candidate_builder_gap_v1_full_qwen35b_*.log -Tail 20 -Wait"
