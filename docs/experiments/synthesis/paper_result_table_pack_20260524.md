# Paper Result Table Pack

Date: 2026-05-24  
Status: frozen source-backed manuscript table pack  
Decision scope: paper table freeze; no scorer, loader, registry, or model-output changes

## Purpose

This note freezes the compact results tables that are safe to use as the current manuscript evidence pack. Values below were checked against primary `runs/<run_id>/metrics.json` files when the run directory is present, then cross-checked against promoted inspection or synthesis docs and `docs/experiments/synthesis/experiment_registry.json`.

The pack intentionally avoids SDK drafts as evidence. The review-only Cursor source map `docs/experiments/cursor_sdk_drafts/20260524T131249Z_paper_synthesis_draft.md` was used only as a checklist for rows to verify.

## Global Caveats

- Gan results use `gan_2026_fixed_v1:validation` synthetic validation records and `gan_frequency_deterministic_v1`; they are not published Gan Real(300) or Real(150) reproduction claims.
- Gan primary gold is `seizure_frequency_number[0]`; `reference[0]` is a secondary difficulty signal.
- ExECT results use the fixed 40-record ExECTv2 validation split and local field-family deterministic scorers; they are not CUI-aware ExECTv2 Table 1 reproduction claims.
- ExECT schema-ladder rows change field-family scope across S1-S4. Treat the pooled micro F1 trend as schema breadth pressure, not a calibrated learning curve.
- Evidence support is a deterministic quote/source-grounding diagnostic, not human-adjudicated evidence quality.
- Cap-25 and slice rows are search or diagnostic gates only; full-validation rows carry the manuscript headline evidence unless explicitly described otherwise.

## Table 1 - Gan S0 Current Operational Surface

| Arm | Run ID | Config / program surface | Split / N | Scorer | Monthly | Purist | Pragmatic | Schema valid | Evidence support | Decision / caveat |
| --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| GPT 4.1-mini candidate-builder gap v1 | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` | `configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation.json`; `gan_frequency_s0_temporal_candidates_single_pass` | validation / 299 evaluated | `gan_frequency_deterministic_v1` | 80.6% | 86.0% | 88.6% | 100.0% | 100.0% | Historical canonical diagnostic default on synthetic validation; not Real benchmark reproduction and should be rescored with `gan2026_paper_reproduction` for direct paper comparison. |
| Qwen3.6:35b candidate-builder gap v1 | `gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z` | `configs/experiments/gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation.json`; same program surface | validation / 299 predicted, 297 valid scored | `gan_frequency_deterministic_v1` | 70.7% | 83.2% | 90.6% | 99.3% | 99.7% | Accepted local transfer arm; not hosted parity because GPT remains +9.9 pp monthly. |

Primary sources: `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z/metrics.json`; `runs/gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z/metrics.json`; `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_full_validation_rerun_inspection_20260523.md`; `docs/experiments/gan/gan_s0_operational_default_promotion_review_20260523.md`; `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_qwen35b_full_validation_inspection_20260523.md`.

## Table 2 - Gan S0 Architecture History And Superseded Anchors

| Arm | Run ID | Model | Split / N | Monthly | Purist | Pragmatic | Schema valid | Evidence support | Decision / caveat |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Synthesis bootstrap single-pass | `gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z` | GPT 4.1-mini | validation / 299 | 62.9% | 70.1% | 73.9% | 97.3% | 89.9% | Superseded; original run directory is referenced by docs but may be absent locally. |
| Verify-repair v2 | `gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z` | GPT 4.1-mini | validation / 299 | 65.4% | 72.7% | 79.2% | 96.7% | 92.7% | Superseded by temporal candidates and later builder-gap v1. |
| Temporal candidates verify-repair v1.1 | `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z` | GPT 4.1-mini | validation / 299 | 65.1% | 76.5% | 84.2% | 99.7% | 100.0% | Former promoted operational surface; superseded by builder-gap v1. |
| Temporal candidates verify-repair v1.1 | `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T230324Z` | Qwen3.6:35b | validation / 299 | 65.8% | 75.5% | 82.6% | 99.7% | 100.0% | Former local promoted surface; superseded by Qwen builder-gap transfer. |

Interpretation: the paper-safe story is not "verify-repair alone wins." The stronger current claim is that deterministic temporal candidate recall before LLM adjudication moved Gan S0 from the mid-60s monthly range to 80.6% monthly on GPT 4.1-mini synthetic validation.

## Table 3 - ExECT GPT Schema Ladder

| Schema level | Field-family scope | Run ID | Program surface | Split / N | Scorer | Micro F1 | Key family caveats |
| --- | --- | --- | --- | ---: | --- | ---: | --- |
| S1 | diagnosis, seizure type, annotated medication | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` | single-pass v4.10 with benchmark policy / bridges | validation / 40 | `exect_field_family_deterministic_v1` | 92.3% | Diagnosis 93.8%, seizure type 90.5%, medication 92.8%. |
| S2 | S1 plus investigation, comorbidity | `exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` | frozen S2 v1.3 single-pass | validation / 40 | `exect_s2_field_family_deterministic_v1` | 80.9% | Investigation remains strong at 90.0%; comorbidity is weaker at 69.3%. |
| S3 | S2 plus birth history, onset, epilepsy cause, when diagnosed | `exect_s3_validation_full_gpt4_1_mini_20260519T235439Z` | frozen S3 v1.2 single-pass | validation / 40 | `exect_s3_field_family_deterministic_v1` | 72.1% | Sparse added families are weak; comorbidity remains an accepted gap. |
| S4 | S3 plus seizure frequency, medication temporality | `exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` | frozen S4 v1.2 single-pass | validation / 40 | `exect_s4_field_family_deterministic_v1` | 65.5% | Seizure frequency 45.7%; medication temporality 62.5%; investigation 96.7%. |

