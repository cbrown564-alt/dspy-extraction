$ErrorActionPreference = "Stop"
Set-Location "C:\Users\cbrow\Code\dspy-extraction"

$scriptPath = Join-Path $PWD "scripts\run_gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1.ps1"
Start-Process -FilePath "powershell.exe" -ArgumentList @(
  "-NoProfile",
  "-ExecutionPolicy",
  "Bypass",
  "-File",
  $scriptPath
) -WorkingDirectory $PWD -WindowStyle Hidden
