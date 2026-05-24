# Paper Narrative Synthesis Draft

**Workflow:** Automated paper narrative synthesis (review-only)  
**Repository:** `C:\Users\cbrow\Code\dspy-extraction`  
**Draft date:** 2026-05-24  
**Status:** Interpretive synthesis only — not evidence unless linked to primary run artifacts under `runs/`.

---

## Sources Read

| Path | Role |
| --- | --- |
| `docs/outline.md` | Research goals, architecture, ablation plan, model suite |
| `docs/experiments/synthesis/experiment_registry.json` | Canonical run IDs, headline metrics, decision scopes, comparison groups (130 rows; curated matrix uses 72) |
| `docs/experiments/synthesis/experiments_narrative_report_20260520.md` | Chronological experiment narrative through 2026-05-20 evening |
| `docs/experiments/synthesis/experiment_registry_matrix_20260520.md` | Paper-ready grouped export (generated 2026-05-21) |
| `docs/experiments/synthesis/experiments_methods_results_20260520.md` | Referenced by narrative report as paper-style Methods/Results extract (Tables 1–4) |

**Registry–narrative freshness note (`stale_check`):** The matrix and registry include rows post-dating the 2026-05-20 narrative (e.g., ExECT Qwen S4 full validation, S1 interleaving/ladder arms, S4 temporality probes). Where they diverge, this draft prefers registry canonical metrics and flags the gap.

---

## Proposed Results Section Outline

Use this as the paper Results skeleton; each subsection should cite one primary run ID per comparison row.

### §4.1 Gan S0 — Seizure-frequency extraction (N = 299 validation)

- **4.1.1 Full-validation system comparison** — Table 1: promoted temporal-candidates v1.1 (hosted + local) vs verify-repair v2 vs synthesis bootstrap vs Qwen direct baseline.
- **4.1.2 Architecture ablation** — verify-repair cap-25 gains; temporal-candidates promotion gates; evidence/schema diagnostics.
- **4.1.3 Optimizer negative results** — GEPA cap-5, few-shot ladder (cap-25 only; headline metrics often null in registry).
- **4.1.4 Residual error stratification** — `gold_pragmatic = infrequent` bucket (~43–51% monthly); source: narrative report + promoted full runs (not a separate registry row).
- **4.1.5 Hard-slice probes (N = 14)** — temporal-candidates B1/B2 vs ReAct temporal tools (reject).

### §4.2 ExECT S0/S1 — Three-family monolithic extraction (N = 40 validation; N = 40 test holdout)

- **4.2.1 Frozen GPT v4.10 validation anchor** — diagnosis / seizure-type / medication micro F1.
- **4.2.2 Architecture negative result** — section-aware cap-25 vs monolithic.
- **4.2.3 Generalization** — validation vs test holdout gap.
- **4.2.4 Factor isolation (cap-25 / full)** — verify-repair reject; evidence-policy cap-25; interleaving H1 vs H2.

### §4.3 ExECT schema ladder — Breadth cost (GPT frozen; N = 40 validation)

- **4.3.1 S1 → S4 micro F1 trajectory** — with explicit caveat that family sets differ (3 → 5 → 9 → 11 families).
- **4.3.2 Per-family failure modes at S4** — seizure-frequency F1, investigation recovery, comorbidity accepted gaps.
- **4.3.3 S4 temporality deterministic probe** — medication temporality precision (cap-25 pass, full reject).

### §4.4 Local Qwen3.6:35b replication (frozen GPT prompts)

- **4.4.1 Gan** — temporal-candidates parity with hosted GPT on monthly/Purist/Pragmatic.
- **4.4.2 ExECT ladder** — S1 seizure-type gap; S2–S4 pooled micro tracking; S4 per-family divergence caveat.

### §4.5 Hybrid deterministic placement (mechanism claims)

- **4.5.1 Gan temporal-candidates (H2 pre + H4 deterministic-first)** — pre-conditioning beats direct-only and ReAct tools on hard slice.
- **4.5.2 ExECT deterministic ladder floor (D1)** — substring-only baseline vs L1+policy full validation.
- **4.5.3 ExECT post-hoc deterministic bridges (H1)** — S4 temporality classifier: precision up, F1 down → reject.

### §4.6 Summary of rejected hypotheses

- Section-aware ExECT; GEPA at scale; larger Qwen output budget; deterministic surface replay; BootstrapFewShot on local Qwen for routine eval; cap-25 as full-validation predictor for temporal path.

