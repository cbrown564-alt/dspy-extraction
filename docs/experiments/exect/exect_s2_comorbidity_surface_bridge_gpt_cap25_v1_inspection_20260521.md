# ExECT S2 Comorbidity Surface Bridge GPT Cap-25 v1 — Inspection

Date: 2026-05-21  
Pre-registration: `docs/experiments/exect/exect_s2_comorbidity_surface_bridge_gpt_cap25_v1_preregistration_20260521.md`  
decision_scope: **arm**

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | `exect_s2_field_family` |
| Comparison group | `exect_s2_comorbidity_surface_bridge_gpt_cap25_v1` |
| Research axis | 3 |
| stage_graph_id | `g1_l1_policy_bridges` |
| varied_factor | `implementation_variant` |
| decision_scope | arm |

## Arms

| arm_id | run_id | comorbidity F1 | micro F1 | gate |
| --- | --- | ---: | ---: | --- |
| L1 | `exect_s2_comorbidity_l1_baseline_cap25_gpt4_1_mini_20260521T082618Z` | **85.7%** | 87.5% | control |
| C0 | `exect_s2_comorbidity_c0_cap25_gpt4_1_mini_20260521T082626Z` | **85.7%** | 87.5% | null |
| C0+C1 | `exect_s2_comorbidity_c0_c1_cap25_gpt4_1_mini_20260521T082630Z` | **85.7%** | 87.5% | null |

Configs: `exect_s2_comorbidity_l1_baseline_cap25_gpt4_1_mini.json`, `exect_s2_comorbidity_c0_cap25_gpt4_1_mini.json`, `exect_s2_comorbidity_c0_c1_cap25_gpt4_1_mini.json`

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| L1 | hold (control) | arm | Frozen v1.3 single-pass |
| C0 | **hold (inconclusive)** | arm | 0.0pp vs L1; 0/25 doc label diffs |
| C0+C1 | **hold (inconclusive)** | arm | 0.0pp vs L1; 0/25 doc label diffs |

## Primary metric read

| Metric | L1 | C0 | C0+C1 | Δ (best − L1) |
| --- | ---: | ---: | ---: | ---: |
| comorbidity F1 | **85.7%** | **85.7%** | **85.7%** | **0.0pp** |
| comorbidity precision | 77.1% | 77.1% | 77.1% | 0 |
| comorbidity recall | 96.4% | 96.4% | 96.4% | 0 |

Promotion gate requires **≥+3.0pp** comorbidity F1 — not met.

## Regression guard (frozen families)

| Family | L1 F1 | C0 F1 | C0+C1 F1 |
| --- | ---: | ---: | ---: |
| diagnosis | 90.5% | 90.5% | 90.5% |
| seizure_type | 83.1% | 83.1% | 83.1% |
| investigation | 88.2% | 88.2% | 88.2% |
| annotated_medication | 91.8% | 91.8% | 91.8% |

No family regressed ≥2pp.

## Qualitative read

Post-module C0/C1 bridges (`comorbidity_atomization_tbi_v1`, `comorbidity_surface_plural_v1`) did not change any scored comorbidity label on this cap-25 slice. Fixture targets (EA0150 TBI, EA0170 haemorrhage) are **not in** the validation cap-25 prefix — bridges are wired but inactive on matched LLM outputs here.

**Do not** mechanism-close comorbidity atomization from this null. Residual-slice replay on the 6-doc queue or full validation is required before rejecting C0/C1 tiers.

## Mechanism review

Not claimed. One cap-25 grid with identical predictions across arms does not close `exect.comorbidity.atomization_bridge.v1`.

## Open cells

- ~~Residual-slice replay on EA0150, EA0170, EA0179 qualitative queue~~ **Done** — `exect_s2_comorbidity_residual_slice_replay_20260521.md` (C0 +14pp on 6-doc queue)
- C2/C3 symptom-scope tiers
- S3 nine-family port after slice shows label deltas
- Whether LLM already atomizes surfaces that bridges target on cap-25

## References

- Design: `docs/experiments/exect/exect_s2_comorbidity_surface_policy_design_20260521.md`
- Full anchor: `runs/exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` (69.3% comorbidity F1)
