# Best Pipeline Benchmark-Context Assessment

Date: 2026-05-21  
Status: Research synthesis note, not a benchmark reproduction claim  
Primary sources: `docs/outline.md`, `docs/policies/published_benchmark_metrics.md`, `docs/experiments/synthesis/experiments_methods_results_20260520.md`, `docs/experiments/synthesis/experiments_narrative_report_20260520.md`, `docs/research_atlas/evidence_matrix.md`, `docs/planning/kanban_plan.md`

## Research Question

How do the project's best currently observed pipelines compare, approximately, to the best published ExECTv2 and Gan results, while acknowledging that the repo does not yet reproduce the published benchmark settings?

## Motivation

The original project goal in `docs/outline.md` was to build a hybrid deterministic + DSPy clinical extraction system that could compete with or exceed published benchmark systems on two related but different epilepsy extraction tasks:

- **Gan 2026:** narrow seizure-frequency extraction with difficult temporal reasoning and canonical frequency labels.
- **ExECTv2:** broad hierarchical epilepsy extraction across diagnosis, prescriptions, seizure frequency, investigations, patient history, and other clinical annotation families.

The repo now has enough local validation evidence to ask a pragmatic comparison question: even without perfect benchmark alignment, are the best current pipelines in the same performance neighborhood as the published systems?

## Method

This note compares published benchmark anchors with the strongest currently documented local pipeline anchors.

### Published Anchors

Published values are taken from `docs/policies/published_benchmark_metrics.md`.

For **Gan 2026**, the relevant published anchors are:

- Real(300), best reported Purist micro-F1: approximately **0.788**.
- Real(300), best reported Pragmatic micro-F1: approximately **0.847**.
- Table 6 synthetic-only training evaluated on Real(300), best Purist micro-F1: approximately **0.776**.
- Table 6 synthetic-only training evaluated on Real(300), best Pragmatic micro-F1: approximately **0.832**.

For **ExECTv2**, the relevant published anchors are:

- All annotations, per-item F1: **0.87**.
- All annotations, per-letter F1: **0.90**.
- Diagnosis per-letter F1: **0.94**.
- Prescription per-letter F1: **0.87**.
- Seizure frequency per-letter F1: **0.68**.

### Local Anchors

Local results are taken from the current promoted or frozen pipeline summaries.

For **Gan S0**, the strongest current pipelines are:

- Hosted GPT 4.1-mini temporal-candidates verify-repair full validation:
  - Run: `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z`
  - Dataset/split: `gan_2026_fixed_v1:validation`
  - Records: 299
  - Scorer: `gan_frequency_deterministic_v1`
  - Monthly-frequency accuracy: **65.1%**
  - Purist category accuracy: **76.5%**
  - Pragmatic category accuracy: **84.2%**
  - Schema-valid prediction rate: **99.7%**
  - Evidence support: **100.0%**

- Local Qwen3.6:35b temporal-candidates verify-repair full validation:
  - Run: `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T230324Z`
  - Dataset/split: `gan_2026_fixed_v1:validation`
  - Records: 299
  - Scorer: `gan_frequency_deterministic_v1`
  - Monthly-frequency accuracy: **65.8%**
  - Purist category accuracy: **75.5%**
  - Pragmatic category accuracy: **82.6%**
  - Schema-valid prediction rate: **99.7%**
  - Evidence support: **100.0%**

For **ExECT**, the strongest current anchors are:

- Hosted GPT 4.1-mini S0/S1 v4.10 validation:
  - Run: `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z`
  - Dataset/split: ExECT validation
  - Records: 40
  - Scope: diagnosis, seizure type, annotated medication
  - Micro F1: **92.3%**
  - Diagnosis F1: **93.8%**
  - Seizure-type F1: **90.5%**
  - Medication F1: **92.8%**

- Hosted GPT 4.1-mini S0/S1 v4.10 test holdout:
  - Run: `exect_s0_s1_validation_test_gpt4_1_mini_20260519T222615Z`
  - Dataset/split: ExECT test
  - Records: 40
  - Scope: diagnosis, seizure type, annotated medication
  - Micro F1: **77.8%**
  - Diagnosis F1: **71.4%**
  - Seizure-type F1: **66.0%**
  - Medication F1: **92.7%**

