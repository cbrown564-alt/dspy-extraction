# Paper Narrative Synthesis Draft

**Status:** Review-only draft. Not evidence for publication unless each claim is verified against primary run artifacts (`runs/<canonical_run_id>/metrics.json`).  
**Scope note:** `experiment_registry.json` was generated 2026-05-22 (`row_count`: 204) and extends beyond the 2026-05-20 narrative. Post-20260520 rows are flagged below; they are **not** in the narrative report and should be treated as **stale_check** until reconciled with operational defaults.

---

## Sources Read

| Path | Role |
| --- | --- |
| `docs/outline.md` | Research goals, model list, schema ladder design, ablation plan |
| `docs/experiments/synthesis/experiment_registry.json` | Canonical run IDs, headline metrics, outcomes, decision scopes |
| `docs/experiments/synthesis/experiments_narrative_report_20260520.md` | Living synthesis through 2026-05-20; Tables 1–4 analog |
| `docs/experiments/synthesis/experiment_registry_matrix_20260520.md` | Curated 72-row paper-ready export grouped by `comparison_group` |

**Cross-source artifact:** `docs/experiments/synthesis/experiments_methods_results_20260520.md` (referenced by narrative; not in primary list but consistent with narrative Tables 1–4).

---

## Proposed Results Section Outline

### 4.1 Evaluation setup (Methods bridge)
- Two synthetic epilepsy letter benchmarks: **Gan 2026 S0** (N=299 validation, narrow frequency + evidence) and **ExECTv2 partial ladder** (N=40 validation, 3→11 field families).
- Shared deterministic scorers: `gan_frequency_deterministic_v1`, `exect_*_field_family_deterministic_v1`.
- **Fact:** Not published Real(300) Gan or CUI-aware ExECTv2 Table 1 reproduction (`experiments_narrative_report_20260520.md` §Published benchmark distance; `experiment_registry_matrix_20260520.md` §Caveats).
- **decision_scope:** operational (scorer/split policy frozen).

### 4.2 Gan S0 — architecture and hybrid pipeline (hosted + local)
- **Table A:** Full-validation architecture comparison (same split/scorer).
  - Synthesis + BootstrapFewShot (historical reference)
  - Verify-repair v2 (superseded reference)
  - Temporal-candidates verify-repair v1.1 (operational default through 20260520)
  - Direct + guardrails (local baseline)
- **Interpretation:** Deterministic temporal-candidate preconditioning + verify-repair ties verify-repair on monthly accuracy while improving Purist/Pragmatic and evidence support.
- **Stratified residual:** `gold_pragmatic=infrequent` bucket ~43–51% monthly (narrative §2.5).
- **decision_scope:** operational (promoted defaults); arm (post-20260520 F0/builder-gap variants).

### 4.3 Gan S0 — negative ablations
- GEPA (cap-5): reject — schema/evidence gains, unstable labels.
- ReAct temporal tools (14-record slice): reject — 42.9% monthly.
- Deterministic post-repair: bounded surface-form fixes only (3/299 records).
- Cap-25 unreliability for temporal path (44% cap vs ~65% full).
- **decision_scope:** mechanism (ablation evidence); blocked (GEPA at scale).

### 4.4 ExECT S0/S1 — monolithic three-family extraction
- Frozen GPT v4.10 validation anchor; test holdout generalization gap.
- Section-aware ablation: reject.
- Verify-repair on S1: reject (cap-25).
- **decision_scope:** operational (S1 freeze); arm (test holdout).

### 4.5 ExECT schema ladder S1→S4 — breadth cost
- Monotonic family expansion with frozen label policies per level.
- Micro F1 trend (GPT, N=40): 92.3% → 80.9% → 72.1% → 65.5%.
- Per-family caveats: seizure-frequency weak at S4 (45.7% F1); investigation recovered after v1.0 collapse.
- **decision_scope:** operational (frozen ladder anchors); **do not** plot as single learning curve without family-scope annotation.

