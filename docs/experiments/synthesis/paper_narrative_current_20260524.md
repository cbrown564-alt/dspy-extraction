# Paper Narrative — Current Version

Date: 2026-05-24  
Status: Source-backed paper narrative synthesis (post–critical-review revision)  
Decision scope: writing artifact only; no scorer, loader, registry, or model-output changes  
Skills: `paper-narrative-synthesis`, revised per [paper_narrative_critical_review_20260524.md](paper_narrative_critical_review_20260524.md)

## Companion Artifacts (Evidence Freeze)

| Role | Document |
| --- | --- |
| Operational defaults (D1) | [paper_frozen_operational_defaults_20260524.md](paper_frozen_operational_defaults_20260524.md) |
| Negative arms (D2) | [paper_frozen_arm_reject_table_20260524.md](paper_frozen_arm_reject_table_20260524.md) |
| Results prose (D3) | [paper_frozen_results_narrative_20260524.md](paper_frozen_results_narrative_20260524.md) |
| Manuscript tables | [paper_result_table_pack_20260524.md](paper_result_table_pack_20260524.md) |
| Three-axis interpretive frame | [core_research_questions_pipeline_review_20260524.md](core_research_questions_pipeline_review_20260524.md) |
| Experiment traceability | [core_research_questions_experiment_source_index_20260524.md](core_research_questions_experiment_source_index_20260524.md) |
| Critical review (applied) | [paper_narrative_critical_review_20260524.md](paper_narrative_critical_review_20260524.md) |
| Manuscript prose draft | [paper_manuscript_draft_20260524.md](paper_manuscript_draft_20260524.md) |

---

# Controlled Hybrid Clinical Extraction Under Benchmark Policy: Task-Dependent Placement on Synthetic Validation

## Abstract (draft)

We study how to design hybrid deterministic + LLM clinical extraction pipelines when benchmark labels, scorer semantics, and dataset policy—not raw note text alone—define success. On **frozen synthetic validation splits only** (Gan 2026 validation, N=299; ExECTv2 validation, **n=40**), with deterministic scorers held fixed, we compare pipeline variants on two epilepsy extraction tasks. We do **not** claim published benchmark parity (Gan Real(300)/Real(150) or CUI-aware ExECT Table 1 remain blocked).

The main empirical finding is **task-dependent hybrid placement**: Gan seizure-frequency extraction is consistent with a recall bottleneck addressed by deterministic temporal candidates before LLM adjudication (80.6% monthly accuracy, GPT 4.1-mini); ExECT phenotyping remains primarily a benchmark-aligned LLM extraction problem with post-LLM bridges and selective guards (92.3% micro F1 on three-family S1; 85.8% on a separate five-family S5 diagnostic surface). A secondary methodological contribution is **arm-vs-mechanism discipline**: 24 preregistered arm rejections document which decomposition, optimizer, and verifier variants failed under explicit gates.

**Non-claims:** beating published benchmarks; clinical deployment readiness; universal local-model parity (Qwen3.6:35b transfer is reported where run, pending for promoted ExECT S5 v2b).

## Paper Scope and Relation to Project Goals

The original project outline (`docs/outline.md`) includes beating ExECTv2 and Gan published benchmarks. **This manuscript does not carry that claim.** Frozen evidence supports a **methods + controlled negative-evidence** paper on synthetic validation. Benchmark reproduction, test holdout, and clinical utility require separate future work with explicit gates (Pathway D4 deferred).

Primary venue story: *how to explore hybrid pipelines rigorously under benchmark policy*, not *state-of-the-art benchmark scores*.

## Thesis

