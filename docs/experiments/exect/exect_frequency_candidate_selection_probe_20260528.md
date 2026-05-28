# ExECT Frequency Candidate Selection Split

Date: 2026-05-28
Status: current synthesis; preregistered component probe
Kanban card: E10 - ExECT Frequency Candidate Selection Split
Dataset/split: ExECTv2 `validation` (40 documents)
Model/provider: none for payload/oracle surfaces; GPT 4.1-mini / OpenAI for S4/S5 comparison surfaces
Scorer mode: `seizure-frequency slice of exect_s4_field_family_deterministic_v1`

## Summary

The broad event/rate payload is recall-sufficient but not prediction-ready: it scores **100.0% recall** and **22.2% precision** when promoted directly as frequency predictions.

A gold-constrained oracle over the same broad candidate set reaches **100.0% F1**, so the remaining component work is candidate adjudication/target selection rather than payload coverage.

## Surface Comparison

| Surface | Classification | Precision | Recall | F1 | TP | FP | FN |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Broad event/rate payload | diagnostic coverage substrate | 22.2% | 100.0% | 36.3% | 43 | 151 | 0 |
| High-precision payload | diagnostic narrowed substrate | 19.5% | 58.1% | 29.2% | 25 | 103 | 18 |
| Candidate-constrained gold oracle | oracle upper bound / not deployable | 100.0% | 100.0% | 100.0% | 43 | 0 | 0 |
| Existing S4 GPT frequency surface | existing S4 diagnostic surface | 42.9% | 48.8% | 45.7% | 21 | 28 | 22 |
| Existing S5 GPT frequency surface | existing stacked operational surface | 69.4% | 79.1% | 73.9% | 34 | 15 | 9 |

## Extra-Candidate Strata

| Surface | Strata |
| --- | --- |
| Broad event/rate payload | `note_regex_quantified` 114; `qualitative_change_cue` 35; `seizure_free_surface` 2 |
| High-precision payload | `note_regex_quantified` 103 |

## Error Attribution

| Surface | Error docs | Categories |
| --- | ---: | --- |
| High-precision payload | 37 | `fn:adjudication_missed_broad_candidate:qualitative_change` 12; `fn:adjudication_missed_broad_candidate:seizure_free` 6; `fp:target_selection_extra_candidate:note_regex_quantified` 103 |
| Existing S4 GPT frequency surface | 29 | `fn:adjudication_missed_broad_candidate:qualitative_change` 7; `fn:adjudication_missed_broad_candidate:seizure_free` 4; `fn:adjudication_missed_high_precision_candidate` 11; `fp:label_construction_not_in_broad_payload` 20; `fp:target_selection_extra_candidate:note_regex_quantified` 6; `fp:target_selection_extra_candidate:qualitative_change_cue` 2 |
| Existing S5 GPT frequency surface | 19 | `fn:adjudication_missed_broad_candidate:qualitative_change` 4; `fn:adjudication_missed_broad_candidate:seizure_free` 3; `fn:adjudication_missed_high_precision_candidate` 2; `fp:label_construction_not_in_broad_payload` 1; `fp:target_selection_extra_candidate:note_regex_quantified` 8; `fp:target_selection_extra_candidate:qualitative_change_cue` 5; `fp:target_selection_extra_candidate:seizure_free_surface` 1 |

## Interpretation

- Broad payload coverage is not a frequency ceiling because direct promotion creates many extra labels.
- The high-precision payload is not safe as a replacement because it drops qualitative-change and seizure-free/zero-rate coverage.
- S4/S5 model surfaces sit between direct-payload promotion and the oracle, which localizes remaining error to adjudication plus a smaller amount of label construction outside the broad payload.
- The next E10 step should be an adjudicator/ranker comparison against this fixed broad payload, not another broad-stack prompt loop.

## Reproducibility

- E1 payload: `docs/experiments/exect/exect_frequency_event_rate_payload_audit_20260528.json`
- S4 comparison run: `exect_s4_validation_full_gpt4_1_mini_20260520T071248Z`
- S5 comparison run: `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z`
- No model calls, scorer changes, loader changes, split changes, benchmark bridge changes, or prompt changes were made.
