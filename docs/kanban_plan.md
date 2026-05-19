# Clinical Extraction Kanban Plan

Source: `docs/outline.md`  
Grounding: `docs/deterministic_foundation_decisions.md`  
Local Qwen policy: `docs/qwen_dspy_latency_policy.md`  
Deep recap (metrics, decisions, citations): `docs/research_status_recap_20260519.md` (narrative archive; this file is the active tracker)  
Alignment audit: `docs/research_drift_audit_20260519.md`  
Architecture review: `docs/codebase_architecture_review_20260519.md`  
Last refreshed: 2026-05-19 (cap-25 gate **cleared** — 100% schema, 44% monthly)

## Session Handoff

**Active tracks:**

| Track | Status | Artifact / command |
| --- | --- | --- |
| Gan S0 Qwen temporal v1.1 full validation | **Review** — promotion packet | `…183614Z`; `docs/gan_s0_temporal_candidates_v1_1_full_validation_decision_20260519.md`; log `runs/temporal_candidates_v1_1_full_validation_run.log` |
| ExECT S0/S1 monolithic full validation v4.2 (GPT 4.1-mini) | **Done** — micro F1 **78.5%** (40 records); new anchor | `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T202626Z`; `docs/exect_s0_label_policy_v4_2_implementation.md` |
| ExECT diagnosis-recall probe v1 | **Negative** — slice recall flat, precision regressed | `runs/exect_s0_s1_diagnosis_recall_regression_slice_gpt4_1_mini_20260519T202910Z`; `docs/exect_s0_s1_diagnosis_recall_probe_inspection_20260519.md` |
| ExECT S0/S1 monolithic full validation v4.1 | **Historical** — 75.3% micro F1 | `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T201721Z` |
| ExECT S0/S1 monolithic full validation v3 | **Historical** — 67.8% micro F1 | `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T200017Z` |

**Slice comparison (14 records, same scorer):**

| Variant | Monthly | Schema valid | Original 10 | Infrequent 4 |
| --- | ---: | ---: | ---: | ---: |
| v2.4 hybrid | 71.4% (10/14) | 14/14 | 9/10 | 1/4 |
| Temporal v1 (prompt only) | 50.0% (7/14) | 11/14 | 5/10 | 3/4 |
| **Temporal v1.1 (guards)** | **100% (14/14)** | **14/14** | **10/10** | **4/4** |

**Promotion gates:**

| Gate | Requirement | Status |
| --- | --- | --- |
| Slice → cap-25 | ≥3/4 infrequent gold-correct, original ≥10/10, schema 100%, evidence 100% | **Cleared** (`…180329Z`) |
| Cap-25 → full validation | Material monthly/Purist gain without invalid-cluster or short seizure-free regression | **Cleared** (`…183213Z`) — 100% schema (25/25), 44% monthly (+6.5pp vs direct), 100% evidence |

**Latest artifacts:**

| Artifact | Role |
| --- | --- |
| `runs/gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_guardrails_20260519T180329Z` | **Slice gate run** — temporal v1.1, 100% all metrics |
| `docs/gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_guardrails_error_analysis.md` | Post-run analyzer (updated for v1.1 run) |
| `src/clinical_extraction/programs/gan_frequency_s0.py` | `_apply_temporal_verifier_guards` confirm-first + candidate-gated repair |
| `runs/gan_s0_qwen35b_temporal_candidates_verify_repair_cap25_guardrails_validation_20260519T183213Z` | **Cap-25 post-repair** — 44% monthly, **100% schema** (25/25) |
| `runs/gan_s0_qwen35b_temporal_candidates_verify_repair_cap25_guardrails_validation_20260519T181053Z` | Cap-25 pre-repair — 45.5% monthly, 88% schema (3 invalid) |
| `configs/experiments/gan_s0_qwen35b_temporal_candidates_verify_repair_cap25_guardrails_validation.json` | Cap-25 config |
| `runs/gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_guardrails_20260519T175345Z` | Temporal v1 baseline (regressed original/schema) |
| `runs/gan_s0_qwen35b_labeled_fewshot_verify_repair_regression_slice_guardrails_20260519T171413Z` | v2.4 hybrid (prior best balanced row) |
| `docs/gan_s0_temporal_candidate_pivot_20260519.md` | Pivot rationale |

