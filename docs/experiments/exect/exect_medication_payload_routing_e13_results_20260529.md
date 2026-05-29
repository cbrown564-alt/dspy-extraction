# ExECT Medication Payload Routing E13 Results

Date: 2026-05-29
Status: rejected arm; validation-only; mechanism open
Kanban card: E13 - Medication Payload Routing / Prompt Isolation

## Decision

The tested AM+MT lifecycle-context arm is **rejected as tested**. It did not
reduce medication false positives versus the matched AM-only comparator and it
dropped annotated-medication recall by six labels.

This rejects the specific prompt-context routing arm, not medication lifecycle
decomposition as a mechanism class.

## Taxonomy

Dataset: ExECTv2
Split: `exectv2_fixed_v1:validation`
Clinical task family: annotated medication
Schema complexity: medication-only component surface under S1 artifact schema
Comparison group: `exect_medication_payload_routing_e13_validation_v1`
Model/provider: GPT 4.1-mini / OpenAI
Scorer: medication-family slice of `exect_field_family_deterministic_v1`
Scored endpoint: annotated medication only
Lifecycle/temporality: diagnostic context only
Decision scope: arm

## Runs

| Arm | Config | Run ID | Scope |
| --- | --- | --- | --- |
| AM-only smoke | `configs/experiments/exect_s1_e13_am_only_cap5_gpt4_1_mini.json` | `exect_s1_e13_am_only_cap5_gpt4_1_mini_20260529T101912Z` | cap-5 validation smoke |
| AM+MT smoke | `configs/experiments/exect_s1_e13_am_mt_lifecycle_cap5_gpt4_1_mini.json` | `exect_s1_e13_am_mt_lifecycle_cap5_gpt4_1_mini_20260529T101920Z` | cap-5 validation smoke |
| AM-only full | `configs/experiments/exect_s1_e13_am_only_full_gpt4_1_mini.json` | `exect_s1_e13_am_only_full_gpt4_1_mini_20260529T102009Z` | 40-document validation |
| AM+MT full | `configs/experiments/exect_s1_e13_am_mt_lifecycle_full_gpt4_1_mini.json` | `exect_s1_e13_am_mt_lifecycle_full_gpt4_1_mini_20260529T102054Z` | 40-document validation |

## Metrics

| Surface | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E6 no-model current-Rx ceiling | 47 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| Prior S1 GPT medication surface | 45 | 5 | 2 | 90.0% | 95.7% | 92.8% |
| Prior S5 GPT medication surface | 47 | 12 | 0 | 79.7% | 100.0% | 88.7% |
| E13 AM-only GPT | 42 | 4 | 5 | 91.3% | 89.4% | 90.3% |
| E13 AM+MT lifecycle-context GPT | 36 | 4 | 11 | 90.0% | 76.6% | 82.8% |

Both E13 full runs had exact evidence support for emitted values. The partial
S1 micro metrics in `metrics.json` are not the decision metric because diagnosis
and seizure type were intentionally out of scope.

## E7 Ledger

| E7 row | Category | AM-only | AM+MT |
| --- | --- | --- | --- |
| `EA0016` levetiracetam | planned/future | absent | absent |
| `EA0052` levetiracetam | historical/switched | absent | absent |
| `EA0052` lamotrigine | historical/switched | absent | absent |
| `EA0053` levetiracetam | planned/future | absent | absent |
| `EA0059` gabapentin | other-medication/non-current | absent | absent |
| `EA0078` levetiracetam | historical/switched | absent | absent |
| `EA0078` carbamazepine | missing-gold/annotation-policy | predicted FP | predicted FP |
| `EA0098` levetiracetam | historical/switched | absent | absent |
| `EA0131` carbamazepine | historical/switched | absent | absent |
| `EA0136` carbamazepine | missing-gold/annotation-policy | predicted FP | predicted FP |
| `EA0143` lamotrigine | historical/switched | absent | absent |
| `EA0188` lamotrigine | planned/future | absent | absent |

The lifecycle-context arm did not improve the E7 false-positive ledger relative
to AM-only. The remaining two E7 rows are annotation-policy/missing-gold cases,
so hiding them as precision gains would violate the preregistered caveat.

The two S1 false negatives recovered by S5 (`EA0052` carbamazepine and `EA0136`
epilim chrono / epilim) were not cleanly recovered by either E13 arm.

## Error Read

AM-only is a useful matched comparator but not a promotion candidate: it improves
precision over the S5 stack while losing five current-Rx labels and underperforming
the prior S1 medication surface.

AM+MT lifecycle context reduced recall without reducing false positives. The
likely failure mode is prompt/input burden from diagnostic lifecycle rows rather
than a useful routing signal. This is arm-level evidence against this context
injection position.

## Caveats

- No scorer, loader, split, benchmark bridge, prediction-repair, or holdout
  semantics changed.
- Lifecycle and temporality remain diagnostic only.
- Holdout rows from E11 were not used for prompt or scorer tuning.
- This result does not close prompt isolation or deterministic routing as a
  mechanism class; it rejects only the tested AM+MT lifecycle-context arm.
