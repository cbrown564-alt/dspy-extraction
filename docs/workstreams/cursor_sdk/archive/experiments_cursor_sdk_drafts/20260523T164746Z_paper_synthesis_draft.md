# Paper Narrative Synthesis Draft

Review-only artifact. Metrics below are drawn from `experiment_registry.json` headline fields and secondary blocks unless noted; per-family F1 breakdowns come from `experiments_narrative_report_20260520.md` / `experiments_methods_results_20260520.md` where the registry reports pooled micro only. **Not** evidence for published ExECTv2 Table 1 or Gan Real(300) claims unless explicitly flagged and tied to primary run artifacts.

---

## Sources Read

| Path | Role |
| --- | --- |
| `docs/outline.md` | Research goals, model suite, schema ladder, ablation plan |
| `docs/experiments/synthesis/experiment_registry.json` | Canonical run IDs, headline metrics, decision scopes, metric caveats |
| `docs/archive/experiments/synthesis/pre_component_pivot/experiments_narrative_report_20260520.md` | Chronological experiment narrative through 2026-05-20 |
| `docs/archive/experiments/synthesis/pre_component_pivot/experiment_registry_matrix_20260520.md` | Curated comparison-group matrix (72 rows; generated 2026-05-21) |
| `docs/archive/experiments/synthesis/pre_component_pivot/experiments_methods_results_20260520.md` | Referenced by narrative report for Tables 1–4 (read for metric cross-check) |

**Temporal note:** Narrative report status is through 2026-05-20 evening; registry includes later rows (e.g. model-suite runs 2026-05-22, ExECT S4 Qwen full 2026-05-20T160914Z). Where they diverge, registry is treated as authoritative for run IDs; narrative staleness is flagged below.

---

## Suggested Results Section Outline

### R1. Gan S0 seizure-frequency extraction (narrow schema, temporal reasoning)
- Full-validation anchors on `gan_2026_fixed_v1:validation` (N=299)
- Architecture ladder: synthesis bootstrap → verify-repair v2 → temporal-candidates v1.1
- Local Qwen: direct+guardrails vs temporal-candidates (Tier 1 default)
- Residual error bucket: `gold_pragmatic=infrequent`

### R2. ExECT S0/S1 monolithic baseline (three audited families)
- Label-policy engineering arc → frozen v4.10
- Negative: section-aware ablation
- Generalization: validation vs test holdout

### R3. ExECT schema breadth ladder (S1→S4, GPT frozen)
- Micro F1 vs family count (breadth cost, not a single learning curve)
- Accepted gaps at S3/S4 freeze (seizure frequency, comorbidity)

### R4. Local Qwen replication (frozen GPT prompts)
- S0/S1–S4 full-validation ladder vs GPT anchors
- Family-level divergence (especially seizure-type at S1)

### R5. Hybrid deterministic + LLM placement
- Gan: H2/H4 temporal-candidates (pre-deterministic hints + LLM verify/repair)
- ExECT S1: H1 post-bridge vs H2 pre-vocab interleaving matrix
- ExECT S4: medication temporality post-classifier (field-specific)

### R6. Model suite comparison (frozen architecture)
- ExECT S1 and S4 across GPT 4.1-mini, Gemini 3 Flash, Claude Sonnet 4.6, Qwen3.6:35b
- **Scope:** `decision_scope: arm`; not mechanism closure

### R7. Negative / inconclusive findings
- GEPA, BootstrapFewShot on ExECT, ReAct temporal tools, section-aware ExECT, deterministic surface replay, cap-25 as full predictor

### R8. Limitations (mandatory)
- Synthetic splits only; no published benchmark reproduction; small ExECT N=40; multi-family micro F1 non-comparability across ladder levels

---

## Key Paper Claims Map

Each entry: claim → canonical run ID → metrics → rationale/caveats. Decision scopes preserved from registry `notes` / matrix.

---

