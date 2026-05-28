# Gan S0 Candidate Inventory Coverage Report

Date: 2026-05-28
Status: G1 no-model coverage report
Dataset/split: Gan 2026 synthetic validation split (`gan_2026_fixed_v1:validation`)
Candidate source: `deterministic_temporal_candidates_current_d1_builder`
Gold source: `check__Seizure Frequency Number.seizure_frequency_number[0]`
Scorer semantics: unchanged; category-equivalent coverage is diagnostic.

## Summary

Exact gold-label coverage is **61/299** (20.4%).
Gold-equivalent Purist coverage is **63/299** (21.1%); Pragmatic coverage is **63/299** (21.1%).
The current deterministic substrate emits at least one candidate for **65/299** records (21.7%).

## Coverage By Label Family

| Label family | Records | Any candidates | Exact | Purist equiv. | Pragmatic equiv. |
| --- | ---: | ---: | ---: | ---: | ---: |
| `cluster` | 29 | 13 (44.8%) | 13 (44.8%) | 13 (44.8%) | 13 (44.8%) |
| `no_reference` | 11 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `quantified_rate` | 162 | 38 (23.5%) | 36 (22.2%) | 37 (22.8%) | 37 (22.8%) |
| `seizure_free` | 45 | 5 (11.1%) | 3 (6.7%) | 4 (8.9%) | 4 (8.9%) |
| `unknown` | 35 | 4 (11.4%) | 4 (11.4%) | 4 (11.4%) | 4 (11.4%) |
| `unknown_cluster` | 5 | 1 (20.0%) | 1 (20.0%) | 1 (20.0%) | 1 (20.0%) |
| `vague_or_multiple_rate` | 12 | 4 (33.3%) | 4 (33.3%) | 4 (33.3%) | 4 (33.3%) |

## Coverage By Hard Stratum

| Hard stratum | Records | Any candidates | Exact | Purist equiv. | Pragmatic equiv. |
| --- | ---: | ---: | ---: | ---: | ---: |
| `cluster` | 141 | 31 (22.0%) | 30 (21.3%) | 31 (22.0%) | 31 (22.0%) |
| `gold_evidence_multispan` | 19 | 7 (36.8%) | 7 (36.8%) | 7 (36.8%) | 7 (36.8%) |
| `label_reference_disagreement` | 39 | 5 (12.8%) | 5 (12.8%) | 5 (12.8%) | 5 (12.8%) |
| `multi_highest` | 109 | 24 (22.0%) | 23 (21.1%) | 24 (22.0%) | 24 (22.0%) |
| `no_reference` | 11 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `seizure_free_conflict` | 136 | 42 (30.9%) | 38 (27.9%) | 40 (29.4%) | 40 (29.4%) |
| `unknown_with_events` | 35 | 4 (11.4%) | 4 (11.4%) | 4 (11.4%) | 4 (11.4%) |
| `vague_frequency` | 54 | 18 (33.3%) | 16 (29.6%) | 17 (31.5%) | 17 (31.5%) |

## Candidate Count Distribution

| Candidate count | Records |
| --- | ---: |
| `0` | 234 |
| `1` | 65 |
| `2-3` | 0 |
| `4+` | 0 |

## Candidate Schema Diagnostics

Records with non-canonical candidate labels: **1**.

| Candidate label | Count |
| --- | ---: |
| `a pair of per 4 month` | 1 |

## Uncovered Exact Gold Samples

