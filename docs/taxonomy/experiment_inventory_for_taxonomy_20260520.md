# Experiment inventory for taxonomy design

Date: 2026-05-20  
Purpose: Consolidated fact-finding from configs, runs, docs, and program code — input for designing a coherent experiment taxonomy and research pipeline.  
Sources: four exploration passes, `configs/experiments/` (93 configs), local `runs/` (191 dirs, 162 with `metrics.json`, 80 unique `experiment_id`s), `docs/experiments/synthesis/experiments_narrative_report_20260520.md`, frozen-thread history, inspection/decision docs.

**Not a taxonomy yet.** This document inventories what exists. Taxonomy candidates are in §8.

**Validity caveat:** All headline metrics use **repo synthetic splits** and **deterministic scorers** — not Gan Real(300) or full ExECT Table 1 (`docs/policies/published_benchmark_metrics.md`).

---

## 1. Scale and artifacts

| Layer | Count | Location |
| --- | ---: | --- |
| Experiment configs | 93 | `configs/experiments/*.json` |
| Registered program variants | 13 | `src/clinical_extraction/programs/` |
| Model adapter configs | 11 | `configs/models/` |
| Run directories (local) | 191 | `runs/<experiment_id>_<timestamp>/` |
| Runs with `metrics.json` | 162 | same |
| Distinct `experiment_id`s with metrics | 80 | from `config.json` in run dirs |
| Experiment-tagged docs | 50+ | `docs/*experiment*`, `*validation*`, `*inspection*`, `*error_analysis*`, `*decision*` |

**Per-run artifact bundle:** `config.json`, `metadata.json`, `predictions.json`, `metrics.json`, `errors.json`, `prompts.json`, optional `artifacts/compiled_state.json`.

**Entrypoint:** `uv run python scripts/run_experiment.py --experiment <config> --env-file .env`

---

## 2. Program variants (pipeline architecture axis)

| Variant | Dataset / scope | Stages | Configs | Role |
| --- | --- | --- | ---: | --- |
| `gan_frequency_s0_single_pass` | Gan S0 | CoT extract | 19 | Baseline, synthesis, CoT ladder, latency probes |
| `gan_frequency_s0_direct_single_pass` | Gan S0 | Predict extract | 30 | Primary workhorse; optimizers; guardrails |
| `gan_frequency_s0_direct_verify_repair` | Gan S0 | Extract → verify/repair | 6 | Prior hosted default (superseded) |
| `gan_frequency_s0_temporal_candidates_verify_repair` | Gan S0 | Extract → deterministic temporal hints → verify/repair | 5 | **Current default** (hosted + local) |
| `gan_frequency_s0_temporal_event_table_verify_repair` | Gan S0 | + LLM event table | 1 | Slice helper (B2), not promoted standalone |
| `gan_frequency_s0_react_temporal_tools` | Gan S0 | ReAct tools → extract | 1 | Pending slice probe |
| `exect_s0_s1_field_family_single_pass` | ExECT 3 families | CoT monolithic | 9 | **Frozen** v4.10 label policy |
| `exect_s0_s1_field_family_section_aware` | ExECT 3 families | Per-field section extract | 1 | **Rejected** (−8.1 pp micro F1 cap) |
| `exect_s0_s1_field_family_diagnosis_recall` | ExECT 3 families | Extract + add-only recall | 1 | **Abandoned** |
| `exect_s0_s1_field_family_verify_repair` | ExECT 3 families | Extract → verify/repair | 1 | **Closed** (no beat v4.10) |
| `exect_s2_field_family_single_pass` | ExECT 5 families | CoT monolithic | 6 | **Frozen** v1.3 |
| `exect_s3_field_family_single_pass` | ExECT 9 families | CoT monolithic | 6 | **Frozen** v1.2 |
| `exect_s4_field_family_cause_bridge_k0_k1_single_pass` | ExECT 11 families | CoT monolithic + K0+K1 cause bridge | 6 | **Frozen** operational default (GPT) 2026-05-21 |
| `exect_s4_field_family_single_pass` | ExECT 11 families | CoT monolithic (L1 control) | 6 | Grid control alias `EXECT_S4_L1_VARIANT`; historical anchor …071248Z |

