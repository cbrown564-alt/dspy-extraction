# L1.2 ExECT S5 Local vs Closed Model Comparison

Date: 2026-05-25
Status: Complete after true v2b Qwen rerun
Decision scope: L-track local transfer assessment for ExECT S5; no scorer or loader changes
Comparison group: `exect_s5_frequency_verify_v2b_model_comparison`; varied factor: `model_track`

## Purpose

This document replaces the earlier v1/A3 Qwen comparison with a true v2b rerun. The previous Qwen run used `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v1` with `frequency_evidence_verify_reject_only_v1`; it is now a superseded comparison aid, not evidence for v2b local parity.

Current comparison:

| Model | Run ID | Config | Program |
| --- | --- | --- | --- |
| GPT 4.1-mini | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z` | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini.json` | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b` |
| Qwen3.6:35b / Ollama | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama_20260525T072245Z` | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama.json` | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b` |

Both runs use `exectv2_fixed_v1:validation` (n=40), scorer `exect_s5_core_field_family_deterministic_v1`, no ChainOfThought, no BootstrapFewShot, and no GEPA.

## Headline Metrics

| Metric | GPT 4.1-mini v2b | Qwen3.6:35b v2b | Delta (Qwen - GPT) |
| --- | ---: | ---: | ---: |
| Micro F1 | **85.8%** | 85.4% | -0.4pp |
| Micro precision | 82.1% | **83.9%** | +1.8pp |
| Micro recall | **90.0%** | 87.1% | -2.9pp |

Verdict: **accepted local transfer / near-parity, not a Qwen lead.** Qwen v2b is within 0.4pp micro F1 of the GPT v2b anchor, but the frequency family drops below GPT because v2b is more recall-suppressing on Qwen than the earlier v1/A3 run.

## Per-Family Metrics

| Family | GPT F1 | GPT P | GPT R | Qwen F1 | Qwen P | Qwen R | Delta F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| annotated_medication | 88.7% | 79.7% | 100.0% | 88.7% | 79.7% | 100.0% | 0.0pp |
| diagnosis | 90.0% | 94.7% | 85.7% | **92.5%** | 97.4% | 88.1% | +2.5pp |
| investigation | **96.7%** | 96.7% | 96.7% | 94.9% | 96.6% | 93.3% | -1.8pp |
| seizure_frequency | **73.9%** | 71.4% | 69.4% | 73.2% | **79.1%** | 69.8% | -2.5pp |
| seizure_type | **84.0%** | 79.2% | 89.4% | 82.5% | 80.0% | 85.1% | -1.5pp |

Qwen remains strong on diagnosis and identical on annotated medication. The local transfer risk is concentrated in seizure_frequency recall and, secondarily, seizure_type recall.

## Evidence Grounding

| Metric | GPT 4.1-mini v2b | Qwen3.6:35b v2b |
| --- | ---: | ---: |
| Evidence offsets present rate | 94.1% | 95.5% |
| Evidence offsets valid rate | 100.0% | 100.0% |
| Evidence quote support rate (raw) | 94.1% | 95.5% |
| Evidence quote repair rate | 0.0% | 1.0% |
| Evidence quote support after ellipsis repair | n/a | 100.0% |

Evidence support is diagnostic quote grounding only; it is not clinician-adjudicated evidence quality.

## Superseded v1/A3 Qwen Run

The earlier run `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_full_qwen35b_ollama_20260524T213206Z` scored 86.2% micro F1 and 75.3% seizure_frequency F1, but it used the v1 verifier policy. It should be described as a useful historical comparison, not as the local v2b result.

| Run | Program / verifier | Micro F1 | Seizure freq F1 | Status |
| --- | --- | ---: | ---: | --- |
| `...full_qwen35b_ollama_20260524T213206Z` | v1 / `frequency_evidence_verify_reject_only_v1` | 86.2% | 75.3% | Superseded for L1.1 v2b claim |
| `...v2b_full_qwen35b_ollama_20260525T072245Z` | v2b / `frequency_evidence_verify_reject_only_v2b` | 85.4% | 71.4% | Current local transfer evidence |

## L-Track Status

| Claim | Supported? |
| --- | --- |
| Qwen3.6:35b achieves S5 micro F1 near-parity with GPT 4.1-mini on the true v2b stack | Yes: 85.4% vs 85.8% (-0.4pp) |
| Qwen seizure_frequency F1 meets or exceeds GPT on v2b | No: 71.4% vs 73.9% (-2.5pp) |
| Qwen annotated_medication F1 meets GPT | Yes: 88.7% = 88.7% |
| Qwen evidence grounding meets GPT diagnostic quote support | Yes: 95.5% raw / 100.0% after repair vs GPT 94.1% |
| Local S5 deployment claim is paper-ready | Needs careful wording: accepted local transfer on synthetic validation, not deployment readiness |

L1.1/L1.2 should be marked **complete as accepted local transfer**, with the caveat that v2b lowers Qwen frequency recall relative to the superseded v1/A3 run.

## Remaining L-Track Work

| Card | Status | Notes |
| --- | --- | --- |
| L1.1 S5 Qwen true v2b full-validation | Done | Run `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama_20260525T072245Z` |
| L1.2 S5 local vs closed comparison | Done | This document |
| L1.3 S2/S3 clean-ladder Qwen replay | Ready | Do not overlap with another local Ollama job |
| L2 G0 Qwen error forensics | Backlog | 87 monthly mismatches |
| L3 S1 Qwen seizure-type arm | Backlog | Largest remaining local gap |
| L4 Best-closed S4/S5 anchors | Backlog | GPT 5.5 S4; closed S5 suite untested |

## Artifact Provenance

| Artifact | Path |
| --- | --- |
| Qwen true v2b run | `runs/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama_20260525T072245Z/` |
| Qwen v2b config | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama.json` |
| Qwen detached log | `runs/overnight_logs/exect_s5_v2b_full_qwen35b_20260525_082242.log` |
| GPT v2b anchor run | `runs/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z/` |
| S5 v2b promotion review | `docs/experiments/exect/exect_s5_frequency_verifier_v2b_full_validation_promotion_review_20260524.md` |
