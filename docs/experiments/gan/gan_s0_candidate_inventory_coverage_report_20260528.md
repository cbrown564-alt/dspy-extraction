# Gan S0 Candidate Inventory Coverage Report

Date: 2026-05-28
Status: G1 no-model coverage report
Dataset/split: Gan 2026 synthetic validation split (`gan_2026_fixed_v1:validation`)
Candidate source: `deterministic_temporal_candidates_current_d1_builder`
Gold source: `check__Seizure Frequency Number.seizure_frequency_number[0]`
Scorer semantics: unchanged; category-equivalent coverage is diagnostic.

## Summary

Exact gold-label coverage is **278/299** (93.0%).
Gold-equivalent Purist coverage is **292/299** (97.7%); Pragmatic coverage is **295/299** (98.7%).
The current deterministic substrate emits at least one candidate for **299/299** records (100.0%).

## Coverage By Label Family

| Label family | Records | Any candidates | Exact | Purist equiv. | Pragmatic equiv. |
| --- | ---: | ---: | ---: | ---: | ---: |
| `cluster` | 29 | 29 (100.0%) | 29 (100.0%) | 29 (100.0%) | 29 (100.0%) |
| `no_reference` | 11 | 11 (100.0%) | 11 (100.0%) | 11 (100.0%) | 11 (100.0%) |
| `quantified_rate` | 162 | 162 (100.0%) | 144 (88.9%) | 155 (95.7%) | 158 (97.5%) |
| `seizure_free` | 45 | 45 (100.0%) | 43 (95.6%) | 45 (100.0%) | 45 (100.0%) |
| `unknown` | 35 | 35 (100.0%) | 35 (100.0%) | 35 (100.0%) | 35 (100.0%) |
| `unknown_cluster` | 5 | 5 (100.0%) | 4 (80.0%) | 5 (100.0%) | 5 (100.0%) |
| `vague_or_multiple_rate` | 12 | 12 (100.0%) | 12 (100.0%) | 12 (100.0%) | 12 (100.0%) |

## Coverage By Hard Stratum

| Hard stratum | Records | Any candidates | Exact | Purist equiv. | Pragmatic equiv. |
| --- | ---: | ---: | ---: | ---: | ---: |
| `cluster` | 141 | 141 (100.0%) | 129 (91.5%) | 136 (96.5%) | 139 (98.6%) |
| `gold_evidence_multispan` | 19 | 19 (100.0%) | 17 (89.5%) | 19 (100.0%) | 19 (100.0%) |
| `label_reference_disagreement` | 39 | 39 (100.0%) | 33 (84.6%) | 36 (92.3%) | 37 (94.9%) |
| `multi_highest` | 109 | 109 (100.0%) | 104 (95.4%) | 107 (98.2%) | 109 (100.0%) |
| `no_reference` | 11 | 11 (100.0%) | 11 (100.0%) | 11 (100.0%) | 11 (100.0%) |
| `seizure_free_conflict` | 136 | 136 (100.0%) | 123 (90.4%) | 132 (97.1%) | 134 (98.5%) |
| `unknown_with_events` | 35 | 35 (100.0%) | 35 (100.0%) | 35 (100.0%) | 35 (100.0%) |
| `vague_frequency` | 54 | 54 (100.0%) | 53 (98.1%) | 54 (100.0%) | 54 (100.0%) |

## Candidate Count Distribution

| Candidate count | Records |
| --- | ---: |
| `0` | 0 |
| `1` | 10 |
| `2-3` | 44 |
| `4+` | 245 |

## Candidate Schema Diagnostics

Records with non-canonical candidate labels: **0**.

| Candidate label | Count |
| --- | ---: |
| `none` | 0 |

## Uncovered Exact Gold Samples

