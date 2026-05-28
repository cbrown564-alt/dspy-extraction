# Gan S0 Error Analysis: gan_s0_qwen35b_direct_cap25_guardrails_validation

## Run

- Artifact directory: `runs\gan_s0_qwen35b_direct_cap25_guardrails_validation_20260519T154228Z`
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
| monthly_frequency | 27.3% | 6 | 22 |
| purist_category | 45.5% | 10 | 22 |
| pragmatic_category | 63.6% | 14 | 22 |

Benchmark-facing metrics are monthly frequency, Purist category, and Pragmatic category. Normalized-label exact is diagnostic format fidelity.

## Stratified operational reporting

- All-record denominator: 25 (valid scored: 22; invalid/missing: 3)
- Overall operational failure rate: 76.0% (19 failures)

| Stratum | All records | Valid scored | Operational failure rate | Monthly (valid only) |
| --- | ---: | ---: | ---: | ---: |
| hard_case=true | 5 | 4 | 60.0% | 50.0% |
| hard_case=false | 20 | 18 | 80.0% | 22.2% |
| row_ok=true | 24 | 21 | 75.0% | 28.6% |
| row_ok=false | 1 | 1 | 100.0% | 0.0% |
| gold_pragmatic=frequent | 16 | 13 | 75.0% | 30.8% |
| gold_pragmatic=infrequent | 4 | 4 | 100.0% | 0.0% |
| gold_pragmatic=no_seizure_information | 2 | 2 | 0.0% | 100.0% |
| gold_pragmatic=unknown | 3 | 3 | 100.0% | 0.0% |

## Do the four metrics move together?

Bit order in patterns is `normalized | monthly | purist | pragmatic` (1 = match).

| Pattern | Label | Count | Share |
| --- | --- | ---: | ---: |
| `1111` | all_four_match | 5 | 22.7% |
| `0000` | all_four_wrong | 8 | 36.4% |
| `0011` | purist_pragmatic_not_monthly | 4 | 18.2% |
| `0001` | pragmatic_only | 4 | 18.2% |
| `0111` | monthly_purist_pragmatic_not_normalized | 1 | 4.5% |

### Logical containment on this run

- Normalized exact (5 records): always co-occurs with monthly, Purist, and Pragmatic match.
- Monthly match (6 records): always implies Purist and Pragmatic; 5 also have normalized exact.
- Purist match (10 records): always implies Pragmatic; 6 also match monthly.
- Pragmatic-only wins (pattern `0001`): 4 records.
- Purist-without-monthly (pattern `0010`/`0011`): 0 + 4 records.

### Boundary cases

- **purist_bin_boundary_within_pragmatic**: 4
- **pragmatic_match_monthly_divergence**: 8
- **purist_match_monthly_divergence**: 4
- **monthly_match_label_surface_mismatch**: 1

## Holistic failure taxonomy

### Action tiers (scored misses)

Benchmark-severe classes should drive prompt or verifier work. Diagnostic-only classes preserve monthly/Purist/Pragmatic matches despite normalized-label mismatch.

| Action tier | Count |
| --- | ---: |
| benchmark_severe | 16 |
| diagnostic_only | 1 |

#### benchmark_severe

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 5 |
| purist_bin_boundary_within_pragmatic | 4 |
| pragmatic_match_monthly_divergence | 3 |
| cluster_collapsed_to_rate | 1 |
| cluster_semantic_mismatch | 1 |
| cluster_structure_swap | 1 |
| unknown_as_quantified_rate | 1 |

#### diagnostic_only

| Failure class | Count |
| --- | ---: |
| seizure_free_label_shape_mismatch | 1 |

### Scored misses (normalized label wrong)

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 5 |
| purist_bin_boundary_within_pragmatic | 4 |
| pragmatic_match_monthly_divergence | 3 |
| cluster_structure_swap | 1 |
| cluster_semantic_mismatch | 1 |
| cluster_collapsed_to_rate | 1 |
| seizure_free_label_shape_mismatch | 1 |
| unknown_as_quantified_rate | 1 |

