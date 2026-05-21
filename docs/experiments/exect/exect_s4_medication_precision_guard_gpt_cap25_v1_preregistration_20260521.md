# ExECT S4 Medication Precision Guard GPT Cap-25 v1 — Pre-Registration

Date: 2026-05-21  
Status: **Ready to run**  
Comparison group: `exect_s4_medication_precision_guard_gpt_cap25_v1`  
Design: `docs/experiments/exect/exect_s4_medication_precision_guard_design_20260521.md`  
Parent plan: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md` (item 20)

## Research question

On ExECT S4 cap-25, does tier **G0** (non-ASM-only post-guard) improve `medication_temporality` **precision** versus L1 single-pass baseline **without** ≥2pp `medication_temporality` F1 regression?

**Do not** rerun H1 `exect.medication_temporality.post_classifier.v1` (full-validation reject: recall collapse).

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema | `exect_s4_field_family` |
| Research axis | 3 |
| Comparison group | `exect_s4_medication_precision_guard_gpt_cap25_v1` |
| Primary varied factor | `implementation_variant` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

## Fixed controls

| Control | Value |
| --- | --- |
| Split | `exectv2_fixed_v1:validation` cap 25 |
| Model | GPT 4.1-mini |
| Scorer | `exect_s4_field_family_deterministic_v1` |
| Prompt | `exect_s4_field_family_v1_2_label_policy` |
| Program architecture | `single_pass` (eleven families) |
| LLM extraction | Identical across arms; only post-recovery differs |

## Arms

| Arm | implementation_variant | Program variant | Config |
| --- | --- | --- | --- |
| L1 | `mt_guard_l1_control` | `exect_s4_field_family_single_pass` | `exect_s4_mt_guard_l1_baseline_cap25_gpt4_1_mini.json` |
| G0 | `mt_guard_non_asm_only_v1` | `exect_s4_field_family_mt_guard_non_asm_single_pass` | `exect_s4_mt_guard_g0_non_asm_cap25_gpt4_1_mini.json` |

Primitive: G0 applies `exect.medication_temporality.non_asm_guard.v1` — drops non-ASM / unlisted medications; **preserves** model `medication|status`; does **not** drop dose-only `current` ASM rows.

## Primary and guardrail metrics

| Metric | Role |
| --- | --- |
| `medication_temporality` precision | **Primary** |
| `medication_temporality` F1 | **F1 guard** (must not regress ≥2pp vs L1) |
| `medication_temporality` recall | Diagnostic |
| Pooled micro F1 | Diagnostic only |
| Per-family F1 (investigation, seizure_type, annotated_medication, diagnosis) | Regression guard (no ≥2pp drop) |

## Promotion gates (cap-25)

| Outcome | Rule |
| --- | --- |
| **Hold (cap-25 proceed)** | G0 MT precision ≥ L1 + **3pp** and F1 guard passes |
| **Hold (inconclusive)** | G0 precision +1–2pp with F1 guard pass |
| **Reject (arm)** | G0 precision ≤ L1 or F1 regresses ≥2pp |
| **Full validation** | Only if cap-25 hold gate passes; same precision/F1 rules on 40 records |

External anchor (not in-session control): GPT S4 v1.2 full `runs/exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` — 46.4% MT precision, 62.5% MT F1.

## Inspection requirements

- Taxonomy with `decision_scope: arm`
- MT precision/F1/recall table L1 vs G0
- Frozen-family regression table
- Label delta on shared 25 IDs (expect non-ASM FP removals only)
- Explicit: no mechanism reject; G1/G2 deferred per design doc

## Open cells

- G0+G2 dose-current fallback arm
- G1 planned/previous evidence-gated drop
- G3 brand alias map
- Annotated-medication coupled guard
- Qwen port

## Run order

1. Dry-run both configs
2. Cap-25 L1 then G0 (or parallel)
3. Inspection `docs/exect_s4_medication_precision_guard_gpt_cap25_v1_inspection_<date>.md`