**Optimizer support:** Gan only (`BootstrapFewShot`, `LabeledFewShot`, `GEPA`). ExECT configs have no optimizer path in the runner.

---

## 3. Config inventory by research thread

### 3.1 Gan S0 — 63 configs (`gan_2026`, validation N=299 unless capped)

| Family | Configs | Program(s) | Primary question |
| --- | ---: | --- | --- |
| A. Baseline / early | 3 | single_pass | Initial prompt + bootstrap metric |
| B. Provider smokes | 7 | single_pass / direct | Adapter + JSON contract |
| C. Direct + guardrails | 6 | direct | Single-pass vs verify-repair precursor |
| D. Verify-repair v2 | 5 | verify_repair | Two-stage hosted/local |
| E. Temporal candidates v1.1 | 5 | temporal_candidates | **Promoted** architecture |
| F. Temporal ablations (slice) | 2 | event_table, react | Engineering probes on 14-record slice |
| G. Synthesis bootstrap | 2 | single_pass + BFS | Compact guidance + optimizer |
| H. Semantic optimizer | 4 | direct + optimizers | Semantic vs synthesis metric |
| I. Synthesis ladder | 7 | direct / single_pass | Zero-shot → BFS → RS → labeled |
| J. GEPA probes | 2 | direct + GEPA | Optimizer vs manual (cap 5) |
| K. Qwen latency (cap 3) | 5 | direct / single_pass | CoT vs direct, bootstrap |
| L. Max-budget / overnight | 13 | direct / single_pass | Token budget, local throughput |
| M. Qwen labeled-fewshot slices | 2 | direct / verify_repair | Few-shot on error slice |

**Cap ladder pattern (repeated):** smoke (1) → cap25 (25) → full (299) → optional regression slice (14 fixed IDs).

**Regression slice fixture:** `data/fixtures/gan_s0_qwen_error_regression_slice.json`

### 3.2 ExECT — 30 configs (`exect_v2`, validation N=40 full unless capped)

| Level | Families | Configs | Program | Scorer |
| --- | ---: | ---: | --- | --- |
| S0/S1 | 3 | 12 | single_pass (+ section, recall, VR probes) | `exect_field_family_deterministic_v1` |
| S2 | 5 | 6 | single_pass | `exect_s2_field_family_deterministic_v1` |
| S3 | 9 | 6 | single_pass | `exect_s3_field_family_deterministic_v1` |
| S4 | 11 | 6 | single_pass | `exect_s4_field_family_deterministic_v1` |

**Standard 6-config grid per level:** `smoke_gpt4` · `smoke_qwen35b` · `cap25_gpt4` · `cap25_qwen35b` · `full_gpt4` · `full_qwen35b`

**Special configs:** label-policy regression slice (37 IDs), diagnosis-recall slice, section-aware cap25, verify-repair cap25, **test split** (`exect_s0_s1_validation_test_gpt4_1_mini`, `report_on_test_split: true`).

**Regression slice fixture:** `data/fixtures/exect_s0_label_policy_error_regression_slice.json`

---

## 4. Executed studies with outcomes (decision log)

Statuses: **Promote** · **Freeze** · **Hold** · **Reject** · **Iterate** · **Exploratory** · **Pending**

### 4.1 Foundation (no LLM experiments)

| Study | Outcome | Evidence |
| --- | --- | --- |
| Loaders, scorers, splits, audits | **Ship** | `deterministic_foundation_decisions.md`, dataset audits |

### 4.2 Infrastructure smokes

