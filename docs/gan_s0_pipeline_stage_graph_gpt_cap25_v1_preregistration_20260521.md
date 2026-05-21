# Gan S0 Pipeline Stage-Graph GPT Cap-25 v1 Preregistration

Date: 2026-05-21  
Status: Cap-25 complete — see `docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md`  
Comparison group: `gan_s0_pipeline_stage_graph_gpt_cap25_v1`  
Related: `docs/hybrid_pipeline_research_pivot_20260521.md`, `docs/hybrid_pipeline_exploration_implementation_plan_20260521.md`, `docs/hybrid_pipeline_mechanism_status_20260521.md`, `docs/kanban_plan.md`

## Research Question

Which Gan S0 pipeline decomposition should be used as the skeleton for later candidate-source and implementation sweeps?

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | 1 — pipeline stage graph / decomposition |
| Comparison group | `gan_s0_pipeline_stage_graph_gpt_cap25_v1` |
| Primary varied factor | `pipeline_stage_graph` |
| decision_scope target | `arm` |
| Mechanism closure allowed? | No |

## Fixed Controls

| Control | Value |
| --- | --- |
| Split | `gan_2026_fixed_v1:validation` |
| Cap | First 25 validation records, same order as Lane A cap-25 groups |
| Model | GPT 4.1-mini |
| Scorer | `gan_frequency_deterministic_v1` |
| Primary metric | Monthly frequency accuracy |
| Diagnostics | Purist category accuracy, Pragmatic category accuracy, schema-valid prediction rate, evidence support, valid/invalid count |
| Prompt family | v1.1 temporal/guardrail policy where applicable |
| Candidate-source control | Deterministic `temporal_candidates.py` only where a candidate stage exists |
| Evidence policy | Required model quote |

## Arms

| Arm | stage_graph_id | Candidate source | High-level graph | New support needed |
| --- | --- | --- | --- | --- |
| A1 | `g1_direct` | none | Single-pass extract+normalize | Existing direct path |
| A2 | `g2_extract_repair` | none | Extract → repair/normalize | Existing verify-repair path or stage metadata only |
| A3 | `g2_candidates_adjudicate` | deterministic | Deterministic temporal candidates → LLM adjudicate | `temporal_candidates_single_pass` |
| A4 | `g3_extract_verify_repair` | none | Extract → verify → repair | Existing verify-repair path with explicit stage metadata |
| A5 | `g3_candidates_extract_repair` | deterministic | Deterministic temporal candidates → extract/adjudicate → repair | Existing promoted temporal-candidates verify-repair path |

## Explicit Non-Goals

- Do not test LLM-only candidate generation in this comparison group.
- Do not test det+LLM candidate merge in this comparison group.
- Do not test candidate presentation variants such as table vs JSON vs bullets.
- Do not change evidence policy, scorer semantics, validation split, or model.
- Do not claim mechanism reject for verify-repair, deterministic candidate generation, or multi-stage pipelines from this cap-25 grid alone.

## Gates

| Decision | Rule |
| --- | --- |
| Rank arms | Order by monthly frequency accuracy; use Purist/Pragmatic, schema validity, evidence support, and invalid count as diagnostics |
| Hold for Axis 2 | Any arm within 3 percentage points of the best monthly score, or any arm with clearly distinct failure behavior worth isolating |
| Reject arm | More than 3 percentage points below best monthly score without diagnostic benefit, or schema-valid prediction rate below 95% |
| Proceed to full validation | No full validation from this group by default; only Axis 2/3 winners should consume full-validation budget |

## Inspection Requirements

The inspection must include:

- Run IDs for all five arms.
- The taxonomy block above, including `decision_scope: arm`.
- A table of metrics for all arms.
- Prediction-overlap notes for arms sharing candidate source or repair stages.
- Open cells explicitly listing LLM candidate generation and hybrid candidate merge as untested.
- A recommendation for which `stage_graph_id` values move to `gan_s0_stage_executor_gpt_cap25_v1`.

## Open Cells

- `stage_executor`: deterministic vs LLM vs hybrid candidate generation.
- `implementation_variant`: candidate presentation, tool interface, evidence guard shape.
- Model transfer: Qwen confirmation.
- Full validation: deferred until a stage graph plus executor assignment wins the cap-25 search path.
