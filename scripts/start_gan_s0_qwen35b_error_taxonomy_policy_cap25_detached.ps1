$ErrorActionPreference = "Stop"
Set-Location "C:\Users\cbrow\Code\dspy-extraction"

$scriptPath = Join-Path $PWD "scripts\run_gan_s0_qwen35b_error_taxonomy_policy_cap25.ps1"
Start-Process -FilePath "powershell.exe" -ArgumentList @(
  "-NoProfile",
  "-ExecutionPolicy",
  "Bypass",
  "-File",
  $scriptPath
) -WorkingDirectory $PWD -WindowStyle Hidden

Write-Host "Detached Gan S0 Qwen35b Error Taxonomy Policy cap-25 launcher started."
Write-Host "  Monitor: Get-Content runs\overnight_logs\gan_s0_qwen35b_error_taxonomy_policy_cap25_*.log -Tail 20 -Wait"
