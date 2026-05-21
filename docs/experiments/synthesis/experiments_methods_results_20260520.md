# Methods and Results: Clinical Extraction Experiments (Through 2026-05-20)

Companion to [`experiments_narrative_report_20260520.md`](experiments_narrative_report_20260520.md).  
Artifact index: `runs/`, `configs/experiments/`, `docs/planning/kanban_frozen_threads_history.md`.

---

## Methods

### Study design

We evaluate a hybrid **deterministic + DSPy** pipeline for structured extraction from synthetic epilepsy clinic letters. Two datasets define complementary task difficulty:

| Dataset | Letters | Task character | Primary benchmark-facing output |
| --- | ---: | --- | --- |
| **Gan 2026** | 1,500 synthetic (repo subset) | Narrow schema; temporal logic; mandatory source evidence | Canonical seizure-frequency label (`seizure_frequency_number[0]`) |
| **ExECTv2** | 200 synthetic | Broad hierarchical schema; negation/certainty; multi-entity families | Audited field-family sets (diagnosis, seizure type, medication, …) |

Experiments were run in two **parallel tracks** that share loaders and scorers but differ in model and promotion policy: **hosted GPT 4.1-mini** (fast iteration) and **local Qwen3.6:35b via Ollama** (privacy-relevant deployment path). Cross-track comparisons are reported separately; they are not treated as a single randomized model study.

All model-backed work was preceded by a **deterministic foundation milestone** (loaders, gold-source policies, normalizers, split metadata, scorers, run artifacts) so that metric changes could not arise from silent label reinterpretation (`docs/policies/deterministic_foundation_decisions.md`, `docs/policies/deterministic_scorer_semantics.md`).

### Data splits and sample sizes

- **Gan:** split `gan_2026_fixed_v1`. Full-validation headline results use the **validation** partition (**N = 299** scored records in promoted full runs). Capped diagnostics use **N = 25**, **5**, or **3** as noted per config. A **14-record regression slice** (`data/fixtures/gan_s0_qwen_error_regression_slice.json`) replays known failure modes from full-validation error analysis.
- **ExECT:** train/dev/test metadata from `data/splits`. **Full-validation** ExECT runs use **N = 40** validation letters unless stated otherwise. **Cap-25** diagnostics use **N = 25**. S0/S1 **test holdout** uses **N = 40** test letters (one-shot, frozen policy). Label-policy regression slice: **N = 37**.

These splits are **repo synthetic evaluations**, not the published Gan Real(300) clinician-annotated set or full ExECTv2 Table 1 reproduction (`docs/policies/published_benchmark_metrics.md`).

### Gold labels and normalization

**Gan.** Primary gold is `check__Seizure Frequency Number.seizure_frequency_number[0]`. Secondary `reference[0]` is retained for audit and difficulty flags only. Labels are normalized to **seizures per month**; Purist and Pragmatic category labels are derived deterministically from monthly frequency. Distinct abstention semantics: `unknown` versus `no seizure frequency reference` (`docs/datasets/gan/gan_2026_label_audit.md`).

**ExECT.** JSON entity files are the primary gold for benchmark-facing field families. Diagnosis scoring includes affirmed entities with certainty ≥ 4; medication scoring uses annotated prescriptions and **excludes** planned/current temporality from benchmark-facing metrics until reliable temporality gold exists. S2–S4 extend the family set with versioned scorers (`exect_s2_field_family_deterministic_v1` through `exect_s4_field_family_deterministic_v1`; S4 policy in `docs/experiments/exect/exect_s4_gold_policy.md`).

### Evaluation metrics

**Gan (`gan_frequency_deterministic_v1`).**

| Metric | Role |
| --- | --- |
| Monthly-frequency accuracy | Primary benchmark-facing label match after normalization |
| Purist / Pragmatic category accuracy | Benchmark-facing coarse classification |
| Schema-valid prediction rate | Structural contract compliance |
| Evidence quote support rate | Diagnostic: predicted quote substring-supported in source letter |
| Normalized-label exact match | Diagnostic format fidelity (stricter than monthly match) |

**ExECT (`exect_*_field_family_deterministic_v1`).**

| Metric | Role |
| --- | --- |
| Per-family precision, recall, F1 | Benchmark-facing entity-set match |
| Micro F1 | Unweighted mean across **scored families at that schema level** |
| Evidence quote support rate | Diagnostic (does not change field-family F1) |

Optimizer metrics (e.g. `synthesis_exact_with_evidence`, GEPA feedback) were kept **separate** from benchmark scorers. Post-hoc deterministic surface replay (quoted `"unknown"`, denominator ranges) was evaluated as a **bounded** postprocessor, not as model improvement.

### DSPy programs and experimental factors

