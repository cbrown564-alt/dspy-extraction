# Gan S0 Error Analysis: gan_s0_qwen35b_direct_full_validation_guardrails

## Run

- Artifact directory: `runs\gan_s0_qwen35b_direct_full_validation_guardrails_20260519T102249Z`
- Split: `gan_2026_fixed_v1:validation`
- Records in split: 299
- Valid scored predictions: 281
- Invalid or missing predictions: 18

## Metrics snapshot (valid predictions only)

| Metric | Accuracy | Correct | Denominator |
| --- | ---: | ---: | ---: |
| normalized_label | 43.8% | 123 | 281 |
| monthly_frequency | 55.9% | 157 | 281 |
| purist_category | 61.9% | 174 | 281 |
| pragmatic_category | 70.5% | 198 | 281 |

Benchmark-facing metrics are monthly frequency, Purist category, and Pragmatic category. Normalized-label exact is diagnostic format fidelity.

## Do the four metrics move together?

Bit order in patterns is `normalized | monthly | purist | pragmatic` (1 = match).

| Pattern | Label | Count | Share |
| --- | --- | ---: | ---: |
| `0000` | all_four_wrong | 83 | 29.5% |
| `0011` | purist_pragmatic_not_monthly | 17 | 6.0% |
| `1111` | all_four_match | 123 | 43.8% |
| `0001` | pragmatic_only | 24 | 8.5% |
| `0111` | monthly_purist_pragmatic_not_normalized | 34 | 12.1% |

### Logical containment on this run

- Normalized exact (123 records): always co-occurs with monthly, Purist, and Pragmatic match.
- Monthly match (157 records): always implies Purist and Pragmatic; 123 also have normalized exact.
- Purist match (174 records): always implies Pragmatic; 157 also match monthly.
- Pragmatic-only wins (pattern `0001`): 24 records.
- Purist-without-monthly (pattern `0010`/`0011`): 0 + 17 records.

### Boundary cases

- **purist_bin_boundary_within_pragmatic**: 24
- **pragmatic_match_monthly_divergence**: 41
- **purist_match_monthly_divergence**: 17
- **monthly_match_label_surface_mismatch**: 34

## Holistic failure taxonomy

### Scored misses (normalized label wrong)

| Failure class | Count |
| --- | ---: |
| missed_frequency_reference | 35 |
| unknown_vs_no_reference | 22 |
| purist_bin_boundary_within_pragmatic | 20 |
| monthly_match_label_surface_mismatch | 19 |
| frequent_undercalled | 13 |
| pragmatic_match_monthly_divergence | 13 |
| cluster_collapsed_to_rate | 11 |
| cluster_semantic_mismatch | 6 |
| unknown_as_high_rate | 6 |
| unknown_cluster_vs_no_reference | 4 |
| other_semantic_mismatch | 4 |
| frequent_overcalled | 2 |
| unknown_as_quantified_rate | 2 |
| unknown_vs_seizure_free | 1 |

### Invalid / abstained / missing

| Failure class | Count |
| --- | ---: |
| abstention_or_missing_value | 11 |
| invalid_predicted_label | 7 |

### Taxonomy grouped by which metric failed

#### Misses against **normalized_exact**

| Failure class | Count |
| --- | ---: |
| missed_frequency_reference | 35 |
| unknown_vs_no_reference | 22 |
| purist_bin_boundary_within_pragmatic | 20 |
| monthly_match_label_surface_mismatch | 19 |
| frequent_undercalled | 13 |
| pragmatic_match_monthly_divergence | 13 |
| cluster_collapsed_to_rate | 11 |
| cluster_semantic_mismatch | 6 |
| unknown_as_high_rate | 6 |
| other_semantic_mismatch | 4 |
| unknown_cluster_vs_no_reference | 4 |
| frequent_overcalled | 2 |
| unknown_as_quantified_rate | 2 |
| unknown_vs_seizure_free | 1 |

#### Misses against **monthly**

| Failure class | Count |
| --- | ---: |
| missed_frequency_reference | 22 |
| unknown_vs_no_reference | 22 |
| purist_bin_boundary_within_pragmatic | 20 |
| frequent_undercalled | 13 |
| pragmatic_match_monthly_divergence | 13 |
| cluster_collapsed_to_rate | 9 |
| cluster_semantic_mismatch | 6 |
| unknown_as_high_rate | 6 |
| other_semantic_mismatch | 4 |
| unknown_cluster_vs_no_reference | 4 |
| frequent_overcalled | 2 |
| unknown_as_quantified_rate | 2 |
| unknown_vs_seizure_free | 1 |

#### Misses against **purist**

| Failure class | Count |
| --- | ---: |
| missed_frequency_reference | 22 |
| unknown_vs_no_reference | 22 |
| purist_bin_boundary_within_pragmatic | 20 |
| frequent_undercalled | 13 |
| cluster_collapsed_to_rate | 8 |
| unknown_as_high_rate | 6 |
| other_semantic_mismatch | 4 |
| unknown_cluster_vs_no_reference | 4 |
| cluster_semantic_mismatch | 3 |
| frequent_overcalled | 2 |
| unknown_as_quantified_rate | 2 |
| unknown_vs_seizure_free | 1 |

#### Misses against **pragmatic**