### Claim 1 — Promoted Gan architecture reaches ~65% monthly frequency with strong evidence/schema on repo validation split

**Claim statement:** Temporal-candidates verify-repair v1.1 is the promoted Gan S0 program; hosted and local full-validation runs tie prior verify-repair on monthly accuracy while improving Purist/Pragmatic categories and evidence support.

| Field | Hosted (GPT 4.1-mini) | Local (Qwen3.6:35b) |
| --- | --- | --- |
| **Supporting run ID** | `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z` | `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T230324Z` |
| **Registry experiment_id** | `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails` | `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails` |
| **Monthly frequency accuracy** | 65.1% | 65.8% |
| **Purist category accuracy** | 76.5% | 75.5% |
| **Pragmatic category accuracy** | 84.2% | 82.6% |
| **Schema valid rate** | 99.7% | 99.7% |
| **Evidence quote support** | 100.0% | 100.0% |
| **Outcome / scope** | `promote`, `decision_scope: operational` | `promote`, `decision_scope: operational` |
| **Comparison group** | `gan_s0_architecture_gpt_validation_v1` | `gan_s0_architecture_qwen_validation_v1` |

**Rationale:** Primary benchmark-facing metrics per `gan_frequency_deterministic_v1`. Hosted monthly −0.3 pp vs superseded verify-repair v2 (within 1 pp gate); evidence +7.3 pp (`docs/experiments/gan/gan_s0_gpt4_1_mini_temporal_candidates_full_validation_decision_20260520.md`, cited in registry). Local temporal beats direct+guardrails baseline by ~10 pp monthly (55.9% → 65.8%).

**Caveats:** Split is repo synthetic validation, not Gan Real(300). Verify-repair doubles model calls; latency not comparable to direct. Residual `gold_pragmatic=infrequent` bucket ~43–51% monthly (narrative report §2.5; not in registry headline).

---

### Claim 2 — Verify-repair and synthesis bootstrap establish architecture ladder on Gan (hosted)

**Claim statement:** Verify-repair v2 improved over synthesis CoT+bootstrap on monthly accuracy; both are superseded by temporal-candidates but remain valid reference arms.

| Architecture | Supporting run ID | Monthly | Purist | Pragmatic | Evidence | Outcome |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Synthesis + BootstrapFewShot | `gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z` | 62.9% | 70.1% | 73.9% | 89.9% | `superseded`, `decision_scope: arm` |
| Verify-repair v2 | `gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z` | 65.4% | 72.7% | 79.2% | 92.7% | `superseded`, `decision_scope: arm` |

**Rationale:** Ordered architecture comparison within `gan_s0_architecture_gpt_validation_v1`, same split/scorer.

**Caveats:** Synthesis run artifact **may be absent locally** (registry: "documented but not present in the current local runs directory"). Metrics sourced from registry headline, not re-verified from `runs/…/metrics.json` in this draft.

---

### Claim 3 — Local Qwen direct extraction is viable but inferior to temporal-candidates without deterministic temporal scaffolding

**Claim statement:** Qwen3.6:35b direct single-pass with guardrails achieves usable but lower monthly accuracy; temporal-candidates closes the gap to hosted performance.

| Variant | Supporting run ID | Monthly | Purist | Pragmatic | Evidence |
| --- | --- | ---: | ---: | ---: | ---: |
| Direct + guardrails | `gan_s0_qwen35b_direct_full_validation_guardrails_20260519T102249Z` | 55.9% | 62.0% | 70.5% | 99.6% |
| Temporal-candidates v1.1 | `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T230324Z` | 65.8% | 75.5% | 82.6% | 100.0% |

**Rationale:** Clean within-track comparison (`gan_s0_architecture_qwen_validation_v1`). Supports outline objective that local models can handle semantic extraction when hybrid scaffolding is present.

**Caveats:** `decision_scope: arm` for direct row. ChainOfThought + BootstrapFewShot on Qwen deprioritized per narrative (latency/truncation); not a headline claim without separate run IDs.

