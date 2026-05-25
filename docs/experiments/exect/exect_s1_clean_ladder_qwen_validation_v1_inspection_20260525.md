# ExECT S1 Clean-Ladder Qwen Validation v1 Inspection

Date: 2026-05-25

Comparison group: `exect_s1_clean_ladder_qwen_validation_v1`

## Decision

Promote `exect_s1_clean_ladder_v2_diagnosis_stable_full_qwen35b_ollama_20260525T103640Z` as the clean Qwen S1 ladder anchor.

Decision scope: `operational`. This freezes an S1 clean-ladder anchor for the Qwen ladder demonstration; it does not close broader S1 prompt-graph or optimizer mechanisms.

## Hypothesis

The prior Qwen ladder was not clean because S1 used the older v4.10 operational anchor while S2/S3 used clean-ladder guard stacks. A clean S1 anchor should combine the stable S1 diagnosis behavior from v4.10 with the stronger v4.11 seizure-type policy and S1-appropriate promoted annotated-medication guard.

## Runs

| Arm | Run | Config | Result |
| --- | --- | --- | --- |
| Baseline S1 v4.10 | `exect_s0_s1_validation_full_qwen35b_ollama_20260525T075445Z` | `configs/experiments/exect_s0_s1_validation_full_qwen35b_ollama.json` | 79.0% micro |
| S1 clean v1 | `exect_s1_clean_ladder_v1_full_qwen35b_ollama_20260525T103403Z` | `configs/experiments/exect_s1_clean_ladder_v1_full_qwen35b_ollama.json` | 84.3% micro |
| **S1 clean v2** | **`exect_s1_clean_ladder_v2_diagnosis_stable_full_qwen35b_ollama_20260525T103640Z`** | **`configs/experiments/exect_s1_clean_ladder_v2_diagnosis_stable_full_qwen35b_ollama.json`** | **85.9% micro** |

Cap gates:

| Arm | Cap run | Micro F1 | Diagnosis | Seizure type | Medication |
| --- | --- | ---: | ---: | ---: | ---: |
| S1 clean v1 | `exect_s1_clean_ladder_v1_cap25_qwen35b_ollama_20260525T103353Z` | 85.4% | 92.7% | 78.3% | 88.9% |
| S1 clean v2 | `exect_s1_clean_ladder_v2_diagnosis_stable_cap25_qwen35b_ollama_20260525T103629Z` | 86.1% | 95.2% | 78.3% | 88.9% |

## Full-Validation Metrics

| Rung / arm | Micro F1 | Precision | Recall | Diagnosis F1 | Seizure type F1 | Annotated medication F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S1 v4.10 Qwen | 79.0% | 79.3% | 78.7% | 95.1% | 55.7% | 89.1% |
| S1 clean v1 Qwen | 84.3% | 85.6% | 83.1% | 90.0% | 74.2% | 90.1% |
| **S1 clean v2 Qwen** | **85.9%** | **86.6%** | **85.3%** | **95.1%** | **74.2%** | **90.1%** |
| S2 clean Qwen | 84.4% | 82.9% | 86.0% | 93.8% | 70.5% | 93.8% |
| S3 clean Qwen | 75.3% | 72.1% | 78.8% | 86.1% | 72.3% | 86.8% |
| S4 Qwen | 67.5% | 60.6% | 76.1% | 88.3% | 76.3% | 80.4% |
| S5 v2b Qwen | 85.4% | 83.9% | 87.1% | 92.5% | 82.5% | 88.7% |

## Interpretation

S1 clean v2 restores the expected monotonic ladder relationship for the current Qwen validation evidence:

- S1 clean v2: 85.9% micro
- S2 clean: 84.4% micro
- S3 clean: 75.3% micro
- S4: 67.5% micro

It also edges above the optimized S5 v2b core-surface run (85.4% micro), but S5 remains a separate optimized surface rather than a simple breadth-only rung. S5 includes frequency-specific mechanisms and omits medication temporality, so it should be discussed as an optimized S5 core-field anchor, not as a pure schema-complexity ladder point.

The v1 result shows the v4.11 seizure policy was the main lift over v4.10. The v2 routing result shows the remaining S1 anomaly came from v4.11 diagnosis drift, not from schema breadth. Routing diagnosis from v4.10 recovers diagnosis F1 from 90.0% to 95.1% while preserving v4.11 seizure F1 at 74.2%.

## Taxonomy

- Dataset: `exect_v2`
- Clinical task family: diagnosis, seizure_type, medication
- Schema complexity: `exect_s1`
- Program architecture: `field_family_prompt_graph`
- Hybrid balance class: `H1_post_deterministic`
- Interleaving positions: `during`, `post`
- Varied factor: `implementation_variant`
- Comparison group: `exect_s1_clean_ladder_qwen_validation_v1`
- Outcome: promote operational S1 clean-ladder anchor

## Caveats

- This is fixed validation-split reporting, not published ExECTv2 Table 1 reproduction.
- The v2 arm uses two extraction calls per record. That improves quality but is less latency-efficient than monolithic S1.
- The full run reused previously executed prompt surfaces and completed from cache; latency should be reported from a cold rerun if runtime cost becomes a claim.
- Medication temporality is not benchmark-facing in S1 because ExECT prescription gold lacks a native temporality column.
- S1/S2/S3/S4 pooled micro values are useful for a scaling hypothesis demonstration, but each rung changes field-family support and should also be reported with per-family F1.

## Validation

- `uv run --extra dev pytest tests/test_exect_s0_s1_program.py tests/test_experiment_configs.py -q`
- `uv run python scripts/validate_experiment_taxonomy.py --errors-only`
- Dry runs for all four new S1 clean configs.
- Cap/full Qwen runs for v1 and v2 configs.