| Failure class | Count |
| --- | ---: |
| missed_frequency_reference | 22 |
| unknown_vs_no_reference | 22 |
| frequent_undercalled | 13 |
| unknown_as_high_rate | 6 |
| cluster_collapsed_to_rate | 5 |
| other_semantic_mismatch | 4 |
| unknown_cluster_vs_no_reference | 4 |
| cluster_semantic_mismatch | 2 |
| frequent_overcalled | 2 |
| unknown_as_quantified_rate | 2 |
| unknown_vs_seizure_free | 1 |

## Interpretation

The four metrics form a strict hierarchy on valid predictions: normalized exact ⊂ monthly ⊂ Purist ⊂ Pragmatic. They do **not** always improve together in the sense that fixing one layer can leave coarser layers unchanged, but finer success never appears without coarser success.

The leading benchmark-severe failure classes on this run are `missed_frequency_reference` and `unknown_vs_no_reference` (22 scored misses each). These are the first prompt or verifier targets; lower-tier metric wins should not hide them.

Cluster-format errors account for 21 scored misses, split between incomplete cluster labels (invalid), cluster structure swaps, and cluster collapsed to simple rates.

There are 24 **pragmatic-only** successes: same coarse bucket (infrequent vs frequent vs unknown vs no information) but wrong monthly value and Purist bin. These are clinically misleading if only Pragmatic accuracy is reported.

Purist-without-monthly cases: 17; pragmatic-without-monthly: 41. These arise when different labels land in the same bin but convert to different seizures/month.

Outside scored metrics: 11 abstentions/null outputs and 7 schema-invalid labels (mostly incomplete cluster surfaces and unsupported per-hour rates). These are excluded from the 281-record denominator but are full failures operationally.

## Record index

Full per-record rows are in the companion `records.jsonl` in the run `analysis/` folder.

