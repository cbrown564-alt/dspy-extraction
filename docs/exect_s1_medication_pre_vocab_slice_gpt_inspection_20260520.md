# ExECT S1 Medication Pre-Vocab Slice — Inspection

Date: 2026-05-20  
Comparison group: `exect_s1_medication_pre_vocab_slice_gpt_v1`  
Support map: `docs/exect_field_family_deterministic_support_map_20260520.md`

## Run artifacts

| Arm | Run ID | Config |
| --- | --- | --- |
| **L1 baseline** | `exect_s1_interleaving_l1_baseline_medication_slice_gpt4_1_mini_20260520T191336Z` | `exect_s1_interleaving_l1_baseline_medication_slice_gpt4_1_mini.json` |
| **H2 medication pre-vocab** | `exect_s1_interleaving_h2_medication_pre_vocab_slice_gpt4_1_mini_20260520T191345Z` | `exect_s1_interleaving_h2_medication_pre_vocab_slice_gpt4_1_mini.json` |

Fixed controls: 14-record Rx-heavy slice (`data/fixtures/exect_s1_medication_pre_vocab_regression_slice.json`), ExECTv2 validation split subset, `exect_s0_s1_field_family`, `exect_field_family_deterministic_v1`, GPT 4.1-mini, prompt `exect_s0_s1_field_family_v4_10_label_policy`.

Varied factor: medication-only `H2_pre_deterministic` pre-vocabulary injection vs frozen L1 single-pass (`program_architecture` / `interleaving_position` per config taxonomy).

## Headline metrics

| Arm | Micro F1 | Diagnosis F1 | Seizure F1 | **Medication F1** | Evidence support |
| --- | ---: | ---: | ---: | ---: | ---: |
| L1 baseline | **93.3%** | 90.9% | 88.4% | **98.3%** | 98.0% |
| H2 medication pre-vocab | **92.0%** | 90.9% | 88.4% | **95.1%** | 94.0% |

Primary delta (H2 − L1): **−3.2pp medication F1**; **−1.3pp** pooled micro (diagnostic).

Diagnosis and seizure_type F1 are identical between arms on this slice — the decision rests on medication.

## Decisions

| Arm | Outcome | Rationale |
| --- | --- | --- |
| **L1 baseline** | **Hold (slice reference)** | 98.3% medication F1 on Rx-heavy records; use as comparison anchor only — do not extrapolate to full validation. |
| **H2 medication pre-vocab** | **Reject** | Medication F1 regressed 95.1% vs 98.3% (−3.2pp). Family-isolated pre-vocab does not recover the full-note H2 failure mode; still harmful on medication-heavy notes. |

## Error notes

H2 shows additional medication evidence gaps on EA0135 and EA0150 (missing evidence spans for levetiracetam/clobazam/lamotrigine). Pre-vocab candidate lists may anchor surface forms without improving benchmark-facing normalization on this slice.

## Recommended next work

1. Do not promote medication-only H2 pre-vocab to full validation or Qwen.
2. Proceed to support-map queue #3: S4 seizure-frequency pre-candidate experiment (family-isolated; cap-25 first).
3. Keep full-note H2 pre-vocab frozen as rejected (v1 full + this slice).