Programs are versioned modules with Pydantic-validated structured outputs (`src/clinical_extraction/programs/`). Key **program variants** manipulated one factor at a time unless testing an architecture interaction:

| Variant | Dataset | Description |
| --- | --- | --- |
| Direct single-pass | Gan | One LLM call → frequency label + evidence |
| Synthesis + `BootstrapFewShot` | Gan | Chain-of-thought extraction; optimizer on train split |
| Verify-repair | Gan | Extract → verify evidence → conditional repair |
| Temporal-candidates verify-repair v1.1 | Gan | Deterministic temporal candidate hints + confirm-first verifier |
| Monolithic field-family single-pass | ExECT | One call per note for all active families at schema level |
| Section-aware field-family | ExECT | Per-family calls on deterministic section snippets (ablation) |
| Label-policy versions (v4.x, v1.x) | ExECT | Prompt guidance + deterministic bridges (no scorer change) |

**DSPy optimizers** (`BootstrapFewShot`, `LabeledFewShot`, `BootstrapRS`, `GEPA`) were wired only for **Gan** in `scripts/run_experiment.py`. ExECT improvements used **manual label-policy iteration** and deterministic bridges.

**Factors held fixed** within a comparison row: dataset, split, scorer mode, schema level, and (for replication) frozen prompt version and program variant.

**Factors varied across study phases:** model/provider, program architecture, optimizer presence, output guardrails (local Qwen), and schema breadth (ExECT S1→S4 ladder).

### Models and runtime

| Model | Config path | Use |
| --- | --- | --- |
| GPT 4.1-mini | `configs/models/gpt4_1_mini.yaml` | Hosted primary for Gan optimization and ExECT ladder |
| Gemini 3.1 Flash Lite | `configs/models/gemini31_flash_lite.yaml` | Hosted Gan comparison |
| Qwen3.6:35b | `configs/models/gan_s0_qwen35b_ollama.json`, `exect_qwen35b_ollama.json` | Local Gan + ExECT replication |
| Qwen3.5:9b | `configs/models/gan_s0_qwen9b_ollama.json` | Latency / feasibility probes only |

Local Qwen used LiteLLM `ollama_chat/` with reasoning disabled. ExECT Qwen configs raised `max_tokens` and `num_ctx` versus Gan direct defaults. Per `docs/policies/qwen_dspy_latency_policy.md`, **ChainOfThought + BootstrapFewShot on Qwen3.6:35b** was excluded from routine evaluation after truncation and latency failures.

### Procedure

1. **Infrastructure smokes** (1–3 records per provider/program): validate JSON schema, scorer execution, artifact layout.
2. **Capped diagnostics** (3–25 records): compare variants before full split cost.
3. **Full validation** (Gan N=299; ExECT N=40): headline metrics for promotion decisions.
4. **Error analysis** on stored predictions (`scripts/analyze_gan_frequency_run.py`, inspection markdown per run).
5. **Pre-registered promotion gates** for Gan temporal port (monthly within 1 pp of prior anchor, evidence ≥ prior anchor, schema ≥ 99%; `docs/experiments/gan/gan_s0_gpt4_1_mini_temporal_candidates_full_validation_decision_20260520.md`).

Each run wrote `config.json`, `metadata.json`, `predictions.json`, `metrics.json`, `errors.json`, and `prompts.json` under `runs/<experiment_id>_<timestamp>/`.

### Analysis

Primary results are **point estimates** from deterministic scorers over stored predictions. Bootstrap confidence intervals were computed for selected Gan full-validation comparisons (hosted temporal vs verify-repair v2); overlapping CIs on monthly accuracy were interpreted as **tie**, not proven superiority. Stratified tables used gold-derived `gold_pragmatic` and `hard_case` flags from the loader.

---

## Results

### R1 — Gan S0: full-validation anchors (synthetic validation, N = 299)

Table 1 summarizes promoted and reference **full-validation** runs on the same split and scorer. Verify-repair and temporal programs incur **two model calls per record**; direct and synthesis paths differ in call count and should not be compared on latency alone.

**Table 1. Gan S0 full-validation benchmark-facing metrics (GPT 4.1-mini and Qwen3.6:35b).**

| System | Run ID (suffix) | Monthly acc. | Purist acc. | Pragmatic acc. | Schema valid | Evidence support |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Synthesis + bootstrap (CoT) | `…065115Z` | 62.9% | 70.1% | 73.9% | 97.3% | 89.9% |
| Verify-repair v2 | `…084732Z` | 65.4% | 72.7% | 79.2% | 96.7% | 92.7% |
| **Temporal-candidates v1.1 (hosted, promoted)** | `…130933Z` | **65.1%** | **76.5%** | **84.2%** | **99.7%** | **100.0%** |
| **Temporal-candidates v1.1 (local, Tier 1)** | `…230324Z` | **65.8%** | **75.5%** | **82.6%** | **99.7%** | **100.0%** |
| Direct + guardrails (local) | `…102249Z` | 55.9% | 62.0% | 70.5% | — | 99.6% |
| Direct, no guardrails (local) | `…035636Z` | 55.6% | 61.7% | 69.2% | 89.0% | 94.0% |

