# Gan S0 Temporal/Date-Stage Ablation Grid Preregistration

Date: 2026-05-28  
Status: Preregistered; no model runs launched  
Comparison group: `gan_s0_temporal_date_stage_gpt_cap25_v1`  
Related: `docs/planning/kanban_plan.md`, `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`, `docs/datasets/gan/gan_2026_label_audit.md`

## Research Question

Does isolating a specialist date/event stage improve Gan S0 seizure-frequency extraction when the downstream adjudicator, scorer, split, model, and evidence policy are held fixed?

## Motivation

Gan S0 errors remain concentrated in temporal reasoning: current versus historical windows, bounded periods such as year-to-date, seizure-free intervals, clusters, and ambiguous references where `seizure_frequency_number[0]` and `reference[0]` disagree. Current operational defaults use deterministic temporal candidate builders plus an LLM adjudicator, but the project has not cleanly isolated whether the date/event stage should be deterministic, LLM-generated, hybrid-merged, or exposed as a tool during reasoning.

This preregistration treats the date/event stage as the unit of comparison. It does not alter the Gan scorer, gold-label interpretation, or downstream adjudicator.

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Clinical task family | frequency |
| Research axis | 1/2 first: specialist stage graph, then stage executor placement |
| Comparison group | `gan_s0_temporal_date_stage_gpt_cap25_v1` |
| Primary varied factor | `date_event_stage_executor` |
| Anchor `stage_graph_id` | `g3_date_events_candidates_adjudicate` |
| Baseline stage graph | `g2_candidates_adjudicate` |
| decision_scope target | `arm` |
| Mechanism closure allowed? | No. A cap-25 grid can rank arms and identify follow-ups; it cannot close date/event extraction or tool-during mechanisms. |

## Hypothesis

A specialist date/event stage that exposes explicit temporal anchors, seizure events, seizure-free intervals, and bounded-window denominators will reduce temporal-window errors versus the current candidate-only adjudication baseline, but the best executor placement is unknown and must be compared under a fixed downstream adjudicator.

## Fixed Controls

| Control | Value |
| --- | --- |
| Split | `gan_2026_fixed_v1:validation` |
| Cap | First 25 validation records, same ordering used by existing Gan cap-25 grids |
| Model | GPT 4.1-mini |
| Provider config | `configs/models/gan_s0_gpt4_1_mini.json` |
| Scorer | `gan_frequency_deterministic_v1` |
| Gold label | `seizure_frequency_number[0]` only |
| Reference label | Diagnostic/hard-case flag only; never promotion gold |
| Primary metric | Monthly frequency accuracy |
| Required diagnostics | Purist category, Pragmatic category, schema-valid prediction rate, evidence support, valid/invalid count |
| New temporal diagnostics | temporal-error slice accuracy, current-vs-historical confusion count, bounded-window/YTD count, seizure-free interval count, cluster-window count, hard-case label/reference-disagreement count |
| Downstream adjudication | Same Gan S0 downstream adjudicator policy across all arms |
| Evidence policy | Required model quote with existing evidence-support diagnostics |
| Structured output | Provider JSON schema with Pydantic validation |
| Few-shot policy | none |
| Test reporting | forbidden |

## Date/Event Stage Interface

All treatment arms must pass the same typed conceptual payload to the downstream adjudicator. Implementation may reuse existing models or add a compatible adapter later, but the comparison should preserve this interface:

| Slot | Meaning |
| --- | --- |
| `clinic_date` | Encounter or letter date when available. |
| `temporal_anchors` | Explicit dates, month/year mentions, duration phrases, and relative windows. |
| `seizure_events` | Candidate seizure/event mentions with count/range, seizure type if stated, period denominator, and local context. |
| `seizure_free_intervals` | Statements indicating seizure freedom, no current seizures, or seizure-free since a date/event. |
| `cluster_events` | Cluster frequency and per-cluster count slots, kept separate from non-cluster rates. |
| `current_window_cues` | Textual cues that establish current, historical, prior-to-medication-change, planned/future, or administrative/no-clinical-content status. |
| `candidate_labels` | Canonical Gan label candidates derived from the date/event payload where the executor supports this. |
| `evidence_text` | Verbatim or locatable quote supporting each event/candidate; no summarized secondary `reference[1]` evidence. |
| `stage_confidence` | Optional diagnostic confidence; must not change scorer semantics. |