| Record | Family | Strata | Gold | Candidate labels |
| --- | --- | --- | --- | --- |
| `gan_6532` | `unknown_cluster` | `cluster`, `label_reference_disagreement`, `vague_frequency` | `unknown, multiple per cluster` | `none` |
| `gan_4956` | `seizure_free` | `cluster`, `label_reference_disagreement`, `seizure_free_conflict` | `seizure free for 7 month` | `none` |
| `gan_4702` | `vague_or_multiple_rate` | `cluster`, `multi_highest`, `vague_frequency` | `multiple per day` | `none` |
| `gan_2609` | `quantified_rate` | `cluster`, `multi_highest` | `1 per day` | `none` |
| `gan_1794` | `quantified_rate` | `multi_highest` | `8 per 2 month` | `none` |
| `gan_7894` | `seizure_free` | `label_reference_disagreement`, `seizure_free_conflict`, `vague_frequency` | `seizure free for multiple year` | `none` |
| `gan_3246` | `cluster` | `cluster` | `2 cluster per month, 4 per cluster` | `none` |
| `gan_4113` | `quantified_rate` | `cluster` | `1 per 1 to 2 day` | `none` |
| `gan_536` | `quantified_rate` | `none` | `1 per 2 day` | `none` |
| `gan_4709` | `vague_or_multiple_rate` | `cluster`, `vague_frequency` | `multiple per day` | `none` |
| `gan_9566` | `unknown` | `seizure_free_conflict`, `unknown_with_events` | `unknown` | `none` |
| `gan_1584` | `quantified_rate` | `cluster`, `multi_highest` | `11 per month` | `none` |
| `gan_15997` | `quantified_rate` | `cluster`, `seizure_free_conflict` | `10 per 3 month` | `none` |
| `gan_17287` | `quantified_rate` | `multi_highest`, `seizure_free_conflict` | `1 per 1 to 2 day` | `none` |
| `gan_16772` | `quantified_rate` | `gold_evidence_multispan` | `9 per 5 month` | `none` |
| `gan_16825` | `quantified_rate` | `cluster`, `gold_evidence_multispan`, `multi_highest`, `seizure_free_conflict` | `10 per 6 month` | `none` |
| `gan_10398` | `cluster` | `cluster` | `1 cluster per week, 2 per cluster` | `none` |
| `gan_16041` | `quantified_rate` | `none` | `9 per 3 month` | `none` |
| `gan_714` | `quantified_rate` | `cluster`, `multi_highest` | `2 per day` | `none` |
| `gan_12465` | `quantified_rate` | `multi_highest` | `1 per day` | `none` |
| `gan_4011` | `quantified_rate` | `seizure_free_conflict` | `1 per month` | `none` |
| `gan_804` | `quantified_rate` | `cluster`, `multi_highest`, `seizure_free_conflict` | `1 per month` | `none` |
| `gan_22` | `quantified_rate` | `cluster`, `multi_highest` | `3 per day` | `none` |
| `gan_16335` | `quantified_rate` | `none` | `7 per 3 month` | `none` |
| `gan_3867` | `quantified_rate` | `none` | `3 per day` | `none` |
| `gan_467` | `quantified_rate` | `multi_highest`, `seizure_free_conflict` | `9 per month` | `none` |
| `gan_2513` | `quantified_rate` | `multi_highest` | `2 to 3 per 2 week` | `none` |
| `gan_5974` | `unknown` | `seizure_free_conflict`, `unknown_with_events` | `unknown` | `none` |
| `gan_6607` | `unknown` | `cluster`, `unknown_with_events` | `unknown` | `none` |
| `gan_12438` | `quantified_rate` | `cluster`, `multi_highest` | `1 per day` | `none` |
| ... | ... | ... | ... | 208 more in JSON report |

## Hard-Stratum Misses With Candidates

These are target-selection or label-construction candidates for G2/G3: the substrate found something, but not the exact gold label.

| Record | Family | Strata | Gold | Candidate labels |
| --- | --- | --- | --- | --- |
| `gan_8858` | `seizure_free` | `multi_highest`, `seizure_free_conflict`, `vague_frequency` | `seizure free for multiple month` | `seizure free for multiple year` |
| `gan_13416` | `seizure_free` | `seizure_free_conflict`, `vague_frequency` | `seizure free for multiple year` | `1 per day` |
| `gan_13290` | `quantified_rate` | `cluster`, `seizure_free_conflict` | `4 per 6 month` | `2 per 6 month` |
| `gan_14390` | `quantified_rate` | `seizure_free_conflict` | `2 per 3 month` | `a pair of per 4 month` |

## Interpretation

- This is a no-model inventory report. It does not score a run and does not change `gan_frequency_deterministic_v1` or `gan2026_paper_reproduction`.
- Exact coverage measures whether the deterministic substrate already contains the audited Gan label surface.
- Purist/Pragmatic coverage measures whether a candidate lands in the same diagnostic category as gold, which can be useful for separating candidate inventory failures from exact label-construction failures.
- `reference[0]` is used only through hard-case flags; `seizure_frequency_number[0]` remains the gold label.

## Companion Artifact

`docs/experiments/gan/gan_s0_candidate_inventory_coverage_report_20260528.json` contains all record-level candidates, evidence snippets, hard-stratum flags, and exact/category coverage booleans.