| record_id | status | norm | mo | pur | prag | failure_class | gold | predicted |
| --- | --- | :---: | :---: | :---: | :---: | --- | --- | --- |
| gan_10003 | invalid | - | - | - | - | invalid_predicted_label | 1 cluster per week, multiple per cluster | 1 cluster per week |
| gan_10031 | scored | N | N | N | N | cluster_collapsed_to_rate | 1 cluster per week, multiple per cluster | no seizure frequency reference |
| gan_10047 | scored | N | N | N | N | cluster_semantic_mismatch | 2 cluster per 3 month, multiple per cluster | 2 cluster per 3 month, 1 per cluster |
| gan_10052 | invalid | - | - | - | - | invalid_predicted_label | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month |
| gan_10074 | scored | N | N | Y | Y | cluster_semantic_mismatch | 5 cluster per month, multiple per cluster | 5 cluster per month, 2 to 3 per cluster |
| gan_10292 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_10398 | scored | N | N | Y | Y | cluster_semantic_mismatch | 1 cluster per week, 2 per cluster | 2 cluster per week, 2 per cluster |
| gan_10410 | invalid | - | - | - | - | invalid_predicted_label | 1 cluster per week, 3 to 4 per cluster | 3 to 4 cluster per week |
| gan_10434 | scored | N | N | N | Y | cluster_semantic_mismatch | multiple cluster per week, 2 to 3 per cluster | 1 cluster per week, 2 to 3 per cluster |
| gan_10447 | invalid | - | - | - | - | abstention_or_missing_value | unknown | None |
| gan_10509 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_10542 | scored | N | N | N | N | unknown_cluster_vs_no_reference | unknown, 2 to 4 per cluster | no seizure frequency reference |
| gan_10553 | scored | N | N | N | N | unknown_cluster_vs_no_reference | unknown, 2 to 3 per cluster | no seizure frequency reference |
| gan_10583 | scored | N | Y | Y | Y | cluster_collapsed_to_rate | unknown, 2 to 3 per cluster | unknown |
| gan_10618 | scored | N | N | N | N | unknown_cluster_vs_no_reference | unknown, 4 to 6 per cluster | no seizure frequency reference |
| gan_10673 | scored | N | N | N | N | cluster_collapsed_to_rate | 1 cluster per month, multiple per cluster | no seizure frequency reference |
| gan_1070 | scored | Y | Y | Y | Y | all_metrics_match | 3 to 4 per week | 3 to 4 per week |
| gan_10751 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_10862 | invalid | - | - | - | - | invalid_predicted_label | 1 cluster per week, multiple per cluster | 1 cluster per week |
| gan_10884 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster |
| gan_10984 | scored | N | N | N | Y | cluster_collapsed_to_rate | 3 cluster per month, 3 to 4 per cluster | 3 per month |
| gan_10993 | scored | N | N | Y | Y | cluster_semantic_mismatch | 2 cluster per month, 2 to 4 per cluster | 2 to 4 cluster per month, 2 to 4 per cluster |
| gan_10996 | scored | N | N | N | Y | cluster_collapsed_to_rate | 1 to 2 cluster per month, 4 per cluster | 1 to 2 per month |
| gan_11035 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per 3 month, 1 per cluster | 1 cluster per 3 month, 1 per cluster |
| gan_11044 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per 3 month, 2 to 4 per cluster | 1 cluster per 3 month, 2 to 4 per cluster |
| gan_11196 | scored | Y | Y | Y | Y | all_metrics_match | 3 cluster per month, 5 per cluster | 3 cluster per month, 5 per cluster |
| gan_11207 | scored | Y | Y | Y | Y | all_metrics_match | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster |
| gan_11216 | scored | N | N | N | N | unknown_vs_seizure_free | unknown | seizure free for 4 month |
| gan_11221 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_11259 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_11380 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_11399 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_11408 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_11411 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_11434 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_115 | scored | Y | Y | Y | Y | all_metrics_match | 7 to 8 per month | 7 to 8 per month |
| gan_11706 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_11733 | invalid | - | - | - | - | abstention_or_missing_value | no seizure frequency reference | None |
| gan_11734 | invalid | - | - | - | - | abstention_or_missing_value | no seizure frequency reference | None |
| gan_11748 | invalid | - | - | - | - | abstention_or_missing_value | no seizure frequency reference | None |
| gan_11763 | invalid | - | - | - | - | abstention_or_missing_value | no seizure frequency reference | None |
| gan_11804 | invalid | - | - | - | - | abstention_or_missing_value | no seizure frequency reference | None |
| gan_11841 | invalid | - | - | - | - | abstention_or_missing_value | no seizure frequency reference | None |
| gan_11874 | invalid | - | - | - | - | abstention_or_missing_value | no seizure frequency reference | None |
| gan_12130 | scored | N | N | N | N | frequent_undercalled | multiple per week | 3 per year |
| gan_12145 | scored | Y | Y | Y | Y | all_metrics_match | multiple per week | multiple per week |
| gan_12218 | scored | Y | Y | Y | Y | all_metrics_match | 1 per day | 1 per day |
| gan_12246 | scored | Y | Y | Y | Y | all_metrics_match | 1 to 2 per day | 1 to 2 per day |
| gan_12296 | scored | Y | Y | Y | Y | all_metrics_match | 3 to 4 per day | 3 to 4 per day |
| gan_12314 | scored | Y | Y | Y | Y | all_metrics_match | 3 per week | 3 per week |
| gan_12319 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per week | 2 to 3 per week |
| gan_12348 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per week | 2 to 3 per week |
| gan_12362 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 2 to 3 per day | 3 per day |
| gan_12438 | scored | Y | Y | Y | Y | all_metrics_match | 1 per day | 1 per day |
| gan_12465 | scored | Y | Y | Y | Y | all_metrics_match | 1 per day | 1 per day |
| gan_12562 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 1 per day | 4 per week |
| gan_12667 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 1 per day | 1 to 2 per month |
| gan_12679 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 1 per day | 1 to 2 per month |
| gan_128 | scored | Y | Y | Y | Y | all_metrics_match | 17 per month | 17 per month |
| gan_12810 | scored | N | N | N | N | frequent_undercalled | 5 per 2 month | 5 per year |
| gan_12823 | scored | N | N | N | N | frequent_undercalled | 9 per month | 9 per year |
| gan_12871 | scored | N | N | N | N | frequent_undercalled | 5 per 2 month | 5 per year |
| gan_12877 | scored | N | N | N | N | frequent_undercalled | 10 per 4 month | 10 per year |
| gan_12950 | scored | N | N | N | N | frequent_undercalled | 7 per 3 month | 7 per year |
| gan_13019 | scored | N | N | N | N | frequent_undercalled | 9 per 3 month | 9 per year |
| gan_13058 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 2 per 7 month | 1 per 3 month |
| gan_13123 | scored | Y | Y | Y | Y | all_metrics_match | 1 per year | 1 per year |
| gan_13149 | invalid | - | - | - | - | abstention_or_missing_value | 3 per year | None |
| gan_13190 | scored | N | N | N | N | missed_frequency_reference | 1 per 5 month | no seizure frequency reference |
| gan_13290 | scored | N | N | N | N | frequent_overcalled | 4 per 6 month | 2 per week |
| gan_13376 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 2 year | seizure free for 2 year |
| gan_13416 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | seizure free for multiple year | seizure free for 6 month |
| gan_13450 | scored | N | Y | Y | Y | missed_frequency_reference | seizure free for 1 year | no seizure frequency reference |
| gan_13487 | scored | N | Y | Y | Y | missed_frequency_reference | seizure free for multiple year | no seizure frequency reference |
| gan_1357 | scored | N | N | N | N | missed_frequency_reference | 1 per day | no seizure frequency reference |
| gan_13574 | scored | N | Y | Y | Y | missed_frequency_reference | seizure free for multiple year | no seizure frequency reference |
| gan_13595 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | seizure free for multiple year | seizure free for years |
| gan_13598 | scored | N | Y | Y | Y | missed_frequency_reference | seizure free for multiple year | no seizure frequency reference |
| gan_13993 | scored | N | N | N | N | unknown_as_high_rate | unknown | 2 to 3 per month |
| gan_14002 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_14025 | scored | N | N | N | N | unknown_as_high_rate | unknown | 2 per 6 week |
| gan_14036 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_14040 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_14076 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_14081 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_14092 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_14137 | scored | N | N | N | N | unknown_as_high_rate | unknown | 3 to 4 per month |
| gan_14146 | scored | N | N | N | N | unknown_as_high_rate | unknown | 3 per 2 month |
| gan_14214 | scored | N | N | N | N | missed_frequency_reference | 2 to 4 per month | no seizure frequency reference |
| gan_14250 | scored | N | N | N | N | missed_frequency_reference | 2 per month | no seizure frequency reference |
| gan_14271 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 2 to 3 per month | 2 to 3 per week |
| gan_14354 | scored | N | N | N | N | missed_frequency_reference | 2 to 4 per 3 month | no seizure frequency reference |
| gan_14390 | scored | N | N | N | N | other_semantic_mismatch | 2 per 3 month | seizure free for 3 month |
| gan_14485 | scored | N | N | N | N | missed_frequency_reference | 2 per 3 month | no seizure frequency reference |
| gan_14562 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 3 per 6 month | 3 per year |
| gan_14628 | scored | N | N | N | N | missed_frequency_reference | 2 per 2 month | no seizure frequency reference |
| gan_1463 | scored | Y | Y | Y | Y | all_metrics_match | 3 per month | 3 per month |
| gan_14655 | scored | N | N | N | N | missed_frequency_reference | 2 per 2 month | no seizure frequency reference |
| gan_14689 | scored | N | N | N | N | missed_frequency_reference | 3 per 2 month | no seizure frequency reference |
| gan_14748 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 2 per 3 month | 2 per year |
| gan_14792 | scored | N | N | N | N | missed_frequency_reference | 1 per month | no seizure frequency reference |
| gan_14821 | scored | N | N | N | N | other_semantic_mismatch | 1 per month | seizure free for 3 week |
| gan_1486 | scored | Y | Y | Y | Y | all_metrics_match | 3 per month | 3 per month |
| gan_14881 | scored | N | N | N | N | missed_frequency_reference | 1 per month | no seizure frequency reference |
| gan_14965 | scored | N | N | N | N | missed_frequency_reference | 1 per 3 month | no seizure frequency reference |
| gan_1497 | scored | Y | Y | Y | Y | all_metrics_match | 3 per month | 3 per month |
| gan_14973 | scored | N | N | N | N | missed_frequency_reference | 1 per month | no seizure frequency reference |
| gan_15127 | scored | N | N | N | N | frequent_overcalled | 5 per 13 month | 4 per month |
| gan_15129 | scored | Y | Y | Y | Y | all_metrics_match | 4 per 15 month | 4 per 15 month |
| gan_15168 | scored | N | N | N | N | missed_frequency_reference | multiple per 15 month | no seizure frequency reference |
| gan_15193 | scored | N | N | N | N | missed_frequency_reference | multiple per 13 month | no seizure frequency reference |
| gan_15240 | scored | N | N | N | N | cluster_collapsed_to_rate | multiple cluster per 12 month, multiple per cluster | no seizure frequency reference |
| gan_15255 | scored | N | N | N | N | cluster_collapsed_to_rate | multiple cluster per 15 month, multiple per cluster | no seizure frequency reference |
| gan_15302 | scored | N | N | N | N | missed_frequency_reference | 1 to 2 per 14 month | no seizure frequency reference |
| gan_15306 | scored | N | N | N | N | missed_frequency_reference | 2 to 3 per 15 month | no seizure frequency reference |
| gan_15404 | scored | N | N | N | N | cluster_semantic_mismatch | 1 cluster per 4 month, 3 to 4 per cluster | 3 to 4 cluster per month, 1 per cluster |
| gan_15442 | invalid | - | - | - | - | abstention_or_missing_value | 1 cluster per 4 day, 2 per cluster | None |
| gan_15513 | scored | N | N | N | Y | cluster_collapsed_to_rate | 1 cluster per 4 to 5 day, 2 to 3 per cluster | 2 to 3 per day |
| gan_15639 | scored | Y | Y | Y | Y | all_metrics_match | 2 per week | 2 per week |
| gan_15737 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per week | 2 to 3 per week |
| gan_15771 | scored | Y | Y | Y | Y | all_metrics_match | 3 per week | 3 per week |
| gan_15783 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per week | 2 to 3 per week |
| gan_1584 | scored | Y | Y | Y | Y | all_metrics_match | 11 per month | 11 per month |
| gan_15847 | scored | Y | Y | Y | Y | all_metrics_match | 6 per week | 6 per week |
| gan_15876 | scored | Y | Y | Y | Y | all_metrics_match | 6 per week | 6 per week |
| gan_15923 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 8 per 2 month | 7 per month |
| gan_15982 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 9 per 2 month | 8 per month |
| gan_15997 | scored | N | N | N | N | frequent_undercalled | 10 per 3 month | 1 per month |
| gan_16041 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 9 per 3 month | 5 per month |
| gan_16251 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 14 per 4 month | 7 per month |
| gan_16335 | scored | Y | Y | Y | Y | all_metrics_match | 7 per 3 month | 7 per 3 month |
| gan_1640 | scored | Y | Y | Y | Y | all_metrics_match | 5 per week | 5 per week |
| gan_16408 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 3 day | 1 per 3 day |
| gan_16422 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 1 per 2 to 3 day | 1 per day |
| gan_16523 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | 1 per 5 day | 1 cluster per 5 day, 1 per cluster |
| gan_16529 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 5 day | 1 per 5 day |
| gan_16574 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | 1 per 4 day | 1 cluster per 4 days, 1 per cluster |
| gan_16645 | scored | N | N | N | N | missed_frequency_reference | 5 per 7 month | no seizure frequency reference |
| gan_16750 | scored | N | N | N | N | missed_frequency_reference | 6 per 7 month | no seizure frequency reference |
| gan_16753 | scored | N | N | N | N | frequent_undercalled | 19 per 6 month | 1 per month |
| gan_16772 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 9 per 5 month | 9 per month |
| gan_16780 | scored | N | N | N | N | missed_frequency_reference | 3 per 7 month | no seizure frequency reference |
| gan_16825 | scored | N | N | N | N | missed_frequency_reference | 10 per 6 month | no seizure frequency reference |
| gan_16883 | scored | N | N | N | N | frequent_undercalled | 4 per 3 month | 3 per 3 month |
| gan_16938 | scored | N | N | N | N | frequent_undercalled | 2 per week | 2 per 2 month |
| gan_1694 | scored | N | Y | Y | Y | cluster_collapsed_to_rate | 1 cluster per 2 week, 3 per cluster | 3 per 2 week |
| gan_16947 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 2 per week | 4 per 2 month |
| gan_16964 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 2 per week | 4 to 5 per 2 month |
| gan_16991 | scored | Y | Y | Y | Y | all_metrics_match | multiple per month | multiple per month |
| gan_17 | scored | Y | Y | Y | Y | all_metrics_match | 2 per day | 2 per day |
| gan_17006 | scored | Y | Y | Y | Y | all_metrics_match | 2 per week | 2 per week |
| gan_17239 | scored | Y | Y | Y | Y | all_metrics_match | 4 per week | 4 per week |
| gan_17279 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 4 to 5 week | 1 per 4 to 5 week |
| gan_17287 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 1 per 1 to 2 day | 1 per day |
| gan_1794 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 8 per 2 month | 6 per 2 month |
| gan_180 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 1 per 7 day | 1 per week |
| gan_182 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 2 day | 1 per 2 day |
| gan_1883 | scored | Y | Y | Y | Y | all_metrics_match | 4 per 3 month | 4 per 3 month |
| gan_1914 | scored | Y | Y | Y | Y | all_metrics_match | 7 per 3 month | 7 per 3 month |
| gan_198 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 1 per 4 week | 1 per month |
| gan_2135 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_22 | scored | Y | Y | Y | Y | all_metrics_match | 3 per day | 3 per day |
| gan_2226 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 3 to 10 per 2 week | 3 to 10 per week |
| gan_2262 | scored | Y | Y | Y | Y | all_metrics_match | 7 to 9 per 3 week | 7 to 9 per 3 week |
| gan_234 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 2 month | 1 per 2 month |
| gan_2354 | scored | Y | Y | Y | Y | all_metrics_match | 6 to 7 per week | 6 to 7 per week |
| gan_2366 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 4 per year | 2 to 4 per year |
| gan_2369 | scored | Y | Y | Y | Y | all_metrics_match | 3 to 4 per month | 3 to 4 per month |
| gan_243 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 4 month | 1 per 4 month |
| gan_2456 | scored | Y | Y | Y | Y | all_metrics_match | 6 to 7 per 2 week | 6 to 7 per 2 week |
| gan_2486 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per 3 month | 2 to 3 per 3 month |
| gan_2487 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per 3 month | 2 to 3 per 3 month |
| gan_2513 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 2 to 3 per 2 week | 2 to 3 per week |
| gan_2549 | scored | Y | Y | Y | Y | all_metrics_match | 7 to 8 per 2 month | 7 to 8 per 2 month |
| gan_2609 | scored | Y | Y | Y | Y | all_metrics_match | 1 per day | 1 per day |
| gan_2652 | scored | Y | Y | Y | Y | all_metrics_match | 1 per day | 1 per day |
| gan_2725 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 1 per 2 week | 1 per week |
| gan_2740 | scored | Y | Y | Y | Y | all_metrics_match | 1 per month | 1 per month |
| gan_2781 | scored | Y | Y | Y | Y | all_metrics_match | 1 per week | 1 per week |
| gan_2795 | scored | Y | Y | Y | Y | all_metrics_match | 1 per week | 1 per week |
| gan_2824 | scored | Y | Y | Y | Y | all_metrics_match | 1 per day | 1 per day |
| gan_3015 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | seizure free for 12 month | seizure free for 1 year |
| gan_3095 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 12 month | seizure free for 12 month |
| gan_31 | scored | Y | Y | Y | Y | all_metrics_match | 4 per day | 4 per day |
| gan_3102 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 14 month | seizure free for 14 month |
| gan_3113 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 14 month | seizure free for 14 month |
| gan_3118 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | seizure free for multiple month | seizure free for 12 month |
| gan_3225 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per month, 3 to 10 per cluster | 1 cluster per month, 3 to 10 per cluster |
| gan_3246 | scored | Y | Y | Y | Y | all_metrics_match | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster |
| gan_3261 | scored | Y | Y | Y | Y | all_metrics_match | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster |
| gan_3291 | scored | Y | Y | Y | Y | all_metrics_match | 9 per month | 9 per month |
| gan_3300 | scored | Y | Y | Y | Y | all_metrics_match | 9 per month | 9 per month |
| gan_3325 | scored | Y | Y | Y | Y | all_metrics_match | 3 per week | 3 per week |
| gan_3329 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per day | 2 to 3 per day |
| gan_3340 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per month | 2 to 3 per month |
| gan_3355 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | 1 per 3 month | 2 per 6 month |
| gan_338 | scored | N | N | N | N | other_semantic_mismatch | multiple per month | unknown |
| gan_3452 | scored | Y | Y | Y | Y | all_metrics_match | 6 to 8 per month | 6 to 8 per month |
| gan_3512 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_3623 | scored | Y | Y | Y | Y | all_metrics_match | 7 per week | 7 per week |
| gan_3630 | scored | Y | Y | Y | Y | all_metrics_match | 7 per week | 7 per week |
| gan_3692 | scored | Y | Y | Y | Y | all_metrics_match | 9 per week | 9 per week |
| gan_3747 | scored | Y | Y | Y | Y | all_metrics_match | 3 per day | 3 per day |
| gan_3791 | scored | Y | Y | Y | Y | all_metrics_match | 10 per year | 10 per year |
| gan_3864 | scored | Y | Y | Y | Y | all_metrics_match | 3 per day | 3 per day |
| gan_3867 | scored | Y | Y | Y | Y | all_metrics_match | 3 per day | 3 per day |
| gan_4011 | scored | Y | Y | Y | Y | all_metrics_match | 1 per month | 1 per month |
| gan_4100 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 1 per 2 to 3 week | 1 per 2 week |
| gan_4113 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 1 per 1 to 2 day | 1 per day |
| gan_4378 | scored | N | N | N | N | frequent_undercalled | 3 per 2 month | 3 per year |
| gan_4591 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 5 month | 1 per 5 month |
| gan_4597 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 3 week | 1 per 3 week |
| gan_4602 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 7 to 10 day | 1 per 7 to 10 days |
| gan_467 | scored | Y | Y | Y | Y | all_metrics_match | 9 per month | 9 per month |
| gan_4700 | invalid | - | - | - | - | invalid_predicted_label | multiple per day | 4 per hour |
| gan_4702 | invalid | - | - | - | - | invalid_predicted_label | multiple per day | 4 per hour |
| gan_4709 | invalid | - | - | - | - | invalid_predicted_label | multiple per day | 6 per hour |
| gan_4831 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | seizure free for multiple month | seizure free for 6 month |
| gan_4919 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 2 year | seizure free for 2 year |
| gan_4956 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 7 month | seizure free for 7 month |
| gan_4992 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 11 month | seizure free for 11 month |
| gan_4996 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | seizure free for 16 month | seizure free for 1 year |
| gan_5082 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | seizure free for multiple month | seizure free for 6 month |
| gan_5092 | scored | N | Y | Y | Y | missed_frequency_reference | seizure free for multiple month | no seizure frequency reference |
| gan_5197 | scored | N | Y | Y | Y | missed_frequency_reference | seizure free for multiple month | no seizure frequency reference |
| gan_531 | scored | Y | Y | Y | Y | all_metrics_match | 12 to 30 per 3 month | 12 to 30 per 3 month |
| gan_5351 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 18 month | seizure free for 18 month |
| gan_536 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 2 day | 1 per 2 day |
| gan_5379 | scored | N | N | N | N | other_semantic_mismatch | seizure free for multiple month | 1 per 6 month |
| gan_5551 | scored | Y | Y | Y | Y | all_metrics_match | multiple per day | multiple per day |
| gan_5653 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 2 day | 1 per 2 day |
| gan_5682 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 4 per month | 2 to 4 per month |
| gan_5837 | scored | N | N | Y | Y | cluster_collapsed_to_rate | 2 cluster per 3 week, multiple per cluster | 3 per 3 week |
| gan_5866 | scored | Y | Y | Y | Y | all_metrics_match | 4 per 6 week | 4 per 6 weeks |
| gan_5954 | scored | Y | Y | Y | Y | all_metrics_match | 2 per week | 2 per week |
| gan_5974 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_5976 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_5977 | invalid | - | - | - | - | abstention_or_missing_value | unknown | None |
| gan_6029 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_6077 | scored | N | N | N | N | unknown_as_quantified_rate | unknown | 1 per 8 month |
| gan_6094 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 3 per month | 5 cluster per month, 1 per cluster |
| gan_6131 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_6153 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 9 per month | 3 per week |
| gan_6296 | scored | Y | Y | Y | Y | all_metrics_match | 3 per 4 month | 3 per 4 month |
| gan_6387 | scored | N | N | N | N | unknown_as_quantified_rate | unknown | 2 per 6 month |
| gan_6509 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | 1 per week | 2 per 2 week |
| gan_6532 | scored | N | N | N | N | unknown_cluster_vs_no_reference | unknown, multiple per cluster | no seizure frequency reference |
| gan_6607 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_6624 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_6661 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | 0.5 per week | 3 per 6 weeks |
| gan_6684 | scored | Y | Y | Y | Y | all_metrics_match | 3 per 4 month | 3 per 4 month |
| gan_6763 | scored | Y | Y | Y | Y | all_metrics_match | 1 per week | 1 per week |
| gan_6836 | scored | Y | Y | Y | Y | all_metrics_match | 1 per week | 1 per week |
| gan_6987 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_714 | scored | Y | Y | Y | Y | all_metrics_match | 2 per day | 2 per day |
| gan_7290 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_731 | scored | Y | Y | Y | Y | all_metrics_match | 1 per day | 1 per day |
| gan_7316 | scored | Y | Y | Y | Y | all_metrics_match | 1 to 2 per month | 1 to 2 per month |
| gan_7341 | scored | N | N | N | N | unknown_as_high_rate | unknown | 2 per month |
| gan_7420 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 1 to 2 per 2 week | 1 to 2 per week |
| gan_7431 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 1 per month | 2 per 8 weeks |
| gan_744 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | multiple per week | 5 per week |
| gan_750 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | multiple per week | 1 per day |
| gan_7573 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 2 week | 1 per 2 week |
| gan_7783 | scored | N | Y | Y | Y | missed_frequency_reference | seizure free for multiple month | no seizure frequency reference |
| gan_7818 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 2 year | seizure free for 2 year |
| gan_7872 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | seizure free for multiple month | seizure free for 6 month |
| gan_7882 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 6 month | seizure free for 6 month |
| gan_7884 | scored | N | Y | Y | Y | missed_frequency_reference | seizure free for multiple month | no seizure frequency reference |
| gan_7894 | scored | N | Y | Y | Y | missed_frequency_reference | seizure free for multiple year | no seizure frequency reference |
| gan_8002 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 1 per 6 to 8 week | 1 per 6 week |
| gan_804 | scored | Y | Y | Y | Y | all_metrics_match | 1 per month | 1 per month |
| gan_8113 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 14 month | seizure free for 14 month |
| gan_8116 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 12 month | seizure free for 12 month |
| gan_8160 | scored | N | Y | Y | Y | missed_frequency_reference | seizure free for multiple month | no seizure frequency reference |
| gan_8203 | scored | N | Y | Y | Y | missed_frequency_reference | seizure free for multiple month | no seizure frequency reference |
| gan_8224 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | seizure free for multiple month | seizure free for 3 month |
| gan_8264 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 4 month | seizure free for 4 month |
| gan_8474 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | seizure free for multiple month | seizure free for 6 month |
| gan_848 | scored | Y | Y | Y | Y | all_metrics_match | 1 per year | 1 per year |
| gan_8564 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 6 month | seizure free for 6 month |
| gan_8577 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | seizure free for multiple month | seizure free for 18 month |
| gan_8645 | scored | N | Y | Y | Y | missed_frequency_reference | seizure free for multiple month | no seizure frequency reference |
| gan_8723 | scored | N | Y | Y | Y | missed_frequency_reference | seizure free for multiple month | no seizure frequency reference |
| gan_8844 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 15 month | seizure free for 15 month |
| gan_8852 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 8 month | seizure free for 8 month |
| gan_8858 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | seizure free for multiple month | seizure free for 15 month |
| gan_8893 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | seizure free for multiple month | seizure free for 4 month |
| gan_9002 | scored | Y | Y | Y | Y | all_metrics_match | 7 per year | 7 per year |
| gan_9063 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 8 month | seizure free for 8 month |
| gan_9109 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_9179 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | seizure free for multiple month | seizure free for 2 month |
| gan_9279 | scored | Y | Y | Y | Y | all_metrics_match | 1 to 2 per week | 1 to 2 per week |
| gan_9365 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 2 day | 1 per 2 days |
| gan_9424 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 10 per 9 month | 1 per week |
| gan_9483 | scored | N | N | N | N | frequent_undercalled | 8 per 6 month | 1 per month |
| gan_9526 | scored | N | N | N | N | missed_frequency_reference | 4 per 8 month | no seizure frequency reference |
| gan_9566 | scored | N | N | N | N | unknown_as_high_rate | unknown | 1 to 2 per week |
| gan_9943 | scored | N | N | N | N | cluster_collapsed_to_rate | 1 cluster per 4 to 5 week, multiple per cluster | no seizure frequency reference |

