# Paper Narrative Synthesis Draft

Review-only synthesis. Numbers below trace to `experiment_registry.json` and the 2026-05-20 narrative unless noted. This draft is **not** evidence for published benchmark superiority claims.

---

## Sources Read

| Path | Role |
| --- | --- |
| `docs/outline.md` | Research goals, model suite, architecture, ablation plan |
| `docs/experiments/synthesis/experiment_registry.json` | Canonical run IDs, headline metrics, outcomes, decision scopes (generated 2026-05-22; 185 rows) |
| `docs/archive/experiments/synthesis/pre_component_pivot/experiments_narrative_report_20260520.md` | Chronological synthesis, promotion decisions, stratified residuals |
| `docs/archive/experiments/synthesis/pre_component_pivot/experiment_registry_matrix_20260520.md` | Curated comparison groups (72 rows; generated 2026-05-21) |
| `docs/archive/experiments/synthesis/pre_component_pivot/experiments_methods_results_20260520.md` | Paper-style Methods/Results Tables 1–4 (referenced by narrative report) |

**Registry vs narrative lag:** The registry post-dates the narrative report. Notably, ExECT Qwen S4 full validation was *pending* in the narrative but is **complete** in the registry (`67.5%` micro F1). Rows dated 2026-05-22–23 (e.g. `gan_s0_candidate_builder_gap_*`) are **not** covered by the narrative report and are flagged as **open / unverified for paper use** below.

---

## Proposed Results Section Outline

### 3.1 Evaluation setup (brief cross-reference to Methods)
- Two synthetic benchmarks: Gan 2026 S0 (N=299 validation) and ExECTv2 partial field-family ladder (N=40 validation).
- Shared deterministic scorers: `gan_frequency_deterministic_v1`, `exect_*_field_family_deterministic_v1`.
- **Fact:** All headline numbers use repo splits, not Gan Real(300) or full ExECTv2 Table 1 (`experiments_narrative_report_20260520.md` §Published benchmark distance; `docs/policies/published_benchmark_metrics.md` cited therein).

### 3.2 Gan S0 — seizure-frequency extraction (narrow schema)
- **Table 1:** Full-validation architecture comparison (hosted GPT 4.1-mini and local Qwen3.6:35b).
- **3.2.1** Promoted system: temporal-candidates verify-repair v1.1 (operational defaults).
- **3.2.2** Architecture ablation arc: synthesis bootstrap → verify-repair v2 → temporal-candidates.
- **3.2.3** Local path: direct+guardrails vs temporal-candidates (+~10 pp monthly).
- **3.2.4** Negative results: GEPA, few-shot ladder, ReAct temporal tools (slice), deterministic surface replay.
- **3.2.5** Residual error mode: `gold_pragmatic=infrequent` stratification (~43–51% monthly).

### 3.3 ExECT S0/S1 — three-family monolithic extraction (broad schema, narrow scorer)
- **Table 2:** Monolithic label-policy v4.10 vs section-aware ablation; test holdout generalization.
- **3.3.1** Label-policy engineering outcome (92.3% val micro F1).
- **3.3.2** Architecture negative: section-aware cap-25 rejected.
- **3.3.3** Verification negative on ExECT S1 (verify-repair cap-25 regresses vs single-pass).

### 3.4 ExECT schema ladder S1→S4 — breadth cost (GPT frozen anchors)
- **Table 3:** Micro F1 by schema level (3 / 5 / 9 / 11 families); per-family callouts (seizure frequency, investigation, comorbidity).
- **Caveat paragraph:** Cross-level micro F1 is **not** a single learning curve (different family sets).

### 3.5 Model-track replication (Qwen3.6:35b, selected Gemini)
- **Table 4:** GPT frozen prompts vs Qwen on Gan and ExECT ladder.
- Gan: parity under temporal-candidates.
- ExECT: Qwen matches/exceeds GPT on S2–S4 pooled micro; lags on S0/S1 seizure-type granularity.