- Hosted GPT 4.1-mini S4 v1.2 full validation:
  - Run: `exect_s4_validation_full_gpt4_1_mini_20260520T071248Z`
  - Dataset/split: ExECT validation
  - Records: 40
  - Scope: 11 field-family diagnostic view
  - Micro F1: **65.5%**
  - Seizure-frequency F1: **45.7%**
  - Investigation F1: **96.7%**
  - Medication temporality F1: **62.5%**

- Local Qwen3.6:35b S4 full validation:
  - Run: `exect_s4_validation_full_qwen35b_ollama_20260520T160914Z`
  - Dataset/split: ExECT validation
  - Records: 40
  - Scope: same 11-family diagnostic view
  - Micro F1: **67.5%**

## Results

### Gan 2026

The current Gan comparison is the closest to the published benchmark neighborhood.

| System | Evaluation Setting | Purist | Pragmatic | Notes |
| --- | --- | ---: | ---: | --- |
| Published best | Real(300), headline best | ~78.8% micro-F1 | ~84.7% micro-F1 | Published real-letter benchmark |
| Published synthetic-only best | Synthetic training, Real(300) evaluation | ~77.6% micro-F1 | ~83.2% micro-F1 | Table 6 style comparison |
| Our GPT temporal-candidates verify-repair | Synthetic validation, category accuracy | 76.5% | 84.2% | Not real-set reproduction |
| Our Qwen temporal-candidates verify-repair | Synthetic validation, category accuracy | 75.5% | 82.6% | Local model path |

Best-effort interpretation:

- The hosted GPT temporal-candidates pipeline is approximately **1-2 percentage points below** the published Purist anchors.
- The hosted GPT temporal-candidates pipeline is approximately **at or near** the published Pragmatic anchors.
- The local Qwen temporal-candidates pipeline is slightly behind hosted GPT on category metrics but still close to the published synthetic-only benchmark neighborhood.
- Monthly-frequency accuracy remains around **65%**, which indicates that the system is much stronger at coarse clinical bucket assignment than at exact/current frequency normalization.

This supports the view that the Gan S0 pipeline is close to competitive on coarse category performance, but still has an exact-frequency gap.

### ExECTv2

The ExECT comparison is less favorable and less directly aligned.

| System | Scope | Metric | Result | Notes |
| --- | --- | --- | ---: | --- |
| Published ExECTv2 | All annotation families | Per-letter F1 | 90% | Full benchmark system |
| Published ExECTv2 | All annotation families | Per-item F1 | 87% | Full benchmark system |
| Published ExECTv2 | Diagnosis | Per-letter F1 | 94% | CUI/feature-aware published setting |
| Published ExECTv2 | Prescription | Per-letter F1 | 87% | Published setting |
| Our GPT S0/S1 validation | Diagnosis, seizure type, medication | Micro F1 | 92.3% | Narrow three-family validation result |
| Our GPT S0/S1 test | Diagnosis, seizure type, medication | Micro F1 | 77.8% | Narrow three-family holdout result |
| Our GPT S4 validation | 11-family diagnostic view | Micro F1 | 65.5% | Broader but not CUI-aware published reproduction |
| Our Qwen S4 validation | 11-family diagnostic view | Micro F1 | 67.5% | Local model, same diagnostic view |

Best-effort interpretation:

- The narrow S0/S1 validation result looks competitive with published ExECT values, but it covers only three audited field families and should not be treated as parity with the full published system.
- The S0/S1 test holdout gap, from **92.3% validation micro F1** to **77.8% test micro F1**, suggests that the strongest narrow validation result is not yet a stable benchmark-level claim.
- The broader S4 diagnostic view is more comparable in spirit to ExECTv2's broad extraction task, and it is substantially lower: **65.5-67.5% local micro F1** versus published **87-90%** full-system F1.
- ExECT seizure-frequency remains weak locally, with GPT S4 seizure-frequency F1 at **45.7%**, below the published ExECT seizure-frequency per-letter F1 of **68%**.