On synthetic validation splits with frozen deterministic scorers, **hybrid pipeline design must follow task bottleneck shape**—but claims must stay within arm-level evidence and explicit benchmark distance. Gan seizure-frequency extraction **improved coincident with** deterministic temporal candidate builders before LLM adjudication (80.6% monthly accuracy with GPT 4.1-mini on N=299); we treat this as **consistent with a recall bottleneck**, not an isolated causal ablation. ExECT phenotyping on **n=40** validation remains primarily a benchmark-aligned LLM extraction problem with deterministic bridges and selective post guards (92.3% micro F1 on three-family S1; 85.8% on the **separate** five-family S5 diagnostic surface—see below). The methodological contribution is **arm-vs-mechanism discipline**: negative results, dataset audits, and scorer semantics as first-class evidence, illustrated by canonical decision arcs rather than experiment catalog size.

## Contributions

1. **A three-axis hybrid exploration framework** (stage graph, deterministic/LLM placement, implementation variant) with explicit `decision_scope: arm` reporting, preventing premature mechanism closure from single failed configs.
2. **Task-dependent operational pipeline graphs** on two benchmark-facing epilepsy tasks: pre-LLM deterministic candidates + LLM adjudication for Gan S0 frequency; single-pass LLM extraction + post-LLM benchmark bridges for ExECT S1/S4; a promoted five-family S5 stack with reject-only frequency verifier (distinct from the S1–S4 ladder).
3. **Three canonical decision arcs** (reader-facing): (a) Gan builder-gap v1 promotion after mid-60s era anchors; (b) ExECT S1 section-split rejection; (c) ExECT S5 combined v2 rejection → v2b verifier isolation.
4. **A consolidated negative-result corpus** (24 rejected arms, `decision_scope: arm`) showing that tested prompt addenda, section decomposition, static pre-vocabulary, verify-repair second passes, and DSPy optimizer arms did not beat frozen hand-designed policy on the named surfaces.
5. **Frozen operational defaults with full traceability**: split, scorer mode, run ID, and config for every headline number (source index: 204 registry experiments).
6. **Preliminary local-model transfer probes** (Discussion / future work until L1.1 completes): Qwen3.6:35b on Gan builder-gap v1 (70.7% monthly) and ExECT S1–S4 replication—**not** on promoted ExECT S5 v2b (zero Qwen runs as of 2026-05-24).

---

## Argument Map

### 1. Problem and gap

**Problem:** Clinical note extraction requires structured facts with evidence, temporal scope, and benchmark-specific label policy—not free-form summarization. Notes encode ambiguous frequency statements, negation, medication temporality, and fine-grained seizure typing that break naive LLM JSON extraction.

**Gap:** Generic LLM extraction runs are insufficient because (a) benchmark gold labels follow dataset-specific normalization and policy rules documented in audits (`docs/datasets/exect/exect_gold_label_audit.md`, `docs/datasets/gan/gan_2026_label_audit.md`), (b) pooled metrics hide family-specific failure modes, and (c) without deterministic scorers and staged error analysis, improvements from prompt tweaks cannot be attributed to mechanisms.

### 2. Dataset and benchmark constraints

| Dataset | Split (headline runs) | Scorer | Scope caveat |
| --- | --- | --- | --- |
| Gan 2026 | `gan_2026_fixed_v1:validation`, N=299 | `gan_frequency_deterministic_v1` | Synthetic validation only; primary gold `seizure_frequency_number[0]`; not Real(300)/Real(150) reproduction |
| ExECTv2 | Fixed **n=40** validation | `exect_field_family_deterministic_v1` (S1), family-specific scorers S2–S5 | Local field-family diagnostics; small-n uncertainty; not CUI-aware Table 1 reproduction |

Both datasets use **synthetic letters on validation splits only**. Published benchmark parity remains **blocked** until Real Gan access and CUI-aware ExECT reproduction gates reopen.

### ExECT S5 surface definition (not “S4 improved”)

S5 is a **separate five-family diagnostic surface**, not the next rung after S4 on the same task:

| Property | S4 ladder rung | S5 diagnostic surface |
| --- | --- | --- |
| Field families | S3 + seizure frequency + medication temporality | Diagnosis, seizure type, annotated medication, investigation, seizure frequency only |
| Medication temporality | In scope | **Excluded** (no native temporality column in prescription gold) |
| Program stack | S4 v1.2 single-pass | Pre-vocab candidates + AM guard + reject-only v2b frequency verifier |
| Scorer | `exect_s4_field_family_deterministic_v1` | `exect_s5_core_field_family_deterministic_v1` |
| Headline micro F1 (GPT) | 65.5% (n=40) | 85.8% (n=40) |

**Do not** present S5 as monotonic improvement along the S1→S4 ladder. Compare S5 only to its own superseded anchors (v1 verifier, AM-guard-only) and to S4 frequency family F1 with explicit metric/scorer caveats.

### Frequency metrics — three non-comparable frames

Report these in **separate Results subsections**; never rank across rows:

| Frame | Dataset / surface | Metric | Scorer | Headline (GPT) |
| --- | --- | --- | --- | --- |
| A | Gan S0 builder-gap v1 | Monthly accuracy | `gan_frequency_deterministic_v1` | 80.6% (N=299) |
| B | ExECT S4 ladder | Seizure frequency F1 | `exect_s4_field_family_deterministic_v1` | 45.7% (n=40) |
| C | ExECT S5 diagnostic | Seizure frequency F1 | `exect_s5_core_field_family_deterministic_v1` | 73.9% (n=40) |

Frames A/B/C differ in label policy, pipeline stack, and metric definition. Cross-frame comparison is methods discussion only, not a performance ranking.

### 3. Method design

**Infrastructure (Layer 1):** Deterministic loaders, Pydantic schemas, gold scorers, run tracking, preregistered gates, cap-25 search grids before full-validation promotion.

**Hybrid doctrine:** Decompose by bottleneck, place determinism where recall or policy alignment is mechanical, keep LLM stages for semantic adjudication and broad clinical interpretation. Test one varied factor per arm against a frozen comparison group.

**Gan S0 winning graph:**

```text
note → deterministic temporal candidate builders → LLM adjudication + evidence quote
     → deterministic frequency normalization → schema validation → scorer
```

**ExECT S1/S4 winning graph:**

```text
note → LLM broad extraction with inline benchmark policy → structured field-family output
     → deterministic benchmark bridges → schema validation → field-family scorer
```

**ExECT S5 promoted stack (2026-05-24 freeze):** high-recall pre-vocab frequency candidates → S5 extraction (v1.2) → reject-only v2b frequency verifier → AM guard (`am_guard_non_asm_brand_alias.v1`). See S5 surface definition above.

**Iteration model note:** GPT 4.1-mini is the rapid iteration and promotion anchor for most frozen arms; Qwen3.6:35b is the local transfer probe where runs exist. This reflects iteration economics, not a claim that hosted mini models are the primary research target (`docs/outline.md` originally centered Qwen3.6:35b).

### 4. Evaluation design

- **Gan:** monthly accuracy (primary benchmark-facing), Purist/Pragmatic category, schema validity, **evidence support** = deterministic check that an extracted quote appears in the source note (diagnostic grounding only; **not** clinician-adjudicated evidence quality).
- **ExECT:** pooled micro F1 with mandatory per-family reporting on **n=40** validation; schema ladder S1→S4 changes **field-family scope** (report as scope expansion, not a calibrated difficulty curve).
- **Promotion gates:** cap-25 for search; full validation for operational defaults; explicit recall/precision tradeoff thresholds for post-LLM guards. **Never** present cap-25 numbers as headline results without scope label.
- **Model comparison:** GPT 4.1-mini (hosted iteration anchor); Qwen3.6:35b via Ollama (local transfer probes on frozen surfaces where run); frozen model-suite profiles (S1/S4/Gan F0) as supplementary bottleneck diagnosis—not operational decision source.

### 5. Results and error analysis

Organize Results into **four blocks** matching the frequency-metric separation above: (1) Gan S0, (2) ExECT S1–S4 ladder, (3) ExECT S5 diagnostic surface, (4) local-model probes (Discussion if L1.1 pending).

