# Research Drift Audit — Status Update

Date: 2026-05-19  
Audit type: alignment check against core research plan  
Active tracker: `docs/kanban_plan.md`  
Narrative archive: `docs/research_status_recap_20260519.md`

## Research Question

Is the project still aligned with the hybrid deterministic + DSPy clinical extraction research plan in `docs/outline.md`, or has recent work drifted toward distractions, premature breadth, or ungoverned experimentation?

## Motivation

The repo completed its deterministic foundation milestone and entered an intensive model-backed optimization phase on 2026-05-17 through 2026-05-19. That phase produced many parallel experiment paths (GEPA, few-shot ladders, verify-repair, temporal candidates, ExECT baselines) plus a large uncommitted working tree. A drift audit is needed to confirm whether the active workstream still serves the stated research objectives and to identify operational risks before the next promotion decision.

## Method

This audit followed the project `research-drift-audit` workflow:

1. **Core direction documents**
   - `docs/outline.md` — research goals, architecture layers, ablation plan
   - `docs/kanban_plan.md` — active tracker, gates, session handoff
   - `docs/deterministic_foundation_decisions.md` — infrastructure-first policy
   - `docs/research_status_recap_20260519.md` — narrative synthesis
   - `docs/gan_s0_temporal_candidates_v1_1_full_validation_decision_20260519.md` — pre-registered promotion tiers
   - `docs/gan_s0_temporal_candidate_pivot_20260519.md` — pivot rationale

2. **Recent git history** — 40+ commits since 2026-05-17; commit messages and file clusters inspected through `git log` and `git diff --stat`.

3. **Working tree** — uncommitted changes (~1,784 lines across 22 tracked files; additional untracked configs, docs, runs, and `src/clinical_extraction/gan/temporal_candidates.py`).

4. **Run artifacts** — promotion gate runs, anchor runs, and incomplete full-validation directory inspected under `runs/`.

5. **Alignment axes** (from `docs/outline.md`):
   - benchmark reproduction and improvement
   - deterministic infrastructure before model complexity
   - Gan versus ExECT sequencing
   - reproducible experiments and ablations
   - local versus closed-model comparison
   - downstream use-case exploration

## Current Position

The project has moved beyond deterministic scaffolding into **Gan S0–first optimization**, with ExECT S0/S1 held as a broader-schema comparison anchor. The active engineering bet is **temporal-candidates v1.1** on local Qwen3.6:35b: a deterministic candidate set plus confirm-first verifier guards, targeting infrequent quantified rates that require temporal event aggregation across note spans.

### Active tracks (2026-05-19)

| Track | Status | Primary artifact |
| --- | --- | --- |
| Gan temporal v1.1 regression slice | **Gate cleared** | `runs/gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_guardrails_20260519T180329Z` |
| Gan temporal v1.1 cap-25 validation | **Gate cleared** | `runs/gan_s0_qwen35b_temporal_candidates_verify_repair_cap25_guardrails_validation_20260519T183213Z` |
| Gan temporal v1.1 full validation | **Incomplete** | `runs/gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T183614Z` — config/metadata only; log stopped at 140/299 |
| ExECT S0/S1 monolithic full validation | **Done (anchor)** | `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T200017Z` — 67.8% micro F1 (40 records) |
| ExECT label-policy v4 regression slice | **Ready, not gated** | `configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json` |
| Published benchmark reproduction | **Blocked** | Missing CUI-aware ExECT all-family scorer; no Gan Real(300) access |

### Quality anchors (unchanged for cross-run claims)

| Path | Split | Monthly | Evidence | Notes |
| --- | --- | ---: | ---: | --- |
| GPT verify-repair v2 | 299 validation | 65.4% | 92.7% | Hosted quality ceiling |
| Qwen direct + guardrails | 299 validation | 55.9% | 99.6% | Local baseline |
| Qwen direct cap-25 v2 | 25 validation | 37.5% | 100% | Best local cap-25 monthly (prior) |
| Temporal v1.1 cap-25 | 25 validation | 44.0% | 100% | 100% schema (25/25); +6.5pp monthly vs direct cap-25 anchor |
| Temporal v1.1 slice | 14 regression | 100% | 100% | 10/10 original, 4/4 infrequent |

Scorer: `gan_frequency_deterministic_v1` throughout. Dataset: Gan 2026, split `gan_2026_fixed_v1:validation`. Program variant: `gan_frequency_s0_temporal_candidates_verify_repair_v1_1`.

## Alignment Assessment

### Aligned with core objectives

**Deterministic infrastructure before model complexity.** Loaders, gold-source policies, normalization, splits, scorers, run artifacts, and evidence diagnostics remain stable. Scorer semantics were not changed to inflate metrics during the optimization sprint. Surface repair stays bounded; semantic changes flow through named verifier/repair variants with separate reporting.

**Gan before ExECT for optimization.** Kanban explicitly sequences Gan S0 as the tight reference task and ExECT S0/S1 as the broader-schema anchor. ExECT section-aware extraction was tried and deprioritized after a negative cap-25 result (monolithic 73.7% vs section-aware 65.6% micro F1 on 25 records).