| Study | Model(s) | Outcome | Evidence |
| --- | --- | --- | --- |
| Gan/ExECT provider smokes | GPT, Gemini, Qwen9b/35b | **Ship** | `model_config_smoke_tests.md`, smoke run IDs |
| Windows Ollama adapter | Qwen35b | **Ship** | `gan_s0_smoke_qwen35b_ollama_windows_*` |

### 4.3 Gan S0 — hosted GPT

| Study | N | Headline metrics | Outcome | Run / doc |
| --- | ---: | --- | --- | --- |
| Synthesis bootstrap full | 299 | Monthly 62.9%, evidence 89.9% | **Reference** (superseded) | `…065115Z` |
| Verify-repair v2 full | 299 | Monthly 65.4%, evidence 92.7% | **Superseded** default | `…084732Z` |
| **Temporal candidates v1.1 full** | 299 | Monthly **65.1%**, Purist 76.5%, evidence **100%** | **Promote** hosted default | `…130933Z`, decision 20260520 |
| Gemini direct/VR full | 299 | Monthly 63.9% direct | **Hold** cost/latency | `…101710Z` |
| GEPA cap-5 | 5 | Monthly 60%, prompt bloat | **Deprioritize** | GEPA decision doc |
| Few-shot / semantic ladder cap25 | 25 | Best ~52% monthly | **Abandon** vs temporal | ladder inspection |
| Deterministic surface replay | 299 | ~3 records changed | **Abandon** post-repair | replay doc |

### 4.4 Gan S0 — local Qwen3.6:35b

| Study | N | Headline metrics | Outcome | Run / doc |
| --- | ---: | --- | --- | --- |
| Direct full (no guardrails) | 299 | Monthly 55.6%, schema 89% | **Iterate** | overnight full runs |
| Direct full + guardrails | 299 | Monthly 55.9%, evidence 99.6% | **Baseline** pre-temporal | `…102249Z` |
| **Temporal candidates v1.1 full** | 299 | Monthly **65.8%**, evidence **100%** | **Promote** local Tier 1 | `…230324Z` |
| Latency CoT+bootstrap cap3 | 3 | Failed (max_tokens) | **Reject** routine use | latency doc |
| max_tokens 81920 | varies | No metric gain | **Reject** | narrative R2 |
| B2 event table slice | 14 | 14/14 monthly on slice | **Helper only** | B2 error analysis |
| ReAct temporal tools slice | 14 | — | **Pending** | config exists; run killed |

### 4.5 ExECT — hosted GPT (label-policy engineering)

| Study | N | Micro F1 | Outcome | Notes |
| --- | ---: | ---: | --- | --- |
| Monolithic cap25 baseline | 25 | 73.7% | **Anchor** | |
| Section-aware cap25 | 25 | 65.6% | **Reject** | −8.1 pp |
| Label-policy v3→v4.10 iterations | slice→40 | 67%→**92.3%** | **Freeze** v4.10 | 12 full runs show progression (`…200017Z`→`…221944Z`) |
| Test holdout v4.10 | 40 test | 77.8% | **Record gap** | no more val tuning |
| Verify-repair cap25 | 25 | — | **Close** | no beat v4.10 |
| Diagnosis-recall slice | slice | — | **Abandon** | |

### 4.6 ExECT — schema ladder (hosted GPT, frozen prompts per level)

| Level | N | Micro F1 | Notable weakness | Outcome | Frozen run |
| --- | ---: | ---: | --- | --- | --- |
| S2 v1.3 | 40 | **80.9%** | Comorbidity 69.3% | **Freeze** | `…231223Z` |
| S3 v1.2 | 40 | **72.1%** | Comorbidity 59.8% | **Freeze** | `…235439Z` |
| S4 v1.2 | 40 | **65.5%** | Seizure freq F1 45.7% | **Freeze** | `…071248Z` |

*Cross-level micro F1 is not a single learning curve — scorer adds families each step.*

### 4.7 ExECT — Qwen3.6:35b replication (frozen GPT prompts, no re-tuning)

