# ExECT S3 Epilepsy Cause Residual-Slice Replay — Inspection

Date: 2026-05-21  
Comparison group: `exect_s3_epilepsy_cause_bridge_gpt_cap25_v1` (deterministic replay only)  
Fixture: `data/fixtures/exect_s3_epilepsy_cause_residual_slice.json`  
Reference: `runs/exect_s3_validation_full_gpt4_1_mini_20260519T235439Z`  
decision_scope: **arm**

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema | `exect_s3_field_family` |
| Research axis | 3 |
| varied_factor | `implementation_variant` (post-module bridges only) |
| decision_scope | arm |

## Question

On the fixed 3-doc epilepsy_cause qualitative queue (EA0150, EA0016, EA0137), do K0+K1 bridges change scored cause labels when replayed on stored full-validation raw cause outputs?

Cap-25 grid showed +20pp cause F1 with one doc delta (EA0059); this slice tests whether the same tiers help on the preregistered qualitative queue using anchor-run raw labels.

## Arms (replay, no new model calls)

| Arm | Bridge tiers | Queue cause F1 |
| --- | --- | ---: |
| L1 | (none) | **28.6%** |
| K0+K1 | `cause_synonym_plural_v1` + `cause_modifier_strip_v1` | **28.6%** |

Script: `scripts/replay_exect_s3_epilepsy_cause_residual_slice.py`  
Artifact: `artifacts/exect_s3_epilepsy_cause_residual_replay_20260521/summary.json`

## Headline

| Metric | Value |
| --- | ---: |
| K0+K1 vs L1 F1 delta | **0.0pp** |
| Doc-level fixes vs L1 | **0** |
| Doc-level regressions vs L1 | **0** |

## Per-document read

| Doc | L1 F1 | K0+K1 F1 | Notes |
| --- | ---: | ---: | --- |
| EA0150 | 0% | 0% | Composite `traumatic brain injury` vs gold `traumatic` — needs **K2** TBI atomization, not K0+K1 |
| EA0016 | 0% | 0% | Model `stroke` vs gold plural `strokes`; K0 maps plural→singular, not reverse |
| EA0137 | 66.7% | 66.7% | TP `perinatal trauma`; FN `hypoxia during birth` is recall miss, not bridge surface |

## Outcomes

| Arm | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| L1 | hold (control) | arm | Replay baseline |
| K0+K1 | **hold (inconclusive on slice)** | arm | Null on queue; cap-25 proceed signal unchanged |

**Do not** reject K0+K1 from slice null alone. Cap-25 showed modifier-strip win on EA0059; full-validation prereg is ready (`exect_s3_epilepsy_cause_bridge_gpt_full_validation_v1_preregistration_20260521.md`).

## Mechanism review

Not claimed. Replay uses one full-validation prediction set; K0+K1 not re-tested across independent LLM samples.

## Open cells

- Full validation L1 vs K0+K1 (~40 records each)
- K2/K3 tiers for EA0150 / EA0124-class failures
- S4 cause-bridge port after full-validation read

## Next steps

1. Run `exect_s3_epilepsy_cause_bridge_gpt_full_validation_v1` (configs ready).
2. Wire K0+K1 into S4 artifact recovery (implementation plan item 31).
3. Design K2 TBI atomization if full validation shows composite FPs persist.

## References

- Cap-25 inspection: `exect_s3_epilepsy_cause_bridge_gpt_cap25_v1_inspection_20260521.md`
- Full-validation prereg: `exect_s3_epilepsy_cause_bridge_gpt_full_validation_v1_preregistration_20260521.md`
- Design: `exect_s3_epilepsy_cause_cui_phrase_bridge_design_20260521.md`
