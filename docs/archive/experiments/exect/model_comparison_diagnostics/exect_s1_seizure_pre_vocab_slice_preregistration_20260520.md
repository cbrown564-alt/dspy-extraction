# ExECT S1 Seizure-Type Pre-Vocab Slice — Pre-Registration

Date: 2026-05-20  
Comparison group: `exect_s1_seizure_pre_vocab_slice_gpt_v1`  
Support map: `docs/experiments/exect/exect_field_family_deterministic_support_map_20260520.md`  
Grill decisions: seizure-type-only isolated probe (2026-05-20)

## Hypothesis

**Seizure-type-only** `H2_pre_deterministic` pre-vocabulary injection (static audited surfaces from `_PRE_VOCAB_SEIZURE_TYPE_SURFACES`, no diagnosis or medication candidate lists) improves `seizure_type` F1 on a seizure-heavy validation slice versus frozen L1 single-pass, without repeating the full-note H2 seizure regression (−11.3pp at full validation in `exect_s1_interleaving_gpt_validation_v1`).

## Fixed controls

| Control | Value |
| --- | --- |
| Dataset / split | ExECTv2 `exectv2_fixed_v1:validation` |
| Record filter | 15-record slice (`data/fixtures/exect_s1_seizure_pre_vocab_regression_slice.json`) |
| Schema | `exect_s0_s1_field_family` (diagnosis, seizure_type, annotated_medication) |
| Scorer | `exect_field_family_deterministic_v1` |
| Model | GPT 4.1-mini (`configs/models/gan_s0_gpt4_1_mini.json`) |
| Prompt | `exect_s0_s1_field_family_v4_10_label_policy` |
| `repair_policy` | `none` (production benchmark bridges on both arms) |
| Program architecture | `single_pass` |

## Slice selection (frozen before runs)

Include validation records with **≥2 gold `seizure_type` labels OR ≥2 distinct note-anchored hits** from `_PRE_VOCAB_SEIZURE_TYPE_SURFACES` (word-boundary match, same logic as pre-vocab injection).

**15 records:** EA0008, EA0016, EA0018, EA0045, EA0059, EA0061, EA0069, EA0072, EA0090, EA0109, EA0116, EA0124, EA0143, EA0150, EA0153.

Do not merge the medication pre-vocab slice or the 37-record label-policy regression slice into this comparison group.

## Varied factor

`interleaving_position` — L1 (`during` only, full note) vs H2 (`pre` + `during`, seizure-type candidate list only).

| Arm | Program variant (planned) | Config (planned) |
| --- | --- | --- |
| L1 baseline | `exect_s0_s1_field_family_single_pass` | `exect_s1_interleaving_l1_baseline_seizure_slice_gpt4_1_mini.json` |
| H2 seizure pre-vocab | `exect_s0_s1_field_family_seizure_pre_vocab_single_pass` | `exect_s1_interleaving_h2_seizure_pre_vocab_slice_gpt4_1_mini.json` |

**No cap-25 gate** for this comparison group (medication slice precedent: slice-only first).

## Primary metric

`seizure_type` field-family **F1** (`benchmark_metrics.field_f1.seizure_type` or equivalent per-family F1 in run metrics).

## Diagnostic metrics

- Pooled micro F1 across three S1 families (diagnostic only; not a promotion metric)
- `diagnosis` and `annotated_medication` F1 (cross-family guardrail)
- Evidence quote support rate
- Precomputed candidate metadata on H2 arm

## Promotion gates (slice → full validation)

| Outcome | Rule |
| --- | --- |
| **Reject** | H2 **< L1** on **seizure_type** F1, **or** **≥2pp** regression on **diagnosis** or **medication** F1 on the slice |
| **Hold (slice only)** | Seizure F1 gain **< +2pp** with no cross-family regression **≥2pp** — document; **no** full validation |
| **Proceed to full validation (40)** | Seizure F1 **≥ +2pp** vs L1 on the slice **and** no cross-family regression **≥2pp** |
| **Qwen port** | Only after a full-validation win meets the same **≥2pp** seizure F1 rule |

## Expected reject paths

- Any seizure F1 regression on slice → **reject** (family isolation did not fix full-note H2 failure mode)
- Seizure gain with **≥2pp** diagnosis or medication regression → **reject**
- Small positive seizure delta (<2pp) → **hold**; do not extrapolate to full validation

## Artifacts (post-run)

- Inspection: `docs/experiments/exect/exect_s1_seizure_pre_vocab_slice_gpt_inspection_20260520.md`
- Registry rows under `exect_s1_seizure_pre_vocab_slice_gpt_v1` with `intended_decision` updated after inspection