#### Gan S0 (operational default) — Frame A

| Metric | GPT 4.1-mini builder-gap v1 | Qwen3.6:35b transfer |
| --- | ---: | ---: |
| Monthly accuracy | **80.6%** | 70.7% (297/299 valid-scored) |
| Purist | 86.0% | 83.2% |
| Pragmatic | 88.6% | 90.6% |
| Schema valid | 100.0% | 99.3% |
| Evidence support† | 100.0% | 99.7% |

†Deterministic quote-in-note check only; not human evidence-quality adjudication.

Run IDs: `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z`; `gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z`.

**Mechanism story (softened):** Monthly accuracy rose from the mid-60s era (verify-repair, temporal-candidates anchors in Table 2) to 80.6% on the builder-gap v1 surface. This is **consistent with** closing temporal candidate recall gaps documented in residual audits, but historical comparisons confound program surface, adjudication policy, and builder code—**not** a single-factor ablation. Residual errors on the promoted surface are predominantly semantic adjudication and builder coverage on no-candidate records (Pathway C3), not missing temporal windows alone.

**Rejected arms (Tier 1):** unknown-overuse guard v1.5 (16.0% monthly cap-25); GEPA G1/G2 (−16.0pp / −28.0pp vs control). `decision_scope: arm`.

#### ExECT schema ladder (GPT 4.1-mini, n=40 validation)

| Level | Field-family scope | Micro F1 | Notable family caveats |
| --- | --- | ---: | --- |
| S1 | Diagnosis, seizure type, annotated medication | 92.3% | Seizure type 90.5%, medication 92.8% |
| S2 | S1 + investigation, comorbidity | 80.9% | Comorbidity 69.3% |
| S3 | S2 + onset, birth history, cause, when diagnosed | 72.1% | Sparse added families weak |
| S4 | S3 + seizure frequency, medication temporality | 65.5% | Seizure frequency **45.7%** (Frame B); med. temporality 62.5% |

Caption every ExECT table with **n=40 validation, synthetic split**. Do not use population-level generalization language.

#### ExECT S5 diagnostic surface (paper-frozen v2b, n=40) — Frame C

| Family | F1 |
| --- | ---: |
| Pooled micro | **85.8%** |
| Diagnosis | 90.0% |
| Seizure type | 84.0% |
| Annotated medication | 88.7% |
| Investigation | 96.7% |
| Seizure frequency | **73.9%** |

Run: `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z`. Incremental gain vs superseded v1 verifier: +1.6pp frequency F1 (72.3% → 73.9%), recall flat at 79.1%. Supersedes AM-guard-only anchor (60.2% freq F1). **GPT-only** as of freeze; Qwen transfer pending (Kanban L1.1).

#### Qwen replication pattern (ExECT S1–S4 only; preliminary)

- S1 (n=40): −13.3pp vs GPT (seizure type 55.7% vs 90.5%).
- S2–S4 (n=40): +0.1 to +2.0pp pooled micro with divergent per-family profiles.
- **Interpretation:** surface-dependent transfer on tested programs; **not** deployment readiness. S5 v2b excluded until L1.1 runs.

#### Cross-dataset bridge

| Dimension | Gan S0 | ExECT S1/S4/S5 |
| --- | --- | --- |
| Primary bottleneck | Temporal candidate recall → semantic adjudication | Benchmark policy + sparse/temporal families |
| Best deterministic placement | **Pre-LLM** candidate builders | **Post-LLM** bridges; selective reject-only guards |
| Best LLM role | Adjudicate injected candidates | Broad extraction with policy during pass |
| Rejected default moves | Prompt-only repair; GEPA optimizers | Section split; static pre-vocab; broad verify-repair |

### 6. Interpretation and limitations

**Interpretation:** Identical hybrid doctrine yields different operational graphs because datasets encode different failure modes. Gan gains on the promoted surface are **consistent with** a recall-first placement hypothesis; ExECT S1/S4 gains align with broad LLM extraction plus post-LLM benchmark bridges. Negative arms (`decision_scope: arm`) support rejecting specific tested variants—not closing entire mechanism classes.