### 4.6 Local Qwen3.6:35b replication
- Same frozen prompts as GPT; mixed outcome by task breadth.
- S0/S1: −13.3 pp micro (seizure-type collapse); S2/S3: parity; S4: completed post-narrative (+2.0 pp pooled micro, per-family divergence).
- **decision_scope:** arm (replication track, not operational default).

### 4.7 Deterministic interleaving (hybrid balance)
- ExECT S1 pre-vocab (H2): reject full validation (87.5% vs 92.3% L1).
- ExECT S4 medication temporality post-classifier (H1): cap-25 gain (+14.5 pp precision), full validation reject (56.5% vs 46.4% baseline — registry uses field precision metric).
- **decision_scope:** mechanism (interleaving matrix).

### 4.8 Model suite comparison (optional subsection — **stale_check**)
- Registry rows through 20260522 for Gemini 3 Flash, Claude Sonnet 4.6, expanded-builders F0 on Gan.
- GPT 5.5: **not present in registry.json**; inspection doc exists outside primary sources.
- **decision_scope:** arm only; no operational promotion from suite position alone.

### 4.9 Limitations (Results-adjacent)
- Synthetic splits; small ExECT N; multi-family micro F1 non-comparability across ladder levels; verify-repair latency confound; evidence metric is diagnostic quote-support, not human audit.

---

## Key Paper Claims Map

Each entry: claim → canonical run ID → metrics → rationale. Percentages from registry `headline_metric.value` unless noted from narrative per-family breakdown.

---

### Claim 1 — Hybrid modular system handles two distinct task types

**Claim statement:** A shared DSPy + deterministic infrastructure supports both narrow temporal-frequency extraction (Gan) and broad hierarchical field-family extraction (ExECT) with task-specific programs and scorers.

| Field | Value |
| --- | --- |
| **Supporting run IDs** | Gan: `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z`; ExECT: `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z`, `exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` |
| **Supporting metrics** | Gan: monthly 65.1%, Purist 76.5%, Pragmatic 84.2%; ExECT S1: micro F1 92.3%; ExECT S4: micro F1 65.5% |
| **Rationale** | Same artifact layout and scorer discipline; different schema levels and program architectures. Validates modularity, not superiority over published benchmarks. |
| **decision_scope** | operational |
| **Sources** | `experiment_registry.json` (experiment_ids above); `experiments_narrative_report_20260520.md` §Executive Summary |

---

### Claim 2 — Temporal-candidates verify-repair v1.1 is the promoted Gan architecture (through 20260520)

**Claim statement:** Deterministic temporal candidate hints plus confirm-first verify-repair matches prior verify-repair on monthly accuracy while improving category and evidence metrics on full validation (N=299).

| Field | Value |
| --- | --- |
| **Supporting run ID (hosted, promote)** | `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z` |
| **Supporting metrics** | Monthly 65.1%; Purist 76.5%; Pragmatic 84.2%; schema valid 99.7%; evidence 100.0% |
| **Comparator run ID (superseded)** | `gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z` |
| **Comparator metrics** | Monthly 65.4%; Purist 72.7%; Pragmatic 79.2%; evidence 92.7% |
| **Rationale** | Promotion gates: monthly within 1 pp (−0.3 pp), evidence +7.3 pp, Purist +3.8 pp (`experiments_narrative_report_20260520.md` §2.5). Monthly treated as tie, not proven superiority. |
| **decision_scope** | operational |
| **Sources** | `experiment_registry.json`; `experiment_registry_matrix_20260520.md` §gan_s0_architecture_gpt_validation_v1 |

**Local mirror (promote):**

| Field | Value |
| --- | --- |
| **Run ID** | `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T230324Z` |
| **Metrics** | Monthly 65.8%; Purist 75.5%; Pragmatic 82.6%; schema 99.7%; evidence 100.0% |
| **Baseline comparator** | `gan_s0_qwen35b_direct_full_validation_guardrails_20260519T102249Z` — monthly 55.9% (+10.0 pp for temporal path) |
| **decision_scope** | operational (local Tier 1 default) |

---

### Claim 3 — Local Qwen3.6:35b is viable for Gan at hosted parity; direct path alone is insufficient