| Record | Family | Strata | Gold | Candidate labels |
| --- | --- | --- | --- | --- |
| `gan_15997` | `quantified_rate` | `cluster`, `seizure_free_conflict` | `10 per 3 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`3 per week`<br>`4 per month`<br>`3 per month`<br>`unknown, multiple per cluster` |
| `gan_16772` | `quantified_rate` | `gold_evidence_multispan` | `9 per 5 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`8 per 2 month`<br>`11 per 3 month`<br>`11 per 10 month`<br>`11 per month`<br>`unknown, 1 per cluster` |
| `gan_16825` | `quantified_rate` | `cluster`, `gold_evidence_multispan`, `multi_highest`, `seizure_free_conflict` | `10 per 6 month` | `no seizure frequency reference`<br>`unknown`<br>`12 per 2 month`<br>`12 per 3 month`<br>`8 per 3 month`<br>`8 per 10 month`<br>`8 per month`<br>`unknown, 3 per cluster` |
| `gan_16335` | `quantified_rate` | `none` | `7 per 3 month` | `no seizure frequency reference`<br>`unknown`<br>`1 per month`<br>`4 per 3 month` |
| `gan_10583` | `unknown_cluster` | `cluster`, `vague_frequency` | `unknown, 2 to 3 per cluster` | `no seizure frequency reference`<br>`unknown` |
| `gan_1463` | `quantified_rate` | `cluster`, `seizure_free_conflict` | `3 per month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`seizure free for multiple month`<br>`seizure free for 6 month`<br>`seizure free for multiple month`<br>`4 per month`<br>`1 per month` |
| `gan_9424` | `quantified_rate` | `seizure_free_conflict` | `10 per 9 month` | `no seizure frequency reference`<br>`unknown`<br>`5 per 3 month` |
| `gan_6094` | `quantified_rate` | `cluster`, `label_reference_disagreement`, `multi_highest` | `3 per month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`2 per month`<br>`1 per month` |
| `gan_1486` | `quantified_rate` | `cluster` | `3 per month` | `no seizure frequency reference`<br>`unknown`<br>`1 per month` |
| `gan_7431` | `quantified_rate` | `label_reference_disagreement`, `seizure_free_conflict` | `1 per month` | `no seizure frequency reference`<br>`unknown`<br>`2 per 8 week`<br>`0.25 per week` |
| `gan_16883` | `quantified_rate` | `none` | `4 per 3 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`3 per 2 month`<br>`3 per 3 month`<br>`5 per 3 month` |
| `gan_4996` | `seizure_free` | `seizure_free_conflict` | `seizure free for 16 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`seizure free for multiple month`<br>`seizure free for multiple month`<br>`seizure free for multiple month` |
| `gan_3355` | `quantified_rate` | `cluster`, `label_reference_disagreement`, `seizure_free_conflict` | `1 per 3 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`seizure free for multiple month`<br>`5 per day`<br>`3 per 6 month`<br>`0.5 per month`<br>`2 per 2 month`<br>`2 per 4 month`<br>`2 per 5 month` |
| `gan_15129` | `quantified_rate` | `label_reference_disagreement` | `4 per 15 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`2 per day` |
| `gan_9063` | `seizure_free` | `seizure_free_conflict` | `seizure free for 8 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`2017 per 8 month` |
| `gan_13290` | `quantified_rate` | `cluster`, `seizure_free_conflict` | `4 per 6 month` | `2 per 6 month`<br>`no seizure frequency reference`<br>`unknown`<br>`0.333 per month` |
| `gan_6509` | `quantified_rate` | `cluster`, `label_reference_disagreement`, `multi_highest` | `1 per week` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`2 per day`<br>`1 per day`<br>`1 per 2 week`<br>`0.5 per week` |
| `gan_4378` | `quantified_rate` | `cluster`, `multi_highest`, `seizure_free_conflict` | `3 per 2 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`2 per day` |
| `gan_6296` | `quantified_rate` | `label_reference_disagreement`, `seizure_free_conflict` | `3 per 4 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month` |
| `gan_13019` | `quantified_rate` | `cluster`, `seizure_free_conflict` | `9 per 3 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month` |
| `gan_9526` | `quantified_rate` | `cluster`, `multi_highest`, `seizure_free_conflict` | `4 per 8 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`seizure free for multiple month`<br>`5 per 4 month`<br>`5 per 6 month` |

## Hard-Stratum Misses With Candidates

These are target-selection or label-construction candidates for G2/G3: the substrate found something, but not the exact gold label.

| Record | Family | Strata | Gold | Candidate labels |
| --- | --- | --- | --- | --- |
| `gan_15997` | `quantified_rate` | `cluster`, `seizure_free_conflict` | `10 per 3 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`3 per week`<br>`4 per month`<br>`3 per month`<br>`unknown, multiple per cluster` |
| `gan_16772` | `quantified_rate` | `gold_evidence_multispan` | `9 per 5 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`8 per 2 month`<br>`11 per 3 month`<br>`11 per 10 month`<br>`11 per month`<br>`unknown, 1 per cluster` |
| `gan_16825` | `quantified_rate` | `cluster`, `gold_evidence_multispan`, `multi_highest`, `seizure_free_conflict` | `10 per 6 month` | `no seizure frequency reference`<br>`unknown`<br>`12 per 2 month`<br>`12 per 3 month`<br>`8 per 3 month`<br>`8 per 10 month`<br>`8 per month`<br>`unknown, 3 per cluster` |
| `gan_10583` | `unknown_cluster` | `cluster`, `vague_frequency` | `unknown, 2 to 3 per cluster` | `no seizure frequency reference`<br>`unknown` |
| `gan_1463` | `quantified_rate` | `cluster`, `seizure_free_conflict` | `3 per month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`seizure free for multiple month`<br>`seizure free for 6 month`<br>`seizure free for multiple month`<br>`4 per month`<br>`1 per month` |
| `gan_9424` | `quantified_rate` | `seizure_free_conflict` | `10 per 9 month` | `no seizure frequency reference`<br>`unknown`<br>`5 per 3 month` |
| `gan_6094` | `quantified_rate` | `cluster`, `label_reference_disagreement`, `multi_highest` | `3 per month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`2 per month`<br>`1 per month` |
| `gan_1486` | `quantified_rate` | `cluster` | `3 per month` | `no seizure frequency reference`<br>`unknown`<br>`1 per month` |
| `gan_7431` | `quantified_rate` | `label_reference_disagreement`, `seizure_free_conflict` | `1 per month` | `no seizure frequency reference`<br>`unknown`<br>`2 per 8 week`<br>`0.25 per week` |
| `gan_4996` | `seizure_free` | `seizure_free_conflict` | `seizure free for 16 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`seizure free for multiple month`<br>`seizure free for multiple month`<br>`seizure free for multiple month` |
| `gan_3355` | `quantified_rate` | `cluster`, `label_reference_disagreement`, `seizure_free_conflict` | `1 per 3 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`seizure free for multiple month`<br>`5 per day`<br>`3 per 6 month`<br>`0.5 per month`<br>`2 per 2 month`<br>`2 per 4 month`<br>`2 per 5 month` |
| `gan_15129` | `quantified_rate` | `label_reference_disagreement` | `4 per 15 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`2 per day` |
| `gan_9063` | `seizure_free` | `seizure_free_conflict` | `seizure free for 8 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`2017 per 8 month` |
| `gan_13290` | `quantified_rate` | `cluster`, `seizure_free_conflict` | `4 per 6 month` | `2 per 6 month`<br>`no seizure frequency reference`<br>`unknown`<br>`0.333 per month` |
| `gan_6509` | `quantified_rate` | `cluster`, `label_reference_disagreement`, `multi_highest` | `1 per week` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`2 per day`<br>`1 per day`<br>`1 per 2 week`<br>`0.5 per week` |
| `gan_4378` | `quantified_rate` | `cluster`, `multi_highest`, `seizure_free_conflict` | `3 per 2 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`2 per day` |
| `gan_6296` | `quantified_rate` | `label_reference_disagreement`, `seizure_free_conflict` | `3 per 4 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month` |
| `gan_13019` | `quantified_rate` | `cluster`, `seizure_free_conflict` | `9 per 3 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month` |
| `gan_9526` | `quantified_rate` | `cluster`, `multi_highest`, `seizure_free_conflict` | `4 per 8 month` | `no seizure frequency reference`<br>`unknown`<br>`seizure free for multiple month`<br>`seizure free for multiple month`<br>`5 per 4 month`<br>`5 per 6 month` |

## Interpretation

- This is a no-model inventory report. It does not score a run and does not change `gan_frequency_deterministic_v1` or `gan2026_paper_reproduction`.
- Exact coverage measures whether the deterministic substrate already contains the audited Gan label surface.
- Purist/Pragmatic coverage measures whether a candidate lands in the same diagnostic category as gold, which can be useful for separating candidate inventory failures from exact label-construction failures.
- `reference[0]` is used only through hard-case flags; `seizure_frequency_number[0]` remains the gold label.

## Companion Artifact

`docs/experiments/gan/gan_s0_candidate_inventory_coverage_report_20260528.json` contains all record-level candidates, evidence snippets, hard-stratum flags, and exact/category coverage booleans.