**Quality anchors (do not replace):**

| Path | Monthly | Evidence | Notes |
| --- | --- | --- | --- |
| GPT 4.1-mini verify-repair v2 full validation `…084732Z` | 65.4% | 92.7% | Hosted quality anchor |
| Qwen3.6:35b direct full validation guardrails `…102249Z` | 55.9% | 99.6% | Local baseline (v1 prompt) |
| Qwen3.6:35b direct cap-25 v2 `…140952Z` | 37.5% | 100% | Best local cap-25 monthly |

**Commands:**

```powershell
uv run --extra dev pytest tests/test_gan_temporal_candidates.py tests/test_gan_frequency.py tests/test_gan_scoring.py tests/test_gan_qwen_error_regression_slice.py tests/test_gan_s0_program.py tests/test_experiment_configs.py tests/test_analyze_gan_frequency_run.py

uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails.json --env-file .env

uv run python scripts/analyze_gan_frequency_run.py runs/<run_id> --split-name gan_2026_fixed_v1:validation --markdown docs/gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_error_analysis.md

# Slice replay on a full-validation run dir (promotion packet B):
uv run python scripts/analyze_gan_frequency_run.py runs/<run_id> --split-name gan_2026_fixed_v1:validation --record-ids-file data/fixtures/gan_s0_qwen_error_regression_slice.json --markdown docs/gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_from_full_validation_error_analysis.md
```

**Deprioritized:** semantic bootstrap/GEPA full validation; Gemini verify-repair scale-up; routine GEPA on Qwen 35B.

## Goal

Hybrid deterministic + DSPy clinical extraction across ExECTv2 (broad) and Gan seizure-frequency (focused), with dataset fidelity, reproducible splits, auditable scoring, and experiment traceability.

**Execution focus:** Gan S0 as the tight reference task. **Hosted** anchor: GPT 4.1-mini verify-repair v2. **Local** path: Qwen3.6:35b direct + guardrails, gated by the 14-record regression slice. GEPA/semantic optimizers are not the active path. ExECT S0/S1 monolithic baseline is the broader-schema anchor, not the current implementation gate.

## Definitions Of Done

- ExECTv2 and Gan gold load from agreed sources without silent scorer changes.
- Raw, normalized, flags, evidence diagnostics, and benchmark-facing views stay separable.
- Gan splits are reproducible with documented salt, allocation, stratification, and hard-case counts.
- Scorers expose benchmark-facing and diagnostic metrics separately.
- DSPy runs record dataset, split, model, schema, variant, scorer, configs, predictions, metrics, errors, artifacts, and caveats.
- Cross-run comparisons state when scorer semantics differ.

## Historical Context

Summarized only — full narratives, run tables, and error reads live in linked docs and `docs/research_status_recap_20260519.md`.

### Deterministic foundation (complete)

Loaders, normalization, `gan_frequency_deterministic_v1` / ExECT field-family scorers, splits, manifests, prediction/evidence schemas, evaluation CLI, run artifacts, evidence support, bootstrap CIs, review export. Policy: Gan `seizure_frequency_number[0]` is gold; ExECT benchmark-facing S0/S1 = diagnosis, seizure type, annotated medications only.

Key refs: `docs/deterministic_scorer_semantics.md`, `docs/gan_2026_label_audit.md`, `docs/exect_gold_label_audit.md`, `tests/test_gan_scoring.py`, `tests/test_exect_scoring.py`.

### Gan S0 model-backed arc

