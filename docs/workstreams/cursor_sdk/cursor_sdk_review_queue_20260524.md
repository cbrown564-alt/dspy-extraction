# Cursor SDK Review Queue

Date: 2026-05-24  
Status: Active review queue after documentation consolidation  
Authority: triage and review process only; no source-of-truth claims

## Review Status Vocabulary

| Status | Meaning |
| --- | --- |
| `active_review` | Worth reviewing now because it can support the current Kanban pull. |
| `keep_as_lead` | Contains potentially useful leads, but no immediate source promotion. |
| `defer` | Preserve for a later workstream; do not review now. |
| `archive_no_action` | Archived because it is superseded, prompt-only, duplicated, or resolved. |
| `reject` | Do not use except as incident context or negative evidence. |
| `promote_specific_claims` | Specific claims were verified against primary sources and manually promoted elsewhere. |

## Active Review

| Item | Archived source | Status | Review action |
| --- | --- | --- | --- |
| _None_ | _No currently queued SDK draft requires active review._ | `archive_no_action` | Reopen only if a current Kanban card needs an archived draft or a new SDK run is added to `cursor_sdk_runs.jsonl`. |

## Reviewed In This Pass

| Item | Archived source | Status | Review outcome |
| --- | --- | --- | --- |
| Paper result table source-map draft | [20260524T131249Z_paper_synthesis_draft.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/cursor_sdk_drafts/20260524T131249Z_paper_synthesis_draft.md) | `keep_as_lead` | Useful as a paper-table source map and discrepancy checklist, but no metric or operational-default claim was promoted. Before publication, every table value still needs primary verification against `runs/*/metrics.json`, promoted inspection docs, or `experiment_registry.json`; Gan candidate-builder gap v1 remains `stale_check` for operational/default language. |
| Model compatibility stale-check | [20260524T131358Z_model_compatibility_report.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/workstreams/cursor_sdk/compatibility/20260524T131358Z_model_compatibility_report.md) | `promote_specific_claims` | Promoted only code-backed backlog items to `docs/policies/model_config_compatibility_backlog_20260524.md`: config-level coverage should exercise `build_dspy_lm`, and Gemini `reasoning_effort` substring matching needs explicit config/test policy before broad Gemini comparisons. Draft wrapper code and unverified provider-behavior claims were not promoted. |
| Paper Narrative Synthesis | [20260524T093308Z_paper_synthesis_draft.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/cursor_sdk_drafts/20260524T093308Z_paper_synthesis_draft.md) | `keep_as_lead` | Superseded for active table-freeze work by fresh run `20260524T131249Z`. Keep as a broad paper-outline lead only; no claims promoted, and all metrics still require primary artifact checks. |
| Documentation Hygiene Scan | [20260524T093256Z_hygiene_scan.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/workstreams/cursor_sdk/hygiene_scans/20260524T093256Z_hygiene_scan.md) | `keep_as_lead` | Reviewed as a cleanup lead. Useful findings include stale `session_brief.md`, SDK output-path routing drift, uncommitted consolidation state, and stale Kanban/archive wording. No cleanup was applied by the SDK pass; accepted fixes require separate patches. |
| Gan S0 GEPA workstream inspection stub | [20260524T125735Z_inspection_draft.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/cursor_sdk_drafts/20260524T125735Z_inspection_draft.md) | `reject` | Verified file length is 0 bytes. The ledger records successful runner completion but the output is unusable; do not use for source claims. Rely on `docs/workstreams/optimizer/gan_s0_multistage_gepa_workstream_20260524.md`, configs, tests, and future run artifacts instead. |
| ExECT S4/S5 frequency audit guidance | `archive/experiments_cursor_sdk_drafts/20260524T083058Z_inspection_draft.md` | `promote_specific_claims` | The draft was used only as checklist/taxonomy support for `docs/experiments/exect/exect_s4_s5_frequency_gold_template_audit_20260524.md`. The promoted audit cites primary sources and the machine-readable artifact `artifacts/audits/exect_s4_s5_frequency_gold_template_audit_20260524.json`. Headline validation counts were checked against the JSON summary: 40 validation docs, 24 docs with frequency gold, 43 gold labels, 11 candidate labels, 5 matched labels, 38 misses, 6 extras, 11.6% gold coverage, 45.5% candidate precision, and 2/24 gold-bearing docs fully covered. |
| Model compatibility report | `archive/compatibility/20260523T164950Z_model_compatibility_report.md` | `promote_specific_claims` | Verified current adapter/config findings were promoted to `docs/policies/model_config_compatibility_backlog_20260524.md`. Focused validation passed: `uv run pytest tests/test_llm_adapters.py tests/test_model_comparison_configs.py` = 43 passed. Stale/unverified claims were explicitly not promoted. |
| Disposable mutation pilot report | External: `C:/Users/cbrow/Code/dspy-extraction-cursor-pilot-artifacts/20260524T082000Z_mutation_test_report.md`; historical shared-workspace incident: `archive/experiments_cursor_sdk_drafts/20260523T161218Z_mutation_test_report.md` | `promote_specific_claims` | Reviewed in `docs/experiments/gan/gan_s0_cursor_sdk_mutation_pilot_review_20260524.md`. Promoted only the disposable-worktree safety lesson and the narrow `seizure free for multiple year` Gan backlog lead for `gan_13574`/`gan_13598`; no source code was promoted. Current baseline validation passed: `uv run pytest tests/test_gan_temporal_candidates.py` = 49 passed. |
| Adapter mutation proposal | `archive/experiments_cursor_sdk_drafts/20260523T160319Z_adapter_mutation_draft.md` | `promote_specific_claims` | Used only alongside the disposable pilot review. Non-multi-year helper families were not promoted because they overlapped existing candidate builders or crossed risky frequency-policy boundaries. |
| Paper narrative synthesis draft: pipeline decomposition and deterministic versus LLM placement | `archive/experiments_cursor_sdk_drafts/20260524T084403Z_paper_synthesis_draft.md` | `promote_specific_claims` | Reviewed-through-promotion into `docs/experiments/synthesis/core_research_questions_pipeline_review_20260524.md` with `docs/experiments/synthesis/core_research_questions_experiment_source_index_20260524.md` as a generated registry appendix. A registry sanity check confirmed 204 rows and matched the report's headline claims for Gan builder-gap GPT/Qwen and ExECT S1-S4 GPT ladder metrics. Manuscript tables still require primary artifact pulls before publication. |

