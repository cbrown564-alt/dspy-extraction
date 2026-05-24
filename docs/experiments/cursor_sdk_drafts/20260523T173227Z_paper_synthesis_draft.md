# Paper Narrative Synthesis Draft

**Status:** Review-only synthesis. Not edited into the repo. Metrics below come from `experiment_registry.json` headline fields and corroborating narrative/docs unless noted as interpretive.

---

## Sources Read

| Path | Role | Notes |
| --- | --- | --- |
| `docs/outline.md` | Research goals, architecture, ablation plan, schema ladder (S0–S4) | Aspirational; not all goals have run evidence |
| `docs/experiments/synthesis/experiment_registry.json` | Canonical experiment rows, run IDs, headline metrics, decision scopes | `generated_on`: 2026-05-22; `row_count`: 186 |
| `docs/experiments/synthesis/experiments_narrative_report_20260520.md` | Chronological narrative through 2026-05-20 evening | S4 Qwen full marked in-flight at draft time |
| `docs/experiments/synthesis/experiment_registry_matrix_20260520.md` | Curated paper-ready matrix (72 rows, 2026-05-21) | Subset of registry; some metrics stale vs registry |
| `docs/experiments/synthesis/experiments_methods_results_20260520.md` | Referenced by narrative report (Tables 1–4) | Not in the primary-source list but used for per-family F1 where registry lacks secondary fields |

**Temporal note:** Registry rows post-dating the 2026-05-20 narrative (notably `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation`, 2026-05-23) are included below with explicit scope flags. They are **not** retroactively validated by the narrative report.

---

## Proposed Results Section Outline

### 4.1 Evaluation setup (Methods cross-reference)
- Two synthetic benchmark tracks: **Gan 2026 S0** (narrow frequency + evidence; N=299 validation) and **ExECTv2 partial field-family ladder S1→S4** (N=40 validation).
- Shared deterministic scorers: `gan_frequency_deterministic_v1`, `exect_*_field_family_deterministic_v1` (`docs/policies/deterministic_scorer_semantics.md` per narrative).
- **Fact:** No published Gan Real(300) or full ExECTv2 CUI-aware Table 1 reproduction (`experiments_narrative_report_20260520.md` §Cross-Cutting; registry metric_caveats on anchor rows).

### 4.2 Gan S0 — architecture and hybrid placement
- **Table A:** Full-validation architecture comparison (hosted GPT 4.1-mini): synthesis bootstrap → verify-repair v2 → temporal-candidates v1.1 (promoted 2026-05-20).
- **Table B:** Local Qwen3.6:35b parity row (direct+guardrails vs temporal-candidates v1.1).
- **Subsection:** Residual error bucket (`gold_pragmatic=infrequent`; narrative §2.5).
- **Optional appendix row (registry-only, post-narrative):** candidate-builder gap v1.4 full validation — cite with `decision_scope: arm` caveat.

### 4.3 Gan S0 — negative / inconclusive ablations
- GEPA cap-5, few-shot ladder, ReAct temporal tools (14-record slice), deterministic surface replay, output-budget ablation (from narrative §2.3–2.6, R2/R6 in methods/results doc).

### 4.4 ExECT S0/S1 — monolithic three-family extraction
- Section-aware ablation (reject).
- Label-policy v4.10 frozen validation anchor + test holdout generalization gap.
- Factor-isolation rows: verification verify-repair (reject, cap-25), interleaving H2 pre-vocab (reject, full).

### 4.5 ExECT schema breadth ladder (GPT frozen anchors)
- S1 (3 fam) → S2 (5) → S3 (9) → S4 (11): micro F1 decline with scope expansion; per-family weaknesses at S4 (seizure frequency, comorbidity).
- Explicit caveat: pooled micro across levels is **not** a single calibrated trajectory.

### 4.6 Model-track replication (local Qwen vs hosted GPT)
- Gan: near parity at temporal-candidates v1.1.
- ExECT: S1 seizure-type gap; S2/S3 near parity; S4 Qwen full completed in registry after narrative draft.

### 4.7 Model-suite extension (partial)
- Gemini 3.1 Flash Lite ladder replay (S1, S4 hold rows) — arm scope only.

### 4.8 Limitations (required)
- Synthetic splits, small ExECT N, cap-25 non-predictiveness for Gan, verify-repair call-count confound, evidence as program-enforced diagnostic.

