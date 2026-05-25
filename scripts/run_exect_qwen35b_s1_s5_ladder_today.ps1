# Away-safe ExECT Qwen3.6:35b schema ladder queue for 2026-05-25.
# Waits for the already-running S5 v2b job to clear, then runs S1-S4 sequentially.
param(
    [switch]$SkipWaitForCurrentS5,
    [switch]$RerunS5
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false

$repoRoot = "C:\Users\cbrow\Code\dspy-extraction"
Set-Location $repoRoot

$logDir = Join-Path $repoRoot "runs\overnight_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logPath = Join-Path $logDir "exect_qwen35b_s1_s5_ladder_today_$timestamp.log"
$summaryPath = Join-Path $logDir "exect_qwen35b_s1_s5_ladder_today_$timestamp.summary.txt"
$pidPath = Join-Path $logDir "exect_qwen35b_s1_s5_ladder_today_$timestamp.pid"
$PID | Set-Content -Path $pidPath -Encoding utf8

$currentS5Run = Join-Path $repoRoot "runs\exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama_20260525T072245Z"

$experiments = @(
    [pscustomobject]@{
        Level = "S1"
        Config = "configs/experiments/exect_s0_s1_validation_full_qwen35b_ollama.json"
        Note = "Frozen operational Qwen S1 anchor (v4.10), not held/rejected prompt-policy arms."
    },
    [pscustomobject]@{
        Level = "S2"
        Config = "configs/experiments/exect_s2_clean_ladder_v1_full_qwen35b_ollama.json"
        Note = "Clean-ladder v1 replay with I0/C0/C1/AM guards."
    },
    [pscustomobject]@{
        Level = "S3"
        Config = "configs/experiments/exect_s3_clean_ladder_v1_full_qwen35b_ollama.json"
        Note = "Clean-ladder v1 replay with inherited S2 guards plus K0/K1 cause bridges."
    },
    [pscustomobject]@{
        Level = "S4"
        Config = "configs/experiments/exect_s4_validation_full_qwen35b_ollama.json"
        Note = "Frozen S4 Qwen anchor."
    }
)

if ($RerunS5) {
    $experiments += [pscustomobject]@{
        Level = "S5"
        Config = "configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama.json"
        Note = "Rerun requested explicitly; otherwise the active 20260525T072245Z S5 run is the S5 rung."
    }
}

function Write-Log {
    param([string]$Message)
    $line = "$(Get-Date -Format o) $Message"
    Write-Host $line
    $line | Out-File -FilePath $logPath -Append -Encoding utf8
}

function Get-LatestS5Log {
    Get-ChildItem $logDir -Filter "exect_s5_v2b_full_qwen35b_*.log" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
}

function Wait-ForCurrentS5 {
    if ($SkipWaitForCurrentS5) {
        Write-Log "Skipping wait for the active S5 run because -SkipWaitForCurrentS5 was supplied."
        return
    }

    if (-not (Test-Path $currentS5Run)) {
        Write-Log "Current S5 run directory not found; continuing without wait: $currentS5Run"
        return
    }

    $metricsPath = Join-Path $currentS5Run "metrics.json"
    if (Test-Path $metricsPath) {
        Write-Log "Current S5 run already has metrics.json; continuing."
        return
    }

    Write-Log "Waiting for active S5 v2b Qwen run to clear before starting S1-S4."
    Write-Log "Current S5 run: $currentS5Run"
    Write-Log "This avoids overlapping local Ollama jobs on the same Qwen3.6:35b instance."

    while ($true) {
        if (Test-Path $metricsPath) {
            Write-Log "Current S5 run completed with metrics.json; continuing."
            return
        }

        $latestLog = Get-LatestS5Log
        if ($null -ne $latestLog) {
            $tail = Get-Content $latestLog.FullName -Tail 80 -ErrorAction SilentlyContinue
            $exitLine = $tail | Select-String -Pattern "===== EXIT (-?\d+) =====" | Select-Object -Last 1
            if ($null -ne $exitLine) {
                Write-Log "Current S5 launcher exited according to $($latestLog.Name): $($exitLine.Line)"
                if (-not (Test-Path $metricsPath)) {
                    Write-Log "WARNING: S5 exit was seen but metrics.json is absent. The queue will continue so S1-S4 can run."
                }
                return
            }

            $ageMinutes = [math]::Round(((Get-Date) - $latestLog.LastWriteTime).TotalMinutes, 1)
            if ($ageMinutes -ge 30) {
                Write-Log "WARNING: latest S5 log has not changed for $ageMinutes minutes: $($latestLog.FullName)"
            } else {
                Write-Log "S5 still running or settling; latest log age ${ageMinutes}m: $($latestLog.Name)"
            }
        } else {
            Write-Log "No S5 log found yet; waiting."
        }

        Start-Sleep -Seconds 300
    }
}

function Invoke-Experiment {
    param(
        [string]$Level,
        [string]$Config,
        [string]$Note
    )

    Write-Log ""
    Write-Log "===== START $Level $Config ====="
    Write-Log "Note: $Note"
    Write-Log "Ollama status before ${Level}:"
    try {
        & ollama ps 2>&1 | ForEach-Object { Write-Log $_ }
    } catch {
        Write-Log "WARNING: ollama ps failed before ${Level}: $_"
    }

    $env:PYTHONUNBUFFERED = "1"
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & uv run python scripts/run_experiment.py --experiment $Config --env-file .env 2>&1 |
        ForEach-Object {
            $_ | Out-File -FilePath $logPath -Append -Encoding utf8
            Write-Host $_
        }
    $experimentExitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    Write-Log "===== EXIT $experimentExitCode $Level $Config ====="
    Write-Log "Ollama status after ${Level}:"
    try {
        & ollama ps 2>&1 | ForEach-Object { Write-Log $_ }
    } catch {
        Write-Log "ollama ps unavailable after ${Level}: $_"
    }

    return $experimentExitCode
}

Write-Log "ExECT Qwen3.6:35b S1-S5 ladder queue started."
Write-Log "Log: $logPath"
Write-Log "PID file: $pidPath"
Write-Log "S5 policy: active run 20260525T072245Z counts as S5 unless -RerunS5 is supplied."

Wait-ForCurrentS5

$failed = New-Object System.Collections.Generic.List[string]
$succeeded = New-Object System.Collections.Generic.List[string]

foreach ($experiment in $experiments) {
    $exitCode = Invoke-Experiment -Level $experiment.Level -Config $experiment.Config -Note $experiment.Note
    if ($exitCode -ne 0) {
        $failed.Add("$($experiment.Level) $($experiment.Config)") | Out-Null
        Write-Log "FAILED (continuing queue): $($experiment.Level) $($experiment.Config)"
    } else {
        $succeeded.Add("$($experiment.Level) $($experiment.Config)") | Out-Null
        Write-Log "OK: $($experiment.Level) $($experiment.Config)"
    }
}

Write-Log ""
Write-Log "Ladder queue finished. Succeeded: $($succeeded.Count) / $($experiments.Count); Failed: $($failed.Count)"

@(
    "ExECT Qwen3.6:35b S1-S5 ladder queue summary",
    "Finished: $(Get-Date -Format o)",
    "Log: $logPath",
    "PID file: $pidPath",
    "S5 active run counted unless rerun: $currentS5Run",
    "RerunS5: $RerunS5",
    "",
    "Succeeded ($($succeeded.Count)):",
    ($succeeded | ForEach-Object { "  OK   $_" }),
    "",
    "Failed ($($failed.Count)):",
    ($(if ($failed.Count -eq 0) { "  (none)" } else { $failed | ForEach-Object { "  FAIL $_" } }))
) | Set-Content -Path $summaryPath -Encoding utf8

Write-Log "Summary: $summaryPath"

if ($failed.Count -gt 0) {
    exit 1
}
exit 0
