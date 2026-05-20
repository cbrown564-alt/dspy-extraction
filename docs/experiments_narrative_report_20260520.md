# Experiments Conducted to Date — Full Narrative Report

Date: 2026-05-20  
Status: Living synthesis through 2026-05-20 evening (hosted Gan temporal promote; ExECT Qwen S4 in flight)  
Primary sources: `runs/` artifacts (161 runs with `metrics.json` as of this report), `configs/experiments/` (93 configs), frozen-thread history, inspection docs, and `docs/research_status_recap_20260519.md`.

**Paper-style extract:** [`experiments_methods_results_20260520.md`](experiments_methods_results_20260520.md) — Methods, Results (Tables 1–4), Limitations, brief discussion.

---

## Executive Summary

This project is building a **hybrid deterministic + DSPy clinical extraction system** on two benchmark datasets: **ExECTv2** (broad hierarchical epilepsy schema, 200 letters) and **Gan 2026** (seizure-frequency extraction with evidence, 1,500 letters). Research began with a **deterministic foundation**—loaders, gold-label policies, normalizers, scorers, splits, and run tracking—so that later model experiments could not silently change benchmark semantics.

Model-backed work started in mid-May 2026 on two parallel tracks:

| Track | Dataset focus | Primary model(s) | Current default program |
| --- | --- | --- | --- |
| **Hosted (fast iteration)** | Gan S0 + ExECT S1–S4 ladder | GPT 4.1-mini | Gan: temporal-candidates verify-repair v1.1; ExECT: frozen label-policy ladder |
| **Local (privacy / hospital path)** | Gan S0 + ExECT replication | Qwen3.6:35b via Ollama | Gan: temporal-candidates verify-repair v1.1 (Tier 1); ExECT: frozen GPT prompts, no re-tuning |

**Headline outcomes as of 2026-05-20:**

- **Gan (299-record synthetic validation split):** The best full-validation runs cluster around **~65% monthly-frequency accuracy**, **~76% Purist**, **~83–84% Pragmatic**, with **near-perfect schema validity and evidence support** on the promoted temporal-candidates path. This ties or slightly beats earlier verify-repair and synthesis-bootstrap references while improving evidence and category metrics.
- **ExECT (40-record validation split for full runs):** Hosted GPT **S0/S1 monolithic label policy v4.10** reached **92.3% micro F1** on three audited field families. A **schema ladder** through S2 (5 families), S3 (9 families), and S4 (11 families) documents predictable breadth cost: S4 full micro F1 **65.5%** with seizure-frequency and rare-family weaknesses accepted at freeze.
- **Local Qwen:** Viable for direct and verify-repair Gan extraction; **temporal-candidates v1.1** is the local default. ExECT Qwen replication shows **strong diagnosis, weaker seizure-type** vs GPT on the same frozen prompts; S4 replication was the remaining gate when this report was drafted.
- **Negative results that shaped the roadmap:** ExECT section-aware extraction regressed vs monolithic; GEPA and large-output budgets did not beat compact manual guidance on Gan; deterministic post-repair only fixes surface forms; BootstrapFewShot/CoT on local Qwen is deprioritized for latency and truncation risk.

Nothing in this report claims **published benchmark reproduction** on Gan Real(300) or full ExECTv2 CUI-aware Table 1 metrics. All comparisons use repo splits, deterministic scorers, and documented caveats (`docs/published_benchmark_metrics.md`).

---

## Research Questions the Experiment Program Serves

From `docs/outline.md`, the experiment system exists to answer:

1. Can a modular DSPy pipeline beat ExECTv2 and Gan paper benchmarks under fair scorer alignment?
2. How do verification, evidence requirements, sectioning, few-shot optimization, and repair interact with task difficulty?
3. Can **local Qwen3.6:35b** handle the hardest semantic work, or do some subtasks require hosted models?
4. Where should improvement come from—**optimizers (GEPA, BootstrapFewShot)** vs **manual label-policy engineering** vs **program architecture** (verify-repair, temporal tools, ReAct)?

