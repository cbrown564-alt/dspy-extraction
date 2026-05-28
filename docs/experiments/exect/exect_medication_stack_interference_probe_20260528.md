# ExECT Medication Stack-Interference Probe

Date: 2026-05-28
Status: current synthesis; diagnostic stack-interference attribution
Kanban card: E7 - Medication Stack-Interference Probe
Dataset/split: ExECTv2 `validation` (40 documents)
Model/provider: GPT 4.1-mini / OpenAI for S1/S5 comparison surfaces
Scorer mode: `medication-only slice of exect_field_family_deterministic_v1`

## Summary

S5 medication loss is a precision/interference problem, not a current-Rx coverage problem. S1 scores **92.8% F1** (45 TP / 5 FP / 2 FN), while S5 scores **88.7% F1** (47 TP / 12 FP / 0 FN).

S5 adds **8** false positives that S1 avoided, while recovering the two S1 false negatives. The current AM guard fixed the earlier non-ASM/brand failure mode enough to reach full recall, but it does not isolate current-Rx medication from plan, history, other-medication, or annotation-policy contexts.

## S1 Versus S5 Delta

| Surface | Precision | Recall | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S1 GPT medication surface | 90.0% | 95.7% | 92.8% | 45 | 5 | 2 |
| S5 GPT medication surface | 79.7% | 100.0% | 88.7% | 47 | 12 | 0 |

| Delta item | Count |
| --- | ---: |
| S5-only false positives | 8 |
| Shared S1/S5 false positives | 4 |
| S5 recovered S1 false negatives | 2 |

## Attribution Categories

| Category | Count |
| --- | ---: |
| `historical_failed_or_switched_evidence` | 6 |
| `missing_gold_or_annotation_policy` | 2 |
| `other_medication_or_non_current_section` | 1 |
| `planned_or_future_evidence` | 3 |

## Row-Level Interference

| Document | Medication | Delta | Category | Evidence cue |
| --- | --- | --- | --- | --- |
| `EA0016` | `levetiracetam` | `s5_only_fp` | `planned_or_future_evidence` | I would suggest maybe Levetiracetam 250 mg once-a-day, increasing by 250 mg every two weeks to 250 milligra... |
| `EA0052` | `levetiracetam` | `s5_only_fp` | `historical_failed_or_switched_evidence` | levetiracetam gave her mood disorder |
| `EA0052` | `lamotrigine` | `s5_only_fp` | `historical_failed_or_switched_evidence` | lamotrigine wasn’t effective |
| `EA0053` | `levetiracetam` | `s5_only_fp` | `planned_or_future_evidence` | I would therefore suggest starting levetiracetam 250mg od increasing by 250mg every fortnight until she is ... |
| `EA0059` | `gabapentin` | `s5_only_fp` | `other_medication_or_non_current_section` | gabapentin |
| `EA0078` | `levetiracetam` | `shared_s1_s5_fp` | `historical_failed_or_switched_evidence` | I think that the levetiracetam she is taking could well be contributing to this |
| `EA0078` | `carbamazepine` | `shared_s1_s5_fp` | `missing_gold_or_annotation_policy` | Increase the carbamazepine to 600mg twice a day |
| `EA0098` | `levetiracetam` | `s5_only_fp` | `historical_failed_or_switched_evidence` | He has changed from levetiracetam to lamotrigine |
| `EA0131` | `carbamazepine` | `s5_only_fp` | `historical_failed_or_switched_evidence` | Her epilepsy was not well controlled on carbamazepine monotherapy. |
| `EA0136` | `carbamazepine` | `shared_s1_s5_fp` | `missing_gold_or_annotation_policy` | He is currently taking Carbamazepine and Eplim Chrono 1000mg bd |
| `EA0143` | `lamotrigine` | `shared_s1_s5_fp` | `historical_failed_or_switched_evidence` | Initially she was treated with lamotrigine. |
| `EA0188` | `lamotrigine` | `s5_only_fp` | `planned_or_future_evidence` | In the future we can consider an increase in the lamotrigine |

## Interpretation

- Over-emission is the right headline: S5 has 12 medication false positives and no false negatives.
- The S5-only errors are consistent with broad-stack context pulling plan/history/other-medication evidence into the narrow annotated-medication slot.
- A broader temporality guard is not the immediate next step; first test payload routing or prompt isolation so medication sees a current-Rx substrate before family stacking.
- Lifecycle categories remain diagnostic only under E5; no medication scorer semantics changed.

## Reproducibility

- E3 payload: `docs/experiments/exect/exect_medication_current_rx_lifecycle_payload_audit_20260528.json`
- E6 ceiling probe: `docs/experiments/exect/exect_medication_current_rx_ceiling_probe_20260528.json`
- S1 comparison run: `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z`
- S5 comparison run: `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z`
- No model calls, scorer changes, loader changes, split changes, benchmark bridge changes, prompt changes, or artifact mutations were made.