**Limitations (lead in abstract and every ExECT table caption):**

1. All headline numbers are **validation-split synthetic data**; no test holdout or published benchmark reproduction.
2. ExECT evaluations use **n=40** validation records—wide uncertainty on family-level F1.
3. ExECT S5 promoted stack has **no Qwen transfer run** (L1.1 pending); local-model claims stop at S1–S4 + Gan.
4. Evidence support is deterministic quote grounding, not clinician-adjudicated evidence quality.
5. Cap-25 systematically optimistic (~+3.5pp vs full on S1); never mix scopes without annotation.
6. Gan historical comparisons (mid-60s → 80.6%) confound multiple program factors; causal mechanism not isolated.
7. Medication temporality remains open (A4 temporal guard rejected; G0G2 dose-current passes arm gates but is not full S4 solution).
8. Seizure frequency remains the active bottleneck on both datasets despite verifier gains (Gan: semantic mismatch; ExECT S5: precision-dominated qualitative FPs).

---

## Canonical Decision Arcs (reader-facing)

Use these three arcs as the persuasion unit—not registry row count.

### Arc 1 — Gan builder-gap v1 promotion

| Stage | Outcome |
| --- | --- |
| Observation | Mid-60s monthly accuracy on temporal-candidates / verify-repair era |
| Hypothesis | Candidate recall, not prompt addenda, limits Gan S0 |
| Intervention | Deterministic builder-gap v1 + LLM adjudication |
| Result | 80.6% monthly full validation (GPT); Qwen transfer 70.7% |
| Rejected | Unknown-overuse guard (16% cap-25); GEPA G1/G2 |
| Caveat | Historical confounds; synthetic validation only |

### Arc 2 — ExECT S1 decomposition reject

| Stage | Outcome |
| --- | --- |
| Hypothesis | Section/family split improves S1 extraction |
| Arm | S1 section-aware cap-25 |
| Result | 65.6% micro F1 vs 95.8% cap-25 monolithic + bridges baseline |
| Decision | Reject arm; retain single-pass + bridges default |
| Caveat | cap-25 search scope; full validation n=40 anchor separate |

### Arc 3 — ExECT S5 combined v2 reject → v2b isolation

| Stage | Outcome |
| --- | --- |
| Hypothesis | v1.3 extractor + strict qualitative guard + v2 verifier improves frequency |
| Arm | Combined v2 cap-25 |
| Result | Recall −16.0pp; rejected |
| Isolation | v2b temporal/scope rules alone promote (+1.6pp freq F1 full validation) |
| Caveat | Incremental gain; GPT-only; five-family diagnostic surface |

---

## Section Plan

### Introduction

- Motivate structured clinical extraction with evidence and temporal scope.
- **State scope immediately:** synthetic validation only; no published benchmark-beating claim; ExECT n=40.
- Contrast end-to-end LLM extraction with **controlled hybrid exploration under benchmark policy**.
- Preview central finding: **task-dependent hybrid placement**, not one universal recipe.
- Name non-claims: clinical deployment, universal local-model parity, benchmark SOTA.

### Related Work

- ExECTv2 and Gan 2026 benchmark papers and annotation/normalization policies.
- DSPy/programmatic prompt optimization for structured extraction.
- Clinical NLP hybrid pipelines (rules + neural), evidence-grounded extraction.
- Position this work as **methods + negative-evidence methodology**, not benchmark leaderboard paper.

### Data and Benchmark Policy

- ExECTv2: hierarchical schema, certainty, medication temporality, field-family ladder S0–S5.
- **S5 surface definition box** (five-family diagnostic surface; not S4+; MT excluded).
- Gan: seizure frequency normalization, `unknown` vs no-reference distinction, pragmatic vs purist categories.
- Gold-label audits as threats to validity and design constraints.
- Scorer semantics (`docs/policies/deterministic_scorer_semantics.md`); why comparisons require frozen scorer modes.
- **Frequency metrics separation table** (Frames A/B/C).
- Explicit statement: local synthetic validation ≠ published Real(300) or CUI-aware ExECT reproduction.

