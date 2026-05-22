$ErrorActionPreference = "Stop"
Set-Location "C:\Users\cbrow\Code\dspy-extraction"

$scriptPath = Join-Path $PWD "scripts\run_gan_s0_expanded_builders_prose_cap25_qwen35b.ps1"
Start-Process -FilePath "powershell.exe" -ArgumentList @(
  "-NoProfile",
  "-ExecutionPolicy",
  "Bypass",
  "-File",
  $scriptPath
) -WorkingDirectory $PWD -WindowStyle Hidden

Write-Host "Detached Gan S0 F0 cap-25 Qwen launcher started."
Write-Host "  Monitor: Get-Content runs\overnight_logs\gan_s0_expanded_builders_prose_cap25_qwen35b_*.log -Tail 20 -Wait"
