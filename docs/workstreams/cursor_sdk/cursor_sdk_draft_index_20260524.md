# Cursor SDK Draft Index

Date: 2026-05-24  
Status: Active review index  
Decision scope: operational  
Authority: draft bookkeeping only; no source-of-truth claims promoted by this index

## Purpose

This index is the canonical review queue for existing Cursor SDK outputs. It separates prompt rehearsals from live drafts, marks duplicate or superseded files, and points reviewers to the preferred draft for each topic. Use it with `docs/workstreams/cursor_sdk/cursor_sdk_run_ledger_20260524.md`.

## Status Vocabulary

| Status | Meaning |
| --- | --- |
| `prompt_rehearsal` | Prompt text only; not a live Cursor agent result. |
| `stub` | Too little substance for review. |
| `substantive` | Reviewable, but not selected as canonical. |
| `canonical_for_review` | Preferred draft for human/Codex review. |
| `superseded` | Replaced by a later draft or manually promoted source document. |
| `non_sdk_reference` | Useful nearby file, but not a Cursor SDK output. |

## Canonical Review Pointers

| Topic | Canonical draft | Status | Review note |
| --- | --- | --- | --- |
| C1 memory pass | `docs/memory/dreams/20260523T093633Z_cursor_sdk_memory_pass_candidate.md` | `canonical_for_review` | Pilot memory draft; later memory draft is a broader evening follow-up. |
| C2 Gan slice inspection | `docs/experiments/cursor_sdk_drafts/20260523T101141Z_inspection_draft.md` | `canonical_for_review` | Pilot inspection draft used in SDK promotion review. |
| C3 hygiene scan | `docs/workstreams/cursor_sdk/hygiene_scans/20260523T101227Z_hygiene_scan.md` | `canonical_for_review` | Pilot hygiene scan used in SDK promotion review. |
| Evening adapter mutation draft | `docs/experiments/cursor_sdk_drafts/20260523T160319Z_adapter_mutation_draft.md` | `canonical_for_review` | Substantive proposal draft only; no code authority. |
| Evening mutation report | `docs/experiments/cursor_sdk_drafts/20260523T161218Z_mutation_test_report.md` | `canonical_for_review` | Review as incident / disposable-worktree design evidence, not as approved mutation practice. |
| G16 stale-check inspection | `docs/experiments/cursor_sdk_drafts/20260523T164636Z_inspection_draft.md` | `canonical_for_review` | Preferred G16 full-validation stale-check draft. |
| Paper synthesis draft | `docs/experiments/cursor_sdk_drafts/20260523T173227Z_paper_synthesis_draft.md` | `canonical_for_review` | Latest paper draft; paper-facing claims still require primary artifact verification. |
| Evening hygiene scan | `docs/workstreams/cursor_sdk/hygiene_scans/20260523T164844Z_hygiene_scan.md` | `canonical_for_review` | Preferred broad drift scan; identified this index as missing. |
| Model compatibility report | `docs/workstreams/cursor_sdk/compatibility/20260523T164950Z_model_compatibility_report.md` | `canonical_for_review` | Latest compatibility draft; provider changes remain gated by tests. |

## Full Existing Output Index

