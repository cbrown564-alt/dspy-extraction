# Clinical Extraction Kanban Plan

**Core direction:** `docs/outline.md`  
**Infrastructure:** `docs/deterministic_foundation_decisions.md`  
**Scorer semantics:** `docs/deterministic_scorer_semantics.md`, `docs/gan_2026_label_audit.md`, `docs/exect_gold_label_audit.md`  
**Local Qwen policy:** `docs/qwen_dspy_latency_policy.md`  
**Frozen-thread detail (runs, tables, configs):** `docs/kanban_frozen_threads_history.md`  
**Narrative archive:** `docs/research_status_recap_20260519.md`  
**Alignment audit:** `docs/research_drift_audit_20260520.md` (prior: `docs/research_drift_audit_20260519.md`)  
**DSPy optimizer audit:** `docs/dspy_optimizer_vs_manual_engineering_audit_20260520.md`  
**Last refreshed:** 2026-05-20 — ExECT Qwen S4 cap-25 **done** (`…133930Z` 72.4% micro); **next** S4 full + inspection doc

---

## Execution Model

| Track | Model | Role | Status |
| --- | --- | --- | --- |
| **Gan S0 — local Qwen** | Qwen3.6:35b (Ollama) | Temporal-candidates verify-repair v1.1 — **Tier 1 default** | Engineering fork: ReAct probe → hosted port |
| **ExECT S1–S4 — local Qwen** | Qwen3.6:35b (Ollama) | Replicate frozen GPT ladder | **In progress** — S4 remaining — `docs/exect_qwen35b_ladder_replication_plan.md` |
| **ExECT S1–S4 — hosted GPT** | GPT 4.1-mini | Frozen ladder (S1 v4.10, S2 v1.3, S3 v1.2, S4 v1.2) | Regression / holdout only |
| **Gan S0 — hosted GPT** | GPT 4.1-mini | Temporal-candidates port (Option A) | Full validation **promote** — `…130933Z` (65.1% monthly, 100% evidence) |

**Do not compare across tracks as one experiment.** Same deterministic scorers within each dataset; anchors documented per track in `docs/kanban_frozen_threads_history.md`.

**Single-threaded (both tracks):** scorer semantics, split policy, `gan_frequency_deterministic_v1`, benchmark-reproduction claims.

**Deprioritized:** GEPA/semantic optimizer at scale; BootstrapFewShot on Qwen35b routine paths; Gemini verify-repair scale-up; ExECT section-aware; **hosted GPT label-policy micro-iteration** (Threads B–E frozen); **ExECT architecture ablation** until S4 inspection + ReAct doc + GPT cap-25 decision note. See `docs/dspy_optimizer_vs_manual_engineering_audit_20260520.md` for rationale.

---

## Active Work

### Gan — post–Tier 1 engineering fork

Tier 1 signed (`…230324Z`); B1/B2 slice gates cleared. Detail and anchors → `docs/kanban_frozen_threads_history.md` (Thread A).

| Step | Status | Artifact |
| --- | --- | --- |
| B1 expand `temporal_candidates.py` | Done | `…232514Z` 14/14 |
| B2 model event table | Done | `…235058Z` 14/14 |
| **ReAct bounded probe** | **Ready** (after S4 read) | `gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails.json` — prior partial run killed (Ollama contention); dedicated Ollama **after** S4 full + inspection doc |
| **GPT temporal-candidates port** | Full **promote** | `…130933Z` 65.1% monthly, 76.5% Purist, 84.2% Pragmatic, 99.7% schema, 100% evidence; decision `docs/gan_s0_gpt4_1_mini_temporal_candidates_full_validation_decision_20260520.md` |

**ReAct exit (pre-registered):** global non-regression vs B2 `…235058Z` (≥13/14 monthly on valid preds); **E-guard** = per-record monthly parity on infrequent quartet (`gan_13123`, `gan_14485`, `gan_14881`, `gan_15306`) vs B2; evidence ≥99%; no evidence regression vs B2; `react_tool_call_count` ≤ `GAN_REACT_TEMPORAL_MAX_ITERS` (4) per record. **Any probe pass** (tie or beat) = fork complete, **not** local ReAct Tier 1 promotion → hosted temporal path.

**Scaffold:** `src/clinical_extraction/gan/react_tools.py`, `gan_frequency_s0_react_temporal_tools` variant.

### ExECT — Qwen ladder replication

Hosted GPT ladder **complete and frozen** (Thread E v1.2 `…071248Z`). Local replication uses frozen prompts/scorers; **no** validation re-tuning from Qwen errors.