### §4.7 Limitations (cross-reference Methods)

- Synthetic splits only; no Gan Real(300) or full ExECT CUI-aware Table 1 reproduction (`docs/policies/published_benchmark_metrics.md` per narrative).

---

## Key Paper Claims Map

Each row: **Claim Statement** → **Supporting Run ID** → **Metrics** → **Rationale** → **Decision scope**

---

### Claim 1 — Temporal-candidates verify-repair v1.1 is the promoted Gan S0 architecture (hosted)

1. **Claim Statement:** Deterministic temporal candidate hints plus verify-repair outperform or tie prior hosted architectures on benchmark-facing Gan metrics while improving evidence and category accuracy.
2. **Supporting Run ID:** `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z`  
   - Registry: `experiment_id` = `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails`  
   - Comparison group: `gan_s0_architecture_gpt_validation_v1`  
   - Outcome: **promote**
3. **Supporting Metrics:** Monthly 65.1%; Purist 76.5%; Pragmatic 84.2%; schema valid 99.7%; evidence 100.0%  
   - Source: `experiment_registry.json` headline_metric on above run; corroborated in `experiments_methods_results_20260520.md` Table 1 and `experiments_narrative_report_20260520.md` §2.5
4. **Rationale:** Monthly ties verify-repair v2 (−0.3 pp, within 1 pp gate per `docs/experiments/gan/gan_s0_gpt4_1_mini_temporal_candidates_full_validation_decision_20260520.md` cited in registry). Purist (+3.8 pp), Pragmatic (+5.0 pp), evidence (+7.3 pp) vs `gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z` (65.4% monthly, 92.7% evidence). **Fact:** metrics on `gan_2026_fixed_v1:validation` (N = 299), not published Gan Real(300). **Interpretation:** architecture + deterministic scaffolding drives adoption, not raw monthly gain.
5. **Decision scope:** `operational`

---

### Claim 2 — Local Qwen reaches hosted-GPT parity on Gan under the same temporal program

1. **Claim Statement:** Qwen3.6:35b with temporal-candidates v1.1 matches hosted GPT on monthly frequency and exceeds direct-only local extraction.
2. **Supporting Run ID:** `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T230324Z`  
   - Registry: `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails` → **promote**
3. **Supporting Metrics:** Monthly 65.8%; Purist 75.5%; Pragmatic 82.6%; schema 99.7%; evidence 100.0%  
   - Baseline contrast: `gan_s0_qwen35b_direct_full_validation_guardrails_20260519T102249Z` — monthly 55.9%, Purist 62.0%, Pragmatic 70.5%
4. **Rationale:** +10.0 pp monthly vs local direct guardrails; within ~1 pp of hosted temporal (65.1%). Supports outline Goal 5 (local model viability for narrow semantic task) **on repo synthetic validation only**. Residual `infrequent` bucket unchanged (narrative §2.5; not isolated as registry headline).
5. **Decision scope:** `operational`

---

### Claim 3 — Verify-repair and synthesis bootstrap are superseded Gan references, not defaults

1. **Claim Statement:** Prior hosted verify-repair v2 and synthesis BootstrapFewShot full-validation runs are historical comparators superseded by temporal-candidates.
2. **Supporting Run IDs:**
   - Verify-repair v2: `gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z` (**superseded**) — monthly 65.4%, Purist 72.7%, Pragmatic 79.2%, evidence 92.7%
   - Synthesis bootstrap: `gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z` (**superseded**) — monthly 62.9%, Purist 70.1%, Pragmatic 73.9%, evidence 89.9%
3. **Supporting Metrics:** As above from `experiment_registry.json`
4. **Rationale:** Temporal-candidates meets or beats both on monthly while improving category/evidence metrics. Synthesis established optimizer path viability but lower monthly than verify-repair/temporal. **Caveat (`stale_check`):** registry notes synthesis run directory **may be absent locally** — metrics sourced from registry/docs, not re-verified from `runs/` in this draft.
5. **Decision scope:** `arm` (historical reference)

---

### Claim 4 — GEPA and cap-scale optimizers do not beat manual/architectural Gan engineering

1. **Claim Statement:** GEPA cap-5 improved schema/evidence on small caps but did not yield stable full-validation label quality; deprioritized vs temporal-candidates.
2. **Supporting Run ID:** `gan_s0_gepa_direct_cap5_gpt4_1_mini_20260519T054057Z`  
   - Registry: `gan_s0_gepa_direct_cap5_gpt4_1_mini` → **reject**; `headline_metric`: **null**
