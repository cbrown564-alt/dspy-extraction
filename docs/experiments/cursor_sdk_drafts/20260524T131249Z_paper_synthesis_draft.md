# Paper Narrative Synthesis Draft

**Status:** Review-only synthesis. No files edited. Metrics below are registry-sourced unless noted; per-family breakdowns cite narrative reports that point to `runs/<run_id>/metrics.json`.

**Registry freshness note:** `experiment_registry.json` was generated **2026-05-22** and includes rows **after** the 2026-05-20 narrative (e.g., `gan_s0_candidate_builder_gap_v1_*`). Those newer rows are tagged **`decision_scope: arm`** and are **not** operational defaults unless separately promoted.

---

## Sources Read

| Path | Role |
| --- | --- |
| `docs/outline.md` | Research goals, architecture, ablation plan, model suite intent |
| `docs/experiments/synthesis/experiment_registry.json` | Canonical run IDs, headline metrics, outcomes, decision scopes (204 rows) |
| `docs/archive/experiments/synthesis/pre_component_pivot/experiments_narrative_report_20260520.md` | Phase narrative, stratified residuals, per-family F1, promotion gates |
| `docs/archive/experiments/synthesis/pre_component_pivot/experiment_registry_matrix_20260520.md` | Curated comparison groups (72 rows), matrix caveats |
| `docs/archive/experiments/synthesis/pre_component_pivot/experiments_methods_results_20260520.md` | Paper-style Methods/Results tables R1–R6 (referenced by narrative report) |

---

## Proposed Results Section Outline

### §4.1 Evaluation setup (brief cross-reference to Methods)
- Two synthetic benchmarks: **Gan 2026 S0** (N=299 validation) and **ExECTv2 partial ladder** (N=40 validation).
- Shared deterministic scorers: `gan_frequency_deterministic_v1`, `exect_*_field_family_deterministic_v1`.
- **Fact:** No published Real(300) or CUI-aware Table 1 reproduction (`docs/policies/published_benchmark_metrics.md`; registry caveats on every anchor row).
- **Decision scope:** `blocked` for external benchmark claims.

### §4.2 Gan S0 — seizure frequency (narrow, temporal task)
- **Table 1:** Full-validation architecture ladder (hosted GPT + local Qwen).
- **§4.2.1** Verify-repair and temporal-candidates vs direct extraction.
- **§4.2.2** Optimizer negative results (GEPA, few-shot ladder, semantic bootstrap).
- **§4.2.3** Residual error analysis: `gold_pragmatic=infrequent` bucket (~43–51% monthly; narrative §2.5, runs cited below).
- **§4.2.4** Post-2026-05-20 arm results (candidate-builder gap v1) — **stale_check** vs operational defaults.

### §4.3 ExECT S0/S1 — three-family monolithic baseline
- **Table 2:** Frozen v4.10 validation vs test holdout vs section-aware ablation.
- **§4.3.1** Label-policy engineering gains (v3→v4.10); manual policy, not optimizer.
- **§4.3.2** Hybrid interleaving matrix (H1 post-bridge vs H2 pre-vocab vs L1 raw).

### §4.4 ExECT schema ladder S1→S4 — breadth cost
- **Table 3:** Micro F1 at each schema level (different family sets — not a single learning curve).
- Per-family weaknesses at S4 (seizure frequency, comorbidity, medication temporality).

### §4.5 Local Qwen3.6:35b replication
- **Table 4:** GPT frozen prompts vs Qwen on same splits through S4.
- Task-dependent local viability: strong on Gan temporal path; mixed on ExECT S0/S1 (diagnosis ↑, seizure-type ↓).

### §4.6 Negative and inconclusive findings (summary table)
- Section-aware ExECT, GEPA, deterministic post-repair, ReAct temporal tools, cap-25 predictiveness.

### §4.7 Limitations
- Synthetic splits, small ExECT N, call-count confounds on verify-repair, evidence as diagnostic not human audit.

---

## Key Paper Claims Map

Each row maps an outline-level claim to a **primary run ID** and **registry headline metric**. Decision scopes preserved.