| Phase | Gate | Status (2026-05-20) |
| --- | --- | --- |
| 0 — four smokes | Contract / JSON valid | **Passed** (`…001917Z` S1, `…003342Z` S2, `…005327Z` S3, `…010617Z` S4) |
| 1 — S1 cap-25, slice, full | vs GPT `…221944Z` (92.3% micro) | **Done** — full `…042117Z` **79.0%** micro (−13.3pp vs GPT); slice `…031422Z`; cap-25 `…012214Z` |
| 2 — S2→S4 cap-25 + full | vs frozen GPT anchors | **S2** cap-25 `…042636Z` 86.9% / full `…073552Z` 82.6% (GPT 80.9%); **S3** cap-25 `…091642Z` 77.1% / full `…092244Z` 72.2% (GPT 72.1%); **S4** cap-25 `…133930Z` **72.4%** (GPT cap `…070616Z` 69.2%) / **full next** vs GPT `…071248Z` (65.5%) |

**Launchers:** `scripts/run_overnight_exect_qwen35b_queue.ps1`, `scripts/run_overnight_exect_qwen35b_queue_resume.ps1` (S4 pending), `scripts/run_exect_s3_cap25_qwen35b.ps1`, `scripts/run_exect_s3_full_qwen35b.ps1`, `scripts/run_exect_s4_cap25_qwen35b.ps1`, `scripts/run_exect_s4_full_qwen35b.ps1`  
**Detached spawn (required for agents / long runs):** `scripts/start_exect_s4_cap25_qwen35b_detached.ps1`, `scripts/start_exect_s4_full_qwen35b_detached.ps1` — `Start-Process` wrappers; **do not** use Cursor/IDE background shells (stall at `1/N` or ~`20/25`; see experiment-run-lifecycle skill step 7).  
**Policy:** halt after Phase 0 if any smoke fails; try `strict_json_prompt_with_pydantic_validation` before scaling.  
**S3 cap-25 caveat:** final `…091642Z` completed via **DSPy disk cache** replay after partial runs stalled at ~20/25 in background terminals; metrics/scorer artifacts are complete — treat latency as non-authoritative.  
**S3 full:** live inference ~83 min (`…092244Z`); inspection `docs/exect_s3_validation_full_qwen35b_ollama_inspection_20260520.md`.  
**S4 cap-25:** live inference ~46 min (`…133930Z`); 25/25, 0 schema errors, 94.6% evidence; freq 59.6% / med-temp 68.4% on cap slice (optimistic vs GPT cap — expect drop on full). Log: `runs/overnight_logs/exect_s4_cap25_qwen35b_20260520_143927.log`.  
**S1 holdout:** deferred — full validation −13.3pp vs GPT; no `exect_s0_s1_validation_test_qwen35b_ollama` until failure modes documented.

### Horizon

- **Benchmark reproduction infra** — CUI-aware all-family ExECT scorer (blocked on design)
- **ExECT S3 Phase 2** — family/social/driving/pregnancy — deferred (no JSON gold)
- **ExECT architecture ablation** — deferred until S4 inspection + ReAct doc + GPT cap-25 decision note (see Blocked)

---

## Kanban Board

### In Progress

#### ExECT Qwen S4 ladder (Phase 2 close-out) — **full validation next**

- **Plan:** `docs/exect_qwen35b_ladder_replication_plan.md`
- **GPT anchor:** `runs/exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` — 65.5% micro (11 fam); freq 45.7% accepted
- **Cap-25 done:** `…133930Z` — 72.4% micro (11 fam); 94.6% evidence; 0 schema errors; ~46 min live
- **Next:** `exect_s4_validation_full_qwen35b_ollama.json` → inspection doc
- **Use:** `scripts/run_exect_s4_full_qwen35b.ps1` from external PowerShell (~80–90 min). **Not** Cursor background shells.

#### Gan bounded ReAct temporal probe — **after S4 full inspection**

- **Prerequisite:** B2 `…235058Z` 14/14 — done; S4 full + inspection doc — pending
- **Ollama:** dedicated **after** ExECT S4 long runs (no overlap)
- **Config:** `configs/experiments/gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails.json`
- **Exit:** see Active Work (E-guard = infrequent quartet + global non-regression)
- **After pass:** hosted temporal path only (no local ReAct Tier 1); GPT full **done** (`…130933Z` promote)

### Review

_(empty)_

### Ready

