# Gan S0 Cursor SDK Mutation Pilot Review

Date: 2026-05-24  
Status: Promoted review note; no source code promoted  
Decision scope: Gan S0 temporal-candidate backlog and Cursor SDK mutation protocol

## Decision

The Cursor SDK mutation material is useful as a reviewed lead, not as an implementation source. Promote two claims only:

1. Live Cursor SDK mutation must remain confined to a clean disposable worktree or clone.
2. The `seizure free for multiple year` gap for `gan_13574` and `gan_13598` is a plausible, source-backed future Gan temporal-candidate improvement if Gan S0 deterministic candidate work reopens.

Do not promote the rest of the adapter-mutation proposal. Several suggested helper families overlap existing builders and would add maintenance/review burden without source-backed net gain.

## Sources Reviewed

| Source | Role |
| --- | --- |
| `docs/workstreams/cursor_sdk/archive/experiments_cursor_sdk_drafts/20260523T160319Z_adapter_mutation_draft.md` | Archived mutation proposal; treated as untrusted lead text. |
| `C:/Users/cbrow/Code/dspy-extraction-cursor-pilot-artifacts/20260524T082000Z_mutation_test_report.md` | Successful disposable-worktree pilot report; treated as protocol and slice-coverage evidence. |
| `docs/workstreams/cursor_sdk/archive/experiments_cursor_sdk_drafts/20260523T161218Z_mutation_test_report.md` | Historical shared-workspace mutation incident; treated as negative protocol evidence. |
| `docs/experiments/gan/gan_s0_candidate_builder_gap_preregistration_20260523.md` | Preregistered gap boundaries and excluded helper classes. |
| `docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md` | Source-backed enriched-slice missing-record audit. |
| `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_full_validation_rerun_inspection_20260523.md` | Later inspection confirming the two enriched-slice no-candidate records remain missing. |
| `docs/datasets/gan/gan_2026_label_audit.md` | Gan gold-source and label-policy audit. |
| `docs/policies/deterministic_scorer_semantics.md` | Current scorer and diagnostic metric semantics. |
| `docs/taxonomy/taxonomy_primitive_catalog.md` | Primitive status for Gan temporal candidates, policy bridge, evidence guard, and verify-repair. |
| `tests/test_gan_temporal_candidates.py` | Current regression surface for temporal candidate helpers. |

## Reviewed Findings

### 1. Disposable mutation protocol is promoted

The successful external pilot reports a clean disposable worktree, successful mutation application, focused tests passing, and rollback with `git restore --staged --worktree .`. It also reports the intended test movement:

| Check | Pilot-reported result |
| --- | --- |
| Existing temporal-candidate tests after helpers | 49/49 passed |
| Enriched gap slice exact-gold candidate coverage | 23/25 -> 25/25 |
| Residual gap slice coverage | 24/30 unchanged |

The earlier shared-workspace mutation report is rejected as an implementation basis but kept as protocol evidence. It documents the failure mode the current protocol is designed to prevent: a live mutation in a dirty shared workspace followed by rollback to committed `HEAD`, not necessarily to the pre-session dirty state.

### 2. Only the multi-year seizure-free lead is technically promoted

The source-backed Gan gap audit identifies two enriched-slice records where deterministic candidates lack the exact gold label:

| Record | Gold label | Current audit status |
| --- | --- | --- |
| `gan_13574` | `seizure free for multiple year` | No exact-gold temporal candidate in the enriched slice. |
| `gan_13598` | `seizure free for multiple year` | No exact-gold temporal candidate in the enriched slice. |

Current note inspection confirms both records contain a long-remission expression with `having been seizure free for years`. This matches the pilot's reported useful helper and fits the Gan label scheme, where `seizure free for <v|multiple> <month|year>` is a valid surface form and seizure-free labels map to monthly frequency `0.0`.

This does not change scorer semantics. It is a candidate-generation coverage lead only. Exact normalized-label match remains stricter than monthly-frequency or category matching and should be interpreted as a format-fidelity diagnostic unless a future experiment explicitly targets label-scheme reproduction.

### 3. Other proposed helpers are not promoted

The archived proposal bundled several speculative helper families. Review found no reason to promote them now:

| Proposed helper family | Review decision |
| --- | --- |
| Vague "from time to time" since major seizure wording | Not promoted; overlaps existing no-major-seizures/minor-continues candidates. |
| Unknown cluster spacing with per-cluster range | Not promoted; overlaps existing grouped-spell/unknown-spacing handling and touches a risky unknown-vs-specific boundary. |
| Concurrent daily type-frequency candidates | Not promoted; overlaps existing daily seizure-type frequency handling. |
| Broad post-hoc helper sweep | Not promoted; lacks independent source-backed movement outside the multi-year seizure-free records. |

## Required Gates Before Implementation

If this lead is implemented later, make it a normal reviewed Gan patch:

1. Add dedicated regression tests for `gan_13574` and `gan_13598` requiring an exact `seizure free for multiple year` candidate.
2. Keep the helper narrow to explicit multi-year seizure-free remission wording; do not infer from generic remission alone.
3. Preserve `seizure_frequency_number[0]` as gold and keep `reference[0]` diagnostic only.
4. Re-run `uv run pytest tests/test_gan_temporal_candidates.py`.
5. Re-run the candidate-gap audit command used by the active Gan gap docs before claiming 25/25 enriched-slice coverage.
6. If primitive contracts change, also run `uv run python scripts/validate_primitives.py --errors-only`.

## Validation During This Review

- `uv run pytest tests/test_gan_temporal_candidates.py` passed in the current workspace: 49 passed.
- Current source search found no existing `seizure_free_for_multiple` helper, so no code promotion has already occurred.
- Current record inspection confirmed the two lead records contain the relevant `seizure free for years` surface.

