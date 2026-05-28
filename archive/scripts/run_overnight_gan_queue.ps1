$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false
Set-Location "C:\Users\cbrow\Code\dspy-extraction"

function New-GanConfig {
  param(
    [string]$Base,
    [string]$Out,
    [string]$ExperimentId,
    [Nullable[int]]$MaxRecords
  )

  $cfg = Get-Content $Base -Raw | ConvertFrom-Json
  $cfg.experiment_id = $ExperimentId
  $cfg.hypothesis = "[overnight local LLM queue] " + $cfg.hypothesis

  if ($null -eq $MaxRecords) {
    $cfg.PSObject.Properties.Remove("max_records")
  } else {
    if ($cfg.PSObject.Properties.Name -contains "max_records") {
      $cfg.max_records = $MaxRecords
    } else {
      $cfg | Add-Member -NotePropertyName max_records -NotePropertyValue $MaxRecords
    }
  }

  $json = $cfg | ConvertTo-Json -Depth 20
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText((Join-Path $PWD $Out), $json + [Environment]::NewLine, $utf8NoBom)
}

New-GanConfig `
  -Base "configs/experiments/gan_s0_latency_qwen35b_direct_cap3.json" `
  -Out "configs/experiments/gan_s0_overnight_qwen35b_direct_cap25.json" `
  -ExperimentId "gan_s0_overnight_qwen35b_direct_cap25" `
  -MaxRecords 25

New-GanConfig `
  -Base "configs/experiments/gan_s0_latency_qwen35b_direct_cap3.json" `
  -Out "configs/experiments/gan_s0_overnight_qwen35b_direct_cap100.json" `
  -ExperimentId "gan_s0_overnight_qwen35b_direct_cap100" `
  -MaxRecords 100

New-GanConfig `
  -Base "configs/experiments/gan_s0_latency_qwen35b_direct_cap3.json" `
  -Out "configs/experiments/gan_s0_overnight_qwen35b_direct_full_validation.json" `
  -ExperimentId "gan_s0_overnight_qwen35b_direct_full_validation" `
  -MaxRecords $null

New-GanConfig `
  -Base "configs/experiments/gan_s0_maxbudget_qwen35b_direct_cap1.json" `
  -Out "configs/experiments/gan_s0_overnight_qwen35b_direct_maxbudget_cap25.json" `
  -ExperimentId "gan_s0_overnight_qwen35b_direct_maxbudget_cap25" `
  -MaxRecords 25

New-GanConfig `
  -Base "configs/experiments/gan_s0_maxbudget_qwen35b_cot_cap1.json" `
  -Out "configs/experiments/gan_s0_overnight_qwen35b_cot_maxbudget_cap3.json" `
  -ExperimentId "gan_s0_overnight_qwen35b_cot_maxbudget_cap3" `
  -MaxRecords 3

New-GanConfig `
  -Base "configs/experiments/gan_s0_maxbudget_qwen9b_direct_cap3.json" `
  -Out "configs/experiments/gan_s0_overnight_qwen9b_direct_maxbudget_cap25.json" `
  -ExperimentId "gan_s0_overnight_qwen9b_direct_maxbudget_cap25" `
  -MaxRecords 25

New-GanConfig `
  -Base "configs/experiments/gan_s0_maxbudget_qwen9b_direct_bootstrap_cap3.json" `
  -Out "configs/experiments/gan_s0_overnight_qwen9b_direct_bootstrap_maxbudget_cap10.json" `
  -ExperimentId "gan_s0_overnight_qwen9b_direct_bootstrap_maxbudget_cap10" `
  -MaxRecords 10

$experiments = @(
  "configs/experiments/gan_s0_overnight_qwen35b_direct_cap25.json",
  "configs/experiments/gan_s0_overnight_qwen35b_direct_cap100.json",
  "configs/experiments/gan_s0_overnight_qwen35b_direct_full_validation.json",
  "configs/experiments/gan_s0_overnight_qwen35b_direct_maxbudget_cap25.json",
  "configs/experiments/gan_s0_overnight_qwen35b_cot_maxbudget_cap3.json",
  "configs/experiments/gan_s0_overnight_qwen9b_direct_maxbudget_cap25.json",
  "configs/experiments/gan_s0_overnight_qwen9b_direct_bootstrap_maxbudget_cap10.json"
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $PWD "runs\\overnight_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir "gan_overnight_queue_$timestamp.log"

"Queue started at $(Get-Date -Format o)" | Tee-Object -FilePath $logPath -Append

foreach ($exp in $experiments) {
  "`n===== START $exp =====" | Tee-Object -FilePath $logPath -Append
  $previousErrorActionPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  & uv run python scripts/run_experiment.py --experiment $exp --env-file .env 2>&1 |
    Tee-Object -FilePath $logPath -Append
  $experimentExitCode = $LASTEXITCODE
  $ErrorActionPreference = $previousErrorActionPreference
  "===== EXIT $experimentExitCode $exp =====" | Tee-Object -FilePath $logPath -Append

  "`nOllama residency after run:" | Tee-Object -FilePath $logPath -Append
  & ollama ps 2>&1 | Tee-Object -FilePath $logPath -Append

  if ($experimentExitCode -ne 0) {
    throw "Experiment failed: $exp"
  }
}

"Queue finished at $(Get-Date -Format o)" | Tee-Object -FilePath $logPath -Append
