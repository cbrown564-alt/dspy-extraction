# ExECT S1 Raw/Bridge/Prompt Split Audit

Date: 2026-05-28

## Scope

- Dataset: ExECTv2
- Split surfaces: validation cap-25, full validation, and pre-existing test holdout
- Fields: diagnosis and seizure type
- Scorer: `exect_field_family_deterministic_v1`
- Model calls: 0

## Stage Metrics

| Surface | Split | Repair policy | Micro F1 | Diagnosis F1 | Seizure-type F1 |
| --- | --- | --- | ---: | ---: | ---: |
| schema_raw_cap25 | exectv2_fixed_v1:validation | raw_no_benchmark_bridges | 67.7% | 51.0% | 62.0% |
| policy_raw_cap25 | exectv2_fixed_v1:validation | raw_no_benchmark_bridges | 72.8% | 71.4% | 56.3% |
| policy_post_bridge_cap25 | exectv2_fixed_v1:validation | artifact_benchmark_bridge_only | 95.8% | 97.6% | 95.4% |
| policy_raw_full_validation | exectv2_fixed_v1:validation | raw_no_benchmark_bridges | 68.6% | 61.5% | 57.4% |
| policy_post_bridge_full_validation | exectv2_fixed_v1:validation | artifact_benchmark_bridge_only | 92.3% | 93.8% | 90.5% |
| qwen_clean_validation | exectv2_fixed_v1:validation | post_prediction_clean_ladder_v1 | 85.9% | 95.1% | 74.2% |
| qwen_clean_test_holdout | exectv2_fixed_v1:test | post_prediction_clean_ladder_v1 | 71.8% | 66.7% | 52.2% |

## Field-F1 Deltas

| Contrast | Diagnosis | Seizure type | Interpretation |
| --- | ---: | ---: | --- |
| prompt_policy_raw_cap25 | +20.4 pp | -5.6 pp | v4.10 prompt policy without bridges vs schema-only raw cap-25. |
| bridge_cap25 | +26.1 pp | +39.0 pp | Post benchmark bridge effect on the v4.10 policy cap-25 surface. |
| bridge_full_validation | +32.3 pp | +33.1 pp | Post benchmark bridge effect on the full validation surface. |
| qwen_holdout_minus_validation | -28.5 pp | -22.1 pp | Qwen clean v2 test holdout minus Qwen clean v2 validation. |

## Bridge-Flagged Values

| Surface | Diagnosis | Seizure type |
| --- | ---: | ---: |
| policy_post_bridge_cap25 | 7 | 21 |
| policy_post_bridge_full_validation | 22 | 28 |
| qwen_clean_validation | 21 | 20 |
| qwen_clean_test_holdout | 17 | 17 |

## Residual Classes

| Surface | Extraction | Bridge | Policy | Specificity/collapse | Scope |
| --- | ---: | ---: | ---: | ---: | ---: |
| policy_post_bridge_full_validation | 1 | 5 | 2 | 1 | 2 |
| qwen_clean_validation | 3 | 6 | 7 | 1 | 1 |
| qwen_clean_test_holdout | 9 | 10 | 6 | 7 | 6 |

## Holdout Residual Sample

| Document | Field | Class | False positives | False negatives |
| --- | --- | --- | --- | --- |
| EA0007 | seizure_type | policy | focal seizures | - |
| EA0015 | diagnosis | extraction | epilepsy | - |
| EA0015 | seizure_type | extraction | - | epileptic attack |
| EA0020 | seizure_type | policy | generalized tonic clonic seizure, absence seizure | - |
| EA0033 | seizure_type | bridge | absence seizures | - |
| EA0039 | diagnosis | extraction | - | epilepsy |
| EA0049 | seizure_type | bridge | absence seizures | myoclonic seizures, generalized tonic clonic seizure |
| EA0056 | diagnosis | specificity_collapse | - | localisation related epilepsy, epilepsy |
| EA0056 | seizure_type | scope | focal aware seizures, focal motor seizures, focal to bilateral convulsive seizures | partial motor seizures, secondary generalized seizures |
| EA0058 | diagnosis | bridge | - | epilepsy |
| EA0060 | diagnosis | extraction | - | epilepsy |
| EA0060 | seizure_type | bridge | secondary | - |

## Interpretation

- Full-validation GPT S1 is near ceiling only after benchmark-policy bridges: diagnosis rises from 61.5% raw to 93.8% bridged, and seizure type rises from 57.4% to 90.5%.
- The full-validation bridge contribution remains large (+32.3 pp diagnosis, +33.1 pp seizure type), so raw extraction is not itself at ceiling.
- The Qwen clean v2 test holdout drops sharply relative to its validation anchor (-28.5 pp diagnosis, -22.1 pp seizure type), so S1 should be treated as validation-aligned rather than globally solved.
- Residuals should be worked family by family: diagnosis failures skew toward scope/specificity/extraction boundaries, while seizure-type failures retain policy and bridge-sensitive granularity problems.
- Decision: E2 supports keeping S1 as a strong validation anchor, but not as a near-ceiling mechanism claim until raw extraction and prompt-policy transfer are verified on holdout without using holdout for tuning.

## Caveats

- This audit reuses stored artifacts and makes no model calls.
- It does not change loader, scorer, split, or benchmark bridge semantics.
- Cap-25 prompt-policy deltas are diagnostic slice comparisons, not full-validation estimates.
- Test-holdout metrics are reported only from the pre-existing test-holdout run and must not be used for tuning.
- Medication is excluded from E2 because this card targets diagnosis and seizure-type causal attribution.