---

## Key Paper Claims Map

Each entry: **Claim Statement** → **Supporting Run ID** → **Metrics** → **Rationale** (fact vs interpretation separated).

---

### Claim 1 — Hybrid temporal-candidates verify-repair is the best *frozen operational* Gan architecture (2026-05-20 promotion)

**Claim Statement:** Deterministic temporal candidate preconditioning plus LLM verify/repair (v1.1) matches prior hosted monthly accuracy while improving category and evidence metrics on Gan synthetic validation.

| Field | Value |
| --- | --- |
| **Supporting Run ID (hosted, promoted)** | `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z` |
| **Experiment ID** | `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails` |
| **Supporting Metrics** | Monthly **65.1%**; Purist **76.5%**; Pragmatic **84.2%**; schema valid **99.7%**; evidence support **100.0%** |
| **Sources** | `experiment_registry.json` (headline_metric); `experiments_narrative_report_20260520.md` §2.5; matrix `gan_s0_architecture_gpt_validation_v1` |

**Rationale:**
- **Fact:** Registry secondary metrics match narrative promotion packet comparisons vs verify-repair v2 (−0.3 pp monthly, +7.3 pp evidence, +3.8 pp Purist, +5.0 pp Pragmatic).
- **Interpretation:** Monthly treated as tie within 1 pp gate; promotion driven by category + evidence (`decision_scope: operational` per registry notes).
- **Caveat:** Split is `gan_2026_fixed_v1:validation` (N=299), not published Real(300).

**Local parity anchor:**

| Field | Value |
| --- | --- |
| **Supporting Run ID (local, promoted)** | `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T230324Z` |
| **Supporting Metrics** | Monthly **65.8%**; Purist **75.5%**; Pragmatic **82.6%**; schema **99.7%**; evidence **100.0%** |
| **Sources** | `experiment_registry.json`; matrix `gan_s0_architecture_qwen_validation_v1` |

**Rationale (interpretation):** Supports outline goal #5 partially — local Qwen reaches hosted-GPT-class Gan performance **under this program**, not across all tasks.

---

### Claim 2 — Prior hosted Gan references (superseded but citable as architecture ladder)

**Claim 2a — Verify-repair v2**

| Field | Value |
| --- | --- |
| **Supporting Run ID** | `gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z` |
| **Supporting Metrics** | Monthly **65.4%**; Purist **72.7%**; Pragmatic **79.2%**; evidence **92.7%**; schema **96.7%** |
| **Outcome** | `superseded` (`decision_scope: arm`) |
| **Sources** | `experiment_registry.json`; narrative §2.2 |

**Claim 2b — Synthesis + BootstrapFewShot (CoT)**

| Field | Value |
| --- | --- |
| **Supporting Run ID** | `gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z` |
| **Supporting Metrics** | Monthly **62.9%**; Purist **70.1%**; Pragmatic **73.9%**; evidence **89.9%**; schema **97.3%** |
| **Outcome** | `superseded` |
| **Sources** | `experiment_registry.json` (headline_metric); narrative §2.1 |

**Rationale:**
- **Fact:** Verify-repair improved monthly +2.5 pp over synthesis on same split/scorer.
- **Caveat (registry):** Synthesis artifact documented but **may be absent from local `runs/`** — metrics sourced from decision/docs backfill (`metric_caveats` on row).

**Claim 2c — Local direct path baseline (architecture contrast)**

| Field | Value |
| --- | --- |
| **Supporting Run ID** | `gan_s0_qwen35b_direct_full_validation_guardrails_20260519T102249Z` |
| **Supporting Metrics** | Monthly **55.9%**; Purist **61.9%**; Pragmatic **70.5%**; evidence **99.6%** |
| **Outcome** | `exploratory` (`decision_scope: arm`) |
| **Sources** | `experiment_registry.json`; matrix |

**Rationale (interpretation):** Temporal-candidates adds **~10 pp** monthly over direct+guardrails locally — supports hybrid **H2/H4 pre-conditioning** claim from outline architecture section.

---

### Claim 3 — GEPA / few-shot optimizers did not beat manual architecture on Gan at scale

**Claim Statement:** DSPy GEPA and cap-25 few-shot ladders did not exceed synthesis or temporal-candidates full-validation monthly accuracy.

