# ExECT S4 Medication Precision Guard GPT Full Validation v1 — Pre-Registration

Date: 2026-05-21  
Status: **Done; G0G2 addendum completed 2026-05-24** - inspections `docs/experiments/exect/exect_s4_medication_precision_guard_gpt_full_validation_v1_inspection_20260521.md`, `docs/experiments/exect/exect_s4_mt_guard_g0g2_dose_current_gpt_inspection_20260524.md`  
Comparison group: `exect_s4_medication_precision_guard_gpt_full_validation_v1`  
Cap-25 inspection: `docs/experiments/exect/exect_s4_medication_precision_guard_gpt_cap25_v1_inspection_20260521.md`  
Design: `docs/experiments/exect/exect_s4_medication_precision_guard_design_20260521.md`  
Parent plan: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md`

## Research question

On the full ExECTv2 fixed validation split (40 records), does tier **G0** (non-ASM-only post-guard) improve `medication_temporality` **precision** versus paired **L1** control **without** ≥2pp `medication_temporality` F1 regression?

Triggered after cap-25 hold: G0 MT precision **+11.2pp**, MT F1 **+9.7pp** vs L1 (`…073727Z` / `…073717Z`).

**Do not** rerun H1 `exect.medication_temporality.post_classifier.v1` (full-validation reject: recall collapse).

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema | `exect_s4_field_family` |
| Research axis | 3 |
| Comparison group | `exect_s4_medication_precision_guard_gpt_full_validation_v1` |
| Primary varied factor | `implementation_variant` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

## Fixed controls

| Control | Value |
| --- | --- |
| Split | `exectv2_fixed_v1:validation` (full, no cap) |
| Model | GPT 4.1-mini |
| Scorer | `exect_s4_field_family_deterministic_v1` |
| Prompt | `exect_s4_field_family_v1_2_label_policy` |
| Program architecture | `single_pass` (eleven families) |
| LLM extraction | Identical across arms; only post-recovery differs |

## Arms

| Arm | implementation_variant | Program variant | Config |
| --- | --- | --- | --- |
| L1 | `mt_guard_l1_control` | `exect_s4_field_family_single_pass` | `exect_s4_mt_guard_l1_baseline_full_gpt4_1_mini.json` |
| G0 | `mt_guard_non_asm_only_v1` | `exect_s4_field_family_mt_guard_non_asm_single_pass` | `exect_s4_mt_guard_g0_non_asm_full_gpt4_1_mini.json` |
| G0G2 | `mt_guard_non_asm_dose_current_v1` | `exect_s4_field_family_mt_guard_non_asm_dose_current_single_pass` | `exect_s4_mt_guard_g0g2_dose_current_full_gpt4_1_mini.json` |

Primitive: G0 applies `exect.medication_temporality.non_asm_guard.v1` — drops non-ASM / unlisted medications; preserves model `medication|status`; does not drop dose-only `current` ASM rows.

Primitive: G0G2 applies `exect.medication_temporality.non_asm_dose_current_guard.v1` after cap-25 clearance; it keeps G0 non-ASM removal, preserves `current` ASM labels on prescription-style dose evidence, and prunes unsupported planned/previous labels.

## Primary and guardrail metrics

| Metric | Role |
| --- | --- |
| `medication_temporality` precision | **Primary** |
| `medication_temporality` F1 | **F1 guard** (G0 must not regress ≥2pp vs L1) |
| `medication_temporality` recall | Diagnostic |
| Pooled micro F1 | Diagnostic only |
| Per-family F1 (investigation, seizure_type, annotated_medication, diagnosis, seizure_frequency) | Regression guard (no ≥2pp drop vs L1) |

## Confirmation gates (full validation)

| Outcome | Rule |
| --- | --- |
| **Hold (operational candidate)** | G0 MT precision ≥ L1 + **3pp** and F1 guard passes |
| **Hold (inconclusive)** | G0 precision +1–2pp with F1 guard pass |
| **Reject (arm)** | G0 precision ≤ L1 or F1 regresses ≥2pp |
| **Mechanism** | Not closable from one full-validation pair |

External anchor (not in-session control): GPT S4 v1.2 full `runs/exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` — 46.4% MT precision, 62.5% MT F1, 65.5% micro.

## Run order

1. Dry-run both configs
2. Full validation L1 then G0 (~40 LLM calls each)
3. Inspection `docs/experiments/exect/exect_s4_medication_precision_guard_gpt_full_validation_v1_inspection_20260521.md`
4. Registry rows with `decision_scope: arm`

## Open cells

- G0+G2 dose-current fallback - complete in 2026-05-24 addendum
- G1 planned/previous evidence gate
- G3 brand alias map
- Annotated-medication coupled guard
- Qwen port