**Claim statement:** Qwen temporal-candidates v1.1 reaches hosted-comparable monthly accuracy; direct extraction with guardrails remains ~10 pp lower.

| Field | Value |
| --- | --- |
| **Run IDs** | Temporal: `…230324Z` (above); Direct: `gan_s0_qwen35b_direct_full_validation_guardrails_20260519T102249Z` |
| **Metrics** | 65.8% vs 55.9% monthly |
| **Rationale** | Supports outline goal of local-model hospital path for frequency task; semantic temporal errors dominate direct path (`experiments_narrative_report_20260520.md` §2.4). |
| **decision_scope** | operational (local default) / arm (direct exploratory) |
| **Caveat** | CoT + BootstrapFewShot on Qwen deprioritized (latency/truncation); not a registry row with full-validation headline. |

---

### Claim 4 — Schema breadth predictably reduces pooled micro F1 (ExECT ladder)

**Claim statement:** Adding field families monotonically increases task difficulty; pooled micro F1 falls as scope expands (different family sets — not a single calibrated score).

| Level | Run ID | Families | Micro F1 | Outcome |
| --- | --- | ---: | ---: | --- |
| S1 | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` | 3 | 92.3% | freeze |
| S2 | `exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` | 5 | 80.9% | freeze |
| S3 | `exect_s3_validation_full_gpt4_1_mini_20260519T235439Z` | 9 | 72.1% | freeze |
| S4 | `exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` | 11 | 65.5% | freeze |

| Field | Value |
| --- | --- |
| **Rationale** | Documents outline §Schema S0–S4 parameter; seizure-frequency F1 at S4 remains weak (45.7% per narrative Table 3 / inspection docs). |
| **decision_scope** | operational (frozen anchors) |
| **Sources** | `experiment_registry.json`; `experiment_registry_matrix_20260520.md` §exect_schema_complexity_gpt_validation_v1; `experiments_narrative_report_20260520.md` §Phase 4 |

---

### Claim 5 — ExECT S0/S1 monolithic label-policy engineering reaches strong validation performance; generalization gap on test

**Claim statement:** Manual label-policy iteration (v4.10) on monolithic single-pass extraction yields 92.3% micro F1 on validation; one-shot test holdout drops to 77.8%.

| Field | Value |
| --- | --- |
| **Validation run ID** | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` |
| **Validation metrics** | Micro F1 92.3% |
| **Test run ID** | `exect_s0_s1_validation_test_gpt4_1_mini_20260519T222615Z` |
| **Test metrics** | Micro F1 77.8% (−14.5 pp vs validation) |
| **Rationale** | Supports manual engineering over optimizers on ExECT; cautions against overfitting to 40-record validation. |
| **decision_scope** | operational (validation freeze) / arm (test holdout) |
| **Sources** | `experiment_registry.json`; `experiments_narrative_report_20260520.md` §3.2 |

---

### Claim 6 — Section-aware extraction regresses vs monolithic (ExECT ablation)

**Claim statement:** Section selection + thin family prompts hurt diagnosis and evidence on cap-25.

| Field | Value |
| --- | --- |
| **Run ID (reject)** | `exect_s0_s1_section_aware_cap25_gpt4_1_mini_20260518T174714Z` |
| **Metrics** | Micro F1 65.6% (registry); narrative adds diagnosis F1 44.9%, evidence 75.5% vs monolithic cap-25 73.7% / 92.1% |
| **Rationale** | Negative result for outline §Variant B / ablation “Does splitting by section improve…”. Early policy (v3); compare only within same policy generation. |
| **decision_scope** | arm (reject) |
| **Sources** | `experiment_registry.json`; `experiment_registry_matrix_20260520.md` §exect_s1_architecture_gpt_cap25_v1 |

---

### Claim 7 — Verify-repair helps Gan but ExECT S1 verify-repair regresses

**Claim statement:** Verify-repair improves Gan labels relative to synthesis bootstrap; on ExECT S1 cap-25, verify-repair underperforms monolithic v4.10.

