# Gan S0 Error Analysis: gan_s0_qwen35b_verify_repair_regression_slice_guardrails

## Run

- Artifact directory: `runs\gan_s0_qwen35b_verify_repair_regression_slice_guardrails_20260519T155438Z`
- Split: `gan_2026_fixed_v1:validation`
- Analysis scope: `record_ids_filter`
- Records in split: 299
- Records analyzed: 14
- Valid scored predictions: 13
- Invalid or missing predictions: 1

## Metrics snapshot (valid predictions only)

| Metric | Accuracy | Correct | Denominator |
| --- | ---: | ---: | ---: |
| normalized_label | 46.2% | 6 | 13 |
| monthly_frequency | 46.2% | 6 | 13 |
| purist_category | 53.8% | 7 | 13 |
| pragmatic_category | 61.5% | 8 | 13 |

Benchmark-facing metrics are monthly frequency, Purist category, and Pragmatic category. Normalized-label exact is diagnostic format fidelity.

## Stratified operational reporting

- All-record denominator: 14 (valid scored: 13; invalid/missing: 1)
- Overall operational failure rate: 57.1% (8 failures)

| Stratum | All records | Valid scored | Operational failure rate | Monthly (valid only) |
| --- | ---: | ---: | ---: | ---: |
| hard_case=true | 0 | 0 | n/a | n/a |
| hard_case=false | 14 | 13 | 57.1% | 46.2% |
| row_ok=true | 12 | 11 | 58.3% | 45.5% |
| row_ok=false | 2 | 2 | 50.0% | 50.0% |
| gold_pragmatic=frequent | 6 | 5 | 50.0% | 60.0% |
| gold_pragmatic=infrequent | 4 | 4 | 75.0% | 25.0% |
| gold_pragmatic=no_seizure_information | 1 | 1 | 0.0% | 100.0% |
| gold_pragmatic=unknown | 3 | 3 | 66.7% | 33.3% |

## Do the four metrics move together?

Bit order in patterns is `normalized | monthly | purist | pragmatic` (1 = match).

| Pattern | Label | Count | Share |
| --- | --- | ---: | ---: |
| `1111` | all_four_match | 6 | 46.2% |
| `0000` | all_four_wrong | 5 | 38.5% |
| `0011` | purist_pragmatic_not_monthly | 1 | 7.7% |
| `0001` | pragmatic_only | 1 | 7.7% |

### Logical containment on this run

- Normalized exact (6 records): always co-occurs with monthly, Purist, and Pragmatic match.
- Monthly match (6 records): always implies Purist and Pragmatic; 6 also have normalized exact.
- Purist match (7 records): always implies Pragmatic; 6 also match monthly.
- Pragmatic-only wins (pattern `0001`): 1 records.
- Purist-without-monthly (pattern `0010`/`0011`): 0 + 1 records.

### Boundary cases

- **purist_bin_boundary_within_pragmatic**: 1
- **pragmatic_match_monthly_divergence**: 2
- **purist_match_monthly_divergence**: 1
- **monthly_match_label_surface_mismatch**: 0

## Holistic failure taxonomy

### Action tiers (scored misses)

Benchmark-severe classes should drive prompt or verifier work. Diagnostic-only classes preserve monthly/Purist/Pragmatic matches despite normalized-label mismatch.

| Action tier | Count |
| --- | ---: |
| benchmark_severe | 7 |

#### benchmark_severe

| Failure class | Count |
| --- | ---: |
| cluster_collapsed_to_rate | 1 |
| frequent_undercalled | 1 |
| missed_frequency_reference | 1 |
| other_semantic_mismatch | 1 |
| purist_bin_boundary_within_pragmatic | 1 |
| unknown_vs_no_reference | 1 |
| unknown_vs_seizure_free | 1 |

### Scored misses (normalized label wrong)

| Failure class | Count |
| --- | ---: |
| unknown_vs_no_reference | 1 |
| unknown_vs_seizure_free | 1 |
| frequent_undercalled | 1 |
| cluster_collapsed_to_rate | 1 |
| purist_bin_boundary_within_pragmatic | 1 |
| other_semantic_mismatch | 1 |
| missed_frequency_reference | 1 |

### Invalid / abstained / missing

| Failure class | Count |
| --- | ---: |
| invalid_predicted_label | 1 |

