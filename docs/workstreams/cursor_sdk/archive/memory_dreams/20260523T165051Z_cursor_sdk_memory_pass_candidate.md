# Cursor SDK Memory Pass Candidate

**Date:** 2026-05-23  
**Candidate ID:** `cursor_sdk_memory_pass_20260523T2` (review-only draft; do not promote without human review)  
**Scope:** Cross-source memory consolidation after G16 execution artifacts appeared; Kanban/session_brief still list G16 as the next pull  
**Status:** `needs_review`

---

## Sources Read

| Path | Role |
| --- | --- |
| `docs/memory/README.md` | Precedence rules, decision scopes, promotion checklist |
| `docs/memory/session_brief.md` | Promoted memory seed (last reviewed 2026-05-23) |
| `docs/memory/workflow_index.md` | Task routing and consolidation validation (last reviewed 2026-05-22) |
| `docs/memory/dreams/TEMPLATE.md` | Required candidate output shape |
| `docs/planning/kanban_plan.md` | Active execution board (last refreshed 2026-05-23) |
| `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | Mechanism doctrine index (dated 2026-05-21) |
| `docs/experiments/synthesis/experiment_registry.json` | Registry rows and comparison groups (sampled; builder-gap slice row confirmed; no full-validation row found) |

**Secondary artifacts referenced for conflict detection only (not primary sources per task spec):** Kanban Priority 4 text names SDK drafts under `docs/experiments/cursor_sdk_drafts/` and `docs/workstreams/cursor_sdk/`; run directory existence for G16 was verified at `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z/metrics.json`. Metrics and reconciliation details below that depend on those drafts or run artifacts are labeled `needs_review` unless directly corroborated by the seven primary paths above.

---

## Proposed Memory Updates

| Target file | Status | Confidence | Source path(s) | Proposed wording |
| --- | --- | --- | --- | --- |
| `docs/memory/session_brief.md` — **Current Active State** | `stale_check` | `direct_source` + `needs_review` | `docs/planning/kanban_plan.md`, `docs/memory/session_brief.md` | Replace “execute G16 broader GPT validation” framing with: **Primary follow-through is G16 reconciliation (inspection / decision note / optional rerun), not first execution.** Kanban and session_brief still list G16 as `Ready / next pull`; Kanban assessment text (Priority 4) already references a G16 full-validation inspection draft flagging slice/full candidate mismatch. |
| `docs/memory/session_brief.md` — **Active Pulls (G16 row)** | `stale_check` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/memory/session_brief.md` | Change G16 from `ready` / “Execute broader GPT validation…” to **`review`** / “Reconcile G16 full-validation artifacts: confirm canonical run ID, write promoted inspection, decide rerun vs hold; do not re-run blindly.” Next action: `none` until Kanban card is updated by owner. |
| `docs/memory/session_brief.md` — **Important Non-Claims (new row)** | `arm` | `needs_review` | `docs/planning/kanban_plan.md`, `docs/experiments/synthesis/experiment_registry.json` | **G16 full-validation run exists but is not promoted memory yet.** Canonical run ID candidate: `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z` (artifact verified on disk; not named in Kanban G16 card). No registry row for full validation; slice row remains registered (`gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice`). Treat any aggregate monthly lift vs F0 as **`arm`-scope, confounded** until matched-prompt control and candidate-emission parity are reconciled. |
| `docs/memory/session_brief.md` — **Important Non-Claims (builder-gap slice row)** | `arm` | `direct_source` | `docs/memory/session_brief.md`, `docs/experiments/synthesis/experiment_registry.json` | Revise “Full-validation generalization pending G16” to **“Full-validation generalization unresolved — G16 execution artifacts exist; promoted inspection and registry row pending; slice→full candidate replay inconsistent (`needs_review`).”** |
| `docs/memory/session_brief.md` — **Validation Note** | `stale_check` | `direct_source` | `docs/memory/session_brief.md`, `docs/experiments/synthesis/experiment_registry.json` | Narrow line 61: slice registry row **`gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice`** exists (promoted 2026-05-23); **full-validation G16 row still absent.** Taxonomy validation note remains valid per session brief line 59. |
| `docs/memory/session_brief.md` — **Before Starting New Work** | `operational` | `direct_source` | `docs/planning/kanban_plan.md` | For G16 follow-through, read Kanban G11–G16 block, prereg `docs/experiments/gan/gan_s0_candidate_builder_gap_preregistration_20260523.md`, slice inspection `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md`, and primary run artifacts under `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z/` before promotion or rerun decisions. |
| `docs/memory/workflow_index.md` — header | `open` | `direct_source` | `docs/memory/workflow_index.md`, `docs/planning/kanban_plan.md` | Bump **Last reviewed** to 2026-05-23. |
| `docs/memory/workflow_index.md` — **Memory Consolidation** | `open` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/memory/workflow_index.md` | Update Cursor SDK pilot note: C1–C4 done; **C5–C8 evening drafts may exist** (Kanban Priority 4 lists C5 G16 inspection, C6 paper claim map, C7 hygiene scan, C8 model compatibility as `Ready / evening-suitable` while assessment text says useful drafts were produced). SDK outputs remain review-only under `docs/experiments/cursor_sdk_drafts/` and `docs/workstreams/cursor_sdk/`; **mutating workflows blocked in shared workspace** (Kanban C9). |
| `docs/memory/workflow_index.md` — **New Or Changed Experiments** | `open` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/experiments/synthesis/experiment_registry.json` | Add routing warning: after a full-validation run, **confirm registry row + promoted inspection under `docs/experiments/gan/`** before treating execution as complete; builder-gap slice row notes “Broader validation pending in G16” even though G16 run artifacts may already exist. |