| Gan reference | Run ID | Monthly | Outcome |
| --- | --- | ---: | --- |
| Synthesis bootstrap | `gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z` | 62.9% | superseded |
| Verify-repair v2 | `gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z` | 65.4% | superseded |

| ExECT S1 | Run ID | Micro F1 | Outcome |
| --- | --- | ---: | --- |
| Verify-repair cap-25 | `exect_s0_s1_verify_repair_cap25_gpt4_1_mini_20260519T205419Z` | 83.8% (matrix) | exploratory |
| Monolithic cap-25 v4.10 | `exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T221936Z` | 95.8% | exploratory |

| Field | Value |
| --- | --- |
| **Rationale** | Task-dependent verifier value; outline ablation “Does a verifier improve precision but reduce recall?” — partially supported on Gan, not on ExECT S1 at cap-25. |
| **decision_scope** | arm |
| **Caveat** | Synthesis run artifact noted as missing from local `runs/` in registry caveat; metrics from documented research docs. |

---

### Claim 8 — GEPA / compile-time optimizers did not beat manual guidance at scale

**Claim statement:** GEPA cap-5 runs reject promotion; synthesis bootstrap and temporal architecture outperform optimizer probes for stable benchmark-facing outcomes.

| Field | Value |
| --- | --- |
| **Run IDs** | `gan_s0_gepa_direct_cap5_gpt4_1_mini_20260519T054057Z`; `gan_s0_gepa_direct_cap5_qwen35b_ollama_20260519T060700Z` |
| **Outcome** | reject (both) |
| **Rationale** | Narrative §2.3: prompt bloat, unstable canonical labels on Qwen; cap-5 only. |
| **decision_scope** | blocked (GEPA at scale) / mechanism |
| **Sources** | `experiment_registry.json`; `experiments_narrative_report_20260520.md` §2.3 |

---

### Claim 9 — Deterministic pre/post placement: mixed results

**Claim statement:** Pre-vocab deterministic injection (H2) regresses ExECT S1 full validation; post-classifier (H1) helps medication temporality on cap-25 but not full validation.