The empirical program has weighted questions 3–4 heavily on Gan (narrow, instrumented) and question 2 on ExECT (broad, label-policy-heavy), while keeping question 1 blocked on scorer breadth and real-letter datasets.

---

## Phase 0 — Deterministic Foundation (Pre-Model)

**Period:** Through ~2026-05-17  
**Artifacts:** `docs/deterministic_foundation_decisions.md`, `docs/deterministic_scorer_semantics.md`, dataset audits, loader/scorer tests.

Before any LLM calls, the project implemented:

- **ExECTv2** and **Gan 2026** loaders with audit-guided gold-source policies (`docs/exect_gold_label_audit.md`, `docs/gan_2026_label_audit.md`).
- **Deterministic scorers:** `exect_field_family_deterministic_v1` (partial S0/S1 field families only), `gan_frequency_deterministic_v1` (monthly frequency, Purist/Pragmatic categories, normalized-label exact match, evidence diagnostics).
- **Split metadata** (`gan_2026_fixed_v1`, ExECT train/dev/test from `data/splits`).
- **Run artifact layout:** `config.json`, `metadata.json`, `predictions.json`, `metrics.json`, `errors.json`, `prompts.json`.

**Why it matters:** Every later experiment reports benchmark-facing metrics through these scorers. Gan uses `seizure_frequency_number[0]` as primary gold; `unknown` vs `no seizure frequency reference` are distinct. ExECT medication scoring excludes planned/current temporality until gold exists. Comparisons across models are only meaningful when scorer mode and split are held fixed.

---

## Phase 1 — Infrastructure and Model Smoke Tests

**Period:** ~2026-05-17–18  
**Goal:** Prove the experiment runner, adapters, and structured-output path per provider.

Representative runs (contract validation, not performance estimates):

| Run ID | Model | Purpose |
| --- | --- | --- |
| `gan_s0_smoke_gpt4_1_mini_token_usage_smoke_20260519T000000Z` | GPT 4.1-mini | Token/residency plumbing |
| `gan_s0_smoke_gemini3_flash_20260518T134109Z` | Gemini 3 Flash | Provider adapter |
| `gan_s0_smoke_gemini31_flash_lite_20260519T101222Z` | Gemini 3.1 Flash Lite | Lite model path |
| `gan_s0_smoke_qwen9b_ollama_20260518T131957Z` | Qwen3.5:9b | Local Ollama gate |
| `gan_s0_smoke_qwen35b_ollama_windows_20260518T202315Z` | Qwen3.6:35b | Windows Ollama + `ollama_chat/` adapter |
| `exect_s0_s1_smoke_gpt4_1_mini_20260518T160445Z` | GPT 4.1-mini | ExECT S0/S1 JSON + scorer contract |

**Finding:** Local Qwen required `ollama_chat/` with thinking disabled; OpenAI-compatible Ollama routes produced empty content and parse failures. Documented in `docs/qwen_local_latency_experiment_20260518.md` and `docs/model_config_smoke_tests.md`.

---

## Phase 2 — Gan S0 Seizure Frequency (Primary Reference Task)

Gan S0 is the project's **tight experimental loop**: one primary label, temporal reasoning, cluster formats, abstention boundaries, and mandatory evidence. Most optimizer configs (22 of 93 experiment configs) and the majority of run directories are Gan runs.

### 2.1 Prior prompt synthesis → BootstrapFewShot (hosted GPT reference arc)

**Hypothesis:** Compact benchmark-contract guidance from prior error analysis beats copying historical prompt bundles.

| Stage | Run | Records | Monthly | Pragmatic | Schema valid | Evidence |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Capped bootstrap | `gan_s0_synthesis_bootstrap_gpt4_1_mini_20260518T062451Z` | 25 | 37.5% | 79.2% | 96.0% | 87.0% |
| **Full validation (historical hosted reference)** | `gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z` | 299 | **62.9%** | **73.9%** | **97.3%** | **89.9%** |

