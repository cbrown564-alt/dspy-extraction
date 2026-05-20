# Research Drift Audit — Status Update

Date: 2026-05-19 (refreshed after kanban dual-track update)  
Audit type: alignment check against core research plan  
**Superseded for active planning by:** `docs/research_drift_audit_20260520.md` (hosted ExECT ladder frozen; Qwen replication; Gan Tier 1 signed)  
Active tracker: `docs/kanban_plan.md`  
Narrative archive: `docs/research_status_recap_20260519.md`

## Research Question

Is the project still aligned with the hybrid deterministic + DSPy clinical extraction research plan in `docs/outline.md`, or has recent work drifted toward distractions, premature breadth, or ungoverned experimentation?

## Motivation

The repo completed its deterministic foundation milestone and entered an intensive model-backed optimization phase on 2026-05-17 through 2026-05-19. That phase produced many parallel experiment paths (GEPA, few-shot ladders, verify-repair, temporal candidates, ExECT label-policy ladder) plus a large working tree of runs and inspection docs. A drift audit confirms whether active work still serves stated research objectives and flags operational risks before the Gan temporal v1.1 promotion decision.

## Method

This audit followed the project `research-drift-audit` workflow:

1. **Core direction documents**
   - `docs/outline.md` — research goals, architecture layers, ablation plan
   - `docs/kanban_plan.md` — active tracker, dual-track map, gates
   - `docs/deterministic_foundation_decisions.md` — infrastructure-first policy
   - `docs/research_status_recap_20260519.md` — narrative synthesis
   - `docs/gan_s0_temporal_candidates_v1_1_full_validation_decision_20260519.md` — pre-registered Gan promotion tiers
   - `docs/gan_s0_temporal_candidate_pivot_20260519.md` — pivot rationale
   - `docs/exect_s0_label_policy_v4_2_implementation.md` — ExECT v4.2 anchor

2. **Recent git history** — 40+ commits since 2026-05-17; latest sprint commit `bfb157b` (Gan temporal + ExECT v4.2).

3. **Run artifacts** — promotion gate runs, ExECT v4.2 ladder, Gan full-validation log under `runs/`.

4. **Alignment axes** (from `docs/outline.md`):
   - benchmark reproduction and improvement
   - deterministic infrastructure before model complexity
   - Gan versus ExECT sequencing
   - reproducible experiments and ablations
   - local versus closed-model comparison
   - downstream use-case exploration

## Current Position

The project operates on **two parallel tracks** (see `docs/kanban_plan.md` § Execution Model). They share deterministic infrastructure but differ in model, latency, and promotion gates:

| Track | Model | Role | Active bet |
| --- | --- | --- | --- |
| **A — Gan S0** | Qwen3.6:35b (local) | Tight reference task; local-model promotion path | Temporal-candidates v1.1 + confirm-first verifier guards |
| **B — ExECT S0/S1** | GPT 4.1-mini (hosted) | Broader-schema label-policy iteration | Monolithic v4.2 prompt + deterministic bridges |

**Gan** remains the gate for **local-model promotion** (slice → cap-25 → full validation, pre-registered tiers). **ExECT** is no longer “cap-25 only until Gan tier signs” — it is an explicit **parallel rapid-iteration path** on hosted GPT while the slow Qwen full validation run completes (~600 calls).

### Active tracks (2026-05-19)

| Track | Stage | Status | Primary artifact |
| --- | --- | --- | --- |
| **A** Gan temporal v1.1 slice | 14-record regression | **Gate cleared** | `…180329Z` — 100% monthly/schema/evidence |
| **A** Gan temporal v1.1 cap-25 | 25-record validation | **Gate cleared** | `…183213Z` — 44% monthly, 100% schema |
| **A** Gan temporal v1.1 full | 299-record validation | **In progress** (~180/299 in log) | `…183614Z`; log `runs/temporal_candidates_v1_1_full_validation_run.log` |
| **B** ExECT label-policy v4.2 | 15-record slice | **Gate cleared** | `…202412Z` — 89.1% micro F1 |
| **B** ExECT label-policy v4.2 | cap-25 / full | **Anchor set** | `…202537Z` / `…202626Z` — 86.4% / **78.5%** micro F1 |
| **B** ExECT diagnosis-recall probe | 14-record slice | **Negative — closed** | `…202910Z`; `docs/exect_s0_s1_diagnosis_recall_probe_inspection_20260519.md` |
| Published benchmark reproduction | — | **Blocked** | CUI-aware ExECT scorer; no Gan Real(300) access |

