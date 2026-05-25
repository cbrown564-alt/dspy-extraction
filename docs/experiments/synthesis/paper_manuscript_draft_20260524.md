# Manuscript Draft — Controlled Hybrid Clinical Extraction Under Benchmark Policy

Date: 2026-05-24  
Status: First prose draft from [paper_narrative_current_20260524.md](paper_narrative_current_20260524.md)  
Decision scope: writing artifact only; numbers cite frozen D1/table pack; no new claims  
Tables: see [paper_result_table_pack_20260524.md](paper_result_table_pack_20260524.md)

---

## Abstract

Structured extraction from clinical letters requires more than mapping free text to JSON. Benchmark-facing tasks impose label normalization rules, temporal scope, negation policy, and evidence requirements that generic large language model (LLM) pipelines often treat as afterthoughts. We study how to explore hybrid pipelines—combining deterministic components with targeted LLM stages—under explicit benchmark policy and frozen scorers.

We report results on **synthetic validation splits only**: Gan 2026 seizure-frequency extraction (N=299, split `gan_2026_fixed_v1:validation`) and ExECTv2 field-family phenotyping (**n=40** validation records). We do **not** claim parity with published Gan Real(300)/Real(150) benchmarks or CUI-aware ExECT Table 1 reproduction; those comparisons remain blocked pending data and scorer gates.

Our main empirical finding is **task-dependent hybrid placement**. For Gan frequency, monthly accuracy on the promoted builder-gap v1 surface reaches **80.6%** (GPT 4.1-mini) when deterministic temporal candidate builders precede LLM adjudication—a pattern **consistent with** a recall bottleneck, though historical comparisons confound multiple program factors. For ExECT, a single-pass LLM extraction with post-LLM benchmark bridges remains the operational default on narrow S1 families (**92.3%** micro F1, n=40); a separate five-family S5 diagnostic surface with reject-only frequency verification reaches **85.8%** pooled micro F1 and **73.9%** seizure-frequency F1 on the same small validation split. These surfaces are not directly comparable.

A secondary contribution is methodological: **arm-vs-mechanism discipline** with preregistered gates and 24 documented arm rejections (`decision_scope: arm`), showing that tested section decomposition, static pre-vocabulary injection, verify-repair second passes, and DSPy optimizer substitutions did not beat frozen hand-designed policy on the named surfaces. Preliminary Qwen3.6:35b transfer probes exist for Gan and ExECT S1–S4 but not yet for the promoted ExECT S5 stack.

**Non-claims:** beating published benchmarks; clinical deployment readiness; universal local-model parity.

---

## 1 Introduction

Clinical notes encode epilepsy phenotypes, treatments, and seizure-frequency statements in prose that resists naive structured extraction. A note may report that a patient is “seizure free since March” while also describing cluster events in a prior window, list current and historical anti-seizure medications in the same paragraph, or use seizure-type labels at a granularity that benchmark annotation guidelines treat differently from colloquial chart language. Extraction systems intended for research benchmarking must therefore align with **dataset policy**—normalization rules, temporality conventions, and field definitions—not only with clinical plausibility.

Recent LLM-based extractors can produce JSON-like outputs at scale, but end-to-end designs make it difficult to attribute gains, audit failures, or separate benchmark alignment from open-ended interpretation. Hybrid pipelines that surround LLM stages with deterministic loaders, validators, normalizers, and scorers offer an alternative: the LLM handles semantic judgment where rules are brittle; deterministic code enforces reproducible benchmark semantics where policy is mechanical.

This paper asks a narrower question than “what is the best extractor?” We ask: **where should deterministic and LLM components be placed** when benchmark policy is held fixed, and **how should negative results be reported** so that failed variants do not get mistaken for closed mechanism classes? We study two epilepsy benchmark tasks with different bottleneck shapes: Gan 2026 seizure-frequency extraction (temporal candidate recall and semantic adjudication) and ExECTv2 field-family phenotyping (broad clinical interpretation with benchmark bridges).

**Scope.** All headline results come from **validation splits on synthetic letter corpora**. ExECT evaluations use **n=40** records; uncertainty at the family level is therefore large and we avoid population-level generalization language. We do not report test-holdout numbers or claim to beat published ExECTv2 or Gan leaderboard results. GPT 4.1-mini served as the rapid iteration anchor for most promoted arms because of cost and turnaround; Qwen3.6:35b appears only where explicit local transfer runs exist.

