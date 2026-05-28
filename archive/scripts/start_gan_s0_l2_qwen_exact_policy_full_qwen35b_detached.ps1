$ErrorActionPreference = "Stop"
Set-Location "C:\Users\cbrow\Code\dspy-extraction"

$scriptPath = Join-Path $PWD "scripts\run_gan_s0_l2_qwen_exact_policy_full_qwen35b.ps1"
Start-Process -FilePath "powershell.exe" -ArgumentList @(
  "-NoProfile",
  "-ExecutionPolicy",
  "Bypass",
  "-File",
  $scriptPath
) -WorkingDirectory $PWD -WindowStyle Hidden

Write-Host "Detached Gan S0 Qwen35b L2.1 Exact Policy Full Validation launcher started."
Write-Host "  Monitor: Get-Content runs\overnight_logs\gan_s0_l2_qwen_exact_policy_full_qwen35b_*.log -Tail 20 -Wait"