**Reproducible experiments and ablations.** The May 19 sprint ran many one-factor probes (direct vs verify-repair, guardrails v2.x, GEPA, semantic optimizers, few-shot ladders, Gemini, temporal candidates). Most produced documented negative or inconclusive results rather than silent dead ends. Infrastructure additions (`record_ids` filters, stratified analyzer output, regression slice fixture, promotion decision doc) support governed iteration.

**Local versus closed-model comparison.** Comparisons use the same split and scorer with documented anchors. Finding: local Qwen needs structural help (temporal decomposition), not just larger token budgets or optimizer-heavy prompts.

**Modular specialization across tasks.** Gan exposes temporal-window, cluster, abstention, and evidence-grounding failures in a compact schema. ExECT exposes label-policy, cross-family leakage, and evidence-span failures across a wider field-family view. The two tasks remain intentionally distinct proving grounds.

### Appropriately deferred

**Beat published benchmarks.** Published Gan Purist micro-F1 is ~0.77–0.79 on Real(300); in-repo best hosted monthly is 65.4%. Gap is expected and explicitly scoped: `docs/published_benchmark_metrics.md` and kanban block benchmark-reproduction claims until scorer alignment and real-letter data exist.

**Downstream use cases** (clinical support, billing, cohort selection). No implementation work observed. Outline Phase 6 items (review UI, Postgres, FHIR export) remain backlog.

**Architecture comparison matrix** (monolithic vs field-group vs verify-repair at scale). Deferred until temporal v1.1 promotion tier is signed.

### Useful detours (evidence-backed, now closed or deprioritized)

| Detour | Outcome | Decision artifact |
| --- | --- | --- |
| GEPA + semantic optimizers | Operational but rejected for scale-up; prompt bloat, weak label gains | `docs/gan_s0_gepa_vs_synthesis_decision_20260519.md` |
| Few-shot / LabeledFewShot ladders | Did not clear infrequent gate; informed v2.4 hybrid baseline | `docs/gan_s0_few_shot_ladder_cap25_inspection_20260519.md` |
| Qwen token budget 256→1024 | No metric improvement; slower inference | `docs/qwen_local_latency_experiment_20260518.md` |
| Gemini Flash-Lite probes | Competitive labels/latency; weaker evidence vs GPT verify-repair | `docs/gan_s0_gemini31_flash_lite_full_validation_inspection_20260519.md` |
| ExECT section-aware ablation | Regressed vs monolithic on cap-25 | `docs/exect_section_aware_cap25_inspection.md` |

These detours satisfy the ablation intent in `docs/outline.md` without becoming permanent scope creep. The synthesis is captured in `docs/gan_s0_temporal_candidate_pivot_20260519.md`.

## Drift Signals

| Signal | Present? | Assessment |
| --- | --- | --- |
| Implementation without Kanban card | No | Temporal pivot has cards, gates, and decision doc |
| Model runs before scorer/data contracts stable | No | Scorers held constant across variants |
| UI/tooling dominating | No | No review UI, FastAPI, or export pipeline work |
| Narrow task expanding into broad architecture | No | Section-aware closed; temporal candidates are targeted |
| Cross-run claims without scorer caveats | Mostly no | Anchors documented; watch slice→full extrapolation |
| Optimizer path persisting after negative evidence | Resolved | GEPA deprioritized in kanban after May 19 probes |

## Unresolved Risks

### 1. Incomplete full-validation run (operational)

The temporal v1.1 full-validation directory (`…183614Z`) contains only `config.json`, `metadata.json`, and `prompts.json`. The run log (`runs/temporal_candidates_v1_1_full_validation_run.log`) reports progress only through 140/299 predictions. Promotion packet checklist items A–F in `docs/gan_s0_temporal_candidates_v1_1_full_validation_decision_20260519.md` cannot be completed until this run finishes.

### 2. Large uncommitted working tree (reproducibility)

As of the audit, ~1,784 lines across 22 tracked files plus many untracked configs, inspection docs, run artifacts, and `temporal_candidates.py` were not committed. Research traceability depends on git history; the current sprint's conclusions are not yet durable.

### 3. Slice perfection may not transfer to full split (interpretive)

Temporal v1.1 achieved 100% on the 14-record regression slice but only 44% monthly on cap-25. Tier 1 promotion requires ~55.9% monthly on full validation (299 records) or near-that with ≥99% schema and ≥99.5% evidence. There is a real risk of over-interpreting slice success while full-split label quality remains below the Qwen direct anchor.

### 4. Mild parallelization drift on ExECT

The promotion decision doc allowed ExECT cap-25 only until the Gan tier was signed. Full ExECT validation (40 records) completed in parallel. The work is anchor-scoring with no scorer changes, so substance is acceptable, but the explicit gate was bypassed for scheduling convenience.

### 5. Documentation lag

`docs/research_status_recap_20260519.md` still frames GEPA as a main active question while kanban has deprioritized it. The recap should be refreshed after the temporal tier decision.

