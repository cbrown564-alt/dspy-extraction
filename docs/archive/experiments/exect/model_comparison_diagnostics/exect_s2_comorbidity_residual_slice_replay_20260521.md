# ExECT S2 Comorbidity Residual-Slice Replay — Inspection

Date: 2026-05-21  
Comparison group: `exect_s2_comorbidity_surface_bridge_gpt_cap25_v1` (deterministic replay only)  
Fixture: `data/fixtures/exect_s2_comorbidity_residual_slice.json`  
Reference: `runs/exect_s2_validation_full_gpt4_1_mini_20260519T231223Z`  
decision_scope: **arm**

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema | `exect_s2_field_family` |
| Research axis | 3 |
| varied_factor | `implementation_variant` (post-module bridges only) |
| decision_scope | arm |

## Question

On the fixed 6-doc comorbidity qualitative queue, do C0/C1 bridges change scored comorbidity labels when replayed on stored full-validation raw comorbidity outputs?

Cap-25 grid was null because queue docs were not in the cap-25 failure surface for comorbidity (`exect_s2_comorbidity_surface_bridge_gpt_cap25_v1_inspection_20260521.md`).

## Arms (replay, no new model calls)

| Arm | Bridge tiers | Queue comorbidity F1 |
| --- | --- | ---: |
| L1 | (none) | **23.1%** |
| C0 | `comorbidity_atomization_tbi_v1` | **37.0%** |
| C0+C1 | C0 + `comorbidity_surface_plural_v1` | **37.0%** |

Script: `scripts/replay_exect_s2_comorbidity_residual_slice.py`  
Artifact: `artifacts/exect_s2_comorbidity_residual_replay_20260521/summary.json`

## Headline

| Metric | Value |
| --- | ---: |
| C0 vs L1 F1 delta | **+14.0pp** |
| C0+C1 vs L1 F1 delta | **+14.0pp** |
| Doc-level fixes vs L1 | **2** |
| Doc-level regressions vs L1 | **0** |

## Per-document read

| Doc | L1 F1 | C0 F1 | Notes |
| --- | ---: | ---: | --- |
| EA0150 | 22.2% | **60.0%** | TBI atomization: `traumatic` + `brain injury` TPs vs composite FP |
| EA0170 | 0% | 0% | C1 normalizes `haemorrhage` spelling; gold wants plural `hemorrhages` / `cerebral vascular events` — bridge insufficient |
| EA0179 | 33.3% | 33.3% | Recall block unchanged (episodes/syncope/febrile) |
| EA0136 | 0% | 0% | Unchanged |
| EA0090 | 66.7% | 66.7% | Unchanged |
| EA0148 | 0% | 0% | Unchanged |

## Outcomes

| Arm | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| L1 | hold (control) | arm | Replay baseline |
| C0 | **hold (proceed cap-25)** | arm | +14pp on slice; EA0150 fix; no regressions |
| C0+C1 | hold (inconclusive vs C0) | arm | No slice lift beyond C0 on this queue |

**Do not** mechanism-close comorbidity atomization. Slice supports proceeding with cap-25 **and** considering C0 default on S3 comorbidity recovery after S3 cause grid.

## Mechanism review

Not claimed. Replay uses one full-validation prediction set; bridges not re-tested across independent LLM samples.

## Open cells

- Cap-25 re-run with C0 variant (may still null if LLM already atomizes)
- C2/C3 tiers for EA0179 recall / EA0148 scope
- Port C0 to S3 `_recover_s2_comorbidity_raw_values` default path

## Next steps

1. Run `exect_s3_epilepsy_cause_bridge_gpt_cap25_v1` (prereg ready).
2. Optional: S2 cap-25 C0 re-run after slice proceed signal.
3. Wire C0 comorbidity tiers into S3/S4 when preregistered.

## References

- Cap-25 inspection: `exect_s2_comorbidity_surface_bridge_gpt_cap25_v1_inspection_20260521.md`
- Design: `exect_s2_comorbidity_surface_policy_design_20260521.md`
