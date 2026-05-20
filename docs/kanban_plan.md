# Clinical Extraction Kanban Plan

**Core direction:** `docs/outline.md`  
**Infrastructure:** `docs/deterministic_foundation_decisions.md`  
**Scorer semantics:** `docs/deterministic_scorer_semantics.md`, `docs/gan_2026_label_audit.md`, `docs/exect_gold_label_audit.md`  
**Local Qwen policy:** `docs/qwen_dspy_latency_policy.md`  
**Frozen-thread detail (runs, tables, configs):** `docs/kanban_frozen_threads_history.md`  
**Narrative archive:** `docs/research_status_recap_20260519.md`  
**Alignment audit:** `docs/research_drift_audit_20260520.md` (prior: `docs/research_drift_audit_20260519.md`)  
**Last refreshed:** 2026-05-20 — active board slimmed; frozen Threads B–E + Tier-1 Gan detail archived

---

## Execution Model

| Track | Model | Role | Status |
| --- | --- | --- | --- |
| **Gan S0 — local Qwen** | Qwen3.6:35b (Ollama) | Temporal-candidates verify-repair v1.1 — **Tier 1 default** | Engineering fork: ReAct probe → hosted port |
| **ExECT S1–S4 — local Qwen** | Qwen3.6:35b (Ollama) | Replicate frozen GPT ladder | **In progress** — `docs/exect_qwen35b_ladder_replication_plan.md` |
| **ExECT S1–S4 — hosted GPT** | GPT 4.1-mini | Frozen ladder (S1 v4.10, S2 v1.3, S3 v1.2, S4 v1.2) | Regression / holdout only |
| **Gan S0 — hosted GPT** | GPT 4.1-mini | Temporal-candidates port (Option A) | **Ready** after ReAct slice gate |

**Do not compare across tracks as one experiment.** Same deterministic scorers within each dataset; anchors documented per track in `docs/kanban_frozen_threads_history.md`.

**Single-threaded (both tracks):** scorer semantics, split policy, `gan_frequency_deterministic_v1`, benchmark-reproduction claims.

**Deprioritized:** GEPA/semantic optimizer at scale; Gemini verify-repair scale-up; ExECT section-aware; **hosted GPT label-policy micro-iteration** (Threads B–E frozen); **ExECT architecture ablation** until Gan ReAct doc + GPT temporal cap-25 + Qwen Phase 0 gates clear.

---

## Active Work

### Gan — post–Tier 1 engineering fork

Tier 1 signed (`…230324Z`); B1/B2 slice gates cleared. Detail and anchors → `docs/kanban_frozen_threads_history.md` (Thread A).

| Step | Status | Artifact |
| --- | --- | --- |
| B1 expand `temporal_candidates.py` | Done | `…232514Z` 14/14 |
| B2 model event table | Done | `…235058Z` 14/14 |
| **ReAct bounded probe** | **In progress** | `gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails.json` — prior partial run killed (Ollama contention); re-run dedicated |
| **GPT temporal-candidates port** | Ready (after ReAct) | Mirror Qwen v1.1 + B2 guards; tiered cap-25 gate → full 299 on promote |

**ReAct exit (pre-registered):** non-regression + E-guard vs B2 `…235058Z` (14/14 monthly on valid preds); evidence ≥99%; no E-regression; `react_tool_call_count` bounded. Tie at 14/14 = pass for probe, not local ReAct promotion → hosted port.

**Scaffold:** `src/clinical_extraction/gan/react_tools.py`, `gan_frequency_s0_react_temporal_tools` variant.

### ExECT — Qwen ladder replication

Hosted GPT ladder **complete and frozen** (Thread E v1.2 `…071248Z`). Local replication uses frozen prompts/scorers; **no** validation re-tuning from Qwen errors.

| Phase | Gate | Status (2026-05-20) |
| --- | --- | --- |
| 0 — four smokes | Contract / JSON valid | **Passed** (resume queue started from S2 full) |
| 1 — S1 cap-25, slice, full | vs GPT `…221944Z` | Pending / in queue |
| 2 — S2→S4 cap-25 + full | vs frozen GPT anchors | **S2 full done** `…073552Z` 82.6% micro (GPT 80.9%); S3 cap-25 running |