### 3.6 Hybrid deterministic placement (mechanism-oriented subset)
- Gan: H2/H4 pre-conditioning (temporal candidates) beats H3 tool-during ReAct on hard slice.
- ExECT: D1→L0→L1→L1+policy ladder; H1 post-bridge vs H2 pre-vocab interleaving probes.
- **Interpretation (not primary metric):** Gains on Gan from deterministic temporal scaffolding; gains on ExECT from manual label policy + bridges, not optimizers.

### 3.7 Limitations subsection (mirror `experiments_methods_results_20260520.md` §Limitations)
- Synthetic splits, small ExECT N, cap-25 non-predictiveness for Gan temporal path, verify-repair call-count confound.

---

## Key Paper Claims Map

Each row: **claim → run ID → metrics → rationale**. Decision scopes from registry `notes` are preserved.

---

### Claim 1 — Promoted Gan S0 system reaches ~65% monthly frequency with strong category/evidence metrics (hosted)

| Field | Value |
| --- | --- |
| **Claim statement** | Temporal-candidates verify-repair v1.1 is the operational hosted Gan S0 default; it ties prior verify-repair on monthly accuracy while improving Purist, Pragmatic, schema validity, and evidence support. |
| **Supporting run ID** | `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z` |
| **Experiment ID** | `gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini` → superseded; compare to `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails` |
| **Supporting metrics** | Monthly **65.1%**; Purist **76.5%**; Pragmatic **84.2%**; schema valid **99.7%**; evidence support **100%** (N=299, `gan_2026_fixed_v1:validation`) |
| **Rationale** | Validates architecture claim under fixed scorer. Monthly −0.3 pp vs verify-repair v2 (65.4%) is within pre-registered 1 pp gate; category/evidence gains drove promotion (`experiments_narrative_report_20260520.md` §2.5; registry outcome: **promote**, decision_scope: **operational**). |
| **Uncertainty** | Bootstrap CIs on monthly overlapped verify-repair v2 — **tie**, not proven superiority on primary label (`experiments_methods_results_20260520.md` R1). |

---

### Claim 2 — Local Qwen3.6:35b matches hosted GPT on Gan under the same program

| Field | Value |
| --- | --- |
| **Claim statement** | Local Qwen achieves hosted-parity monthly frequency with the promoted temporal-candidates program. |
| **Supporting run ID** | `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T230324Z` |
| **Supporting metrics** | Monthly **65.8%**; Purist **75.5%**; Pragmatic **82.6%**; schema **99.7%**; evidence **100%** |
| **Rationale** | Same program/scorer/split as Claim 1; supports outline objective on local-model viability for the narrow temporal task (registry: **promote**, decision_scope: **operational**). Direct baseline without temporal scaffolding: `gan_s0_qwen35b_direct_full_validation_guardrails_20260519T102249Z` at **55.9%** monthly — architecture delta **+9.9 pp**. |
| **Caveat** | Latency and hardware residency not in registry headline metrics; verify-repair doubles model calls. |

---

### Claim 3 — Verify-repair and synthesis establish an architecture improvement arc on Gan (hosted)

| Field | Value |
| --- | --- |
| **Claim statement** | Moving from synthesis bootstrap → verify-repair v2 → temporal-candidates improves or preserves monthly accuracy while strengthening auxiliary metrics. |
| **Supporting run IDs** | (1) `gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z` — (2) `gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z` — (3) Claim 1 run |
| **Supporting metrics** | Synthesis: monthly **62.9%**, Purist **70.1%**, Pragmatic **73.9%**, evidence **89.9%**. Verify-repair v2: monthly **65.4%**, Purist **72.7%**, Pragmatic **79.2%**, evidence **92.7%**. Temporal: see Claim 1. |
| **Rationale** | Ordered comparison within `gan_s0_architecture_gpt_validation_v1` (matrix §gan_s0_architecture_gpt_validation_v1). decision_scope: **arm** for synthesis and verify-repair (superseded references). |
| **Uncertainty** | Synthesis run artifact **may be absent locally** (registry metric_caveats: "documented in research docs… not present in the current local runs folder"). Re-verify from `runs/` before citation. |

---

### Claim 4 — Deterministic temporal pre-conditioning beats tool-during ReAct on hard Gan slice (mechanism)

