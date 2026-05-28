# ExECT task deep review: component groups, error modes, tested mechanisms, and missed fundamentals

Date: 2026-05-28

Decision scope: ExECTv2 extraction tasks, benchmark-facing scorers, and hybrid-pipeline mechanisms. This is a research review, not a code or scorer change.

Related prompt: Gan S0 recently tested a deterministic date/event payload in [`build_deterministic_date_event_payload`](../../../src/clinical_extraction/programs/gan_frequency_s0.py). That test is simple on the surface but targets exactly the substrate LLMs are weak at: temporal anchoring, event enumeration, and calculation across events. This review asks whether ExECT has analogous skipped fundamentals.

## Executive judgment

Yes: ExECT has several likely skipped fundamentals.

The project has tested many prompt variants, model variants, bridge variants, and verifier variants. However, several of the most important ExECT problems have not yet been reduced to explicit typed intermediate payloads before LLM extraction. In particular:

1. ExECT seizure-frequency work has not yet had a Gan-style frequency event/template payload with type association, currentness, zero windows, qualitative changes, and seizure-free intervals represented as structured candidates.
2. ExECT section/list structure has mostly been tested as LLM context routing, not as a deterministic document-structure payload that preserves exact evidence lines and family-specific list membership.
3. Medication temporality has been treated as an inferred label family and guarded post hoc, but not yet audited as a medication lifecycle table that separates benchmark prescription-span policy from richer clinical status.
4. Diagnosis and seizure type now perform well on validation after bridges, but the causal split between annotation-policy guidance, deterministic bridges, and model reasoning is still under-characterized, especially on holdout.
5. CUI-aware annotation reproduction remains blocked. Until that path exists, Table 1-style benchmark claims and ontology-level conclusions are unsafe.
6. Holdout degradation is large enough that ExECT needs a targeted shift audit before treating validation behavior as stable.

The deeper pattern: many "mechanisms" have only been tested as a prompt arm, section-aware arm, or verifier arm. That can reject an implementation, but it does not close the underlying mechanism. The Gan date/event payload is a useful corrective: first expose the hard latent reasoning problem as structured data, then let the LLM adjudicate or verbalize.

## Source map

Core project and policy:

- [Research outline](../../outline.md)
- [Current Kanban plan](../../planning/kanban_plan.md)
- [ExECT gold label audit](../../datasets/exect/exect_gold_label_audit.md)
- [Deterministic scorer semantics](../../policies/deterministic_scorer_semantics.md)
- [Taxonomy primitive catalog](../../taxonomy/taxonomy_primitive_catalog.md)
- [Hybrid pipeline research pivot](../../workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md)
- [Hybrid mechanism status](../../workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md)

ExECT task and experiment references:

- [Post-Gan ExECT experiment structure](exect_post_gan_s0_experiment_structure_20260524.md)
- [S5 core surface design](exect_s5_core_surface_design_20260524.md)
- [S4 gold policy](exect_s4_gold_policy.md)
- [S1 pipeline decomposition audit](exect_s1_pipeline_decomposition_audit_20260524.md)
- [Section-aware ablation design](exect_section_aware_ablation_design.md)
- [Section-aware cap-25 inspection](exect_section_aware_cap25_inspection.md)
- [S1 residual error analysis](exect_s1_residual_error_analysis_20260521.md)
- [S2 residual error analysis](exect_s2_residual_error_analysis_20260521.md)
- [S3 residual error analysis](exect_s3_residual_error_analysis_20260521.md)
- [S4 residual error analysis](exect_s4_residual_error_analysis_20260521.md)
- [S4/S5 frequency gold template audit](exect_s4_s5_frequency_gold_template_audit_20260524.md)
- [S5 frequency residual audit](exect_s5_frequency_residual_audit_20260524.md)
- [S5 frequency post-promotion residual audit](exect_s5_frequency_post_promotion_residual_audit_20260524.md)
- [S5 frequency verifier v2b full validation promotion review](exect_s5_frequency_verifier_v2b_full_validation_promotion_review_20260524.md)
- [S5 Qwen v2b full validation inspection](exect_s5_frequency_verifier_v2b_qwen35b_full_validation_inspection_20260525.md)
- [S5 GPT-5.5 anchor inspection](exect_s5_best_closed_gpt5_5_anchor_inspection_20260526.md)
- [S5 per-family parallel ceiling inspection](exect_s5_per_family_parallel_ceiling_gpt_cap25_v1_inspection_20260524.md)

