# ExECT Ladder Investigation Guard GPT Cap-25 v1 — Pre-Registration

Date: 2026-05-21  
Status: **Done** — inspection `exect_ladder_investigation_guard_gpt_cap25_v1_inspection_20260521.md` (I0 hold proceed +5.6pp)  
Comparison group: `exect_ladder_investigation_guard_gpt_cap25_v1`  
Design: `docs/experiments/exect/exect_ladder_investigation_regression_guard_design_20260521.md`  
Parent plan: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md` (items 25–26)

## Research question

On ExECT S2 cap-25, does tier **I0** (drop out-of-scope ECG investigation labels) improve `investigation` F1 versus L1 without ≥2pp regression on seizure_type, comorbidity, or diagnosis?

**Do not** claim investigation solved from I0 alone. I1 planned-scan guard is a follow-on arm.

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema | `exect_s2_field_family` (first grid) |
| Research axis | 3 |
| Comparison group | `exect_ladder_investigation_guard_gpt_cap25_v1` |
| Primary varied factor | `implementation_variant` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

## Fixed controls

| Control | Value |
| --- | --- |
| Split | `exectv2_fixed_v1:validation` cap 25 |
| Model | GPT 4.1-mini |
| Scorer | `exect_s2_field_family_deterministic_v1` |
| Prompt | `exect_s2_field_family_v1_3_label_policy` |
| Allowed modalities | EEG, MRI, CT (S2 policy) |

## Arms

| Arm | implementation_variant | Program variant | Config |
| --- | --- | --- | --- |
| L1 | `inv_guard_l1_control` | `exect_s2_field_family_single_pass` | `exect_ladder_inv_l1_baseline_cap25_gpt4_1_mini.json` |
| I0 | `inv_guard_drop_ecg_v1` | `exect_s2_field_family_inv_guard_i0_single_pass` | `exect_ladder_inv_i0_cap25_gpt4_1_mini.json` |

## Primary and guardrail metrics

| Metric | Role |
| --- | --- |
| `investigation` F1 | **Primary** |
| `seizure_type`, `comorbidity`, `diagnosis` F1 | **Regression guard** (no ≥2pp drop vs L1) |
| Pooled micro F1 | Diagnostic only |

## Promotion gates (cap-25)

| Outcome | Rule |
| --- | --- |
| **Hold** | Investigation F1 ≥ L1 + net FP reduction on EA0016/EA0100 with regression guards pass |
| **Reject (arm)** | Investigation F1 ≤ L1 or regression guard fails |
| **S3/S4 port** | Winning tier becomes regression checklist arm in wider-schema prereg |

External anchor: GPT S2 full — 90.0% investigation F1 (`…231223Z`).

## Fixture clearance (pre-run)

| Doc | I0 expectation |
| --- | --- |
| EA0016 | `ecg normal` removed |
| EA0100 | ECG FP removed (gold-quality caveat on missing-gold) |

## Open cells

- I1 planned-scan unknown on S2 cap-25
- I2 polarity guard isolated on slice only
- Shared module import path for S3/S4 investigation recovery