Program: `gan_frequency_s0_synthesis_v1` with `BootstrapFewShot` and optimizer metric `synthesis_exact_with_evidence`. Config: `gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini.json`.

**Interpretation:** Synthesis-backed optimization established that **evidence grounding and label policy can be improved together** on a narrow task when the optimizer metric matches the clinical contract. This remained the strongest **CoT + bootstrap** reference until verify-repair and temporal-candidates paths matured.

**Deterministic post-repair boundary:** Replay `gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_surface_replay_20260518T000000Z` fixed only quoted `"unknown"` and matching-count denominator ranges (+1.0 pp schema validity; negligible benchmark delta). Documented in `docs/gan_s0_post_repair_validation_replay.md` — semantic failures need model-side logic, not scorer-adjacent patching.

### 2.2 Direct extraction and verify-repair (hosted GPT)

**Hypothesis:** Extract → verify evidence → repair improves labels without hiding errors in postprocessing.

| Variant | Cap-25 run | Full run | Monthly (full) | Evidence (full) |
| --- | --- | --- | ---: | ---: |
| Direct | `gan_s0_direct_cap25_gpt4_1_mini_20260519T081439Z` | — | — | — |
| Verify-repair v1 | `gan_s0_verify_repair_cap25_gpt4_1_mini_20260519T081441Z` | — | +4.3 pp monthly on cap vs direct | — |
| **Verify-repair v2 (prior hosted default)** | `gan_s0_verify_repair_cap25_gpt4_1_mini_20260519T084511Z` | `gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z` | **65.4%** | **92.7%** |

v2 cleared promotion gates on cap-25 (no exact-label regression vs direct) but **monthly/Purist gains from v1 did not all persist** — inspect `docs/gan_s0_verify_repair_cap25_v2_inspection_20260519.md`.

### 2.3 Optimizer probes: GEPA, semantic bootstrap, few-shot ladder

**GEPA (GPT and Qwen, cap-5):** Harness runs proved `dspy.GEPA` compiles with reflection LM and pickling fixes. Rich-feedback cap-5 (`gan_s0_gepa_direct_cap5_gpt4_1_mini_20260519T054057Z`) improved schema/evidence but not stable label quality; Qwen GEPA produced prompt bloat and non-canonical labels at high token budgets. Decision: **deprioritize GEPA at scale** — `docs/gan_s0_gepa_vs_synthesis_decision_20260519.md`, `docs/dspy_optimizer_vs_manual_engineering_audit_20260520.md`.

**Few-shot ladder (cap-25, direct path):** Compared zero-shot, labeled few-shot, bootstrap, bootstrap+RS, CoT variants (`gan_s0_ladder_*`, `gan_s0_cot_ladder_*`, 20260519). Best cap-25 monthly among ladder runs ~52% (Gemini direct); ladder did not beat synthesis CoT full validation on the same metric definitions.

**Semantic bootstrap (cap-25):** `gan_s0_semantic_bootstrap_cap25_gpt4_1_mini_20260519T100255Z` — monthly 33.3%; did not beat verify-repair v2 anchor on cap-25.

**Gemini 3.1 Flash Lite:** Strong cap-25 (`gan_s0_direct_cap25_gemini31_flash_lite_20260519T100621Z` monthly 52.2%); full validation monthly 63.9% (`…101710Z`) — competitive hosted alternative, not promoted as default.

### 2.4 Local Qwen — direct path, guardrails, latency policy

**Operational finding:** Direct extraction is the default local path; `ChainOfThought` + `BootstrapFewShot` on Qwen is **13×+ slower** and truncation-prone (`docs/qwen_local_latency_experiment_20260518.md`). Raising `max_tokens` from 256→1024 on direct full validation **did not improve** monthly or category metrics; slowed inference.

