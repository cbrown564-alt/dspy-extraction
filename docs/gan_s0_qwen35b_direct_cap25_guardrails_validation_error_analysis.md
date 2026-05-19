# Gan S0 Error Analysis: gan_s0_qwen35b_direct_cap25_guardrails_validation

## Run

- Artifact directory: `runs\gan_s0_qwen35b_direct_cap25_guardrails_validation_20260519T145440Z`
- Split: `gan_2026_fixed_v1:validation`
- Analysis scope: `predicted_subset`
- Records in split: 299
- Records analyzed: 25
- Valid scored predictions: 22
- Invalid or missing predictions: 3

## Metrics snapshot (valid predictions only)

| Metric | Accuracy | Correct | Denominator |
| --- | ---: | ---: | ---: |
| normalized_label | 22.7% | 5 | 22 |
| monthly_frequency | 36.4% | 8 | 22 |
| purist_category | 54.5% | 12 | 22 |
| pragmatic_category | 77.3% | 17 | 22 |

Benchmark-facing metrics are monthly frequency, Purist category, and Pragmatic category. Normalized-label exact is diagnostic format fidelity.

## Do the four metrics move together?

Bit order in patterns is `normalized | monthly | purist | pragmatic` (1 = match).

| Pattern | Label | Count | Share |
| --- | --- | ---: | ---: |
| `1111` | all_four_match | 5 | 22.7% |
| `0001` | pragmatic_only | 5 | 22.7% |
| `0111` | monthly_purist_pragmatic_not_normalized | 3 | 13.6% |
| `0000` | all_four_wrong | 5 | 22.7% |
| `0011` | purist_pragmatic_not_monthly | 4 | 18.2% |

### Logical containment on this run

- Normalized exact (5 records): always co-occurs with monthly, Purist, and Pragmatic match.
- Monthly match (8 records): always implies Purist and Pragmatic; 5 also have normalized exact.
- Purist match (12 records): always implies Pragmatic; 8 also match monthly.
- Pragmatic-only wins (pattern `0001`): 5 records.
- Purist-without-monthly (pattern `0010`/`0011`): 0 + 4 records.

### Boundary cases

- **purist_bin_boundary_within_pragmatic**: 5
- **pragmatic_match_monthly_divergence**: 9
- **purist_match_monthly_divergence**: 4
- **monthly_match_label_surface_mismatch**: 3

## Holistic failure taxonomy

### Action tiers (scored misses)

Benchmark-severe classes should drive prompt or verifier work. Diagnostic-only classes preserve monthly/Purist/Pragmatic matches despite normalized-label mismatch.

| Action tier | Count |
| --- | ---: |
| benchmark_severe | 14 |
| diagnostic_only | 3 |

#### benchmark_severe

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 4 |
| purist_bin_boundary_within_pragmatic | 4 |
| pragmatic_match_monthly_divergence | 3 |
| cluster_semantic_mismatch | 2 |
| unknown_as_quantified_rate | 1 |

#### diagnostic_only

| Failure class | Count |
| --- | ---: |
| unknown_cluster_label_shape_mismatch | 2 |
| seizure_free_to_no_reference_monthly_match | 1 |

### Scored misses (normalized label wrong)

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 4 |
| purist_bin_boundary_within_pragmatic | 4 |
| pragmatic_match_monthly_divergence | 3 |
| cluster_semantic_mismatch | 2 |
| unknown_cluster_label_shape_mismatch | 2 |
| seizure_free_to_no_reference_monthly_match | 1 |
| unknown_as_quantified_rate | 1 |

### Invalid / abstained / missing

| Failure class | Count |
| --- | ---: |
| invalid_predicted_label | 3 |

### Taxonomy grouped by which metric failed

#### Misses against **normalized_exact**

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 4 |
| purist_bin_boundary_within_pragmatic | 4 |
| pragmatic_match_monthly_divergence | 3 |
| cluster_semantic_mismatch | 2 |
| unknown_cluster_label_shape_mismatch | 2 |
| seizure_free_to_no_reference_monthly_match | 1 |
| unknown_as_quantified_rate | 1 |

#### Misses against **monthly**

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 4 |
| purist_bin_boundary_within_pragmatic | 4 |
| pragmatic_match_monthly_divergence | 3 |
| cluster_semantic_mismatch | 2 |
| unknown_as_quantified_rate | 1 |