### Taxonomy grouped by which metric failed

#### Misses against **normalized_exact**

| Failure class | Count |
| --- | ---: |
| cluster_collapsed_to_rate | 1 |
| frequent_undercalled | 1 |
| missed_frequency_reference | 1 |
| other_semantic_mismatch | 1 |
| purist_bin_boundary_within_pragmatic | 1 |
| unknown_vs_no_reference | 1 |
| unknown_vs_seizure_free | 1 |

#### Misses against **monthly**

| Failure class | Count |
| --- | ---: |
| cluster_collapsed_to_rate | 1 |
| frequent_undercalled | 1 |
| missed_frequency_reference | 1 |
| other_semantic_mismatch | 1 |
| purist_bin_boundary_within_pragmatic | 1 |
| unknown_vs_no_reference | 1 |
| unknown_vs_seizure_free | 1 |

#### Misses against **purist**

| Failure class | Count |
| --- | ---: |
| frequent_undercalled | 1 |
| missed_frequency_reference | 1 |
| other_semantic_mismatch | 1 |
| purist_bin_boundary_within_pragmatic | 1 |
| unknown_vs_no_reference | 1 |
| unknown_vs_seizure_free | 1 |

#### Misses against **pragmatic**

| Failure class | Count |
| --- | ---: |
| frequent_undercalled | 1 |
| missed_frequency_reference | 1 |
| other_semantic_mismatch | 1 |
| unknown_vs_no_reference | 1 |
| unknown_vs_seizure_free | 1 |

## Interpretation

The four metrics form a strict hierarchy on valid predictions: normalized exact ⊂ monthly ⊂ Purist ⊂ Pragmatic. They do **not** always improve together in the sense that fixing one layer can leave coarser layers unchanged, but finer success never appears without coarser success.

The leading benchmark-severe failure classes on this run are `cluster_collapsed_to_rate`, `frequent_undercalled`, `missed_frequency_reference`, `other_semantic_mismatch`, `purist_bin_boundary_within_pragmatic`, `unknown_vs_no_reference`, `unknown_vs_seizure_free` (1 scored miss each). These are the first prompt or verifier targets; lower-tier metric wins should not hide them.

Cluster-format errors account for 1 scored misses, split between incomplete cluster labels (invalid), cluster structure swaps, and cluster collapsed to simple rates.

There are 1 **pragmatic-only** successes: same coarse bucket (infrequent vs frequent vs unknown vs no information) but wrong monthly value and Purist bin. These are clinically misleading if only Pragmatic accuracy is reported.

Purist-without-monthly cases: 1; pragmatic-without-monthly: 2. These arise when different labels land in the same bin but convert to different seizures/month.

Outside scored metrics: 0 abstentions/null outputs and 1 schema-invalid labels (mostly incomplete cluster surfaces and unsupported per-hour rates). These are excluded from the 281-record denominator but are full failures operationally.

## Record index

Full per-record rows are in the companion `records.jsonl` in the run `analysis/` folder.

| record_id | status | norm | mo | pur | prag | failure_class | gold | predicted |
| --- | --- | :---: | :---: | :---: | :---: | --- | --- | --- |
| gan_10509 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_10751 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_11221 | scored | N | N | N | N | unknown_vs_seizure_free | unknown | seizure free for 4 month |
| gan_11733 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_12130 | scored | Y | Y | Y | Y | all_metrics_match | multiple per week | multiple per week |
| gan_12810 | scored | Y | Y | Y | Y | all_metrics_match | 5 per 2 month | 5 per 2 month |
| gan_12823 | scored | N | N | N | N | frequent_undercalled | 9 per month | 9 per 12 month |
| gan_10003 | scored | N | N | Y | Y | cluster_collapsed_to_rate | 1 cluster per week, multiple per cluster | 1 per week |
| gan_10052 | invalid | - | - | - | - | invalid_predicted_label | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month |
| gan_10410 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster |
| gan_13123 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 1 per year | 1 per 3 month |
| gan_14485 | scored | N | N | N | N | other_semantic_mismatch | 2 per 3 month | seizure free for 1 month |
| gan_14881 | scored | N | N | N | N | missed_frequency_reference | 1 per month | no seizure frequency reference |
| gan_15306 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per 15 month | 2 to 3 per 15 month |