### Quality anchors (unchanged for cross-run claims)

| Path | Split | Monthly / micro F1 | Evidence | Notes |
| --- | --- | ---: | ---: | --- |
| GPT verify-repair v2 (Gan) | 299 validation | 65.4% monthly | 92.7% | Hosted quality ceiling |
| Qwen direct + guardrails (Gan) | 299 validation | 55.9% monthly | 99.6% | Local baseline |
| Temporal v1.1 cap-25 (Gan) | 25 validation | 44.0% monthly | 100% | 100% schema; +6.5pp vs direct cap-25 |
| Temporal v1.1 slice (Gan) | 14 regression | 100% monthly | 100% | 10/10 original, 4/4 infrequent |
| ExECT v4.2 monolithic (ExECT) | 40 validation | **78.5%** micro F1 | 84.0% | +10.7pp vs v3 full; current broad-schema anchor |
| ExECT v3 monolithic (ExECT) | 40 validation | 67.8% micro F1 | 87.6% | Historical comparison only |

Gan scorer: `gan_frequency_deterministic_v1`. ExECT scorer: `exect_field_family_deterministic_v1`. Do not compare Gan monthly % to ExECT micro F1.

## Alignment Assessment

### Aligned with core objectives

**Deterministic infrastructure before model complexity.** Loaders, gold-source policies, normalization, splits, scorers, run artifacts, and evidence diagnostics remain stable. Scorer semantics were not changed to inflate metrics during the optimization sprint. Surface repair stays bounded; semantic changes flow through named verifier/repair variants with separate reporting.

**Dual-track sequencing (refined).** Gan S0 is still the **optimization gate for local Qwen** and the tightest proving ground for temporal/cluster/abstention failures. ExECT S0/S1 is a **parallel hosted track** for label-policy and cross-family leakage — not blocked by Gan full validation. This matches `docs/outline.md` (GPT 4.1-mini for rapid iteration; Qwen for local deployment) and removes the earlier “ExECT cap-25 only” scheduling constraint, which was operational rather than research-policy.

**Gan before ExECT for local-model claims only.** Cross-dataset promotion comparisons remain invalid; within ExECT, v4.2 full validation is the anchor for the audited field-family view.

**Reproducible experiments and ablations.** The May 19 sprint ran one-factor probes with documented outcomes (GEPA rejected, diagnosis-recall negative, section-aware negative, temporal v1 regressed → v1.1 guards). Infrastructure: `record_ids` filters, stratified analyzer, regression slice fixtures for both datasets.

**Local versus closed-model comparison.** Same split and scorer per dataset with documented anchors. Finding: local Qwen needs structural temporal help; hosted GPT supports fast ExECT label-policy iteration without waiting on Ollama throughput.

**Modular specialization across tasks.** Gan and ExECT remain distinct proving grounds; parallel execution uses idle hosted capacity while local GPU runs long validation.

### Appropriately deferred

**Beat published benchmarks.** Published Gan Purist micro-F1 is ~0.77–0.79 on Real(300); in-repo best hosted monthly is 65.4%. Gap expected until scorer alignment and real-letter data exist (`docs/published_benchmark_metrics.md`).

**Downstream use cases** (clinical support, billing, cohort selection). No implementation work. Outline Phase 6 items remain backlog.

**Architecture comparison matrix** (monolithic vs field-group vs verify-repair at scale). Deferred until Gan temporal tier is signed; ExECT verify-repair confirm-first remains a bounded backlog probe.

**Gan engineering fork (B1/B2/ReAct/hosted port).** Blocked on tier decision per `docs/gan_s0_temporal_candidates_v1_1_full_validation_decision_20260519.md`.

### Useful detours (evidence-backed, now closed or deprioritized)

