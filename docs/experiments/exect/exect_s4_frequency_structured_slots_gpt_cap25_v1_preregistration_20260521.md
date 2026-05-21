# ExECT S4 Frequency Structured Slots GPT Cap-25 v1 — Preregistration

Date: 2026-05-21  
Status: Complete — `docs/experiments/exect/exect_s4_frequency_structured_slots_gpt_cap25_v1_inspection_20260521.md`  
Parent plan: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md` (item 23)  
Parent synthesis: `docs/experiments/exect/exect_s4_residual_error_analysis_20260521.md`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | S4 field-family (11 families) |
| Research axis | 3 — structured frequency slots + multi-label retention |
| Comparison group | `exect_s4_frequency_structured_slots_gpt_cap25_v1` |
| Primary varied factor | `implementation_variant` |
| `stage_graph_id` | `g1_l1_policy_bridges` |
| `bridge_mode` | inline S3 bridges unchanged; frequency varies slot presentation + retention recovery |
| decision_scope target | `arm` |
| Mechanism closure allowed? | No |

## Hypothesis

Exposing note-anchored seizure-frequency labels as **ExECT structured slots** (quantified / zero-rate / qualitative / seizure-free) plus **multi-label retention recovery** improves `seizure_frequency` F1 on cap-25 versus frozen v1.2 inline bridge (R0), without regressing frozen S3 families.

This is **not** Gan monthly normalization, **not** H2 pre-vocab candidate injection, and **not** R1 full post-merge (arm-reject on cap-25).

## Motivation

Full-validation residual read (`docs/experiments/exect/exect_s4_residual_error_analysis_20260521.md`) shows frequency burden from multi-label collapse, qualitative co-label misses, and prose≠template surfaces. R1 post-merge (`frequency_post_merge_v1_3`) regressed −2.9pp on cap-25. The next cell tests structured slot presentation with narrower partial-block fill only when the model emits at least one supported frequency label.

## Fixed Controls

| Control | Value |
| --- | --- |
| Split | `exectv2_fixed_v1:validation` |
| Cap | 25 (Lane A order) |
| Model | GPT 4.1-mini |
| Scorer | `exect_s4_field_family_deterministic_v1` |
| Program architecture | `single_pass` (eleven-family) |
| S3 bridges | Frozen v1.2 inline bridges for nine S3 families |
| Investigation guard | v1.2 S4-only guard retained in both arms |
| LLM calls | One pass per record |

## Arms

| Arm | implementation_variant | Program variant | Config |
| --- | --- | --- | --- |
| R0 | `frequency_bridge_v1_2_control` | `exect_s4_field_family_single_pass` | `exect_s4_frequency_slots_r0_control_cap25_gpt4_1_mini.json` |
| S2 | `frequency_structured_slots_v1` | `exect_s4_field_family_frequency_structured_slots_single_pass` | `exect_s4_frequency_slots_s2_structured_cap25_gpt4_1_mini.json` |

### S2 implementation (pre-run spec)

1. **Prompt:** inject `format_exect_frequency_slot_payload_for_prompt` table + JSON from note-anchored audited labels (`exect.frequency.structured_slots.v1`).
2. **Recovery:** `recover_exect_frequency_benchmark_values_with_multi_label_retention` on model outputs:
   - v1.2 inline bridge (unchanged repair/co-label base path)
   - widened co-label retention when model engaged frequency and note has change cues
   - partial multi-label slot fill: union missing note-anchored labels **only when** model emitted ≥1 supported frequency label
   - spurious seizure-free guard (same as R1)

Do **not** clear all frequency predictions when note regex finds no templates. Do **not** union note labels when model abstained entirely.

## Primary and Secondary Metrics

| Metric | Role |
| --- | --- |
| `seizure_frequency` field-family F1 | **Primary** |
| Pooled micro F1 (11 fam) | Diagnostic |
| Frozen S3 family F1 | Regression guard |
| Evidence quote support | Gate >= 85% |
| Bridge flags per arm | Diagnostic |

## Gates

| Decision | Rule |
| --- | --- |
| **Hold / promote to full validation** | S2 seizure_frequency F1 ≥ R0 + **3.0pp** on cap-25, no frozen S3 family regresses **≥2pp** vs R0, both arms pass evidence gate |
| **Hold (inconclusive)** | S2 improves frequency but delta < 3.0pp |
| **Reject arm** | S2 seizure_frequency F1 ≤ R0, or S3 regression ≥2pp, or evidence gate failure |
| **Mechanism closure** | Forbidden from this group alone |

## Reference Runs

| Reference | Run suffix | seizure_frequency F1 | Notes |
| --- | --- | ---: | --- |
| R0 (surface repair group) | `…T072357Z` | **51.0%** | Reuse as control |
| R1 post-merge (reject) | `…T072445Z` | 48.1% | Do not rerun |

## Explicit Non-Goals

- Do not port Gan slot_payload monthly normalization
- Do not rerun R1 `frequency_post_merge_v1_3`
- Do not vary stage graph or add verify-repair second pass
- Sparse families (onset, when_diagnosed, cause, birth) deferred per residual synthesis
