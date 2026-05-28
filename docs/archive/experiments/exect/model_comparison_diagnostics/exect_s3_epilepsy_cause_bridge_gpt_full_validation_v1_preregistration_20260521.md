# ExECT S3 Epilepsy Cause Bridge GPT Full Validation v1 — Pre-Registration

Date: 2026-05-21  
Status: **Done** — inspection `docs/experiments/exect/exect_s3_epilepsy_cause_bridge_gpt_full_validation_v1_inspection_20260521.md`  
Comparison group: `exect_s3_epilepsy_cause_bridge_gpt_full_validation_v1`  
Cap-25 inspection: `docs/experiments/exect/exect_s3_epilepsy_cause_bridge_gpt_cap25_v1_inspection_20260521.md`  
Residual slice replay: `docs/experiments/exect/exect_s3_epilepsy_cause_residual_slice_replay_20260521.md`  
Design: `docs/experiments/exect/exect_s3_epilepsy_cause_cui_phrase_bridge_design_20260521.md`  
Parent plan: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md` (ExECT S1–S3 item 32)

## Research question

On the full ExECTv2 fixed validation split (40 records), do post-module epilepsy_cause CUIPhrase bridges **K0+K1** (`cause_synonym_plural_v1` + `cause_modifier_strip_v1`) improve `epilepsy_cause` F1 versus paired **L1** control **without** ≥2pp regression on investigation, seizure_type, or comorbidity?

Triggered after cap-25 hold: K0+K1 **+20.0pp** cause F1 vs L1 (`…090550Z` / `…090542Z`; 1/25 doc delta EA0059 meningitis).

**Do not** mechanism-close CUIPhrase cause bridges from cap-25 or residual slice alone.

## Preconditions (met)

| Gate | Status |
| --- | --- |
| EC-* fixture tests | Green — `tests/test_exect_s3_epilepsy_cause_bridge.py` |
| Cap-25 grid | Done — K0+K1 hold proceed |
| I0 investigation guard on S3 recovery | Ported |
| Qualitative queue fixture | `data/fixtures/exect_s3_epilepsy_cause_residual_slice.json` (EA0150, EA0016, EA0137) |
| Residual slice replay | Done — **null** on 3-doc queue (K0+K1 needs K2 TBI / recall fixes not in tier) |

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema | `exect_s3_field_family` |
| Research axis | 3 |
| Comparison group | `exect_s3_epilepsy_cause_bridge_gpt_full_validation_v1` |
| Primary varied factor | `implementation_variant` |
| stage_graph_id | `g1_l1_policy_bridges` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

## Fixed controls

| Control | Value |
| --- | --- |
| Split | `exectv2_fixed_v1:validation` (full, no cap) |
| Model | GPT 4.1-mini |
| Scorer | `exect_s3_field_family_deterministic_v1` |
| Prompt | `exect_s3_field_family_v1_2_label_policy` |
| Program architecture | `single_pass` (nine families) |
| LLM extraction | Identical across arms; only post-recovery differs on `epilepsy_cause` |

## Arms

| Arm | implementation_variant | Program variant | Config |
| --- | --- | --- | --- |
| L1 | `cause_bridge_l1_control` | `exect_s3_field_family_single_pass` | `exect_s3_cause_l1_baseline_full_gpt4_1_mini.json` |
| K0+K1 | `cause_synonym_plural_v1+cause_modifier_strip_v1` | `exect_s3_field_family_cause_bridge_k0_k1_single_pass` | `exect_s3_cause_k0_k1_full_gpt4_1_mini.json` |

Primitive: K0+K1 applies `exect.epilepsy_cause.cui_phrase_bridge.v1` tiers on `epilepsy_cause` recovery only.

## Primary and guardrail metrics

| Metric | Role |
| --- | --- |
| `epilepsy_cause` F1 | **Primary** |
| `investigation`, `seizure_type`, `comorbidity` F1 | **Regression guard** (no ≥2pp drop vs L1) |
| Pooled micro F1 | Diagnostic only — unstable on 7-label cause family |
| Per-doc qualitative queue (EA0150, EA0016, EA0137) | Tag label deltas; not a standalone promotion gate |

## Confirmation gates (full validation)

| Outcome | Rule |
| --- | --- |
| **Hold (operational candidate)** | Cause F1 ≥ L1 + **3pp** and regression guards pass |
| **Hold (inconclusive)** | Cause F1 +1–2pp with guards pass |
| **Reject (arm)** | Cause F1 ≤ L1 or regression guard fails |
| **Mechanism** | Not closable from one full-validation pair |

External anchor (not in-session control): GPT S3 v1.2 full `runs/exect_s3_validation_full_gpt4_1_mini_20260519T235439Z` — 72.1% micro; sparse cause support (7 labels).

Cap-25 anchor: K0+K1 20.0% cause F1 vs L1 0.0% (+20pp; n=3 labels on cap-25).

## Residual-slice context

3-doc replay on stored full-validation raw labels is **null** (28.6% cause F1 both arms). Queue failures are K2 TBI atomization (EA0150), plural gold `strokes` vs singular `stroke` (EA0016), and recall miss `hypoxia during birth` (EA0137) — not K0+K1 trigger surfaces on the anchor run. Full validation still required because cap-25 showed a real modifier-strip win (EA0059) and fresh LLM outputs may differ.

## Run order

1. Dry-run both configs
2. Full validation L1 then K0+K1 (~40 LLM calls each)
3. Inspection `docs/experiments/exect/exect_s3_epilepsy_cause_bridge_gpt_full_validation_v1_inspection_20260521.md`
4. Registry rows with `decision_scope: arm`

## Open cells

- K2 TBI atomization tier (`cause_tbi_atomized_v1`) for EA0150-class composites
- K3 template strip (`secondary to X` → `X`) for EA0124-class surfaces
- S4 cause-bridge port (no-model) — implementation plan item 31
- Qwen port only after GPT full-validation hold