| Level | N | Micro F1 vs GPT | Outcome | Run |
| --- | ---: | --- | --- | --- |
| S0/S1 full | 40 | 79.0% vs 92.3% (−13.3 pp) | **Hold** | `…042117Z` |
| S2 full | 40 | 82.6% vs 80.9% (+1.7 pp) | **Done** | `…073552Z` |
| S3 full | 40 | 72.2% vs 72.1% | **Done** | `…092244Z` |
| S4 cap25 | 25 | 72.4% vs 69.2% cap | **Done** | `…133930Z` |
| **S4 full** | 40 | — | **Pending** | config exists; no local metrics yet |

---

## 5. Current defaults (promoted / frozen anchors)

| Role | Dataset | Track | `experiment_id` | Run suffix (local) |
| --- | --- | --- | --- | --- |
| Hosted Gan default | Gan | GPT 4.1-mini | `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails` | `…130933Z` |
| Local Gan default | Gan | Qwen35b Ollama | `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails` | `…230324Z` |
| Frozen ExECT S0/S1 | ExECT | GPT | `exect_s0_s1_validation_full_gpt4_1_mini` | `…221944Z` (v4.10) |
| Frozen ExECT S2/S3/S4 | ExECT | GPT | `exect_s2/s3/s4_validation_full_gpt4_1_mini` | `…231223Z` / `…235439Z` / `…071248Z` |

---

## 6. Config ↔ documentation gaps

**Configs with little or no dedicated inspection/decision doc:**

- `gan_s0_baseline_gpt4_1_mini`, `gan_s0_bootstrap_gpt4_1_mini`, `gan_s0_vocab_guided_gpt4_1_mini`
- `gan_s0_overnight_qwen35b_direct_cap100`, `gan_s0_overnight_qwen9b_*`
- ExECT Qwen cap-only runs (metrics in kanban, no inspection md)
- Intermediate ExECT label-policy versions (v4.2–v4.9): same JSON configs, version in `prompt_version` only

**Docs / plans without completed runs:**

- Published Gan Real(300) / full ExECT Table 1
- `exect_s0_s1_validation_test_qwen35b_ollama` (deferred)
- Gan ReAct slice (partial/killed)
- ExECT S4 Qwen full inspection doc (expected after run)

**Untracked configs (git status):** GPT temporal cap25/full guardrails configs — have decision + error-analysis docs.

---

## 7. Orthogonal dimensions (every experiment row should tag these)

Use these fields when building a taxonomy or experiment registry:

1. **Research program** — Gan frequency S0 · ExECT S0/S1 · ExECT ladder S2–S4 · infrastructure
2. **Dataset** — `gan_2026` · `exect_v2`
3. **Schema scope** — field count / `schema_level` string
4. **Program architecture** — single_pass · direct · verify_repair · temporal_candidates · section_aware · react · …
5. **Improvement mechanism** — none · manual prompt/label-policy · deterministic bridges · DSPy optimizer · temporal tooling
6. **Model track** — hosted GPT · Gemini · local Qwen35b · local Qwen9b probe
7. **Run tier** — smoke · cap25 · full validation · regression slice · test (explicit flag)
8. **Scorer mode** — `gan_frequency_deterministic_v1` · `exect_*_deterministic_v1`
9. **Outcome class** — promote · freeze · hold · reject · exploratory · pending
10. **Evidence type** — contract smoke · diagnostic cap · slice gate · headline full-validation

---

## 8. Taxonomy candidates (for next session — not chosen)

These are **ways to cut** the inventory; each emphasizes different pipeline decisions.

### Option A — Research thread (narrative-first)

```
Foundation → Infrastructure → Gan track → ExECT S0/S1 → ExECT ladder → Qwen replication
```

**Pros:** Matches how work actually progressed and docs are organized.  
**Cons:** Mixes architecture, model, and optimizer in one branch.

### Option B — Two-axis matrix (recommended starting point)

