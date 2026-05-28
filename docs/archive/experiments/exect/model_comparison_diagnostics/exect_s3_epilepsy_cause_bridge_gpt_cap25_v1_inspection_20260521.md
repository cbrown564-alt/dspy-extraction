# ExECT S3 Epilepsy Cause Bridge GPT Cap-25 v1 — Inspection

Date: 2026-05-21  
Pre-registration: `docs/experiments/exect/exect_s3_epilepsy_cause_bridge_gpt_cap25_v1_preregistration_20260521.md`  
decision_scope: **arm**

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | `exect_s3_field_family` |
| Comparison group | `exect_s3_epilepsy_cause_bridge_gpt_cap25_v1` |
| Research axis | 3 |
| stage_graph_id | `g1_l1_policy_bridges` |
| varied_factor | `implementation_variant` |
| decision_scope | arm |

## Arms

| arm_id | run_id | epilepsy_cause F1 | micro F1 | gate |
| --- | --- | ---: | ---: | --- |
| L1 | `exect_s3_cause_l1_baseline_cap25_gpt4_1_mini_20260521T090542Z` | **0.0%** | 78.1% | control |
| K0+K1 | `exect_s3_cause_k0_k1_cap25_gpt4_1_mini_20260521T090550Z` | **20.0%** | 78.7% | pass primary |

Configs: `exect_s3_cause_l1_baseline_cap25_gpt4_1_mini.json`, `exect_s3_cause_k0_k1_cap25_gpt4_1_mini.json`

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| L1 | hold (control) | arm | Frozen v1.2 nine-family pass; I0 investigation guard on recovery |
| K0+K1 | **hold (cap-25 proceed)** | arm | +20.0pp cause F1; 1/25 doc label delta; regression guards pass |

## Primary metric read

| Metric | L1 | K0+K1 | Δ (K0+K1 − L1) |
| --- | ---: | ---: | ---: |
| epilepsy_cause F1 | **0.0%** | **20.0%** | **+20.0pp** |
| epilepsy_cause precision | 0.0% | 14.3% | +14.3pp |
| epilepsy_cause recall | 0.0% | 33.3% | +33.3pp |
| epilepsy_cause support | 3 | 3 | — |

Promotion gate requires **≥+3.0pp** cause F1 with regression guards — **met** (support n=3; interpret cautiously).

## Regression guard (frozen families)

| Family | L1 F1 | K0+K1 F1 | Δ |
| --- | ---: | ---: | ---: |
| investigation | 93.8% | 93.8% | 0 |
| seizure_type | 88.2% | 88.2% | 0 |
| comorbidity | 73.0% | 73.0% | 0 |

No frozen family regressed ≥2pp. Pooled micro F1 +0.6pp (78.1% → 78.7%).

## Label deltas (epilepsy_cause)

| Doc | L1 | K0+K1 | Mechanism |
| --- | --- | --- | --- |
| EA0059 | `early life meningitis` (FP) | `meningitis` (TP) | K1 modifier strip (`early life` prefix removed) |

24/25 docs identical on scored cause labels. Residual FPs on cap-25 (EA0008 meningioma resection, EA0016 stroke, EA0029 JME, EA0061 cortical dysplasia, EA0098 lobe damage, EA0124 secondary to measles) unchanged — K0 synonym/plural did not fire on this slice.

## Qualitative read

K0+K1 bridges recover one gold CUIPhrase (`meningitis` at EA0059) where the LLM emitted modifier-prefixed surface text. This matches fixture intent for K1 modifier strip. Sparse-family support (3 labels on cap-25) means pooled micro and even cause F1 are unstable; full-validation confirm on qualitative queue docs EA0150, EA0016, EA0137 is required before operational freeze.

**Do not** mechanism-close CUIPhrase cause bridges from one cap-25 doc delta.

## Mechanism review

Not claimed. One implementation variant on one cap-25 slice with n=3 cause support does not close `exect.epilepsy_cause.cui_phrase_bridge.v1`.

## Open cells

- K2 TBI atomization tier for cause (deferred in design)
- S4 cause-bridge port (no-model) after fixtures pass — item 31 in implementation plan
- Full-validation confirm on sparse-family qualitative queue
- Qwen port only after GPT full-validation hold
- Optional S2 C0 cap-25 re-run (comorbidity grid was null; residual slice showed +14pp on 6-doc queue)

## References

- Design: `docs/experiments/exect/exect_s3_epilepsy_cause_cui_phrase_bridge_design_20260521.md`
- Full anchor: `runs/exect_s3_validation_full_gpt4_1_mini_20260519T235439Z` (72.1% micro)
- Comorbidity residual context: `docs/experiments/exect/exect_s2_comorbidity_residual_slice_replay_20260521.md`

## Next steps

1. Wire K0+K1 cause bridge into S4 artifact recovery path (no-model; when S4 fixtures green).
2. Full-validation prereg for K0+K1 on S3 if sparse-family queue shows consistent label deltas.
3. Do **not** claim cause-bridge mechanism closed from cap-25 alone.
