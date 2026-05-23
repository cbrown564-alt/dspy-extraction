# Cursor SDK Memory Pass Candidate

**Date:** 2026-05-23  
**Candidate ID:** `cursor_sdk_memory_pass_20260523`  
**Scope:** Cross-source memory consolidation after Kanban refresh (2026-05-23) and Gan S0 candidate-builder gap completion through G15  
**Author:** Cursor SDK memory-pass (review-only draft)  
**Status:** `needs_review`

---

## Sources Read

| Path | Role |
| --- | --- |
| `docs/memory/README.md` | Memory precedence, rules, promotion checklist |
| `docs/memory/session_brief.md` | Current promoted memory seed (last reviewed 2026-05-22) |
| `docs/memory/workflow_index.md` | Task routing and memory-consolidation validation |
| `docs/memory/dreams/TEMPLATE.md` | Candidate output shape |
| `docs/planning/kanban_plan.md` | Active execution board (last refreshed 2026-05-23) |
| `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | Mechanism doctrine index (dated 2026-05-21) |
| `docs/experiments/synthesis/experiment_registry.json` | Registry rows, comparison groups, taxonomy drift (sampled; file too large to read in full) |

**Not read (referenced only via Kanban links; treat as secondary until opened):**  
`docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md`, `docs/experiments/gan/gan_s0_candidate_builder_gap_preregistration_20260523.md`, `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md`, `docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md`, `docs/workstreams/cursor_sdk/cursor_sdk_research_workflows_20260523.md`

**Prior dream candidates noted for overlap (not primary sources):**  
`docs/memory/dreams/20260522_model_suite_handoff_candidate.md`, `docs/memory/dreams/cursor_sdk_memory_pass_prompt_rehearsal.md`

---

## Proposed Memory Updates

| Target file | Status | Confidence | Source path(s) | Proposed wording |
| --- | --- | --- | --- | --- |
| `docs/memory/session_brief.md` — **Current Active State** | `operational` | `direct_source` | `docs/planning/kanban_plan.md` | Replace “full model suite alignment” framing with: **Primary execution mode is Gan S0 deterministic candidate-builder gap follow-through (G16 broader GPT validation). Model-suite finish (M1 Qwen 27b) is Priority 2, not the top pull.** |
| `docs/memory/session_brief.md` — **Active Pulls** | `open` | `direct_source` | `docs/planning/kanban_plan.md` | Add row: **G16 — broader GPT validation for `gan_s0_candidate_builder_gap_v1`** — `ready` — next pull before Qwen transfer or operational default change. |
| `docs/memory/session_brief.md` — **Active Pulls** | `open` | `direct_source` | `docs/planning/kanban_plan.md` | Update **Local scaling ladder**: Qwen 3.5:9b column **done**; Qwen 3.6:27b **ready / next Ollama pull when idle** (not “9b in flight”). |
| `docs/memory/session_brief.md` — **Active Pulls** | `done` | `direct_source` | `docs/planning/kanban_plan.md` | Mark Qwen 3.6:35b Gan F0 and hosted model-suite replays as **done** per coverage matrix; model-profile synthesis (M2) remains **open after M1**. |
| `docs/memory/session_brief.md` — **Current Operational Defaults (Gan S0)** | `operational` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | Keep: **F0 expanded builders + prose** remains full-validation operational default (**68.1%** monthly GPT anchor). Add scoped note: **v1.4 no-example policy** is enriched-slice GPT control (**36.0%** monthly on enriched residuals). |
| `docs/memory/session_brief.md` — **Important Non-Claims (new row)** | `arm` | `direct_source` | `docs/planning/kanban_plan.md` | **Builder-gap v1 slice lift (92.0% monthly / 96.0% pragmatic on enriched 25-record slice) is slice-gate evidence only, not operational promotion.** Full-validation generalization pending G16. Primary artifacts: `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md`, run `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z` (cited in Kanban). |
| `docs/memory/session_brief.md` — **Important Non-Claims (new row)** | `arm` | `direct_source` | `docs/planning/kanban_plan.md` | **No-model coverage audit:** deterministic builders contained exact gold label for **5/25** enriched-slice records before G13; **23/25** after builder-gap v1 (G14). Treat enriched slice as search/diagnostic surface, not full-validation estimate. |
| `docs/memory/session_brief.md` — **Important Non-Claims (new row)** | `arm` | `direct_source` | `docs/planning/kanban_plan.md` | **Do not transfer failed GPT-first arms G5/G6/G6b/G7/G9 to Qwen** until a preregistered transferability question is answered. |
| `docs/memory/session_brief.md` — **Important Non-Claims** | `stale_check` | `direct_source` | `docs/planning/kanban_plan.md` | Retain Gemini Gan F0 lead warning; sharpen to: **Gemini 3 Flash 75.3% monthly on Gan F0 is model-comparison evidence only** (`decision_scope: arm`); does not override F0 operational default. |
| `docs/memory/session_brief.md` — **Before Starting New Work** | `operational` | `direct_source` | `docs/planning/kanban_plan.md` | For Gan S0 builder-gap work, also read `docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md` and linked G11–G15 artifacts before code or promotion decisions. |
| `docs/memory/workflow_index.md` — **New Or Changed Experiments** | `open` | `direct_source` | `docs/planning/kanban_plan.md` | Add routing note: Gan deterministic candidate-builder changes → read G11 audit/prereg, run `scripts/audit_gan_candidate_builder_gap.py`, validate `tests/test_gan_temporal_candidates.py` and `scripts/validate_primitives.py --errors-only`; **no scorer/prompt/model edits hidden in builder cards**. |
| `docs/memory/workflow_index.md` — **Memory Consolidation** | `open` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/workstreams/cursor_sdk/cursor_sdk_research_workflows_20260523.md` | Note Cursor SDK pilot (C1–C4): outputs under `docs/memory/dreams/` are review artifacts; C4 continuation blocked until C1–C3 drafts exist and zero source-of-truth edits occurred. |
| `docs/memory/session_brief.md` — **Validation Note** | `stale_check` | `direct_source` | `docs/memory/session_brief.md`, `docs/experiments/synthesis/experiment_registry.json` | Retain registry taxonomy drift warning (`outcome='blocked'`, `context_strategy='full_note_plus_exect_frequency_structured_slots'`, `model_track='claude_sonnet46'`, `model_track='gemini3flash'`, comparison-group caveat for `exect_s1_qwen_diagnosis_stabilized_v1`). **Add:** no registry rows found for `gan_s0_candidate_builder_gap` work (grep over registry JSON). |

