# ExECT S1 Interleaving GPT Validation v2 — Inspection

Date: 2026-05-20  
Comparison group: `exect_s1_interleaving_gpt_validation_v2`  
Support map: `docs/exect_field_family_deterministic_support_map_20260520.md`

## Run artifacts

| Arm | Scope | Run ID | Config |
| --- | --- | --- | --- |
| **L1 raw (bridge-free)** | cap-25 | `exect_s1_interleaving_l1_raw_no_bridges_cap25_gpt4_1_mini_20260520T190744Z` | `exect_s1_interleaving_l1_raw_no_bridges_cap25_gpt4_1_mini.json` |
| **L1 raw (bridge-free)** | full (40) | `exect_s1_interleaving_l1_raw_no_bridges_gpt4_1_mini_20260520T190804Z` | `exect_s1_interleaving_l1_raw_no_bridges_gpt4_1_mini.json` |
| **H1 post bridge** | cap-25 | `exect_s1_interleaving_h1_post_bridge_cap25_gpt4_1_mini_20260520T190754Z` | `exect_s1_interleaving_h1_post_bridge_cap25_gpt4_1_mini.json` |
| **H1 post bridge** | full (40) | `exect_s1_interleaving_h1_post_bridge_gpt4_1_mini_20260520T190807Z` | `exect_s1_interleaving_h1_post_bridge_gpt4_1_mini.json` |
| **L1 production anchor** *(frozen)* | full (40) | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` | `exect_s0_s1_validation_full_gpt4_1_mini.json` |

Fixed controls: ExECTv2 validation split (40), `exect_s0_s1_field_family`, `exect_field_family_deterministic_v1`, GPT 4.1-mini, prompt `exect_s0_s1_field_family_v4_10_label_policy`.

Varied factor: `repair_policy` — `raw_no_benchmark_bridges` vs `artifact_benchmark_bridge_only` (same model outputs; bridges applied or skipped in `_build_s1_field_family_values`).

## Headline metrics

| Arm | Scope | Micro F1 | Diagnosis | Seizure | Medication | Evidence support |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| L1 raw | cap-25 | **72.8%** | 71.4% | 56.3% | 93.3% | 97.5% |
| L1 raw | full | **68.6%** | 61.5% | 57.4% | 85.7% | 93.8% |
| H1 post bridge | cap-25 | **95.8%** | 97.6% | 95.4% | 94.9% | 97.3% |
| H1 post bridge | full | **92.3%** | 93.8% | 90.5% | 92.8% | 95.8% |
| L1 production anchor | full | **92.3%** | 93.8% | 90.5% | 92.8% | ~96% |

Full deltas (bridged − raw): **+23.7pp** micro F1; seizure **+33.1pp**; diagnosis **+32.3pp**; medication **+7.1pp**.

## Decisions

| Arm | Outcome | Rationale |
| --- | --- | --- |
| **H1 post bridge** | **Hold (null vs production L1)** | Full micro F1 identical to frozen L1 anchor (92.3%). Confirms `artifact_benchmark_bridge_only` applies the same bridges as `repair_policy=none`. |
| **L1 raw** | **Diagnostic anchor** | Quantifies benchmark-bridge contribution on the same extraction pass. Not a deployment candidate. |
| **Interleaving v2 matrix** | **Complete** | v1 null arm is explained; bridge-free vs bridged comparison is now measurable. |

## Interpretation

v1 reported H1 as null because both arms always ran `_build_s1_field_family_values` bridges. v2 adds `raw_no_benchmark_bridges`, which skips bridge normalization while keeping the same scorer.

The **~24pp pooled micro gap** is driven mainly by diagnosis and seizure_type bridges (fused-phrase split, specificity collapse, coarse surfaces). Medication bridges matter less on this split but still add ~7pp F1.

`bridge_stage` metadata (`post` vs `inline`) remains cosmetic; scored labels match when bridges are enabled.

## Recommended next work

1. ~~Run medication-only slice pair~~ — complete; see `docs/exect_s1_medication_pre_vocab_slice_gpt_inspection_20260520.md`.
2. ~~Add registry rows for v2 runs~~ — complete in `docs/experiment_registry.json`.
3. Design S4 seizure-frequency pre-candidate experiment (support map queue #3).
4. Do not port H1 to Qwen until a varied factor shows ≥2pp full-validation gain over production L1.