This supports the view that the current ExECT work is not yet near published broad-system performance, even though some narrow field-family results are strong.

## Interpretation

The best current project pipelines are much closer to published Gan performance than to published broad ExECT performance.

For Gan, the project has likely found a genuinely valuable mechanism: deterministic temporal candidate generation followed by LLM verification and repair. This mechanism appears to recover much of the category-level performance expected from strong published systems, while adding very high evidence support in the repo's diagnostic setting. The remaining gap is not primarily schema validity or evidence support; it is exact frequency normalization and difficult infrequent quantified cases.

For ExECT, the project has learned that narrow field-family extraction can be made strong with careful label-policy alignment, but broad schema performance remains difficult. The S4 ladder shows that adding field families exposes weaknesses in seizure frequency, medication temporality, comorbidity, sparse families, and scope control. The broad ExECT problem is therefore not solved by the current S0/S1 success.

The local-model conclusion is mixed but encouraging. Qwen3.6:35b is credible on Gan under temporal preconditioning and broadly tracks GPT on S2-S4 ExECT diagnostics. However, it has shown model-specific weakness on ExECT S1 seizure-type granularity, so hosted-to-local prompt transfer should be treated as an empirical question rather than an assumption.

## Limitations

This note is deliberately approximate and should not be cited as benchmark reproduction.

Key limitations:

- Gan local results use `gan_2026_fixed_v1:validation`, not the published Real(300) or Real(150) clinician-annotated evaluation sets.
- Gan local metrics report category accuracy from deterministic stored predictions. Published values report micro-F1 under the paper's evaluation setup. These can be numerically close in single-label settings, but they are not automatically identical.
- ExECT local results use normalized field-family scorers, not the full CUI/feature-aware ExECT Table 1 scorer.
- ExECT S0/S1 results cover only diagnosis, seizure type, and annotated medication, not the full published annotation set.
- ExECT S4 local micro F1 aggregates a repo-defined 11-family diagnostic view and should not be interpreted as the same metric as published ExECT All per-letter or per-item F1.
- Evidence quote support is diagnostic in the repo unless explicitly used as an optimizer metric. It should not be substituted for benchmark-facing label performance.
- Many ExECT comparisons use 40-record validation or test splits, so uncertainty is large.

## Current Best Assessment

The current best assessment is:

1. **Gan:** near published category performance, especially under Pragmatic scoring, but with a remaining exact-frequency gap.
2. **ExECT narrow S0/S1:** locally strong, but not enough to claim broad benchmark parity.
3. **ExECT broad S4:** clearly below published ExECTv2 broad-system performance, likely by roughly **20-24 percentage points** depending on which local and published aggregate is compared.
4. **Qwen:** strong enough to remain central to the local-deployment research question, especially for Gan, but not uniformly reliable across ExECT field families.

## Next Experiments

The smallest useful follow-ups are:

1. **Gan external-validity path:** obtain or construct access to the Gan real-letter evaluation setting, or otherwise define a clearly labeled synthetic-only benchmark comparison.
2. **Gan residual error analysis:** focus on the `gold_pragmatic=infrequent` bucket and exact monthly-frequency normalization, because category performance is already close to published anchors.
3. **ExECT broad-scoring path:** implement CUI/feature-aware all-family scoring before making direct ExECTv2 benchmark claims.
4. **ExECT S4 targeted improvement:** prioritize seizure frequency and medication temporality rather than further S0/S1 prompt refinement.
5. **Qwen confirmation:** port only mechanisms with clear hosted evidence to Qwen, and continue treating model-specific failure modes as first-class evidence.

## Bottom Line

Relative to the published systems, the project is **plausibly competitive on Gan category-level seizure-frequency extraction in local synthetic validation**, but **not yet competitive with full ExECTv2 broad extraction**. The most valuable research finding is that deterministic task preconditioning can close much of the Gan gap, while broad ExECT extraction still requires stronger field-family scoring, schema breadth handling, and external-validity work.