Hosted temporal-candidates **met promotion gates** versus verify-repair v2: monthly −0.3 percentage points (within 1 pp), evidence +7.3 pp, Purist +3.8 pp, Pragmatic +5.0 pp, schema +3.0 pp. Monthly bootstrap CIs overlapped verify-repair v2; we treat monthly accuracy as **equivalent**, with category and evidence gains driving adoption.

**Stratified residual (both promoted full runs):** among records with `gold_pragmatic = infrequent` (51 valid records in hosted temporal full analysis), monthly accuracy remained **43.1%** (hosted) to **51.0%** (local reference), versus **62.9%** on `frequent` and **98.2%** on `no_seizure_information`. This bucket dominated remaining errors after promotion.

### R2 — Gan S0: architecture and optimizer comparisons (selected)

**Verify-repair (cap-25, N = 25):** v1 raised monthly accuracy by **+4.3 pp** versus direct; v2 matched v1 on monthly/Purist but avoided exact-label regression versus direct (26.1% exact on cap). Full-validation v2 reached 65.4% monthly (`…084732Z`).

**Sectioning and optimizers:** Few-shot ladder and GEPA cap-5 runs did not exceed synthesis full-validation monthly accuracy; GEPA improved schema/evidence on small caps but introduced **prompt bloat** and unstable canonical labels on Qwen. **Deterministic surface replay** on synthesis full predictions changed **three** records and did not materially move benchmark-facing metrics—remaining errors required semantic repair.

**Output-budget ablation (local Qwen direct):** increasing `max_tokens` from 256 to 1024 did not improve monthly, Purist, Pragmatic, or schema-valid rates; mean latency increased (~6.6 s → ~10.0 s per record).

**Temporal engineering slice (N = 14):** after expanding `temporal_candidates.py` and adding a model event-table guard, the regression slice reached **14/14** valid predictions with **100%** monthly accuracy on Qwen (`…235058Z`); hosted full validation on the same 14-record fixture remained weaker (8/14 monthly), indicating slice overfitting risk was monitored but did not block hosted promotion given full-split gates.

### R3 — ExECT S0/S1: monolithic three-family extraction (GPT 4.1-mini)

**Table 2. ExECT S0/S1 field-family F1 (validation and test).**

| Condition | N | Micro F1 | Diagnosis F1 | Seizure-type F1 | Medication F1 | Evidence support |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Monolithic baseline (cap-25, early policy) | 25 | 73.7% | 60.5% | 65.8% | 92.1% | 92.1% |
| Section-aware ablation (cap-25) | 25 | 65.6% | 44.9% | 59.7% | 88.9% | 75.5% |
| **Label policy v4.10 (val, frozen)** | 40 | **92.3%** | **93.8%** | **90.5%** | **92.8%** | — |
| Label policy v4.10 (cap-25) | 25 | 95.8% | — | — | — | — |
| Label policy v4.10 (test holdout) | 40 | 77.8% | 71.4% | 66.0% | 92.7% | — |

The section-aware ablation **reduced** micro F1 by 8.1 pp on cap-25, with the largest diagnosis drop (−15.6 pp F1) and evidence support drop (−16.6 pp). Iterative label-policy engineering on the monolithic program yielded the frozen v4.10 validation anchor; cap-25 overestimated full-validation micro F1 by ~3.5 pp. Test holdout micro F1 was **77.8%**, a **−14.5 pp** gap versus validation.

Verify-repair and diagnosis-recall add-only variants on cap-25 did not outperform v4.10; the S0/S1 track was **frozen** with no further validation tuning.

### R4 — ExECT schema ladder: breadth cost (GPT 4.1-mini, N = 40 validation)

**Table 3. ExECT full-validation micro F1 by schema level (families scored at each level).**

| Level | Families scored | Frozen run (suffix) | Micro F1 | Notable per-family F1 |
| --- | ---: | --- | ---: | --- |
| S0/S1 | 3 | `…221944Z` | 92.3% | Diagnosis 93.8%; seizure 90.5%; medication 92.8% |
| S2 | 5 | `…231223Z` | 80.9% | Comorbidity 69.3%; investigation 90.0%; seizure 71.0% |
| S3 | 9 | `…235439Z` | 72.1% | Investigation 93.1%; comorbidity 59.8%; seizure 78.1% |
| S4 | 11 | `…071248Z` | 65.5% | Investigation 96.7%; **seizure frequency 45.7%**; medication 71.3% |