| Phase | Outcome | Primary artifact |
| --- | --- | --- |
| Synthesis BootstrapFewShot | Strongest **hosted direct** reference | `runs/gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z` (monthly 62.9%, evidence 89.9%) |
| Surface repair replay | Schema 97.3%→98.3%; semantic gaps remain | `docs/gan_s0_post_repair_validation_replay.md` |
| Verify-repair v2 (GPT) | **Hosted quality anchor** | `runs/gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z` |
| GEPA / semantic optimizers | Rejected for scale-up; prompt bloat | `docs/gan_s0_gepa_vs_synthesis_decision_20260519.md` |
| Qwen guardrails + full validation | Stable evidence; label gap vs hosted | `runs/gan_s0_qwen35b_direct_full_validation_guardrails_20260519T102249Z` |
| Prompt v2 → v2.4 + hybrid | Slice original targets recovered; **infrequent stuck at 1/4** | Pivot: `docs/gan_s0_temporal_candidate_pivot_20260519.md` |
| Temporal candidates v1.1 slice | **Gate cleared** — 100% all metrics, 4/4 infrequent | `…180329Z`; deterministic verifier guards |
| Temporal candidates v1 slice | 3/4 infrequent; original/schema regression | `…175345Z` |

Infrastructure landed: `record_ids` on experiment configs; `gan_failure_taxonomy` + scoped `gan_run_analysis` (`analysis_scope=record_ids_filter`); stratified operational reporting in analyzer output.

### ExECT S0/S1 (anchored, not active frontier)

Monolithic field-family baseline: **v4.2 anchor** (full 78.5% micro F1, +10.7pp vs v3). Cap-25 v4.2 was 86.4% (optimistic vs full). Section-aware **underperformed** — deprioritized.

### Hosted model comparison

`docs/gan_s0_hosted_model_comparison_matrix.md` — Gemini 3.1 Flash-Lite competitive on labels/latency/cost; **evidence trails GPT verify-repair** (84.9% vs 92.7% full validation).

## Kanban

### Ready

No card claimed.

### In Progress

No card claimed.

### Review

#### Temporal-candidates v1.1 full validation — promotion decision

- **Run:** `runs/gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T183614Z` (log: `runs/temporal_candidates_v1_1_full_validation_run.log`)
- **Decision doc:** `docs/gan_s0_temporal_candidates_v1_1_full_validation_decision_20260519.md` (tiers + A–F packet pre-registered)
- **On completion:** Run analyzer (A) + slice replay (B) per decision doc; fill headline table; assign tier 1/2/3; update Session Handoff
- **Do not start until tier signed:** B1/B2/ReAct/hosted port (see decision doc engineering fork)

### Done (recent)