---

## Stale Or Conflicting Claims

| Claim or phrase | Location | Issue | Risk | Source path(s) |
| --- | --- | --- | --- | --- |
| “**G16 — Broader GPT validation** … **Ready / next pull**” | `docs/planning/kanban_plan.md` (Active Cards, Recommended Next Pull) | Kanban still treats G16 as not executed. A full-validation run directory exists (`…161524Z`); Kanban does not name canonical run ID on the G16 card. | Agents re-run G16, duplicate spend, or skip reconciliation/inspection. | `docs/planning/kanban_plan.md`; run artifact path verified separately |
| “Execute broader GPT validation over full split / cap sample” (G16 row `ready`) | `docs/memory/session_brief.md` | Mirrors stale Kanban pull state; session_brief was updated 2026-05-23 but not post-G16 execution. | Same as above; memory handoff perpetuates wrong next action. | `docs/memory/session_brief.md`, `docs/planning/kanban_plan.md` |
| “Full-validation generalization **pending G16**” | `docs/memory/session_brief.md` (builder-gap non-claim) | G16 execution artifacts may exist; what is pending is **decision/reconciliation**, not first run. | Understates review burden; overstates need for fresh execution. | `docs/memory/session_brief.md`, `docs/experiments/synthesis/experiment_registry.json` |
| “Broader validation pending in G16” | `docs/experiments/synthesis/experiment_registry.json` (slice row `notes`, line ~186) | Registry slice row still says G16 pending; no full-validation row added. | Registry-driven synthesis omits G16 outcome; paper/routing tools miss full-validation arm. | `docs/experiments/synthesis/experiment_registry.json` |
| “**G16 broader GPT validation** of candidate-builder gap v1 on full validation split” under **Next status updates expected** | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | Listed as expected future update; Kanban G16 card still `Ready`. Mechanism row for builder-gap v1 (G15) correctly scoped as **`arm`** slice evidence. | Mechanism index understates post-G16 bookkeeping gap; does not contradict arm scope if updated carefully. | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`, `docs/planning/kanban_plan.md` |
| “**C5** … **Ready / evening-suitable**” (and C6–C8) vs assessment “useful drafts … G16 full-validation inspection draft” | `docs/planning/kanban_plan.md` (Priority 4) | Board card statuses lag SDK draft production referenced in same doc. | Repeat evening queue work; under-credit completed review drafts. | `docs/planning/kanban_plan.md` |
| “No registry rows were found for `gan_s0_candidate_builder_gap` work until added via review promotion on 2026-05-23” | `docs/memory/session_brief.md` (Validation Note) | Partially stale: **slice row now exists**; full-validation row still missing. | Reviewers think registry gap fully closed. | `docs/memory/session_brief.md`, `docs/experiments/synthesis/experiment_registry.json` |
| “Gemini 3 Flash **leads** Gan F0 monthly (**75.3%**)” | `docs/planning/kanban_plan.md` (Historical Summary) | Fact within model-suite matrix; “leads” is **`arm`** evidence only. Session_brief already flags as `stale_check`. | Accidental operational promotion from leaderboard language. | `docs/planning/kanban_plan.md`, `docs/memory/session_brief.md` |
| Builder-gap v1 slice **92.0%** monthly vs F0 operational **68.1%** | `docs/planning/kanban_plan.md`, `docs/experiments/synthesis/experiment_registry.json` | Not a contradiction if scoped: slice is **`arm`** gate; F0 remains **`operational`** default until explicit promotion. | Premature default switch before G16 reconciliation. | `docs/planning/kanban_plan.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` |

**Facts vs interpretation vs uncertainty**

- **Fact (`direct_source`):** Kanban Priority 1 is Gan S0 candidate-builder gap; G16 card status is `Ready / next pull`; F0 expanded builders + prose remains operational default at 68.1% monthly GPT anchor (`docs/planning/kanban_plan.md`).
- **Fact (`direct_source`):** G11–G15 marked done; G15 slice 92.0%/96.0% vs v1.4 36.0%/56.0% on enriched 25-record slice; no-model coverage 5/25 → 23/25 (`docs/planning/kanban_plan.md`).
- **Fact (`direct_source`):** Registry contains slice row `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice` with `decision_scope: arm`, `run_scope: slice`, outcome promote to slice-gate; **no** full-validation builder-gap experiment ID (`docs/experiments/synthesis/experiment_registry.json`).
- **Fact (`direct_source`):** Mechanism status lists builder-gap v1 (G15) as **`arm`**; F0 as **`operational`**; deterministic temporal candidate generation as **`operational-freeze`** with mechanism class still **`open`** (`docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`).
- **Interpretation (`inferred_from_sources`):** Primary hygiene risk shifted from Kanban/memory priority drift (largely fixed in session_brief 2026-05-23) to **execution bookkeeping lag** — G16 artifacts vs board status — and **registry/inspection gap** for full validation.
- **Uncertainty (`needs_review`):** Whether `…161524Z` is canonical vs other run directories; whether G16 aggregate metrics support hold vs rerun; slice→full candidate-emission mismatch severity. Kanban mentions an inspection draft finding but primary sources do not include that draft’s metrics — do not treat as paper evidence.

---

## Decisions Reaffirmed

| Decision | Scope | Confidence | Source path(s) | Next action |
| --- | --- | --- | --- | --- |
| `docs/planning/kanban_plan.md` is the sole active execution board; memory is derived and lower precedence. | `operational` | `direct_source` | `docs/memory/README.md`, `docs/planning/kanban_plan.md` | `none` |
| Gan S0 full-validation operational default: **F0 expanded builders + prose** (GPT **68.1%** monthly anchor). | `operational` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | Remains until explicit promotion gate clears |
| Gan enriched-slice GPT control: **v1.4 no-example policy** (**36.0%** monthly on enriched residuals). | `operational` | `direct_source` | `docs/planning/kanban_plan.md` | `none` |
| ExECT S1: **v4_10 + inline bridges**; v4_12 rejected at cap-25. | `operational` | `direct_source` | `docs/planning/kanban_plan.md` | `none` |
| ExECT S4: **K0+K1 cause bridge** frozen variant. | `operational` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | `none` |
| Model-suite rows are **model-comparison evidence only**; no operational promotion from leaderboard. | `arm` | `direct_source` | `docs/planning/kanban_plan.md` | `none` |
| Gemini 3 Flash 75.3% Gan F0 monthly is **not** operational promotion. | `stale_check` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/memory/session_brief.md` | Keep scoped warnings in memory |
| Failed GPT-first Gan arms G5/G6/G6b/G7/G9: **arm rejects**; do not transfer to Qwen without prereg. | `arm` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | `none` |
| Builder-gap v1 G15 slice lift (92.0%/96.0%) is **slice-gate arm evidence only**. | `arm` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/experiments/synthesis/experiment_registry.json`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | Pending G16 reconciliation |
| Arm rejects ≠ mechanism closure unless mechanism review says so. | `mechanism` | `direct_source` | `docs/memory/session_brief.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | `none` |
| Deterministic temporal candidate generation (Gan): **operational-freeze**; mechanism class **open**. | `mechanism` | `direct_source` | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | `none` |
| LLM candidate extraction; candidate-constrained verification: **open mechanism**. | `open` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | Revisit after candidate recall improves |
| Published ExECTv2 reproduction blocked (CUI-aware all-family scoring). | `blocked` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/memory/session_brief.md` | `none` |
| Gan Real(300)/Real(150) blocked (data access). | `blocked` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/memory/session_brief.md` | `none` |
| One Ollama cap/full job at a time; hosted API may parallelize. | `operational` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/memory/workflow_index.md` | Check active local runs before M1 |
| Do not change Gan scorer semantics in builder-gap work. | `operational` | `direct_source` | `docs/planning/kanban_plan.md` | `none` |
| Cursor SDK: review-only research operations; not benchmark model track or source-of-truth updater. | `operational` | `direct_source` | `docs/planning/kanban_plan.md` (Priority 4) | Use draft folders only |
| Mutating SDK workflows blocked in shared dirty workspace. | `blocked` | `direct_source` | `docs/planning/kanban_plan.md` (C9) | Disposable worktree only |
| M1 Qwen 27b model-suite ladder is Priority 2 when Ollama idle. | `operational` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/memory/session_brief.md` | Do not block G16 reconciliation |

