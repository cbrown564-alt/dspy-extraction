# Gan S0 Error Analysis: gan_s0_qwen35b_labeled_fewshot_regression_slice_guardrails

## Run

- Artifact directory: `runs\gan_s0_qwen35b_labeled_fewshot_regression_slice_guardrails_20260519T160348Z`
- Split: `gan_2026_fixed_v1:validation`
- Analysis scope: `record_ids_filter`
- Records in split: 299
- Records analyzed: 14
- Valid scored predictions: 13
- Invalid or missing predictions: 1

## Metrics snapshot (valid predictions only)

| Metric | Accuracy | Correct | Denominator |
| --- | ---: | ---: | ---: |
| normalized_label | 69.2% | 9 | 13 |
| monthly_frequency | 69.2% | 9 | 13 |
| purist_category | 69.2% | 9 | 13 |
| pragmatic_category | 69.2% | 9 | 13 |

Benchmark-facing metrics are monthly frequency, Purist category, and Pragmatic category. Normalized-label exact is diagnostic format fidelity.

## Stratified operational reporting

- All-record denominator: 14 (valid scored: 13; invalid/missing: 1)
- Overall operational failure rate: 35.7% (5 failures)

| Stratum | All records | Valid scored | Operational failure rate | Monthly (valid only) |
| --- | ---: | ---: | ---: | ---: |
| hard_case=true | 0 | 0 | n/a | n/a |
| hard_case=false | 14 | 13 | 35.7% | 69.2% |
| row_ok=true | 12 | 11 | 33.3% | 72.7% |
| row_ok=false | 2 | 2 | 50.0% | 50.0% |
| gold_pragmatic=frequent | 6 | 6 | 0.0% | 100.0% |
| gold_pragmatic=infrequent | 4 | 4 | 100.0% | 0.0% |
| gold_pragmatic=no_seizure_information | 1 | 1 | 0.0% | 100.0% |
| gold_pragmatic=unknown | 3 | 2 | 33.3% | 100.0% |

## Do the four metrics move together?

Bit order in patterns is `normalized | monthly | purist | pragmatic` (1 = match).

| Pattern | Label | Count | Share |
| --- | --- | ---: | ---: |
| `1111` | all_four_match | 9 | 69.2% |
| `0000` | all_four_wrong | 4 | 30.8% |

### Logical containment on this run

- Normalized exact (9 records): always co-occurs with monthly, Purist, and Pragmatic match.
- Monthly match (9 records): always implies Purist and Pragmatic; 9 also have normalized exact.
- Purist match (9 records): always implies Pragmatic; 9 also match monthly.
- Pragmatic-only wins (pattern `0001`): 0 records.
- Purist-without-monthly (pattern `0010`/`0011`): 0 + 0 records.

### Boundary cases

- **purist_bin_boundary_within_pragmatic**: 0
- **pragmatic_match_monthly_divergence**: 0
- **purist_match_monthly_divergence**: 0
- **monthly_match_label_surface_mismatch**: 0

## Holistic failure taxonomy

### Action tiers (scored misses)

Benchmark-severe classes should drive prompt or verifier work. Diagnostic-only classes preserve monthly/Purist/Pragmatic matches despite normalized-label mismatch.

| Action tier | Count |
| --- | ---: |
| benchmark_severe | 4 |

#### benchmark_severe

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 4 |

### Scored misses (normalized label wrong)

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 4 |

### Invalid / abstained / missing

| Failure class | Count |
| --- | ---: |
| abstention_or_missing_value | 1 |

### Taxonomy grouped by which metric failed

#### Misses against **normalized_exact**

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 4 |

#### Misses against **monthly**

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 4 |

#### Misses against **purist**

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 4 |

#### Misses against **pragmatic**

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 4 |

## Interpretation

The four metrics form a strict hierarchy on valid predictions: normalized exact ⊂ monthly ⊂ Purist ⊂ Pragmatic. They do **not** always improve together in the sense that fixing one layer can leave coarser layers unchanged, but finer success never appears without coarser success.

The leading benchmark-severe failure class on this run is `other_semantic_mismatch` (4 scored misses). These are the first prompt or verifier targets; lower-tier metric wins should not hide them.

Cluster-format errors account for 0 scored misses, split between incomplete cluster labels (invalid), cluster structure swaps, and cluster collapsed to simple rates.

There are 0 **pragmatic-only** successes: same coarse bucket (infrequent vs frequent vs unknown vs no information) but wrong monthly value and Purist bin. These are clinically misleading if only Pragmatic accuracy is reported.

Purist-without-monthly cases: 0; pragmatic-without-monthly: 0. These arise when different labels land in the same bin but convert to different seizures/month.

Outside scored metrics: 1 abstentions/null outputs and 0 schema-invalid labels (mostly incomplete cluster surfaces and unsupported per-hour rates). These are excluded from the 281-record denominator but are full failures operationally.

## Record index

Full per-record rows are in the companion `records.jsonl` in the run `analysis/` folder.

| record_id | status | norm | mo | pur | prag | failure_class | gold | predicted |
| --- | --- | :---: | :---: | :---: | :---: | --- | --- | --- |
| gan_10509 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_10751 | invalid | - | - | - | - | abstention_or_missing_value | unknown | None |
| gan_11221 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_11733 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_12130 | scored | Y | Y | Y | Y | all_metrics_match | multiple per week | multiple per week |
| gan_12810 | scored | Y | Y | Y | Y | all_metrics_match | 5 per 2 month | 5 per 2 month |
| gan_12823 | scored | Y | Y | Y | Y | all_metrics_match | 9 per month | 9 per month |
| gan_10003 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster |
| gan_10052 | scored | Y | Y | Y | Y | all_metrics_match | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month, multiple per cluster |
| gan_10410 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster |
| gan_13123 | scored | N | N | N | N | other_semantic_mismatch | 1 per year | unknown |
| gan_14485 | scored | N | N | N | N | other_semantic_mismatch | 2 per 3 month | unknown |
| gan_14881 | scored | N | N | N | N | other_semantic_mismatch | 1 per month | unknown |
| gan_15306 | scored | N | N | N | N | other_semantic_mismatch | 2 to 3 per 15 month | unknown |
