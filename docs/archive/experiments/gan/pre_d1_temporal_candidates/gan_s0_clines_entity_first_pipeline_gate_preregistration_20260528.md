# Gan S0 CLINES-Style Entity-First Pipeline Gate Preregistration

Date: 2026-05-28  
Status: Preregistered; no model runs launched  
Comparison group: `gan_s0_entity_first_stage_graph_gpt_cap25_v1`  
Related: `docs/planning/kanban_plan.md`, `docs/experiments/gan/gan_s0_temporal_date_stage_ablation_grid_preregistration_20260528.md`, `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`, `docs/datasets/gan/gan_2026_label_audit.md`

## Research Question

Does a CLINES-style entity-first stage graph improve Gan S0 seizure-frequency extraction by separating entity/event recall from date normalization and final frequency adjudication?

## Motivation

R11 defined a date/event payload for specialist temporal reasoning. R12 tests the preceding decomposition question: should the pipeline first tag clinically relevant entities and events with offsets/context, then normalize/date-process those tags into the R11 payload, and only then ask the downstream adjudicator to choose the canonical Gan frequency label?

This is a stage-graph hypothesis, not a prompt polish. The cap-25 gate should determine whether entity-first decomposition is worth implementing for the Gan temporal/date-stage grid or whether R11 should proceed with date/event extraction directly from the note.

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Clinical task family | frequency |
| Research axis | 1 — pipeline stage graph / decomposition |
| Comparison group | `gan_s0_entity_first_stage_graph_gpt_cap25_v1` |
| Primary varied factor | `pipeline_stage_graph` |
| Baseline `stage_graph_id` | `g3_date_events_candidates_adjudicate` |
| Treatment `stage_graph_id` | `g4_entity_tags_date_events_candidates_adjudicate` |
| decision_scope target | `arm` |
| Mechanism closure allowed? | No. This gate can rank one entity-first skeleton; it cannot close entity-first decomposition globally. |

## Hypothesis

Entity-first tagging with offsets/context will improve temporal candidate recall and reduce missed-obvious-frequency errors, but it may regress by adding latency, over-selecting historical events, or encouraging the adjudicator to trust noisy tags over the full note. The first gate therefore compares a single entity-first graph against the R11 date/event baseline under fixed model, split, scorer, and downstream adjudication controls.

## Fixed Controls

| Control | Value |
| --- | --- |
| Split | `gan_2026_fixed_v1:validation` |
| Cap | First 25 validation records, same order as existing Gan cap-25 grids |
| Model | GPT 4.1-mini |
| Provider config | `configs/models/gan_s0_gpt4_1_mini.json` |
| Scorer | `gan_frequency_deterministic_v1` |
| Gold label | `seizure_frequency_number[0]` only |
| Reference label | Diagnostic/hard-case flag only; never promotion gold |
| Primary metric | Monthly frequency accuracy |
| Required diagnostics | Purist category, Pragmatic category, schema-valid prediction rate, evidence support, valid/invalid count |
| Entity diagnostics | tag count, tag quote support, tag offset validity, missed-gold-evidence flag when gold evidence is locatable, historical/current tag mix |
| Temporal diagnostics | Same temporal-error slices preregistered in R11 |
| Evidence policy | Required model quote for final prediction; entity tags must carry locatable text and offsets when possible |
| Structured output | Provider JSON schema with Pydantic validation |
| Few-shot policy | none |
| Test reporting | forbidden |

## Entity Tag Interface

The entity-first stage emits an intermediate payload consumed by date/event normalization. Tags are not predictions and must not be scored as gold labels.

| Slot | Meaning |
| --- | --- |
| `entity_id` | Stable within-record identifier. |
| `entity_type` | One of `seizure_event`, `seizure_frequency`, `seizure_free_status`, `cluster`, `temporal_anchor`, `medication_change`, `administrative_no_clinical_content`, `negation_or_absence`, `other_relevant_context`. |
| `text` | Verbatim span or shortest locatable quote from the note. |
| `start_char` / `end_char` | Character offsets when exactly locatable; both present or both null. |
| `context_window` | Short surrounding context used for downstream temporality/date processing. |
| `temporality_hint` | `current`, `historical`, `prior_to_change`, `future_or_planned`, `uncertain`, or `not_applicable`. |
| `count_or_duration_hint` | Raw count, range, duration, or denominator phrase if present. |
| `linked_anchor_ids` | Optional links to temporal anchors or medication-change tags. |
| `confidence` | Diagnostic confidence only. |
| `caveats` | Notes such as ambiguous referent, non-contiguous quote, or paraphrased context. |

The normalizer/date stage maps supported entity tags into the R11 date/event payload slots: `temporal_anchors`, `seizure_events`, `seizure_free_intervals`, `cluster_events`, `current_window_cues`, and `candidate_labels`.

## Arms

| Arm | stage_graph_id | High-level graph | Entity stage | Date/event stage | Adjudication | Calls per record | Priority |
| --- | --- | --- | --- | --- | --- | ---: | --- |
| C0 | `g3_date_events_candidates_adjudicate` | note -> date/event payload -> candidate labels -> adjudicate | none | R11 D1-style deterministic/date-event adapter or nearest implemented R11 baseline | same downstream adjudicator | 1 | Required control |
| C1 | `g4_entity_tags_date_events_candidates_adjudicate` | note -> entity tags with offsets/context -> date/event payload -> candidate labels -> adjudicate | LLM constrained entity tagger | deterministic normalizer/date adapter into R11 payload | same downstream adjudicator | 2 | Required treatment |
| C2 | `g4_det_entity_tags_date_events_candidates_adjudicate` | note -> deterministic entity/candidate tags -> date/event payload -> candidate labels -> adjudicate | deterministic surface tags from existing temporal candidates | deterministic normalizer/date adapter | same downstream adjudicator | 1 | Optional diagnostic only |