The adjudicator may use the payload as context, but final scoring remains against the canonical Gan label and monthly/Purist/Pragmatic conversions already implemented in the scorer.

## Arms

| Arm | stage_executor | High-level graph | Date/event source | Candidate label source | Hybrid balance | Calls per record | Priority |
| --- | --- | --- | --- | --- | --- | ---: | --- |
| D0 | `baseline_det_candidates` | `g2_candidates_adjudicate` | none beyond existing deterministic candidates | existing deterministic temporal candidates | `H2_pre_deterministic`, `H4_deterministic_first_llm_adjudicates` | 1 | Required control |
| D1 | `det_date_events` | `g3_date_events_candidates_adjudicate` | deterministic date/event extraction | deterministic candidates derived from date/events | `H2_pre_deterministic`, `H4_deterministic_first_llm_adjudicates` | 1 | Required |
| D2 | `llm_date_events` | `g3_date_events_candidates_adjudicate` | LLM emits date/event payload with evidence | deterministic adapter converts supported payload to candidate labels, plus LLM-proposed labels if valid | `L1_llm_constrained`, `H4_deterministic_first_llm_adjudicates` | 2 | Required |
| D3 | `hybrid_date_events_merge` | `g3_date_events_candidates_adjudicate` | deterministic payload merged with LLM payload | merged candidate labels after deterministic support/normalization checks | `H2_pre_deterministic`, `L1_llm_constrained`, `H4_deterministic_first_llm_adjudicates` | 2 | Required |
| D4 | `tool_during_date_resolver` | `g2_tool_date_resolve_adjudicate` | adjudicator can call bounded date/event resolver tool | tool observations plus adjudicator final label | `H3_interleaved_tool_hybrid` | variable, capped | Optional if tool wrapper exists before run |

If D4 is not implemented in time, the inspection must mark the tool-during cell as open rather than substituting a different tool surface.

## Config Plan

Create configs only after the date/event adapter surface is available. Planned config IDs:

| Planned config | Program variant | Prompt version | Notes |
| --- | --- | --- | --- |
| `gan_s0_date_stage_d0_baseline_det_candidates_cap25_gpt4_1_mini` | `gan_frequency_s0_temporal_candidates_single_pass` | current frozen candidate-adjudication prompt | Reproduce the matched control on the same cap. |
| `gan_s0_date_stage_d1_det_events_cap25_gpt4_1_mini` | `gan_frequency_s0_date_events_candidates_single_pass` | `gan_frequency_s0_date_events_candidates_v1` | Deterministic date/event payload, no extra LLM call. |
| `gan_s0_date_stage_d2_llm_events_cap25_gpt4_1_mini` | `gan_frequency_s0_llm_date_events_candidates_single_pass` | `gan_frequency_s0_llm_date_events_v1` | LLM specialist stage, then same adjudicator. |
| `gan_s0_date_stage_d3_hybrid_events_cap25_gpt4_1_mini` | `gan_frequency_s0_hybrid_date_events_candidates_single_pass` | `gan_frequency_s0_hybrid_date_events_v1` | Deterministic + LLM merge stage. |
| `gan_s0_date_stage_d4_tool_resolver_cap25_gpt4_1_mini` | `gan_frequency_s0_tool_date_resolver_single_pass` | `gan_frequency_s0_tool_date_resolver_v1` | Optional H3 cell; bounded tool calls and tool-error reporting required. |

Minimum taxonomy block for each config:

```json
{
  "dataset": "gan_2026",
  "schema_complexity": "gan_s0",
  "clinical_task_family": "frequency",
  "comparison_group": "gan_s0_temporal_date_stage_gpt_cap25_v1",
  "stage_graph_id": "g3_date_events_candidates_adjudicate",
  "varied_factor": "date_event_stage_executor",
  "intended_decision": "pending"
}
```

Each config must also include `metric_caveats` stating: cap-25 search only, `decision_scope: arm`, Gan gold is `seizure_frequency_number[0]`, and `reference` is diagnostic only.

## Temporal-Error Slice Reporting

The inspection must report arm metrics on the full cap-25 and on these overlapping diagnostic slices:

| Slice | Detection source | Purpose |
| --- | --- | --- |
| label/reference disagreement | `seizure_frequency_number[0] != reference[0]` | Hard ambiguous-reading cases from the Gan audit. |
| seizure-free interval | date/event payload or existing candidate metadata | Tests current seizure-free status versus historical counts. |
| bounded window / YTD | phrases such as year-to-date, since January, in the last N months/weeks | Tests denominator and current-window handling. |
| historical-prior window | cues such as previously, prior to, before medication change | Tests historical-vs-current filtering. |
| cluster | canonical cluster labels or cluster mentions | Tests cluster-rate and per-cluster separation. |
| unknown/no-reference boundary | gold `unknown` or `no seizure frequency reference` | Tests abstention semantics without collapsing the two labels. |

Slice metrics are diagnostic because the cap is small and slices overlap. They may explain arm behavior; they do not replace the primary monthly metric.

## Gates

| Decision | Rule |
| --- | --- |
| Rank arms | Order by monthly frequency accuracy on cap-25; use Purist, Pragmatic, schema validity, evidence support, and temporal slices as diagnostics. |
| Pass to cap-50 or targeted residual replay | Arm beats D0 by at least 3pp monthly, schema validity >= 95%, evidence support >= 95%, and no increase greater than one record in unknown/no-reference confusion. |
| Hold | Arm is within 3pp of D0 or best arm, or has a distinct temporal-slice rescue pattern worth testing on a targeted residual slice. |
| Reject arm | Arm trails D0 by more than 3pp without diagnostic benefit, schema validity < 95%, evidence support < 95%, or introduces unsupported/prose/noncanonical labels. |
| Qwen port | Deferred until a GPT cap-25 arm passes and a follow-up cap-50 or residual replay confirms the signal. |
| Full validation | Deferred until cap-25 plus one confirmatory gate pass. |
| Mechanism closure | Forbidden from this preregistration alone. |

## Explicit Non-Goals

- Do not change `gan_frequency_deterministic_v1` or any Gan scorer semantics.
- Do not use `reference[0]` as gold, even when the date/event stage agrees with it.
- Do not tune from test-holdout outcomes.
- Do not compare this cap-25 grid to full-validation or test metrics without split/cap caveats.
- Do not sweep candidate presentation, examples, self-consistency, or optimizer strategy inside this comparison group.
- Do not claim tool-during is rejected if D4 fails or is skipped; D4 is one arm/interface only.

## Inspection Requirements

The post-run inspection must include:

- Run IDs, config paths, and prompt versions for all executed arms.
- Taxonomy block with `decision_scope: arm`.
- Metrics table for monthly, Purist, Pragmatic, schema validity, evidence support, valid/invalid count, cost/latency or call count.
- Temporal-error slice table.
- Prediction-overlap notes versus D0.
- Tool-call/error table if D4 runs.
- Open cells explicitly listing untested presentation variants, Qwen transfer, self-consistency, and full validation.
- Recommendation for R12: whether the entity-first pipeline should consume the date/event payload, produce candidate events before it, or remain a separate stage-graph test.

## Open Cells

- Entity-first candidate/event tagging before date processing (R12).
- Self-consistency over the best date-stage arm (R13).
- Candidate presentation format for date/event payloads.
- Qwen confirmation of a GPT-gated winner.
- Full-validation promotion after confirmatory cap-50 or residual replay.