3. **Supporting Metrics:** No registry headline metric; narrative cites cap-5 schema/evidence gains without stable monthly labels (`experiments_narrative_report_20260520.md` §2.3; `docs/experiments/gan/gan_s0_gepa_vs_synthesis_decision_20260519.md`)
4. **Rationale:** Supports outline ablation question on optimizers vs manual engineering. **Uncertainty:** exact cap-5 monthly/evidence numbers must be pulled from `runs/.../metrics.json` before paper tables — not in registry headline field.
5. **Decision scope:** `mechanism` / `arm`

---

### Claim 5 — ExECT monolithic label-policy v4.10 achieves high micro F1 on three audited families (GPT)

1. **Claim Statement:** Iterative manual label-policy engineering on monolithic single-pass extraction reaches 92.3% micro F1 on diagnosis, seizure-type, and annotated medication (validation).
2. **Supporting Run ID:** `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z`  
   - Registry: `exect_s0_s1_validation_full_gpt4_1_mini` → **freeze**; comparison group `exect_schema_complexity_gpt_validation_v1`
3. **Supporting Metrics:** Micro F1 92.3%  
   - Per-family (narrative/methods, not registry headline): Diagnosis 93.8%, Seizure-type 90.5%, Medication 92.8% (`experiments_methods_results_20260520.md` Table 2)
4. **Rationale:** Validates outline claim that broad-task gains came from label policy + deterministic bridges, not section splitting or ExECT optimizers (runner gate: optimizers Gan-only per narrative §Cross-Cutting). **Not** full ExECTv2 paper reproduction (partial 3-family view, N = 40).
5. **Decision scope:** `operational`

---

### Claim 6 — Section-aware ExECT extraction regresses vs monolithic (architecture ablation)

1. **Claim Statement:** Deterministic section selection before per-family extraction hurts micro F1 and evidence support on cap-25.
2. **Supporting Run ID:** `exect_s0_s1_section_aware_cap25_gpt4_1_mini_20260518T174714Z`  
   - Registry: `exect_s0_s1_section_aware_cap25_gpt4_1_mini` → **reject**; micro F1 **65.6%**
3. **Supporting Metrics:** Section-aware micro F1 65.6% vs monolithic cap-25 `exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T221936Z` micro F1 95.8% (registry); early monolithic cap-25 baseline 73.7% in narrative Table 2 (different label-policy generation — **do not mix policy versions without annotation**)
4. **Rationale:** Supports negative result on outline Variant B (section → field-specific extraction). Diagnosis F1 drop largest in narrative (−15.6 pp vs early monolithic cap-25). **Caveat:** cap-25 only (`decision_scope: arm`); optimistic vs full validation.
5. **Decision scope:** `mechanism`

---

### Claim 7 — ExECT validation-to-test generalization gap on frozen S0/S1 policy

1. **Claim Statement:** Frozen v4.10 policy overfits validation relative to one-shot test holdout.
2. **Supporting Run ID:** `exect_s0_s1_validation_test_gpt4_1_mini_20260519T222615Z`  
   - Registry: `exect_s0_s1_validation_test_gpt4_1_mini` → **hold**; micro F1 **77.8%**
3. **Supporting Metrics:** Test micro F1 77.8% vs validation 92.3% (−14.5 pp); test seizure-type F1 66.0% (methods Table 2)
4. **Rationale:** Caveats any claim of near-paper ExECT performance (paper ~0.90 all-letter F1 cited in narrative §Published benchmark distance — **not reproduced**). One-shot test; no further tuning after freeze.
5. **Decision scope:** `arm`

---

### Claim 8 — Schema breadth monotonically reduces pooled micro F1 (GPT ladder)

1. **Claim Statement:** Adding field families predictably lowers micro F1 as schema complexity increases from S1 to S4.
2. **Supporting Run IDs (frozen anchors):**
   - S1 (3 fam): `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` — **92.3%**
   - S2 (5 fam): `exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` — **80.9%**
   - S3 (9 fam): `exect_s3_validation_full_gpt4_1_mini_20260519T235439Z` — **72.1%**
   - S4 (11 fam): `exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` — **65.5%**
