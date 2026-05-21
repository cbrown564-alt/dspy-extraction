# ExECT S2 Comorbidity Surface Bridge GPT Cap-25 v1 — Pre-Registration

Date: 2026-05-21  
Status: **Done** — inspection `exect_s2_comorbidity_surface_bridge_gpt_cap25_v1_inspection_20260521.md` (null on cap-25)  
Comparison group: `exect_s2_comorbidity_surface_bridge_gpt_cap25_v1`  
Design: `docs/experiments/exect/exect_s2_comorbidity_surface_policy_design_20260521.md`  
Parent plan: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md` (items 25–26)

## Research question

On ExECT S2 cap-25, do post-module comorbidity atomization bridges (C0 TBI split; C0+C1 surface plural) improve `comorbidity` F1 versus frozen v1.3 L1 without ≥2pp regression on seizure_type, investigation, or diagnosis?

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema | `exect_s2_field_family` |
| Research axis | 3 |
| Comparison group | `exect_s2_comorbidity_surface_bridge_gpt_cap25_v1` |
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
| LLM extraction | Identical across arms; only post-recovery differs |

## Arms

| Arm | implementation_variant | Program variant | Config |
| --- | --- | --- | --- |
| L1 | `comorbidity_bridge_l1_control` | `exect_s2_field_family_single_pass` | `exect_s2_comorbidity_l1_baseline_cap25_gpt4_1_mini.json` |
| C0 | `comorbidity_atomization_stroke_v1` | `exect_s2_field_family_comorbidity_c0_single_pass` | `exect_s2_comorbidity_c0_cap25_gpt4_1_mini.json` |
| C0+C1 | `comorbidity_atomization_stroke_v1+comorbidity_surface_plural_v1` | `exect_s2_field_family_comorbidity_c0_c1_single_pass` | `exect_s2_comorbidity_c0_c1_cap25_gpt4_1_mini.json` |

Primitive: C0 applies TBI atomization (`traumatic brain injury` → `traumatic`, `brain injury` when note supports). C1 adds haemorrhage→hemorrhage and infarcts→infarct normalization.

## Primary and guardrail metrics

| Metric | Role |
| --- | --- |
| `comorbidity` F1 | **Primary** |
| `seizure_type`, `investigation`, `diagnosis` F1 | **Regression guard** (no ≥2pp drop vs L1) |
| Pooled micro F1 | Diagnostic only |

## Promotion gates (cap-25)

| Outcome | Rule |
| --- | --- |
| **Hold (cap-25 proceed)** | Comorbidity F1 ≥ L1 + **3pp** and regression guards pass |
| **Hold (inconclusive)** | Comorbidity F1 +1–2pp with regression guards pass |
| **Reject (arm)** | Comorbidity F1 ≤ L1 or any regression guard fails |
| **Full validation** | Only cap-25 winner; qualitative clearance on EA0150, EA0170 |

External anchor: GPT S2 full `runs/exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` — 69.3% comorbidity F1.

## Fixture clearance (pre-run)

| Doc | C0/C1 expectation |
| --- | --- |
| EA0150 | TBI atomization |
| EA0170 | haemorrhage spelling |
| EA0179 | learning-disabilities modifier strip (C2 deferred) |

## Open cells

- C2/C3 symptom-scope tiers deferred
- S3 nine-family port of winning C0 tier
- Qwen port only after GPT cap-25 winner