| Detour | Outcome | Decision artifact |
| --- | --- | --- |
| GEPA + semantic optimizers | Rejected for scale-up | `docs/gan_s0_gepa_vs_synthesis_decision_20260519.md` |
| Few-shot / LabeledFewShot ladders | Did not clear infrequent gate | `docs/gan_s0_few_shot_ladder_cap25_inspection_20260519.md` |
| Qwen token budget 256→1024 | No metric improvement | `docs/qwen_local_latency_experiment_20260518.md` |
| Gemini Flash-Lite probes | Weaker evidence vs GPT verify-repair | `docs/gan_s0_gemini31_flash_lite_full_validation_inspection_20260519.md` |
| ExECT section-aware ablation | Regressed vs monolithic on cap-25 | `docs/exect_section_aware_cap25_inspection.md` |
| ExECT diagnosis-recall add-only pass | Recall flat; precision collapsed | `docs/exect_s0_s1_diagnosis_recall_probe_inspection_20260519.md` |

## Drift Signals

| Signal | Present? | Assessment |
| --- | --- | --- |
| Implementation without Kanban card | No | Both tracks mapped in kanban Thread A/B |
| Model runs before scorer/data contracts stable | No | Scorers held constant per dataset |
| UI/tooling dominating | No | No review UI or export pipeline work |
| Narrow task expanding into broad architecture | No | Section-aware and diagnosis-recall closed |
| Cross-run claims without scorer caveats | Mostly no | Anchors documented; cap-25 optimistic on ExECT |
| Optimizer path persisting after negative evidence | Resolved | GEPA deprioritized |
| **Parallel ExECT full validation during Gan run** | **Was flagged; now resolved** | Reframed as intentional Track B — see below |

## Parallel ExECT Work — Resolved (Not Drift)

An earlier version of `docs/gan_s0_temporal_candidates_v1_1_full_validation_decision_20260519.md` listed “ExECT cap-25 only” until the Gan tier was signed. The May 19 sprint then completed:

- ExECT label-policy v4 → v4.1 → **v4.2** (slice, cap-25, full validation)
- ExECT diagnosis-recall probe (negative, closed)

**Assessment:** This is **aligned**, not mild drift:

1. **Different resource pool** — hosted GPT minutes vs local Qwen hours; parallel use is efficient.
2. **Different promotion question** — ExECT asks “label-policy + bridges on audited field families”; Gan asks “temporal candidates on local Qwen.”
3. **No scorer or split contamination** — `exect_field_family_deterministic_v1` unchanged; benchmarks not mixed across datasets.
4. **Kanban updated** — `docs/kanban_plan.md` now documents Track A / Track B explicitly; the cap-25-only note in the promotion decision doc is **superseded for planning** by kanban (decision doc tier gates for **Gan B1/B2/ReAct** remain valid).

**Residual discipline:** ExECT cap-25 remains diagnostically optimistic (~7–9pp above full). Promotion claims on ExECT require full-validation runs, same as Gan.

## Unresolved Risks

### 1. Incomplete Gan full-validation run (operational)

`…183614Z` had no `metrics.json` at audit refresh; log reported ~180/299 predictions. Promotion packet A–F cannot complete until the run finishes.

### 2. Large working tree (reproducibility)

Many configs, inspection docs, and run artifacts may remain uncommitted. Research traceability improves after commit of the May 19 sprint.

### 3. Slice perfection may not transfer to full split (interpretive — Gan)

Temporal v1.1: 100% on 14-record slice, 44% monthly on cap-25. Tier 1 requires ~55.9% monthly on full validation or near-that with high schema/evidence. Risk of over-interpreting slice success remains.

### 4. ExECT cap-25 optimism (interpretive — ExECT)

v4.2: 86.4% micro F1 cap-25 vs 78.5% full. Label-policy gains are real but full validation is the anchor for cross-version claims.

### 5. Documentation lag

`docs/research_status_recap_20260519.md` may still overweight GEPA as an open question; refresh after Gan tier decision. Kanban dual-track section is now authoritative for **what to do next**.

## Interpretation

**Verdict: the project is aligned with the core research plan.** Work concentrates on the right tight local task (Gan temporal reasoning) while using a governed parallel path for broader-schema label policy (ExECT v4.2). Dead-end paths were tested and closed with evidence.

The temporal-candidate pivot addresses **semantic window selection** (which events aggregate, which denominator, when short seizure-free must not become canonical seizure-free). ExECT v4.2 reinforces that on the audited field-family view, gains come from **label-policy alignment and deterministic bridges**, not section splitting or add-only recall passes.

**Dual-track execution is a feature, not drift** — provided each track keeps its own anchors, scorers, and promotion gates.

## Limitations of This Audit