## Interpretation

**Verdict: the project is aligned with the core research plan.** Work is concentrated on the right tight task (Gan S0 temporal reasoning), deterministic contracts are holding, and dead-end paths were tested and closed with evidence. The main risks are operational (stalled full validation, uncommitted artifacts) and interpretive (slice→full extrapolation), not strategic drift toward unrelated goals.

The temporal-candidate pivot represents a methodologically sound response to an identified failure family. Prompt-only iteration, GEPA, and few-shot selection did not unlock infrequent quantified rates because the blocker is **semantic window selection** — deciding which seizure events belong together, which interval is the denominator, and when a short seizure-free interval should not become a canonical seizure-free label. Decomposing that subproblem into deterministic candidates plus bounded verifier repair matches the four-layer architecture in `docs/outline.md`.

ExECT progress reinforces a separate lesson: on the audited S0/S1 field-family view, gains are more likely from **label-policy alignment** (seizure-type splitting, diagnosis surface, cross-family leakage) than from architecture reopening without a new hypothesis.

## Limitations of This Audit

- Based on artifacts and git state as of 2026-05-19; kanban and runs may advance after this document was written.
- Did not re-run experiments or re-score predictions; metrics are taken from inspection docs and run artifacts.
- Benchmark-reproduction gap was assessed from planning docs, not from a fresh scorer audit.
- Uncommitted code was assessed by diff stat and file inventory, not line-by-line review.

## Recommended Next Pull

Priority order:

1. **Resume or restart** Gan temporal v1.1 full validation (`configs/experiments/gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails.json`).
2. **Complete promotion packet A–F** per `docs/gan_s0_temporal_candidates_v1_1_full_validation_decision_20260519.md` and assign tier 1, 2, or 3.
3. **Commit the working tree** — temporal candidates module, program changes, analyzer, configs, inspection docs, kanban refresh.
4. **Gate ExECT label-policy v4** on the 12-record regression slice before cap-25 or full re-runs.

Do not reopen until tier is signed:

- Text-only Gan prompt iteration
- GEPA / semantic optimizer scale-up
- ReAct / B2 model event table
- Section-aware ExECT
- Hosted port of temporal guards

### Tier decision framework (pre-registered)

| Tier | Condition | Action |
| --- | --- | --- |
| **1 — Promote** | Full validation monthly ≥ Qwen direct full (~55.9%), or within ~1pp with schema ≥99% and evidence ≥99.5% | Default local Qwen Gan S0 path |
| **2 — Specialist** | Monthly between cap-25 direct (~37.5%) and full direct; slice B + strata hold without E regressions | Document; next engineering = B1 candidate expansion |
| **3 — Pivot** | Monthly ≤ cap-25 temporal (~44%) or E violations at scale | B2 event table before ReAct/hosted port |

E regression guard (veto): wrong YTD, stripped cluster, `unknown`→`no reference`, short seizure-free — shapes from `docs/gan_s0_temporal_candidate_pivot_20260519.md`.

## Tentative Claims

These remain open until full validation completes:

- Temporal v1.1 is the best local Qwen path for Gan S0 (tier decision pending).
- Deterministic temporal candidates generalize beyond the 14-record slice (slice cleared; full split unknown).
- ExECT monolithic v3/v4 baseline is stable enough to serve as the broad-schema anchor for architecture comparisons later.
- GEPA will not be the primary optimization tool for either dataset without a new hypothesis.

## Artifact References

### Planning and policy

- `docs/outline.md`
- `docs/kanban_plan.md`
- `docs/deterministic_foundation_decisions.md`
- `docs/deterministic_scorer_semantics.md`
- `docs/published_benchmark_metrics.md`
- `docs/gan_2026_label_audit.md`
- `docs/exect_gold_label_audit.md`

### May 19 research notes

- `docs/research_status_recap_20260519.md`
- `docs/gan_s0_temporal_candidate_pivot_20260519.md`
- `docs/gan_s0_temporal_candidates_v1_1_full_validation_decision_20260519.md`
- `docs/gan_s0_gepa_vs_synthesis_decision_20260519.md`
- `docs/exect_s0_s1_validation_full_inspection.md`

### Key runs

- Slice gate: `runs/gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_guardrails_20260519T180329Z`
- Cap-25 gate: `runs/gan_s0_qwen35b_temporal_candidates_verify_repair_cap25_guardrails_validation_20260519T183213Z`
- Full validation (incomplete): `runs/gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T183614Z`
- Hosted anchor: `runs/gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z`
- Qwen direct anchor: `runs/gan_s0_qwen35b_direct_full_validation_guardrails_20260519T102249Z`
- ExECT full validation: `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T200017Z`

### Code touched in active workstream (partially uncommitted)

- `src/clinical_extraction/gan/temporal_candidates.py`
- `src/clinical_extraction/programs/gan_frequency_s0.py`
- `src/clinical_extraction/evaluation/gan_run_analysis.py`
- `scripts/analyze_gan_frequency_run.py`