---

### Claim 4 — ExECT S0/S1 monolithic label policy v4.10 reaches high micro F1 on three audited families (hosted)

**Claim statement:** Iterative manual label-policy engineering on monolithic single-pass extraction yields a frozen GPT anchor at 92.3% micro F1 on 40-record validation for diagnosis, seizure type, and annotated medication.

| Field | Value |
| --- | --- |
| **Supporting run ID** | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` |
| **Micro F1** | 92.3% |
| **Per-family F1** (narrative/methods, not registry headline) | Diagnosis 93.8%; seizure-type 90.5%; medication 92.8% |
| **Outcome / scope** | `freeze`, `decision_scope: operational` |
| **Comparison group** | `exect_schema_complexity_gpt_validation_v1` |

**Rationale:** Frozen dev anchor for ExECT narrow schema. Gains attributed to label-policy versions + deterministic bridges, not DSPy optimizers (narrative §Cross-Cutting; registry notes).

**Caveats:** Partial ExECT diagnostic (3 families), not CUI-aware Table 1 reproduction. Cap-25 (95.8%, run `…221936Z`) is optimistically biased vs full validation (~+3.5 pp, narrative §3.2).

---

### Claim 5 — Section-aware ExECT extraction regresses vs monolithic (negative result)

**Claim statement:** Deterministic section filtering before per-family extraction hurts micro F1 and evidence support on cap-25.

| Variant | Supporting run ID | Scope | Micro F1 | Outcome |
| --- | --- | --- | ---: | --- |
| Monolithic (early policy, cap-25) | `exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T221936Z` | cap25 | 95.8% | `exploratory` |
| Section-aware | `exect_s0_s1_section_aware_cap25_gpt4_1_mini_20260518T174714Z` | cap25 | 65.6% | `reject`, `decision_scope: arm` |

**Rationale:** Within `exect_s1_architecture_gpt_cap25_v1`. Narrative reports −8.1 pp micro vs early monolithic baseline (73.7% at v1 policy, run `…172431Z`); registry cap-25 monolithic v4.10 is not the same prompt version—compare section-aware only within architecture group.

**Caveats:** Cap-25 only; not full-validation section-aware run in registry.

---

### Claim 6 — ExECT validation→test generalization gap on frozen S0/S1 policy

**Claim statement:** One-shot test holdout shows substantial drop from validation micro F1 after development tuning stopped.

| Split | Supporting run ID | Micro F1 |
| --- | --- | ---: |
| Validation (frozen v4.10) | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` | 92.3% |
| Test holdout | `exect_s0_s1_validation_test_gpt4_1_mini_20260519T222615Z` | 77.8% |

**Rationale:** `exect_s1_generalization_gpt_test_v1`; gap −14.5 pp (narrative §3.2). Per-family test F1: diagnosis 71.4%, seizure-type 66.0%, medication 92.7% (methods doc Table 2).

**Caveats:** `decision_scope: arm`. Single one-shot test evaluation; no Qwen test holdout in registry.

---

### Claim 7 — Schema breadth increases task difficulty; micro F1 falls as family set expands (GPT frozen ladder)

**Claim statement:** Adding field families predictably reduces pooled micro F1; values are **not** a single calibrated score across levels.