## Deferred Leads

| Item | Archived source | Status | Review action |
| --- | --- | --- | --- |
| G16 stale-check inspection draft | `archive/experiments_cursor_sdk_drafts/20260523T164636Z_inspection_draft.md` | `defer` | Historical Gan reconciliation lead. Prefer promoted Gan inspection/synthesis docs and the active Kanban over this draft. |

## Archived With No Current Review

| Group | Archive path | Reason |
| --- | --- | --- |
| Prompt rehearsals | `archive/**/**/*prompt*`, plus explicitly indexed files in `cursor_sdk_draft_index_20260524.md` | Prompt text only; not live SDK output. |
| Earlier duplicate inspection drafts | `archive/experiments_cursor_sdk_drafts/20260523T101127Z_inspection_draft.md`, `20260523T163121Z_inspection_draft.md` | Superseded by canonical or promoted source docs. |
| Earlier paper-synthesis drafts | `archive/experiments_cursor_sdk_drafts/20260523T160219Z_paper_synthesis_draft.md`, `20260523T164746Z_paper_synthesis_draft.md`, `20260523T173227Z_paper_synthesis_draft.md` | Do not use for paper claims; paper table freeze must cite primary artifacts and promoted syntheses. |
| Memory pass candidates | `archive/memory_dreams/` | Useful historically; selected updates have already been absorbed into memory/workflow routing or current Kanban. |
| Hygiene scans | `archive/hygiene_scans/` | Findings either resolved, superseded by current Kanban, or represented in this review queue. |
| Old workstream synthesis docs | `archive/workstream_docs/` | Replaced by `README.md`, `cursor_sdk_review_queue_20260524.md`, and current guardrail docs. |

## Review Process

Future review outcomes should be one of:

| Outcome | Meaning |
| --- | --- |
| `promote_specific_claims` | Verified claims are moved into a promoted source document or source-backed backlog. |
| `keep_as_lead` | The draft remains useful but not yet verified. |
| `archive_no_action` | The active audit proceeds from primary docs without using SDK wording. |
| `defer` | The draft is preserved for a later workstream. |
| `reject` | The draft is unusable or unsafe except as incident context. |

Minimum review checklist:

- Every cited source path exists.
- Every claim is traceable to primary docs or code, not to SDK prose.
- Dataset, split, scorer, and evidence caveats are preserved.
- No scorer, loader, schema, registry, or Kanban behavior changes are made as part of review.
- If promoted, wording is applied through a normal patch to the target source document.
