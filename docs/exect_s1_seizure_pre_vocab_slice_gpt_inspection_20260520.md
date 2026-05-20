# ExECT S1 Seizure Pre-Vocab Slice — Inspection

Date: 2026-05-20  
Comparison group: `exect_s1_seizure_pre_vocab_slice_gpt_v1`  
Support map: `docs/exect_field_family_deterministic_support_map_20260520.md`  
Preregistration: `docs/exect_s1_seizure_pre_vocab_slice_preregistration_20260520.md`

## Run artifacts

| Arm | Run ID | Config |
| --- | --- | --- |
| **L1 baseline** | `exect_s1_interleaving_l1_baseline_seizure_slice_gpt4_1_mini_20260520T205806Z` | `exect_s1_interleaving_l1_baseline_seizure_slice_gpt4_1_mini.json` |
| **H2 seizure pre-vocab** | `exect_s1_interleaving_h2_seizure_pre_vocab_slice_gpt4_1_mini_20260520T205814Z` | `exect_s1_interleaving_h2_seizure_pre_vocab_slice_gpt4_1_mini.json` |

Fixed controls: 15-record seizure-heavy slice (`data/fixtures/exect_s1_seizure_pre_vocab_regression_slice.json`), ExECTv2 validation split subset, `exect_s0_s1_field_family`, `exect_field_family_deterministic_v1`, GPT 4.1-mini, prompt `exect_s0_s1_field_family_v4_10_label_policy`, `repair_policy=none`.

Varied factor: seizure-type-only `H2_pre_deterministic` pre-vocabulary injection (static `_PRE_VOCAB_SEIZURE_TYPE_SURFACES`) vs frozen L1 single-pass.

## Headline metrics

| Arm | Micro F1 | Diagnosis F1 | **Seizure F1** | Medication F1 | Evidence support |
| --- | ---: | ---: | ---: | ---: | ---: |
| L1 baseline | **93.5%** | 93.3% | **91.5%** | 97.1% | 96.2% |
| H2 seizure pre-vocab | **90.3%** | 96.6% | **83.3%** | 97.1% | 92.0% |

Primary delta (H2 − L1): **−8.2pp seizure_type F1**; **−3.2pp** pooled micro (diagnostic).

Cross-family guardrails: diagnosis **+3.3pp** (improved); medication **0.0pp** (unchanged). No cross-family regression ≥2pp, but primary seizure metric regressed sharply.

## Decisions

| Arm | Outcome | Rationale |
| --- | --- | --- |
| **L1 baseline** | **Hold (slice reference)** | 91.5% seizure_type F1 on seizure-heavy records; anchor only — do not extrapolate to full validation. |
| **H2 seizure pre-vocab** | **Reject** | Seizure_type F1 regressed 83.3% vs 91.5% (−8.2pp). Family-isolated static pre-vocab does not fix the full-note H2 seizure regression; harmful on seizure-heavy notes. |

## Error notes

H2 shows additional seizure_type evidence failures on EA0016, EA0018, EA0045, and related records (missing spans or unsupported long quotes). Static candidate lists appear to anchor coarse surfaces (`focal seizure`, list hints) without improving audited plural/modifier splits or evidence alignment.

## Taxonomy

| Field | L1 | H2 |
| --- | --- | --- |
| `comparison_group` | `exect_s1_seizure_pre_vocab_slice_gpt_v1` | same |
| `hybrid_balance_class` | `L1_llm_constrained` | `H2_pre_deterministic` |
| `interleaving_positions` | `during` | `pre`, `during` |
| `clinical_task_family` | `seizure_type` | `seizure_type` |
| `program_variant` | `exect_s0_s1_field_family_single_pass` | `exect_s0_s1_field_family_seizure_pre_vocab_single_pass` |

## Recommended next work

1. Do not promote seizure-only H2 pre-vocab to full validation (40) or Qwen.
2. Keep full-note H2 pre-vocab frozen as rejected (`exect_s1_interleaving_gpt_validation_v1` / v2 evidence).
3. Revisit support-map queue for the next family-isolated or bridge-free probe; no further S1 pre-vocab slices without a new hypothesis.
