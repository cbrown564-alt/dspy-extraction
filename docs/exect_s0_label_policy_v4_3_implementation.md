# ExECT Label-Policy v4.3 Implementation

Date: 2026-05-19

Prompt version: `exect_s0_s1_field_family_v4_3_label_policy`

## Target (from v4.2 full-validation medication/evidence read)

1. Medication false positives: planned_rx, planned_switch, taper_stop, historical restart advice
2. Medication false negatives: brand surfaces (`lamictal`, `epilim chrono`) vs generic canonicalization
3. Evidence: header-style quotes and ellipsis stitching on medication lines

Scorer unchanged. v4.2 remains historical comparison anchor (`exect_s0_s1_field_family_v4_2_label_policy`).

## Changes

### Prompt (`EXECT_S0_S1_LABEL_POLICY_GUIDANCE` + policy examples)

- Exclude ASM from prescription requests, planned switches, taper/stop, restart-after-self-stop
- Preserve brand prescription surfaces (Lamictal, Epilim Chrono)
- Evidence without invented section headers
- Six new boundary examples (prescription_request, planned_switch, taper_stop, restart_advice, brand_lamictal, brand_epilim_chrono)

### Deterministic bridges

| Bridge | Behavior |
| --- | --- |
| `medication_brand_surface_preserved` | `lamotrigine` → `lamictal` when note uses Lamictal; `sodium valproate` → `epilim chrono` when note uses Epilim Chrono |
| `medication_surface_repaired` | Typos: `brivitiracetam`, `zonismaide`, `eslicarbazine` (carried from v4.2) |
| Evidence repair | Strip `Medication:` prefixes; ellipsis → contiguous span; fragment fallback for long drug tokens |
| Exclusion phrases | Extended: `to change to`, `could prescribe`, `advised that`, `stopping the medication`, etc. |

## Slice gate (23 records)

Config: `configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json`

Run: `runs/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini_20260519T210001Z`

| Metric | v4.3 slice (23 rec) | v4.2 full rescored on same 23 rec |
| --- | ---: | ---: |
| Micro F1 | **80.0%** | 77.2% |
| Medication F1 | **83.6%** | 75.4% |
| Evidence support | **95.9%** | (see full-run diagnostics) |

**Slice gate: cleared** for cap-25/full promotion path (+2.8pp micro F1; +8.2pp medication F1 vs v4.2 on the same 23 records). v4.2 15-record slice (89.1% micro F1) is not directly comparable due to different record sets.

Compare historical ladder in `docs/exect_s0_label_policy_regression_slice_comparison_20260519.md`.

## Cap-25 (25 records)

Run: `runs/exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T210054Z`

| Metric | v4.3 cap-25 | v4.2 cap-25 | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | 84.7% | **86.4%** | −1.7pp |
| Medication F1 | 89.3% | **93.5%** | −4.2pp |
| Evidence support | **97.3%** | 88.8% | +8.5pp |

Cap-25 remains optimistic vs full; do not use cap-25 alone for promotion.

## Full validation (40 records)

Run: `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T210111Z`

| Metric | v4.3 full | v4.2 full | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **79.8%** | 78.5% | +1.3pp |
| Diagnosis F1 | 74.3% | 74.3% | 0 |
| Seizure F1 | 74.7% | 74.7% | 0 |
| Medication F1 | **89.4%** | 85.1% | +4.3pp |
| Evidence support | **94.1%** | 84.0% | +10.1pp |

**v4.3 is the new monolithic anchor** for ExECT S0/S1 (medication + evidence gains; micro F1 +1.3pp full). Scorer unchanged.

## Next

- Do not promote verify-repair (cap-25 negative on label F1 vs v4.2)
- Diagnosis/seizure unchanged — future work on co-list/specificity-collapse if needed