## Second-pass raw-data assessment

I re-read the raw Gan JSON for representative failures, comparing each prediction against:

- primary gold: `check__Seizure Frequency Number.seizure_frequency_number[0]`
- primary evidence: `check__Seizure Frequency Number.seizure_frequency_number[1]`
- secondary reference: `check__Seizure Frequency Number.reference[0]`
- split metadata in `analysis/records.jsonl`

The core metric read is valid: the valid-prediction metric hierarchy is real for this run
(`normalized_label -> monthly_frequency -> purist_category -> pragmatic_category`), and the
benchmark-facing metrics remain monthly, Purist, and Pragmatic rather than normalized-label exact.
The 18 invalid or missing predictions should still be treated as operational failures even though
they are excluded from the 281-record valid denominator.

The main refinement is that several taxonomy names describe useful symptoms, not clean root causes.
For example, `missed_frequency_reference` contains benchmark-severe misses such as `1 per 5 month`
predicted as `no seizure frequency reference`, but it also contains seizure-free records predicted
as `no seizure frequency reference`; these lose normalized-label exact while preserving monthly,
Purist, and Pragmatic labels because both map to `0.0`. Similarly, `cluster_collapsed_to_rate`
includes the diagnostic surface case `unknown, 2 to 3 per cluster -> unknown`, which preserves all
benchmark-facing frequency categories but loses label-shape fidelity. These should not be
prioritized equally with Pragmatic-crossing semantic errors.