3. **Supporting Metrics:** Micro F1 as above; S4 seizure-frequency F1 **45.7%**, investigation F1 **96.7%** (narrative §4.3 / methods Table 3 — per-family not in registry headline)
4. **Rationale:** Directly addresses outline schema-level ablation (S0–S4). **Critical caveat:** micro F1 aggregates **different family sets** at each level — describe as breadth cost, not a single calibrated learning curve (`experiment_registry_matrix_20260520.md` Caveats; registry `comparison_caveat` on each row).
5. **Decision scope:** `operational` (frozen ladder anchors)

---

### Claim 9 — Local Qwen replication: Gan parity, ExECT S1 seizure-type weakness, S2–S3 tracking, S4 divergence

1. **Claim Statement:** Qwen matches GPT on Gan temporal program; on ExECT replicates GPT at S2–S3 micro F1 but lags at S1 (seizure-type) and shows pooled-micro vs per-family divergence at S4.
2. **Supporting Run IDs:**
   - S1: `exect_s0_s1_validation_full_qwen35b_ollama_20260520T042117Z` — micro F1 **79.0%** (GPT 92.3%, −13.3 pp)
   - S2: `exect_s2_validation_full_qwen35b_ollama_20260520T073552Z` — **82.6%** (GPT 80.9%, +1.7 pp)
   - S3: `exect_s3_validation_full_qwen35b_ollama_20260520T092244Z` — **72.2%** (GPT 72.1%, +0.1 pp)
   - S4: `exect_s4_validation_full_qwen35b_ollama_20260520T160914Z` — **67.5%** (GPT 65.5%, +2.0 pp)
3. **Supporting Metrics:** Micro F1 as above. Narrative/methods: S1 Qwen diagnosis F1 95.1% vs GPT 93.8%; seizure-type F1 55.7% vs 90.5% (`experiments_narrative_report_20260520.md` §3.3)
4. **Rationale:** Supports outline Goal 5 with task-dependent split: **narrow Gan task → local viable; fine-grained seizure typing → hosted advantage on S1**. S4 Qwen **completed in registry** but narrative/methods (20260520) still say *pending* — use registry for paper, note stale narrative. Registry notes: pooled micro exceeds GPT but **per-family profile diverges** (`decision_scope: arm`; inspection: `docs/experiments/exect/exect_s4_validation_full_qwen35b_ollama_inspection_20260520.md`).
5. **Decision scope:** `arm`

---

### Claim 10 — Pre-vocab deterministic injection (H2) regresses ExECT S1 full validation

1. **Claim Statement:** Injecting controlled vocabulary before LLM extraction lowers full-validation micro F1 vs L1 baseline with post-hoc bridges.
2. **Supporting Run ID:** `exect_s1_interleaving_h2_pre_vocab_gpt4_1_mini_20260520T185755Z` → **reject**; micro F1 **87.5%**  
   - Contrast (hold): `exect_s1_interleaving_h1_post_bridge` canonical full validation micro F1 **92.3%** (same as frozen anchor; matrix `exect_s1_interleaving_gpt_validation_v1`)
3. **Supporting Metrics:** H2 full 87.5% vs H1/post-bridge 92.3% (−4.8 pp per registry notes)
4. **Rationale:** Mechanism claim for **where** deterministic normalization helps (post-extraction bridges vs pre-vocab injection). Aligns with outline question on deterministic vs LLM normalization — pre-vocab hurt here.
5. **Decision scope:** `mechanism`

---

### Claim 11 — Deterministic-only floor (D1) far below L1+policy on ExECT S1

1. **Claim Statement:** A deterministic substring-match floor without LLM interpretation achieves ~58.4% micro F1 cap-25 vs ~92.3% full validation with L1 constrained LLM + label policy.
2. **Supporting Run IDs:**
   - D1 cap-25: `exect_s1_full_ladder_d1_cap25_gpt4_1_mini_20260521T003704Z` — micro F1 **58.4%**
   - L1+policy full: `exect_s1_full_ladder_l1_policy_full_gpt4_1_mini_20260521T004209Z` — micro F1 **92.3%**
3. **Supporting Metrics:** As above; D1 secondary: diagnosis F1 52.9%, seizure-type F1 50.0%, medication F1 70.1%
4. **Rationale:** Quantifies hybrid value: deterministic harness alone insufficient; LLM interpretation required for audited families. L1+policy full matches frozen anchor — validates ladder methodology (`docs/experiments/exect/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md`).
5. **Decision scope:** `mechanism` / `operational`

---

### Claim 12 — S4 post-hoc medication temporality classifier: precision gain, F1 loss → reject

