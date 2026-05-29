# Gan S0 G11 Candidate-Inventory Challenge-Set Pass

Date: 2026-05-29
Status: current synthesis / no-model coverage gate
Kanban card: G11 - Gan Candidate-Inventory Challenge-Set Pass
Dataset/split: Gan 2026 synthetic (`gan_2026_fixed_v1:validation`)
Challenge set: `gan_s0_g6_candidate_coverage_exact_miss`
Candidate source: `deterministic_temporal_candidates_current_d1_builder`
Gold source: `check__Seizure Frequency Number.seizure_frequency_number[0]`
Scorer semantics: unchanged; category-equivalent coverage is diagnostic.

## Summary

Challenge set coverage: **0/21** exact, **14/21** Purist-equivalent, and **17/21** Pragmatic-equivalent.
G9 standard50 exact-miss subset coverage: **0/4** exact, **4/4** Purist-equivalent, and **4/4** Pragmatic-equivalent.
Compared with the stored G1 substrate, **20** rows changed.
Candidate-builder policy: current runtime prunes broad abstention options when concrete frequency candidates are present.

## Coverage By Family

| Family | Records | Exact | Purist equiv. | Pragmatic equiv. |
| --- | ---: | ---: | ---: | ---: |
| `quantified_rate` | 18 | 0 (0.0%) | 11 (61.1%) | 14 (77.8%) |
| `seizure_free` | 2 | 0 (0.0%) | 2 (100.0%) | 2 (100.0%) |
| `unknown_cluster` | 1 | 0 (0.0%) | 1 (100.0%) | 1 (100.0%) |

## Coverage By Hard Stratum

| Hard stratum | Records | Exact | Purist equiv. | Pragmatic equiv. |
| --- | ---: | ---: | ---: | ---: |
| `cluster` | 12 | 0 (0.0%) | 7 (58.3%) | 10 (83.3%) |
| `gold_evidence_multispan` | 2 | 0 (0.0%) | 2 (100.0%) | 2 (100.0%) |
| `label_reference_disagreement` | 6 | 0 (0.0%) | 3 (50.0%) | 4 (66.7%) |
| `multi_highest` | 5 | 0 (0.0%) | 3 (60.0%) | 5 (100.0%) |
| `seizure_free_conflict` | 13 | 0 (0.0%) | 9 (69.2%) | 11 (84.6%) |
| `vague_frequency` | 1 | 0 (0.0%) | 1 (100.0%) | 1 (100.0%) |

## Exact-Miss Rows