---

### Claim 1 — Hybrid temporal-candidates verify-repair is the best **operational** Gan S0 architecture on repo validation

| Field | Value |
| --- | --- |
| **Claim statement** | Deterministic temporal candidate hints + verify-repair v1.1 achieves ~65% monthly frequency accuracy with near-perfect schema validity and evidence support on Gan synthetic validation (N=299), matching or slightly beating prior verify-repair while improving category and evidence metrics. |
| **Supporting run ID (hosted, operational)** | `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z` |
| **Supporting metrics** | Monthly **65.1%**; Purist **76.5%**; Pragmatic **84.2%**; schema valid **99.7%**; evidence **100.0%** |
| **Supporting run ID (local, operational)** | `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T230324Z` |
| **Supporting metrics** | Monthly **65.8%**; Purist **75.5%**; Pragmatic **82.6%**; schema valid **99.7%**; evidence **100.0%** |
| **Rationale** | Both rows are `outcome: promote`, `decision_scope: operational` in registry (`experiment_id`: `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails`, `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails`). Hosted monthly ties verify-repair v2 (−0.3 pp, within 1 pp gate per narrative); evidence +7.3 pp vs verify-repair v2. **Caveat:** Not published Gan Real(300) reproduction; verify-repair doubles model calls. |
| **Primary artifacts** | `runs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z/metrics.json`; decision doc: `docs/experiments/gan/gan_s0_gpt4_1_mini_temporal_candidates_full_validation_decision_20260520.md` |

---

### Claim 2 — Verify-repair improves Gan labels over synthesis bootstrap but is superseded by temporal-candidates

| Field | Value |
| --- | --- |
| **Claim statement** | Extract→verify→repair v2 raised monthly accuracy and evidence over synthesis CoT+bootstrap on the same split, before temporal-candidates v1.1 became default. |
| **Supporting run ID (verify-repair v2)** | `gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z` |
| **Supporting metrics** | Monthly **65.4%**; Purist **72.7%**; Pragmatic **79.2%**; evidence **92.7%**; schema **96.7%** |
| **Supporting run ID (synthesis bootstrap)** | `gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z` |
| **Supporting metrics** | Monthly **62.9%**; Purist **70.1%**; Pragmatic **73.9%**; evidence **89.9%**; schema **97.3%** |
| **Rationale** | Registry comparison group `gan_s0_architecture_gpt_validation_v1`. Verify-repair is `outcome: superseded`; synthesis is `outcome: superseded`. Verify-repair +2.5 pp monthly vs synthesis. **Caveat:** Synthesis run directory noted as potentially absent locally (`metric_caveats` in registry); metrics bridged from decision docs. |
| **Decision scope** | `arm` (architecture comparison) |

---

### Claim 3 — Temporal scaffolding closes the local Qwen gap vs direct extraction on Gan

| Field | Value |
| --- | --- |
| **Claim statement** | Local Qwen3.6:35b direct extraction (~56% monthly) is materially weaker than temporal-candidates verify-repair (~66%) on the same validation split. |
| **Supporting run ID (direct baseline)** | `gan_s0_qwen35b_direct_full_validation_guardrails_20260519T102249Z` |
| **Supporting metrics** | Monthly **55.9%**; Purist **61.9%**; Pragmatic **70.5%**; evidence **99.6%** |
| **Supporting run ID (temporal v1.1)** | `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T230324Z` |
| **Supporting metrics** | Monthly **65.8%** (+9.9 pp) |
| **Rationale** | Registry group `gan_s0_architecture_qwen_validation_v1`. Direct is `outcome: exploratory`; temporal is `outcome: promote`. Interpretation: deterministic pre-conditioning + verify-repair addresses semantic temporal errors guardrails alone cannot fix (narrative §2.4–2.5). |
| **Decision scope** | `mechanism` (H2_pre_deterministic + H4_deterministic_first_llm_adjudicates) |

---

### Claim 4 — Post-2026-05-20 candidate-builder gap v1 shows higher Gan monthly accuracy (arm only)