C1 is the primary R12 treatment. C2 may be added only if it reuses existing deterministic temporal-candidate spans without new model calls; otherwise leave the deterministic-entity cell open.

## Config Plan

Create configs only after the R11 date/event adapter surface is reviewed. Planned config IDs:

| Planned config | Program variant | Prompt version | Notes |
| --- | --- | --- | --- |
| `gan_s0_entity_first_c0_date_events_cap25_gpt4_1_mini` | `gan_frequency_s0_date_events_candidates_single_pass` | `gan_frequency_s0_date_events_candidates_v1` | Matched R11 date/event baseline control. |
| `gan_s0_entity_first_c1_llm_tags_date_events_cap25_gpt4_1_mini` | `gan_frequency_s0_entity_tags_date_events_single_pass` | `gan_frequency_s0_entity_tags_v1` | CLINES-style entity tagger plus date/event adapter. |
| `gan_s0_entity_first_c2_det_tags_date_events_cap25_gpt4_1_mini` | `gan_frequency_s0_det_entity_tags_date_events_single_pass` | current candidate-adjudication prompt | Optional diagnostic if existing deterministic spans can be rendered as tags. |

Minimum taxonomy block for each config:

```json
{
  "dataset": "gan_2026",
  "schema_complexity": "gan_s0",
  "clinical_task_family": "frequency",
  "comparison_group": "gan_s0_entity_first_stage_graph_gpt_cap25_v1",
  "varied_factor": "pipeline_stage_graph",
  "intended_decision": "pending"
}
```

Each config must include `metric_caveats` stating: cap-25 search only, `decision_scope: arm`, Gan gold is `seizure_frequency_number[0]`, `reference` is diagnostic only, and entity tags are intermediate context rather than benchmark labels.

## Gates

| Decision | Rule |
| --- | --- |
| Rank arms | Compare C1 against C0 by monthly frequency accuracy; use Purist, Pragmatic, schema validity, evidence support, entity diagnostics, temporal slices, and call count as diagnostics. |
| Pass to R11 integration | C1 beats C0 by at least 3pp monthly, schema validity >= 95%, final evidence support >= 95%, tag quote support >= 90%, and no increase greater than one record in unknown/no-reference confusion. |
| Hold | C1 is within 3pp of C0 or rescues a distinct temporal/entity-miss slice without serious schema/evidence regression. |
| Reject arm | C1 trails C0 by more than 3pp without diagnostic benefit, final schema validity < 95%, final evidence support < 95%, tag quote support < 90%, or introduces unsupported/prose/noncanonical final labels. |
| ExECT port | Deferred. ExECT entity-first should be separately preregistered because its gold labels, offsets, and benchmark bridges differ from Gan. |
| Qwen port | Deferred until GPT cap-25 passes and one confirmatory gate supports the skeleton. |
| Full validation | Deferred until cap-25 plus a confirmatory R11 integration gate pass. |
| Mechanism closure | Forbidden from this preregistration alone. |

## Explicit Non-Goals

- Do not change the Gan loader, split, scorer, label normalization, or evidence scorer.
- Do not use `reference[0]` as gold or `reference[1]` as verbatim evidence.
- Do not infer a frequency label solely from entity tags without the downstream adjudicator.
- Do not tune from test-holdout outcomes.
- Do not combine entity-first with self-consistency, examples, optimizer changes, candidate-presentation sweeps, or tool-during arms in this comparison group.
- Do not generalize a C1 null result to ExECT or to all entity-first mechanisms.

## Inspection Requirements

The post-run inspection must include:

- Run IDs, config paths, prompt versions, and call counts for all executed arms.
- Taxonomy block with `decision_scope: arm`.
- Metrics table for monthly, Purist, Pragmatic, schema validity, evidence support, valid/invalid count, and latency/cost if available.
- Entity-stage diagnostics: tag counts, tag types, quote/offset support, unsupported tags, historical/current tag mix.
- Temporal-error slice table using the R11 slice definitions.
- Prediction-overlap notes versus C0.
- At least five qualitative examples where C1 changed the final label or candidate set versus C0.
- Open cells explicitly listing ExECT port, deterministic entity tagger, tag presentation variants, Qwen transfer, self-consistency, and full validation.
- Recommendation for R11: whether entity tags should feed the date/event payload in the first implementation, remain a later Axis 1 follow-up, or be rejected as this arm only.

## Dataset And Scorer Assumptions

- Gan gold remains `seizure_frequency_number[0]`.
- `reference[0]` disagreement marks hard/ambiguous records and is diagnostic only.
- `unknown` and `no seizure frequency reference` remain separate labels.
- Admin/no-clinical-content records should be handled as valid no-reference/abstention cases according to existing split/scorer behavior.
- Entity tags may expose candidate evidence, but final evidence support remains deterministic quote support against the note text, not overlap with `reference[1]`.

## Open Cells

- ExECT S5 or S1 entity-first gate with ExECT-specific field families and benchmark bridges.
- Deterministic entity tagger built from existing primitive candidates.
- Entity tag presentation formats and tag-pruning thresholds.
- Tool-during entity lookup or quote-offset verification.
- Qwen confirmation of any GPT-gated winner.
- Full-validation promotion after R11/R12 integration gates.