Primary sources: the listed run `metrics.json` files; `docs/experiments/synthesis/experiments_methods_results_20260520.md`; `docs/policies/deterministic_scorer_semantics.md`.

## Table 4 - Local Qwen Replication Against Frozen ExECT Surfaces

| Schema level | GPT anchor run / F1 | Qwen run / F1 | Delta | Decision / caveat |
| --- | ---: | ---: | ---: | --- |
| S1 | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` / 92.3% | `exect_s0_s1_validation_full_qwen35b_ollama_20260520T042117Z` / 79.0% | -13.3 pp | Qwen lags mainly through seizure-type granularity (55.7% F1 vs GPT 90.5%). |
| S2 | `exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` / 80.9% | `exect_s2_validation_full_qwen35b_ollama_20260520T073552Z` / 82.6% | +1.7 pp | Qwen slightly exceeds pooled micro, but family profile differs. |
| S3 | `exect_s3_validation_full_gpt4_1_mini_20260519T235439Z` / 72.1% | `exect_s3_validation_full_qwen35b_ollama_20260520T092244Z` / 72.2% | +0.1 pp | Near tie on pooled micro; local latency and family profile remain relevant. |
| S4 | `exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` / 65.5% | `exect_s4_validation_full_qwen35b_ollama_20260520T160914Z` / 67.5% | +2.0 pp | Pooled micro is higher, but per-family divergences prevent a simple model-ranking claim. |

Paper-safe interpretation: Qwen3.6:35b is viable on some frozen ExECT surfaces, especially broader pooled S2-S4 diagnostics, but it is not a universal replacement for GPT 4.1-mini because S1 seizure-type policy alignment remains much weaker.

## Table 5 - Targeted Negative, Gated, And Mechanism-Open Findings

| Finding | Run ID / artifact | Metric | Decision | Manuscript use |
| --- | --- | ---: | --- | --- |
| ExECT S1 section/family split regressed on cap-25. | `exect_s0_s1_section_aware_cap25_gpt4_1_mini_20260518T174714Z` | 65.6% micro F1 | Reject as tested | Use as a negative decomposition result, not proof that all decomposition fails. |
| ExECT S1 BootstrapFewShot did not beat frozen manual policy. | `exect_s1_optimizer_bootstrap_cap25_gpt4_1_mini_20260521T000608Z` | 90.7% micro F1 vs 95.8% cap-25 baseline | Reject as tested | Supports "optimizer arms did not replace policy engineering" with cap-25 caveat. |
| Gan Qwen ReAct temporal tools underperformed on hard slice. | `gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails_20260520T173943Z` | 42.9% monthly on 14-record slice; 50.0% schema valid | Reject as tested | Use only as slice-level evidence against this ReAct arm. |
| ExECT medication-temporality H1 post-classifier improved precision but hurt recall/F1. | `exect_s4_temporality_h1_post_classifier_full_gpt4_1_mini_20260520T204216Z` | MT precision 56.5%, recall 55.3%, F1 55.9% | Reject as tested | Use as a negative deterministic-postprocess arm. |
| ExECT medication-temporality G0G2 guard is the best current tested MT precision arm. | `exect_s4_mt_guard_g0g2_dose_current_full_gpt4_1_mini_20260524T133253Z` | MT precision 69.4%, recall 91.5%, F1 78.9% | Passes arm gates; mechanism open | Use as a targeted S4 family result, not full S4 solution. Frozen diagnosis, seizure-type, medication, and investigation F1 are unchanged from the S4 baseline. |

Primary source for the final row: `docs/experiments/exect/exect_s4_mt_guard_g0g2_dose_current_gpt_inspection_20260524.md` and `runs/exect_s4_mt_guard_g0g2_dose_current_full_gpt4_1_mini_20260524T133253Z/metrics.json`.

## Claim Readiness For Manuscript Tables

| Claim | Status | Required wording discipline |
| --- | --- | --- |
| Candidate-builder gap v1 is the current best internal Gan S0 operational surface. | Supported | Always say synthetic validation and cite split/scorer/run ID. |
| Qwen transfers Gan builder-gap v1, but GPT remains stronger on monthly accuracy. | Supported | Report 297 valid-scored denominator for Qwen and avoid parity language. |
| ExECT schema breadth increases difficulty across S1-S4. | Supported with caveat | Say field-family scope changes across rungs; report per-family caveats. |
| Qwen can match or exceed GPT pooled micro on broader ExECT surfaces. | Supported with caveat | Do not turn this into a universal model leaderboard; mention S1 seizure-type weakness. |
| DSPy optimizers and tool-use arms did not beat current hand-designed surfaces. | Supported only as tested | Use arm-level language; do not close the entire optimizer or tool-use mechanism class. |
| The project beats published Gan or ExECT benchmarks. | Unsupported / blocked | Do not claim until Real Gan access and CUI-aware ExECT reproduction gates reopen. |

## Verification Notes

Checked primary metrics for all rows with present local run directories:

- Gan builder-gap GPT/Qwen, temporal-candidates GPT/Qwen, verify-repair GPT.
- ExECT GPT S1-S4 ladder and Qwen S1-S4 replication.
- ExECT S1 section-aware cap-25 and optimizer cap-25.
- Gan Qwen ReAct hard slice.
- ExECT S4 H1 post-classifier and G0G2 medication-temporality guard.

The only table row not re-read from a present local `metrics.json` was `gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z`; the registry explicitly notes that the original run directory may be absent locally, so this row should stay a superseded historical anchor unless the manuscript needs a fully reverified number.
