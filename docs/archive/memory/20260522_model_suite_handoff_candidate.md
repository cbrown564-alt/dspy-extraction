# Memory Consolidation Candidate

Date: 2026-05-22
Candidate ID: 20260522_model_suite_handoff
Scope: Model-suite handoff, stale-claim scan, and first use of the dream candidate workflow.
Author: Codex
Status: `needs_review`

## Sources

| Source path | Why it was read | Last observed |
| --- | --- | --- |
| `docs/memory/README.md` | Memory source precedence, allowed status/confidence labels, and promotion rules | 2026-05-22 |
| `docs/memory/session_brief.md` | Current promoted memory seed and validation caveats | 2026-05-22 |
| `docs/memory/workflow_index.md` | Workflow routing and memory-consolidation validation expectations | 2026-05-22 |
| `docs/memory/dreams/TEMPLATE.md` | Candidate shape for this consolidation pass | 2026-05-22 |
| `docs/workstreams/memory/research_memory_layer_design_20260522.md` | Phase plan and rule that dream candidates are review artifacts, not source-of-truth edits | 2026-05-22 |
| `docs/planning/kanban_plan.md` | Active execution board, current model-suite state, sequencing, and stale-risk language | 2026-05-22 |
| `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md` | Arm-vs-mechanism doctrine and stale-claim language rules | 2026-05-22 |
| `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | Current operational freezes, open mechanism classes, and repeat guardrails | 2026-05-22 |
| `docs/experiments/synthesis/experiment_registry.json` | Registry notes for model-suite decision scope, comparison caveats, and controlled-vocabulary drift context | 2026-05-22 |

## Proposed Updates

| Target memory file | Proposed update | Status | Confidence | Source path(s) | Next action |
| --- | --- | --- | --- | --- | --- |
| `docs/memory/session_brief.md` | Add a warning that `docs/planning/kanban_plan.md` has an internal sequencing mismatch: top/current model-suite tables say Qwen 9b ladder is in flight and Qwen 27b is deferred overnight, but the lower roadmap still says to launch 27b then 9b. Treat the top refreshed state as current until Kanban is cleaned. | `stale_check` | `direct_source` | `docs/planning/kanban_plan.md` | Review and, if accepted, promote a one-line warning into `session_brief.md`; separately update Kanban only by explicit source-doc edit. |
| `docs/memory/session_brief.md` | Keep the Gemini Gan F0 lead warning, but sharpen it to cover both Gemini 3 Flash and Gemini 3.1 Flash-Lite: both are model-comparison evidence only; no operational default changes from suite position alone. | `stale_check` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/experiments/synthesis/experiment_registry.json` | Promote wording if this candidate is accepted. |
| `docs/memory/session_brief.md` | Add GPT 5.5 and Claude Sonnet 4.6 to the current model-suite handoff summary as completed hosted full replays, with the same model-comparison-only caveat. | `open` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/experiments/synthesis/model_suite_gpt5_5_full_validation_v1_inspection_20260522.md`, `docs/experiments/synthesis/model_suite_claude_sonnet_4_6_full_validation_v1_inspection_20260522.md` | Promote after reviewing whether the brief should remain ultra-short or become a model-suite status cache. |
| `docs/memory/workflow_index.md` | Add an explicit registry-maintenance validation caveat: current `tests/test_experiment_registry_validation.py::test_repository_experiment_taxonomy_validation_passes_errors_only` fails because validation vocabulary lags newer statuses/model tracks and one comparison-group caveat. | `stale_check` | `direct_source` | `docs/memory/session_brief.md`, `tests/test_experiment_registry_validation.py`, `docs/experiments/synthesis/experiment_registry.json` | Promote only if the caveat is still true after the next registry-validation fix. |
| `docs/memory/model_suite_status.md` | Consider creating this promoted memory file only after the local 9b/27b ladders finish. It would cache model-suite rows and caveats without growing `session_brief.md`. | `open` | `inferred_from_sources` | `docs/workstreams/memory/research_memory_layer_design_20260522.md`, `docs/planning/kanban_plan.md` | Defer until the model-suite table stabilizes. |
| `docs/memory/decision_cache.md` | Consider creating this promoted memory file for compact operational freezes and arm rejects after the first reviewed dream candidate is promoted. | `open` | `inferred_from_sources` | `docs/workstreams/memory/research_memory_layer_design_20260522.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | Defer until this candidate has a review outcome. |

Allowed status values: `operational`, `arm`, `mechanism`, `open`, `blocked`, `stale_check`.

Allowed confidence values: `direct_source`, `inferred_from_sources`, `needs_review`.

## Stale Or Conflicting Claims Found