| Experiment | Run ID | Metric | Outcome |
| --- | --- | --- | --- |
| S1 H2 pre-vocab full | `exect_s1_interleaving_h2_pre_vocab_gpt4_1_mini_20260520T185755Z` | micro F1 87.5% | reject |
| S1 L1 frozen anchor | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` | micro F1 92.3% | freeze |
| S4 temporality H1 cap-25 | `exect_s4_temporality_h1_post_classifier_cap25_gpt4_1_mini` (matrix) | med temporality precision 61.3% | hold |
| S4 temporality L1 cap-25 | `exect_s4_temporality_l1_baseline_cap25_gpt4_1_mini` (matrix) | med temporality precision 46.8% | hold |
| S4 temporality H1 full | (matrix) | med temporality precision 56.5% | reject |

| Field | Value |
| --- | --- |
| **Rationale** | Supports outline §“best mix of deterministic + LLM” as empirical question, not uniform win for determinism. |
| **decision_scope** | mechanism |
| **Sources** | `experiment_registry_matrix_20260520.md` §exect_s1_interleaving_gpt_validation_v1, §exect_s4_temporality_deterministic_v1 |

---

### Claim 10 — Local Qwen replication: task-dependent gap vs GPT

**Claim statement:** Qwen matches/exceeds GPT on S2–S4 pooled micro with frozen prompts; trails on S0/S1 due to seizure-type F1 collapse.

| Level | GPT run | GPT micro | Qwen run | Qwen micro | Δ |
| --- | --- | ---: | --- | ---: | ---: |
| S1 | `…221944Z` | 92.3% | `exect_s0_s1_validation_full_qwen35b_ollama_20260520T042117Z` | 79.0% | −13.3 pp |
| S2 | `…231223Z` | 80.9% | `exect_s2_validation_full_qwen35b_ollama_20260520T073552Z` | 82.6% | +1.7 pp |
| S3 | `…235439Z` | 72.1% | `exect_s3_validation_full_qwen35b_ollama_20260520T092244Z` | 72.2% | +0.1 pp |
| S4 | `…071248Z` | 65.5% | `exect_s4_validation_full_qwen35b_ollama_20260520T160914Z` | 67.5% | +2.0 pp |

| Field | Value |
| --- | --- |
| **Rationale** | Addresses outline §“Can Qwen handle hardest semantic work?” — yes for broad multi-family with frozen policy; weak on fine-grained seizure typing at S1. Registry notes per-family divergence at S4 despite pooled micro gain. |
| **decision_scope** | arm (Qwen replication hold) |
| **Sources** | `experiment_registry.json`; `experiment_registry_matrix_20260520.md` §exect_qwen_replication_validation_v1 |

---

### Claim 11 — Model suite: closed models vary by surface (**stale_check** — post-20260520, partial registry coverage)

**Claim statement:** Under frozen architecture v1 (`model_suite_frozen_architecture_v1`), hosted models differ by task; larger models do not uniformly dominate.

| Surface | Model track | Run ID (canonical) | Headline metric |
| --- | --- | --- | --- |
| ExECT S1 | Gemini 3 Flash | `exect_s0_s1_validation_full_gemini3_flash_20260522T111119Z` | micro F1 89.9% |
| ExECT S1 | Claude Sonnet 4.6 | `exect_s0_s1_validation_full_claude_sonnet_4_6_anthropic_20260522T090828Z` | micro F1 81.8% |
| ExECT S4 | Gemini 3 Flash | `exect_s4_validation_full_gemini3_flash_20260522T111330Z` | micro F1 63.2% |
| ExECT S4 | Claude Sonnet 4.6 | `exect_s4_validation_full_claude_sonnet_4_6_anthropic_20260522T093634Z` | micro F1 65.1% |
| Gan F0 | Gemini 3 Flash | `gan_s0_expanded_builders_prose_full_validation_gemini3_flash_20260522T111541Z` | monthly 75.3% |
| Gan F0 | GPT 4.1-mini F0 | `gan_s0_expanded_builders_prose_full_validation_gpt4_1_mini_20260521T073432Z` | monthly 68.1% |

| Field | Value |
| --- | --- |
| **Rationale** | Partial answer to outline model list (Gemini 3 Flash); GPT 5.5 **not in registry** — cannot map to registry run ID from primary sources. |
| **decision_scope** | arm (not mechanism closure) |
| **Caveat** | F0 skeleton ≠ operational temporal-candidates v1.1 default; compare only within `comparison_group`. |

---

### Claim 12 — Candidate-builder gap v1 improves Gan monthly (**stale_check** — post-narrative, arm promote)

**Claim statement:** Expanded deterministic candidate builders with error-taxonomy policy reach higher full-validation monthly than prior operational anchors.

| Field | Value |
| --- | --- |
| **Run ID** | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` |
| **Metrics** | Monthly 80.6%; Purist 86.0%; Pragmatic 88.6%; schema 100%; evidence 100% |
| **Qwen transfer** | `gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z` — monthly 70.7% (hold) |
| **Rationale** | Registry `outcome: promote` but `decision_scope: arm`; notes explicitly state operational default remains separate. **Not** in 20260520 narrative. |
| **decision_scope** | arm |

---

## Discrepancies Or Unsupported Claims

