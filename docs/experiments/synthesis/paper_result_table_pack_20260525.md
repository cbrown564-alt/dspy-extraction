# Paper Result Table Pack

Date: 2026-05-25  
Status: current source-backed manuscript table pack  
Decision scope: paper table synthesis; no scorer, loader, registry, or model-output changes

## Purpose

This note refreshes the manuscript-facing result tables after the May 25 clean-ladder and local-transfer work. It supersedes `docs/archive/experiments/synthesis/pre_component_pivot/paper_result_table_pack_20260524.md` for current manuscript tables, while preserving that earlier pack as historical evidence.

The rows below are intended for paper drafting, not for benchmark-reproduction claims. They separate full-validation headline evidence from cap-25 gates, arm rejections, and diagnostic forensics.

## Global Caveats

- Gan rows in this historical table use the synthetic `gan_2026_fixed_v1:validation` split and `gan_frequency_deterministic_v1`; they are not Gan Real(300) or Real(150) reporting. New benchmark-comparison tables should lead with `gan2026_paper_reproduction` and keep these canonical metrics as diagnostics/sensitivity analysis.
- Gan gold remains `seizure_frequency_number[0]`; `reference[0]` is a secondary diagnostic cross-check.
- ExECT rows use the fixed 40-record `exectv2_fixed_v1:validation` split and deterministic field-family scorers; they are not CUI-aware ExECTv2 Table 1 reproduction.
- ExECT S1-S4 ladder rows change field-family scope across rungs, so pooled micro F1 should be read as schema-breadth pressure plus family-composition effects.
- ExECT S5 is an optimized core-field surface, not a simple monotonic ladder rung: it includes diagnosis, seizure type, annotated medication, investigation, and seizure frequency, and omits medication temporality.
- Evidence support is deterministic quote/source grounding unless a run explicitly uses evidence as a prediction-affecting control.
- Cap-25 and slice rows are gates or diagnostics; full-validation rows carry manuscript headline evidence.

## Table 1 - Gan S0 Operational Surface

| Arm | Run ID | Program / variant | Split / N | Scorer | Monthly | Purist | Pragmatic | Schema valid | Evidence support | Decision / caveat |
| --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| GPT 4.1-mini candidate-builder gap v1 | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` | `gan_frequency_s0_temporal_candidates_single_pass`; `gan_s0_candidate_builder_gap_v1` | validation / 299 evaluated | `gan_frequency_deterministic_v1` | **80.6%** | 86.0% | 88.6% | 100.0% | 100.0% | Historical canonical diagnostic default on synthetic validation; rescore with `gan2026_paper_reproduction` for benchmark comparison. |
| Qwen3.6:35b candidate-builder gap v1 | `gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z` | same surface | validation / 299 predicted, 297 valid scored | `gan_frequency_deterministic_v1` | 70.7% | 83.2% | **90.6%** | 99.3% | 99.7% | Accepted local transfer arm, but not hosted parity; GPT remains +9.9pp monthly. |

Primary sources: `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z/metrics.json`; `runs/gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z/metrics.json`; `docs/experiments/gan/gan_s0_operational_default_promotion_review_20260523.md`; `docs/experiments/gan/gan_s0_qwen35b_builder_gap_l2_error_forensics_20260525.md`.

## Table 2 - Gan L2 Qwen Policy Gate

| Arm | Run ID | Scope | Baseline / reference | Monthly | Purist | Pragmatic | Schema valid | Evidence support | Decision |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Qwen exact-policy cap-25 | `gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama_20260525T162702Z` | cap-25 validation gate | baseline parent: `gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1_20260521T065534Z` at 40.0% monthly; GPT E1 reference at 52.0% | **69.6%** | 73.9% | 91.3% | 92.0% | 100.0% | Promote to full validation per gate and user override accepting one schema-invalid record. |

Interpretation: the cap-25 gate suggests Qwen's Gan gap is partly prompt-policy calibration, especially exact canonical-label preservation under sparse deterministic candidate coverage. This row is not yet a full-validation replacement for the Qwen 70.7% operational transfer row.

Primary source: `docs/experiments/gan/gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama_inspection_20260525.md`.

## Table 3 - ExECT Clean Schema Ladder

| Schema level | Current GPT anchor | GPT micro F1 | Current Qwen anchor | Qwen micro F1 | Decision / caveat |
| --- | --- | ---: | --- | ---: | --- |
| S1 | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` | **92.3%** | `exect_s1_clean_ladder_v2_diagnosis_stable_full_qwen35b_ollama_20260525T103640Z` | 85.9% | GPT S1 remains the frozen benchmark-facing anchor; Qwen clean v2 restores the local ladder shape. |
| S2 | `exect_s2_clean_ladder_v1_full_gpt4_1_mini_20260525T073213Z` | 82.7% | Qwen clean ladder anchor reported in S1 clean-ladder inspection | **84.4%** | Clean-ladder S2 includes transferable AM, investigation, and comorbidity guards. |
| S3 | `exect_s3_clean_ladder_v1_full_gpt4_1_mini_20260525T073224Z` | 74.4% | Qwen clean ladder anchor reported in S1 clean-ladder inspection | **75.3%** | Sparse S3-only families remain weak; do not describe this as solved broad-schema extraction. |
| S4 | `exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` | 65.5% | `exect_s4_validation_full_qwen35b_ollama_20260520T160914Z` | **67.5%** | Pooled Qwen lead is family-profile dependent; avoid simple model-ranking language. |