| Run | Program | Monthly | Purist | Pragmatic | Schema | Evidence |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Direct full (no guardrails) | `gan_s0_overnight_qwen35b_direct_full_validation_20260519T035636Z` | 55.6% | 61.7% | 69.2% | 89.0% | 94.0% |
| **Direct full + guardrails** | `gan_s0_qwen35b_direct_full_validation_guardrails_20260519T102249Z` | **55.9%** | 62.0% | 70.5% | — | 99.6% |
| Direct cap-25 guardrails v2 | `gan_s0_qwen35b_direct_cap25_guardrails_validation_20260519T154228Z` | 37.5% | — | — | — | 100% |

Guardrails enforced canonical vocabulary, cluster retention, forbidden units/lexicon, and evidence-length limits (`docs/gan_s0_qwen35b_guardrails_cap25_validation_20260519.md`). Invalid-label rate dropped; **semantic temporal errors remained** the dominant failure mode.

### 2.5 Temporal-candidates verify-repair v1.1 (pivot and promotion)

**Hypothesis:** Infrequent quantified rates need **deterministic temporal candidate hints** + confirm-first verifier guards, not more output tokens or GEPA instruction bloat. Pivot doc: `docs/gan_s0_temporal_candidate_pivot_20260519.md`.

Program: `gan_frequency_s0_temporal_candidates_verify_repair_v1_1`.

| Stage | Local Qwen run | Monthly | Purist | Pragmatic | Schema | Evidence |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Regression slice (14) | `…180329Z` | 100% | 100% | 100% | 100% | 100% |
| Cap-25 | `…183213Z` | 44% | 64% | 84% | 100% | 100% |
| **Full validation — Tier 1 local default** | `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T230324Z` | **65.8%** | **75.5%** | **82.6%** | **99.7%** | **100%** |

**Hosted port (Option A, 2026-05-20):**

| Stage | Run | Monthly | Purist | Pragmatic | Schema | Evidence | Decision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Cap-25 hold (pre-bridge) | `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_cap25_guardrails_validation_20260520T125302Z` | 44% | 64% | 72% | 100% | 84% | Hold |
| Cap-25 promote | `…130724Z` | 44% | 64% | 72% | 100% | 100% | Launch full |
| **Full — hosted default** | `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z` | **65.1%** | **76.5%** | **84.2%** | **99.7%** | **100%** | **Promote** |

Promotion packet: `docs/gan_s0_gpt4_1_mini_temporal_candidates_full_validation_decision_20260520.md`. Monthly **ties** verify-repair v2 (−0.3 pp, within 1 pp gate); evidence **+7.3 pp**, Purist **+3.8 pp**, Pragmatic **+5.0 pp**.

**Residual failure bucket (both local and hosted full):** `gold_pragmatic=infrequent` monthly ~43–51% on ~51 records — same stratified pattern on Qwen and GPT full runs.

**Post–Tier-1 engineering on slice (14 records):**

| Step | Run | Outcome |
| --- | --- | --- |
| B1 expand `temporal_candidates.py` | `…232514Z` | 14/14; gold-in-candidates 10/14 |
| B2 model event table | `…235058Z` | 14/14; rescue guard for `gan_14881` |

**Pending:** Bounded ReAct temporal-tools probe on regression slice (`gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails.json`) — scheduled after ExECT Qwen S4 full inspection to avoid Ollama contention.

### 2.6 Gan experiments not promoted (summary)

| Family | Representative configs/runs | Outcome |
| --- | --- | --- |
| Qwen9b overnight / max-budget | `gan_s0_overnight_qwen9b_*`, `gan_s0_maxbudget_*` | Exploratory; weaker than 35b |
| Labeled few-shot + verify-repair (Qwen slice) | `gan_s0_qwen35b_labeled_fewshot_verify_repair_*` | ~71% monthly on 14-record slice; below temporal v1.1 |
| ReAct temporal tools (partial) | `gan_s0_qwen35b_react_temporal_tools_*` | Killed/contended; not complete |
| Temporal event table alone | `…235058Z` | Slice helper; not standalone full-validation program |
| Semantic GEPA / semantic bootstrap cap-25 | `gan_s0_semantic_gepa_*`, `gan_s0_semantic_bootstrap_*` | No promotion |