**Queue:** `scripts/run_overnight_exect_qwen35b_queue.ps1` / `scripts/run_overnight_exect_qwen35b_queue_resume.ps1`  
**Policy:** halt after Phase 0 if any smoke fails; try `strict_json_prompt_with_pydantic_validation` before scaling.

### Horizon

- **Benchmark reproduction infra** — CUI-aware all-family ExECT scorer (blocked on design)
- **ExECT S3 Phase 2** — family/social/driving/pregnancy — deferred (no JSON gold)
- **ExECT architecture ablation** — deferred until Gan port + Qwen Phase 0–1 reads clear

---

## Kanban Board

### In Progress

#### Gan bounded ReAct temporal probe

- **Prerequisite:** B2 `…235058Z` 14/14 — done
- **Ollama:** dedicated (before / not competing with Qwen overnight)
- **Config:** `configs/experiments/gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails.json`
- **Exit:** non-regression + E-guard vs B2 (see Active Work)
- **After pass:** parallel **Qwen Phase 1–2** (if smokes clear) + **GPT temporal-candidates cap-25**

#### ExECT Qwen S1–S4 ladder (Phases 1–2)

- **Plan:** `docs/exect_qwen35b_ladder_replication_plan.md`
- **Resume log:** `runs/overnight_logs/exect_qwen35b_ladder_resume_20260520_083549.log`
- **Next read:** S3 cap-25/full vs GPT `…235439Z`; then S4

### Review

_(empty)_

### Ready

| Card | Prerequisite | Notes |
| --- | --- | --- |
| **Gan GPT temporal-candidates port (Option A)** | ReAct slice pass | `gan_frequency_s0_temporal_candidates_verify_repair` on GPT 4.1-mini; configs TBD. **Cap-25 gate:** promote full if monthly ≥40%, schema 100%, evidence ≥90%, no E-regression; hold 34.8–40%; stop below verify-repair cap-25 (`…084511Z` 34.8%). Compare full to `…084732Z`. |
| **Benchmark reproduction infra** | Scorer design | CUI-aware all-family ExECT |

### Done (recent)

| Card | Pointer |
| --- | --- |
| ExECT S4 freeze at v1.2 (hosted GPT) | `docs/kanban_frozen_threads_history.md` Thread E; `docs/exect_s4_validation_full_v1_2_gpt4_1_mini_inspection_20260520.md` |
| ExECT S3 freeze at v1.2 | Thread D; comorbidity gap accepted |
| ExECT S2 freeze at v1.3 | Thread C |
| ExECT S1 freeze at v4.10 + test holdout | Thread B |
| Gan temporal v1.1 Tier 1 + B1/B2 | Thread A; `docs/gan_s0_temporal_candidates_v1_1_full_validation_decision_20260519.md` |
| ExECT Qwen Phase 0 smokes | Resume queue from S2 full (2026-05-20) |

Older cards → `docs/kanban_frozen_threads_history.md`, `docs/research_status_recap_20260519.md`, git history.

### Blocked

| Card | Blocker |
| --- | --- |
| **ExECT architecture ablation** | Gan ReAct doc + GPT temporal cap-25 + Qwen Phase 0–1 reads |
| Reproduce published ExECTv2 / Gan benchmark numbers | CUI-aware ExECT scorer; Gan Real(300)/Real(150) access |
| Runner/program refactor | Optional — avoid during active fork interpretation |
| GEPA / Gemini verify-repair scale-up | Deprioritized |

### Backlog

| Card | Notes |
| --- | --- |
| ExECT S3 Phase 2 outline fields | No JSON gold |
| ExECT architecture comparison at fixed S1 | Monolithic vs field-group vs verify-repair |
| Consolidate experiment runner + program modules | `docs/codebase_architecture_review_20260519.md` |
| Gan abstention calibration | After verifier boundary stable |
| Review workflow on JSONL export | Independent |
| Gold-label ambiguity audit | Horizon |

---

## Historical Context

