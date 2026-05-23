# Model Suite Qwen 3.6:27b Full Validation v1 - Inspection

Date: 2026-05-23  
Comparison group: `model_suite_frozen_architecture_v1`  
Preregistration: `docs/experiments/synthesis/model_suite_frozen_architecture_v1_preregistration_20260522.md`  
Ladder log: `runs/overnight_logs/qwen27b_model_suite_ladder_20260522_235509.log`  
Ladder summary: `runs/overnight_logs/qwen27b_model_suite_ladder_20260522_235509.summary.txt`  
decision_scope: **arm** (model-comparison evidence only; not mechanism closure or operational promotion)

## Purpose

Complete the remaining local Qwen3.6:27b column on the three frozen comparison surfaces: ExECT S1, ExECT S4, and Gan S0 F0. This closes the planned frozen model-suite ladder. The only varied factor is `model_track`; split, scorer, program surface, and frozen prompt/policy variants remain fixed to the preregistered suite controls.

## Run artifacts

| Surface | Run ID | Records | Config | Outcome |
| --- | --- | ---: | --- | --- |
| ExECT S1 full | `exect_s0_s1_validation_full_qwen27b_ollama_20260522T225513Z` | 40 | `configs/experiments/exect_s0_s1_validation_full_qwen27b_ollama.json` | Pass |
| ExECT S4 full | `exect_s4_validation_full_qwen27b_ollama_20260523T071044Z` | 40 | `configs/experiments/exect_s4_validation_full_qwen27b_ollama.json` | Pass |
| Gan S0 F0 full | `gan_s0_expanded_builders_prose_full_validation_qwen27b_ollama_20260523T133604Z` | 299 | `configs/experiments/gan_s0_expanded_builders_prose_full_validation_qwen27b_ollama.json` | Pass |

Queue result: **3/3 succeeded**, 0 failed.

## Results

| Surface | GPT 4.1-mini anchor | Qwen 3.6:35b | Qwen 3.5:9b | Qwen 3.6:27b | Read |
| --- | ---: | ---: | ---: | ---: | --- |
| ExECT S1 micro | 92.3% | 79.0% | 79.4% | **85.7%** | Best local S1 track, still 6.6pp below GPT anchor |
| ExECT S4 micro | 65.5% | 67.5% | 64.0% | **69.3%** | Best current S4 suite score; per-family caveats remain essential |
| Gan F0 monthly | 68.1% | 64.4% | 65.9% | **74.9%** | Near top of Gan F0 suite; tied with GPT 5.5 after rounding and 0.4pp below Gemini 3 Flash |

## Surface details

### ExECT S1

| Metric | Value |
| --- | ---: |
| Micro F1 | **85.7%** |
| Precision / recall | 87.7% / 83.8% |
| Diagnosis F1 | 92.3% |
| Seizure type F1 | 78.4% |
| Annotated medication F1 | 87.9% |
| Evidence quote support | 100.0% |
| Runtime | 743.1 s/record |
| Residency | 71%/29% CPU/GPU, context 65536 |

### ExECT S4

| Metric | Value |
| --- | ---: |
| Micro F1 | **69.3%** |
| Precision / recall | 63.6% / 76.1% |
| Evidence quote support | 95.2% |
| Runtime | 577.9 s/record |
| Residency | 71%/29% CPU/GPU, context 65536 |

Per-family F1:

| Family | F1 |
| --- | ---: |
| `investigation` | 94.7% |
| `diagnosis` | 90.0% |
| `seizure_type` | 80.4% |
| `annotated_medication` | 79.6% |
| `medication_temporality` | 71.0% |
| `comorbidity` | 62.1% |
| `seizure_frequency` | 56.0% |
| `birth_history` | 22.2% |
| `epilepsy_cause` | 20.0% |
| `onset` | 0.0% |
| `when_diagnosed` | 0.0% |

### Gan S0 F0

| Metric | Value |
| --- | ---: |
| Monthly frequency accuracy | **74.9%** |
| 95% CI, monthly | 69.9-79.6% |
| Pragmatic category accuracy | 80.6% |
| Purist category accuracy | 77.9% |
| Normalized-label exact | 64.5% |
| Schema validity | 100.0% |
| Evidence quote support | 100.0% |
| Runtime | 32.4 s/record |
| Residency | 68%/32% CPU/GPU, context 4096 |

## Interpretation

Qwen3.6:27b completes the frozen local scaling picture and is the strongest local track overall. It does not recover the GPT 4.1-mini S1 anchor, but it substantially improves over 35b and 9b on S1. It also leads the current S4 table by pooled micro F1 and reaches the top Gan F0 cluster, essentially tied with GPT 5.5 and just below Gemini 3 Flash.

The local scaling story is therefore not monotonic by parameter count. Qwen 27b is better than 35b on all three frozen surfaces in this suite, despite the 35b model being larger. The likely explanation is an interaction among model variant, quantization/runtime behavior, prompt compliance, and context/residency settings, not raw scale alone.

Operationally, the latency is the major constraint. ExECT S1 and S4 took roughly 10-12 minutes per record with partial CPU offload, while Gan F0 took about 32 seconds per record. That makes Qwen 27b useful as a local comparison/profiling track, but not a default extraction path without a separate throughput decision.

## Caveats

- These are validation-suite diagnostics, not published benchmark reproduction.
- ExECT S1/S4 use the fixed validation subset of 40 predicted records under deterministic field-family scorers.
- Gan F0 uses `gan_frequency_deterministic_v1`; `seizure_frequency_number[0]` is the primary gold label and evidence support is diagnostic.
- S4 pooled micro F1 should not be read without the per-family profile. Sparse families such as `onset`, `when_diagnosed`, `epilepsy_cause`, and `birth_history` remain weak.
- The suite varies `model_track` only. It does not test Qwen-specific prompt adaptation, optimizer use, or alternative context settings.

## Decision

| Item | Position |
| --- | --- |
| Qwen 27b ladder | **Complete** |
| Model-suite coverage | **Complete for planned S1/S4/Gan F0 surfaces** |
| Operational promotion | **No**; arm evidence only |
| Main follow-up | Fold Qwen 27b into the model-profile synthesis and decide whether the paper needs an S2/S3 extension |

## Next steps

1. If a paper claim needs the middle ExECT ladder, make a separate yes/no decision on `model_suite_exect_s2_s3_extension_v1`; do not run it by inertia.
2. Backfill registry rows for Qwen 27b only if the registry is being used as the current paper-claim source; the inspection and synthesis docs already preserve exact run IDs.
3. Keep Gan S0 builder-gap validation as the primary engineering pull; the model suite should now serve interpretation and reporting.