**Contributions.** We contribute (1) a three-axis framework for hybrid pipeline exploration—stage graph, executor placement, and implementation variant—with explicit arm-level decision scope; (2) task-dependent operational graphs on Gan S0 and ExECT S1/S4/S5 surfaces; (3) three canonical decision arcs that illustrate promotion and rejection logic; (4) a frozen negative-result corpus of 24 rejected arms; and (5) fully traceable operational defaults (split, scorer, run ID, config) for every headline metric.

The central finding previewed here is not a universal recipe. Identical hybrid doctrine yields **different winning graphs** because the tasks encode different failure modes.

---

## 2 Related Work

**Benchmark corpora.** ExECTv2 provides a hierarchical epilepsy phenotyping schema with certainty, temporality, and medication-status distinctions on synthetic clinical letters. Gan 2026 focuses on seizure-frequency normalization with pragmatic and purist category diagnostics. Both corpora ship annotation and normalization policies that differ from raw clinical charting conventions; we treat those policies as part of the task definition.

**LLM structured extraction and DSPy.** Programmatic prompt optimization and modular LLM pipelines can improve extraction quality, but optimizer gains are difficult to interpret when comparison baselines, scorers, and pipeline graphs change together. We report optimizer arms as **tested and rejected at arm scope**, not as evidence that optimization cannot help under other controls.

**Hybrid clinical NLP.** Rule-based and neural components have long been combined for negation, temporality, and terminology normalization. Our work differs in emphasis: we treat **placement** (pre-LLM, during extraction policy, post-LLM bridge) as the primary experimental axis under frozen benchmark scorers, and we foreground negative arms as controls rather than as implementation detail.

We position this manuscript as a **methods and controlled negative-evidence** study on synthetic validation, not as a benchmark leaderboard paper.

---

## 3 Data, Tasks, and Benchmark Policy

### 3.1 Datasets and splits

**Gan 2026.** We evaluate on split `gan_2026_fixed_v1:validation` (N=299) using scorer `gan_frequency_deterministic_v1`. Primary gold for benchmark-facing accuracy is `seizure_frequency_number[0]`; `reference[0]` is retained as a secondary difficulty signal. Letters are synthetic; results do not constitute reproduction of Gan Real(300) or Real(150).

**ExECTv2.** We evaluate on a fixed **n=40** validation subset of synthetic ExECTv2 letters. Scorers are field-family deterministic modes (`exect_field_family_deterministic_v1` for S1; family-specific scorers for S2–S5). These are local diagnostic scores, not CUI-aware Table 1 reproduction.

Gold-label audits (`docs/datasets/exect/exect_gold_label_audit.md`, `docs/datasets/gan/gan_2026_label_audit.md`) document quirks that affect interpretation— for example, Gan distinguishes `unknown` from absent frequency reference, and ExECT medication and seizure-type labels follow benchmark policy that may omit clinically richer distinctions.

### 3.2 ExECT schema ladder versus S5 diagnostic surface

ExECT experiments use two related but **non-nested** reporting surfaces.

The **S1–S4 ladder** expands field-family scope rung by rung: S1 covers diagnosis, seizure type, and annotated medication; S4 adds seizure frequency and medication temporality atop sparse history and comorbidity families. Pooled micro F1 on this ladder should be read as **scope expansion**, not as a calibrated difficulty curve on a fixed label set.

**S5** is a separate **five-family diagnostic surface**: diagnosis, seizure type, annotated medication, investigation, and seizure frequency. Medication temporality is excluded because prescription gold lacks a native temporality column. The promoted S5 program stack adds high-recall frequency pre-vocabulary, an annotated-medication guard, and a reject-only frequency verifier (v2b). It uses scorer `exect_s5_core_field_family_deterministic_v1`.

Readers should not interpret S5 pooled micro F1 (**85.8%**, n=40) as monotonic improvement over S4 (**65.5%**, n=40). The tasks, scorers, and pipelines differ.

### 3.3 Frequency metrics are not rank-comparable

Seizure frequency appears in three reporting frames that **must not be ranked against each other**:

| Frame | Surface | Metric | GPT headline |
| --- | --- | --- | ---: |
| A | Gan S0 builder-gap v1 | Monthly accuracy | 80.6% (N=299) |
| B | ExECT S4 ladder | Seizure frequency F1 | 45.7% (n=40) |
| C | ExECT S5 diagnostic | Seizure frequency F1 | 73.9% (n=40) |

