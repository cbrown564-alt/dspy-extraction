# Gan S0 G12 Aggregation-Aware Answer-Option Surface

Date: 2026-05-29
Status: current synthesis / no-model answer-option decision
Kanban card: G12 - Gan Aggregation-Aware Answer-Option Surface
Dataset/split: Gan 2026 synthetic (`gan_2026_fixed_v1:validation`)
Challenge set: `gan_s0_g6_candidate_coverage_exact_miss`
Model calls: none
Scorer, loader, split, bridge, prompt, model, and prediction-repair semantics: unchanged.

## Summary

Raw option view: **0/21** exact, **14/21** Purist-equivalent, and **17/21** Pragmatic-equivalent.
Constructed aggregate option view: **0/21** exact, **11/21** Purist-equivalent, and **13/21** Pragmatic-equivalent.
G9 standard50 subset, raw view: **0/4** exact, **4/4** Purist-equivalent, and **4/4** Pragmatic-equivalent.
G9 standard50 subset, constructed aggregate view: **0/4** exact, **4/4** Purist-equivalent, and **4/4** Pragmatic-equivalent.
Candidate diff versus stored G1/G11: **20** of 21 rows differ from stored G1, all due to candidate-label changes from current abstention pruning.

## Option Surface Decision

- Decision: **category_level_selector_only_before_new_aggregation_constructor**.
- Exact-label claim: **not authorized: current constructed aggregate view exact-covers 0/21 rows**.
- Category-level claim: **authorized as a narrowed G10 mechanism claim: raw options cover 14/21 Purist and 17/21 Pragmatic equivalent rows**.
- Required follow-up before an exact closed-option G10: G14 temporal anchoring plus G16 rate/duration aggregation policy, or a separate deterministic aggregation constructor with fixture tests

## Coverage By Family

### Raw Option View

| Family | Records | Options | Exact | Purist equiv. | Pragmatic equiv. |
| --- | ---: | ---: | ---: | ---: | ---: |
| `quantified_rate` | 18 | 18 (100.0%) | 0 (0.0%) | 11 (61.1%) | 14 (77.8%) |
| `seizure_free` | 2 | 2 (100.0%) | 0 (0.0%) | 2 (100.0%) | 2 (100.0%) |
| `unknown_cluster` | 1 | 1 (100.0%) | 0 (0.0%) | 1 (100.0%) | 1 (100.0%) |

### Constructed Aggregate Option View

| Family | Records | Options | Exact | Purist equiv. | Pragmatic equiv. |
| --- | ---: | ---: | ---: | ---: | ---: |
| `quantified_rate` | 18 | 14 (77.8%) | 0 (0.0%) | 11 (61.1%) | 13 (72.2%) |
| `seizure_free` | 2 | 1 (50.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `unknown_cluster` | 1 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |

## Row-Level Surface

| Record | Gold | Raw exact/Purist/Pragmatic | Constructed exact/Purist/Pragmatic | Constructed aggregate options |
| --- | --- | --- | --- | --- |
| `gan_15997` | `10 per 3 month` | no/yes/yes | no/yes/yes | `4 per month`<br>`3 per month` |
| `gan_16772` | `9 per 5 month` | no/yes/yes | no/yes/yes | `8 per 2 month`<br>`11 per 3 month`<br>`11 per 10 month`<br>`11 per month` |
| `gan_16825` | `10 per 6 month` | no/yes/yes | no/yes/yes | `12 per 2 month`<br>`12 per 3 month`<br>`8 per 3 month`<br>`8 per 10 month`<br>`8 per month` |
| `gan_16335` | `7 per 3 month` | no/yes/yes | no/yes/yes | `1 per month`<br>`4 per 3 month` |
| `gan_10583` | `unknown, 2 to 3 per cluster` | no/yes/yes | no/no/no | `none` |
| `gan_1463` | `3 per month` | no/no/yes | no/no/yes | `4 per month`<br>`1 per month` |
| `gan_9424` | `10 per 9 month` | no/yes/yes | no/yes/yes | `5 per 3 month` |
| `gan_6094` | `3 per month` | no/yes/yes | no/yes/yes | `2 per month`<br>`1 per month` |
| `gan_1486` | `3 per month` | no/no/no | no/no/no | `1 per month` |
| `gan_7431` | `1 per month` | no/yes/yes | no/yes/yes | `2 per 8 week`<br>`0.25 per week` |
| `gan_16883` | `4 per 3 month` | no/yes/yes | no/yes/yes | `3 per 2 month`<br>`3 per 3 month`<br>`5 per 3 month` |
| `gan_4996` | `seizure free for 16 month` | no/yes/yes | no/no/no | `none` |
| `gan_3355` | `1 per 3 month` | no/yes/yes | no/yes/yes | `3 per 6 month`<br>`0.5 per month`<br>`2 per 2 month`<br>`2 per 4 month`<br>`2 per 5 month` |
| `gan_15129` | `4 per 15 month` | no/no/no | no/no/no | `none` |
| `gan_9063` | `seizure free for 8 month` | no/yes/yes | no/no/no | `2017 per 8 month` |
| `gan_13290` | `4 per 6 month` | no/yes/yes | no/yes/yes | `0.333 per month` |
| `gan_6509` | `1 per week` | no/no/yes | no/no/yes | `1 per 2 week`<br>`0.5 per week` |
| `gan_4378` | `3 per 2 month` | no/no/yes | no/no/no | `none` |
| `gan_6296` | `3 per 4 month` | no/no/no | no/no/no | `none` |
| `gan_13019` | `9 per 3 month` | no/no/no | no/no/no | `none` |
| `gan_9526` | `4 per 8 month` | no/yes/yes | no/yes/yes | `5 per 4 month`<br>`5 per 6 month` |

## Interpretation

- The current raw inventory remains category-useful but exact-label incomplete on the locked exact-miss surface.
- The current constructed aggregate subset does not recover exact labels; it is a traceability subset of existing candidates, not a new aggregation algorithm.
- G10 may proceed only as a category-level or candidate-ranking mechanism comparison unless it adds a separately preregistered aggregation constructor after temporal anchoring and rate/duration aggregation policy work.
- Exact normalized-label and monthly-frequency results from such a narrowed G10 must be reported as unsupported diagnostics, not as evidence that exact label construction is solved.

## Companion Artifact

`docs/experiments/gan/gan_s0_g12_answer_option_surface_20260529.json` contains row-level raw and constructed option views, G1/G11 diffs, summaries, and fixed-control metadata.