| Level | Families (scored) | Supporting run ID | Micro F1 | Outcome |
| --- | ---: | --- | ---: | --- |
| S0/S1 | 3 | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` | 92.3% | `freeze` |
| S2 | 5 | `exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` | 80.9% | `freeze` |
| S3 | 9 | `exect_s3_validation_full_gpt4_1_mini_20260519T235439Z` | 72.1% | `freeze` |
| S4 | 11 | `exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` | 65.5% | `freeze` |

**Rationale:** `exect_schema_complexity_gpt_validation_v1`. Supports outline schema-breadth experimental parameter (S0–S4). Narrative per-family highlights: S4 seizure-frequency F1 45.7%, investigation 96.7%, medication temporality ~62–67% (methods Table 3).

**Caveats:** Registry `comparison_caveat`: "micro F1 aggregates different family sets." Comorbidity gap accepted at S3/S4 freeze (narrative §4.2–4.3). S4 operational default may have moved to cause-bridge program per registry note on `exect_s4_validation_full_gpt4_1_mini`—verify before citing as live default.

---

### Claim 8 — Local Qwen replicates frozen GPT prompts with model-specific failure modes

**Claim statement:** Qwen3.6:35b matches or beats GPT on S2/S3/S4 pooled micro but trails substantially at S1 due to seizure-type granularity collapse.

| Level | GPT run / micro F1 | Qwen run / micro F1 | Δ |
| --- | --- | --- | ---: |
| S1 | `…221944Z` / 92.3% | `exect_s0_s1_validation_full_qwen35b_ollama_20260520T042117Z` / 79.0% | −13.3 pp |
| S2 | `…231223Z` / 80.9% | `exect_s2_validation_full_qwen35b_ollama_20260520T073552Z` / 82.6% | +1.7 pp |
| S3 | `…235439Z` / 72.1% | `exect_s3_validation_full_qwen35b_ollama_20260520T092244Z` / 72.2% | +0.1 pp |
| S4 | `…071248Z` / 65.5% | `exect_s4_validation_full_qwen35b_ollama_20260520T160914Z` / 67.5% | +2.0 pp |

**Rationale:** `exect_qwen_replication_validation_v1`. Supports outline claim that local Qwen can handle complex tasks on some subtasks but not uniformly.

**Caveats:** `decision_scope: arm` for Qwen rows. S1 per-family (narrative): Qwen diagnosis 95.1% vs GPT 93.8%; seizure-type 55.7% vs 90.5%. S4 Qwen +2.0 pp pooled micro but registry warns "per-family profile diverges"—do not claim uniform superiority. **Narrative report lists S4 Qwen as pending; registry shows completed run** → stale_check on narrative.

---

### Claim 9 — Deterministic pre-placement (temporal candidates) beats pure LLM scaling on Gan infrequent-rate cases

**Claim statement:** Deterministic temporal candidate hints + confirm-first verifier outperform direct extraction and beat GEPA/larger-token-budget probes for stable benchmark-facing outcomes.

| Evidence type | Supporting run ID | Metric | Outcome |
| --- | --- | --- | --- |
| Temporal-candidates full (Qwen) | `…230324Z` | 65.8% monthly | `promote` |
| Direct full (Qwen) | `…102249Z` | 55.9% monthly | `exploratory` |
| ReAct temporal tools (14-record slice) | `gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails_20260520T173943Z` | 42.9% monthly; 50% schema valid | `reject`, `decision_scope: arm` |
| Temporal-candidates regression slice (14 rec) | `gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_guardrails_20260519T232514Z` | 100% monthly | `exploratory` (slice) |

**Rationale:** Supports outline hybrid architecture (deterministic temporal rules + LLM adjudication). ReAct rejection supports deprioritizing tool-loop CoT on local Qwen.

**Caveats:** Slice runs (N=14) must not extrapolate to full validation. GEPA cap-5 runs exist (`gan_s0_gepa_direct_cap5_gpt4_1_mini_20260519T054057Z`) but registry `headline_metric: null`—negative conclusion from narrative/decision docs only.

---

### Claim 10 — ExECT deterministic interleaving: post-hoc bridges help; pre-vocab injection hurts at full validation

**Claim statement:** H1 post-deterministic bridges match frozen L1 anchor; H2 pre-vocab controlled vocabulary injection regresses full-validation micro F1.

| Arm | Supporting run ID | Scope | Micro F1 | Outcome |
| --- | --- | --- | ---: | --- |
| H1 post-bridge | `exect_s1_interleaving_h1_post_bridge_gpt4_1_mini_20260520T185747Z` | full_validation | 92.3% | `hold`, `decision_scope: arm` |
| H2 pre-vocab | `exect_s1_interleaving_h2_pre_vocab_gpt4_1_mini_20260520T185755Z` | full_validation | 87.5% | `reject`, `decision_scope: arm` |
| L1 raw no bridges | `exect_s1_interleaving_l1_raw_no_bridges_gpt4_1_mini` (full) | full_validation | 68.6% | `exploratory` |

**Rationale:** `exect_s1_interleaving_gpt_validation_v1` / `v2`. H1 identical to frozen anchor confirms bridges are load-bearing, not redundant.

**Caveats:** `decision_scope: arm`; mechanism not closed (matrix caveat). Medication/seizure pre-vocab slice tests also `reject` at slice scope (matrix rows).

---

### Claim 11 — ExECT S4 medication temporality: post-classifier improves precision but fails full-validation F1 guard

**Claim statement:** Deterministic post-hoc medication temporality classifier raises precision but collapses recall at full validation; not promoted.

| Arm | Supporting run ID | Medication temporality precision | Outcome |
| --- | --- | ---: | --- |
| L1 baseline | `exect_s4_temporality_l1_baseline_full_gpt4_1_mini_20260520T204207Z` | 46.4% | `hold`, `decision_scope: operational` |
| H1 post-classifier | `exect_s4_temporality_h1_post_classifier_full_gpt4_1_mini_20260520T204216Z` | 56.5% | `reject`, `decision_scope: arm` |

**Rationale:** `exect_s4_temporality_deterministic_v1`. Cap-25 gate passed (+14.5 pp precision) but full validation failed F1 guard (−6.6 pp MT F1 per registry note).

**Caveats:** Field-specific metric, not pooled micro. Supports outline ablation on temporality guidelines with nuanced negative result.

---

### Claim 12 — Model suite comparison under frozen ExECT architecture (hosted models vs Qwen)

**Claim statement:** On ExECT S1 (3 families), GPT 4.1-mini leads; Gemini 3 Flash and Gemini 3.1 Flash Lite are competitive; Claude Sonnet 4.6 and Qwen trail, with seizure-type F1 as dominant gap for weaker models.

| Model | S1 run ID | S1 micro F1 | S4 run ID | S4 micro F1 |
| --- | --- | ---: | --- | ---: |
| GPT 4.1-mini (anchor) | `…221944Z` | 92.3% | `…071248Z` | 65.5% |
| Gemini 3 Flash | `exect_s0_s1_validation_full_gemini3_flash_20260522T111119Z` | 89.9% | `exect_s4_validation_full_gemini3_flash_20260522T111330Z` | 63.2% |
| Gemini 3.1 Flash Lite | `exect_s0_s1_validation_full_gemini31_flash_lite_20260521T093501Z` | 90.3% | *(smoke/S4 replay in registry; full S4 headline not in curated matrix)* | — |
| Claude Sonnet 4.6 | `exect_s0_s1_validation_full_claude_sonnet_4_6_anthropic_20260522T090828Z` | 81.8% | `exect_s4_validation_full_claude_sonnet_4_6_anthropic_20260522T093634Z` | 65.1% |
| Qwen3.6:35b | `…042117Z` | 79.0% | `…160914Z` | 67.5% |

**Rationale:** `model_suite_frozen_architecture_v1`; same scorer/split/program architecture; `varied_factor: model_track`.

**Caveats:** All rows `decision_scope: arm`. **GPT 5.5 not in registry** (outline lists it; no runs). Gan model-suite comparison incomplete: Gemini 3.1 Flash Lite Gan full run (`gan_s0_direct_full_validation_gemini31_flash_lite_20260519T101710Z`) has `headline_metric: null` in registry—narrative cites 63.9% monthly but not registry-backed here.

---

### Claim 13 — DSPy optimizers do not beat manual engineering on ExECT; BootstrapFewShot on ExECT cap-25 regresses

**Claim statement:** Compile-time optimization on ExECT was never promoted; cap-25 bootstrap underperforms frozen v4.10 baseline.

| Arm | Supporting run ID | Micro F1 | Outcome |
| --- | --- | ---: | --- |
| Optimizer baseline (v4.10) | `exect_s1_optimizer_baseline_cap25_gpt4_1_mini_20260521T000602Z` | 95.8% | `hold` |
| BootstrapFewShot compiled | `exect_s1_optimizer_bootstrap_cap25_gpt4_1_mini_20260521T000608Z` | 90.7% | `reject`, `decision_scope: arm` |

**Rationale:** `exect_s1_optimizer_gpt_cap25_v1`. Aligns with narrative conclusion that ExECT gains are label-policy-driven.

**Caveats:** Cap-25 only; no full-validation optimizer run.

---

### Claim 14 — Verify-repair on ExECT S1 cap-25 does not beat single-pass v4.10

**Claim statement:** Adding verify-repair to ExECT monolithic extraction regresses cap-25 micro F1 vs single-pass.

| Arm | Supporting run ID | Micro F1 | Outcome |
| --- | --- | ---: | --- |
| Single-pass v4.10 | `exect_s1_verification_single_pass_cap25` → `…221936Z` | 95.8% | `hold` |
| Verify-repair | `exect_s0_s1_verify_repair_cap25_gpt4_1_mini_20260519T205419Z` | 83.8% | `exploratory` |

**Rationale:** `exect_s1_verification_gpt_validation_v1`. Contrasts with Gan, where verify-repair helped before temporal-candidates.

**Caveats:** Cap-25; factor-isolation inspection docs dated 20260521 (post-narrative).

---

## Discrepancies Or Unsupported Claims

### Unsupported or blocked (outline.md vs registry/narrative)

| Outline claim | Status | Source |
| --- | --- | --- |
| **Beat ExECTv2 and Gan paper benchmarks** | **Blocked / unsupported.** No Gan Real(300) or CUI-aware ExECT Table 1 reproduction. Published anchors (~0.78 Purist / ~0.85 Pragmatic Gan; ~0.90 ExECT per-letter F1) explicitly disclaimed. | `outline.md` §Goal 1; narrative §Cross-Cutting "Published benchmark distance"; `docs/policies/published_benchmark_metrics.md` (cited in narrative) |
| **GPT 5.5 evaluation** | **No registry rows.** Outline lists GPT 5.5; no `canonical_run_id` found. | `outline.md` §Models; registry grep |
| **Downstream use-case adaptation** (billing, cohort selection, outcome variables) | **No experiments.** Outline goal 2; no registry rows. | `outline.md` §Goal 2 |
| **Qwen3.5:9b as primary local model** | **Exploratory only; weaker than 35b.** Smoke runs exist; not promoted. | Narrative §2.6; registry smoke rows |
| **GEPA replaces manual guidance at scale** | **Not supported** as headline claim; cap-5 probes only, deprioritized. Registry headline null for GEPA rows. | Narrative §2.3; registry `gan_s0_gepa_direct_cap5_*` |

### Stale or divergent sources (stale_check)

| Issue | Detail |
| --- | --- |
| **ExECT Qwen S4 status** | Narrative/methods (20260520) list S4 Qwen as *pending*; registry has full run `exect_s4_validation_full_qwen35b_ollama_20260520T160914Z` at **67.5% micro F1**. Update narrative before paper cites pending state. |
| **Synthesis bootstrap artifact** | Registry notes run directory may be missing locally; metrics from docs bridge. Re-verify artifact before primary citation. |
| **Matrix vs registry date** | Matrix generated 20260521; registry includes 20260522+ model-suite rows not in narrative report. |
| **Gemini Gan full validation** | Narrative: 63.9% monthly (`…101710Z`); registry row has `headline_metric: null`. |
| **ExECT S4 default program** | Registry note on GPT S4 anchor: operational default may have moved to cause-bridge K0+K1 (20260521). Paper should not cite `…071248Z` as current default without verification. |

### Claims requiring per-family tables (not in registry headline alone)

- ExECT S1/S2/S3/S4 per-family F1 (seizure frequency 45.7% at S4, comorbidity trends): methods doc Table 3 / narrative §4; registry provides pooled micro only.
- Gan stratified `gold_pragmatic=infrequent` bucket: narrative §2.5; not encoded as registry headline metric.
- Bootstrap CIs for Gan monthly (hosted temporal vs verify-repair): methods §Analysis; no registry row.

### Interpretation vs fact boundary

| Fact (artifact-backed) | Interpretation (requires human review) |
| --- | --- |
| Temporal-candidates monthly ≈ verify-repair v2 (−0.3 pp hosted) | "Equivalent" monthly accuracy with category/evidence gains driving adoption |
| Qwen S4 +2.0 pp pooled micro vs GPT | "Local model viable at broad schema" — registry warns per-family divergence |
| ExECT val 92.3% vs test 77.8% | "Generalization gap" — single holdout, development stopped after val tuning |
| 100% Gan evidence support on promoted runs | Evidence enforced by program policy + deterministic span check, not independent human audit |

---

## Open Writing Tasks

### Verification before publication (human)

1. **Re-read primary metrics** from `runs/<canonical_run_id>/metrics.json` for all headline numbers in Tables 1–4 analog; confirm synthesis bootstrap artifact existence.
2. **Resolve S4 operational default:** confirm whether paper reports historical L1 anchor (`…071248Z`) or cause-bridge K0+K1 program (registry note on `exect_s4_validation_full_gpt4_1_mini`).
3. **Update stale narrative sections** (ExECT Qwen S4 complete; model-suite 20260522 runs; factor-isolation 20260521 rows).
4. **Published benchmark paragraph:** explicit non-claim plus roadmap (Gan Real(300), CUI-aware ExECT scorer) — currently `blocked` in narrative.
5. **Per-family tables:** extract from frozen run inspections (`docs/experiments/exect/exect_s4_validation_full_v1_2_gpt4_1_mini_inspection_20260520.md`, etc.) for Results tables; do not rely on pooled micro alone for S4 claims.
6. **Decision scope labels:** tag each Results subsection with operational vs arm vs mechanism vs open/blocked per registry `notes`.
7. **GPT 5.5 / downstream tasks:** either run experiments or demote outline goals to Future Work.

### Results prose still to draft

- **Methods cross-reference:** split names, N, scorer modes (`gan_frequency_deterministic_v1`, `exect_*_field_family_deterministic_v1`) — largely in `experiments_methods_results_20260520.md`; needs tightening for journal format.
- **Error analysis subsection:** infrequent Gan bucket, ExECT seizure-type/Qwen failure taxonomy — point to inspection docs, not this draft.
- **Latency / cost:** model-suite secondary metrics include `prediction_seconds_per_record` for Claude/Gemini (registry); Qwen latency policy cited but no unified comparison table.
- **Ablation interaction narrative:** few-shot × verification × sectioning — partially covered; ExECT few-shot/optimizer negative; Gan few-shot ladder not in curated matrix (many `pending_backfill`).
- **Limitations:** copy/adapt from methods doc §Limitations; add registry row count (~130) vs curated matrix (72) for transparency.

### Registry / matrix hygiene (open, not for this draft to change)

- Backfill `pending_backfill` comparison groups (GEPA, few-shot ladder, Gemini Gan full).
- Controlled vocabulary validation for retrospective taxonomy fields (matrix caveat §Caveats).
- Post-20260520 rows (error taxonomy policy, candidate builder gap, targeted examples) — **not in user-specified primary sources**; omit from paper claims unless explicitly promoted later.

---

*End of review-only draft. No files were modified.*