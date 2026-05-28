# ExECT Qwen3.6:35b S1-S5 Ladder Away Run Plan

Date: 2026-05-25

## Purpose

Run a full local Qwen3.6:35b ExECT schema ladder on the fixed validation split while avoiding local Ollama contention with the active S5 job.

## Current Active S5 Run

- Run: `runs/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama_20260525T072245Z`
- Config: `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama.json`
- Role: counts as the S5 rung unless an explicit rerun is requested.

## Queue Artifact

- Direct queue: `scripts/run_exect_qwen35b_s1_s5_ladder_today.ps1`
- Detached starter: `scripts/start_exect_qwen35b_s1_s5_ladder_today_detached.ps1`
- Logs: `runs/overnight_logs/exect_qwen35b_s1_s5_ladder_today_*.log`
- Summary: `runs/overnight_logs/exect_qwen35b_s1_s5_ladder_today_*.summary.txt`

The queue waits for the active S5 run to produce `metrics.json` or for the S5 launcher log to show an exit line, then runs the remaining rungs sequentially.

## Ladder Configs

| Rung | Config | Rationale |
| --- | --- | --- |
| S1 | `configs/experiments/exect_s0_s1_validation_full_qwen35b_ollama.json` | Frozen operational Qwen S1 anchor using v4.10 label policy. Held v4.11 and rejected v4.12 arms are not mixed into this clean ladder. |
| S2 | `configs/experiments/exect_s2_clean_ladder_v1_full_qwen35b_ollama.json` | Clean-ladder replay of GPT-promoted S2 stack with I0/C0/C1/AM guards. |
| S3 | `configs/experiments/exect_s3_clean_ladder_v1_full_qwen35b_ollama.json` | Clean-ladder replay of GPT-promoted S3 stack with inherited S2 guards plus K0/K1 cause bridges. |
| S4 | `configs/experiments/exect_s4_validation_full_qwen35b_ollama.json` | Frozen S4 Qwen anchor. |
| S5 | active run above | Promoted v2b S5 stack with frequency pre-vocab, AM guard, and frequency verifier. |

## Fixed Controls

- Dataset: `exect_v2`
- Split: `exectv2_fixed_v1:validation`
- Model config: `configs/models/exect_qwen35b_ollama.json`
- Provider/model: Ollama `qwen3.6:35b`
- Structured output: provider JSON schema with Pydantic validation
- Optimizer: none
- Test reporting: disabled

## Caveats

- This is validation-split reporting, not ExECTv2 published Table 1 reproduction.
- S1-S4 are not directly comparable as one pooled schema because field-family breadth changes by rung.
- S2/S3 are the clean-ladder variants; they deliberately exclude frequency-only and rejected S5 mechanisms.
- Local Qwen3.6:35b should run in an external or detached PowerShell process, not as an IDE child process.