---

## Open Questions

| Question | Why it matters | Status | Source path(s) | Next action |
| --- | --- | --- | --- | --- |
| Is `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z` the canonical G16 run? | Kanban does not name a canonical ID; retry directories may exist elsewhere. | `open` | `docs/planning/kanban_plan.md` | Owner confirms in Kanban G16 card / promoted inspection |
| Does G16 require rerun before any arm hold/reject decision? | Kanban assessment references slice/full candidate mismatch in a draft; primary sources do not adjudicate rerun. | `open` | `docs/planning/kanban_plan.md` | Human review of run artifacts + draft reconciliation |
| Does G16 full-validation monthly accuracy change recommended next pull vs F0 68.1% given prompt/confound mismatch (v1.4 vs v1.1)? | Affects whether builder-gap v1 earns **`arm` hold** vs stays slice-only. | `open` | `docs/planning/kanban_plan.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | Promoted inspection with matched controls |
| When should a full-validation registry row be added, and with what `outcome` / `decision_scope`? | Registry currently slice-only; affects M2 synthesis and validation tests. | `open` | `docs/experiments/synthesis/experiment_registry.json`, `docs/planning/kanban_plan.md` | After promoted inspection; scoped **`arm`** metadata |
| Should non-standard error analysis at repo root be relocated under `docs/experiments/gan/`? | Kanban/SDK hygiene flags path inconsistency; not resolved in primary sources. | `open` | `docs/planning/kanban_plan.md` (Priority 4 hygiene context) | Follow-up card only if user requests source-doc edit |
| Does enriched-slice mechanism signal (G13/G15) generalize on full split once candidate emission is verified? | Core builder-gap hypothesis; G16 reconciliation outcome decides Qwen transfer gate. | `open` | `docs/planning/kanban_plan.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | G16 decision note |