| Field | Value |
| --- | --- |
| **Supporting Run ID (GEPA cap-5)** | `gan_s0_gepa_direct_cap5_gpt4_1_mini_20260519T054057Z` |
| **Supporting Metrics** | `headline_metric: null` in registry — **missing primary metric in registry row** |
| **Outcome** | Narrative: schema/evidence gains, unstable labels; decision deprioritize GEPA |
| **Sources** | `experiment_registry.json`; narrative §2.3; `docs/experiments/gan/gan_s0_gepa_vs_synthesis_decision_20260519.md` (cited in registry) |

**Rationale:**
- **Fact:** Full-validation monthly for GEPA cap-5 is **not** in registry headline fields.
- **Interpretation (narrative):** GEPA did not beat synthesis full validation (62.9% monthly anchor).
- **Caveat:** Claim must cite narrative/decision doc for qualitative outcome until registry backfill.

---

### Claim 4 — ExECT monolithic label-policy engineering reaches strong S0/S1 validation performance (partial schema)

**Claim Statement:** Frozen GPT 4.1-mini monolithic label policy v4.10 achieves high micro F1 on three audited field families (diagnosis, seizure type, annotated medication) on 40-record validation.

| Field | Value |
| --- | --- |
| **Supporting Run ID** | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` |
| **Experiment ID** | `exect_s0_s1_validation_full_gpt4_1_mini` |
| **Supporting Metrics** | Micro F1 **92.3%** |
| **Per-family (secondary, ladder row)** | Diagnosis **93.8%**; seizure type **90.5%**; medication **92.8%** F1 — from `exect_s1_full_ladder_l1_policy_full_gpt4_1_mini` registry secondary / `experiments_methods_results_20260520.md` Table 2 |
| **Outcome** | `freeze` (`decision_scope: operational`) |
| **Sources** | `experiment_registry.json`; matrix `exect_schema_complexity_gpt_validation_v1` |

**Test holdout (generalization):**

| Field | Value |
| --- | --- |
| **Supporting Run ID** | `exect_s0_s1_validation_test_gpt4_1_mini_20260519T222615Z` |
| **Supporting Metrics** | Micro F1 **77.8%** (−14.5 pp vs validation per methods doc) |
| **Outcome** | `hold` |
| **Sources** | `experiment_registry.json`; matrix `exect_s1_generalization_gpt_test_v1` |

**Rationale:**
- **Fact:** High validation micro F1 on **partial** ExECT schema only (3 families / 40 val).
- **Interpretation:** Supports modular specialization on broad-schema task **within audited subset**; does **not** establish full ExECTv2 paper reproduction (registry metric_caveats).

---

### Claim 5 — Section-aware ExECT extraction regresses vs monolithic (negative result)

| Field | Value |
| --- | --- |
| **Supporting Run ID** | `exect_s0_s1_section_aware_cap25_gpt4_1_mini_20260518T174714Z` |
| **Supporting Metrics** | Micro F1 **65.6%** (cap-25) |
| **Baseline (narrative)** | Monolithic cap-25 early policy **73.7%** — run `exect_s0_s1_validation_cap25_gpt4_1_mini_20260518T172431Z` cited in narrative §3.1; registry cap-25 v4.10 row shows **95.8%** under later policy (not comparable to section-aware v3 policy) |
| **Outcome** | `reject` (`decision_scope: arm`) |
| **Sources** | `experiment_registry.json`; narrative §3.1; matrix `exect_s1_architecture_gpt_cap25_v1` |

**Rationale (interpretation):** Supports outline ablation expectation that section splitting can hurt without stronger section classification — but **cap-25 scope** and **policy version mismatch** limit paper strength; prefer paired same-policy comparison or cite as directional only.

---

### Claim 6 — Schema breadth increases task difficulty (ExECT ladder)

**Claim Statement:** As field-family scope expands S1→S4, pooled micro F1 falls on the same 40-record validation split under GPT 4.1-mini monolithic programs.

| Schema | Run ID | Families (fact from design docs) | Micro F1 |
| --- | --- | --- | ---: |
| S1 | `…221944Z` | 3 | **92.3%** |
| S2 | `exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` | 5 | **80.9%** |
| S3 | `exect_s3_validation_full_gpt4_1_mini_20260519T235439Z` | 9 | **72.1%** |
| S4 | `exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` | 11 | **65.5%** |

**Sources:** `experiment_registry.json` headline metrics; matrix `exect_schema_complexity_gpt_validation_v1`; narrative §4; `experiments_methods_results_20260520.md` Table 3 for per-family color (seizure frequency **45.7%** at S4 — narrative/registry inspection docs, not all in headline fields).

**Rationale:**
- **Fact:** Monotonic decline in headline micro F1 at each frozen GPT anchor.
- **Caveat (required):** Micro F1 aggregates **different family sets** — registry `comparison_caveat` and narrative §Metric Caveats #4: trend describes **breadth cost**, not a single score scale.
- **Outcome:** S1–S4 GPT rows `freeze` / `operational` per registry.

---

### Claim 7 — Local Qwen replication: Gan parity, ExECT task-dependent gap

**Claim 7a — ExECT S0/S1 Qwen vs GPT**

| Field | Value |
| --- | --- |
| **Supporting Run ID** | `exect_s0_s1_validation_full_qwen35b_ollama_20260520T042117Z` |
| **Supporting Metrics** | Micro F1 **79.0%** vs GPT **92.3%** (−13.3 pp) |
| **Per-family (narrative)** | Diagnosis **95.1%** vs **93.8%**; seizure type **55.7%** vs **90.5%**; medication **89.1%** vs **92.8%** |
| **Outcome** | `hold` (`decision_scope: arm`) |
| **Sources** | `experiment_registry.json`; narrative §3.3; methods Table 4 |

**Claim 7b — ExECT S2/S3 Qwen near GPT**

| Level | GPT run | GPT micro | Qwen run | Qwen micro | Δ |
| --- | --- | ---: | --- | ---: | ---: |
| S2 | `…231223Z` | 80.9% | `…073552Z` | **82.6%** | +1.7 pp |
| S3 | `…235439Z` | 72.1% | `…092244Z` | **72.2%** | +0.1 pp |

**Sources:** `experiment_registry.json`; matrix `exect_qwen_replication_validation_v1`.

**Claim 7c — ExECT S4 Qwen (registry update post-narrative)**

| Field | Value |
| --- | --- |
| **Supporting Run ID** | `exect_s4_validation_full_qwen35b_ollama_20260520T160914Z` |
| **Supporting Metrics** | Micro F1 **67.5%** vs GPT S4 **65.5%** (+2.0 pp pooled) |
| **Outcome** | `hold` (`decision_scope: arm`) |
| **Sources** | `experiment_registry.json`; matrix (updated vs narrative "pending") |

**Rationale (interpretation):** Qwen viable for hospital-local deployment on Gan and mid-ladder ExECT; **S1 seizure-type granularity** remains the documented weakness. S4 Qwen pooled micro **exceeds** GPT but registry notes **per-family profile diverges** — do not claim uniform superiority without inspection doc per-family table (`docs/experiments/exect/exect_s4_validation_full_qwen35b_ollama_inspection_20260520.md`).

---

### Claim 8 — Deterministic hybrid placement matters (interleaving / verification ablations)

**Claim 8a — ExECT verify-repair hurts S1 (cap-25)**

| Field | Value |
| --- | --- |
| **Supporting Run ID** | `exect_s1_verification_verify_repair_cap25_gpt4_1_mini_20260520T232841Z` |
| **Supporting Metrics** | Micro F1 **86.4%** vs single-pass cap-25 **95.8%** (registry matrix) |
| **Outcome** | `reject` (`decision_scope: arm`) |

**Claim 8b — Pre-vocab H2 interleaving regresses full S1**

| Field | Value |
| --- | --- |
| **Supporting Run ID** | `exect_s1_interleaving_h2_pre_vocab_gpt4_1_mini_20260520T185755Z` |
| **Supporting Metrics** | Micro F1 **87.5%** vs L1 anchor **92.3%** |
| **Outcome** | `reject` (`decision_scope: arm`) |

**Claim 8c — S4 medication temporality: post-hoc classifier not promoted at full validation**

| Field | Value |
| --- | --- |
| **Baseline run** | `exect_s4_temporality_l1_baseline_full_gpt4_1_mini_20260520T204207Z` |
| **Baseline metric** | `field_precision.medication_temporality` **46.4%** |
| **H1 post-classifier full** | `exect_s4_temporality_h1_post_classifier_full` — **56.5%** precision at cap-25 hold but **`reject` at full** (matrix) |
| **Sources** | `experiment_registry.json`; matrix `exect_s4_temporality_deterministic_v1` |

**Rationale (interpretation):** Supports outline thesis that deterministic placement is task-dependent — helps Gan temporal path (pre), hurts ExECT verify-repair and some pre-vocab injections.

---

### Claim 9 — ReAct temporal tools inferior to temporal-candidates on hard slice (mechanism probe)

| Field | Value |
| --- | --- |
| **Supporting Run ID** | `gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails_20260520T173943Z` |
| **Supporting Metrics** | Monthly **42.9%** (7/14 valid preds); schema valid **50%** |
| **Contrast (slice)** | Temporal-candidates regression slice **100%** monthly (N=14) — `gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_guardrails` |
| **Outcome** | `reject` (`decision_scope: arm`) |
| **Sources** | `experiment_registry.json`; matrix `gan_s0_hard_slice_qwen_architecture_v1` |

**Rationale:** **Fact:** Negative control on fixed 14-record fixture. **Caveat:** Slice not extrapolatable to full validation (registry metric_caveats).

---

### Claim 10 — Gemini 3.1 Flash Lite as hosted alternative (partial model suite)

| Track | Run ID | Micro / Monthly | Outcome |
| --- | --- | --- | --- |
| ExECT S1 full | `exect_s0_s1_validation_full_gemini31_flash_lite_20260521T093501Z` | Micro **90.3%** | `hold` (arm) |
| ExECT S4 full | `exect_s4_validation_full_gemini31_flash_lite_20260521T093556Z` | Micro **66.8%** | `hold` (arm) |
| Gan direct full (narrative) | `gan_s0_direct_full_validation_gemini31_flash_lite_20260519T101710Z` | Monthly **63.9%** (narrative §2.3; registry `headline_metric: null`) |

**Sources:** Registry for ExECT; narrative for Gan monthly.

**Rationale:** **Interpretation:** Intermediate hosted model competitive on Gan/ExECT **repo metrics**; not promoted as operational default. **Missing:** GPT 5.5, Gemini 3 Flash full ladder — not in registry curated anchors.

---

### Claim 11 — NEWER (post-202605-20 narrative): candidate-builder gap v1.4 full validation

| Field | Value |
| --- | --- |
| **Supporting Run ID** | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` |
| **Supporting Metrics** | Monthly **80.6%**; Purist **86.0%**; Pragmatic **88.6%**; schema **100%**; evidence **100%** |
| **Outcome** | `promote` but **`decision_scope: arm`** — registry notes: *operational default remains separate* |
| **Sources** | `experiment_registry.json` only (not in 20260520 narrative/matrix) |

