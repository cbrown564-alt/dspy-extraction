# ExECT S1 Pipeline Stage-Graph GPT Cap-25 v1 Preregistration

Date: 2026-05-21  
Status: Preregistered — configs ready, runs pending  
Comparison group: `exect_s1_pipeline_stage_graph_gpt_cap25_v1`  
Related: `docs/hybrid_pipeline_research_pivot_20260521.md`, `docs/hybrid_pipeline_exploration_implementation_plan_20260521.md`, `docs/hybrid_pipeline_mechanism_status_20260521.md`, `docs/kanban_plan.md`

## Research Question

Which ExECT S1 pipeline decomposition should anchor later executor and bridge-placement grids, when prompt policy (v4_10), model, split, and scorer are fixed?

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | S1 field-family (diagnosis, seizure_type, annotated_medication) |
| Research axis | 1 — pipeline stage graph / decomposition |
| Comparison group | `exect_s1_pipeline_stage_graph_gpt_cap25_v1` |
| Primary varied factor | `pipeline_stage_graph` |
| decision_scope target | `arm` |
| Mechanism closure allowed? | No |

## Fixed Controls

| Control | Value |
| --- | --- |
| Split | `exectv2_fixed_v1:validation` |
| Cap | First 25 validation records, same order as Lane A cap-25 groups |
| Model | GPT 4.1-mini |
| Scorer | `exect_field_family_deterministic_v1` |
| Primary metric | Pooled micro F1 |
| Diagnostics | Per-family F1, evidence quote support, bridge contribution notes |
| Prompt family | `exect_s0_s1_field_family_v4_10_label_policy` (verify-repair uses v4_10 via extraction mapping) |
| Few-shot | embedded benchmark-facing label-policy examples |
| Evidence policy | Standard v4_10 quote requirement |

## Bridge Mode (documented per arm)

| `bridge_mode` | `repair_policy` | Meaning |
| --- | --- | --- |
| `inline` | `none` | Single-pass extraction with inline benchmark bridges (production-shaped) |
| `none_diagnostic` | `raw_no_benchmark_bridges` | Raw model surfaces only; no benchmark bridges |
| `post_module` | `artifact_benchmark_bridge_only` | Extract raw → apply bridges as post stage only |
| `none_diagnostic` (verify-repair) | `raw_no_benchmark_bridges` + verify-repair variant | Two-stage LLM verify without bridge confound |

## Arms

| Arm | `stage_graph_id` | `bridge_mode` | Program / graph | Config |
| --- | --- | --- | --- | --- |
| S1 | `g1_l1_policy_bridges` | `inline` | Single-pass L1 + inline bridges | `exect_s1_stage_graph_g1_l1_policy_bridges_cap25_gpt4_1_mini.json` |
| S2 | `g1_l1_policy_no_bridges` | `none_diagnostic` | Single-pass L1, bridge-free | `exect_s1_stage_graph_g1_l1_policy_no_bridges_cap25_gpt4_1_mini.json` |
| S3 | `g2_extract_verify` | `none_diagnostic` | Extract → confirm-first verify/repair, bridges off | `exect_s1_stage_graph_g2_extract_verify_cap25_gpt4_1_mini.json` |
| S4 | `g2_raw_post_bridge` | `post_module` | Single-pass extract → post bridge only | `exect_s1_stage_graph_g2_raw_post_bridge_cap25_gpt4_1_mini.json` |
| S5 | `g3_family_split_merge` | `inline` | Section-aware per-family extract → merge | `exect_s1_stage_graph_g3_family_split_merge_cap25_gpt4_1_mini.json` |

## Explicit Non-Goals

- Do not test per-family det-assisted pre-candidates (Axis 2) in this group.
- Do not test prompt-policy variants (v4_11) or optimizer compilation.
- Do not test evidence-policy addenda or verify-repair with inline bridges (covered by Lane A verification group).
- Do not change scorer semantics, split, or model.
- Do not claim mechanism reject for multi-stage pipelines, verify-repair, or bridge placement from this cap-25 grid alone.

## Gates

| Decision | Rule |
| --- | --- |
| Rank arms | Order by pooled micro F1; use per-family F1, evidence support, and bridge Δ vs S2 as diagnostics |
| Hold for Axis 2 | Any arm within 2pp of best micro F1, or any arm with distinct failure behavior worth isolating |
| Reject arm | More than 2pp below best micro F1 without diagnostic benefit |
| Proceed to full validation | No full validation from this group by default; only Axis 2 winners consume full-validation budget |

## Inspection Requirements

The inspection must include:

- Run IDs for all five arms.
- Taxonomy block with `decision_scope: arm`.
- Metrics table with bridge_mode column.
- Bridge contribution analysis: S1 vs S2 (inline bridge Δ), S4 vs S2 (post vs none).
- Prediction-overlap notes for arms sharing extraction stages.
- Open cells: per-family executor placement, det pre-candidates, bridge inline vs post on winning graph.
- Recommendation for which `stage_graph_id` values move to `exect_s1_stage_executor_gpt_cap25_v1`.

## Frozen References

| Role | Artifact | Notes |
| --- | --- | --- |
| Production anchor | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` | 92.3% micro full validation |
| Cap-25 single-pass | `exect_s1_verification_single_pass_cap25_gpt4_1_mini_20260520T232837Z` | 95.8% micro — expect S1 match |
| Cap-25 bridge-free | interleaving L1 raw cap-25 | expect S2 match |
| Cap-25 verify-repair (bridges on) | `exect_s1_verification_verify_repair_cap25_gpt4_1_mini_20260520T232841Z` | 86.4% — **not** S3 (bridges off) |

## Open Cells

- `stage_executor`: LLM vs det-assisted per family on winning graph.
- `bridge_mode`: inline vs post on matched extraction skeleton.
- `implementation_variant`: prompt policy, evidence guard shape.
- Model transfer: Qwen confirmation deferred.
- Full validation: deferred until cap-25 winner identified.
