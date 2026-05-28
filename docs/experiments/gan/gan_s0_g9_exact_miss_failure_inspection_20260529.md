# Gan S0 G9 Exact-Miss Failure Inspection

Status: current synthesis / no-model routing decision  
Date: 2026-05-29  
Related card: G9 - Gan G8 Exact-Miss And Special-Class Failure Inspection  
Routes next: G11 before G10

## Question

Do the G8 standard-50 paper-monthly misses show that the next Gan S0 pull
should be another selector run, or do the exact-miss records require a
candidate-inventory challenge-set pass first?

## Method

- Dataset/split: Gan 2026 synthetic, `gan_2026_fixed_v1:validation`.
- Gold source:
  `check__Seizure Frequency Number.seizure_frequency_number[0]`.
- Reference policy: `reference[0]` is a secondary difficulty signal, not gold.
- Run inspected:
  `runs/gan_s0_g8_special_class_target_selector_gpt4_1_mini_standard50_20260528T233005Z`.
- Artifact inputs:
  `errors.json`, `predictions.json`,
  `docs/experiments/gan/gan_s0_candidate_inventory_coverage_report_20260528.json`,
  and
  `docs/experiments/gan/gan_s0_g6_evaluation_slice_standard_decision_20260528.md`.
- Scorer view for miss set: `gan2026_paper_reproduction` monthly mismatch.

No model calls, scorer changes, loader changes, split changes, benchmark bridge
changes, candidate-builder changes, or prediction-repair changes were made.

## Summary

G8 had 13 paper-monthly misses on `gan_s0_g6_standard50_v1`.

| Failure class | Records | Interpretation |
| --- | ---: | --- |
| Candidate-coverage exact miss | 4 | Gold exact label is absent from the candidate list. |
| Seizure-free over quantified target selection | 3 | Gold quantified label is available, but G8 selects seizure freedom. |
| Unknown policy target selection | 3 | Gold unknown or unknown-cluster label is available, but G8 selects quantified or seizure-free. |
| Quantified target selection / temporal anchoring | 3 | Gold or a compatible family is available, but G8 selects the wrong quantified target. |

The four standard-50 exact-miss records are true candidate-inventory failures
for exact label reproduction: `gan_15997`, `gan_16772`, `gan_16825`, and
`gan_16335`. This does not mean candidate inventory is the only open bottleneck;
the remaining 9 misses still implicate target selection and policy. It does
mean G10 should not be run yet as a candidate-constrained or answer-options
selector over the current inventory, because four G6 standard-50 records would
not contain the gold exact answer as an option.

## Record-Level Inspection