Synthesis and holdout:

- [Paper result table pack](../synthesis/paper_result_table_pack_20260525.md)
- [Paper claims caveats](../synthesis/paper_claims_caveats_20260525.md)
- [Test holdout evaluation report](../synthesis/test_holdout_evaluation_report_20260527.md)

Prior context:

- [Previous ExECT error analysis](../../archive/prior-context/previous_exect_error_analysis.md)
- [Prior prompt error-analysis synthesis](../../archive/prior-context/prior_prompt_error_analysis_synthesis.md)
- [Previously effective prompts](../../archive/prior-context/previously_effective_prompts.md)

Implementation references:

- [ExECT dataset loader](../../../src/clinical_extraction/datasets/exect.py)
- [ExECT evaluator](../../../src/clinical_extraction/evaluation/exect.py)
- [S1 program](../../../src/clinical_extraction/programs/exect_s0_s1.py)
- [S2 program](../../../src/clinical_extraction/programs/exect_s2.py)
- [S3 program](../../../src/clinical_extraction/programs/exect_s3.py)
- [S4/S5 program](../../../src/clinical_extraction/programs/exect_s4.py)
- [ExECT primitives](../../../src/clinical_extraction/exect/primitives.py)
- [ExECT family backlog](../../../src/clinical_extraction/exect/family_backlog.py)
- [Sectioning helper](../../../src/clinical_extraction/pipeline/sectioning.py)
- [ExECT splits](../../../data/splits/exectv2_splits.json)

## Ground truth and scoring constraints

The ExECT benchmark surface is annotation-policy-bound, not a pure clinical extraction target.

Key constraints from the gold audit and scorer policy:

- Diagnosis gold comes from JSON entities with `DiagCategory=Epilepsy`, affirmed status, and certainty at least 4.
- Seizure type gold comes from diagnosis JSON entities with `DiagCategory=MultipleSeizures` or `SingleSeizure`, not from seizure-frequency rows.
- Prescription gold comes from prescription JSON entities. Temporality is not a native annotation column.
- Investigation, comorbidity, birth history, onset, epilepsy cause, when-diagnosed, seizure frequency, and medication temporality have distinct annotation-policy quirks.
- Diagnosis specificity is collapsed in canonical gold while raw diagnosis values are preserved.
- Excluded or uncertain annotations can be clinically plausible but benchmark-negative.
- Evidence support diagnostics are useful, but they do not currently replace exact set scoring.

This means some model "errors" are actually annotation-policy mismatches. The system should separate:

- benchmark reproduction,
- clinically rich extraction,
- deterministic bridge behavior,
- model reasoning behavior,
- scorer semantics.

## Foundational component groups

| Component group | What it means in ExECT | Why it is hard | Current state |
|---|---|---|---|
| Gold-policy surface | Which annotated entities count for each family | Gold is tied to annotation category, certainty, affirmation, and source JSON/CSV conventions | Loader and scorer policy are now documented and mostly stable |
| Document structure | Headings, lists, clinic summaries, impression sections, medication blocks, historical paragraphs | Family membership is often implied by local structure rather than the sentence alone | Simple sectioning exists; section-aware LLM arm was rejected; deterministic family-span primitive is planned but not implemented |
| Entity family identity | Diagnosis vs seizure type vs frequency vs cause vs comorbidity vs investigation | Same phrase can be relevant to multiple families or none depending on annotation policy | Bridges and prompts handle many S1/S2 cases; sparse S3 and S4 still brittle |
| Temporality/currentness | Current, previous, planned, resolved, historical, "since", "last", "no longer", "per week" | LLMs confuse clinical salience, recency, and benchmark labels | Frequency and medication-temporality remain the clearest weak points |
| Surface normalization | Mapping rich clinical text to benchmark labels | Exact-match scoring punishes synonyms, granularity, and modifier choice | Deterministic bridges are high-value, especially S1 |
| Evidence support | Exact quote support for extracted labels | A quote can support a raw phrase without supporting the normalized label | Evidence is tracked and repaired, but family-specific evidence gating is underdeveloped |
| Stage architecture | Single pass, family split, sequential, verifier, bridge-only, candidate injection | Decomposition can remove useful context or add latency | Several arms rejected, but not all mechanism classes are closed |
| Reporting and reproducibility | Split, model, scorer mode, prompt/program variant, run ID, artifacts | Claims are unsafe if scorer semantics or bridges change silently | Good documentation exists; holdout shift now requires focused follow-up |

## Task ladder and present performance

| Rung | Included families | Validation headline | Holdout headline | Main caveat |
|---|---|---:|---:|---|
| S1 | diagnosis, seizure type, annotated medication | GPT 92.3, Qwen clean 85.9 | GPT 77.8, Qwen 71.8 | Validation looks mature, but holdout drop and bridge/prompt causality are unresolved |
| S2 | S1 + investigation, comorbidity | GPT 82.7, Qwen 84.4 | GPT 70.0, Qwen 67.6 | Comorbidity surface/overlap/atomization drives much of the remaining burden |
| S3 | S2 + birth history, onset, epilepsy cause, when diagnosed | GPT 74.4, Qwen 75.3 | GPT 66.0, Qwen 65.6 | Sparse families have low support and annotation-surface brittleness |
| S4 | S3 + seizure frequency, medication temporality | GPT 65.5, Qwen 67.5 | GPT 57.0, Qwen 62.5 | Frequency and medication temporality dominate the error profile |
| S5 | diagnosis, seizure type, annotated medication, investigation, seizure frequency | GPT 85.8, Qwen 85.4 | GPT 69.4, Qwen 73.3 | Core surface is better, but holdout frequency and seizure type remain weak |

Validation metrics are from the [paper result table pack](../synthesis/paper_result_table_pack_20260525.md). Holdout metrics are from the [test holdout evaluation report](../synthesis/test_holdout_evaluation_report_20260527.md). Holdout was not used for tuning.

## Predominant error modes by family

### Diagnosis

Primary errors:

- over-specific or under-specific diagnosis labels;
- modifier capture, such as treating "symptomatic" as the diagnosis instead of preserving the epilepsy diagnosis;
- false positives from single seizure events or seizure-type evidence;
- uncertainty and differential-diagnosis boundary errors;
- exact-match surface mismatch after clinically reasonable paraphrase.

What improved it:

- benchmark-facing prompt policy;
- deterministic diagnosis benchmark bridge;
- raw-value preservation plus canonical specificity collapse;
- examples that distinguish "single focal seizure" from established focal epilepsy.

Remaining uncertainty:

- how much of current S1 performance comes from prompt policy versus post-bridge normalization;
- why holdout diagnosis drops sharply relative to validation;
- whether diagnosis family can be represented as a structured annotation-policy candidate table before the LLM.

### Seizure type

Primary errors:

- label granularity mismatch, especially ILAE-specific phrases versus gold's coarser benchmark labels;
- inferring seizure type from diagnosis lines;
- treating secondary generalization as a separate seizure type rather than a modifier of the primary seizure;
- missing multiple seizure types when distributed across list/header structure;
- Qwen-specific local gap relative to GPT in some validation analyses.

What improved it:

- explicit benchmark policy examples;
- deterministic seizure-type benchmark bridge;
- prompt boundary examples from prior effective prompts;
- model-specific clean S1 stack.

Remaining uncertainty:

- whether a typed candidate table for seizure-type mentions, modifiers, and annotation category would close the Qwen gap;
- whether holdout seizure-type degradation is a distribution shift, a scorer-surface issue, or a bridge generalization issue;
- whether frequency-type association can improve seizure-type extraction indirectly.

### Annotated medication

Primary errors:

- current medication versus historical/planned/tapered mention confusion;
- brand/generic mismatch;
- non-ASM leakage;
- dose or prescription-line context treated as a separate medication fact;
- recall loss when guards become too strict.

What improved it:

- medication surface bridge and alias handling;
- annotated-medication guard in S5;
- local policy around benchmark prescription spans.

Remaining uncertainty:

- how much medication extraction should depend on a structured medication lifecycle table;
- whether planned/current/previous mentions should be handled as benchmark-facing temporality, clinically rich status, or both;
- whether non-ASM and dose-current guards can be integrated without suppressing valid prescription gold.

### Investigation

Primary errors:

- modality/result surface mismatch;
- planned or unavailable investigation mentions;
- ECG and other non-target investigation leakage;
- family-boundary confusion with history or diagnosis prose.

What improved it:

- S2/S5 inclusion with clean ladder policy;
- investigation bridges and guards;
- high-performing validation S5 investigation scores.

Remaining uncertainty:

- whether investigation is truly solved or just validation-stable;
- whether holdout robustness comes from bridge generalization or favorable support distribution;
- whether a deterministic investigation mention table would reduce residual edge cases.

### Comorbidity

Primary errors:

- atomization mismatch, such as bundled history phrases versus separate gold labels;
- overlap with epilepsy cause, birth history, and general patient history;
- surface normalization;
- annotation scope ambiguity.

What improved it:

- S2 comorbidity bridge and atomization attempts.

Remaining uncertainty:

- whether comorbidity should stay in broad ladder reporting or be treated as an annotation-surface stress test;
- whether a no-model representability audit can separate bridgeable surface cases from true annotation ambiguity;
- whether cause/comorbidity overlap needs a formal policy table.

### Sparse S3 families

Families: birth history, onset, epilepsy cause, when diagnosed.

Primary errors:

- low support and high variance;
- temporal surface ambiguity;
- overlap with comorbidity and diagnosis;
- prose-to-template mismatch;
- weak evidence support for normalized interpretations.

What improved it:

- some family-specific bridges for cause and misplaced seizure/investigation prose.

Remaining uncertainty:

- whether these families are worth optimizing in the main ladder;
- whether they should be reported as exploratory sparse families rather than central benchmark evidence;
- whether a no-model gold-support audit would show deterministic representability or annotation scarcity.

### Seizure frequency

Primary errors:

- qualitative co-label misses and over-emissions;
- seizure-free and zero-rate surface mismatch;
- multi-label blocks;
- prose-to-template conversion;
- spurious extraction on gold-empty documents;
- current versus historical scope;
- type-specific frequency versus flat benchmark labels;
- evidence/candidate echo without sufficient semantic support.

What improved it:

- high-recall candidate injection;
- frequency verifier v1/v2/v2b;
- S5 core-surface narrowing;
- keeping high-recall candidates and rejecting high-precision pruning.

What did not solve it:

- early deterministic template candidates had only 11.6 percent gold coverage in the no-model S4/S5 audit;
- high-precision candidate pruning failed;
- structured slots were not proven under a richer candidate substrate;
- verifier improvements were meaningful but still leave holdout frequency weak.

Remaining uncertainty:

- whether ExECT needs the direct analogue of Gan's deterministic date/event payload: a typed frequency event payload, not just candidate labels;
- whether type association and currentness can be represented deterministically enough to reduce over-emission;
- whether the flat benchmark gold requires extracting all annotated frequency labels or a clinically current subset in certain cases.

### Medication temporality

Primary errors:

- planned/previous/current over-tagging;
- non-ASM leakage;
- dose-current confusion;
- span-inferred labels rather than native temporality annotations;
- broad post-classifier recall collapse.

What improved it:

- narrow guards showed promise in some settings;
- exclusion from S5 avoided letting a noisy inferred family dominate the core result.

Remaining uncertainty:

- whether this is a benchmark family, a clinical status family, or an audit-only family;
- whether a medication lifecycle table can recover precision without recall collapse;
- whether a challenge set is needed before further model work.

## What has been tested

### Gold and loader fixes

Implemented and documented:

- corrected seizure-type source from diagnosis JSON rather than frequency CSV;
- prescription JSON source handling;
- diagnosis specificity collapse with raw values preserved;
- certainty threshold policy;
- missing-gold and gold-quality flags.

These changes are foundational and should not be silently changed.

### Benchmark-facing prompt policy and bridges

S1 success depends heavily on annotation-policy alignment and deterministic benchmark bridges. Raw bridge-free S1 behavior is much worse than bridged behavior, and post-bridge replay can match inline-bridge behavior in key cap/full comparisons.

Interpretation: this is good engineering, but it means the model's clinical reasoning and the benchmark-normalization mechanism are entangled unless explicitly separated.

### Stage graphs and decomposition

Tested:

- single pass;
- section-aware S1;
- verify/repair S1;
- extract-verify without bridges;
- raw post-bridge;
- family split/merge;
- parallel prompt graphs;
- sequential prompt graphs;
- per-family parallel S5.

Rejected arms include section-aware S1, verify/repair S1, some prompt graphs, and per-family parallel S5. These reject particular implementations. They do not reject:

- deterministic family-span payloads;
- sequential context-table extraction;
- family-specific evidence gates;
- structured candidate tables;
- tool-first decomposition.

### Candidate injection and pre-vocabulary

Tested:

- S1 pre-vocabulary arms;
- S4/S5 frequency candidate injection;
- high-recall and high-precision frequency candidate variants;
- medication candidate/bridge variants.

Key lesson: static or shallow candidate lists are not enough. Candidate presentation helps when it exposes the right latent structure and hurts or stalls when it just adds labels.

### Frequency verifier stack

Tested:

- S5 high-recall frequency candidates;
- AM guard plus frequency verifier v1;
- v2/v2b verifier refinements;
- Qwen v2b port;
- GPT-5.5 fixed-stack anchor.

Best validation stack: S5 pre-vocabulary + annotated-medication guard + v2b frequency verifier. GPT-4.1-mini validation micro F1 85.8, frequency F1 73.9. Qwen validation micro F1 85.4, frequency F1 71.4. GPT-5.5 did not displace GPT-4.1-mini under the fixed stack.

Holdout warning: S5 frequency drops to 47.1 for GPT and 58.7 for Qwen.

### Medication temporality guards

Tested:

- broad post-classifier;
- narrow non-ASM and dose-current guard ideas;
- S4 inclusion and S5 exclusion.

Lesson: broad filtering can collapse recall. This family needs a clearer target definition before more prompt tuning.

### Model comparisons

Tested:

- GPT-4.1-mini;
- Qwen 3.5B via Ollama;
- Gemini/Claude in earlier S1 contexts;
- GPT-5.5 fixed-stack anchor.

Lesson: model choice matters, but mechanism clarity matters more. Qwen sometimes matches or beats GPT on broader noisy rungs but lags or shifts on specific families.

## What remains untested or unknown

| Untested or under-tested area | Why it matters | Current evidence gap |
|---|---|---|
| ExECT frequency event payload | Direct analogue of Gan date/event payload; targets temporal scope, type association, and label assembly | Current frequency candidates are label-oriented and had poor no-model coverage before verifier work |
| Deterministic family-span/list payload | Many ExECT facts live in structured note sections and lists | Section-aware LLM context failed, but deterministic span payload was not implemented |
| Medication lifecycle table | Current/planned/previous medication status is a core clinical task and a benchmark ambiguity | Guards exist, but no structured medication status substrate or challenge-set decision |
| Diagnosis/seizure annotation-policy candidate table | S1 validation is strong but bridge/prompt causality and holdout shift remain unclear | Bridges work, but the mechanism is not cleanly isolated |
| CUI-aware Table 1 path | Needed for published-benchmark reproduction claims | Explicitly blocked/deferred |
| Holdout residual taxonomy | Validation-to-test drops are large | Holdout report has metrics but not a full error-mode decomposition |
| Sparse-family representability audits | S3 families may be deterministically unrepresentable or too sparse | Current results mix model weakness, scorer surface, and gold scarcity |
| Family-specific evidence gates | Evidence can support raw text but not normalized labels | Current evidence diagnostics are useful but rarely decision-making |
| Sequential context-table architecture | Per-family parallel failed, but monolithic may succeed by sharing context | Open cell after S5 parallel rejection |

## Fundamental solutions likely skipped

### 1. ExECT frequency event/template payload

This is the closest ExECT analogue to Gan's deterministic date/event payload.

Current S5 frequency work injects candidates and verifies predictions. What is missing is a typed intermediate representation that exposes why a candidate should exist:

- note date if available;
- frequency-bearing section and list context;
- exact evidence line;
- quantified rates;
- implicit rates such as weekly/monthly/daily;
- zero-rate windows;
- seizure-free intervals and `since` anchors;
- qualitative changes such as increased, decreased, infrequent, controlled;
- associated seizure type when local structure allows it;
- current/historical/resolved markers;
- gold-template candidate labels;
- ambiguity flags.

This should be tested no-model first. The previous no-model audit found only 11.6 percent coverage for existing frequency templates. That was a red flag: the LLM and verifier were being asked to compensate for a weak substrate.

Smallest useful pull:

1. Implement an `exect.frequency.event_payload.v1` primitive or payload builder alongside the current rate candidates.
2. Run a no-model coverage audit on validation frequency gold.
3. Only then run cap-25 S5 with the payload injected into the existing v2b stack.

Suggested promotion gates:

- no-model candidate coverage rises materially from 11.6 percent, ideally above 60 percent before model testing;
- candidate noise remains inspectable, for example a small bounded number of candidates per gold-bearing document;
- cap-25 frequency F1 improves at least 3 points, or precision improves at least 5 points without recall dropping more than 3 points;
- non-frequency S5 families do not regress by more than 1 point micro F1.

### 2. Deterministic family-span and list-structure payload

The section-aware S1 arm should not be treated as a rejection of section mechanisms. It was a context-routing prompt implementation that introduced evidence echo and lost context.

The untested fundamental is different: parse document structure into family-relevant spans while preserving exact source text.

Potential payload fields:

- heading path;
- section label;
- line text;
- bullet/list membership;
- nearby header terms;
- family keyword scores;
- exact quote candidates;
- cross-family ambiguity flags.

This would support diagnosis, seizure type, medication, investigation, comorbidity, and frequency without forcing the model into separate section windows.

Smallest useful pull:

1. Implement the planned `exect.sections.family_spans.v1` primitive as metadata, not as an extraction decision.
2. Run no-model audits: gold evidence quote coverage, family-span recall, and false-family span load.
3. Inject top spans into one high-error family first, preferably frequency or seizure type, before broad S1/S5 retesting.

### 3. Medication lifecycle table

Medication temporality is currently a noisy inferred benchmark family, but the clinical problem is real. The project needs to separate:

- prescription-span benchmark extraction;
- current medication list;
- previous medication history;
- planned medication changes;
- taper/stop/increase/decrease actions;
- non-ASM mentions.

Potential payload fields:

- medication surface and normalized alias;
- evidence span;
- section heading;
- action verb;
- status cue;
- current/planned/previous/taper/stop/change classification;
- benchmark prescription-span eligibility;
- non-ASM flag;
- dose-only flag.

Smallest useful pull:

1. Run a no-model medication lifecycle audit on validation S4/S5 documents.
2. Compare lifecycle candidates to annotated medication gold and medication-temporality gold separately.
3. Decide whether medication temporality should be optimized as a benchmark family, moved to a clinical auxiliary task, or kept excluded from S5.

### 4. Diagnosis and seizure annotation-policy candidate table

S1 looks mature on validation, but the holdout drop argues against complacency.

Potential payload fields:

- diagnosis-like mentions;
- seizure-type-like mentions;
- annotation-policy category hints where deterministic evidence exists;
- certainty and negation cues;
- differential/suspected/resolved cues;
- single-event versus established epilepsy cues;
- secondary generalization modifier cues;
- raw surface and bridge candidate;
- evidence span.

Smallest useful pull:

1. Build a no-model residual replay for S1 validation and holdout: raw model output, post-bridge output, gold, and candidate table.
2. Separate failures into model omission, prompt-policy violation, bridge miss, bridge overreach, and scorer/gold ambiguity.
3. Only then design a Qwen-specific or holdout-specific fix.

### 5. CUI-aware annotation reproduction path

The current scorer is useful and deterministic, but it is not yet the CUI-aware Table 1 reproduction path. This limits claims about matching published ExECT results.

Smallest useful pull:

1. Define the CUI-aware normalization target for diagnosis, seizure type, medication, investigation, and frequency.
2. Build a scorer-only replay over gold labels and current predictions without changing programs.
3. Report metric deltas and label classes affected.

This is a prerequisite for any strong published-benchmark comparison claim.

### 6. Holdout shift audit

The holdout report shows large drops, especially S5 GPT frequency and seizure type. This should be treated as a signal, not an afterthought.

Smallest useful pull:

1. For S1 and S5, produce holdout residual samples by family.
2. Compare validation versus holdout support, label distribution, note structure, section availability, and evidence-support rates.
3. Categorize errors using the same taxonomy as validation analyses.
4. Do not tune on holdout; use the audit to choose validation-side stress tests or future challenge sets.

## Actionable Kanban cards

### Card E1: ExECT frequency event payload no-model audit

Objective: Build a deterministic typed payload for ExECT seizure-frequency evidence and measure representability before any model run.

Files likely involved:

- [`src/clinical_extraction/exect/primitives.py`](../../../src/clinical_extraction/exect/primitives.py)
- [`src/clinical_extraction/programs/exect_s4.py`](../../../src/clinical_extraction/programs/exect_s4.py)
- a new audit script under `scripts/` or `src/clinical_extraction/experiments/`
- a new report under `docs/experiments/exect/`

Validation:

- validation split only;
- no model calls;
- report coverage by template class: quantified rate, implicit rate, qualitative change, seizure free, seizure free since year, zero-rate window, multi-type block.

Stop condition:

- if no-model coverage remains low, do not run a model grid. Improve the payload first.

### Card E2: ExECT frequency event payload cap-25 integration

Objective: Inject the E1 payload into the current S5 v2b stack and compare against the promoted S5 baseline.

Validation:

- cap-25 first;
- same scorer and split as existing S5 cap/full runs;
- compare frequency precision, recall, F1, S5 micro, and non-frequency family regressions.

Stop condition:

- reject the arm if gains come only from recall collapse or if diagnosis/seizure/medication/investigation regress materially.

### Card E3: Deterministic family-span primitive

Objective: Implement `exect.sections.family_spans.v1` as a structured payload, not a section-aware prompt decomposition.

Validation:

- no-model evidence coverage audit;
- family-span recall and noise count;
- one-family cap-25 injection only after no-model coverage is acceptable.

### Card E4: Medication lifecycle audit

Objective: Decide whether medication temporality is a benchmark target, clinical auxiliary target, or excluded noisy family.

Validation:

- compare lifecycle table against annotated medication and medication-temporality gold;
- stratify errors by current, previous, planned, taper/stop/change, non-ASM, dose-only.

Decision:

- either define a narrow benchmark-safe guard or keep temporality out of S5 and document the reason.

### Card E5: S1 bridge/prompt/holdout causal split

Objective: Explain how much S1 performance comes from prompt policy, model extraction, and deterministic bridge normalization.

Validation:

- validation plus holdout replay, no holdout tuning;
- raw output versus post-bridge output;
- family-level residual taxonomy.

Decision:

- only pursue Qwen-specific seizure fixes or diagnosis tweaks if the split shows model/prompt errors rather than bridge or distribution issues.

### Card E6: CUI-aware scorer replay

Objective: Unblock Table 1-style benchmark reproduction and identify ontology-level sensitivity.

Validation:

- scorer-only replay first;
- no program changes;
- report metric deltas and affected label classes.

## Suggested next pull order

1. E1: ExECT frequency event payload no-model audit.
2. E2: cap-25 integration only if E1 coverage is strong.
3. E5: S1/S5 holdout residual and bridge/prompt causal split.
4. E3: family-span primitive if E1 shows list/section structure as a major frequency blocker.
5. E4: medication lifecycle audit if the paper needs S4 or temporality claims.
6. E6: CUI-aware scorer replay before any published-benchmark reproduction claim.

## Research-facing claim posture

Safe claims:

- ExECT performance is strongly affected by annotation-policy alignment and deterministic bridge mechanisms.
- S5 core-surface narrowing plus frequency verification improves validation performance over broader S4-style extraction.
- Qwen can approach GPT-4.1-mini on the promoted S5 validation stack, but model differences vary by family and split.
- Some rejected arms are implementation rejects, not mechanism rejects.

Unsafe or premature claims:

- "The system solves ExECT frequency."
- "Section-aware extraction does not help ExECT."
- "Per-family decomposition does not help ExECT."
- "Current metrics reproduce the published ExECT benchmark."
- "Medication temporality is a reliable benchmark family."
- "Validation behavior generalizes to holdout."

## Bottom line

The main missed ExECT fundamental is the same kind of move that made the Gan date/event ablation feel obvious in retrospect: convert the weak LLM subproblem into an explicit, inspectable intermediate representation.

For ExECT, the first such representation should be a seizure-frequency event/template payload. The second should be deterministic family-span/list structure. The third should be a medication lifecycle table. These are more basic than another prompt variant, and they directly target the known failure modes: temporal scope, list structure, currentness, type association, and benchmark-specific surface assembly.

The immediate recommendation is to pull E1 next and require no-model coverage evidence before spending another model run on ExECT frequency.
