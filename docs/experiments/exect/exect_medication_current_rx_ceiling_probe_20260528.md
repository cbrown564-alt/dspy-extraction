# ExECT Medication Current-Rx Isolated Ceiling Probe

Date: 2026-05-28
Status: current synthesis; isolated component ceiling probe
Kanban card: E6 - Medication Isolated Current-Rx Ceiling Probe
Dataset/split: ExECTv2 `validation` (40 documents)
Model/provider: none for isolated payload; GPT 4.1-mini / OpenAI for S1/S5 comparison surfaces
Scorer mode: `medication-only slice of exect_field_family_deterministic_v1`

## Summary

The E3 annotation-derived current-Rx payload reaches an isolated medication ceiling of **100.0% F1** (47/47 labels).

Existing model surfaces remain below that ceiling: S1 GPT is **92.8% F1** and S5 GPT is **88.7% F1** on the same validation medication target.

## Medication Metrics

| Surface | Precision | Recall | F1 | TP | FP | FN | Support |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Isolated E3 annotation current-Rx payload | 100.0% | 100.0% | 100.0% | 47 | 0 | 0 | 47 |
| Existing S1 GPT medication surface | 90.0% | 95.7% | 92.8% | 45 | 5 | 2 | 47 |
| Existing S5 GPT medication surface | 79.7% | 100.0% | 88.7% | 47 | 12 | 0 | 47 |

## Residual Categories

| Surface | Residual docs | Categories |
| --- | ---: | --- |
| Existing S1 GPT medication surface | 4 | `fn:annotation_current_rx_missed_by_surface` 2; `fp:dose_line_or_unknown_temporality_evidence` 2; `fp:missing_gold_or_no_current_rx_gold` 3 |
| Existing S5 GPT medication surface | 10 | `fp:dose_line_or_unknown_temporality_evidence` 1; `fp:missing_gold_or_no_current_rx_gold` 5; `fp:over_emission_extra_current_rx_surface` 6 |

## Lifecycle Diagnostics

| Case type | Count |
| --- | ---: |
| `dose_line_rows` | 131 |
| `dose_only_rows` | 60 |
| `non_asm_rows` | 4 |
| `planned_rows` | 11 |
| `prescription_list_rows` | 78 |
| `previous_rows` | 9 |
| `taper_or_stop_rows` | 8 |
| `unknown_temporality_rows` | 116 |

## Interpretation

- Annotated current-Rx is now an isolated no-model ceiling for the benchmark-facing medication component.
- S1 loss is small and mixed: two current-Rx misses plus brand/surface mismatch and missing-gold false positives.
- S5 reaches full recall but loses precision through extra medication emissions, which routes naturally to E7 stack-interference attribution.
- Lifecycle rows remain diagnostic only; planned, previous, taper, dose-only, and unknown-temporality rows do not enter medication F1.

## Reproducibility

- E3 payload: `docs/experiments/exect/exect_medication_current_rx_lifecycle_payload_audit_20260528.json`
- S1 comparison run: `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z`
- S5 comparison run: `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z`
- No model calls, scorer changes, loader changes, split changes, benchmark bridge changes, or prompt changes were made.