### Invalid / abstained / missing

| Failure class | Count |
| --- | ---: |
| invalid_predicted_label | 3 |

### Taxonomy grouped by which metric failed

#### Misses against **normalized_exact**

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 5 |
| purist_bin_boundary_within_pragmatic | 4 |
| pragmatic_match_monthly_divergence | 3 |
| cluster_collapsed_to_rate | 1 |
| cluster_semantic_mismatch | 1 |
| cluster_structure_swap | 1 |
| seizure_free_label_shape_mismatch | 1 |
| unknown_as_quantified_rate | 1 |

#### Misses against **monthly**

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 5 |
| purist_bin_boundary_within_pragmatic | 4 |
| pragmatic_match_monthly_divergence | 3 |
| cluster_collapsed_to_rate | 1 |
| cluster_semantic_mismatch | 1 |
| cluster_structure_swap | 1 |
| unknown_as_quantified_rate | 1 |

#### Misses against **purist**

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 5 |
| purist_bin_boundary_within_pragmatic | 4 |
| cluster_collapsed_to_rate | 1 |
| cluster_structure_swap | 1 |
| unknown_as_quantified_rate | 1 |

#### Misses against **pragmatic**

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 5 |
| cluster_collapsed_to_rate | 1 |
| cluster_structure_swap | 1 |
| unknown_as_quantified_rate | 1 |

## Interpretation

The four metrics form a strict hierarchy on valid predictions: normalized exact ⊂ monthly ⊂ Purist ⊂ Pragmatic. They do **not** always improve together in the sense that fixing one layer can leave coarser layers unchanged, but finer success never appears without coarser success.

The leading benchmark-severe failure class on this run is `other_semantic_mismatch` (5 scored misses). These are the first prompt or verifier targets; lower-tier metric wins should not hide them.

Cluster-format errors account for 3 scored misses, split between incomplete cluster labels (invalid), cluster structure swaps, and cluster collapsed to simple rates.

There are 4 **pragmatic-only** successes: same coarse bucket (infrequent vs frequent vs unknown vs no information) but wrong monthly value and Purist bin. These are clinically misleading if only Pragmatic accuracy is reported.

Purist-without-monthly cases: 4; pragmatic-without-monthly: 8. These arise when different labels land in the same bin but convert to different seizures/month.

Outside scored metrics: 0 abstentions/null outputs and 3 schema-invalid labels (mostly incomplete cluster surfaces and unsupported per-hour rates). These are excluded from the 281-record denominator but are full failures operationally.

## Record index

Full per-record rows are in the companion `records.jsonl` in the run `analysis/` folder.

| record_id | status | norm | mo | pur | prag | failure_class | gold | predicted |
| --- | --- | :---: | :---: | :---: | :---: | --- | --- | --- |
| gan_10052 | scored | Y | Y | Y | Y | all_metrics_match | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month, multiple per cluster |
| gan_10434 | invalid | - | - | - | - | invalid_predicted_label | multiple cluster per week, 2 to 3 per cluster | multiple per week, multiple per cluster |
| gan_10618 | scored | N | N | N | N | cluster_structure_swap | unknown, 4 to 6 per cluster | 1 cluster per week, multiple per cluster |
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
| gan_4709 | scored | N | N | N | N | other_semantic_mismatch | multiple per day | unknown |
| gan_4956 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 7 month | seizure free for 7 month |
| gan_536 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 2 day | 1 per 2 day |
| gan_6532 | scored | N | N | N | N | cluster_collapsed_to_rate | unknown, multiple per cluster | 5 per 2 week |
| gan_7894 | scored | N | Y | Y | Y | seizure_free_label_shape_mismatch | seizure free for multiple year | seizure free for 35 year |
| gan_9566 | scored | N | N | N | N | unknown_as_quantified_rate | unknown | 1 to 2 per 8 week |