| Card | Outcome |
| --- | --- |
| ExECT diagnosis-recall probe (v1) | **Negative** — 14-record slice: diagnosis recall flat (36%), precision 90%→53%; `…202910Z`; `docs/exect_s0_s1_diagnosis_recall_probe_inspection_20260519.md` |
| ExECT S0/S1 monolithic full validation (GPT 4.1-mini) | `…200017Z` — micro F1 67.8%, evidence 87.6%; cap-25 was optimistic (73.7%); inspection `docs/exect_s0_s1_validation_full_inspection.md` |
| Cap-25 re-run post schema surface repairs | `…183213Z` — 100% schema (25/25), 44% monthly, 100% evidence; error analysis refreshed |
| Cap-25 schema-invalid surface repairs | `per hour` → daily/`multiple per day`; rate+`, N per cluster` → insert `cluster`; 6 new tests; scorer unchanged |
| Temporal-candidates v1.1 cap-25 validation (pre-repair) | 45.5% monthly (+8pp vs direct anchor); 88% schema (3 invalid); `…181053Z` |
| Temporal verifier v1.1 confirm-first + candidate-gated guards | Deterministic guards; slice 100% (`…180329Z`); 4 new tests |
| Run temporal-candidates verify-repair on Qwen regression slice | v1 run `…175345Z` exposed verifier over-repair; led to v1.1 |
| Wire temporal candidates into experiment + analyzer | Program variant, metadata fields, `temporal_candidate_diagnostics` in analyzer; slice config ready |
| Temporal-candidate pivot report + scaffold | `docs/gan_s0_temporal_candidate_pivot_20260519.md`; `temporal_candidates.py` + tests (4/4 infrequent gold in candidate set) |
| LabeledFewShot + verify-repair v2.4 hybrid probe | Ties v2.4 (71.4%, 1/4 infrequent); `docs/gan_s0_qwen35b_labeled_fewshot_verify_repair_regression_slice_guardrails_error_analysis.md` |
| Verify-repair v2.4 regression slice | 4096 tokens clears truncation; 9/10 original, 1/4 infrequent |
| Bounded verify-repair + LabeledFewShot infrequent probe | v2.3 over-repair; LabeledFewShot 0/4 infrequent |
| Qwen guardrails v2.2 | Original 10/10; infrequent 0/4; cap-25 monthly regressed |
| Gan stratified operational reporting | Strata in `summary.json` + Markdown |
| Qwen regression slice + analyzer taxonomy | Fixture `gan_s0_qwen_error_regression_v1`; `record_ids_filter` scope |
| GPT verify-repair v2 full validation | Hosted anchor run + inspection docs |
| ExECT label-policy v4.2 (granular seizure + medication guardrails) | Prompt + bridges; 15-record slice expanded; scorer unchanged |
| ExECT label-policy v4/v4.1 (seizure split + diagnosis surface) | Full v4.1 anchor 75.3% micro F1; comparison docs |
| ExECT S0/S1 monolithic baseline + cap-25 | Field-family contract; section-aware negative result recorded |

Older completed cards (GEPA harness, Gemini caps, few-shot ladder, overnight Qwen ladder, ExECT smokes, runtime/token capture, etc.) are recorded in git history and `docs/research_status_recap_20260519.md` — not duplicated here.

## Blocked

#### Reproduce published ExECTv2 and Gan benchmark numbers

- **Blocked on:** CUI/feature-aware ExECT all-family scorer; Gan Real(300)/Real(150) access; benchmark alignment tests.
- **Notes:** Current metrics are partial/diagnostic for published-benchmark claims.

#### Run Qwen-backed local model comparisons (matrix)

- **Blocked on:** Cap-25 temporal-candidate validation; slice gate now cleared.
- **Notes:** 35B full-validation row exists; cap-25/monthly still trails until cap-25 gate clears.

## Backlog

#### Consolidate experiment runner and program modules

- **Report:** `docs/codebase_architecture_review_20260519.md`
- **Goal:** Reduce orchestration branching and god-module coupling without changing scorer semantics or active experiment contracts.
- **Blocked on:** Gan temporal v1.1 promotion tier signed (do not refactor during active full-validation interpretation).
- **Phase 1 (runner):** Extract `clinical_extraction/experiments/runner.py`; add `ExperimentBackend` registry for `gan_2026` and `exect_v2`; thin `scripts/run_experiment.py` to CLI only; keep `tests/test_run_experiment_runtime.py` green.
- **Phase 2 (programs):** Split `programs/gan_frequency_s0.py` into `programs/gan/` (signatures, modules, metrics, predict); mirror for ExECT when Gan split is stable.
- **Phase 3 (evaluation):** Unify `evaluation/cli.py` for Gan + ExECT `PredictionSet`; extract shared prediction/evidence helpers.
- **Phase 4 (hygiene):** Relocate `kanban.py` out of `src/clinical_extraction/`; optional `pyproject.toml` console entry points.
- **Out of scope:** `gan_frequency_deterministic_v1`, split policy, benchmark-reproduction scorer alignment, prompt-policy content changes bundled with structural moves.