Hard-case/reference-disagreement records are not the main explanation for this run's misses. The
validation split has 39 hard cases; all 39 were scored, and their monthly accuracy was 26/39
(66.7%), compared with 131/242 (54.1%) for non-hard scored records. Hard cases still matter for
stratified reporting, but the current Qwen failure pattern is better explained by label-policy and
selection errors than by the audited primary/reference disagreement flag.

Raw examples support these root-cause groups:

- **Unknown vs no-reference boundary**: records like `gan_10509`, `gan_10751`, and `gan_11221`
  mention seizures but lack a Gan-quantifiable rate. Predicting `no seizure frequency reference`
  is semantically wrong because seizure activity is present; this crosses from `unknown` to
  `no_seizure_information`.
- **Temporal-window and highest-current-frequency errors**: records like `gan_12130` contain a
  rare generalized seizure count plus more frequent focal sensory events. The model selected the
  lower-rate seizure type (`3 per year`) instead of the highest current quantified frequency
  (`multiple per week`). Records like `gan_12810` and `gan_12823` show year-to-date denominator
  ambiguity where the dataset expects months elapsed since January, not a full-year denominator.
- **Cluster extraction errors**: incomplete outputs such as `1 cluster per week` are correctly
  invalid. Raw notes often state the missing per-cluster detail nearby (`number per cluster not
  documented`, `3 or 4 per cluster`, or `each cluster comprising brief episodes`). These are not
  deterministic postprocessing candidates unless the note is read; they belong in verifier/repair
  or prompt/example work.
