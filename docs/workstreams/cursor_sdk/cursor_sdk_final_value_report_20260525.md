# Cursor SDK Final Value Report

Date: 2026-05-25
Status: final retirement summary
Decision scope: operational/research-ops only

## Bottom Line

Cursor SDK was useful as a short-lived review and source-mapping accelerator, but not valuable enough to keep as an active dependency once the temporary discount expired. Its best outputs were not direct code or paper prose; they were checklists, contradiction-finding passes, and focused leads that Codex or a human then verified against primary artifacts.

The workstream should stay retired unless there is a specific future need for cheap parallel review. Historical outputs remain non-authoritative.

## What Was Added

| Contribution | Added value | Promoted source |
| --- | --- | --- |
| ExECT S4/S5 frequency gold-template audit lead | Helped shape the source-backed audit that exposed very low deterministic candidate coverage for frequency: 5/43 gold labels covered, 11.6% coverage, 2/24 gold-bearing docs fully covered. | `docs/experiments/exect/exect_s4_s5_frequency_gold_template_audit_20260524.md` and `artifacts/audits/exect_s4_s5_frequency_gold_template_audit_20260524.json` |
| Core research-question synthesis source map | Helped locate and organize evidence for the Gan-vs-ExECT pipeline interpretation: Gan favors deterministic temporal candidates plus LLM adjudication; ExECT S1/S4 favors broad LLM extraction plus deterministic bridges. | `docs/archive/experiments/synthesis/pre_component_pivot/core_research_questions_pipeline_review_20260524.md` and `docs/archive/experiments/synthesis/pre_component_pivot/core_research_questions_experiment_source_index_20260524.md` |
| Model compatibility stale checks | Produced review leads that became concrete backlog items for production `build_dspy_lm` coverage and explicit Gemini reasoning-effort policy. | `docs/policies/model_config_compatibility_backlog_20260524.md` |
| Gan mutation pilot review | Surfaced one narrow future Gan lead: explicit multi-year seizure-free candidates for `gan_13574` and `gan_13598`; also confirmed no mutation diff should be promoted. | `docs/experiments/gan/gan_s0_cursor_sdk_mutation_pilot_review_20260524.md` |
| ExECT Pathway A review lanes | A1R confirmed the residual audit shape and found a small table correction. A2R diagnosed the verifier recall loss as addressable implementation/prompt issues rather than scorer drift. | `docs/workstreams/cursor_sdk/pathway_a/20260524T191250353424Z_pathway_a_card_report.md`; `docs/workstreams/cursor_sdk/pathway_a/20260524T203900Z_pathway_a_card_report.md` |
| Paper narrative expansion | Helped move the project from scattered experiment reports into a coherent manuscript argument: synthetic-validation scope, task-dependent hybrid placement, arm-vs-mechanism discipline, S5-vs-S4 separation, and explicit non-claims. The critical review then hardened the narrative against overclaiming before the first prose draft was written. | `docs/experiments/synthesis/paper_narrative_current_20260524.md`; `docs/experiments/synthesis/paper_narrative_critical_review_20260524.md`; `docs/experiments/synthesis/paper_manuscript_draft_20260524.md` |
| Workflow hygiene | Forced a clearer rule that SDK drafts are leads, not evidence, and that live mutation belongs only in disposable worktrees. | `docs/workstreams/cursor_sdk/cursor_sdk_disposable_worktree_protocol_20260524.md`; `docs/workstreams/cursor_sdk/cursor_sdk_review_queue_20260524.md` |

## What Did Not Add Enough Value

| Output class | Assessment |
| --- | --- |
| Unreviewed paper prose drafts | Useful as source maps and discrepancy checklists, but not safe as manuscript text. All metrics and operational defaults still needed primary artifact verification. This does not apply to the later source-backed narrative/critical-review/manuscript artifacts listed above. |
| Hygiene scans | Found some stale-doc and routing issues, but mostly created triage burden rather than direct project progress. |
| Broad mutation proposals | Too speculative. Most Gan helper suggestions overlapped existing builders or crossed risky policy boundaries. |
| Live implementation orchestration | The wrapper could create prompts and reports, but the A2 implementation report omitted the full diff, so Codex still had to implement/review manually. |
| Failed/stub outputs | At least one GEPA inspection completed successfully at the runner level while producing a zero-byte draft; this reinforced that SDK success status was not substantive evidence. |

## Net Evaluation

The SDK was best at parallel first-pass reading when the desired product was a lead list, source map, or critic report. It was weaker where the project needed trusted implementation, metric interpretation, paper-ready synthesis, or scorer-sensitive clinical reasoning.

Its highest-value lasting contribution is procedural: the repo now has a stronger norm that generated research-ops artifacts must be promoted claim-by-claim from primary sources, with decision scope and caveats preserved.

## Retirement Decision

Retire active Cursor SDK usage now:

- delete the two project-local Cursor skills;
- keep `docs/workstreams/cursor_sdk/` as historical traceability;
- do not run `scripts/cursor_sdk_workflows.py` unless a future task explicitly reopens this workstream;
- keep the disposable-worktree protocol as a cautionary reference for any future external mutation agent.

## Remaining Useful Leads

| Lead | Status |
| --- | --- |
| Gan `seizure free for multiple year` candidate helper for `gan_13574` and `gan_13598` | Backlog lead only; requires normal tests and Gan audit gates before implementation. |
| Model compatibility B6/B7 | Open backlog: production `build_dspy_lm` config coverage and explicit Gemini reasoning policy. |
| Paper result-table source map | Lead only; use as checklist, not evidence. |
| A2 verifier recall fixes | Historical lead only; current S5 frequency direction should follow the promoted Kanban and primary ExECT inspection docs. |

## Skills Removed

- `.agents/skills/cursor-implementation-orchestration`
- `.agents/skills/cursor-sdk-research-ops`

The rest of the project skill system remains active and should cover future work through domain-specific skills such as `dataset-audit-first`, `gold-scorer-integrity`, `dspy-experiment-design`, `experiment-run-lifecycle`, and `research-synthesis`.