| Outline / implied claim | Status | Evidence gap |
| --- | --- | --- |
| **Beat ExECTv2 and Gan paper benchmarks** | **Unsupported / blocked** | Narrative §Executive Summary: no Real(300) Gan, no CUI-aware ExECT Table 1. Repo ExECT S1 92.3% micro on 3 families ≠ paper ~0.90 all-family F1. |
| **Downstream use cases** (billing, cohort selection, outcome variables) | **Unsupported** | No registry rows or narrative experiments for these use cases. |
| **GPT 5.5 assessment** | **Missing from primary registry** | Listed in `outline.md` §Models; no `experiment_id` in `experiment_registry.json`. Cannot cite as registry-backed without adding rows from `runs/`. |
| **Gemini 3 Flash (outline)** | **Partial** | Model-suite rows in registry (post-20260520); not in narrative or matrix export. |
| **Qwen3.5:9b as peer model** | **Exploratory only** | Latency/feasibility probes; reject outcomes; weaker than 35b (`experiments_narrative_report_20260520.md` §2.6). |
| **Comprehensive ablation matrix** (few-shot per field, negation, temporality guidelines, ILAE guidelines, multi-step vs failure modes) | **Mostly open** | Partial coverage: section-aware, verify-repair, GEPA, interleaving, evidence policy cap-25 rows. Many outline ablations have no registry anchor. |
| **DSPy optimizer on ExECT** | **Blocked** | Runner gate: optimizers Gan-only; ExECT gains from manual label policy (`experiments_narrative_report_20260520.md` §Cross-Cutting). |
| **Operational default vs best arm on Gan** | **Discrepancy / stale_check** | Operational promote through 20260520: temporal-candidates v1.1 (~65% monthly). Registry post-20260521: F0 expanded builders 68.1%, candidate-builder-gap 80.6% — higher metrics but `decision_scope: arm`. Paper must not conflate without human promotion review. |
| **Synthesis bootstrap artifact** | **Caveat** | Registry notes run directory may be absent locally; metrics from documented sources. |
| **Cap-25 ↔ full-validation extrapolation** | **Unsupported as claim** | Explicitly unreliable for temporal path (44% cap vs ~65% full). |

---

## Open Writing Tasks

### Verification before publication
1. **Reconcile operational vs arm defaults** on Gan: choose whether Results cite temporal-candidates v1.1 (operational through 20260520) or post-20260521 F0/builder-gap arms; read promotion decision docs cited in registry.
2. **Backfill GPT 5.5** (and any other outline models) into `experiment_registry.json` or exclude from Results until canonical run IDs exist.
3. **Confirm primary artifacts** exist: `runs/<canonical_run_id>/metrics.json` for every cited row (especially synthesis bootstrap, superseded runs).
4. **Per-family tables** for ExECT ladder and model suite — pooled micro alone is insufficient per registry `metric_caveats`.
5. **Bootstrap CIs** — narrative mentions overlap for Gan monthly; verify from stored metrics JSON before claiming equivalence.
6. **Test holdout** — report ExECT test 77.8% with clear “one-shot, post-development” warning; no Qwen test holdout in registry.

### Methods / framing still to write
7. **Deterministic foundation milestone** (Phase 0) — short Methods paragraph pointing to `docs/policies/deterministic_scorer_semantics.md`.
8. **Sample size and split table** — Gan N=299 validation; ExECT N=40 validation / test; cap-25/slice scopes labeled non-headline.
9. **Call-count / latency confound** for verify-repair vs direct.
10. **Published benchmark distance** paragraph — mandatory limitation; cite `docs/policies/published_benchmark_metrics.md` if allowed beyond primary four sources.

### Experiments not yet paper-ready (outline promises)
11. Gan Real(300) reproduction — **blocked**.
12. Full ExECT CUI-aware scorer — **blocked**.
13. Gan train/dev/test splits (outline §Dataset) — **open** (Gan split exists; outline asked for ExECT-style splits).
14. Downstream task specialization — **open**.
15. ReAct bounded probe — narrative scheduled; registry shows reject on slice (`gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails_20260520T173943Z`, monthly 42.9%).

### Registry hygiene (human review)
16. Retrospective taxonomy tags (`pending_backfill` comparison groups) — matrix §Caveats.
17. Align narrative report date (20260520) with registry date (20260522) in paper Methods “data cut” statement.
18. Resolve matrix S4 Qwen micro (67.5%) vs narrative “pending at report time” — registry now has `exect_s4_validation_full_qwen35b_ollama_20260520T160914Z`.

---

**Uncertainty summary:** Facts above are registry- or narrative-backed with paths. Interpretation (e.g., “breadth cost,” “local viability”) is supported by paired comparisons but should not be overstated as causal ablation without controlling for label-policy version changes across ladder steps. Post-20260520 registry rows require **stale_check** against current Kanban/operational defaults before paper submission.