# ExECT S5 Frequency Verifier v2b Qwen35b Full-Validation Inspection

Date: 2026-05-25
Status: Complete
Decision scope: model-transfer arm; no scorer, loader, split, or gold-label changes

## Run

| Field | Value |
| --- | --- |
| Run ID | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama_20260525T072245Z` |
| Config | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama.json` |
| Model | Qwen3.6:35b via Ollama |
| Program variant | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b` |
| Verifier policy | `frequency_evidence_verify_reject_only_v2b` |
| Split | `exectv2_fixed_v1:validation` / 40 records |
| Scorer | `exect_s5_core_field_family_deterministic_v1` |
| Launcher | `scripts/start_exect_s5_v2b_full_qwen35b_detached.ps1` |
| Log | `runs/overnight_logs/exect_s5_v2b_full_qwen35b_20260525_082242.log` |

Ollama reported `qwen3.6:35b` at 77%/23% CPU/GPU with `num_ctx=262144` after the run.

## Result

| Metric | GPT v2b anchor | Qwen v2b | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **85.8%** | 85.4% | -0.4pp |
| Micro precision | 82.1% | **83.9%** | +1.8pp |
| Micro recall | **90.0%** | 87.1% | -2.9pp |
| Diagnosis F1 | 90.0% | **92.5%** | +2.5pp |
| Seizure type F1 | **84.0%** | 82.5% | -1.5pp |
| Annotated medication F1 | 88.7% | 88.7% | 0.0pp |
| Investigation F1 | **96.7%** | 94.9% | -1.8pp |
| Seizure frequency F1 | **73.9%** | 71.4% | -2.5pp |

## Evidence Diagnostics

| Metric | Qwen v2b |
| --- | ---: |
| Evidence quote support rate | 95.5% |
| Evidence quote support after ellipsis repair | 100.0% |
| Evidence quote repair rate | 1.0% |
| Evidence offsets present rate | 95.5% |
| Evidence offsets valid rate | 100.0% |

Evidence support is a deterministic quote-grounding diagnostic and is not part of benchmark-facing field-family F1.

## Interpretation

True v2b local transfer is accepted: Qwen is within 0.4pp micro F1 of the GPT v2b anchor on the same S5 surface and preserves the annotated-medication guard. It should not be described as Qwen leading GPT on v2b. The earlier Qwen v1/A3 run had higher frequency F1 (75.3%) but was not the promoted v2b verifier policy.

The main local risk is seizure-frequency recall under v2b. If S5 frequency becomes the next active local-improvement target, compare v1/A3 vs v2b on Qwen as a model-specific verifier-policy arm before changing the operational default.

## Validation

- Config contract tests passed: `uv run --extra dev pytest tests/test_experiment_configs.py -q` = 467 passed.
- Dry run passed for the v2b Qwen config before model execution.
- Detached full-validation run completed with exit 0.
- Primary metric source: `runs/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama_20260525T072245Z/metrics.json`.