---

## Stale Or Conflicting Claims

| Claim or phrase | Location | Issue | Risk if promoted to memory unchecked | Source path(s) |
| --- | --- | --- | --- | --- |
| “Current mode: full model suite alignment on frozen ExECT S1/S4 and Gan F0 surfaces.” | `docs/memory/session_brief.md` | Kanban refreshed 2026-05-23 puts **Gan S0 candidate-builder gap (G16)** as Priority 1; model suite is Priority 2. | Agents may deprioritize G16 or treat suite finish as top pull. | `docs/memory/session_brief.md`, `docs/planning/kanban_plan.md` |
| “Local scaling ladder … 9b column done; **27b overnight next**” (under model-suite-primary framing) | `docs/memory/session_brief.md` | Fact partially correct (9b done, 27b next) but **context is wrong**: ladder is secondary; recommended sequencing is G16 → C1 → M1 when Ollama idle. | Wrong pull order in handoff. | `docs/memory/session_brief.md`, `docs/planning/kanban_plan.md` |
| “next pull is deterministic candidate-builder gap analysis before more model spend” | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` (Gan S0 policy/pipeline synthesis row) | Kanban records G11–G15 **done**; next pull is **G16 broader validation**, not initial gap analysis. | Mechanism index reads as pre-G11 state; understates completed builder-gap work. | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`, `docs/planning/kanban_plan.md` |
| “Gan deterministic candidate-builder gap analysis on enriched slice before more model spend” (under **Next status updates expected**) | `docs/workworks/hybrid/hybrid_pipeline_mechanism_status_20260521.md` | Listed as pending; Kanban shows audit, prereg, implementation, no-model validation, and GPT slice **done**. | Stale “expected update” may trigger duplicate G11–G15 work. | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`, `docs/planning/kanban_plan.md` |
| “Best known Gan arm” | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` (operational defaults table) | Overbroad “best” without scope; F0 is operational default at **68.1%** full-validation while builder-gap v1 shows **92.0%** on enriched slice only. | Accidental operational promotion from slice metrics or model-suite “leader” language. | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`, `docs/planning/kanban_plan.md` |
| “Gemini 3 Flash **leads** Gan F0 monthly (**75.3%**)” | `docs/planning/kanban_plan.md` (Historical Summary / Model Suite Arc) | Fact within model-suite matrix, but “leads” needs **`decision_scope: arm`** label every time. | Suite leaderboard mistaken for operational default change. | `docs/planning/kanban_plan.md` |
| “Gan F0 model default \| Expanded builders + prose remains full-validation operational default” vs builder-gap v1 slice **92.0%** monthly | `docs/planning/kanban_plan.md` (Current Decisions vs G15 outcome) | Not a contradiction if scoped: operational default unchanged until G16 + explicit promotion. | Premature default switch before broader validation. | `docs/planning/kanban_plan.md` |
| Registry rows for builder-gap experiments | `docs/experiments/synthesis/experiment_registry.json` | **Missing context:** no `builder_gap` / `candidate_builder` experiment IDs found; G15 run cited in Kanban may be unregistered. | Memory/registry handoffs omit new arm; synthesis and validation drift widen. | `docs/experiments/synthesis/experiment_registry.json`, `docs/planning/kanban_plan.md`, `docs/memory/session_brief.md` |
| Prior dream note: Kanban 27b-then-9b sequencing mismatch | `docs/memory/dreams/20260522_model_suite_handoff_candidate.md` | **Appears resolved** in refreshed Kanban: 9b **Done**, 27b **Ready**. | Stale warning if promoted without re-check. | `docs/memory/dreams/20260522_model_suite_handoff_candidate.md`, `docs/planning/kanban_plan.md` |

**Facts vs interpretation**

- **Fact (direct_source):** G11–G15 cards marked done in Kanban; G16 ready; F0 remains operational default (`docs/planning/kanban_plan.md`).
- **Fact (direct_source):** No-model coverage 5/25 → 23/25; G15 slice 92.0%/96.0% vs v1.4 36.0%/56.0% on same enriched slice (`docs/planning/kanban_plan.md`).
- **Interpretation (inferred_from_sources):** Candidate coverage—not schema/evidence—is the current Gan S0 bottleneck (`docs/planning/kanban_plan.md` hypothesis section).
- **Uncertainty (needs_review):** Whether builder-gap v1 generalizes beyond enriched slice; requires G16 inspection not in primary sources.

---

## Decisions Reaffirmed

| Decision | Scope | Confidence | Source path(s) |
| --- | --- | --- | --- |
| `docs/planning/kanban_plan.md` is the sole active execution board; memory is derived and lower precedence. | `operational` | `direct_source` | `docs/memory/README.md`, `docs/planning/kanban_plan.md` |
| Gan S0 full-validation operational default: **F0 expanded builders + prose** (GPT **68.1%** monthly anchor). | `operational` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` |
| Gan enriched-slice GPT control: **v1.4 no-example policy** (**36.0%** monthly on enriched residuals). | `operational` | `direct_source` | `docs/planning/kanban_plan.md` |
| ExECT S1 policy: **v4_10 + inline bridges** on all tracks; v4_12 rejected at cap-25. | `operational` | `direct_source` | `docs/planning/kanban_plan.md` |
| ExECT S4: **K0+K1 cause bridge** frozen variant; mechanism classes for weak families remain open. | `operational` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` |
| Model-suite rows (`model_suite_frozen_architecture_v1`) are **model-comparison evidence only**; no operational promotion from leaderboard. | `arm` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/experiments/synthesis/experiment_registry.json` |
| Failed GPT-first Gan arms **G5/G6/G6b/G7/G9** are **arm rejects**; do not transfer to Qwen without prereg. | `arm` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` |
| Arm rejects are **not** mechanism closure unless a mechanism review says so. | `mechanism` | `direct_source` | `docs/memory/session_brief.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` |
| Deterministic temporal candidate generation (Gan): **operational-freeze**; mechanism class still **open**. | `mechanism` | `direct_source` | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` |
| LLM candidate extraction and candidate-constrained verification remain **open mechanism** paths; revisit after candidate recall improves. | `open` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` |
| Published ExECTv2 reproduction blocked (CUI-aware all-family scoring). | `blocked` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/memory/session_brief.md` |
| Gan Real(300)/Real(150) reproduction blocked (data access). | `blocked` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/memory/session_brief.md` |
| One Ollama cap/full job at a time on Windows laptop; hosted API may run in parallel. | `operational` | `direct_source` | `docs/planning/kanban_plan.md`, `docs/memory/workflow_index.md` |
| Do not change Gan scorer semantics in builder-gap work. | `operational` | `direct_source` | `docs/planning/kanban_plan.md` |
| Cursor SDK outputs are review-only drafts; not benchmark model tracks or paper evidence. | `operational` | `direct_source` | `docs/planning/kanban_plan.md` (Priority 4 guardrails) |
| Registry controlled-vocabulary validation still fails on newer statuses/tracks (per session brief). | `stale_check` | `direct_source` | `docs/memory/session_brief.md`, `docs/experiments/synthesis/experiment_registry.json` |

---

## Open Questions

| Question | Why it matters | Source path(s) |
| --- | --- | --- |
| Does **builder-gap v1** generalize on full/cap validation (G16), or is the enriched-slice lift overfit? | Gates operational default promotion vs keeping F0. | `docs/planning/kanban_plan.md` |
| Should **`hybrid_pipeline_mechanism_status_20260521.md`** be updated for G11–G15 outcomes and revised “next status updates”? | Memory currently inherits stale mechanism index; arm rejects vs coverage finding need explicit rows. | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`, `docs/planning/kanban_plan.md` |
| Should **registry rows** be added for builder-gap audit, no-model validation, and G15 slice run? | Registry grep found no `candidate_builder` entries; affects synthesis (M2) and validation hygiene. | `docs/experiments/synthesis/experiment_registry.json`, `docs/planning/kanban_plan.md`, `docs/memory/session_brief.md` |
| After M1 (Qwen 27b), should model-suite table move to a dedicated memory cache (`model_suite_status.md`) per prior dream suggestion? | Suite matrix is mature; `session_brief.md` may be overloaded. | `docs/memory/dreams/20260522_model_suite_handoff_candidate.md`, `docs/planning/kanban_plan.md` |
| Should registry taxonomy drift be fixed before any automated memory export? | Known validation failure may block trustworthy exports. | `docs/memory/session_brief.md`, `docs/memory/workflow_index.md` |
| Continue Cursor SDK pilot after C1 (C4 decision)? | Requires C1–C3 drafts and zero source-of-truth edits by SDK agent. | `docs/planning/kanban_plan.md` |

---

## Promotion Checklist

From `docs/memory/README.md`:

- [x] **Source paths included** for every proposed update above
- [ ] **Source paths exist** — primary sources verified; G11–G15 inspection/audit paths **not independently opened** (flagged)
- [x] **Decision scope explicit** (`operational`, `arm`, `mechanism`, `open`, `blocked`, `stale_check`)
- [x] **Confidence explicit** (`direct_source`, `inferred_from_sources`, `needs_review` where noted)
- [x] **Stale-risk language scoped** (“leads”, “best”, “default”, “reject” tied to arm/operational/slice vs full-validation)
- [x] **No source-of-truth docs rewritten** (this pass is review-only)
- [x] **Conflicting claims surfaced** rather than smoothed over
- [ ] **Human/Codex review complete** — pending

**Additional checks (dream template):**

- [x] No scorer, audit, registry, or Kanban semantics changed from candidate text alone
- [ ] Reviewer selects which rows to promote into `session_brief.md` / `workflow_index.md`
- [ ] Re-run `uv run pytest tests/test_experiment_registry_validation.py` before treating registry drift note as current

---

**Review outcome:** pending  
**Suggested filename if saved:** `docs/memory/dreams/cursor_sdk_memory_pass_20260523.md` (not written — review-only per task rules)