| Field | Value |
| --- | --- |
| **Claim statement** | An enriched temporal-candidates single-pass variant with candidate-builder gap fixes reached **80.6%** monthly on full validation — substantially above operational temporal v1.1 (~65%). |
| **Supporting run ID** | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` |
| **Supporting metrics** | Monthly **80.6%**; Purist **86.0%**; Pragmatic **88.6%**; schema **100%**; evidence **100%** |
| **Supporting run ID (Qwen transfer, arm)** | `gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z` |
| **Supporting metrics** | Monthly **70.7%**; Purist **83.2%**; Pragmatic **90.6%** |
| **Rationale** | Registry `outcome: promote` (GPT) / `hold` (Qwen) but **`decision_scope: arm`** — explicitly **not** operational default per registry notes. **stale_check:** Absent from 2026-05-20 narrative/matrix; human must decide promotion before citing as headline result. |
| **Primary artifacts** | `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z/metrics.json`; `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_full_validation_rerun_inspection_20260523.md` |

---

### Claim 5 — ExECT monolithic label policy v4.10 reaches high micro F1 on three audited families (validation)

| Field | Value |
| --- | --- |
| **Claim statement** | Iterative manual label-policy engineering on monolithic single-pass extraction yields **92.3%** micro F1 on diagnosis + seizure type + medication (N=40 validation). |
| **Supporting run ID** | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` |
| **Supporting metrics** | Micro F1 **92.3%** (per-family: diagnosis **93.8%**, seizure **90.5%**, medication **92.8%** — from narrative Table 2 → `runs/.../metrics.json`) |
| **Rationale** | Registry `outcome: freeze`, `decision_scope: operational`. Scorer covers 3 families only — **not** full ExECTv2 paper Table 1. Cap-25 (95.8%) systematically optimistic (+3.5 pp). |
| **Primary artifacts** | `docs/experiments/exect/exect_s0_label_policy_v4_10_implementation.md` |

---

### Claim 6 — Validation-to-test generalization gap on ExECT S0/S1

| Field | Value |
| --- | --- |
| **Claim statement** | Frozen v4.10 policy generalizes to held-out test split with a **−14.5 pp** micro F1 drop. |
| **Supporting run ID (validation)** | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` → **92.3%** |
| **Supporting run ID (test holdout)** | `exect_s0_s1_validation_test_gpt4_1_mini_20260519T222615Z` → **77.8%** |
| **Rationale** | Registry group `exect_s1_generalization_gpt_test_v1`; `decision_scope: arm`. One-shot test — no tuning allowed. Seizure-type F1 drops most (90.5% → 66.0% per narrative). |
| **Uncertainty** | N=40 per split; no bootstrap CIs in registry. |

---

### Claim 7 — Section-aware extraction **regresses** vs monolithic ExECT S0/S1

| Field | Value |
| --- | --- |
| **Claim statement** | Deterministic section selection + per-family thin prompts hurt micro F1 and evidence support vs monolithic baseline. |
| **Supporting run ID (section-aware, reject)** | `exect_s0_s1_section_aware_cap25_gpt4_1_mini_20260518T174714Z` |
| **Supporting metrics** | Micro F1 **65.6%** (cap-25, N=25) |
| **Comparator (monolithic cap-25)** | `exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T221936Z` → micro F1 **95.8%** (registry matrix; cap optimistic) |
| **Early monolithic baseline (narrative)** | `exect_s0_s1_validation_cap25_gpt4_1_mini_20260518T172431Z` → **73.7%** micro F1 (early policy v3) |
| **Rationale** | Registry `outcome: reject`, `decision_scope: arm`. Diagnosis F1 −15.6 pp vs early monolithic; evidence −16.6 pp (narrative §3.1). **Caveat:** Cap-25 only; directionally consistent with full-validation policy arc. |
| **Primary artifacts** | `docs/experiments/exect/exect_section_aware_cap25_inspection.md` |

---

### Claim 8 — Schema breadth increases task difficulty (ExECT S1→S4 ladder)

| Field | Value |
| --- | --- |
| **Claim statement** | As field families expand, pooled micro F1 falls predictably; S4 weakest families include seizure frequency and medication temporality. |
| **Supporting run IDs & metrics (GPT, frozen, N=40 each)** | |
| S0/S1 (3 fam) | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` → **92.3%** |
| S2 (5 fam) | `exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` → **80.9%** |
| S3 (9 fam) | `exect_s3_validation_full_gpt4_1_mini_20260519T235439Z` → **72.1%** |
| S4 (11 fam) | `exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` → **65.5%** |
| **Per-family (S4, narrative → metrics.json)** | Seizure frequency F1 **45.7%**; investigation **96.7%**; medication temporality **62.5%** |
| **Rationale** | Registry group `exect_schema_complexity_gpt_validation_v1`; all `outcome: freeze`. **Critical caveat:** Micro F1 aggregates **different family sets** — describe as breadth cost, not a calibrated single metric trajectory (`metric_caveats`). |
| **Decision scope** | `mechanism` (schema_complexity varied factor) |