---

## Phase 3 — ExECT S0/S1 Monolithic Baseline (Hosted GPT)

**Scope:** Audited **diagnosis**, **seizure type**, **annotated medication** only — not full ExECTv2 paper reproduction.

### 3.1 Early baseline and section-aware negative result

| Run | Program | Cap | Micro F1 | Diagnosis F1 | Seizure F1 | Med F1 | Evidence |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Monolithic v1 | `exect_s0_s1_field_family_single_pass` | 25 | **73.7%** | 60.5% | 65.8% | 92.1% | 92.1% |
| Section-aware | `exect_s0_s1_section_aware_field_family` | 25 | 65.6% | 44.9% | 59.7% | 88.9% | 75.5% |

Runs: `exect_s0_s1_validation_cap25_gpt4_1_mini_20260518T172431Z` vs `exect_s0_s1_section_aware_cap25_gpt4_1_mini_20260518T174714Z`. Design: `docs/exect_section_aware_ablation_design.md`; inspection: `docs/exect_section_aware_cap25_inspection.md`.

**Finding:** Simple section selection + thin family prompts **hurt** diagnosis and evidence (synthetic heading-shaped quotes). Monolithic baseline remains the architecture anchor unless a stronger hypothesis addresses this failure mode.

### 3.2 Label-policy ladder v4.2 → v4.10 (frozen)

Iterative prompt-policy and deterministic bridge work (medication scope, diagnosis vocabulary alignment, fused seizure-type bridge, evidence diagnostics). Closed negative paths: verify-repair cap-25, diagnosis-recall add-only probe.