- **Seizure-free vs no-reference label-shape errors**: several predictions collapse seizure-free
  labels to `no seizure frequency reference`. This is mostly a normalized-label fidelity problem
  under the current benchmark scorer, but it matters if the project later evaluates label-scheme
  reproduction or seizure-freedom duration.
- **Administrative/no-clinical-content abstention**: 12 validation records have `row_ok=false`; 5
  were scored correctly as `no seizure frequency reference`, and 7 abstained/null. These are good
  abstention-calibration tests: for Gan scoring, a no-clinical-content note still expects the
  explicit label `no seizure frequency reference`, not null.

## Fix-and-test action plan

### Ready: tighten benchmark-severe decision boundaries

- **Outcome**: Update the direct Gan S0 prompt/policy guidance so Qwen distinguishes
  `unknown` from `no seizure frequency reference`, uses the highest current quantified seizure-type
  frequency, and treats administrative/no-clinical-content notes as
  `no seizure frequency reference` rather than null.
- **Dependencies**: None; scorer semantics remain unchanged.
- **Parallelizable**: No, because this defines the shared extraction contract.
- **Validation**: Add prompt/contract tests in `tests/test_gan_s0_program.py`; dry-run the affected
  config; run a capped validation slice containing `gan_10509`, `gan_10751`, `gan_11221`,
  `gan_11733`, `gan_12130`, `gan_12810`, and `gan_12823`.