---

## Promotion Checklist

(from `docs/memory/README.md`)

- [x] Source paths included for every proposed update
- [x] Source paths exist (seven primary paths read; G16 run artifact path verified on disk)
- [x] Decision scopes/statuses labeled (`operational`, `arm`, `mechanism`, `open`, `blocked`, `stale_check`)
- [x] Confidence labels included (`direct_source`, `inferred_from_sources`, `needs_review`)
- [x] No source docs modified automatically (review-only draft)
- [x] No scorer, audit, registry, or Kanban semantics changed from candidate text alone
- [x] Stale or conflicting claims surfaced explicitly
- [ ] Human/Codex review complete — **pending**

**Reviewer actions suggested (not automatic):**

1. Update Kanban G16 card to Review/Done with canonical run ID, then mirror in `session_brief.md`.
2. Promote selected rows from this candidate into `session_brief.md` and bump `workflow_index.md` last-reviewed date.
3. Defer registry row addition until a promoted G16 inspection exists under `docs/experiments/gan/`.
4. Score SDK drafts (C5–C8) per Kanban Priority 4 rubric before marking those cards Done.

---

*This artifact is a review-only memory consolidation candidate. It is not promoted memory and must not be cited as paper evidence unless reconciled to primary run artifacts, configs, and inspection docs.*