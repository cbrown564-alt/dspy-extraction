# ExECT S4 Seizure-Frequency Pre-Candidate — Inspection (GPT cap-25)

Date: 2026-05-20  
Comparison group: `exect_s4_frequency_deterministic_v1`  
Pre-registration: `docs/exect_s4_frequency_deterministic_preregistration_20260520.md`

## Run artifacts

| Arm | Run ID | Config |
| --- | --- | --- |
| **L1 baseline** | `exect_s4_frequency_l1_baseline_cap25_gpt4_1_mini_20260520T191914Z` | `exect_s4_frequency_l1_baseline_cap25_gpt4_1_mini.json` |
| **H2 frequency pre-vocab** | `exect_s4_frequency_h2_pre_vocab_cap25_gpt4_1_mini_20260520T191951Z` | `exect_s4_frequency_h2_pre_vocab_cap25_gpt4_1_mini.json` |

Fixed controls: cap-25 ExECTv2 validation, `exect_s4_field_family`, `exect_s4_field_family_deterministic_v1`, GPT 4.1-mini, prompt `exect_s4_field_family_v1_2_label_policy`.

Varied factor: seizure-frequency-only `H2_pre_deterministic` pre-candidate injection vs L1 single-pass.

## Headline metrics

| Arm | **Seizure_frequency F1** | Micro F1 | Diagnosis | Seizure_type | Medication | Investigation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| L1 baseline | **49.1%** | 69.2% | 95.2% | 90.9% | 69.0% | 93.8% |
| H2 pre-vocab | **47.1%** | 71.5% | 95.2% | 90.9% | 74.4% | 93.8% |

Primary delta (H2 − L1): **−2.0pp seizure_frequency F1** (fails ≥2pp promotion gate).

Pooled micro rose +2.3pp (driven by medication/comorbidity), but cap-25 promotion requires primary metric gain without ≥2pp S3-family regression — diagnosis/seizure_type held; no S3 regression observed.

## Decisions

| Arm | Outcome | Rationale |
| --- | --- | --- |
| **L1 baseline** | **Hold (cap-25 reference)** | 49.1% seizure_frequency F1 on gate split; aligns with ~45.7% full-validation anchor directionally. |
| **H2 frequency pre-vocab** | **Reject** | Primary metric regressed −2.0pp; note-anchored + filtered Gan hints did not help ExECT frequency surfaces on cap-25. |

## Interpretation

Family-isolated pre-vocab mirrors S1 H2 and medication-slice failures: candidate lists anchor the model without improving benchmark-facing normalization. Gan temporal hints filtered to ExECT templates were insufficient; monthly-style derivations that do not map to gold `N per period` surfaces remain a transfer risk.

Do not promote to full validation (40) or Qwen port.

## Recommended next work

1. Keep frozen S4 single-pass as default; do not enable frequency pre-vocab in production paths.
2. Proceed to support-map queue #4: medication temporality post classifier (`exect_s4_temporality_deterministic_v1`).
3. Optional: error-read on cap-25 frequency FPs (qualitative vs quantified confusion) before further frequency scaffolding.