| Claim or phrase | Location | Issue | Suggested treatment | Source path(s) |
| --- | --- | --- | --- | --- |
| "launch Qwen 27b model-suite ladder ... then 9b column" | `docs/planning/kanban_plan.md` lower roadmap | Conflicts with the refreshed header, coverage table, sequencing table, and current-decisions table that say Qwen 9b is already in flight and 27b is deferred overnight. | Treat as stale sequencing text; use the top/current model-suite tables for handoff. | `docs/planning/kanban_plan.md` |
| "Gan monthly leader" | `docs/planning/kanban_plan.md` current decisions | Potentially ambiguous because F0 expanded builders prose is the operational/search-anchor leader at 68.1%, while Gemini 3 Flash leads the model-suite monthly table at 75.3% but is model-comparison only. | Keep both claims, but always label scope: operational/search-anchor leader vs model-suite track leader. | `docs/planning/kanban_plan.md`, `docs/experiments/synthesis/experiment_registry.json` |
| "Best known Gan arm" | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | Scoped as operational, but stale-risk term "best" can be overread as mechanism closure. | Keep only with operational/arm scope and "mechanism class still open" caveat. | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`, `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md` |
| "model-suite ladder in flight" | `docs/memory/session_brief.md` | Correct by current Kanban header, but underspecified because the 9b ladder is the in-flight local job and 27b is deferred. | Preserve and, if promoted, specify "9b in flight; 27b deferred overnight." | `docs/memory/session_brief.md`, `docs/planning/kanban_plan.md` |
| Registry controlled-vocabulary validation drift | `docs/memory/session_brief.md` validation note | Useful memory warning but not yet backed by a promoted registry repair plan. | Keep as stale-control warning until registry validation vocabulary and comparison caveat are fixed. | `docs/memory/session_brief.md`, `tests/test_experiment_registry_validation.py`, `docs/experiments/synthesis/experiment_registry.json` |

Check especially for overbroad uses of "closed", "best", "leader", "default", "benchmark", and "rejected".

## Decisions Reaffirmed

| Decision | Scope | Confidence | Source path(s) | Next action |
| --- | --- | --- | --- | --- |
| `docs/planning/kanban_plan.md` remains the sole active execution board; memory is derived and lower precedence. | `operational` | `direct_source` | `docs/memory/README.md`, `docs/planning/kanban_plan.md` | `none` |
| Model-suite rows are model-comparison evidence only (`decision_scope: arm`) unless an inspection explicitly promotes an operational default. | `arm` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/experiments/synthesis/experiment_registry.json` | `none` |
| Operational freezes are not mechanism closure. | `operational` | `direct_source` | `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | `none` |
| Do not run two Ollama jobs at once on the Windows laptop; hosted API calls may run alongside one local Ollama job. | `operational` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/memory/session_brief.md` | `none` |
| Published ExECTv2 reproduction and Gan real-set reproduction remain blocked by CUI/all-family scorer alignment and real-data access, respectively. | `blocked` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/memory/session_brief.md` | `none` |

## New Open Questions

| Question | Why it matters | Status | Source path(s) | Next action |
| --- | --- | --- | --- | --- |
| Should `session_brief.md` stay one-page, or should the model-suite table move into a dedicated `model_suite_status.md` cache after the local ladders complete? | The current brief is still useful, but the suite now has enough rows that repeated handoffs may need a separate compact cache. | `open` | `docs/workstreams/memory/research_memory_layer_design_20260522.md`, `docs/planning/kanban_plan.md` | Decide after 9b/27b ladder outcomes are inspected. |
| Should registry controlled-vocabulary drift be fixed before creating any deterministic memory export script? | Phase 3 export would likely depend on registry rows and validation taxonomy; exporting stale vocabulary drift could normalize a known control issue. | `open` | `docs/memory/session_brief.md`, `docs/workstreams/memory/research_memory_layer_design_20260522.md`, `tests/test_experiment_registry_validation.py` | Fix or explicitly document registry-validation vocabulary before `scripts/export_research_memory.py`. |
| Should "Gan monthly leader" be split into "operational leader" and "model-suite leader" in promoted memory? | Without scope labels, the phrase can accidentally promote Gemini suite evidence into an operational default. | `open` | `docs/planning/kanban_plan.md`, `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md` | Promote scoped wording if this candidate is accepted. |

## Skill Or Workflow Updates Suggested

| Skill or workflow | Suggested update | Confidence | Source path(s) | Next action |
| --- | --- | --- | --- | --- |
| Future `research-memory-consolidation` skill | When created, require a scan for internal source-doc contradictions, not only memory-vs-source contradictions. This candidate found a Kanban-internal sequencing mismatch. | `inferred_from_sources` | `docs/workstreams/memory/research_memory_layer_design_20260522.md`, `docs/planning/kanban_plan.md` | Add to the future skill after Phase 1/2 candidate flow proves useful. |
| `research-synthesis` / handoff workflow | For model-suite writeups, require a scope label for "leader" and "best": operational/search-anchor, model-suite track, or mechanism-level conclusion. | `direct_source` | `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`, `docs/planning/kanban_plan.md` | Use immediately in synthesis; consider skill tune only after repeated misses. |

## Promotion Checklist

- [x] Source paths included for every proposed update
- [x] Source paths exist
- [x] Decision scopes/statuses labeled
- [x] Confidence labels included
- [x] No source docs modified automatically
- [x] No scorer, audit, registry, or Kanban semantics changed from candidate text alone
- [x] Stale or conflicting claims surfaced explicitly
- [ ] Human/Codex review complete

## Review Outcome

Reviewer:
Date:
Outcome: `promote_selected` | `revise` | `reject`

Promoted updates:

-

Rejected or deferred updates:

-
