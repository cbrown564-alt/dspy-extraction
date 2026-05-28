# Paper Frozen Operational Defaults

Date: 2026-05-24  
Status: Frozen operational defaults for manuscript tables  
Decision scope: Paper table freeze; no scorer, loader, registry, or model-output changes

## Purpose

This document freezes the operational defaults for the clinical extraction system across the ExECTv2 and Gan datasets. These models and configurations represent the best-performing and most stable baselines/arms validated on the synthetic splits, serving as the benchmark references for current manuscript claims.

---

## 1. Gan S0 Operational Defaults

| Model / Configuration | Run ID | Split / N | Scorer | Monthly Acc. | Purist F1 | Pragmatic F1 | Schema Valid | Evidence Support | Key Decision / Caveats |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| **GPT 4.1-mini Candidate-Builder Gap v1** (Operational Default) | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` | validation / 299 | `gan_frequency_deterministic_v1` | 80.6% | 86.0% | 88.6% | 100.0% | 100.0% | Best overall monthly accuracy. Uses temporal candidates pre-injection. Synthetic validation only; not Real benchmark. |
| **Qwen3.6:35b Candidate-Builder Gap v1** (Local Transfer) | `gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z` | validation / 299 predicted, 297 valid scored | `gan_frequency_deterministic_v1` | 70.7% | 83.2% | 90.6% | 99.3% | 99.7% | Promoted local transfer model. Monthly accuracy trails GPT by ~10pp, but achieves high pragmatic accuracy. |

**Primary Sources:**
- `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z/metrics.json`
- `runs/gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z/metrics.json`
- `docs/experiments/gan/gan_s0_operational_default_promotion_review_20260523.md`

---

## 2. ExECT Schema-Ladder Operational Defaults (S1–S5)

All runs are evaluated on the 40-record ExECTv2 validation split using `gpt-4.1-mini`.

| Schema Level | Field-Family Scope | Run ID | Program / Variant | Scorer | Pooled Micro F1 | Individual Family F1 Results | Key Caveats / Decisions |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| **S1** | Diagnosis, Seizure Type, Annotated Medication | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` | Single-pass v4.10 with benchmark policy / bridges | `exect_field_family_deterministic_v1` | 92.3% | Diagnosis: 93.8%<br>Seizure Type: 90.5%<br>Medication: 92.8% | Frozen S1 benchmark view. High alignment on core families. |
| **S2** | S1 + Investigation, Comorbidity | `exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` | S2 v1.3 single-pass | `exect_s2_field_family_deterministic_v1` | 80.9% | Investigation: 90.0%<br>Comorbidity: 69.3% | Comorbidity is a known weaker family in this rung. |
| **S3** | S2 + Onset, Birth Hist., Cause, When Diag. | `exect_s3_validation_full_gpt4_1_mini_20260519T235439Z` | S3 v1.2 single-pass | `exect_s3_field_family_deterministic_v1` | 72.1% | Added sparse families are weak; comorbidity remains weak. | S3 comparison anchor. |
| **S4** | S3 + Seizure Freq., Medication Temporality | `exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` | S4 v1.2 single-pass | `exect_s4_field_family_deterministic_v1` | 65.5% | Seizure Freq.: 45.7%<br>Med. Temporality: 62.5% | S4 baseline. Seizure frequency is extremely challenging at this stage. |
| **S5** | S5 Core (diagnosis, seizure type, annotated medication, investigation, seizure frequency) | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z` | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b` | `exect_s5_core_field_family_deterministic_v1` | **85.8%** | Diagnosis: 90.0%<br>Seizure Type: 84.0%<br>Medication: 88.7%<br>Investigation: 96.7%<br>Seizure Freq.: **73.9%** | **Current S5 paper freeze.** High-recall pre-vocab + AM guard + v2b reject-only verifier (v1.2 extractor + v2 temporal/scope rules). Supersedes v1 verifier + A3 row (85.5% micro / 72.3% freq). Combined v2 arm rejected (D2). |

**Superseded S5 anchors (historical):**

| Run ID | Program | Micro F1 | Seizure Freq. F1 | Notes |
| --- | --- | ---: | ---: | --- |
| `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_full_gpt4_1_mini_20260524T195813Z` | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v1` | 85.5% | 72.3% | v1 verifier + A3 prompt policy |
| `exect_s5_frequency_pre_vocab_am_guard_full_gpt4_1_mini_20260524T182142Z` | `exect_s5_frequency_pre_vocab_am_guard_non_asm_brand_alias_v1` | 81.4% | 60.2% | AM guard only |

**Primary Sources:**
- `runs/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z/metrics.json`
- `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini.json`
- `docs/experiments/exect/exect_s5_frequency_verifier_v2b_full_validation_promotion_review_20260524.md`
- `docs/experiments/exect/exect_s5_frequency_verifier_v2_cap25_rejection_20260524.md`
- `docs/experiments/exect/exect_s5_frequency_verifier_v2b_cap25_inspection_20260524.md`

---

## 3. Local Qwen Replication (ExECT S1–S5 Reruns)

Replication of the ExECT schema ladder using local model `Qwen3.6:35b` via Ollama, compared to GPT-4.1-mini.

| Schema Level | GPT Anchor Run / Micro F1 | Qwen Run ID / Micro F1 | Delta | Key Observations / Caveats |
| --- | ---: | --- | ---: | --- |
| **S1** | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` / 92.3% | `exect_s0_s1_validation_full_qwen35b_ollama_20260520T042117Z` / 79.0% | -13.3 pp | Qwen lags primarily on Seizure Type granularity (55.7% vs. GPT 90.5%). |
| **S2** | `exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` / 80.9% | `exect_s2_validation_full_qwen35b_ollama_20260520T073552Z` / 82.6% | +1.7 pp | Qwen slightly leads pooled micro, but family performance profile varies. |
| **S3** | `exect_s3_validation_full_gpt4_1_mini_20260519T235439Z` / 72.1% | `exect_s3_validation_full_qwen35b_ollama_20260520T092244Z` / 72.2% | +0.1 pp | Equal pooled performance; local latency and family-specific deltas persist. |
| **S4** | `exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` / 65.5% | `exect_s4_validation_full_qwen35b_ollama_20260520T160914Z` / 67.5% | +2.0 pp | Higher pooled micro, but per-family divergences prevent ranking Qwen as superior overall. |
| **S5 true v2b** | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z` / 85.8% | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama_20260525T072245Z` / 85.4% | -0.4 pp | Accepted local transfer / near-parity. Seizure-frequency F1 trails GPT (71.4% vs 73.9%); prior Qwen v1/A3 run is superseded for v2b claims. |

---

## 4. Standing Research Caveats

1. **Benchmark Claims**: No claims of beating published clinical benchmarks (ExECTv2 or Gan 2026) are supported on these synthetic validation splits. Comparison against published work is blocked until official CUI-aware reproduction and Real clinical dataset access is unlocked.
2. **Medication Temporality**: High-precision temporal pruning (e.g. distinguishing previous/suggested/planned ASMs) is deliberately excluded from the S5 baseline and remains an active research workstream. The promoted S5 stack includes a reject-only **seizure-frequency** verifier (second LLM pass), not medication-temporality extraction.
3. **Seizure Frequency Scorer**: Do not change deterministic scorer semantics. All frequency comparisons must use identical metric denominators and raw label normalizations. The promoted S5 frequency F1 (73.9%) is not comparable to Gan monthly-frequency metrics.