### Methods

#### System architecture

Four-layer stack: infrastructure, DSPy modules, optimizable configs, experiment orchestration.

#### Three-axis exploration framework

- Axis 1: stage graph (monolithic, decomposed, verify-repair, candidates-adjudicate).
- Axis 2: executor placement (deterministic vs LLM per stage).
- Axis 3: implementation variant (prompt policy, candidate format, verifier style).
- Arm-vs-mechanism vocabulary and preregistration gates.

#### Program variants (headline)

- Gan: `gan_frequency_s0_temporal_candidates_single_pass` + candidate-builder gap v1.
- ExECT S1: single-pass v4.10 + inline benchmark bridges.
- ExECT S5: pre-vocab candidates + AM guard + reject-only v2b frequency verifier.

#### Models and execution

- GPT 4.1-mini (hosted iteration anchor for promotion); Qwen3.6:35b via Ollama (local transfer probes where run).
- Explain why GPT 4.1-mini led iteration (cost/latency/stability)—not because it is the project's primary target model.
- Cap-25 search grids; full-validation promotion protocol.
- Supplementary: frozen model-suite profiles (`model_suite_pattern_interpretation_20260522.md`) for surface-dependent bottleneck diagnosis.

#### Evaluation

- Field-family F1 (ExECT, **n=40**), Gan monthly/purist/pragmatic (N=299), schema validity, evidence support (define once as deterministic quote check).
- Error taxonomy and residual audits (Pathway C Gan; ExECT S5 frequency residual audits).

### Experiments

Organize by **decision informed**, not chronology:

1. **Model-suite bottleneck diagnosis** (frozen S1/S4/Gan F0): surface-dependent model profiles.
2. **Gan candidate-builder gap v1**: deterministic recall intervention + GPT/Qwen full validation.
3. **Gan mechanism search closures** (Pathway C): negative prompt/optimizer arms.
4. **ExECT schema ladder S1–S4**: breadth-pressure characterization.
5. **ExECT S1/S4 negative probes**: decomposition, pre-vocab, verify-repair, optimizers.
6. **ExECT S5 frequency/medication stack**: AM guard, frequency verifier v1→v2b, rejected combined v2 and high-precision candidates.

### Results

Four subsections matching frequency frames: **5.1 Gan S0 (Frame A)** · **5.2 ExECT S1–S4 ladder (n=40)** · **5.3 ExECT S5 diagnostic (Frame C)** · **5.4 Negative arms (D2 Tier 1)**.

Use [paper_result_table_pack_20260524.md](paper_result_table_pack_20260524.md) tables directly:

- Table 1: Gan operational surface (caption: N=299, synthetic validation).
- Table 2: Gan architecture history (caption: confounded historical comparison).
- Table 3: ExECT GPT schema ladder (caption: **n=40**, field-family scope changes per row).
- Table 4: Qwen replication S1–S4 only (caption: preliminary; S5 pending L1.1).
- Table 5: Selected negative/gated findings.
- Supplementary: D2 full arm-reject table (24 rows, Tier 1–4).
- Figure: three canonical decision arcs (see above).

Prose layer: [paper_frozen_results_narrative_20260524.md](paper_frozen_results_narrative_20260524.md).

### Discussion

- **Task-dependent hybrid placement** as the main empirical theme.
- **Methodological contribution:** arm-vs-mechanism discipline via canonical decision arcs.
- **Local vs hosted models:** move to Discussion / future work until L1.1 completes; report Gan + S1–S4 probes with non-parity wording only.
- **Schema breadth vs S5 diagnostic surface:** prevent ladder misread.
- **Benchmark distance:** what would be needed for published parity (Real Gan, CUI-aware ExECT, test holdout)—explicit future work, not current claims.

