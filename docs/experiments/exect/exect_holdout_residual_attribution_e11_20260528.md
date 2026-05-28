# ExECT Holdout Residual Attribution

Date: 2026-05-28
Status: current synthesis; diagnostic holdout residual analysis
Kanban card: E11 - ExECT Holdout Residual Attribution
Dataset/splits: ExECTv2 `validation` and frozen `test` holdout
Model/provider: GPT 4.1-mini / OpenAI and Qwen3.6:35b / Ollama stored artifacts
Model calls: 0
Scorer mode: existing ExECT field-family scorers only

## Summary

E11 attributes the ExECT holdout drop without tuning on holdout. S1 transfer loss is concentrated in diagnosis and seizure-type policy/bridge/extraction residuals, while annotated medication stays stable. S5 frequency loss is a mixed payload-generalization and adjudication problem: the broad frequency payload covers 43/43 validation labels but only 31/44 holdout labels.

The medication substrate does transfer: the annotation-derived current-Rx payload still reaches 53/53 holdout labels. S5 medication loss on holdout is therefore stack behavior, not a current-Rx representability failure.

## Transfer Deltas

| Surface | Micro F1 val | Micro F1 test | Delta | Main field deltas |
| --- | ---: | ---: | ---: | --- |
| S1 GPT | 92.3% | 77.8% | -14.5 pp | `annotated_medication` -0.1 pp; `diagnosis` -22.4 pp; `seizure_type` -24.6 pp |
| S1 Qwen | 85.9% | 71.8% | -14.1 pp | `annotated_medication` +3.2 pp; `diagnosis` -28.5 pp; `seizure_type` -22.1 pp |
| S5 GPT | 85.8% | 69.4% | -16.4 pp | `annotated_medication` -5.9 pp; `diagnosis` -18.6 pp; `investigation` -6.3 pp; `seizure_frequency` -26.9 pp; `seizure_type` -27.7 pp |
| S5 Qwen | 85.4% | 73.3% | -12.2 pp | `annotated_medication` -7.7 pp; `diagnosis` -17.8 pp; `investigation` +2.3 pp; `seizure_frequency` -12.8 pp; `seizure_type` -25.6 pp |

## S1 Attribution

| Surface | Residual classes | Bridge-flagged values |
| --- | --- | --- |
| S1 GPT validation | `extraction` 1; `bridge` 5; `policy` 2; `specificity_collapse` 1; `scope` 2 | `diagnosis` 22; `seizure_type` 28 |
| S1 GPT test holdout | `extraction` 10; `bridge` 10; `policy` 8; `specificity_collapse` 6; `scope` 4 | `diagnosis` 15; `seizure_type` 19 |
| S1 Qwen validation | `extraction` 3; `bridge` 6; `policy` 7; `specificity_collapse` 1; `scope` 1 | `diagnosis` 21; `seizure_type` 20 |
| S1 Qwen test holdout | `extraction` 9; `bridge` 10; `policy` 6; `specificity_collapse` 7; `scope` 6 | `diagnosis` 17; `seizure_type` 17 |

The E2 split remains the causal context: full-validation S1 bridge contribution was `diagnosis` +32.3 pp; `seizure_type` +33.1 pp, so raw S1 extraction is not itself at ceiling. On holdout, GPT S1 residual rows expand from 11 validation diagnosis/seizure mismatches to 38 holdout mismatches, with extraction and bridge classes both reaching 10 rows.

## Frequency Attribution

| Split | Broad payload recall | Oracle F1 | S5 GPT F1 | S5 error docs | S5 categories |
| --- | ---: | ---: | ---: | ---: | --- |
| validation | 100.0% | 100.0% | 73.9% | 19 | `fn:adjudication_missed_broad_candidate:qualitative_change` 4; `fn:adjudication_missed_broad_candidate:seizure_free` 3; `fn:adjudication_missed_high_precision_candidate` 2; `fp:label_construction_not_in_broad_payload` 1; `fp:target_selection_extra_candidate:note_regex_quantified` 8; `fp:target_selection_extra_candidate:qualitative_change_cue` 5; `fp:target_selection_extra_candidate:seizure_free_surface` 1 |
| test | 70.5% | 82.7% | 47.1% | 24 | `fn:adjudication_missed_broad_candidate:qualitative_change` 3; `fn:adjudication_missed_broad_candidate:seizure_free` 3; `fn:adjudication_missed_high_precision_candidate` 7; `fn:payload_coverage_gap:qualitative_change` 5; `fn:payload_coverage_gap:quantified_rate` 1; `fn:payload_coverage_gap:seizure_free` 4; `fn:payload_coverage_gap:zero_rate` 1; `fp:label_construction_not_in_broad_payload` 5; `fp:target_selection_extra_candidate:gan_temporal_filtered` 1; `fp:target_selection_extra_candidate:note_regex_quantified` 11; `fp:target_selection_extra_candidate:qualitative_change_cue` 2; `fp:target_selection_extra_candidate:seizure_free_surface` 2 |

The holdout frequency surface is not just a model-selection failure. Broad-payload recall drops -29.5 pp, and the gold-constrained oracle over that payload drops -17.3 pp. The remaining GPT S5 gap to the holdout oracle is -35.6 pp, which keeps candidate adjudication open after payload repair is studied on validation.

## Medication And Stack

| Surface | Precision | Recall | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| isolated_current_rx_payload | 100.0% | 100.0% | 100.0% | 53 | 0 | 0 |
| s1_gpt_surface | 89.5% | 96.2% | 92.7% | 51 | 6 | 2 |
| s5_gpt_surface | 76.2% | 90.6% | 82.8% | 48 | 15 | 5 |

Shared-family stack deltas on GPT holdout are diagnosis +0.0 pp, seizure type -9.6 pp, and annotated medication -10.0 pp. That routes the next medication mechanism toward payload routing or prompt isolation, not a broad temporality scorer change.

## Decision

- Diagnosis and seizure-type transfer dominate the S1 drop; medication remains stable. Residuals expand in extraction, bridge, policy, specificity, and scope classes, so S1 remains validation-aligned rather than an isolated ceiling.
- S5 frequency loss is split between holdout payload representability and candidate adjudication/label construction. The broad validation payload covers 43/43 validation labels but only 31/44 holdout labels.
- Medication current-Rx is representable on holdout by the annotation-derived payload, but S5 loses precision and recall relative to S1 under the stacked prompt.
- Use validation-only component probes for S1 diagnosis/seizure transfer, frequency payload generalization, and medication payload routing/prompt isolation before rebuilding broad stacks.

## Reproducibility

- S1 GPT validation: `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z`
- S1 GPT holdout: `exect_s0_s1_validation_test_gpt4_1_mini_20260526T184057Z`
- S5 GPT validation: `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z`
- S5 GPT holdout: `test_holdout_exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260527T055059Z`
- S1 split source: `docs/experiments/exect/exect_s1_raw_bridge_prompt_split_audit_20260528.json`
- No model calls, scorer changes, loader changes, split changes, benchmark bridge changes, prompt changes, prediction repair, or artifact mutation were made.

## Caveats

- Holdout is used for residual attribution only, not prompt, scorer, loader, split, bridge, or repair tuning.
- Current ExECT project scorers are field-family diagnostic/project scorers, not CUI-aware Table 1 reproduction.
- Frequency labels use ExECT SeizureFrequency annotation surfaces, not Gan monthly-frequency normalization.
- Medication lifecycle categories remain diagnostic; annotated current-Rx is the benchmark-facing medication surface.
- Stack-interference attribution is inferred from stored S1-vs-S5 behavior, not from a randomized prompt-isolation run.
