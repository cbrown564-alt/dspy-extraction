# ExECT S1 Pipeline Decomposition Audit

Date: 2026-05-24  
Status: E1 reconciliation complete; no model calls, scorer changes, loader changes, or prompt changes  
Kanban card: `E1 - ExECT S1 pipeline decomposition audit`  
Decision scope: design audit plus prior cap-25 evidence reconciliation

## Purpose

This note reconciles the active Kanban's ExECT S1 decomposition card with the
already completed 2026-05-21 S1 stage-graph and stage-executor grids. The goal is
to prevent duplicated model spend and to carry forward the ExECT-specific label
policy caveats before moving to the S5 core-surface scaffold.

The central question for E1 was:

> Can ExECT S1 be expressed as a preregisterable Axis 1 grid with stable
> `stage_graph_id`, bridge mode, fixed controls, and explicit open cells?

Answer: yes. The preregistered grid already exists and was executed on GPT
4.1-mini cap-25. E1 should therefore close as a reconciliation/audit task, not
as a request to rerun the same S1 grid.

## Required Context

This audit uses:

- ExECT gold policy: `docs/datasets/exect/exect_gold_label_audit.md`
- Scorer semantics: `docs/policies/deterministic_scorer_semantics.md`
- Hybrid doctrine: `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`
- Mechanism status: `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`
- Post-Gan ExECT structure: `docs/experiments/exect/exect_post_gan_s0_experiment_structure_20260524.md`
- Axis 1 preregistration: `docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_preregistration_20260521.md`
- Axis 1 inspection: `docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md`
- Axis 2 preregistration: `docs/experiments/exect/exect_s1_stage_executor_gpt_cap25_v1_preregistration_20260521.md`
- Axis 2 inspection: `docs/experiments/exect/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md`
- Qwen S1 seizure-gap analysis: `docs/experiments/exect/exect_qwen_s1_seizure_gap_error_analysis_20260520.md`

## Audit Rules Applied

Benchmark-facing S1 is not clinically rich extraction. It is the audited
field-family view of:

- `diagnosis`
- `seizure_type`
- `annotated_medication`

The scorer is `exect_field_family_deterministic_v1`.

Rules that matter for the decomposition:

- Diagnosis labels come from affirmed JSON `Diagnosis` entities with
  `DiagCategory == Epilepsy` and certainty >= 4.
- Seizure types come from affirmed JSON `Diagnosis` entities with
  `DiagCategory` `MultipleSeizures` or `SingleSeizure`, not from frequency rows.
- Diagnosis specificity collapse is part of the benchmark-facing view.
- Medication scoring uses annotated prescription names and intentionally does
  not score current/planned/historical status at S1.
- Benchmark bridges are policy infrastructure, not proof of clinical validity.
- Raw annotations and quality flags remain diagnostic context.

## Current Anchors

| Anchor | Run / artifact | Scope | Metric |
| --- | --- | --- | ---: |
| GPT S1 operational default | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` | validation 40 | 92.3% micro F1 |
| GPT S1 cap-25 default | `exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T221936Z` | validation cap-25 | 95.8% micro F1 |
| Qwen S1 default | `exect_s0_s1_validation_full_qwen35b_ollama_20260520T042117Z` / post-bridge analysis anchor | validation 40 | 79.0% micro F1 |
| Qwen residual focus | `docs/experiments/exect/exect_qwen_s1_seizure_gap_error_analysis_20260520.md` | validation 40 | seizure F1 55.7% vs GPT 90.5% |

The GPT default is near ceiling for the local S1 field-family scorer. Qwen's
remaining gap is largely seizure-label policy and surface behavior under the
same benchmark bridges, not a missing post-bridge stage.

## Axis 1 Grid Status

Comparison group: `exect_s1_pipeline_stage_graph_gpt_cap25_v1`  
Research axis: 1  
Primary `varied_factor`: `pipeline_stage_graph`  
Fixed controls: ExECTv2 validation cap-25, GPT 4.1-mini,
`exect_field_family_deterministic_v1`, S1 field-family scope, v4_10 policy
where applicable.

| Arm | `stage_graph_id` | Bridge mode | Micro F1 | Outcome |
| --- | --- | --- | ---: | --- |
| S1 | `g1_l1_policy_bridges` | inline | 95.8% | Hold |
| S2 | `g1_l1_policy_no_bridges` | none diagnostic | 72.8% | Hold diagnostic |
| S3 | `g2_extract_verify` | none diagnostic | 72.8% | Reject arm |
| S4 | `g2_raw_post_bridge` | post module | 95.8% | Hold |
| S5 | `g3_family_split_merge` | inline | 83.3% | Reject arm |

Audit interpretation:

- The grid satisfies E1's preregisterable requirements: stable graph IDs,
  bridge modes, fixed controls, and open cells are present.
- Inline and post benchmark bridges tied on cap-25. This is an arm-level null,
  not a mechanism closure for bridge placement.
- Bridge-free verify/repair did not improve over bridge-free single-pass on
  this slice.
- Section-aware family split regressed under this implementation and should not
  advance without a new implementation-variant preregistration.

## Axis 2 Companion Evidence

Comparison group: `exect_s1_stage_executor_gpt_cap25_v1`  
Research axis: 2  
Anchor graph: `g1_l1_policy_bridges`  
Primary `varied_factor`: `stage_executor`

| Arm | `stage_executor` | Micro F1 | Outcome |
| --- | --- | ---: | --- |
| E1 | `llm_extract_inline_bridges` | 95.8% | Hold |
| E2 | `llm_extract_post_bridges` | 95.8% | Hold |
| E5 | `det_medication_hints_llm_extract` | 93.3% | Reject arm |
| E4 | `det_seizure_hints_llm_extract` | 92.8% | Reject arm |
| E3 | `det_all_family_hints_llm_extract` | 90.9% | Reject arm |

Audit interpretation:

- The executor grid gives enough cap-25 evidence to avoid rerunning E3 as a
  broad "try deterministic hints again" card.
- Family-isolated hints regressed less than all-family hints but still missed
  the promotion gate.
- The active next ExECT value is not another S1 Axis 1 or Axis 2 repeat. It is
  either a new Axis 3 implementation hypothesis or the S5 reporting-surface
  scaffold. The current Kanban already names S5 as the next parallelizable
  design task.

## Open Cells

These remain open and should not be described as closed mechanisms:

- Bridge placement on full validation.
- Qwen transfer of the winning S1 skeleton.
- Diagnosis-only hint executor.
- Hint presentation variants that differ from the rejected static candidate
  shapes.
- Verify/repair with a new target or bridge placement, if preregistered as a
  new implementation variant.
- ExECT S5 core-surface definition and scorer composition.

## Decision

E1 is complete as an audit/reconciliation card.

Do not rerun `exect_s1_pipeline_stage_graph_gpt_cap25_v1` or
`exect_s1_stage_executor_gpt_cap25_v1` unless a new preregistration changes the
primary factor or implementation variant.

Recommended next pull:

1. `E4 - Define and scaffold ExECT S5 core surface`.
2. Then use the S5 scaffold to decide whether S4 frequency needs a new
   candidate-adjudication or structured-slot implementation.

## Reporting Caveats

- All metrics here are local ExECT field-family diagnostics, not published
  ExECTv2 Table 1 reproduction.
- Cap-25 results are search/ranking evidence only.
- `decision_scope` remains `arm`; no mechanism class is closed by this audit.
- Medication temporality is outside S1 and should not be smuggled into the S5
  medication family without a separate S4/S5 policy decision.