| Card | Prerequisite | Notes |
| --- | --- | --- |
| **ExECT Qwen S1 inspection doc** | Optional | Phase 1 runs complete; add `docs/exect_s0_s1_validation_full_qwen35b_ollama_inspection_*.md` if seizure-gap forensics needed before test holdout |
| **Benchmark reproduction infra** | Scorer design | CUI-aware all-family ExECT |
| **Gan ReAct MIPRO cap-25 (hosted GPT)** | ReAct slice pass + inspection doc | Only untried optimizer class for multi-step Gan; cap-25 vs uncompiled ReAct; no local Qwen. Design: `docs/dspy_optimizer_vs_manual_engineering_audit_20260520.md` § Recommendations |

### Done (recent)

| Card | Pointer |
| --- | --- |
| ExECT S4 freeze at v1.2 (hosted GPT) | `docs/kanban_frozen_threads_history.md` Thread E; `docs/exect_s4_validation_full_v1_2_gpt4_1_mini_inspection_20260520.md` |
| ExECT S3 freeze at v1.2 | Thread D; comorbidity gap accepted |
| ExECT S2 freeze at v1.3 | Thread C |
| ExECT S1 freeze at v4.10 + test holdout | Thread B |
| Gan temporal v1.1 Tier 1 + B1/B2 | Thread A; `docs/gan_s0_temporal_candidates_v1_1_full_validation_decision_20260519.md` |
| ExECT Qwen Phase 0 smokes | Four smokes passed (2026-05-20) |
| ExECT Qwen S1 full | `…042117Z` 79.0% micro (GPT 92.3%); seizure F1 55.7% — holdout deferred |
| ExECT Qwen S2 cap-25 + full | `…042636Z` 86.9% cap-25; `…073552Z` 82.6% full (GPT 80.9%) |
| ExECT Qwen S3 cap-25 | `…091642Z` 77.1% micro; cache-assembled completion caveat |
| ExECT Qwen S3 full | `…092244Z` 72.2% micro (GPT 72.1%); 94.7% evidence; `docs/exect_s3_validation_full_qwen35b_ollama_inspection_20260520.md` |
| ExECT Qwen S4 cap-25 | `…133930Z` 72.4% micro (GPT cap 69.2%); freq 59.6%; evidence 94.6%; ~46 min live |
| DSPy optimizer vs manual engineering audit | `docs/dspy_optimizer_vs_manual_engineering_audit_20260520.md` |
| Gan GPT temporal full 299 (promote) | `…130933Z` 65.1% monthly, 100% evidence; `docs/gan_s0_gpt4_1_mini_temporal_candidates_full_validation_decision_20260520.md` |
| Gan GPT temporal cap-25 (promote) | `…130724Z` 44% monthly, 100% evidence; bridge fix in `_guard_evidence_text` |
| Gan GPT temporal cap-25 (pre-bridge hold) | `…125302Z` 84% evidence — superseded |

Older cards → `docs/kanban_frozen_threads_history.md`, `docs/research_status_recap_20260519.md`, git history.

### Blocked

| Card | Blocker |
| --- | --- |
| **ExECT architecture ablation** | S4 full inspection doc + ReAct slice error-analysis doc + GPT temporal cap-25 decision note (hold/promote OK; full 299 not required) |
| Reproduce published ExECTv2 / Gan benchmark numbers | CUI-aware ExECT scorer; Gan Real(300)/Real(150) access |
| Runner/program refactor | Optional — avoid during active fork interpretation |
| GEPA / Gemini verify-repair scale-up | Deprioritized |
| ExECT Qwen S1 test holdout | S1 full −13.3pp vs GPT; config not shipped |

### Backlog

| Card | Notes |
| --- | --- |
| **Wire ExECT optimizer compile path** | Extend `scripts/run_experiment.py` beyond Gan-only gate; `LabeledFewShot` first on frozen S1–S4 programs. Prerequisite for ExECT few-shot ablation. Audit: `docs/dspy_optimizer_vs_manual_engineering_audit_20260520.md` |
| **ExECT S1 LabeledFewShot test-holdout baseline** | Hosted GPT only; k≤4; frozen v4.10 bridges; **test split only** — answer outline few-shot ablation without validation re-tuning. Compare to zero-shot test run `…222615Z` |
| ExECT S3 Phase 2 outline fields | No JSON gold |
| ExECT architecture comparison at fixed S1 | Monolithic vs field-group vs verify-repair; add optional cheap compile factor per optimizer audit |
| Consolidate experiment runner + program modules | `docs/codebase_architecture_review_20260519.md` |
| Gan abstention calibration | After verifier boundary stable |
| Review workflow on JSONL export | Independent |
| Gold-label ambiguity audit | Horizon |

