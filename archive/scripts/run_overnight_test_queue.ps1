$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false
Set-Location "C:\Users\cbrow\Code\dspy-extraction"

function New-TestConfig {
  param(
    [string]$Base,
    [string]$Out,
    [string]$SplitName
  )

  if (-not (Test-Path $Base)) {
    throw "Base config not found: $Base"
  }

  $cfg = Get-Content $Base -Raw | ConvertFrom-Json
  
  # Suffix or prefix the experiment id
  $cfg.experiment_id = "test_holdout_" + $cfg.experiment_id
  $cfg.hypothesis = "[test-holdout validation] " + $cfg.hypothesis
  
  # Change split parameters
  $cfg.split_name = $SplitName
  if ($cfg.PSObject.Properties.Name -contains "report_on_test_split") {
    $cfg.report_on_test_split = $true
  } else {
    $cfg | Add-Member -NotePropertyName report_on_test_split -NotePropertyValue $true
  }

  # Remove max_records if any, to ensure full test run
  if ($cfg.PSObject.Properties.Name -contains "max_records") {
    $cfg.PSObject.Properties.Remove("max_records")
  }

  $json = $cfg | ConvertTo-Json -Depth 20
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText((Join-Path $PWD $Out), $json + [Environment]::NewLine, $utf8NoBom)
}

# Ensure directory for generated configs exists
New-Item -ItemType Directory -Force -Path "configs/experiments/test_holdout" | Out-Null

# 1. Generate test configs
# ExECT S1 Qwen
New-TestConfig -Base "configs/experiments/exect_s1_clean_ladder_v2_diagnosis_stable_full_qwen35b_ollama.json" `
              -Out "configs/experiments/test_holdout/exect_s1_clean_ladder_v2_qwen35b_test.json" `
              -SplitName "exectv2_fixed_v1:test"

# ExECT S2 GPT & Qwen
New-TestConfig -Base "configs/experiments/exect_s2_clean_ladder_v1_full_gpt4_1_mini.json" `
              -Out "configs/experiments/test_holdout/exect_s2_clean_ladder_v1_gpt4_test.json" `
              -SplitName "exectv2_fixed_v1:test"
New-TestConfig -Base "configs/experiments/exect_s2_validation_full_qwen35b_ollama.json" `
              -Out "configs/experiments/test_holdout/exect_s2_clean_ladder_v1_qwen35b_test.json" `
              -SplitName "exectv2_fixed_v1:test"

# ExECT S3 GPT & Qwen
New-TestConfig -Base "configs/experiments/exect_s3_clean_ladder_v1_full_gpt4_1_mini.json" `
              -Out "configs/experiments/test_holdout/exect_s3_clean_ladder_v1_gpt4_test.json" `
              -SplitName "exectv2_fixed_v1:test"
New-TestConfig -Base "configs/experiments/exect_s3_clean_ladder_v1_full_qwen35b_ollama.json" `
              -Out "configs/experiments/test_holdout/exect_s3_clean_ladder_v1_qwen35b_test.json" `
              -SplitName "exectv2_fixed_v1:test"

# ExECT S4 GPT & Qwen
New-TestConfig -Base "configs/experiments/exect_s4_validation_full_gpt4_1_mini.json" `
              -Out "configs/experiments/test_holdout/exect_s4_clean_ladder_v1_gpt4_test.json" `
              -SplitName "exectv2_fixed_v1:test"
New-TestConfig -Base "configs/experiments/exect_s4_validation_full_qwen35b_ollama.json" `
              -Out "configs/experiments/test_holdout/exect_s4_clean_ladder_v1_qwen35b_test.json" `
              -SplitName "exectv2_fixed_v1:test"

# ExECT S5 GPT & Qwen
New-TestConfig -Base "configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini.json" `
              -Out "configs/experiments/test_holdout/exect_s5_v2b_gpt4_test.json" `
              -SplitName "exectv2_fixed_v1:test"
New-TestConfig -Base "configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama.json" `
              -Out "configs/experiments/test_holdout/exect_s5_v2b_qwen35b_test.json" `
              -SplitName "exectv2_fixed_v1:test"

# Gan S0 GPT & Qwen
New-TestConfig -Base "configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation.json" `
              -Out "configs/experiments/test_holdout/gan_s0_builder_gap_v1_gpt4_test.json" `
              -SplitName "gan_2026_fixed_v1:test"
New-TestConfig -Base "configs/experiments/gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation.json" `
              -Out "configs/experiments/test_holdout/gan_s0_builder_gap_v1_qwen35b_test.json" `
              -SplitName "gan_2026_fixed_v1:test"

$test_experiments = @(
  "configs/experiments/exect_s0_s1_validation_test_gpt4_1_mini.json", # Frozen pre-existing S1 test config
  "configs/experiments/test_holdout/exect_s1_clean_ladder_v2_qwen35b_test.json",
  "configs/experiments/test_holdout/exect_s2_clean_ladder_v1_gpt4_test.json",
  "configs/experiments/test_holdout/exect_s2_clean_ladder_v1_qwen35b_test.json",
  "configs/experiments/test_holdout/exect_s3_clean_ladder_v1_gpt4_test.json",
  "configs/experiments/test_holdout/exect_s3_clean_ladder_v1_qwen35b_test.json",
  "configs/experiments/test_holdout/exect_s4_clean_ladder_v1_gpt4_test.json",
  "configs/experiments/test_holdout/exect_s4_clean_ladder_v1_qwen35b_test.json",
  "configs/experiments/test_holdout/exect_s5_v2b_gpt4_test.json",
  "configs/experiments/test_holdout/exect_s5_v2b_qwen35b_test.json",
  "configs/experiments/test_holdout/gan_s0_builder_gap_v1_gpt4_test.json",
  "configs/experiments/test_holdout/gan_s0_builder_gap_v1_qwen35b_test.json"
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $PWD "runs/overnight_test_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir "test_holdout_overnight_queue_$timestamp.log"

"Test Holdout queue started at $(Get-Date -Format o)" | Tee-Object -FilePath $logPath -Append

foreach ($exp in $test_experiments) {
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
    throw "Test experiment failed: $exp"
  }
}

"Test holdout queue finished at $(Get-Date -Format o)" | Tee-Object -FilePath $logPath -Append