Frames A/B/C differ in label policy, pipeline stack, and metric definition. Cross-frame discussion belongs in methods interpretation, not in a single results ranking.

---

## 4 Methods

### 4.1 System architecture

We implement a four-layer stack: fixed infrastructure (loaders, splits, schemas, deterministic scorers, run tracking), DSPy modules (extraction, verification, repair), optimizable configurations (signatures, prompts, module composition), and experiment orchestration (ablations, promotion gates, error analysis). Every promoted arm records split name, scorer mode, program variant, model/provider, and run ID.

### 4.2 Three-axis hybrid exploration

Pipeline design is explored along three axes:

1. **Stage graph (Axis 1):** monolithic extraction, field-family decomposition, extract-verify-repair, candidates-then-adjudicate.
2. **Executor placement (Axis 2):** deterministic vs LLM responsibility at each stage.
3. **Implementation variant (Axis 3):** prompt policy, candidate format, verifier style, optimizer choice.

Each experiment varies **one factor** against a frozen comparison group when possible. Outcomes are labeled `decision_scope: arm` when a specific configuration fails preregistered gates; arm rejection does not close the underlying mechanism class unless separately justified.

**Cap-25 versus full validation.** Cap-25 subsets support search and ranking; full validation supports operational promotion. Cap-25 results are systematically optimistic on some surfaces (~+3.5 percentage points on ExECT S1 relative to full validation in prior probes) and appear in this paper only with explicit scope labels, chiefly for rejected arms.

### 4.3 Operational pipeline graphs

**Gan S0 (promoted).** Clinical note → deterministic temporal candidate builders → LLM adjudication with evidence quote → deterministic frequency normalization → schema validation → Gan scorer.

**ExECT S1/S4 (promoted narrow/broad ladder).** Clinical note → single-pass LLM extraction with inline benchmark policy → structured field-family output → deterministic benchmark bridges → schema validation → field-family scorer.

**ExECT S5 (promoted diagnostic surface).** High-recall frequency pre-vocabulary → S5 extraction (v1.2 prompt) → reject-only v2b frequency verifier → annotated-medication guard → scorer.

### 4.4 Models

GPT 4.1-mini is the hosted iteration and promotion anchor for most frozen arms. Qwen3.6:35b via Ollama is evaluated as a **local transfer probe** on surfaces where runs exist. This choice reflects iteration economics, not a claim that GPT 4.1-mini is the primary research target model. A frozen multi-model suite on earlier surfaces (S1, S4, Gan F0) provides supplementary bottleneck profiles but is not the operational decision source for promoted arms.

### 4.5 Evaluation metrics

**Gan.** Monthly accuracy is the primary benchmark-facing metric; we also report Purist and Pragmatic category accuracy, schema validity, and evidence support. Evidence support is a **deterministic check** that an extracted quote appears in the source note; it is not clinician-adjudicated evidence quality.

**ExECT.** We report pooled micro F1 with mandatory per-family F1. All ExECT tables in this draft assume **n=40** validation unless stated otherwise.

Promotion gates for post-LLM guards require explicit recall/precision tradeoff thresholds; arms that gain precision by collapsing recall are rejected unless gates say otherwise.

---

## 5 Results

### 5.1 Gan S0 seizure frequency (Frame A)

Table 1 reports the paper-frozen Gan S0 operational default: **candidate-builder gap v1** with GPT 4.1-mini on N=299 validation (`gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z`).

GPT 4.1-mini achieves **80.6%** monthly accuracy, **86.0%** Purist category accuracy, **88.6%** Pragmatic category accuracy, **100.0%** schema validity, and **100.0%** evidence support under the deterministic quote check. Qwen3.6:35b on the same program surface scores **70.7%** monthly accuracy on 297/299 valid-scored records—a preregistered local transfer success that trails GPT by 9.9 percentage points and is **not** hosted parity.

Historical anchors in Table 2 place the promoted surface in context: earlier verify-repair and temporal-candidate eras remained in the mid-60s on monthly accuracy for GPT 4.1-mini. The builder-gap era coincides with higher monthly accuracy and residual error profiles dominated by semantic adjudication and builder coverage on no-candidate records rather than by missing temporal windows alone. Because program surface, adjudication policy, and builder code changed together across eras, we treat the recall-bottleneck explanation as **consistent with** the data, not as an isolated causal ablation.