- **Notes**: Success should be measured first on monthly/Purist/Pragmatic improvements and reduced
  null outputs. Normalized-label exact is secondary.

### Ready: build a targeted regression slice

- **Outcome**: Create a deterministic review slice or fixture list for the recurrent raw-data
  patterns: unknown/no-reference, no-clinical-content, highest-current-frequency, year-to-date,
  incomplete cluster, cluster multiplier, short seizure-free threshold, and seizure-free
  label-shape preservation.
- **Dependencies**: None.
- **Parallelizable**: Yes.
- **Validation**: A script or test asserts the fixture record IDs remain present in
  `gan_2026_fixed_v1:validation` or documents any moved examples if the split changes.
- **Notes**: This should be small enough for fast local Qwen capped runs and hosted verifier checks.

### Ready: improve the analyzer taxonomy

- **Outcome**: Refine `scripts/analyze_gan_frequency_run.py` so action-oriented failure classes
  separate benchmark-severe errors from label-shape-only diagnostics. In particular, split
  seizure-free-to-no-reference monthly matches from true missed frequency references, and avoid
  classifying `unknown, N per cluster -> unknown` as a benchmark-severe cluster collapse.
- **Dependencies**: None.
- **Parallelizable**: Yes, but coordinate with any documentation updates that quote class counts.
- **Validation**: Add regression tests for representative rows and regenerate this analysis note
  from the same run to confirm metric counts remain unchanged while class labels become clearer.