**Axis 1 — Benchmark program:** Gan S0 | ExECT S0/S1 | ExECT S2 | S3 | S4  
**Axis 2 — Study type:**

| Study type | Purpose | Examples |
| --- | --- | --- |
| T0 Contract | Runner/adapters work | smokes |
| T1 Architecture | Pipeline shape | direct vs VR vs temporal |
| T2 Policy | Prompts, label rules, bridges | ExECT v4.x, Gan guardrails |
| T3 Optimization | DSPy compile-time | bootstrap, GEPA, ladder |
| T4 Model | Provider comparison | GPT vs Gemini vs Qwen |
| T5 Scale | Cap vs full vs slice | cap25, full, 14/37-id slices |
| T6 Replication | Same frozen artifact, new model | ExECT Qwen ladder |

**Pros:** Separates *what you changed* from *what you measured*; shapes "one factor at a time" discipline.  
**Cons:** Some runs are legitimately multi-factor (e.g. temporal + guardrails + Qwen).

### Option C — Lifecycle stage (pipeline-shaping)

```
Hypothesis → Config draft → Smoke → Slice gate → Cap diagnostic → Full validation → Freeze/Promote → Error read
```

Map each `experiment_id` to its **highest completed stage**. Taxonomy becomes a **gating pipeline** rather than a topic tree.

**Pros:** Directly shapes research ops (what to run next).  
**Cons:** Same config family appears at multiple stages.

### Option D — Factorial decomposition (analysis-design)

Hold fixed: dataset, split, scorer, schema scope. Tag **single varied factor**:

- FACTOR_MODEL
- FACTOR_PROGRAM
- FACTOR_PROMPT_POLICY
- FACTOR_OPTIMIZER
- FACTOR_CONTEXT (section-aware, full note)
- FACTOR_RUN_SCOPE (N)

**Pros:** Clean comparisons; paper-ready methods section.  
**Cons:** Tedious to tag retrospectively; many runs vary 2+ factors.

### Option E — Outcome ontology (decision-centric)

```
PROMOTED_DEFAULT | FROZEN_REFERENCE | SUPERSEDED | REJECTED | EXPLORATORY | INCOMPLETE
```

**Pros:** Immediately answers "what should we build on?"  
**Cons:** Weak for planning *new* experiments.

---

## 9. Suggested next step (taxonomy workshop)

1. **Pick primary axis** (B + C hybrid is a strong default: benchmark program × study type, with lifecycle stage as metadata).
2. **Build registry table** — one row per `experiment_id` (80 rows), not per config (93) or per run (162): merge reruns, keep best/full-validation run ID.
3. **Tag the 10 dimensions** in §7 for each row.
4. **Mark comparability groups** — which rows share fixed controls and differ on exactly one factor.
5. **Derive pipeline rules** — e.g. "no full validation without slice gate for Gan temporal family."

Existing syntheses to keep as narrative layer:

- `docs/experiments/synthesis/experiments_narrative_report_20260520.md`
- `docs/experiments/synthesis/experiments_methods_results_20260520.md`
- `docs/planning/kanban_frozen_threads_history.md`

---

## 10. Quick reference — config filename patterns

| Pattern | Meaning |
| --- | --- |
| `*_smoke_*` | N=1 or 3, contract |
| `*_cap25_*` / `*_cap3_*` / `*_cap5_*` | Capped validation |
| `*_full_validation_*` / `*_validation_full_*` | Full split |
| `*_regression_slice_*` | Fixed `record_ids` |
| `*_overnight_*` / `*_maxbudget_*` | Local long-run / high token cap |
| `*_ladder_*` | Optimizer comparison ladder |
| `*_guardrails_*` | Gan canonical vocab + evidence policy |
| `*_qwen35b_*` / `*_gpt4_1_mini_*` | Model track (see `model_config_path` for truth) |

---

*Generated for taxonomy design. Update when new configs/runs land or when S4 Qwen full completes.*