Micro F1 **decreases as field families are added**; values across rows are **not** directly comparable as a single learning curve because the scorer aggregates different family sets. S3 v1.0 showed **investigation collapse** (10.3% F1) before label-policy v1.1–v1.2 recovery. S4 v1.1–v1.2 raised seizure-frequency F1 from **25.6%** to **45.7%**; medication temporality F1 stabilized near **62–67%**. Comorbidity F1 fell from **69.3%** (S2) to **59.8%** (S3) and **57.1%** (S4 v1.0 vs S3)—an **accepted gap** at S3/S4 freeze.

### R5 — Local Qwen replication of frozen ExECT prompts (N = 40 validation)

**Table 4. ExECT full-validation micro F1: GPT frozen anchor vs Qwen3.6:35b (same prompt version).**

| Level | GPT micro F1 | Qwen micro F1 | Δ (Qwen − GPT) | Qwen run (suffix) |
| --- | ---: | ---: | ---: | --- |
| S0/S1 (3 fam) | 92.3% | 79.0% | −13.3 pp | `…042117Z` |
| S2 (5 fam) | 80.9% | 82.6% | +1.7 pp | `…073552Z` |
| S3 (9 fam) | 72.1% | 72.2% | +0.1 pp | `…092244Z` |
| S4 (11 fam) | 65.5% | *pending* | — | — |

On S0/S1, Qwen **matched or exceeded** GPT diagnosis F1 (95.1% vs 93.8%) but **underperformed on seizure-type F1** (55.7% vs 90.5%), explaining most of the micro F1 gap. S2 and S3 Qwen replication tracked GPT within **~2 pp** at the micro average. S4 Qwen cap-25/full was in progress when this document was drafted (`docs/experiments/exect/exect_qwen35b_ladder_replication_plan.md`).

### R6 — Negative and inconclusive findings (summary)

| Hypothesis | Outcome |
| --- | --- |
| Section-aware ExECT extraction improves S0/S1 | **Rejected** on cap-25 (F1 and evidence down) |
| GEPA replaces manual Gan guidance at scale | **Not supported** (instability, bloat; cap-5 only) |
| Larger Qwen output budget fixes Gan labels | **Not supported** on full validation |
| Deterministic post-repair fixes remaining Gan errors | **Bounded** to surface forms (3/299 records) |
| BootstrapFewShot on local Qwen for routine Gan | **Deprioritized** (latency, truncation) |
| Cap-25 Gan monthly predicts full-validation monthly | **Unreliable** (44% cap vs ~65% full for temporal path) |

---

## Limitations

1. **External validity:** Results are on **synthetic** letter subsets with repo-defined splits. They do not reproduce Gan Real(300) micro-F1 (~0.78 Purist / ~0.85 Pragmatic in published tables) or ExECT full CUI-aware Table 1 metrics.
2. **Comparability:** ExECT micro F1 across S1–S4 aggregates **different numbers of families**; cross-level trends describe breadth cost, not a single calibrated score.
3. **Sample size:** ExECT full validation (N = 40) and Gan caps (N ≤ 25) have wide uncertainty; cap-25 Gan runs were explicitly non-predictive of full monthly accuracy for temporal-candidates.
4. **Confounds:** Verify-repair and temporal programs change **call count and latency**; evidence support is partly enforced by program policy, not an independent human audit.
5. **Optimizer generalization:** Gan synthesis bootstrap used optimizer metrics on train data; test-split leakage controls follow config definitions but compiled prompts were not evaluated on published external benchmarks.
6. **Incomplete replication:** ExECT Qwen S4 and Gan ReAct bounded probe were scheduled but not complete at document date.

---

## Brief discussion (interpretive)

The experiment program supports three empirical conclusions that are robust under the repo’s scorer contracts:

1. **Narrow-task gains** on Gan came from **architecture and deterministic temporal scaffolding** (temporal-candidates verify-repair), not from larger completion budgets or GEPA instruction search at scale.
2. **Broad-task gains** on ExECT came from **monolithic label-policy engineering** and careful gold-policy alignment, not from section splitting or optimizer compilation on the audited S0/S1 view.
3. **Local Qwen3.6:35b** reaches **parity with hosted GPT on Gan** under the promoted temporal program, but **lags on ExECT seizure-type granularity** at S0/S1 while tracking GPT on S2–S3 micro F1.

The dominant remaining Gan error mode—**infrequent quantified frequencies**—is stable across hosted and local promoted systems, motivating bounded tool-use probes without reopening scorer semantics.

---

*For chronological narrative, promotion decisions, and run inventory, see [`experiments_narrative_report_20260520.md`](experiments_narrative_report_20260520.md).*