1. **Claim Statement:** H1 post-classifier improves medication temporality precision on cap-25 but fails full-validation F1 guard due to recall collapse.
2. **Supporting Run IDs:**
   - Cap-25 (hold): `exect_s4_temporality_h1_post_classifier_cap25_gpt4_1_mini_20260520T203803Z` — MT precision **61.3%**
   - Full (reject): `exect_s4_temporality_h1_post_classifier_full_gpt4_1_mini_20260520T204216Z` — MT precision **56.5%** vs L1 baseline full `exect_s4_temporality_l1_baseline_full_gpt4_1_mini_20260520T204207Z` — **46.4%**
3. **Supporting Metrics:** Field precision `medication_temporality` as above; registry notes −6.6 pp MT F1 on full validation for H1
4. **Rationale:** Negative mechanism result for post-hoc deterministic temporality on S4. Addresses outline temporality-guideline ablation partially — deterministic post-classifier not promoted.
5. **Decision scope:** `mechanism`

---

### Claim 13 — ReAct temporal tools underperform temporal-candidates on hard slice

1. **Claim Statement:** Tool-during (H3) interleaved temporal reasoning loses to pre-conditioned temporal-candidates on the 14-record regression slice.
2. **Supporting Run ID:** `gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails_20260520T173943Z` → **reject**  
   - Contrast: `gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_guardrails` — monthly **100%** on slice (matrix; exploratory)
3. **Supporting Metrics:** ReAct monthly **42.9%** (7 valid / 14 evaluated); schema valid **50%** vs temporal-candidates **100%** on slice
4. **Rationale:** Supports choosing H2/H4 pre-conditioning over H3 tool interleaving for Gan temporal errors. Slice N = 14 — directional only.
5. **Decision scope:** `mechanism`

---

### Claim 14 — Modular system adapts to two distinct task regimes (interpretive synthesis)

1. **Claim Statement:** The same DSPy + deterministic infrastructure supports a narrow temporal Gan task and a broad ExECT ladder with different promoted architectures and scorers.
2. **Supporting Run IDs:** Gan promote runs (Claims 1–2); ExECT freeze ladder (Claim 8); shared foundation per narrative Phase 0 (`docs/policies/deterministic_foundation_decisions.md`)
3. **Supporting Metrics:** Gan monthly ~65–66%; ExECT S1 micro 92.3% vs S4 micro 65.5%
4. **Rationale:** **Interpretation** of outline Goal 2 — **Fact:** two task tracks exist with different default programs. **Unsupported:** downstream use cases (billing, cohort selection, outcome variables) — no registry rows.
5. **Decision scope:** `operational` (infra) + `open` (downstream tasks)

---

## Discrepancies Or Unsupported Claims

### Claims in `outline.md` without registry/narrative backing

| Outline claim | Status | Notes |
| --- | --- | --- |
| **Goal 1:** Beat ExECTv2 and Gan **published** benchmarks | **blocked** | Narrative §Executive Summary; matrix Caveats; `docs/policies/published_benchmark_metrics.md`. No Gan Real(300) or full ExECT Table 1 runs in registry. |
| **Goal 2:** Downstream adaptation (billing, cohort selection, outcome variables) | **unsupported** | No experiments in registry or narrative. |
| **Goal 3:** Comprehensive ablation of few-shot, section splitting, evidence, repair **across all tasks** | **partial** | Gan: extensive. ExECT: section-aware, interleaving, temporality, ladder — but many outline ablations (negation-specific, ILAE guidelines, multi-step pipeline matrix) **not run**. |
| **Models:** GPT 5.5, Gemini 3 Flash, Qwen 9b as primary comparators | **partial / smoke only** | Registry has Gemini smokes and Gan direct full (Gemini 63.9% monthly in narrative — run `gan_s0_direct_full_validation_gemini31_flash_lite_20260519T101710Z` but registry `headline_metric: null`). **No GPT 5.5 rows.** Qwen 9b latency probes only. |
| **Beat paper benchmarks** on seizure frequency | **uncertain / not comparable** | Repo validation monthly ~65% vs published Real(300) Purist ~77.6–78.8% (narrative §Published benchmark distance). Different split, scorer, and data. |
| **ExECT ~paper 0.90 F1** | **misleading if cited without scope** | Repo 92.3% micro on **3 families / 40 val** ≠ ExECT paper all-field Table 1. Test holdout 77.8%. |
| **DSPy optimizer beats manual on ExECT** | **unsupported** | Optimizers Gan-only; ExECT gains from manual v4.x policies (narrative §Cross-Cutting). |
| **Evidence extraction first improves precision** (outline ablation) | **not isolated** | Evidence policy cap-25 rows exist (`gan_s0_evidence_*`) but no clean full-validation isolation in curated matrix. |
| **Schema S0 core-only** as rung | **unsupported as separate anchor** | Ladder starts at S1 in frozen anchors; S0 not a distinct full-validation row in matrix. |