**Rationale:**
- **Fact:** Highest registry headline monthly on Gan synthetic validation as of registry date.
- **Uncertainty:** Not validated in narrative report or matrix; supersedes temporal-candidates v1.1 **only as an arm-scope experiment** until operational promotion is documented elsewhere.
- **Paper guidance:** Cite as **emerging result** with synthetic-split caveat; do **not** replace Table 1 from `experiments_methods_results_20260520.md` without human verification of rerun inspection doc (`docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_full_validation_rerun_inspection_20260523.md` — path from registry; **not read in this draft**).

---

## Discrepancies Or Unsupported Claims

### Claims in `outline.md` without registry/narrative backing

| Outline claim | Status | Evidence gap |
| --- | --- | --- |
| **Beat ExECTv2 and Gan paper benchmarks** (Goal #1) | **Unsupported / blocked** | Narrative §Cross-Cutting: no Gan Real(300), no CUI-aware ExECT Table 1. Repo Gan monthly ~65% vs published Purist micro-F1 ~0.78–0.79 (indicative, narrative). |
| **Downstream use cases** (clinical support, billing, cohort selection) | **Unsupported** | No experiments in registry/narrative. |
| **GPT 5.5 evaluation** | **Unsupported** | Listed in outline model list; no registry rows. |
| **Qwen3.5:9b as serious contender** | **Partial / weak** | Smoke/latency probes only; narrative §2.6: weaker than 35b. |
| **Comprehensive ablation grid** (all outline §Ablations) | **Partially supported** | Many factors tested on Gan; ExECT optimizers **never implemented** (narrative §Cross-Cutting). |
| **GEPA / BootstrapFewShot as primary ExECT improvement path** | **Rejected / blocked** | Runner gate: optimizers Gan-only; ExECT gains from manual label policy. |
| **Evidence-first extraction improves precision universally** | **Mixed** | Helps Gan temporal path; ExECT verify-repair rejected. |

### Internal source discrepancies

| Issue | Detail |
| --- | --- |
| **Narrative vs registry on ExECT S4 Qwen** | Narrative §4.4: S4 Qwen *pending*. Registry/matrix: `…160914Z` micro **67.5%** complete. Matrix is authoritative over narrative for this row. |
| **Gan promoted default vs newer arm row** | Operational default remains temporal-candidates v1.1 (`…130933Z`, 65.1%) per 20260520 docs; registry adds candidate-builder gap **80.6%** with `decision_scope: arm`. |
| **Synthesis bootstrap artifact** | Registry: run metrics documented but artifact **may be missing locally** (`metric_caveats`). |
| **Matrix export date** | Matrix generated 2026-05-21 (72 curated rows); registry 2026-05-22 (186 rows). Prefer registry for run IDs/metrics; matrix for comparison_group layout. |
| **Per-family ExECT F1 at S2–S4** | Headline registry fields are pooled micro only; per-family numbers in methods doc Table 3 come from inspection runs — verify against `runs/*/metrics.json` before publication. |
| **Section-aware vs monolithic cap-25** | Different prompt policy versions weaken direct subtraction; narrative −8.1 pp figure uses early monolithic v3 vs section-aware v3 — flag in paper. |

---

## Open Writing Tasks

### Verification before publication (human)

1. **Primary artifact pull:** For every table row, confirm metrics from `runs/<canonical_run_id>/metrics.json` (registry headline fields are secondary).
2. **Resolve Gan headline table:** Choose between (a) frozen 2026-05-20 operational anchors (temporal v1.1) vs (b) include 2026-05-23 candidate-builder gap arm result with explicit scope — requires reading `gan_s0_candidate_builder_gap_v1_gpt_full_validation_rerun_inspection_20260523.md`.
3. **Published benchmark column:** Extract ExECTv2/Gan paper numbers from `data/` papers per outline; label as **external reference**, not repo reproduction (`docs/policies/published_benchmark_metrics.md`).
4. **Per-family ExECT tables:** Export from frozen inspection docs or metrics JSON for S2–S4 (seizure frequency, comorbidity, medication temporality).
5. **Bootstrap CIs:** Narrative mentions overlapping CIs for hosted temporal vs verify-repair monthly — locate CI artifact or recompute for paper.
6. **Stratified Gan infrequent bucket:** Confirm 51-record count and 43–51% monthly from promoted full-run error analysis scripts.

### Writing gaps

7. **Methods:** Document deterministic foundation milestone (Phase 0) briefly; cite scorer policies.
8. **Results framing:** Lead with **repo synthetic evaluation** scope in abstract/intro — do not imply paper benchmark beating.
9. **Discussion:** Separate **operational** conclusions (promoted programs) from **arm** conclusions (interleaving matrix, candidate-builder gap, Gemini ladder).
10. **Limitations paragraph:** N=40 ExECT, cap-25 optimism, verify-repair latency, evidence-as-policy diagnostic.
11. **Model suite section:** Report Gemini partial results; state GPT 5.5 / Real(300) as **planned/blocked** with decision scopes preserved.
12. **Update living docs:** Regenerate matrix after registry freeze for paper snapshot (`scripts/export_experiment_registry_matrix.py` per matrix header).

### Decision-scope legend for paper (preserve verbatim taxonomy)

| Scope | Meaning for prose |
| --- | --- |
| **operational** | Default system choice for a track |
| **arm** | Valid comparison arm; not necessarily deployed default |
| **mechanism** | Isolated factor test; no deployment claim |
| **open** | Scheduled / incomplete |
| **blocked** | Prevented by infra or policy (e.g., published benchmark reproduction) |
| **stale_check** | Re-verify before cite (e.g., synthesis artifact presence, post-narrative rows) |

---

*End of review draft. No repository files were modified.*