---

### Claim 9 — Local Qwen matches GPT on broader ExECT schemas but lags on S0/S1 seizure-type granularity

| Field | Value |
| --- | --- |
| **Claim statement** | Qwen replication with frozen GPT prompts tracks within ~2 pp at S2–S4 micro F1 but drops **−13.3 pp** at S0/S1, driven by seizure-type collapse. |
| **Supporting run IDs** | |
| S0/S1 GPT / Qwen | `…221944Z` **92.3%** / `exect_s0_s1_validation_full_qwen35b_ollama_20260520T042117Z` **79.0%** |
| S2 | `…231223Z` **80.9%** / `exect_s2_validation_full_qwen35b_ollama_20260520T073552Z` **82.6%** (+1.7 pp) |
| S3 | `…235439Z` **72.1%** / `exect_s3_validation_full_qwen35b_ollama_20260520T092244Z` **72.2%** (+0.1 pp) |
| S4 | `…071248Z` **65.5%** / `exect_s4_validation_full_qwen35b_ollama_20260520T160914Z` **67.5%** (+2.0 pp) |
| **Per-family (S0/S1, narrative)** | Qwen diagnosis **95.1%** vs GPT **93.8%**; seizure-type **55.7%** vs **90.5%** |
| **Rationale** | Registry group `exect_qwen_replication_validation_v1`; all Qwen rows `outcome: hold`, `decision_scope: arm`. S4 Qwen +2.0 pp pooled micro but per-family profile diverges (registry note). **stale_check:** Narrative listed S4 Qwen as pending; registry has completed run. |
| **Uncertainty** | Qwen test holdout not run (deferred per narrative). |

---

### Claim 10 — Post-hoc deterministic bridges match frozen L1 on ExECT S1 full validation; pre-vocab injection regresses

| Field | Value |
| --- | --- |
| **Claim statement** | H1 post-deterministic bridges are a null intervention at full validation (same labels as L1); H2 pre-vocab filtering hurts micro F1. |
| **Supporting run ID (H1 post-bridge, hold)** | `exect_s1_interleaving_h1_post_bridge_gpt4_1_mini_20260520T185747Z` → micro F1 **92.3%** (identical to frozen L1) |
| **Supporting run ID (H2 pre-vocab, reject)** | `exect_s1_interleaving_h2_pre_vocab_gpt4_1_mini_20260520T185755Z` → micro F1 **87.5%** (−4.8 pp) |
| **Supporting run ID (L1 raw no bridges, exploratory)** | `exect_s1_interleaving_l1_raw_no_bridges_gpt4_1_mini_*` → micro F1 **68.6%** (full; matrix) |
| **Rationale** | Registry group `exect_s1_interleaving_gpt_validation_v1`. Bridges are part of v4.10 frozen policy — isolating bridge contribution requires raw-no-bridge ablation. Pre-vocab rejected at family slices too (medication, seizure). |
| **Decision scope** | `mechanism` (interleaving_position) |

---