Pathway C arm rejections reinforce that prompt-only and optimizer substitutions did not substitute for structural changes: an unknown-overuse guard collapsed to **16.0%** monthly accuracy on cap-25, and multistage GEPA variants regressed **−16.0** and **−28.0** percentage points relative to cap-25 controls (`decision_scope: arm`).

### 5.2 ExECT S1–S4 schema ladder (n=40)

Table 3 summarizes GPT 4.1-mini full-validation micro F1 as field-family scope expands:

On **S1** (diagnosis, seizure type, annotated medication), pooled micro F1 is **92.3%**, with seizure-type F1 **90.5%** and medication F1 **92.8%**. **S2** adds investigation and comorbidity (80.9% micro; comorbidity 69.3%). **S3** adds sparse history and cause families (72.1% micro). **S4** adds seizure frequency and medication temporality (65.5% micro); seizure-frequency F1 is **45.7%** (Frame B) and medication-temporality F1 **62.5%**.

The ladder shows that core S1 families are extractable under benchmark policy on this small validation split, while sparse and temporal families degrade pooled scores as scope expands. This pattern is **breadth pressure under changing label sets**, not a fixed-task learning curve.

Negative probes on S1/S4 reject default moves that split the pipeline: section/family decomposition regressed to **65.6%** micro F1 on cap-25 versus a **95.8%** cap-25 monolithic baseline; static pre-vocabulary hints, broad verify-repair second passes, and BootstrapFewShot optimizer arms failed promotion gates on tested surfaces (`decision_scope: arm`). The retained S1 shape is single-pass extraction with inline benchmark bridges.

### 5.3 ExECT S5 diagnostic surface (Frame C)

Table 3 in the operational-defaults pack lists the promoted S5 stack (`exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z`, n=40):

Pooled micro F1 **85.8%**; diagnosis **90.0%**; seizure type **84.0%**; annotated medication **88.7%**; investigation **96.7%**; seizure frequency **73.9%**.

Relative to superseded anchors on the same surface, the v2b verifier promotion adds **+1.6** percentage points seizure-frequency F1 versus the v1 verifier stack (72.3% → 73.9%) with recall flat at **79.1%**, and **+13.7** percentage points versus an annotated-medication-guard-only anchor (60.2% frequency F1). A combined cap-25 arm stacking stricter qualitative guards with the v2 verifier collapsed recall and was rejected; factor isolation implicated guard stacking rather than temporal/scope verifier rules alone.

Seizure frequency remains the weakest family on S5 despite verifier gains; residual audits describe precision-dominated qualitative false positives rather than wholesale recall failure. **No Qwen transfer run exists for this promoted stack as of 2026-05-24** (Kanban L1.1 pending).

### 5.4 Negative arms and local-model probes

Table 5 and supplementary Table D2 consolidate 24 rejected arms with comparison group, varied factor, reject reason, and `decision_scope: arm`. Tier 1 rows from Pathways A and C are the primary manuscript-facing negative evidence: combined S5 v2 stacking, temporal medication guard A4, high-precision frequency candidates, Gan unknown-overuse guard, and Gan GEPA G1/G2.

**Local-model probes (preliminary).** Qwen3.6:35b transfers Gan builder-gap v1 at **70.7%** monthly accuracy and replicates ExECT S1–S4 with surface-dependent deltas: **−13.3** percentage points pooled micro on S1 driven by seizure-type granularity (**55.7%** vs **90.5%** F1), and **+0.1** to **+2.0** percentage points pooled micro on S2–S4 with divergent per-family profiles. These results support **task-dependent** local viability assessments only; they do not establish deployment readiness, and they exclude the promoted S5 v2b stack until L1.1 completes.

---

## 6 Discussion

### 6.1 Task-dependent hybrid placement

The clearest cross-dataset pattern is that **optimal deterministic placement follows bottleneck shape**. Gan S0 rewards deterministic temporal structure **before** LLM adjudication when monthly accuracy is the target under Gan normalization policy. ExECT S1/S4 rewards benchmark policy **during** LLM extraction and deterministic bridges **after** extraction; tested pre-LLM static hints and section splits failed on probed surfaces. ExECT S5 adds **selective post-LLM rejection** for seizure frequency without converting the whole task into a multi-stage decomposition default.