| Card | Outcome / dependency |
| --- | --- |
| Consolidate experiment runner and program modules | See detailed card above; unblocks “Experiment configs for architecture ablations” |
| ExECT full verify-repair confirm-first probe | After diagnosis-recall v1 negative; bounded all-field verify-repair |
| Gan abstention calibration | After verifier/repair boundary is stable |
| Field-group / section-aware DSPy modules | New hypothesis only (ExECT section-aware failed) |
| Experiment configs for architecture ablations | After runner registry + program module split (architecture review Phase 1–2) |
| Review workflow on JSONL export | Independent of model path |
| Gan ReAct temporal-tools probe | Design before agentic runs; `docs/dspy_gepa_react_best_practices_deep_dive.md` |
| ExECT S0/S1 GEPA feedback | After Gan GEPA path justified (currently deprioritized) |
| Gold-label ambiguity audit (DSPy-assisted) | Horizon; diagnostic flags only |
| Schema omission / selection-rule quantification | Horizon; Gan + ExECT audits |
| Seizure-letter complexity taxonomy | After ambiguity + schema audits |

## Questions (resolved)

| Question | Decision |
| --- | --- |
| Gan before ExECT? | **Yes** for optimization; ExECT monolithic is comparison anchor |
| Acceptable semantic Gan repair? | Surface-only in deterministic bridge; meaning changes → explicit verifier/repair variant |
| First ExECT baseline breadth? | Diagnosis + seizure type + annotated medications only |

## Long-Term Phases

1. **Gan S0** — temporal-candidate path → slice gate → cap-25 → full validation; keep hosted verify-repair v2 as quality ceiling.
2. **ExECT S0/S1** — monolithic-first improvements; reopen section-aware only with new hypothesis.
3. **Architecture comparison** — monolithic vs field-group vs section-aware vs verify-repair; ReAct only as bounded Gan temporal probe.
4. **Model matrix** — fixed split/scorer/variant; Qwen direct-only on 35B.
5. **ExECT breadth** — additional families after scorer audits.
6. **Benchmark reproduction** — long-term; explicit alignment caveats.

## Dependency Notes (current)

- **Single-threaded:** scorer semantics, `gan_frequency_deterministic_v1`, split policy, benchmark-reproduction claims.
- **Active lever:** temporal-candidates v1.1 cleared slice + cap-25 gates; next is full validation.
- **Plateau broken on slice:** v1.1 100% vs v2.4 hybrid 71.4%; cap-25 100% schema vs 88% pre-repair.
- **Anchors:** GPT verify-repair v2 hosted; Qwen v1 guardrails full validation; best local cap-25 = v2 direct (37.5% monthly).
- **Deprioritized:** GEPA/semantic full validation at scale; Gemini verify-repair scale-up.
- **ExECT:** monolithic cap-25 anchor; section-aware negative result stands.
- **Horizon:** gold-ambiguity audit, schema-omission analysis, complexity taxonomy — do not block Gan slice work.

## Parallelization

- **Now:** Gan temporal v1.1 full validation in Review (`…183614Z`; Qwen sequential).
- **ExECT anchor (done):** full validation `docs/exect_s0_s1_validation_full_inspection.md` (67.8% micro F1); cap-25 73.7% was optimistic; section-aware deprioritized.
- **Defer until Gan tier signed:** B1/B2, hosted Gan port, ReAct, GEPA.
- **Single-threaded:** scorer semantics, `gan_frequency_deterministic_v1`, split policy, benchmark-reproduction claims.

## Recommended Next Pull

1. Monitor full-validation run (`gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails`); on completion, run analyzer and compare to anchors.
2. Compare full-validation monthly/Purist/evidence to Qwen direct guardrails anchor (`…102249Z`) and hosted GPT verify-repair v2 (`…084732Z`).
3. Do not reopen text-only prompt iteration unless tied to candidate selection policy.
4. Keep anchors unchanged for cross-run claims (GPT verify-repair v2; Qwen full-validation v1; v2 direct cap-25).
