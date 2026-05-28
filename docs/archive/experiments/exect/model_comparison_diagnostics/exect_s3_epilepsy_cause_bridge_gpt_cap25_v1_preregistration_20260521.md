# ExECT S3 Epilepsy Cause Bridge GPT Cap-25 v1 — Pre-Registration

Date: 2026-05-21  
Status: **Done** — cap-25 grid run 2026-05-21; inspection `exect_s3_epilepsy_cause_bridge_gpt_cap25_v1_inspection_20260521.md`  
Comparison group: `exect_s3_epilepsy_cause_bridge_gpt_cap25_v1`  
Design: `docs/experiments/exect/exect_s3_epilepsy_cause_cui_phrase_bridge_design_20260521.md`  
Parent plan: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md` (ExECT S1–S3 item 27)

## Research question

On ExECT S3 cap-25, do post-module epilepsy_cause CUIPhrase bridges (K0 synonym/plural + K1 modifier strip) improve `epilepsy_cause` F1 versus frozen v1.2 L1 without ≥2pp regression on investigation, seizure_type, or comorbidity?

## Preconditions (met)

| Gate | Status |
| --- | --- |
| EC-* fixture tests | Green — `tests/test_exect_s3_epilepsy_cause_bridge.py` |
| I0 investigation guard on S3 recovery | Ported — `ladder_investigation_guard_bridge_tiers()` |
| Comorbidity residual slice | Done — `docs/experiments/exect/exect_s2_comorbidity_residual_slice_replay_20260521.md` |

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema | `exect_s3_field_family` |
| Research axis | 3 |
| Comparison group | `exect_s3_epilepsy_cause_bridge_gpt_cap25_v1` |
| Primary varied factor | `implementation_variant` |
| decision_scope | `arm` |

## Fixed controls

| Control | Value |
| --- | --- |
| Split | `exectv2_fixed_v1:validation` cap 25 |
| Model | GPT 4.1-mini |
| Scorer | `exect_s3_field_family_deterministic_v1` |
| Prompt | `exect_s3_field_family_v1_2_label_policy` |
| Investigation recovery | I0 ECG drop guard on all arms (regression guard) |

## Arms

| Arm | implementation_variant | Program variant | Config |
| --- | --- | --- | --- |
| L1 | `cause_bridge_l1_control` | `exect_s3_field_family_single_pass` | `exect_s3_cause_l1_baseline_cap25_gpt4_1_mini.json` |
| K0+K1 | `cause_synonym_plural_v1+cause_modifier_strip_v1` | `exect_s3_field_family_cause_bridge_k0_k1_single_pass` | `exect_s3_cause_k0_k1_cap25_gpt4_1_mini.json` |

## Primary and guardrail metrics

| Metric | Role |
| --- | --- |
| `epilepsy_cause` F1 | **Primary** |
| `investigation`, `seizure_type`, `comorbidity` F1 | **Regression guard** (no ≥2pp drop vs L1) |
| Pooled micro F1 | Diagnostic only — unstable on 7-label cause family |

## Promotion gates (cap-25)

| Outcome | Rule |
| --- | --- |
| **Hold (cap-25 proceed)** | Cause F1 ≥ L1 + **3pp** and regression guards pass |
| **Hold (inconclusive)** | Cause F1 +1–2pp with guards pass |
| **Reject (arm)** | Cause F1 ≤ L1 or regression guard fails |
| **Full validation** | Only cap-25 winner; queue docs EA0150, EA0016, EA0137 |

External anchor: GPT S3 full `runs/exect_s3_validation_full_gpt4_1_mini_20260519T235439Z`.

## Residual-slice context

Comorbidity C0/C1 bridges show label deltas on the 6-doc queue when replayed from full-validation raw labels (`exect_s2_comorbidity_residual_slice_replay_20260521.md`). Cap-25 comorbidity grid was null because queue docs were outside the matched LLM failure surface — cause bridge prereg proceeds independently on sparse-family fixtures.

## Open cells

- K2 TBI atomization for cause (deferred)
- S4 cause bridge port after S3 cap-25 winner
- Qwen port only after GPT winner