This is not an argument that one hybrid template wins everywhere. It is an argument that pipeline graphs should be chosen after error analysis under frozen scorers, not copied from corpus to corpus.

### 6.2 Methodological contribution: arm-vs-mechanism discipline

Large extraction projects accumulate many failed configs. Without explicit decision scope, teams relabel arm failures as mechanism closures or bury negative runs altogether. Our promoted defaults are accompanied by a structured reject table and three canonical arcs—Gan builder-gap promotion, ExECT S1 decomposition rejection, and ExECT S5 combined-v2 rejection with v2b isolation—that show how gates, confounds, and residual audits interact.

We expect this discipline to matter most when benchmark policy is non-obvious and when pooled metrics hide family-specific regressions—conditions that hold for both corpora studied here.

### 6.3 Local models and benchmark distance

Qwen3.6:35b demonstrates that some frozen surfaces transfer locally with acceptable schema validity, but seizure-type policy alignment on ExECT S1 and monthly accuracy on Gan remain hosted-model advantages on tested programs. Until S5 v2b is evaluated locally, the local-model story is incomplete at the newest promoted ExECT surface.

Separately, all numbers in this draft sit on **synthetic validation** with blocked paths to published benchmark reproduction. Framing the work honestly as internal controlled comparison under benchmark policy is preferable to implying proximity to external leaderboard scores we have not reproduced under the required scorers and data access gates.

### 6.4 Open bottlenecks

Seizure frequency remains difficult in every frame reported here: semantic mismatch residuals on Gan, low S4 frequency F1 on the ladder, and precision-dominated qualitative errors on S5. Medication temporality on ExECT S4 is likewise unresolved: a temporal medication guard improved precision at unacceptable recall cost on cap-25, while other tested arms pass only partial gates.

---

## 7 Limitations

1. **Synthetic validation only; no test holdout.** External validity to real clinical deployment or held-out benchmark splits is unknown.
2. **ExECT n=40.** Family-level F1 estimates are unstable; captions must state n on every ExECT table.
3. **Non-comparable frequency metrics.** Frames A/B/C must not be ranked as a single leaderboard.
4. **S5 is not S4+.** Promoted S5 numbers must not be read as ladder improvement.
5. **Confounded Gan history.** Mid-60s → 80.6% comparisons are correlational across program eras.
6. **Evidence support ≠ evidence quality.** Quote-in-note checks do not substitute for clinician review.
7. **Incomplete local transfer.** S5 v2b lacks Qwen evaluation; local-model claims are preliminary.
8. **Cap-25 optimism.** Search-scope numbers are not headline results unless labeled.

---

## 8 Reproducibility Statement

Headline metrics cite frozen operational defaults in `paper_frozen_operational_defaults_20260524.md` with primary sources in `runs/<run_id>/metrics.json` and configs under `configs/experiments/`. A 204-row experiment registry and source index provide traceability for all registered arms. Scorer semantics are documented in `docs/policies/deterministic_scorer_semantics.md`.

Before submission, every table cell should be reverified against primary metric files. This draft intentionally excludes test-set results and published benchmark-beating claims.

---

## Figure and Table Placeholders

- **Figure 1:** Three canonical decision arcs (Gan promotion; S1 decomposition reject; S5 v2b isolation).
- **Figure 2:** Task-dependent pipeline graphs (Gan pre-LLM candidates; ExECT broad LLM + post bridges; S5 verifier stack).
- **Tables 1–5:** [paper_result_table_pack_20260524.md](paper_result_table_pack_20260524.md).
- **Supplementary Table D2:** [paper_frozen_arm_reject_table_20260524.md](paper_frozen_arm_reject_table_20260524.md).

---

## Draft Provenance

| Source | Role |
| --- | --- |
| [paper_narrative_current_20260524.md](paper_narrative_current_20260524.md) | Structure, claim discipline, section plan |
| [paper_narrative_critical_review_20260524.md](paper_narrative_critical_review_20260524.md) | Scope narrowing, mechanism softening, S5/frequency separation |
| [paper_frozen_operational_defaults_20260524.md](paper_frozen_operational_defaults_20260524.md) | Authoritative numbers |
| [paper_frozen_results_narrative_20260524.md](paper_frozen_results_narrative_20260524.md) | Results phrasing anchor |