#### Misses against **purist**

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 4 |
| purist_bin_boundary_within_pragmatic | 4 |
| cluster_semantic_mismatch | 1 |
| unknown_as_quantified_rate | 1 |

#### Misses against **pragmatic**

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 4 |
| unknown_as_quantified_rate | 1 |

## Interpretation

The four metrics form a strict hierarchy on valid predictions: normalized exact ⊂ monthly ⊂ Purist ⊂ Pragmatic. They do **not** always improve together in the sense that fixing one layer can leave coarser layers unchanged, but finer success never appears without coarser success.

The dominant semantic failure mode is **unknown versus no seizure frequency reference** (0 scored misses). This collapses monthly frequency from 1000.0 to 0.0 and fails all four metrics simultaneously (pattern `0000`).

Cluster-format errors account for 4 scored misses, split between incomplete cluster labels (invalid), cluster structure swaps, and cluster collapsed to simple rates.

There are 5 **pragmatic-only** successes: same coarse bucket (infrequent vs frequent vs unknown vs no information) but wrong monthly value and Purist bin. These are clinically misleading if only Pragmatic accuracy is reported.

Purist-without-monthly cases: 4; pragmatic-without-monthly: 9. These arise when different labels land in the same bin but convert to different seizures/month.

Outside scored metrics: 0 abstentions/null outputs and 3 schema-invalid labels (mostly incomplete cluster surfaces and unsupported per-hour rates). These are excluded from the 281-record denominator but are full failures operationally.

## Record index

Full per-record rows are in the companion `records.jsonl` in the run `analysis/` folder.

| record_id | status | norm | mo | pur | prag | failure_class | gold | predicted |
| --- | --- | :---: | :---: | :---: | :---: | --- | --- | --- |
| gan_10052 | scored | Y | Y | Y | Y | all_metrics_match | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month, multiple per cluster |
| gan_10434 | scored | N | N | N | Y | cluster_semantic_mismatch | multiple cluster per week, 2 to 3 per cluster | 1 cluster per week, multiple per cluster |
| gan_10618 | scored | N | Y | Y | Y | unknown_cluster_label_shape_mismatch | unknown, 4 to 6 per cluster | unknown |
| gan_12679 | invalid | - | - | - | - | invalid_predicted_label | 1 per day | 1 to 2 per month, multiple per cluster |
| gan_13123 | scored | N | N | N | N | other_semantic_mismatch | 1 per year | unknown |
| gan_14485 | scored | N | N | N | N | other_semantic_mismatch | 2 per 3 month | unknown |
| gan_14881 | scored | N | N | N | N | other_semantic_mismatch | 1 per month | unknown |
| gan_15306 | scored | N | N | N | N | other_semantic_mismatch | 2 to 3 per 15 month | unknown |
| gan_1584 | scored | Y | Y | Y | Y | all_metrics_match | 11 per month | 11 per month |
| gan_15997 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 10 per 3 month | 8 per 3 month |
| gan_16251 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 14 per 4 month | 7 per month |
| gan_16772 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 9 per 5 month | 9 per 3 month |
| gan_16825 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 10 per 6 month | 10 per 3 month |
| gan_17287 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 1 per 1 to 2 day | 1 per day |
| gan_1794 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 8 per 2 month | 6 per 2 month |
| gan_2609 | scored | Y | Y | Y | Y | all_metrics_match | 1 per day | 1 per day |
| gan_3246 | scored | N | N | Y | Y | cluster_semantic_mismatch | 2 cluster per month, 4 per cluster | 2 cluster per month, multiple per cluster |
| gan_4113 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 1 per 1 to 2 day | 1 per day |
| gan_4702 | invalid | - | - | - | - | invalid_predicted_label | multiple per day | 4 per hour |
| gan_4709 | invalid | - | - | - | - | invalid_predicted_label | multiple per day | 6 per hour |
| gan_4956 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 7 month | seizure free for 7 month |
| gan_536 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 2 day | 1 per 2 day |
| gan_6532 | scored | N | Y | Y | Y | unknown_cluster_label_shape_mismatch | unknown, multiple per cluster | unknown |
| gan_7894 | scored | N | Y | Y | Y | seizure_free_to_no_reference_monthly_match | seizure free for multiple year | no seizure frequency reference |
| gan_9566 | scored | N | N | N | N | unknown_as_quantified_rate | unknown | 1 to 2 per 8 week |
