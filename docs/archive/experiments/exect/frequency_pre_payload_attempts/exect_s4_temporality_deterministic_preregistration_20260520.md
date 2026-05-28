# ExECT S4 Medication-Temporality Post-Classifier — Pre-Registration

Date: 2026-05-20  
Comparison group: `exect_s4_temporality_deterministic_v1`

## Hypothesis

Evidence-aligned **medication-temporality-only** post classification (`H1_post_deterministic`) improves `medication_temporality` **precision** on the cap-25 ExECTv2 validation gate versus frozen S4 single-pass recovery (`L1_llm_constrained`), without changing schema breadth, scorer, or prompt policy version.

## Fixed controls

| Control | Value |
| --- | --- |
| Dataset / split | ExECTv2 `exectv2_fixed_v1:validation` |
| Record cap | 25 |
| Schema | `exect_s4_field_family` (11 families) |
| Scorer | `exect_s4_field_family_deterministic_v1` |
| Model | GPT 4.1-mini (`configs/models/gan_s0_gpt4_1_mini.json`) |
| Prompt | `exect_s4_field_family_v1_2_label_policy` |
| Program architecture | `single_pass` |

## Varied factor

`interleaving_position` — L1 (`during` only, span/note inference recovery) vs H1 (`during` + `post`).

H1 applies `exect.medication_temporality.post_classifier.v1` per aligned evidence quote:

- Reclassify planned/previous/current from evidence cues (taper-on-current-line stays `current`)
- Drop non-ASM medications from `medication_temporality`
- Drop `unknown` temporality (precision-first abstention)

## Arms

| Arm | Config | Program variant |
| --- | --- | --- |
| L1 baseline | `exect_s4_temporality_l1_baseline_cap25_gpt4_1_mini.json` | `exect_s4_field_family_single_pass` |
| H1 post classifier | `exect_s4_temporality_h1_post_classifier_cap25_gpt4_1_mini.json` | `exect_s4_field_family_temporality_post_classifier_single_pass` |
| L1 full validation | `exect_s4_temporality_l1_baseline_full_gpt4_1_mini.json` | `exect_s4_field_family_single_pass` |
| H1 full validation | `exect_s4_temporality_h1_post_classifier_full_gpt4_1_mini.json` | `exect_s4_field_family_temporality_post_classifier_single_pass` |

## Primary metric

`medication_temporality` field-family **precision** (`benchmark_metrics.field_precision.medication_temporality`).

## Diagnostic metrics

- `medication_temporality` F1 and recall
- Pooled micro F1 across eleven families (not comparable to S1–S3 headlines)
- Per-family F1 for frozen S3 families (regression guard)
- Evidence quote support rate
- Post-classifier bridge flags (`s4_bridge:medication_temporality_*`)

## Promotion gate

- Cap-25: require **≥2pp** `medication_temporality` precision vs L1 **and** `medication_temporality` F1 must not regress **≥2pp** vs L1 on the same 25 records
- Full validation (40): same precision and F1 gates on the full fixed validation split; only run after cap-25 gate passes (**passed 2026-05-20**)

## Expected reject paths

- Precision gain with ≥2pp F1 regression → reject (recall collapse)
- Null or negative precision delta → reject; do not port to Qwen
- Precision gain driven only by empty predictions on sparse support → hold (null), inspect planned/taper slice

## Artifacts

Inspection doc after runs: `docs/experiments/exect/exect_s4_temporality_deterministic_gpt_inspection_20260520.md` (post-run).