### Claim 11 — DSPy optimizers (GEPA, BootstrapFewShot on ExECT) do not beat manual label policy

| Field | Value |
| --- | --- |
| **Claim statement** | GEPA and ExECT BootstrapFewShot cap-25 runs underperform frozen manual v4.10 baseline. |
| **Supporting run ID (GEPA cap-5, reject)** | `gan_s0_gepa_direct_cap5_gpt4_1_mini_20260519T054057Z` |
| **Supporting run ID (ExECT bootstrap cap-25, reject)** | `exect_s1_optimizer_bootstrap_cap25` → micro F1 **90.7%** vs baseline **95.8%** (matrix) |
| **Rationale** | GEPA improved schema/evidence on cap-5 but not stable labels; Qwen GEPA produced prompt bloat (narrative §2.3). ExECT optimizer gate never implemented at full validation (runner Gan-only). |
| **Decision scope** | `arm` / `reject` |

---

### Claim 12 — Deterministic post-classifier for medication temporality fails full-validation guard

| Field | Value |
| --- | --- |
| **Claim statement** | H1 post-deterministic medication temporality classifier improves cap-25 precision but collapses recall at full validation. |
| **Supporting run ID (L1 baseline full)** | `exect_s4_temporality_l1_baseline_full_gpt4_1_mini_*` → MT precision **46.4%** (matrix) |
| **Supporting run ID (H1 post-classifier full, reject)** | `exect_s4_temporality_h1_post_classifier_full_gpt4_1_mini_20260520T204216Z` → MT precision **56.5%** but −6.6 pp MT F1 |
| **Rationale** | Registry group `exect_s4_temporality_deterministic_v1`; `outcome: reject`. Supports outline ablation question "Is normalisation more effective in LLM or deterministic harness?" — **deterministic post-hoc alone insufficient** for this field. |
| **Decision scope** | `mechanism` |

---

### Claim 13 — ReAct temporal tools do not beat temporal-candidates on hard slice

| Field | Value |
| --- | --- |
| **Claim statement** | Tool-assisted temporal reasoning underperforms temporal-candidates on the 14-record regression slice. |
| **Supporting run ID (ReAct, reject)** | `gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails_20260520T173943Z` → monthly **42.9%** |
| **Comparator (temporal-candidates slice)** | `gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_guardrails_20260519T232514Z` → monthly **100%** (N=14) |
| **Rationale** | Registry group `gan_s0_hard_slice_qwen_architecture_v1`. Slice scope — not full validation. |
| **Decision scope** | `arm`, `reject` |

---

### Claim 14 — Residual Gan errors concentrate in infrequent-frequency bucket

| Field | Value |
| --- | --- |
| **Claim statement** | After promotion, ~51 validation records with `gold_pragmatic=infrequent` remain at **43–51%** monthly accuracy vs **~63%** frequent and **~98%** no_seizure_information. |
| **Supporting run IDs** | Hosted: `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z`; Local: `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T230324Z` |
| **Supporting metrics** | Stratified monthly (narrative §2.5; derived from run error analysis, not registry headline fields) |
| **Rationale** | **Interpretation**, not a registry headline metric. Primary evidence: run error analyses referenced in narrative. Flag as open residual, not solved claim. |
| **Decision scope** | `open` |

---

## Discrepancies Or Unsupported Claims

### Claims in `docs/outline.md` **without** registry or narrative backing