| Field | Value |
| --- | --- |
| **Claim statement** | H2/H4 deterministic temporal candidates outperform H3 interleaved ReAct tools on the 14-record regression slice. |
| **Supporting run IDs** | Positive: `gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_guardrails_20260519T232514Z` (matrix: **100%** monthly, N=14). Negative: `gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails_20260520T173943Z` |
| **Supporting metrics** | ReAct: monthly **42.9%** (on valid preds); schema valid **50%**; 7/14 schema-invalid. Temporal B1 slice: **100%** monthly (matrix; slice scope). |
| **Rationale** | Supports outline ablation on deterministic vs LLM placement; registry outcome **reject** for ReAct, decision_scope: **arm**. **Do not extrapolate slice to full validation** (registry metric_caveats). |
| **Comparison group** | `gan_s0_hard_slice_qwen_architecture_v1` |

---

### Claim 5 — ExECT monolithic label policy v4.10 reaches 92.3% micro F1 on three audited families (hosted)

| Field | Value |
| --- | --- |
| **Claim statement** | Manual label-policy engineering on monolithic single-pass extraction yields a frozen S0/S1 validation anchor for diagnosis, seizure type, and annotated medication. |
| **Supporting run ID** | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` |
| **Supporting metrics** | Micro F1 **92.3%** (registry secondary from methods doc: diagnosis **93.8%**, seizure-type **90.5%**, medication **92.8%**) |
| **Rationale** | Frozen operational anchor (registry outcome: **freeze**, decision_scope: **operational**). Confirms broad-schema *partial* extraction strength under repo scorer — **not** full ExECTv2 paper reproduction. |
| **Generalization caveat** | Test holdout: `exect_s0_s1_validation_test_gpt4_1_mini_20260519T222615Z` — micro F1 **77.8%** (−14.5 pp vs validation); decision_scope: **arm**, one-shot holdout. |

---

### Claim 6 — Section-aware ExECT extraction regresses vs monolithic (architecture ablation)

| Field | Value |
| --- | --- |
| **Claim statement** | Section selection + thin family prompts hurt S0/S1 extraction vs monolithic full-note pass. |
| **Supporting run ID** | `exect_s0_s1_section_aware_cap25_gpt4_1_mini_20260518T174714Z` |
| **Supporting metrics** | Micro F1 **65.6%** (cap-25, N=25) vs early monolithic cap-25 **73.7%** (narrative §3.1; early policy, not v4.10) |
| **Rationale** | Registry outcome **reject**, decision_scope: **arm**. Cap-25 only — directional. Narrative reports diagnosis F1 −15.6 pp and evidence −16.6 pp vs monolithic at same cap (`experiments_narrative_report_20260520.md` §3.1). |
| **Uncertainty** | No full-validation section-aware run in registry; claim scope must stay cap-25. |

---

### Claim 7 — Schema breadth reduces pooled micro F1 on ExECT (GPT ladder)

| Field | Value |
| --- | --- |
| **Claim statement** | Adding field families monotonically lowers pooled micro F1 under versioned label policies (breadth cost). |
| **Supporting run IDs** | S1: `…221944Z` **92.3%** — S2: `exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` **80.9%** — S3: `exect_s3_validation_full_gpt4_1_mini_20260519T235439Z` **72.1%** — S4: `exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` **65.5%** |
| **Supporting metrics** | Micro F1 as above (3 / 5 / 9 / 11 families respectively). S4 per-family (narrative): seizure-frequency F1 **45.7%**, investigation **96.7%**, medication temporality **62.5%**. |
| **Rationale** | Comparison group `exect_schema_complexity_gpt_validation_v1`; all **freeze**, decision_scope: **operational**. Trend supports outline §Schema breadth parameter — with mandatory caveat that family sets differ. |
| **Interpretation limit** | Registry and matrix explicitly forbid treating this as a single calibrated learning curve. |

---

### Claim 8 — Qwen replicates ExECT frozen prompts with task-dependent gaps vs GPT

| Field | Value |
| --- | --- |
| **Claim statement** | Qwen3.6:35b tracks GPT on S2–S4 micro F1 but trails on S0/S1, driven by seizure-type granularity collapse. |
| **Supporting run IDs** | S1: `exect_s0_s1_validation_full_qwen35b_ollama_20260520T042117Z` — S2: `…073552Z` — S3: `…092244Z` — S4: `exect_s4_validation_full_qwen35b_ollama_20260520T160914Z` |
| **Supporting metrics** | S1 micro **79.0%** (GPT **92.3%**, Δ −13.3 pp). S2 **82.6%** (+1.7 pp). S3 **72.2%** (+0.1 pp). S4 **67.5%** (+2.0 pp vs GPT 65.5%; matrix + registry). |
| **Rationale** | Comparison group `exect_qwen_replication_validation_v1`; decision_scope: **arm** (held, not frozen default). Narrative: diagnosis F1 Qwen **95.1%** vs GPT **93.8%**, seizure-type **55.7%** vs **90.5%** on S1 (`experiments_narrative_report_20260520.md` §3.3). |
| **Uncertainty** | Registry notes S4 Qwen "+2.0 pp pooled micro" but **per-family profile diverges** — inspection doc required before claiming S4 parity (`exect_s4_validation_full_qwen35b_ollama_inspection_20260520.md`). |

---

### Claim 9 — Hybrid placement ladder on ExECT S1: policy bridges dominate over raw LLM or deterministic-only floors

| Field | Value |
| --- | --- |
| **Claim statement** | On ExECT S1, L1+label policy reaches production ceiling; D1 deterministic-only and L0 bare LLM are far below; optimizers do not beat baseline on cap-25. |
| **Supporting run IDs** | D1 cap-25: `exect_s1_full_ladder_d1_cap25_gpt4_1_mini_20260521T003704Z` — L0 cap-25: `…003707Z` — L1 cap-25: `…003924Z` — L1+policy full: `exect_s1_full_ladder_l1_policy_full_gpt4_1_mini_20260521T004209Z` — Optimizer reject: `exect_s1_optimizer_bootstrap_cap25` micro **90.7%** vs baseline **95.8%** (matrix §exect_s1_optimizer_gpt_cap25_v1) |
| **Supporting metrics** | D1 **58.4%**, L0 **60.0%**, L1 **67.7%**, L1+policy full **92.3%** micro F1 |
| **Rationale** | Supports outline Claim 4 (deterministic + LLM mix) and ablation on normalization/policy vs raw extraction. decision_scope: **arm** for ladder rungs; **operational** for L1+policy full match to frozen anchor. |
| **Scope** | Ladder cap-25 rungs are exploratory; only L1+policy full is N=40 validation. |

---

### Claim 10 — Pre-vocab deterministic interleaving (H2) regresses vs post-bridge (H1) on ExECT S1 full validation

| Field | Value |
| --- | --- |
| **Claim statement** | Injecting pre-vocab deterministic constraints before LLM extraction hurts full-validation micro F1 relative to post-bridge H1 at matched policy. |
| **Supporting run IDs** | H1 full: `exect_s1_interleaving_h1_post_bridge` → `…221944Z` equivalent **92.3%** (matrix). H2 full: `exect_s1_interleaving_h2_pre_vocab` → **87.5%** micro (matrix §exect_s1_interleaving_gpt_validation_v1, outcome **reject**) |
| **Rationale** | Mechanism-oriented arm comparison (`decision_scope: arm` in matrix rows). Supports "where to place determinism" finding distinct from Gan (pre-conditioning helps Gan temporal, hurts ExECT pre-vocab in this probe). |
| **Uncertainty** | Full run IDs for interleaving v1 rows need confirmation from registry artifact_paths before publication — matrix lists experiment IDs; human should copy exact canonical_run_id from registry. |

---

### Claim 11 — GEPA and few-shot optimizers do not beat manual engineering at Gan full-validation scale

| Field | Value |
| --- | --- |
| **Claim statement** | DSPy GEPA and cap-25 few-shot ladders fail to exceed synthesis/temporal full-validation monthly accuracy. |
| **Supporting run IDs** | GEPA cap-5: `gan_s0_gepa_direct_cap5_gpt4_1_mini_20260519T054057Z` (exploratory; headline_metric null in registry). Few-shot ladder: e.g. `gan_s0_ladder_bootstrap_cap25_gpt4_1_mini_20260519T092020Z` |
| **Supporting metrics** | Narrative: best ladder cap-25 monthly ~**52%** (Gemini direct); GEPA improved schema/evidence on cap-5 but not stable labels (`experiments_narrative_report_20260520.md` §2.3). Full-validation ceiling remains **~65%** (Claims 1–3). |
| **Rationale** | Supports outline ablation on optimizers vs manual guidance. decision_scope: **arm**, outcomes **exploratory** / deprioritized. |
| **Gap** | Many ladder rows have `headline_metric: null` in registry — cap-25 numbers come from narrative, not registry primary field. |

---

### Claim 12 — Gemini 3.1 Flash Lite is a competitive hosted alternative on Gan (not promoted default)

| Field | Value |
| --- | --- |
| **Claim statement** | Gemini 3.1 Flash Lite direct extraction approaches GPT full-validation monthly on Gan. |
| **Supporting run ID** | `gan_s0_direct_full_validation_gemini31_flash_lite_20260519T101710Z` |
| **Supporting metrics** | Narrative: monthly **63.9%** (registry row has `headline_metric: null` — **stale_check needed**) |
| **Rationale** | Supports partial model-suite comparison from outline; not operational default. |
| **Uncertainty** | Registry headline backfill incomplete; verify from `runs/.../metrics.json`. |

---

### Claim 13 — Residual Gan failure mode: infrequent quantified frequencies

| Field | Value |
| --- | --- |
| **Claim statement** | After promotion, both hosted and local full runs share weak performance on `gold_pragmatic=infrequent`. |
| **Supporting run IDs** | Claims 1 and 2 runs |
| **Supporting metrics** | Narrative: **43.1%** (hosted) to **51.0%** (local) monthly on ~51 infrequent records vs **62.9%** frequent and **98.2%** no_seizure_information (`experiments_narrative_report_20260520.md` §2.5) |
| **Rationale** | Stratified fact from error analysis docs cited in narrative; **not** a standalone registry headline_metric — primary artifacts are analyzer outputs / inspection docs. |
| **Decision scope** | **open** (primary residual error bucket; bounded ReAct probe rejected on slice). |

---

## Discrepancies Or Unsupported Claims

### Claims in `docs/outline.md` without registry/narrative backing

| Outline claim | Status | Notes |
| --- | --- | --- |
| **Beat ExECTv2 and Gan paper benchmarks** | **blocked** | Narrative §Executive Summary: no published Real(300) or full CUI-aware ExECT Table 1 reproduction. Repo Gan ~65% monthly vs published Purist micro-F1 ~0.78–0.79 (indicative only). |
| **Downstream adaptation** (billing, cohort selection, outcome variables) | **unsupported** | No experiment rows; outline aspiration only. |
| **GPT 5.5 evaluation** | **unsupported** | Listed in outline model suite; no runs in registry or matrix through 2026-05-22. |
| **Qwen3.5:9b as primary local model** | **partial / weak** | Smoke and latency probes only; 35b is operational local default. |
| **Gemini 3 Flash** (outline) vs **Gemini 3.1 Flash Lite** (experiments) | **naming mismatch** | Registry adds `exect_s0_s1_validation_full_gemini3_flash` (2026-05-22) post-narrative — verify before paper model table. |
| **Comprehensive ablation battery** (few-shot per field, negation, temporality, guidelines sensitivity) | **partial** | Gan architecture + ExECT ladder/interleaving covered; many outline ablations not run. |
| **DSPy optimizer-driven ExECT improvement** | **negative / blocked** | Optimizers Gan-only in runner; ExECT gains from manual policy (`experiments_narrative_report_20260520.md` §Cross-Cutting). |

### Internal inconsistencies to resolve before publication

| Issue | Sources |
| --- | --- |
| Narrative Table 4 lists ExECT S4 Qwen as *pending*; registry/matrix report **67.5%** micro F1 | Narrative §4.4 vs `experiment_registry_matrix_20260520.md` §exect_qwen_replication_validation_v1 |
| Registry notes ExECT S4 GPT operational default **moved to cause-bridge K0+K1** (2026-05-21) while frozen anchor remains v1.2 L1 single-pass | `experiment_registry.json` row `exect_s4_validation_full_gpt4_1_mini` notes |
| Synthesis bootstrap run metrics documented but artifact **may be missing locally** | Registry `gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini` metric_caveats |
| Cap-25 Gan monthly (**44%**) poorly predicts full-validation (**~65%**) for temporal path | Narrative §2.5; registry promotion gate docs |
| Post-202605-20 registry rows (candidate-builder-gap, error-taxonomy policy slices, Gemini 3 Flash suite) lack narrative synthesis | Registry rows dated 20260522–23 — **stale_check** vs preregistration docs before paper inclusion |

### Claims safe for paper (with caveats) vs interpretive only

| Safe (point to primary run + scorer) | Interpretive / requires human review |
| --- | --- |
| Headline metrics in Claims 1–3, 5, 7–9 | "Beats prior art" or "hospital-ready" |
| Freeze/promote outcomes with decision_scope **operational** | Cross-level ExECT micro F1 as smooth degradation curve |
| Negative results: section-aware, ReAct, GEPA deprioritization | Qwen S4 "+2 pp" as holistic parity without per-family table |
| Test holdout 77.8% as generalization fact | Infrequent-bucket percentages without citing analyzer script output |

---

## Open Writing Tasks

1. **Methods parity:** Copy split sizes, scorer definitions, and program variant table from `experiments_methods_results_20260520.md`; align model names with actual configs (`gpt4_1_mini`, `qwen35b`, `gemini31_flash_lite`).

2. **Primary artifact verification:** For every cited run, confirm `runs/<canonical_run_id>/metrics.json` exists (especially synthesis bootstrap and Gemini full-validation rows with null registry headlines).

3. **Table 1 (Gan full-validation):** Build from Claims 1–3; include call-count footnote for verify-repair/temporal variants.

4. **Table 2 (ExECT S0/S1):** Include validation, test holdout, section-aware cap-25; add per-family F1 columns from frozen anchor inspection doc.

5. **Table 3 (Schema ladder):** Four GPT freeze rows + footnote on non-comparable micro F1; add per-family rows for S4 seizure frequency (45.7%) from `exect_s4_validation_full_v1_2_gpt4_1_mini_inspection_20260520.md`.

6. **Table 4 (Model replication):** Update S4 Qwen from *pending* to **67.5%** with per-family caveat from `exect_s4_validation_full_qwen35b_ollama_inspection_20260520.md`.

7. **Mechanism subsection:** Separate Gan (pre-conditioning helps) from ExECT (post-bridge helps; pre-vocab H2 hurts) — do not merge into one "determinism helps" claim. Tag decision_scope: **mechanism** explicitly in prose where interleaving/ladder rows apply.

8. **Published benchmark distance paragraph:** Mandatory near Results opening; cite `docs/policies/published_benchmark_metrics.md` — state repo results are **internal synthetic evaluation**.

9. **Stratified Gan error analysis:** Pull infrequent-bucket table from promotion decision doc / analyzer markdown; not in registry headline fields.

10. **Decide S4 GPT anchor for paper:** Historical v1.2 (`…071248Z`, 65.5%) vs post-202605-21 cause-bridge K0+K1 default — registry says operational default moved; paper must pick one anchor and document.

11. **Post-narrative experiments:** Human review of 20260522–23 Gan policy slices (`gan_s0_candidate_builder_gap_*`, constrained verifier, targeted examples) before inclusion — outside narrative report scope.

12. **Confidence intervals:** Narrative mentions bootstrap CIs for Gan monthly tie; locate primary CI artifact or recompute before claiming statistical equivalence.

13. **Limitations:** ExECT N=40, cap-25 optimism (~+3.5 pp on S1), evidence metric confound (program-enforced quotes), optimizer train-split leakage controls.

14. **Outline goal 1 rewrite:** Reframe from "beat benchmarks" to "establish repo baselines under deterministic scorers aligned with audit policies" unless/until Real(300) and CUI-aware ExECT runs complete (**blocked** workstream).

---

*Draft produced under review-only workflow. No repository files were modified. Treat all interpretive conclusions as hypotheses until tied to inspected `runs/` artifacts and frozen decision docs cited in the registry.*