| Stage | Run | Split | Micro F1 | Notes |
| --- | --- | --- | ---: | --- |
| Full validation **frozen dev anchor** | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` | 40 val | **92.3%** | v4.10 label policy |
| Cap-25 | `…221936Z` | 25 | 95.8% | Optimistic vs full (~+3.5 pp) |
| **Test holdout (one-shot)** | `exect_s0_s1_validation_test_gpt4_1_mini_20260519T222615Z` | 40 test | **77.8%** | Generalization gap |
| Regression slice | `exect_s0_s1_label_policy_regression_slice_*` (37 records) | safety replay | — | Multiple iterations |

**Status:** Thread B **frozen** — no further v4.x validation tuning (`docs/kanban_frozen_threads_history.md`). Configs: `exect_s0_s1_validation_full_gpt4_1_mini.json`, regression slice, test holdout.

### 3.3 ExECT S0/S1 — local Qwen replication

| Run | Micro F1 | Diagnosis | Seizure | Medication | vs GPT full |
| --- | ---: | ---: | ---: | ---: | --- |
| `exect_s0_s1_validation_full_qwen35b_ollama_20260520T042117Z` | **79.0%** | 95.1% | **55.7%** | 89.1% | −13.3 pp micro |

**Finding:** Qwen matches or exceeds GPT on diagnosis but **seizure-type granularity collapses** on the same frozen prompt. Test holdout deferred until failure modes documented. Plan: `docs/exect_qwen35b_ladder_replication_plan.md`.

---

## Phase 4 — ExECT Schema Ladder S2 → S4 (Hosted GPT, Frozen)

**Design:** Expand field families monotonically with versioned label policies and scorers — `docs/exect_s2_s4_schema_ladder_design.md`.

### 4.1 S2 — five families (v1.3 frozen)

Program: `exect_s2_field_family_single_pass`; scorer: `exect_s2_field_family_deterministic_v1`.  
Prompt: `exect_s2_field_family_v1_3_label_policy`.

| Stage | Run | Micro F1 (5 fam) | Notable |
| --- | --- | ---: | --- |
| Cap-25 v1 (baseline) | `…224038Z` | 66.4% | Seizure 40.0% — multi-family regression |
| Cap-25 v1.1 | `…225159Z` | 79.7% | Seizure recovered to 80.6% |
| **Full v1.3 frozen** | `exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` | **80.9%** | Comorbidity 69.3%; jerk FP 0 |

### 4.2 S3 — nine families (v1.2 frozen)

Program: `exect_s3_field_family_single_pass`; prompt v1.2.

| Stage | Run | Micro F1 (9 fam) | Notable |
| --- | --- | ---: | --- |
| Full v1.0 | `…233810Z` | — | Investigation collapse (10.3% F1) |
| Full v1.1 | `…234907Z` | — | Investigation fixed; seizure weak |
| **Full v1.2 frozen** | `exect_s3_validation_full_gpt4_1_mini_20260519T235439Z` | **72.1%** | Comorbidity 59.8% (**accepted gap** vs S2 69.3%) |

### 4.3 S4 — eleven families (v1.2 frozen)

Scorer: `exect_s4_field_family_deterministic_v1`; gold policy: `docs/exect_s4_gold_policy.md`.

| Version | Full run | Micro F1 (11 fam) | Seizure freq F1 | Investigation F1 | Rx temporality |
| --- | --- | ---: | ---: | ---: | ---: |
| v1.0 | `…001602Z` | 63.4% | 25.6% | — | 65.2% |
| v1.1 | `…064751Z` | 65.6% | 45.2% | — | 67.2% |
| **v1.2 frozen** | `exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` | **65.5%** | **45.7%** | **96.7%** | 62.5% |

**Accepted limitations at freeze:** Seizure-frequency F1 remains weak; comorbidity and medication gaps vs narrower levels documented; onset/when-diagnosed/birth-history families noisy at low gold counts.

### 4.4 ExECT S2–S4 — local Qwen replication (in progress)

| Level | GPT frozen anchor | Qwen full run | Qwen micro F1 | Delta vs GPT |
| --- | --- | --- | ---: | ---: |
| S2 | `…231223Z` 80.9% | `exect_s2_validation_full_qwen35b_ollama_20260520T073552Z` | **82.6%** | +1.7 pp |
| S3 | `…235439Z` 72.1% | `exect_s3_validation_full_qwen35b_ollama_20260520T092244Z` | **72.2%** | +0.1 pp |
| S4 | `…071248Z` 65.5% | cap-25/full **pending** at report time | — | — |

Inspection: `docs/exect_s3_validation_full_qwen35b_ollama_inspection_20260520.md`. S3 cap-25 final run used DSPy disk-cache replay after background shell stalls — metrics valid, latency non-authoritative.

---

## Cross-Cutting Themes

### Optimizers vs manual engineering

`docs/dspy_optimizer_vs_manual_engineering_audit_20260520.md` concludes:

- **DSPy programs and artifact discipline:** strong.
- **Compile-time optimization on ExECT:** never implemented (runner gate: optimizers Gan-only).
- **Gan optimizers:** explored; **synthesis bootstrap** and **temporal-candidates architecture** beat GEPA/ladder probes for stable benchmark-facing outcomes.
- **ExECT gains:** overwhelmingly **manual label-policy versions + deterministic bridges**, not teleprompter search.

### Evidence metrics

Evidence quote support is **diagnostic** unless explicitly part of an optimizer metric. Verify-repair and temporal paths double model calls; latency comparisons must hold program variant constant.

### Published benchmark distance

| Dataset | Repo status | Published anchor (indicative) |
| --- | --- | --- |
| Gan Real(300) Purist micro-F1 | Not run | ~0.776–0.788 (Qwen2.5-14B CoT) |
| Gan Real(300) Pragmatic micro-F1 | Not run | ~0.832–0.847 |
| ExECT All per-letter F1 | Partial S0/S1 families only | 0.90 paper; repo ~0.92 micro F1 on 3 families / 40 val |

---

## Current Defaults and Frozen Anchors (2026-05-20)

| Role | Dataset | Model track | Run / program |
| --- | --- | --- | --- |
| **Default hosted Gan S0** | Gan | GPT 4.1-mini | `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z` |
| **Default local Gan S0** | Gan | Qwen3.6:35b | `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T230324Z` |
| Prior hosted Gan reference | Gan | GPT | `gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z` |
| Historical synthesis reference | Gan | GPT CoT+bootstrap | `gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z` |
| **Frozen ExECT S0/S1** | ExECT | GPT | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` (v4.10) |
| **Frozen ExECT S2/S3/S4** | ExECT | GPT | `…231223Z` / `…235439Z` / `…071248Z` |
| ExECT Qwen S1 full | ExECT | Qwen | `…042117Z` |