**Local Ollama launch rule (Windows):** dry-run/smokes OK in IDE terminals; cap-25 and full validation for Qwen3.6:35b must use `Start-Process` detached scripts or an external PowerShell window. Cursor/agent background shells stall or kill long runs. Monitor `runs/overnight_logs/*.log`; progress lines at 1/10/20/N only. Skill: `.agents/skills/experiment-run-lifecycle/SKILL.md` step 7.

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

**Sprint order (2026-05-20, grill-resolved):**

1. **ExECT Qwen S4 cap-25/full** (Ollama dedicated) — detached launchers; cap-25 = metrics/gates only; **full inspection doc before ReAct**
2. **Hosted (parallel with S4, no Ollama):** GPT temporal cap-25 **hold** `…125302Z` — evidence forensics / retry; on **promote** launch full 299 immediately via pre-shipped config (not after ReAct)
3. **Gan ReAct slice** (Ollama dedicated, **after** S4 inspection) — E-guard = infrequent quartet parity vs B2 + global ≥13/14 monthly
4. **Defer:** ExECT architecture ablation; hosted S4 v1.3; local ReAct Tier 1; Qwen S1 test holdout

```powershell
# ExECT Qwen S4 (long Ollama — MUST use Start-Process detached; NOT Cursor background shell)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start_exect_s4_cap25_qwen35b_detached.ps1
# after cap-25 completes:
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start_exect_s4_full_qwen35b_detached.ps1
# Monitor: Get-Content runs\overnight_logs\exect_s4_*_qwen35b_*.log -Tail 20 -Wait

# Gan ReAct slice — AFTER S4 full + docs/exect_s4_validation_full_qwen35b_ollama_inspection_*.md
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails.json --env-file .env
uv run --extra dev pytest tests/test_gan_react_tools.py tests/test_gan_temporal_candidates.py tests/test_gan_s0_program.py -q
```

---

## Long-Term Phases

| # | Phase | Status |
| --- | --- | --- |
| 1 | Gan S0 tier 1 + B1/B2 | **Done** — ReAct / hosted port active |
| 2 | ExECT S0/S1 (GPT) | **Frozen** v4.10 |
| 3 | ExECT S2–S4 ladder (GPT) | **Frozen** S2 v1.3, S3 v1.2, S4 v1.2 |
| 4 | ExECT Qwen replication | **In progress** — Phases 0–1 + S2/S3 full done; **S4** remaining |
| 5 | Architecture comparison + optional compile baselines | Deferred — see optimizer audit backlog |
| 6 | Benchmark reproduction | CUI-aware scorer |
| 7 | ExECT few-shot ablation (test holdout) | Backlog — after compile path wired |

## Questions (resolved)

| Question | Decision |
| --- | --- |
| Gan before ExECT? | Gan = local optimization gate; ExECT GPT frozen; Qwen = replication track |
| Freeze S3/S4 on hosted GPT? | Yes — see `docs/kanban_frozen_threads_history.md` |
| ReAct slice exit? | E-guard = infrequent quartet (`gan_13123`, `gan_14485`, `gan_14881`, `gan_15306`) monthly parity vs B2; global ≥13/14 monthly; evidence ≥99%; any pass = probe done, **not** local ReAct Tier 1 |
| Ollama scheduling? | **S4 cap-25/full first**, then ReAct; long Qwen runs **Start-Process detached** — **never** Cursor/agent background shells |
| Hosted Gan port variant? | Option A — temporal_candidates_verify_repair; not hosted ReAct by default |
| GPT temporal during S4? | Yes — hosted cap-25/full do not need ReAct prerequisite; cap `…125302Z` **hold** (84% evidence); full 299 on immediate promote when all tier gates pass |
| S4 read before ReAct? | Cap-25 metrics only; **full inspection doc required** before ReAct |
| GPT temporal full config? | Pre-shipped `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails.json`; launch on cap-25 promote |
| ExECT architecture ablation now? | Defer until S4 full inspection + ReAct slice error-analysis + GPT cap-25 decision note; GPT full 299 not required |
| Qwen S1 test holdout? | Defer — full `…042117Z` 79.0% vs GPT 92.3%; document seizure gap first |
| Qwen overnight queue? | Resume queue completed through S3 full; S4 via detached launcher or queue tail |
| Use DSPy optimizers more? | Not by default — Gan probes done; ExECT needs compile infra + test-holdout baseline first. See `docs/dspy_optimizer_vs_manual_engineering_audit_20260520.md` |