### Limitations

Consolidate the six limitations above; add registry staleness risk (verify headline rows against `metrics.json` at copy-edit).

### Reproducibility

- Config paths, run IDs, split names, scorer modes for every table row.
- 204-experiment registry + source index appendix.
- Frozen operational defaults (D1) as authoritative number source.
- Code: DSPy programs, deterministic scorers, typed primitives catalog.
- Explicit non-claims: no test-set numbers, no published benchmark beating.

---

## Claim Readiness Matrix

| Claim | Status | Manuscript discipline |
| --- | --- | --- |
| Controlled hybrid exploration under benchmark policy is the paper scope | **Supported** | Lead abstract/intro; demote benchmark-beating |
| Hybrid placement must follow task bottleneck shape | **Supported** | Cross-dataset table; cite Gan + ExECT graphs |
| Gan builder-gap v1 is best internal Gan S0 surface on synthetic validation | **Supported** | Split, scorer, run ID; deny Real benchmark parity |
| Deterministic pre-candidates materially improve Gan vs mid-60s era | **Thin → Supported as correlational** | Table 2 + "consistent with recall bottleneck"; name confounds |
| Gan builder-gap recall mechanism is causally isolated | **Unsupported** | Do not claim; absent single-factor ablation |
| ExECT S1 broad LLM + bridges is frozen narrow-family anchor | **Supported** | n=40; not CUI-aware Table 1 reproduction |
| ExECT S1 decomposition reject (section split) | **Supported** | cap-25 + arm scope label |
| Schema breadth increases difficulty S1→S4 | **Supported with caveat** | Field-family scope changes each rung; n=40 |
| S5 v2b verifier stack (85.8% micro, 73.9% freq) is paper-frozen default | **Supported** | GPT-only; separate surface from S4 ladder |
| S5 is improved S4 | **Rejected framing** | Use S5 surface definition box |
| Qwen transfers Gan builder-gap; not hosted parity | **Supported** | 297 valid-scored denominator; +9.9pp GPT gap |
| Qwen viable on some ExECT S1–S4 surfaces | **Supported (preliminary)** | Not S5; not deployment |
| Arm-vs-mechanism discipline improves interpretability | **Supported (methodological)** | Canonical decision arcs + D2 |
| Evidence support = clinical evidence quality | **Rejected** | Define as deterministic quote check |
| DSPy optimizers replace hand-designed policy | **Rejected as tested** | Arm-level; GEPA G1/G2, BootstrapFewShot |
| Section/family decomposition helps ExECT by default | **Rejected as tested** | S1 cap-25 65.6% vs 95.8% baseline |
| Project beats published ExECT/Gan benchmarks | **Unsupported / blocked** | Real data + CUI-aware gates |
| Qwen matches GPT across tasks | **Risky** | Surface-specific evidence only |
| Clinical deployment readiness | **Risky / unsupported** | Synthetic validation only |
| Combined v2 S5 stack should be default | **Rejected (arm)** | D2 Tier 1; v2b isolation promoted instead |
| High-precision frequency candidates help | **Rejected (arm)** | Recall −12pp cap-25 |

---

## Weak Points To Resolve