---

## Experiment Inventory Statistics

| Category | Count (approx.) |
| --- | ---: |
| Run directories under `runs/` | ~170 |
| Runs with `metrics.json` | 161 |
| Experiment configs | 93 |
| Configs with DSPy optimizer blocks | 22 (all Gan) |
| Inspection / decision markdown docs in `docs/` | 50+ experiment-tagged |

---

## Open Questions and Scheduled Work

1. **Gan ReAct bounded probe** — Does tool-assisted temporal reasoning beat B2 event-table on the 14-record slice without evidence regression? Exit criteria in `docs/kanban_plan.md`.
2. **ExECT Qwen S4 full** — Does local Qwen preserve GPT's seizure-frequency weakness at 11 families?
3. **ExECT test holdout on Qwen** — Deferred until S1 failure modes documented (−13.3 pp vs GPT on val).
4. **Benchmark reproduction infra** — CUI-aware full ExECT scorer; Gan Real(300) loader — blocked on design and data access.
5. **Infrequent Gan bucket** — ~43–51% monthly on `gold_pragmatic=infrequent`; primary residual for both promoted full runs.

---

## How to Reproduce or Extend This Report

```powershell
# List runs with metrics
Get-ChildItem runs -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'metrics.json') }

# Gan full-run analyzer (example)
uv run python scripts/analyze_gan_frequency_run.py runs/<run_id> `
  --split-name gan_2026_fixed_v1:validation `
  --markdown docs/<your_error_analysis>.md

# ExECT benchmark metrics from a run
$run = "runs/exect_s4_validation_full_gpt4_1_mini_20260520T071248Z"
(Get-Content "$run/metrics.json" | ConvertFrom-Json).benchmark_metrics
```

**Related living docs:** `docs/kanban_plan.md` (active work), `docs/kanban_frozen_threads_history.md` (run tables), `docs/research_status_recap_20260519.md` (narrative through 05-19), `docs/published_benchmark_metrics.md` (alignment caveats).

---

## Metric and Validity Caveats (Read Before Citing Numbers)

1. **Splits:** Gan full-validation numbers use `gan_2026_fixed_v1:validation` (299 records in recent runs), not published Real(300). ExECT full runs use 40-record validation unless noted.
2. **Scorers:** `gan_frequency_deterministic_v1` and `exect_*_field_family_deterministic_v1` — semantics in `docs/deterministic_scorer_semantics.md`.
3. **Capped runs (cap-3, cap-5, cap-25):** Directional only; not comparable to full-validation headline tables without explicit labeling.
4. **Multi-family micro F1:** S2/S3/S4 micro F1 aggregates different field sets — **do not compare S1 92.3% to S4 65.5% as a single trajectory line** without family-scope annotation.
5. **Repair and verify-repair:** Report repair rates and extraction-only metrics when claiming label improvements.
6. **Optimizer prompts:** GEPA and bootstrap compiled states can be large; audit before treating as deployable artifacts.

---

*This report is a standalone synthesis artifact. Update when major promotion decisions, full-validation runs, or benchmark-reproduction milestones land.*