- Based on artifacts and git state as of 2026-05-19; runs may advance after this refresh.
- Did not re-run experiments; metrics from inspection docs and run artifacts.
- Gan full-validation progress taken from log tail, not live process check.
- Uncommitted code assessed at prior audit scope; line-by-line review not repeated.

## Recommended Next Pull

**Track A — Gan (when `…183614Z` completes):**

1. Run promotion packet A–F per `docs/gan_s0_temporal_candidates_v1_1_full_validation_decision_20260519.md`.
2. Assign tier 1, 2, or 3; update kanban anchors if tier 1.
3. Do not reopen text-only Gan prompts unless tied to candidate selection policy.

**Track B — ExECT (now, in parallel):**

1. Error-read v4.2 full validation (`…202626Z`) — medication F1 and evidence gaps vs seizure gains.
2. Expand `data/fixtures/exect_s0_label_policy_error_regression_slice.json` from full-validation false positives before v4.3.
3. Keep v4.2 as anchor until a successor clears slice gate.

**Shared:**

- Commit sprint artifacts when ready.
- Run focused pytest on Gan temporal + ExECT scoring + experiment configs (see kanban).

**Blocked until Gan tier signed:** Gan B1/B2/ReAct/hosted port; runner refactor during promotion interpretation.

**Do not reopen:** GEPA scale-up; section-aware ExECT; diagnosis-recall v1; Gemini verify-repair scale-up.

### Tier decision framework (Gan — pre-registered)

| Tier | Condition | Action |
| --- | --- | --- |
| **1 — Promote** | Full validation monthly ≥ Qwen direct full (~55.9%), or within ~1pp with schema ≥99% and evidence ≥99.5% | Default local Qwen Gan S0 path |
| **2 — Specialist** | Monthly between cap-25 direct (~37.5%) and full direct; slice B + strata hold without E regressions | Document; next = B1 candidate expansion |
| **3 — Pivot** | Monthly ≤ cap-25 temporal (~44%) or E violations at scale | B2 event table before ReAct/hosted port |

E regression guard (veto): wrong YTD, stripped cluster, `unknown`→`no reference`, short seizure-free.

## Tentative Claims

Open until Gan full validation completes:

- Temporal v1.1 is the best local Qwen path for Gan S0 (tier pending).
- Deterministic temporal candidates generalize beyond the 14-record slice (full split unknown).

Supported by completed ExECT runs:

- **ExECT v4.2 monolithic is the broad-schema anchor** (78.5% micro F1 full, scorer unchanged).
- Add-only diagnosis-recall does not improve benchmark-facing diagnosis F1 on the hard slice.
- GEPA is not the primary optimization tool without a new hypothesis.

## Artifact References

### Planning and policy

- `docs/outline.md`
- `docs/kanban_plan.md`
- `docs/deterministic_foundation_decisions.md`
- `docs/deterministic_scorer_semantics.md`
- `docs/exect_s0_s1_baseline_design.md`
- `docs/gan_2026_label_audit.md`
- `docs/exect_gold_label_audit.md`

### May 19 research notes

- `docs/research_status_recap_20260519.md`
- `docs/gan_s0_temporal_candidate_pivot_20260519.md`
- `docs/gan_s0_temporal_candidates_v1_1_full_validation_decision_20260519.md`
- `docs/exect_s0_label_policy_v4_2_implementation.md`
- `docs/exect_s0_s1_diagnosis_recall_probe_inspection_20260519.md`
- `docs/exect_s0_label_policy_regression_slice_comparison_20260519.md`

### Key runs

| Track | Run |
| --- | --- |
| Gan slice gate | `…180329Z` |
| Gan cap-25 gate | `…183213Z` |
| Gan full (in progress) | `…183614Z` |
| Gan hosted anchor | `…084732Z` |
| Gan Qwen direct anchor | `…102249Z` |
| ExECT v4.2 full anchor | `…202626Z` |
| ExECT v3 full (historical) | `…200017Z` |
| ExECT diagnosis-recall (negative) | `…202910Z` |

### Code (active workstream)

- `src/clinical_extraction/gan/temporal_candidates.py`
- `src/clinical_extraction/programs/gan_frequency_s0.py`
- ExECT label-policy bridges in ExECT program module (v4.2)
- `src/clinical_extraction/evaluation/gan_run_analysis.py`
