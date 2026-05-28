# ExECT S1 Stage-Executor GPT Cap-25 v1 Preregistration

Date: 2026-05-21  
Status: Cap-25 complete — see `docs/experiments/exect/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md`  
Comparison group: `exect_s1_stage_executor_gpt_cap25_v1`  
Related: `docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md`, `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md`, `docs/experiments/exect/exect_negative_probe_synthesis_20260520.md`

## Research Question

On the Phase 5a winning skeleton `g1_l1_policy_bridges`, does bridge placement (inline vs post) or per-family deterministic hint injection change benchmark-facing micro F1 when extraction, prompt policy, and scorer are fixed?

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | S1 field-family |
| Research axis | 2 — per-stage executor |
| Comparison group | `exect_s1_stage_executor_gpt_cap25_v1` |
| Primary varied factor | `stage_executor` |
| Anchor `stage_graph_id` | `g1_l1_policy_bridges` |
| decision_scope target | `arm` |
| Mechanism closure allowed? | No |

## Fixed Controls

| Control | Value |
| --- | --- |
| Split | `exectv2_fixed_v1:validation` |
| Cap | First 25 validation records, same order as Phase 5a / Lane A cap-25 |
| Model | GPT 4.1-mini |
| Scorer | `exect_field_family_deterministic_v1` |
| Primary metric | Pooled micro F1 |
| Diagnostics | Per-family F1, evidence quote support, bridge Δ vs E1 |
| Prompt | `exect_s0_s1_field_family_v4_10_label_policy` |
| Few-shot | embedded benchmark-facing label-policy examples |
| Stage graph | `g1_l1_policy_bridges` for all arms |

## Bridge mode (documented per arm)

| Arm | `stage_executor` | `bridge_mode` | `repair_policy` |
| --- | --- | --- | --- |
| E1 | `llm_extract_inline_bridges` | inline | `none` |
| E2 | `llm_extract_post_bridges` | post_module | `artifact_benchmark_bridge_only` |
| E3–E5 | det hints + LLM extract | inline | `none` |

## Arms

| Arm | `stage_executor` | Pre-stage | Extraction | program_variant | Priority |
| --- | --- | --- | --- | --- | --- |
| E1 | `llm_extract_inline_bridges` | none | LLM single-pass | `exect_s0_s1_field_family_single_pass` | Required — Phase 5a S1 reproduction |
| E2 | `llm_extract_post_bridges` | none | LLM single-pass + post bridges | `exect_s0_s1_field_family_single_pass` | Required — bridge placement |
| E3 | `det_all_family_hints_llm_extract` | all-family audited candidates | LLM single-pass | `exect_s0_s1_field_family_pre_vocab_single_pass` | Required — full cap-25 H2 shape |
| E4 | `det_seizure_hints_llm_extract` | seizure-type candidates only | LLM single-pass | `exect_s0_s1_field_family_seizure_pre_vocab_single_pass` | Required — family-isolated executor |
| E5 | `det_medication_hints_llm_extract` | Rx medication candidates only | LLM single-pass | `exect_s0_s1_field_family_medication_pre_vocab_single_pass` | Required — family-isolated executor |

Phase 5a baseline for E1: S1 micro **95.8%** (`exect_s1_stage_graph_g1_l1_policy_bridges_cap25_gpt4_1_mini_20260521T014619Z`).

## Distinction from rejected probes

- E3 uses the **full cap-25** record order under a clean `stage_executor` comparison group, not the interleaving v1 `interleaving_position` varied factor.
- E4/E5 use **full cap-25** (not 14–15 record slices) with family-isolated hint injection — new executor tags vs rejected slice comparison groups.
- Do **not** interpret E3–E5 as reopening interleaving H2 without noting prior full-validation reject (`docs/experiments/exect/exect_s1_interleaving_gpt_validation_v1_inspection_20260520.md`).

## Explicit Non-Goals

- Do not vary stage graph among E1–E5 (all `g1_l1_policy_bridges`).
- Do not test verify-repair, section-aware decomposition, or optimizer compilation.
- Do not change scorer, split, model, or prompt policy.
- Do not claim mechanism reject for bridge placement or pre-vocab hint classes from cap-25 alone.

## Gates

| Decision | Rule |
| --- | --- |
| Rank arms | Order by pooled micro F1; per-family F1 and evidence support as diagnostics |
| Hold | Within 2pp of best micro F1, or qualitatively distinct failure modes |
| Reject arm | >2pp below best without diagnostic benefit |
| Full validation | Deferred until cap-25 winner confirmed |

## Inspection Requirements

- Run IDs for all five arms.
- Taxonomy block with `decision_scope: arm`.
- Metrics table vs E1 and Phase 5a S1 run.
- Bridge Δ analysis E1 vs E2.
- Family-hint arms vs E1 and prior slice/full H2 artifacts.
- Open cells: diagnosis-only hints, Qwen port, full validation.

## Open Cells

- Diagnosis-only deterministic hint stage (no program variant yet).
- `implementation_variant`: hint presentation format.
- Axis 3 sweeps on winning executor assignment.
- Qwen confirmation of cap-25 winner.