| File | Type | Status | Canonical / supersession note |
| --- | --- | --- | --- |
| `docs/memory/dreams/cursor_sdk_memory_pass_prompt_rehearsal.md` | memory prompt | `prompt_rehearsal` | Historical prompt rehearsal before timestamped naming. |
| `docs/memory/dreams/20260523T093633Z_cursor_sdk_memory_pass_candidate.md` | memory draft | `canonical_for_review` | C1 pilot canonical. |
| `docs/memory/dreams/20260523T165051Z_cursor_sdk_memory_pass_candidate.md` | memory draft | `substantive` | Evening follow-up; review only if memory drift reopens. |
| `docs/experiments/cursor_sdk_drafts/20260523T101127Z_inspection_draft.md` | inspection prompt | `prompt_rehearsal` | Replaced by `20260523T101141Z_inspection_draft.md`. |
| `docs/experiments/cursor_sdk_drafts/20260523T101141Z_inspection_draft.md` | inspection draft | `canonical_for_review` | C2 pilot canonical. |
| `docs/workstreams/cursor_sdk/hygiene_scans/20260523T101221Z_hygiene_scan.md` | hygiene prompt | `prompt_rehearsal` | Replaced by `20260523T101227Z_hygiene_scan.md`. |
| `docs/workstreams/cursor_sdk/hygiene_scans/20260523T101227Z_hygiene_scan.md` | hygiene draft | `canonical_for_review` | C3 pilot canonical. |
| `docs/experiments/cursor_sdk_drafts/20260523T160207Z_paper_synthesis_draft.md` | paper prompt | `prompt_rehearsal` | Replaced by live paper drafts. |
| `docs/experiments/cursor_sdk_drafts/20260523T160219Z_paper_synthesis_draft.md` | paper draft | `superseded` | Superseded by later paper drafts and source synthesis updates. |
| `docs/experiments/cursor_sdk_drafts/20260523T164746Z_paper_synthesis_draft.md` | paper draft | `superseded` | Superseded by latest paper draft and source synthesis updates. |
| `docs/experiments/cursor_sdk_drafts/20260523T173227Z_paper_synthesis_draft.md` | paper draft | `canonical_for_review` | Latest paper draft; not source evidence. |
| `docs/experiments/cursor_sdk_drafts/20260523T160210Z_adapter_mutation_draft.md` | adapter prompt | `prompt_rehearsal` | Replaced by `20260523T160319Z_adapter_mutation_draft.md`. |
| `docs/experiments/cursor_sdk_drafts/20260523T160319Z_adapter_mutation_draft.md` | adapter draft | `canonical_for_review` | Proposal draft only. |
| `docs/experiments/cursor_sdk_drafts/20260523T161211Z_mutation_test_report.md` | mutation prompt | `prompt_rehearsal` | Replaced by `20260523T161218Z_mutation_test_report.md`. |
| `docs/experiments/cursor_sdk_drafts/20260523T161218Z_mutation_test_report.md` | mutation report | `canonical_for_review` | Review as mutation-risk evidence; shared-workspace mutation remains blocked. |
| `docs/experiments/cursor_sdk_drafts/20260523T163121Z_inspection_draft.md` | inspection draft | `substantive` | Earlier full-validation inspection; superseded for G16 review by `20260523T164636Z_inspection_draft.md`. |
| `docs/experiments/cursor_sdk_drafts/20260523T164636Z_inspection_draft.md` | inspection draft | `canonical_for_review` | Preferred G16 stale-check inspection draft. |
| `docs/workstreams/cursor_sdk/compatibility/20260523T160212Z_model_compatibility_report.md` | compatibility prompt | `prompt_rehearsal` | Replaced by live compatibility reports. |
| `docs/workstreams/cursor_sdk/compatibility/20260523T160418Z_model_compatibility_report.md` | compatibility draft | `superseded` | Superseded by `20260523T164950Z_model_compatibility_report.md`. |
| `docs/workstreams/cursor_sdk/compatibility/20260523T164950Z_model_compatibility_report.md` | compatibility draft | `canonical_for_review` | Latest compatibility report. |
| `docs/workstreams/cursor_sdk/hygiene_scans/20260523T164844Z_hygiene_scan.md` | hygiene draft | `canonical_for_review` | Preferred evening drift scan. |
| `docs/memory/dreams/20260522_model_suite_handoff_candidate.md` | memory reference | `non_sdk_reference` | Pre-SDK memory candidate; not part of SDK review accounting. |
| `docs/memory/dreams/TEMPLATE.md` | memory template | `non_sdk_reference` | Template only. |

## Promotion Boundary

- `canonical_for_review` means "review this first", not "trust this".
- Paper claims must cite primary run artifacts, configs, registry entries, inspection docs, or policy docs after manual verification.
- Mutating work remains gated by disposable-worktree protocol; this index does not release C12.