| Weak point | Why it matters | Evidence needed | Smallest next action |
| --- | --- | --- | --- |
| No published benchmark reproduction | Reviewers will ask about Real(300)/CUI-aware parity | Real Gan access; CUI-aware scorer reproduction | Keep deferred; state explicitly in abstract/limitations |
| ExECT S5 has no Qwen transfer | Local-model story incomplete for newest promoted stack | Qwen full validation on v2b surface | Preregister Qwen S5 v2b transfer run |
| S5 frequency still bottleneck (73.9% F1) | Weakens broad ExECT claim | Residual taxonomy by error type; preregistered arms | Residual forensics before new model spend |
| Gan monthly vs pragmatic gap (8pp) | Metric interpretation risk | Pragmatic-monthly divergence sub-patterns (Pathway C3) | One paragraph + supplementary breakdown |
| Cap-25 vs full-validation mixing | Overstated gains in prose | Scope labels on every table | Audit manuscript tables for cap-25 rows |
| Bridge vs prompt policy confound on ExECT S1 | Causal attribution incomplete | Full-validation bridge-placement isolation | Deferred experiment; acknowledge in methods |
| Evidence support ≠ evidence quality | Metric overinterpretation | Human spot-check or abstention from strong wording | Define metric as diagnostic in methods |
| Registry/metrics staleness | Copy-edit errors | Re-read `metrics.json` for headline rows | Pre-submission verification pass |
| Medication temporality open | S4/S5 incomplete | G0G2 full-context evaluation or new guard design | Hold as future work; cite A4 rejection |
| Test holdout absent | Generalization unknown | D4 protocol activation | Defer unless manuscript requires holdout |

---

## Highest-Value Revision Loop

1. **Draft manuscript from frozen tables** — four Results subsections (Frames A/B/C + negatives); caption every ExECT table with n=40.
2. **Figure: three canonical decision arcs** — replace registry-scale persuasion with Arcs 1–3.
3. **Run Qwen S5 v2b transfer (L1.1)** — then add §5.4 local-model subsection; until then keep in Discussion/future work.
4. **Pre-submission metrics verification** — re-read primary `runs/<run_id>/metrics.json` for every headline cell.
5. **Abstract pass** — synthetic-only, non-claims, and n=40 in first 150 words.

---

## Artifacts Inspected

| Category | Paths |
| --- | --- |
| Project framing | `docs/outline.md` |
| Critical review | `paper_narrative_critical_review_20260524.md` |
| Paper argument reference | `.agents/skills/paper-narrative-synthesis/references/paper_argument_map.md` |
| Frozen evidence pack | `paper_frozen_operational_defaults_20260524.md`, `paper_frozen_arm_reject_table_20260524.md`, `paper_frozen_results_narrative_20260524.md`, `paper_result_table_pack_20260524.md` |
| Interpretive synthesis | `core_research_questions_pipeline_review_20260524.md`, `paper_synthesis_update_20260524.md`, `24h_progress_and_local_model_gap_review_20260524.md` |
| Hybrid doctrine | `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md` |
| Model profiles | `model_suite_pattern_interpretation_20260522.md` |
| Pathway closure | `pathway_d_paper_evidence_freeze_walkthrough_20260524.md` |
| Promotion reviews | `docs/experiments/exect/exect_s5_frequency_verifier_v2b_full_validation_promotion_review_20260524.md`, `docs/experiments/gan/gan_s0_operational_default_promotion_review_20260523.md` |

---

## Metric and Scorer Caveats (Copy-Edit Checklist)

- **Manuscript type:** methods + controlled negative evidence on synthetic validation—not benchmark SOTA paper.
- **Gan split:** `gan_2026_fixed_v1:validation`, N=299; scorer `gan_frequency_deterministic_v1`; primary gold `seizure_frequency_number[0]`.
- **ExECT split:** fixed **n=40** validation on every ExECT table; family-specific scorers by schema level.
- **S5 ≠ S4 ladder:** five-family diagnostic surface; separate scorer and program stack.
- **Frequency frames A/B/C:** not rank-comparable (see table above).
- **S5 frequency F1 (73.9%)** is not comparable to **Gan monthly accuracy (80.6%)**.
- **Qwen Gan row:** 297/299 valid-scored; two invalid labels excluded from denominator.
- **Evidence support:** deterministic quote-in-note check only; never "clinically grounded."
- **Cap-25 rows:** search/diagnostic scope only unless labeled full validation.
- **Schema ladder:** field-family scope expansion, not difficulty curve.
- **Gan mechanism:** correlational/consistency language only unless ablation added.
- **Local model:** S5 v2b Qwen pending (L1.1)—do not headline in Contributions until run completes.