### Internal source discrepancies (`stale_check`)

| Topic | Narrative (20260520) | Registry (through 20260521+) | Resolution for paper |
| --- | --- | --- | --- |
| ExECT Qwen S4 full | *pending* (methods Table 4, narrative §4.4) | Complete: `exect_s4_validation_full_qwen35b_ollama_20260520T160914Z`, micro F1 **67.5%** | Prefer registry; update narrative-derived tables |
| Synthesis bootstrap artifact | Documented in narrative | Registry: run dir **may be absent locally** | Verify `runs/gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z` before citing as primary evidence |
| Purist for synthesis | Narrative 70.1% | Registry 70.1% (0.701) | Consistent |
| ExECT S4 GPT operational default | Frozen v1.2 at `…071248Z` | Registry notes operational default moved to cause-bridge K0+K1 (2026-05-21) | **Do not** describe v1.2 as current default without checking post-freeze decision docs |
| Cap-25 vs full validation | Narrative warns cap-25 unreliable for temporal | Registry encodes same caveats on cap rows | Always label scope (cap25 / full_validation / slice / test_holdout) |

### Claims safe for paper (with caveats)

- Hybrid deterministic + LLM pipeline **works on repo synthetic benchmarks** under documented scorers.
- **Architecture > optimizer** for stable Gan benchmark-facing metrics.
- **Label policy > architecture** for ExECT S0/S1.
- **Local Qwen viable for Gan**; **task-dependent** for ExECT.
- **Schema breadth costs performance** on pooled micro F1.

---

## Open Writing Tasks

Human verification required before publication:

1. **Primary artifact audit** — Confirm `metrics.json` for every cited run ID under `runs/`; flag synthesis bootstrap if directory still missing (`experiment_registry.json` notes).
2. **Reconcile stale narrative** — Update paper tables for ExECT Qwen S4 (67.5% micro) and any post-20260520 rows (candidate-builder gap, S1 factor isolation, error-taxonomy probes) if inclusion scope expands beyond curated matrix.
3. **Published benchmark section** — Either run Gan Real(300) / full ExECT reproduction (**blocked** per narrative) or explicitly frame all results as internal synthetic evaluation (`docs/policies/published_benchmark_metrics.md`).
4. **Per-family tables** — Registry headline is micro F1 or monthly only; pull diagnosis/seizure/medication/investigation F1 from run `metrics.json` for Tables 2–4 (currently in `experiments_methods_results_20260520.md` without per-field registry headline).
5. **Statistical reporting** — Bootstrap CIs mentioned for Gan temporal vs verify-repair (methods §Analysis) but not stored as registry fields; reproduce or cite analysis script output.
6. **Stratified Gan infrequent bucket** — Document method for `gold_pragmatic=infrequent` stratification (51 records); primary numbers in narrative, not registry headline.
7. **Latency / cost** — Verify-repair and temporal paths use 2× model calls; add latency table from run metadata (non-authoritative for cache-replay runs, e.g. S3 Qwen per narrative).
8. **Model suite completeness** — Decide whether to include Gemini cap/full numbers (registry null headlines) or exclude as non-primary.
9. **Decision scope labeling** — Mark each paper table row with scope: operational (default/system), arm (comparison/replication), mechanism (ablation), vs exploratory/reject.
10. **Outline Goal 2 downstream tasks** — Either cut from Results or move to Future Work; no evidence base today.
11. **ExECT S4 cause-bridge K0+K1** — Registry notes post-v1.2 operational shift; confirm whether paper reports frozen v1.2 ladder endpoints or updated default (`experiment_registry.json` notes on `exect_s4_validation_full_gpt4_1_mini`).
12. **Authorship of interpretation** — Separate Results (registry-linked facts) from Discussion (architecture > optimizer; local-model hospital path viability).

---

*This draft is a review artifact. It does not modify repository files, scorers, registry rows, or source-of-truth documentation.*