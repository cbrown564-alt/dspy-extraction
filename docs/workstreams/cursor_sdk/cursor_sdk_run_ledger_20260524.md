# Cursor SDK Run Ledger

Date: 2026-05-24  
Status: Active bookkeeping layer  
Decision scope: operational  
Authority: review-only instrumentation; not benchmark evidence

## Purpose

This ledger is the human-readable companion to the machine JSONL ledger written by `scripts/cursor_sdk_workflows.py`.

Future SDK workflow executions append structured rows to:

```text
docs/workstreams/cursor_sdk/cursor_sdk_runs.jsonl
```

Each row records attribution data for a single Cursor SDK workflow attempt. Prompt rehearsals and live drafts both get ledger rows because both can create review burden.

## JSONL Fields

| Field | Meaning |
| --- | --- |
| `run_id` | UTC timestamp used for the default output filename. |
| `workflow` | Runner workflow name such as `memory-pass`, `inspection-draft`, or `model-compatibility`. |
| `model` | Cursor model requested by the runner. |
| `prompt_only` | `true` for prompt rehearsal files; `false` for live agent drafts. |
| `output_kind` | `prompt_rehearsal` or `live_draft`. |
| `output_path` | Repo-relative output path. |
| `started_at`, `ended_at`, `duration_seconds` | Runtime attribution. |
| `status` | `success` or `failed`. Failed rows include `error`. |
| `topic`, `run_dir` | Optional workflow context. |
| `command` | Command line used for the run. |
| `human_review_status` | Initial value is `needs_review`; update only after manual review. |
| `source_claim_status` | Initial value is `unchecked`; update after path and claim verification. |

## Manual Review Status Vocabulary

Use these values in the draft index and, when manually editing JSONL rows or derived summaries, preserve the same meanings:

| Status | Meaning |
| --- | --- |
| `prompt_rehearsal` | Prompt text only; not a live Cursor agent result. |
| `stub` | Live or attempted output with too little substance for review. |
| `substantive` | Contains reviewable findings, but no canonical pointer has been chosen. |
| `canonical_for_review` | Preferred draft for a workflow/topic review queue. |
| `superseded` | Replaced by a later draft or promoted source document. |
| `promoted_to_source` | Specific claims were manually promoted into source docs; the draft itself remains non-authoritative. |
| `rejected` | Do not use except as negative evidence or incident context. |

## Guardrails

- SDK ledger rows are operational metadata only.
- SDK drafts remain `needs_review` until cited paths exist and claims are checked against primary artifacts.
- Do not use the JSONL ledger or draft index as paper evidence, registry evidence, scorer evidence, or dataset-policy evidence.
- Do not run high-volume review swarms without checking this ledger and `docs/workstreams/cursor_sdk/cursor_sdk_draft_index_20260524.md` first.