- **Notes**: This is analysis/reporting only. Do not change `gan_frequency_deterministic_v1`
  scorer semantics.

### Backlog: evidence-aware verifier/repair for local Qwen

- **Outcome**: Add or adapt a lightweight verifier pass for local Qwen that reads the note and
  repairs only evidence-supported semantic failures: incomplete cluster labels, unknown/no-reference
  confusion, highest-current-frequency selection, and temporal denominator mistakes.
- **Dependencies**: Targeted regression slice and prompt-boundary pass.
- **Parallelizable**: After the shared contract is updated.
- **Validation**: Compare direct vs verify-repair on the targeted slice, then cap-25, then full
  validation. Report valid denominator and operational denominator (`299`) side by side.
- **Notes**: Do not deterministically infer missing cluster details in a postprocessor; this needs
  note-aware model verification or explicit deterministic retrieval plus verification.

### Backlog: stratified reporting refresh

- **Outcome**: Add reporting rows for `hard_case`, `row_ok`, gold pragmatic category, and
  operational failures so future notes make clear whether a change improves true benchmark errors
  or only normalized-label fidelity.
- **Dependencies**: Analyzer taxonomy cleanup.
- **Parallelizable**: After analyzer changes.
- **Validation**: Regenerated `summary.json` includes hard/non-hard and row_ok true/false
  denominators; metrics snapshot states valid-only and all-record operational rates.

## Recommended first pull

1. Build the targeted regression slice from the raw examples above.
2. Tighten the direct prompt/policy around unknown/no-reference, no-clinical-content nulls, highest
   current frequency, and year-to-date denominators.
3. Run the targeted slice before any full validation; only promote to cap-25/full validation if the
   changes reduce benchmark-severe misses without increasing invalid cluster or forbidden-unit
   outputs.
