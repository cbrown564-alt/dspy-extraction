# ExECT S4 Frequency Structured Slots GPT Cap-25 v1 — Inspection

Date: 2026-05-21  
Pre-registration: `docs/experiments/exect/exect_s4_frequency_structured_slots_gpt_cap25_v1_preregistration_20260521.md`  
decision_scope: **arm**

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | S4 field-family (11 families) |
| Comparison group | `exect_s4_frequency_structured_slots_gpt_cap25_v1` |
| Research axis | 3 — structured frequency slots + multi-label retention |
| stage_graph_id | `g1_l1_policy_bridges` |
| varied_factor | `implementation_variant` |
| decision_scope | arm |

## Arms

| arm_id | run_id | seizure_frequency F1 | micro F1 | evidence support | gate |
| --- | --- | ---: | ---: | ---: | --- |
| R0 | `exect_s4_frequency_surface_r0_control_cap25_gpt4_1_mini_20260521T072357Z` | **51.0%** | 69.5% | 87.9% | pass (reused) |
| S2 | `exect_s4_frequency_slots_s2_structured_cap25_gpt4_1_mini_20260521T075559Z` | **51.0%** | 69.5% | 86.2% | fail primary |

R0 reused from `exect_s4_frequency_surface_repair_gpt_cap25_v1` (identical control config).

Configs:

- R0: `configs/experiments/exect_s4_frequency_slots_r0_control_cap25_gpt4_1_mini.json`
- S2: `configs/experiments/exect_s4_frequency_slots_s2_structured_cap25_gpt4_1_mini.json`

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| R0 | hold (control) | arm | v1.2 inline bridge baseline |
| S2 | **hold (inconclusive)** | arm | 0.0pp vs R0; null on cap-25 |

## Primary metric read

| Metric | R0 | S2 | Δ (S2 − R0) |
| --- | ---: | ---: | ---: |
| seizure_frequency F1 | **51.0%** | **51.0%** | **0.0pp** |
| seizure_frequency recall | 52.0% | 52.0% | 0.0pp |
| seizure_frequency precision | 50.0% | 50.0% | 0.0pp |

Promotion gate requires **≥+3.0pp** — not met.

## Frozen S3 regression guard

| Family | R0 F1 | S2 F1 | Δ |
| --- | ---: | ---: | ---: |
| diagnosis | 95.2% | 95.2% | 0 |
| seizure_type | 90.9% | 90.9% | 0 |
| annotated_medication | 69.0% | 69.0% | 0 |
| investigation | 93.8% | 93.8% | 0 |
| comorbidity | 73.0% | 73.0% | 0 |
| birth_history | 50.0% | 50.0% | 0 |

No frozen S3 family regressed ≥2pp. Pooled micro F1 identical (69.5%).

## Implementation read

S2 injects ExECT structured frequency slot table + JSON (`exect.frequency.structured_slots.v1`) before the note and applies `multi_label_retention` post-bridge recovery. Cap-25 metrics are **label-identical** to R0 on this slice — structured slot presentation did not change scored outputs vs inline bridge alone.

Contrast with rejected arms:

- **R1 post-merge** (`frequency_post_merge_v1_3`): −2.9pp — full note union
- **H2 pre-vocab**: different comparison group; −2.0pp vs L1

## Mechanism review

Not claimed. One new `implementation_variant` on cap-25 with null primary delta does not close structured-slot or multi-label-retention mechanism classes.

## Open cells

- Prompt-policy / example-strategy variants with new IDs
- Narrower quantified-only slot fill (without full note union)
- Frequency-heavy residual slice replay on S2 vs R0 predictions
- Full validation (40) — not triggered
- Qwen port — deferred

## Recommended next steps

1. **Do not promote** S2 `frequency_structured_slots_v1` from cap-25 alone.
2. Keep **R0 / v1.2 inline bridge** as S4 frequency operational default on cap-25 anchors.
3. Optional: replay frequency-mismatch residual queue to see whether bridge flags differ despite tied F1.
4. Next frequency Axis-3 cell needs a **new** `implementation_variant` (e.g. model-facing structured output fields or quantified-only slot fill).

## Explicit non-claims

- No mechanism reject for structured slots or multi-label retention
- Not ExECTv2 Table 1 reproduction
- Not comparable to nine-family S1–S3 micro headlines
