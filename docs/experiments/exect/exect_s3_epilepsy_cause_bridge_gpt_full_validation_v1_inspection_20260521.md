# ExECT S3 Epilepsy Cause Bridge GPT Full Validation v1 — Inspection

Date: 2026-05-21  
Pre-registration: `docs/experiments/exect/exect_s3_epilepsy_cause_bridge_gpt_full_validation_v1_preregistration_20260521.md`  
decision_scope: **arm**

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | `exect_s3_field_family` |
| Comparison group | `exect_s3_epilepsy_cause_bridge_gpt_full_validation_v1` |
| Research axis | 3 |
| stage_graph_id | `g1_l1_policy_bridges` |
| varied_factor | `implementation_variant` |
| decision_scope | arm |

## Arms

| arm_id | run_id | epilepsy_cause F1 | micro F1 | gate |
| --- | --- | ---: | ---: | --- |
| L1 | `exect_s3_cause_l1_baseline_full_gpt4_1_mini_20260521T091816Z` | **11.1%** | 72.5% | control |
| K0+K1 | `exect_s3_cause_k0_k1_full_gpt4_1_mini_20260521T091824Z` | **22.2%** | 72.9% | pass primary |

Configs: `exect_s3_cause_l1_baseline_full_gpt4_1_mini.json`, `exect_s3_cause_k0_k1_full_gpt4_1_mini.json`

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| L1 | hold (control) | arm | Full 40-record validation baseline |
| K0+K1 | **hold (operational candidate)** | arm | +11.1pp cause F1; 1 net TP fix (EA0059); regression guards pass |

## Primary metric read

| Metric | L1 | K0+K1 | Δ (K0+K1 − L1) |
| --- | ---: | ---: | ---: |
| epilepsy_cause F1 | **11.1%** | **22.2%** | **+11.1pp** |
| epilepsy_cause precision | 9.1% | 18.2% | +9.1pp |
| epilepsy_cause recall | 14.3% | 28.6% | +14.3pp |
| epilepsy_cause support | 7 | 7 | — |

Promotion gate requires **≥+3.0pp** cause F1 with regression guards — **met**.

## Regression guard (frozen families)

| Family | L1 F1 | K0+K1 F1 | Δ |
| --- | ---: | ---: | ---: |
| investigation | 93.1% | 93.1% | 0 |
| seizure_type | 78.1% | 78.1% | 0 |
| comorbidity | 61.9% | 61.9% | 0 |

No frozen family regressed ≥2pp. Pooled micro F1 +0.4pp (72.5% → 72.9%).

## Label deltas (epilepsy_cause)

| Doc | L1 | K0+K1 | Mechanism |
| --- | --- | --- | --- |
| EA0059 | `early life meningitis` (FP) | `meningitis` (TP) | K1 modifier strip |
| EA0170 | `recurrent right hemisphere intracerebral haemorrhage` (FP) | `intracerebral hemorrhage` (FP) | K1 strip + US spelling; gold uses `intracerebral haemorrhage` — **no F1 gain** |

39/40 docs identical on cause F1; 2/40 have label-string deltas. Qualitative queue (EA0150, EA0016, EA0137) unchanged.

## Qualitative read

Full validation confirms cap-25 signal: K0+K1 bridges recover **1/7** gold cause label (EA0059 meningitis) via modifier strip without touching other families. EA0170 shows bridge activity but British/American spelling mismatch prevents a TP. Sparse-family support remains low (7 labels); pooled micro lift is small (+0.4pp).

**Do not** mechanism-close CUIPhrase cause bridges from one GPT full-validation pair.

## Mechanism review

Not claimed. One implementation variant on one model track; K2 TBI and K3 template tiers untested.

## Open cells

- K2 TBI atomization for EA0150-class composites
- K3 template strip for EA0124-class surfaces
- S4 cause-bridge port (implementation plan item 31)
- Qwen port only after operational freeze decision
- Comorbidity C0 on S3/S4 (separate track)

## References

- Cap-25 inspection: `exect_s3_epilepsy_cause_bridge_gpt_cap25_v1_inspection_20260521.md`
- Residual slice replay: `exect_s3_epilepsy_cause_residual_slice_replay_20260521.md`
- External anchor: `runs/exect_s3_validation_full_gpt4_1_mini_20260519T235439Z` (72.1% micro; cause F1 not isolated in headline)

## Next steps

1. Wire K0+K1 cause bridge into S4 artifact recovery path (no-model).
2. Update S3 default program variant to `exect_s3_field_family_cause_bridge_k0_k1_single_pass` only after S4 port + regression guards preregistered.
3. Design K2 tier if EA0150 composite FPs persist on S4.