| Record | Gold | Family | Purist equiv. | Pragmatic equiv. | Candidate labels |
| --- | --- | --- | ---: | ---: | --- |
| `gan_15997` | `10 per 3 month` | `quantified_rate` | yes | yes | `seizure free for multiple month`<br>`3 per week`<br>`4 per month`<br>`3 per month`<br>`unknown, multiple per cluster` |
| `gan_16772` | `9 per 5 month` | `quantified_rate` | yes | yes | `seizure free for multiple month`<br>`8 per 2 month`<br>`11 per 3 month`<br>`11 per 10 month`<br>`11 per month`<br>`unknown, 1 per cluster` |
| `gan_16825` | `10 per 6 month` | `quantified_rate` | yes | yes | `12 per 2 month`<br>`12 per 3 month`<br>`8 per 3 month`<br>`8 per 10 month`<br>`8 per month`<br>`unknown, 3 per cluster` |
| `gan_16335` | `7 per 3 month` | `quantified_rate` | yes | yes | `1 per month`<br>`4 per 3 month` |
| `gan_10583` | `unknown, 2 to 3 per cluster` | `unknown_cluster` | yes | yes | `no seizure frequency reference`<br>`unknown` |
| `gan_1463` | `3 per month` | `quantified_rate` | no | yes | `seizure free for multiple month`<br>`seizure free for multiple month`<br>`seizure free for 6 month`<br>`seizure free for multiple month`<br>`4 per month`<br>`1 per month` |
| `gan_9424` | `10 per 9 month` | `quantified_rate` | yes | yes | `5 per 3 month` |
| `gan_6094` | `3 per month` | `quantified_rate` | yes | yes | `seizure free for multiple month`<br>`2 per month`<br>`1 per month` |
| `gan_1486` | `3 per month` | `quantified_rate` | no | no | `1 per month` |
| `gan_7431` | `1 per month` | `quantified_rate` | yes | yes | `2 per 8 week`<br>`0.25 per week` |
| `gan_16883` | `4 per 3 month` | `quantified_rate` | yes | yes | `seizure free for multiple month`<br>`3 per 2 month`<br>`3 per 3 month`<br>`5 per 3 month` |
| `gan_4996` | `seizure free for 16 month` | `seizure_free` | yes | yes | `seizure free for multiple month`<br>`seizure free for multiple month`<br>`seizure free for multiple month`<br>`seizure free for multiple month` |
| `gan_3355` | `1 per 3 month` | `quantified_rate` | yes | yes | `seizure free for multiple month`<br>`seizure free for multiple month`<br>`5 per day`<br>`3 per 6 month`<br>`0.5 per month`<br>`2 per 2 month`<br>`2 per 4 month`<br>`2 per 5 month` |
| `gan_15129` | `4 per 15 month` | `quantified_rate` | no | no | `seizure free for multiple month`<br>`2 per day` |
| `gan_9063` | `seizure free for 8 month` | `seizure_free` | yes | yes | `seizure free for multiple month`<br>`2017 per 8 month` |
| `gan_13290` | `4 per 6 month` | `quantified_rate` | yes | yes | `2 per 6 month`<br>`0.333 per month` |
| `gan_6509` | `1 per week` | `quantified_rate` | no | yes | `seizure free for multiple month`<br>`2 per day`<br>`1 per day`<br>`1 per 2 week`<br>`0.5 per week` |
| `gan_4378` | `3 per 2 month` | `quantified_rate` | no | yes | `seizure free for multiple month`<br>`2 per day` |
| `gan_6296` | `3 per 4 month` | `quantified_rate` | no | no | `seizure free for multiple month` |
| `gan_13019` | `9 per 3 month` | `quantified_rate` | no | no | `seizure free for multiple month` |
| `gan_9526` | `4 per 8 month` | `quantified_rate` | yes | yes | `seizure free for multiple month`<br>`seizure free for multiple month`<br>`5 per 4 month`<br>`5 per 6 month` |

## Decision

- Inventory-stage interpretation: **raw_inventory_requires_aggregation_aware_answer_options**.
- Follow-up: **scope_temporal_anchoring_and_aggregation_answer_option_surface**.
- G10 routing: Do not use raw inventory labels alone as exact-label answer options. Current coverage is 0/21 exact, 14/21 Purist-equivalent, and 17/21 Pragmatic-equivalent; aggregated gold labels may need to be constructed downstream from separately reported event pieces.

## Interpretation

- The existing candidate inventory still has no exact-label coverage on the locked G6 exact-miss challenge set, but exact coverage is not always expected at the inventory boundary.
- Many gold labels in this surface require temporal anchoring and aggregation across separately reported seizure-frequency events; those exact labels may not appear verbatim in the note.
- Most misses have Purist or Pragmatic category-equivalent candidates, so the open question is whether the downstream aggregation/answer-option construction step can compose the right label from represented event pieces.
- Four records routed by G9 from the G8 standard50 misses remain exact misses, even though all four have Purist and Pragmatic equivalent candidates.
- G10 should not treat raw inventory labels as the complete answer-option set for aggregated cases; it needs an aggregation-aware answer-option surface or an explicit decision to evaluate category-level selection only.

## Companion Artifact

`docs/experiments/gan/gan_s0_g11_candidate_inventory_challenge_set_pass_20260529.json` contains row-level candidates, G1 diffs, summaries, and fixed-control metadata.