| Record | Gold | Candidate labels | Gold exact in candidates | Selected label | Target semantic class | Reason code | Challenge tags | G9 reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_11380` | `unknown` | `no seizure frequency reference`; `unknown`; `2 per 2 month`; `2 per 12 month`; `2 per 3 month` | yes | `2 per 2 month` | `frequency_present_quantified` | `select_current_quantified_rate` | `target_selection`; `unknown_no_reference`; `cluster` | unknown policy target selection |
| `gan_12679` | `1 per day` | `1 per day`; `no seizure frequency reference`; `unknown`; `seizure free for 6 month`; `seizure free for multiple month`; `seizure free for multiple month`; `1 to 2 per month`; `1 per 3 to 4 week`; `1 per day`; `1 to 2 per 6 month` | yes | `1 to 2 per month` | `frequency_present_quantified` | `select_current_quantified_rate` | `target_selection`; `seizure_free_vs_quantified`; `cluster`; `temporal_anchoring` | quantified target selection / temporal anchoring |
| `gan_14485` | `2 per 3 month` | `2 per 3 month`; `no seizure frequency reference`; `unknown`; `seizure free for multiple month`; `seizure free for multiple month`; `seizure free for 1 month` | yes | `seizure free for 1 month` | `seizure_free_duration` | `select_seizure_free_duration` | `target_selection`; `seizure_free_vs_quantified`; `temporal_anchoring` | seizure-free over quantified target selection |
| `gan_14881` | `1 per month` | `1 per month`; `no seizure frequency reference`; `unknown`; `seizure free for multiple month`; `seizure free for multiple month`; `3 per month` | yes | `seizure free for multiple month` | `seizure_free_duration` | `select_seizure_free_duration` | `target_selection`; `seizure_free_vs_quantified` | seizure-free over quantified target selection |
| `gan_15306` | `2 to 3 per 15 month` | `2 to 3 per 15 month`; `no seizure frequency reference`; `unknown`; `seizure free for multiple month`; `1 per 15 month` | yes | `seizure free for multiple month` | `seizure_free_duration` | `select_seizure_free_duration` | `target_selection`; `seizure_free_vs_quantified` | seizure-free over quantified target selection |
| `gan_15997` | `10 per 3 month` | `no seizure frequency reference`; `unknown`; `seizure free for multiple month`; `3 per week`; `4 per month`; `3 per month`; `unknown, multiple per cluster` | no | `unknown` | `seizures_referenced_frequency_unclear` | `select_unknown_context` | `target_selection`; `seizure_free_vs_quantified`; `candidate_coverage`; `cluster` | candidate-coverage exact miss |
| `gan_16041` | `9 per 3 month` | `no seizure frequency reference`; `unknown`; `seizure free for multiple month`; `seizure free for multiple month`; `9 per 2 month`; `9 per 3 month`; `3 per 2 month`; `3 per 3 month` | yes | `9 per 2 month` | `frequency_present_quantified` | `select_current_quantified_rate` | `target_selection` | quantified target selection / temporal anchoring |
| `gan_16335` | `7 per 3 month` | `no seizure frequency reference`; `unknown`; `1 per month`; `4 per 3 month` | no | `4 per 3 month` | `frequency_present_quantified` | `select_current_quantified_rate` | `target_selection`; `candidate_coverage` | candidate-coverage exact miss |
| `gan_16772` | `9 per 5 month` | `no seizure frequency reference`; `unknown`; `seizure free for multiple month`; `8 per 2 month`; `11 per 3 month`; `11 per 10 month`; `11 per month`; `unknown, 1 per cluster` | no | `11 per 3 month` | `frequency_present_quantified` | `select_current_quantified_rate` | `target_selection`; `candidate_coverage`; `temporal_anchoring` | candidate-coverage exact miss |
| `gan_16825` | `10 per 6 month` | `no seizure frequency reference`; `unknown`; `12 per 2 month`; `12 per 3 month`; `8 per 3 month`; `8 per 10 month`; `8 per month`; `unknown, 3 per cluster` | no | `12 per 2 month` | `frequency_present_quantified` | `select_current_quantified_rate` | `target_selection`; `seizure_free_vs_quantified`; `candidate_coverage`; `cluster`; `temporal_anchoring` | candidate-coverage exact miss |
| `gan_5974` | `unknown` | `no seizure frequency reference`; `unknown`; `seizure free for 1 year`; `seizure free for 12 month`; `seizure free for multiple month`; `seizure free for multiple month` | yes | `seizure free for 1 year` | `seizure_free_duration` | `select_seizure_free_duration` | `target_selection`; `seizure_free_vs_quantified`; `unknown_no_reference` | unknown policy target selection |
| `gan_6532` | `unknown, multiple per cluster` | `no seizure frequency reference`; `unknown`; `5 per day`; `unknown, multiple per cluster` | yes | `5 per day` | `frequency_present_quantified` | `select_current_quantified_rate` | `target_selection`; `unknown_no_reference`; `cluster`; `vague_frequency` | quantified target selection / temporal anchoring |
| `gan_9566` | `unknown` | `no seizure frequency reference`; `unknown`; `1 per month`; `1 to 2 per 8 week` | yes | `1 to 2 per 8 week` | `frequency_present_quantified` | `select_current_quantified_rate` | `target_selection`; `seizure_free_vs_quantified`; `unknown_no_reference` | unknown policy target selection |

## Exact-Miss Notes

### `gan_15997`

Gold is `10 per 3 month`; exact candidate is absent. The candidates include
`3 per week`, `4 per month`, `3 per month`, and an unknown-cluster fallback.
The miss is not merely G8 selecting badly: the current candidate inventory does
not expose the exact gold aggregate.

### `gan_16772`

Gold is `9 per 5 month`; exact candidate is absent. The candidates include
`8 per 2 month`, `11 per 3 month`, `11 per 10 month`, and `11 per month`. This
is a temporal-window and aggregation coverage problem on a gold-evidence
multispan record.

### `gan_16825`

Gold is `10 per 6 month`; exact candidate is absent. The candidates include
`12 per 2 month`, `12 per 3 month`, `8 per 3 month`, `8 per 10 month`, and
`8 per month`. This combines aggregation, temporal-window, cluster, and
seizure-free-conflict pressure.

### `gan_16335`

Gold is `7 per 3 month`; exact candidate is absent. The candidates include
`1 per month` and `4 per 3 month`. The note text summarized by the candidate
builder has month-specific counts that sum to seven, but the exposed inventory
does not construct the summed gold label.

## Decision

Route to G11 before G10.

The current inventory is adequate for many selector failures, but not adequate
for a candidate-constrained or answer-options selector claim on the G6
standard-50 surface. A G10 selector over the unchanged options would force four
standard-50 exact-miss records into impossible exact-label choices. G11 should
therefore run a no-model candidate-inventory challenge-set pass over the
candidate-coverage exact-miss surface, with special attention to the four
standard-50 records above.

G11 should not mutate candidate-builder behavior by default. Its first output
should be a candidate-coverage report that separates exact, Purist-equivalent,
and Pragmatic-equivalent coverage; identifies whether the missing labels are
aggregation/window-construction failures; and decides whether a scoped
candidate-builder implementation card is needed before G10.

## Caveats

- The G6 standard-50 surface is challenge-balanced and not an unbiased
  validation estimate.
- This is synthetic-validation evidence only, not Real(300), Real(150), or an
  external Gan benchmark claim.
- Canonical Gan metrics remain diagnostic; G9 used paper-reproduction monthly
  mismatches to match the G8 decision surface.
- Scorer semantics and dataset policy are unchanged.
