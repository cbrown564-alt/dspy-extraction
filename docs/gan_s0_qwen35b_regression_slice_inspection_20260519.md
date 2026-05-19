# Gan S0 Error Analysis: gan_s0_qwen35b_direct_regression_slice_guardrails

## Run

- Artifact directory: `runs\gan_s0_qwen35b_direct_regression_slice_guardrails_20260519T145053Z`
- Split: `gan_2026_fixed_v1:validation`
- Analysis scope: `record_ids_filter`
- Records in split: 299
- Records analyzed: 10
- Valid scored predictions: 9
- Invalid or missing predictions: 1

## Metrics snapshot (valid predictions only)

| Metric | Accuracy | Correct | Denominator |
| --- | ---: | ---: | ---: |
| normalized_label | 88.9% | 8 | 9 |
| monthly_frequency | 88.9% | 8 | 9 |
| purist_category | 100.0% | 9 | 9 |
| pragmatic_category | 100.0% | 9 | 9 |

Benchmark-facing metrics are monthly frequency, Purist category, and Pragmatic category. Normalized-label exact is diagnostic format fidelity.

## Do the four metrics move together?

Bit order in patterns is `normalized | monthly | purist | pragmatic` (1 = match).

| Pattern | Label | Count | Share |
| --- | --- | ---: | ---: |
| `1111` | all_four_match | 8 | 88.9% |
| `0011` | purist_pragmatic_not_monthly | 1 | 11.1% |

### Logical containment on this run

- Normalized exact (8 records): always co-occurs with monthly, Purist, and Pragmatic match.
- Monthly match (8 records): always implies Purist and Pragmatic; 8 also have normalized exact.
- Purist match (9 records): always implies Pragmatic; 8 also match monthly.
- Pragmatic-only wins (pattern `0001`): 0 records.
- Purist-without-monthly (pattern `0010`/`0011`): 0 + 1 records.

### Boundary cases

- **purist_bin_boundary_within_pragmatic**: 0
- **pragmatic_match_monthly_divergence**: 1
- **purist_match_monthly_divergence**: 1
- **monthly_match_label_surface_mismatch**: 0

## Holistic failure taxonomy

### Action tiers (scored misses)

Benchmark-severe classes should drive prompt or verifier work. Diagnostic-only classes preserve monthly/Purist/Pragmatic matches despite normalized-label mismatch.

| Action tier | Count |
| --- | ---: |
| benchmark_severe | 1 |

#### benchmark_severe

| Failure class | Count |
| --- | ---: |
| pragmatic_match_monthly_divergence | 1 |

### Scored misses (normalized label wrong)

| Failure class | Count |
| --- | ---: |
| pragmatic_match_monthly_divergence | 1 |

### Invalid / abstained / missing

| Failure class | Count |
| --- | ---: |
| abstention_or_missing_value | 1 |

### Taxonomy grouped by which metric failed

#### Misses against **normalized_exact**

| Failure class | Count |
| --- | ---: |
| pragmatic_match_monthly_divergence | 1 |

#### Misses against **monthly**

| Failure class | Count |
| --- | ---: |
| pragmatic_match_monthly_divergence | 1 |

#### Misses against **purist**

_No misses._

#### Misses against **pragmatic**

_No misses._

## Interpretation

The four metrics form a strict hierarchy on valid predictions: normalized exact ⊂ monthly ⊂ Purist ⊂ Pragmatic. They do **not** always improve together in the sense that fixing one layer can leave coarser layers unchanged, but finer success never appears without coarser success.

The leading benchmark-severe failure class on this run is `pragmatic_match_monthly_divergence` (1 scored miss). These are the first prompt or verifier targets; lower-tier metric wins should not hide them.

Cluster-format errors account for 0 scored misses, split between incomplete cluster labels (invalid), cluster structure swaps, and cluster collapsed to simple rates.

There are 0 **pragmatic-only** successes: same coarse bucket (infrequent vs frequent vs unknown vs no information) but wrong monthly value and Purist bin. These are clinically misleading if only Pragmatic accuracy is reported.

Purist-without-monthly cases: 1; pragmatic-without-monthly: 1. These arise when different labels land in the same bin but convert to different seizures/month.

Outside scored metrics: 1 abstentions/null outputs and 0 schema-invalid labels (mostly incomplete cluster surfaces and unsupported per-hour rates). These are excluded from the 281-record denominator but are full failures operationally.

## Record index

Full per-record rows are in the companion `records.jsonl` in the run `analysis/` folder.

| record_id | status | norm | mo | pur | prag | failure_class | gold | predicted |
| --- | --- | :---: | :---: | :---: | :---: | --- | --- | --- |
| gan_10509 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_10751 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_11221 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_11733 | invalid | - | - | - | - | abstention_or_missing_value | no seizure frequency reference | None |
| gan_12130 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | multiple per week | 1 per week |
| gan_12810 | scored | Y | Y | Y | Y | all_metrics_match | 5 per 2 month | 5 per 2 month |
| gan_12823 | scored | Y | Y | Y | Y | all_metrics_match | 9 per month | 9 per month |
| gan_10003 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster |
| gan_10052 | scored | Y | Y | Y | Y | all_metrics_match | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month, multiple per cluster |
| gan_10410 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster |
