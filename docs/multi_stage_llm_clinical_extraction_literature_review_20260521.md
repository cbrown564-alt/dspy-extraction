# Multi-Stage LLM Pipelines for Clinical Data Extraction: Literature Review

## Research Question

What can recent peer-reviewed literature and credible preprints teach us about using multi-stage LLM pipelines for clinical information extraction, and how should that influence this project's ExECTv2 and Gan epilepsy extraction experiments?

## Scope

This review focuses on clinical data extraction from EHR notes, reports, radiology/pathology text, and related clinical documents. It prioritizes peer-reviewed papers from venues such as JAMIA/JAMIA Open, npj Digital Medicine, npj Precision Oncology, Communications Medicine, JMIR, EMNLP, and credible institutional preprints where the design directly informs multi-stage extraction.

The goal is not a formal systematic review. The goal is to convert the strongest design signals into research decisions and experiment cards for this DSPy-based clinical extraction project.

## Summary Finding

The literature supports this project's hybrid direction, but with an important qualification: the strongest systems are not simply "more LLM calls." They are modular because each stage has a distinct reliability function:

- retrieve or select the right evidence window;
- decompose extraction by field family or relation type;
- constrain outputs with schemas;
- normalize and validate with deterministic rules;
- verify evidence support;
- repair, abstain, or route uncertain cases;
- evaluate with real-world or audit-aware labels, not synthetic fixtures alone.

For this project, the most promising architecture pattern is:

```text
document segmentation / retrieval
  -> field-family extraction
  -> typed normalization
  -> evidence grounding
  -> deterministic validation
  -> selective LLM judge or repair
  -> scorer-facing final label
```

This maps directly onto the current Gan seizure-frequency and ExECT S1/S4 field-family work. The next high-value experiments should test which stages actually add signal, not assume that a longer pipeline is better.

## Key Literature

### Clinical entity augmented retrieval before extraction

Lopez et al. introduce CLEAR, a clinical entity augmented retrieval pipeline for clinical information extraction. CLEAR retrieves note chunks using clinical entities rather than relying only on embedding similarity or full-note prompting. Across 20,000 clinical notes, CLEAR outperformed embedding RAG and full-note approaches, with average F1 scores of 0.90, 0.86, and 0.79 respectively, while also reducing tokens and inference time.

Reference: Lopez et al., "Clinical entity augmented retrieval for clinical information extraction," npj Digital Medicine, 2025. https://www.nature.com/articles/s41746-024-01377-1

Project implication: before spending more effort on prompt wording, test whether the model sees the right evidence. For Gan S0 seizure frequency, full-note prompting may invite confusion between historical and current frequency statements. A retrieval-first or candidate-first design should be treated as a mechanism, not just an implementation detail.

### Schema-first local LLM extraction pipelines

The llm_extractinator paper describes a four-stage open-source framework: task specification, prompt construction, model inference, and post-processing/validation. It supports user-defined schemas, Pydantic or JSON outputs, local Ollama-backed models, optional long/short input handling, and self-correction cycles for schema violations.

Reference: "Leveraging open-source large language models for clinical information extraction in resource-constrained settings," JAMIA Open, 2025. https://academic.oup.com/jamiaopen/article/8/5/ooaf109/8270821

Project implication: our DSPy programs should keep schema and task definitions versioned and explicit. Validation and repair should be first-class stages with recorded failure states, not hidden parser cleanup.

### Multi-stage validation for trustworthy extraction

Mahbub et al. propose a validation framework that combines prompt calibration, rule-based plausibility filtering, semantic grounding assessment, targeted confirmatory evaluation with an independent judge LLM, selective expert review, and external predictive validity analysis. Applied to substance-use disorder extraction from 919,783 clinical notes, rule-based filtering and semantic grounding removed 14.59% of LLM-positive extractions as unsupported, irrelevant, or structurally implausible.

Reference: Mahbub et al., "A Multi-Stage Validation Framework for Trustworthy Large-scale Clinical Information Extraction using Large Language Models," arXiv, 2026. https://arxiv.org/abs/2604.06028

Project implication: use cheap deterministic filters before expensive judge/repair stages. Judge LLMs should be targeted at uncertainty and disagreement, not used as a blanket replacement for benchmark scoring or expert review.

### Agentic extraction and the synthetic-to-real reality gap

Hart and Bergamaschi developed a modular agent-based LLM system for breast cancer synoptic pathology extraction. They normalized CAP protocols into 8 sections, 86 subsections, and 229 discrete fields, then evaluated multiple LLMs using both synthetic test cases and real-world annotated reports. Synthetic accuracy was high, but real-world recall dropped substantially, ranging from 61.8% to 87.7%.

Reference: Hart and Bergamaschi, "Agent-based large language model system for extracting structured data from breast cancer synoptic reports: a dual-validation study," JAMIA Open, 2026. https://academic.oup.com/jamiaopen/article/doi/10.1093/jamiaopen/ooag016/8496817

Project implication: deterministic fixtures are necessary for contracts and edge cases, but they are not performance evidence. Real dev-set examples, audit-aware scoring, and failure-mode tagging are needed before claiming extraction improvement.

### Operational clinical database extraction

UODBLLM integrates LLM extraction into an existing clinical outcomes database using versioned XML prompt templates, configurable batches, schema validation, and standardized JSON storage. In a prostate MRI use case, it processed 1800 reports with 100% completion, 8.90 seconds per report on average, and an estimated cost of US $0.009 per report.

Reference: "Development and Validation of a Generative Artificial Intelligence-Based Pipeline for Automated Clinical Data Extraction From Electronic Health Records: Technical Implementation Study," JMIR Bioinformatics and Biotechnology, 2026. https://bioinform.jmir.org/2026/1/e70708

Project implication: reproducibility metadata matters. Runs should log model, prompt/schema versions, decoding settings, source identifiers, validation outcomes, and repair/judge decisions. This is especially important when comparing local Qwen and hosted GPT variants.

### Biomedical generative IE as frames and relations

LLM-IE provides a Python framework for biomedical generative information extraction covering task definition, prompt design, named entity extraction, entity attribute extraction, relation extraction, data management, and visualization. Its extractor design separates frame extraction from relation extraction.

Reference: Hsu and Roberts, "LLM-IE: a python package for biomedical generative information extraction with large language models," JAMIA Open, 2025. https://academic.oup.com/jamiaopen/article/8/2/ooaf012/8071856

Project implication: field-family decomposition is well supported by the broader IE literature. For ExECT, this argues for extracting diagnosis, seizure, medication, investigation, and history families as separable objects with explicit relation/attribute stages where needed.

### Prompt graph and cross-institution open-weight extraction

Spaanderman et al. evaluated 15 open-weight LLMs on pathology and radiology reports across six use cases, multiple institutes, and multiple languages. They compared zero-shot, one-shot, few-shot, chain-of-thought, self-consistency, and prompt graph strategies. Prompt graph and few-shot prompting improved performance by about 13%, while task-specific factors and annotation variability influenced results more than model size or prompting strategy.

Reference: Spaanderman et al., "Evaluating Open-Weight Large Language Models for Structured Data Extraction from Narrative Medical Reports Across Multiple Use Cases and Languages," arXiv, 2025. https://arxiv.org/abs/2511.10658

Project implication: model size should not be treated as the primary causal explanation. The project should keep emphasizing factor-isolated stage-graph and executor comparisons before broad model comparisons.

### Early few-shot clinical extraction evidence

Agrawal et al. showed that large language models can perform zero- and few-shot clinical information extraction across structured tasks such as span identification, token-level classification, and relation extraction. The paper also highlights the scarcity and fragility of clinical IE benchmarks.

Reference: Agrawal et al., "Large Language Models are Few-Shot Clinical Information Extractors," EMNLP, 2022. https://arxiv.org/abs/2205.12689

Project implication: LLM extraction is plausible, but benchmark design and annotation policy remain central. This aligns with the project's audit-first stance for ExECTv2 and Gan.

### LLaMA vs BERT for clinical NER and relation extraction

The Kiwi/JAMIA study compared instruction-tuned LLaMA models with BERT on clinical NER and relation extraction across multiple note sources. LLaMA improved most in limited-data and cross-institutional settings but came with substantially higher computational cost and slower throughput.

Reference: "Information extraction from clinical notes: are we ready to switch to large language models?" JAMIA, 2026. https://academic.oup.com/jamia/article/33/3/553/8425815

Project implication: local and hosted LLMs should be judged on task value per cost/latency, not F1 alone. Smaller or deterministic components may be preferable for stable subtasks.

## Design Lessons for This Project

### Retrieval and context selection are core experimental factors

CLEAR suggests that evidence retrieval can dominate downstream extraction quality and efficiency. In this project, retrieval should be represented as an explicit stage-graph axis, not a preprocessing convenience.

For Gan S0, this means comparing:

- full-note seizure-frequency extraction;
- deterministic temporal candidate windows;
- entity or phrase retrieved evidence windows;
- candidate table plus LLM adjudication;
- candidate extraction plus verifier/repair.

For ExECT, this suggests stage-graph experiments that compare full-letter extraction against section-aware and field-family evidence windows, especially for seizure, medication, diagnosis, and investigation fields.

### Schema constraints prevent drift but do not guarantee correctness

Schema validation is consistently used in recent systems, but schema-valid output can still be clinically wrong or unsupported. The useful split is:

- schema validity: can the output be parsed?
- semantic validity: does the value obey clinical and benchmark rules?
- evidence support: does the cited text actually support the normalized value?
- scorer validity: does the output match the benchmark label policy?

This is directly relevant to Gan's distinction between `unknown` and `no seizure frequency reference`, and to ExECT's diagnosis, certainty, and medication normalization policies.

### Decomposition should follow clinical and scoring mechanisms

The literature supports decomposition, but the decomposition needs to correspond to meaningful failure modes. For this project, useful stage boundaries include:

- evidence retrieval versus interpretation;
- raw mention extraction versus normalized label;
- current versus historical temporality;
- candidate generation versus adjudication;
- field-family extraction versus cross-family merge;
- deterministic validation versus LLM repair.

Less useful decomposition is stage proliferation without a measurable hypothesis.

### Real validation is non-negotiable

The breast cancer pathology study is an important warning: synthetic cases can overstate readiness by large margins. This project should continue using fixtures for contract coverage, but experiment claims should be based on real held-out or fixed dev examples with dataset-audit caveats.

For Gan, current fixed synthetic validation claims should remain separate from blocked published real-set reproduction. For ExECT, local field-family diagnostics should remain separate from published benchmark reproduction until CUI-aware/all-family blockers are resolved.

### Judge LLMs are best used selectively

The multi-stage validation framework suggests an efficient hierarchy:

1. deterministic schema and plausibility checks;
2. evidence-span support checks;
3. uncertainty or conflict detection;
4. targeted judge LLM review;
5. selective expert review.

For this project, a judge LLM should be evaluated as an intervention with its own false-positive and false-negative profile. It should not silently redefine the gold scorer.

## Recommended Experiment Cards

### Literature Card 1: Evidence-first Gan S0 retrieval ablation

Outcome: a cap-25 comparison between full-note extraction and retrieved/candidate evidence-window extraction for seizure frequency.

Hypothesis: evidence-window extraction reduces historical/current confusion and unsupported frequency labels compared with full-note extraction.

Primary metrics: monthly accuracy, Purist/Pragmatic accuracy, evidence support, unsupported-positive rate, unknown/no-reference confusion.

Dependencies: current Gan temporal-candidates arm and scorer semantics.

### Literature Card 2: Gan S0 validation ladder

Outcome: an ablation that layers schema validation, deterministic plausibility checks, evidence grounding, selective repair, and optional judge review.

Hypothesis: deterministic and evidence checks remove unsupported positives before judge/repair; judge review should be reserved for uncertain or conflicting cases.

Primary metrics: monthly accuracy, unsupported-positive rate, repair rate, abstention rate, judge-disagreement rate, latency/cost.

Dependencies: evidence-first retrieval ablation or current temporal-candidates default.

### Literature Card 3: ExECT S1 field-family prompt graph

Outcome: a stage-graph comparison for S1 that decomposes diagnosis, seizure, and medication extraction into field-family stages and compares against current single-pass policy extraction.

Hypothesis: field-family extraction improves local error interpretability and may improve weaker Qwen family performance, but can regress if merge/bridge policy is not controlled.

Primary metrics: S1 micro F1, per-family F1, evidence support, schema validity, bridge contribution, merge errors.

Dependencies: ExECT S1 stage-graph preregistration; bridge policy must be explicit per arm.

### Literature Card 4: Reality-gap audit for clinical extraction fixtures

Outcome: a small report comparing deterministic fixture performance, cap-25 dev performance, and full validation behavior for one Gan and one ExECT family.

Hypothesis: fixtures catch contract failures but overestimate clinical extraction performance; failure-mode tags should be based on real dev errors.

Primary artifacts: fixture coverage table, dev/full metric comparison, error-mode taxonomy update.

Dependencies: existing fixtures and at least one recent Gan/ExECT inspection.

### Literature Card 5: Run metadata and validation outcome audit

Outcome: an audit of whether run artifacts record the metadata needed for reproducible clinical extraction: model, prompt/schema versions, decoding settings, input identifiers, validation failures, repair decisions, and scorer mode.

Hypothesis: current run tracking captures most experimental metadata but may not expose validation/repair outcomes in a way that supports literature-grade reporting.

Validation: documented gaps plus narrow implementation cards if missing fields are found.

## Recommended Next Pull

The smallest useful next pull is:

1. Write a preregistration for the evidence-first Gan S0 retrieval ablation.
2. Add a validation-ladder design section to that preregistration or a companion preregistration.
3. Keep ExECT S1 field-family prompt graph as the next ExECT card, but do not run it until bridge policy is explicit for every arm.

This keeps the project aligned with the literature while preserving the current discipline: one factor at a time, clear scorer semantics, and no benchmark claims beyond the validated data surface.

## Caveats

This review is selective rather than systematic. It emphasizes papers with direct implications for pipeline design. Some cited studies are preprints or recent articles whose findings should be treated as provisional until independently replicated.

The papers vary in task type, clinical domain, language, and validation standard. Therefore, this review supports experiment design choices, not direct performance expectations for ExECTv2 or Gan.
