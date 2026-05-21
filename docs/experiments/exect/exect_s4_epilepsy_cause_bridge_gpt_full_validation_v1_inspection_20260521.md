# ExECT S4 Epilepsy Cause Bridge GPT Full Validation v1 — Inspection

Date: 2026-05-21  
Pre-registration: `docs/experiments/exect/exect_s4_epilepsy_cause_bridge_gpt_full_validation_v1_preregistration_20260521.md`  
decision_scope: **arm**

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | `exect_s4_field_family` |
| Comparison group | `exect_s4_epilepsy_cause_bridge_gpt_full_validation_v1` |
| Research axis | 3 |
| stage_graph_id | `g1_l1_policy_bridges` |
| varied_factor | `implementation_variant` |
| decision_scope | arm |

## Arms

| arm_id | run_id | epilepsy_cause F1 | micro F1 | gate |
| --- | --- | ---: | ---: | --- |
| L1 | `exect_s4_cause_l1_baseline_full_gpt4_1_mini_20260521T092335Z` | **10.5%** | 66.5% | control |
| K0+K1 | `exect_s4_cause_k0_k1_full_gpt4_1_mini_20260521T092346Z` | **21.1%** | 66.8% | pass primary |

Configs: `exect_s4_cause_l1_baseline_full_gpt4_1_mini.json`, `exect_s4_cause_k0_k1_full_gpt4_1_mini.json`

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| L1 | hold (control) | arm | Matches external S4 v1.2 cause F1 (10.5%) |
| K0+K1 | **hold (operational candidate)** | arm | +10.6pp cause F1; regression guards pass |

## Primary metric read

| Metric | L1 | K0+K1 | Δ (K0+K1 − L1) |
| --- | ---: | ---: | ---: |
| epilepsy_cause F1 | **10.5%** | **21.1%** | **+10.6pp** |
| epilepsy_cause precision | 8.3% | 16.7% | +8.4pp |
| epilepsy_cause recall | 14.3% | 28.6% | +14.3pp |
| epilepsy_cause support | 7 | 7 | — |

Promotion gate requires **≥+3.0pp** cause F1 with regression guards — **met**.

## Regression guard (S4 burden families)

| Family | L1 F1 | K0+K1 F1 | Δ |
| --- | ---: | ---: | ---: |
| medication_temporality | 62.5% | 62.5% | 0 |
| seizure_frequency | 50.6% | 50.6% | 0 |
| investigation | 96.7% | 96.7% | 0 |

No preregistered guard regressed ≥2pp. Pooled micro F1 +0.3pp (66.5% → 66.8%).

Note: L1 seizure_frequency F1 (50.6%) is **+4.9pp** vs external S4 v1.2 anchor (45.7%, `…071248Z`) on the same split — likely LLM output / cache lineage difference, not cause-bridge effect. K0+K1 matches L1 on frequency, so the bridge did not move this family.

## Label deltas (epilepsy_cause)

| Doc | L1 | K0+K1 | Mechanism |
| --- | --- | --- | --- |
| EA0059 | `early life meningitis` (FP) | `meningitis` (TP) | K1 modifier strip |
| EA0170 | `recurrent right hemisphere intracerebral haemorrhage` (FP) | `intracerebral hemorrhage` (FP) | K1 strip + US spelling; gold `intracerebral haemorrhage` — no F1 gain |

38/40 docs identical on cause labels; 2/40 have string deltas. Mirrors S3 full-validation (`…091816Z` / `…091824Z`).

## Qualitative read

S4 port reproduces S3 full-validation cause lift on the eleven-family pass: **1/7** gold cause label recovered (EA0059) with zero movement on medication_temporality, seizure_frequency, or investigation. Sparse cause support remains low; pooled micro lift is small (+0.3pp).

**Do not** mechanism-close CUIPhrase cause bridges from one GPT S4 full-validation pair.

## Mechanism review

Not claimed. One implementation variant on one model track; K2/K3 tiers untested.

## Open cells

- K2 TBI atomization for EA0150-class composites
- K3 template strip for EA0124-class surfaces
- S4 default program variant update (operational) pending explicit freeze decision
- Qwen port only after operational freeze
- MT G0 guard and frequency structured slots remain separate tracks

## References

- S3 full-validation inspection: `exect_s3_epilepsy_cause_bridge_gpt_full_validation_v1_inspection_20260521.md`
- S4 residual synthesis: `exect_s4_residual_error_analysis_20260521.md`
- External anchor: `runs/exect_s4_validation_full_gpt4_1_mini_20260520T071248Z`

## Next steps

1. Register both arms in `docs/experiments/synthesis/experiment_registry.json` with `decision_scope: arm`.
2. Consider operational freeze of `exect_s4_field_family_cause_bridge_k0_k1_single_pass` for S4 cause recovery (paired with S3 default update).
3. Design K2 tier if EA0150 composite FPs persist.
