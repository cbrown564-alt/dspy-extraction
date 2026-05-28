# ExECT S4 Epilepsy Cause Bridge GPT Full Validation v1 — Pre-Registration

Date: 2026-05-21  
Status: **Done** — inspection `docs/experiments/exect/exect_s4_epilepsy_cause_bridge_gpt_full_validation_v1_inspection_20260521.md`  
Comparison group: `exect_s4_epilepsy_cause_bridge_gpt_full_validation_v1`  
S3 full-validation inspection: `docs/experiments/exect/exect_s3_epilepsy_cause_bridge_gpt_full_validation_v1_inspection_20260521.md`  
Design: `docs/experiments/exect/exect_s3_epilepsy_cause_cui_phrase_bridge_design_20260521.md`  
Parent plan: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md` (S4 cause-bridge port item 31)

## Research question

On the full ExECTv2 fixed validation split (40 records), does post-module epilepsy_cause CUIPhrase bridges **K0+K1** on the S4 eleven-family pass improve `epilepsy_cause` F1 versus paired **L1** control **without** ≥2pp regression on **medication_temporality**, **seizure_frequency**, or **investigation**?

Triggered after S3 full-validation hold: K0+K1 **+11.1pp** cause F1 vs L1 on S3 (`…091824Z` / `…091816Z`; EA0059 modifier-strip TP). S4 cause bridge is wired no-model via `EXECT_S4_CAUSE_BRIDGE_K0_K1_VARIANT`.

**Do not** mechanism-close CUIPhrase cause bridges from S3 full validation or S4 port alone.

## Preconditions (met)

| Gate | Status |
| --- | --- |
| EC-* fixture tests | Green — `tests/test_exect_s3_epilepsy_cause_bridge.py`, `tests/test_exect_s4_program.py` |
| S3 full validation | Done — K0+K1 hold operational candidate |
| S4 cause-bridge program port | Done — `exect_s4_field_family_cause_bridge_k0_k1_single_pass` |
| I0 investigation guard on S4 recovery | Ported — `ladder_investigation_guard_bridge_tiers()` |

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema | `exect_s4_field_family` |
| Research axis | 3 |
| Comparison group | `exect_s4_epilepsy_cause_bridge_gpt_full_validation_v1` |
| Primary varied factor | `implementation_variant` |
| stage_graph_id | `g1_l1_policy_bridges` |
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
| LLM extraction | Identical across arms; only post-recovery differs on `epilepsy_cause` via S3 recovery path |

## Arms

| Arm | implementation_variant | Program variant | Config |
| --- | --- | --- | --- |
| L1 | `cause_bridge_l1_control` | `exect_s4_field_family_single_pass` | `exect_s4_cause_l1_baseline_full_gpt4_1_mini.json` |
| K0+K1 | `cause_synonym_plural_v1+cause_modifier_strip_v1` | `exect_s4_field_family_cause_bridge_k0_k1_single_pass` | `exect_s4_cause_k0_k1_full_gpt4_1_mini.json` |

Primitive: K0+K1 applies `exect.epilepsy_cause.cui_phrase_bridge.v1` tiers on `epilepsy_cause` recovery only (routes through `_s3_field_values_from_prediction`).

## Primary and guardrail metrics

| Metric | Role |
| --- | --- |
| `epilepsy_cause` F1 | **Primary** |
| `medication_temporality`, `seizure_frequency`, `investigation` F1 | **Regression guard** (no ≥2pp drop vs L1) |
| Pooled micro F1 | Diagnostic only — dominated by high-support families |
| Per-family S4 burden families | Tag deltas; see `exect_s4_residual_error_analysis_20260521.md` |

## Confirmation gates (full validation)

| Outcome | Rule |
| --- | --- |
| **Hold (operational candidate)** | Cause F1 ≥ L1 + **3pp** and regression guards pass |
| **Hold (inconclusive)** | Cause F1 +1–2pp with guards pass |
| **Reject (arm)** | Cause F1 ≤ L1 or regression guard fails |
| **Mechanism** | Not closable from one full-validation pair |

External anchor (not in-session control): GPT S4 v1.2 full `runs/exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` — 65.5% micro; cause F1 10.5%; MT 62.5%; frequency 45.7%; investigation 96.7%.

S3 full-validation anchor: K0+K1 22.2% cause F1 on nine-family pass (`…091824Z`).

## Run order

1. Dry-run both configs
2. Full validation L1 then K0+K1 (~40 LLM calls each)
3. Inspection `docs/experiments/exect/exect_s4_epilepsy_cause_bridge_gpt_full_validation_v1_inspection_20260521.md`
4. Registry rows with `decision_scope: arm`

## Open cells

- K2 TBI atomization tier for EA0150-class composites
- K3 template strip for EA0124-class surfaces
- S4 default program variant update only after this grid + guards pass
- Qwen port only after GPT full-validation hold
- MT G0 guard and frequency structured slots are separate tracks