Deterministic foundation is **complete** (loaders, scorers, splits, evidence diagnostics). Model-backed arcs below are frozen on hosted GPT; detail lives in the archive doc.

| Arc | Outcome | Detail |
| --- | --- | --- |
| **Gan S0 temporal v1.1** | Tier 1 local path — 65.8% monthly, 100% evidence (`…230324Z`) | `docs/kanban_frozen_threads_history.md` Thread A; `docs/gan_s0_temporal_candidate_pivot_20260519.md` |
| **ExECT S0/S1** | v4.10 frozen — 92.3% dev / 77.8% test | Thread B |
| **ExECT S2** | v1.3 frozen — 80.9% micro (5 fam); jerk FP eliminated | Thread C |
| **ExECT S3** | v1.2 frozen — 72.1% micro (9 fam); comorbidity gap accepted | Thread D |
| **ExECT S4** | v1.2 frozen — 65.5% micro (11 fam); freq 45.7% accepted | Thread E |

Full metric tables, cap-25 vs full breakdowns, and frozen config lists → **`docs/kanban_frozen_threads_history.md`**. Long-form narrative → `docs/research_status_recap_20260519.md`.

---

## Definitions Of Done

- ExECTv2 and Gan gold load without silent scorer changes.
- Raw, normalized, flags, evidence diagnostics, and benchmark-facing views stay separable.
- DSPy runs record dataset, split, model, schema, variant, scorer, configs, predictions, metrics, errors, artifacts, caveats.
- Cross-run comparisons state when scorer semantics or field-family scope differ.

---

## Recommended Next Pull

**Sprint order (2026-05-20):**

1. **Gan ReAct slice** (Ollama dedicated) — exit = non-regression + E-guard vs B2 `…235058Z`
2. **Parallel after ReAct pass:**
   - **GPT temporal-candidates cap-25** — tiered gate; full 299 only on promote
   - **ExECT Qwen** — let resume queue finish S3/S4; read vs GPT anchors; document schema/evidence separately from F1
3. **Defer:** ExECT architecture ablation; hosted S4 v1.3; Gan hosted ReAct unless slice shows tool lift

```powershell
# Gan ReAct slice
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails.json --env-file .env
uv run --extra dev pytest tests/test_gan_react_tools.py tests/test_gan_temporal_candidates.py tests/test_gan_s0_program.py -q

# ExECT Qwen Phase 0 (if re-checking before queue)
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_smoke_qwen35b_ollama.json --env-file .env
# Phases 1–2: scripts/run_overnight_exect_qwen35b_queue.ps1 or _resume.ps1
```

---

## Long-Term Phases

| # | Phase | Status |
| --- | --- | --- |
| 1 | Gan S0 tier 1 + B1/B2 | **Done** — ReAct / hosted port active |
| 2 | ExECT S0/S1 (GPT) | **Frozen** v4.10 |
| 3 | ExECT S2–S4 ladder (GPT) | **Frozen** S2 v1.3, S3 v1.2, S4 v1.2 |
| 4 | ExECT Qwen replication | **In progress** |
| 5 | Architecture comparison | Deferred |
| 6 | Benchmark reproduction | CUI-aware scorer |

## Questions (resolved)

| Question | Decision |
| --- | --- |
| Gan before ExECT? | Gan = local optimization gate; ExECT GPT frozen; Qwen = replication track |
| Freeze S3/S4 on hosted GPT? | Yes — see `docs/kanban_frozen_threads_history.md` |
| ReAct slice exit? | Non-regression + E-guard vs B2; tie = pass for probe, not local promotion |
| Ollama scheduling? | ReAct first; then parallel Qwen queue + GPT temporal cap-25 |
| Hosted Gan port variant? | Option A — temporal_candidates_verify_repair; not hosted ReAct by default |
| GPT temporal cap-25 → full? | Tiered gate: monthly ≥40%, schema 100%, evidence ≥90%, no E-regression |
| ExECT architecture ablation now? | Defer until ReAct doc + GPT temporal cap-25 + Qwen reads clear |
| Qwen overnight queue? | Halt after Phase 0 if smokes fail; resume queue active 2026-05-20 |