| Outline claim | Status | Notes |
| --- | --- | --- |
| **Beat ExECTv2 and Gan paper benchmarks** | **Unsupported / blocked** | Narrative executive summary: no published Real(300) or CUI-aware Table 1 reproduction. Repo ExECT S1 92.3% is 3-family partial on N=40 — not comparable to paper ~0.90 all-field F1. |
| **Downstream adaptation** (billing, cohort selection, outcome variables) | **No experiments** | Outline objective #2; zero registry rows. |
| **GPT 5.5, Gemini 3 Flash, Claude** as evaluated models | **Not run** | Only GPT 4.1-mini (primary), Gemini 3.1 Flash Lite (exploratory Gan), Qwen 35b/9b probed. Gemini full-validation row has `headline_metric: null` in registry. |
| **Qwen3.5:9b as viable production path** | **Exploratory only** | Latency/max-budget caps; weaker than 35b (narrative §2.6). |
| **GEPA / BootstrapFewShot as primary improvement path** | **Negative** | Superseded by manual policy + temporal architecture on both tracks. |
| **Evidence extraction first improves precision** (outline ablation) | **Partial / inconclusive** | Gan evidence policy cap-25 arms (`gan_s0_evidence_*`) show mixed results; optional evidence rejected. |
| **Few-shot helps each field equally** | **Untested at ExECT family level** | Gan few-shot ladder did not beat synthesis full validation. |
| **Modular specialization proven across "very different tasks"** | **Partially supported** | Gan temporal + ExECT breadth ladder demonstrate different failure modes, but shared infrastructure — not independent downstream products. |

### Internal discrepancies (stale_check)

| Issue | Detail |
| --- | --- |
| **Registry vs 2026-05-20 narrative** | Registry includes post-05-20 rows (`candidate_builder_gap_v1`, error taxonomy policy slices) absent from narrative/matrix. |
| **Operational default for Gan** | Narrative/matrix cite temporal v1.1 (~65%) as operational; registry `candidate_builder_gap_v1` GPT arm at **80.6%** is `decision_scope: arm`, not operational. |
| **ExECT S4 Qwen** | Narrative R5 lists S4 Qwen as *pending*; registry has `exect_s4_validation_full_qwen35b_ollama_20260520T160914Z` at **67.5%** micro F1. |
| **Synthesis bootstrap artifact** | Registry notes run directory may be absent locally; metrics bridged from docs — verify `runs/gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z` exists before paper citation. |
| **Gemini full validation** | `gan_s0_direct_full_validation_gemini31_flash_lite` has `headline_metric: null`; narrative cites 63.9% monthly from run — **verify metrics.json** before table inclusion. |
| **ExECT S4 GPT operational note** | Registry notes operational default moved to cause-bridge K0+K1 (2026-05-21); frozen anchor remains v1.2 `…071248Z` at 65.5%. **Human verification needed** if paper cites "current best" vs "frozen ladder anchor." |

---

## Open Writing Tasks

Human verification required before publication:

1. **Choose Gan headline row:** Operational temporal v1.1 (~65%) vs arm `candidate_builder_gap_v1` (~81%) — document promotion decision and preregister if citing latter.
2. **External validity paragraph:** Explicitly state synthetic splits, scorer differences vs published papers; cite `docs/policies/published_benchmark_metrics.md`.
3. **Table footnotes:** N per split (Gan 299, ExECT 40); cap-25 non-comparability; verify-repair call-count confound; micro F1 non-comparability across schema levels.
4. **Bootstrap CIs:** Narrative mentions overlapping CIs for hosted temporal vs verify-repair monthly — locate primary CI artifact or recompute from `runs/*/metrics.json`.
5. **Per-family ExECT tables:** Pull from run `metrics.json` files, not narrative alone (registry stores pooled micro only for most rows).
6. **Generalization:** ExECT test holdout (77.8%) written up; Qwen test holdout still **open**.
7. **Stratified Gan residual:** Formal table for `gold_pragmatic` buckets from error analysis scripts.
8. **Model suite section:** Outline lists 5 models; paper Methods should report only evaluated models with run IDs.
9. **Latency / cost:** Qwen ~10.9 s/record on candidate-builder arm vs ~1.7 s GPT — include if claiming local viability.
10. **Reconcile registry `generated_on: 2026-05-22`** with matrix `2026-05-21` — regenerate matrix or note delta in Methods.
11. **Negative results table:** Consolidate reject/hold outcomes from matrix comparison groups into supplementary material.
12. **Decision scope legend:** Add footnote explaining operational vs arm vs mechanism vs blocked scopes for reproducibility.

---

*This draft is interpretive synthesis. All paper-facing numbers should be verified against `runs/<canonical_run_id>/metrics.json` and named decision docs before submission.*