Primary sources: `docs/experiments/exect/exect_s1_clean_ladder_qwen_validation_v1_inspection_20260525.md`; `docs/experiments/exect/exect_s2_s3_clean_ladder_gpt_validation_v1_inspection_20260525.md`; `docs/archive/experiments/synthesis/pre_component_pivot/paper_frozen_operational_defaults_20260524.md`.

## Table 4 - ExECT S5 Promoted Core Surface And Local Transfer

| Model | Run ID | Program | Split / N | Scorer | Micro F1 | Micro precision | Micro recall | Seizure-frequency F1 | Decision / caveat |
| --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| GPT 4.1-mini | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z` | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b` | validation / 40 | `exect_s5_core_field_family_deterministic_v1` | **85.8%** | 82.1% | **90.0%** | **73.9%** | Current S5 operational default. |
| Qwen3.6:35b / Ollama | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama_20260525T072245Z` | same true-v2b stack | validation / 40 | same | 85.4% | **83.9%** | 87.1% | 71.4% | Accepted local transfer / near-parity; not a Qwen lead and not deployment readiness. |
| GPT 5.5 | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt5_5_openai_20260526T130247Z` | same true-v2b stack | validation / 40 | same | 82.6% | 77.4% | 88.5% | 74.5% | A2 closed-model anchor; does not displace GPT 4.1-mini as S5 headline anchor despite slightly higher frequency F1. |

Primary sources: `docs/experiments/synthesis/l1_2_s5_local_vs_closed_comparison_20260525.md`; `docs/experiments/exect/exect_s5_best_closed_gpt5_5_anchor_inspection_20260526.md`.

## Table 5 - Rejected Or Superseded Arms For Narrative Control

| Finding | Run ID / artifact | Headline metric | Decision | Manuscript use |
| --- | --- | ---: | --- | --- |
| ExECT S5 per-family parallel ceiling regressed. | `exect_s5_core_field_family_parallel_v2b_cap25_gpt4_1_mini_20260524T212052Z` | 83.6% cap-25 micro, -4.6pp vs v2b single-pass cap-25 | Reject as tested | Negative decomposition arm; not closure of all decomposition mechanisms. |
| ExECT S5 combined strict v2 verifier collapsed frequency recall. | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2_cap25_gpt4_1_mini_20260524T205934Z` | 60.0% seizure-frequency recall | Reject as tested | Supports using the isolated v2b verifier rather than stacked strict qualitative filtering. |
| ExECT S5 temporal medication guard over-pruned benchmark-facing medication gold. | `exect_s5_frequency_pre_vocab_am_guard_temporal_frequency_verify_cap25_gpt4_1_mini_20260524T203942Z` | annotated-medication recall 79.3% | Reject as tested | Caveat that medication temporality precision work is not part of promoted S5 core. |
| ExECT S5 high-precision frequency candidates reduced recall. | `exect_s5_frequency_pre_vocab_high_precision_cap25_gpt4_1_mini_20260524T141503Z` | seizure-frequency F1 56.3% | Reject as tested | Justifies keeping high-recall frequency candidates as the baseline. |
| Gan unknown-overuse, GEPA G1, and GEPA G2 arms failed cap gates. | `docs/archive/experiments/synthesis/pre_component_pivot/paper_frozen_arm_reject_table_20260524.md` | monthly 16.0%, 60.0%, and 48.0% respectively | Reject as tested | Negative mechanism-search evidence with `decision_scope: arm`. |

Primary source: `docs/archive/experiments/synthesis/pre_component_pivot/paper_frozen_arm_reject_table_20260524.md`.

## Claim Readiness

| Claim | Status | Required wording |
| --- | --- | --- |
| Gan candidate-builder gap v1 is the current best internal Gan S0 operational surface. | Supported | Say synthetic validation, cite run IDs, and avoid Real benchmark language. |
| Gan Qwen local transfer remains weaker than GPT on monthly accuracy, but L2 exact-policy cap-25 suggests a targeted improvement path. | Supported with gate caveat | Keep the 69.6% exact-policy result as cap-25 only until full validation completes. |
| ExECT clean ladder now supports a coherent local Qwen breadth story across S1-S4. | Supported with caveat | State that field-family scope changes across rungs and S3 sparse families remain weak. |
| ExECT S5 v2b has accepted Qwen local transfer near GPT performance. | Supported | Say near-parity on synthetic validation, not Qwen-leading and not deployment-ready. |
| GPT 5.5 improves the promoted ExECT S5 overall headline. | Unsupported by A2 | GPT 5.5 slightly improves seizure-frequency F1 but lowers pooled micro F1 and seizure-type F1 under the fixed v2b stack. |
| The project beats published ExECTv2 or Gan benchmarks. | Unsupported / blocked | Requires CUI-aware ExECT reproduction and Gan Real reporting protocol/access. |

## Verification Notes

This synthesis used only existing run artifacts and inspection docs. No model calls, scorer changes, loader changes, or registry schema changes were made.
