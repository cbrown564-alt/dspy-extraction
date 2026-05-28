# ExECT task decomposition deep dive: component ceilings before schema stacking

Date: 2026-05-28

Status: corrected research framing. This is a research review, not a code, scorer, or split change.

Decision scope: ExECTv2 benchmark-facing extraction, current DSPy program structure, field-family scorers, component-level experiments, and what the current evidence can and cannot support.

## Executive judgment

The ExECT work has answered one important question: performance declines as schema complexity increases. The clean ladder shows that clearly. But that was not the question we most needed to answer first.

The corrected question is:

> What is the best decomposition of ExECT into independently optimizable components, what is the ceiling for each component, and how much performance is lost when those optimized components are stacked into broader schemas?

By that standard, the current ExECT work is only partly decomposed. The evaluator decomposes metrics into field families, and the code contains useful bridges, guards, and verifier variants. But the main extraction programs still ask broad LLM calls to solve too many things at once, especially in S4 and S5. Several experiments reject particular implementations, but they do not close the underlying decomposition question.

The main conclusion is blunt:

1. The ExECT ladder should now be treated as a baseline complexity-stress test, not as the core decomposition study.
2. The project should optimize family-level F1 ceilings first, using frozen benchmark-facing scorers and no-model representability gates.
3. Only after those ceilings are known should the project stack families and measure interference.
4. The most urgent missing decompositions are seizure frequency as event/rate payloads, medication as a current prescription/lifecycle table, family-specific document spans, and the causal split between raw extraction, benchmark bridge, and prompt policy for S1 diagnosis/seizure type.

This is the ExECT counterpart to the Gan S0 deep dive. The difference is that Gan has one headline calculation task. ExECT has many field families whose labels can support, distract from, or contradict each other. That makes decomposition more important, not less.

## Source map

Core project and policy:

- [Research outline](../../outline.md)
- [ExECT gold label audit](../../datasets/exect/exect_gold_label_audit.md)
- [Deterministic scorer semantics](../../policies/deterministic_scorer_semantics.md)
- [Taxonomy primitive catalog](../../taxonomy/taxonomy_primitive_catalog.md)
- [Hybrid pipeline research pivot](../../workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md)

ExECT experiment references:

- [Post-Gan ExECT experiment structure](../../archive/experiments/exect/model_comparison_diagnostics/exect_post_gan_s0_experiment_structure_20260524.md)
- [S1 pipeline decomposition audit](../../archive/experiments/exect/model_comparison_diagnostics/exect_s1_pipeline_decomposition_audit_20260524.md)
- [S4/S5 frequency gold template audit](exect_s4_s5_frequency_gold_template_audit_20260524.md)
- [S5 frequency residual audit](../../archive/experiments/exect/model_comparison_diagnostics/exect_s5_frequency_residual_audit_20260524.md)
- [S5 frequency post-promotion residual audit](../../archive/experiments/exect/model_comparison_diagnostics/exect_s5_frequency_post_promotion_residual_audit_20260524.md)
- [S5 frequency verifier v2b full validation promotion review](exect_s5_frequency_verifier_v2b_full_validation_promotion_review_20260524.md)
- [S5 annotated medication precision assessment](exect_s5_annotated_medication_precision_assessment_20260524.md)
- [S5 medication temporal guard walkthrough](../../archive/experiments/exect/medication_temporality_rejected_arms/exect_s5_medication_temporal_guard_walkthrough_20260524.md)
- [S4 temporality planned/taper error read](../../archive/experiments/exect/frequency_pre_payload_attempts/exect_s4_temporality_planned_taper_error_read_20260520.md)
- [S4 medication precision guard inspection](../../archive/experiments/exect/medication_temporality_rejected_arms/exect_s4_medication_precision_guard_gpt_full_validation_v1_inspection_20260521.md)

Synthesis and holdout:

- [Paper result table pack](../synthesis/paper_result_table_pack_20260525.md)
- [Test holdout evaluation report](../synthesis/test_holdout_evaluation_report_20260527.md)

Implementation references:

- [ExECT dataset loader](../../../src/clinical_extraction/datasets/exect.py)
- [ExECT evaluator](../../../src/clinical_extraction/evaluation/exect.py)
- [S1 program](../../../src/clinical_extraction/programs/exect_s0_s1.py)
- [S2 program](../../../src/clinical_extraction/programs/exect_s2.py)
- [S3 program](../../../src/clinical_extraction/programs/exect_s3.py)
- [S4/S5 program](../../../src/clinical_extraction/programs/exect_s4.py)
- [ExECT primitives](../../../src/clinical_extraction/exect/primitives.py)
- [ExECT frequency slot payload](../../../src/clinical_extraction/exect/slot_payload.py)
- [Sectioning helper](../../../src/clinical_extraction/pipeline/sectioning.py)

## Corrected Research Question

The old framing asked: "What skipped fundamentals explain ExECT errors?"

That was useful but still too downstream. The corrected framing is:

1. What is the optimal task decomposition for ExECT?
2. Which decomposed components can be optimized independently?
3. What is the maximum benchmark-facing F1 for each component before stacking?
4. Which components support each other, and which interfere?
5. How much F1 is lost as optimized components are stacked into broader schemas?
6. Which code paths already implement that decomposition, and which only simulate it inside broad prompts?
7. Which experiments produce component-level knowledge, and which only produce arm-level wins/losses?

The ExECT ladder answered only question 5 in an unoptimized setting. It showed that broader schemas are harder. It did not show whether diagnosis, seizure type, medications, investigations, frequency, or temporality had been individually pushed near their local ceilings.

That distinction matters because a broad-schema F1 drop can come from at least four different causes:

- The component is intrinsically difficult under the gold policy.
- The component was never given the right intermediate representation.
- The component is being damaged by unrelated families in the prompt.
- The component is correct clinically but mismatched to benchmark annotation policy.

The current ladder cannot separate those explanations.

## Proposed Optimal Decomposition

ExECT should be decomposed by layers first and schema rungs second. A schema rung is a reporting surface. It is not the unit of mechanism.

### Layer 0: Benchmark Contract and Gold Policy

Before extracting anything, each family needs an explicit benchmark-facing task contract:

- What counts as a gold label?
- Which raw annotations are authoritative?
- Which source files are primary?
- Which values are missing, noisy, collapsed, or not representable?
- Which clinically true facts should be excluded because they are not in benchmark scope?
- Which label families are headline targets, diagnostic targets, or deferred targets?

ExECT audit guidance that matters:

- Diagnosis gold comes from JSON diagnosis annotations, with epilepsy category, affirmation, and certainty constraints.
- Seizure type should come from annotated diagnosis/seizure-type markup, not inferred from frequency rows.
- Prescription JSON lacks a native temporality column, so current medication interpretation is partly policy-laden.
- Frequency remains special because the CSV frequency labels have semantics that differ from the JSON diagnosis and prescription sources.
- CUI-aware reproduction is still blocked, so benchmark-publication claims remain unsafe until that path exists.

This layer should be separated from model prompting. Otherwise the model becomes responsible for remembering benchmark policy and extracting clinical facts simultaneously.

### Layer 1: Document Structure and Family Spans

ExECT notes are not flat bags of text. The decomposition should first expose:

- Sections and headings.
- Medication lists versus narrative mentions.
- Diagnosis/problem-list statements versus differential or family history statements.
- Seizure description blocks.
- Frequency statements with local temporal context.
- Investigation lists, results, and planned investigations.
- Current, historical, planned, and discontinued medication regions.

The current sectioning helper provides lightweight keyword-based context selection. That is useful, but it is not yet a typed family-span payload. A family-span payload should preserve exact source lines, section names, offsets when available, local negation/certainty cues, and list membership.

This is the analogue of the Gan date/event payload: make the latent structure visible before asking an LLM to adjudicate.

### Layer 2: Mention, Event, and Candidate Inventory

Each family should have an inventory stage that is optimized for recall, not final F1:

- Raw diagnosis mentions.
- Raw seizure-type mentions.
- Medication mentions, aliases, dose-only lines, and prescription-list rows.
- Investigation mentions and result/planned status.
- Comorbidity and background-history mentions.
- Birth/onset/cause/timing mentions.
- Frequency events and rate statements.
- Medication lifecycle events.

The inventory stage should preserve raw values separately from benchmark-normalized values. It should also carry evidence, section, certainty, temporality, and ambiguity flags.

The key point: a candidate inventory is not the final label set. It is the substrate on which the family-specific adjudicator works.

### Layer 3: Family-Specific Normalization and Benchmark Bridge

Each family then needs a deterministic or semi-deterministic bridge from raw candidates to benchmark-facing values.

Examples:

- Diagnosis: raw diagnosis statement -> benchmark diagnosis surface, with generic/specific collapse policy.
- Seizure type: raw seizure phrase -> audited seizure-type label, without importing frequency-only cues as gold.
- Medication: brand/generic alias -> annotated medication surface, preserving current prescription scope.
- Investigation: raw test phrase -> benchmark investigation label.
- Frequency: event/rate representation -> audited benchmark frequency label set.
- Medication temporality: medication lifecycle row -> current/past/planned/tapering label if that family remains in scope.

This layer should be separately measurable. The S1 bridge effect shows why: raw policy mismatch can dominate apparent model performance.

### Layer 4: Within-Family Adjudication

Only after inventory and bridge should the component decide the final family label set.

Within-family adjudication includes:

- Inclusion versus exclusion.
- Negation, certainty, and historical status.
- Specificity collapse.
- Duplicate merge.
- Multi-label retention.
- Current-scope selection.
- Precision guards.
- Recall-preserving repairs.
- Abstention when evidence is insufficient.

This is where maximum component F1 should be optimized. The primary metric should be family F1 on the validation split, with precision/recall shown separately. Pooled micro F1 should not be the main tuning target at this stage.

### Layer 5: Cross-Family Support and Contradiction

Only after within-family ceilings are known should families be allowed to interact.

Some interactions are supportive:

- Seizure-type mentions can help interpret which frequency statement belongs to which seizure type.
- Medication list structure can help medication temporality.
- Diagnosis context can disambiguate whether a seizure mention is current epilepsy or remote history.
- Investigation sections can distinguish completed tests from planned tests.

Other interactions are dangerous:

- Seizure frequency rows should not create seizure-type gold labels.
- Family history or differential diagnosis should not create patient diagnosis labels.
- Medication temporality guards should not erase current medications merely because the exact line lacks explicit "current" language.
- Comorbidity and epilepsy cause can overlap but are not the same benchmark family.
- Frequency labels can be clinically plausible but outside the audited benchmark templates.

The project needs pairwise interaction tests before broad-stack tests. Otherwise an apparent S4/S5 failure can hide multiple opposing effects.

### Layer 6: Evidence Support

Evidence support should remain diagnostic unless an experiment explicitly changes the scoring target.

For ExECT, evidence needs two levels:

- Raw evidence support: does the quoted text support the raw extracted phrase?
- Normalized-label support: does the quoted text support the benchmark-normalized interpretation?

The current deterministic scorer tracks evidence diagnostics separately from benchmark F1. That is the right default. But component experiments should still report evidence failures because they explain precision errors and bridge overreach.

### Layer 7: Schema Assembly and Interference Measurement

Stacking comes last.

Once family ceilings exist, build:

- S1*: optimized diagnosis + optimized seizure type + optimized annotated medication.
- S2*: S1* + optimized investigation + optimized comorbidity, if comorbidity is representable.
- S3*: S2* + optimized sparse/timeline families, if they clear representability gates.
- S4*: S3* + optimized frequency + medication temporality, if temporality remains headline.
- S5*: optimized core surface: diagnosis + seizure type + annotated medication + investigation + seizure frequency.

Then measure:

- Pooled micro F1.
- Per-family F1.
- Family deltas relative to isolated ceilings.
- Pairwise interaction losses.
- Evidence diagnostic changes.
- Validation-to-holdout transfer.

Only this lets us say whether complexity itself causes decline, or whether broad prompts are degrading unoptimized components.

## Component Map

The table below is the decomposition ExECT should use before another broad schema sweep.

| Component | Independent F1 target | Subcomponents to separate | Supports | Contradictions and leakage | Current maturity |
| --- | --- | --- | --- | --- | --- |
| Diagnosis | Patient-level benchmark diagnosis labels | raw diagnosis mention, certainty, affirmation, specificity collapse, benchmark bridge | seizure descriptions can support context | family history, differential diagnosis, generic parent overcount, seizure type leakage | high validation after bridges, weaker holdout, causal split still incomplete |
| Seizure type | Benchmark seizure-type labels from audited markup | raw seizure event/type mention, certainty, specificity, bridge | frequency type association, diagnosis context | frequency rows should not create seizure-type gold; semiology can be historical or differential | strong validation in S1, weaker holdout, bridge/prompt effects entangled |
| Annotated medication | Current benchmark medication labels | medication mention inventory, alias bridge, current prescription list, non-ASM guard, dose-only line handling | medication temporality and prescription sections | broad S5 prompts over-emit non-ASM or historical drugs; temporality guards can erase true current meds | near-ceiling in S1, degraded by S5 interference, AM guard helpful |
| Investigation | Benchmark investigation labels | test mention, result versus planned, section/list status, bridge | investigation sections and epilepsy workup context | planned/refused/family history tests, broad medical history | high and stable; likely close to ceiling but needs isolated confirmation |
| Comorbidity | Benchmark comorbidity labels | comorbidity mention, patient versus family, history versus cause, bridge | background history | epilepsy cause, diagnosis, family history, unrelated medical context | weak/noisy; should be diagnostic until representability is known |
| Birth history | Benchmark birth-history labels | perinatal mention, patient scope, temporal cue | onset/cause context | family history and background narrative | sparse; needs no-model representability first |
| Onset | Benchmark onset/timing labels | age/date extraction, patient scope, first seizure versus diagnosis date | diagnosis and frequency chronology | "since childhood" ambiguity, copied history, family history | sparse/timeline family; not yet independently optimized |
| Epilepsy cause | Benchmark cause labels | etiology mention, certainty, patient scope | diagnosis and comorbidity | comorbidity overlap, speculative cause, risk factor versus cause | sparse/noisy; should not drive headline stack yet |
| When diagnosed | Benchmark diagnosis-timing labels | date/age mention, diagnosis event versus first seizure | diagnosis history | onset and historical seizure narrative | sparse; needs temporal primitive before broad stack |
| Seizure frequency | Benchmark frequency label set | event inventory, type association, currentness, rate normalization, qualitative change, seizure-free windows, zero-rate windows, multi-label retention | seizure type, temporal sections | clinically true but off-template values, historical rates, candidate echo, type/range mismatch | main bottleneck; current candidate coverage too low, verifier improves precision but not representation |
| Medication temporality | Benchmark medication-temporality labels if retained | medication lifecycle row, current/past/planned/tapering, dose-only status, planned change | medication inventory and prescription sections | over-pruning current meds, future plan versus current prescription, no native gold temporality column | unstable; guards improved precision but collapsed recall in tested arms |

This table implies a different experiment agenda from the historical ladder. The target is not "can one prompt do all of this?" The target is "what is the best possible answer for each row, and what breaks when rows are combined?"

## Current Code Decomposition Audit

### Evaluator and Scorer Structure

The scorer structure is the cleanest part of the current decomposition.

Current field-family surfaces:

- S1: `diagnosis`, `seizure_type`, `annotated_medication`.
- S2: S1 plus `investigation`, `comorbidity`.
- S3: S2 plus `birth_history`, `onset`, `epilepsy_cause`, `when_diagnosed`.
- S4: S3 plus `seizure_frequency`, `medication_temporality`.
- S5: `diagnosis`, `seizure_type`, `annotated_medication`, `investigation`, `seizure_frequency`.

This gives the project useful per-family metrics. It does not by itself imply that the programs are decomposed. The scorer can tell us which family failed after a broad run. It cannot tell us whether that family would have worked if extracted independently with the right substrate.

The evidence diagnostics are also correctly separated from benchmark F1. That should stay true unless a specific experiment explicitly changes the target.

### S1 Program

The S1 code contains the most useful decomposition work so far:

- It has variants for single-pass extraction, pre-vocabulary prompting, family prompt graphs, clean ladder prompts, section-aware context, deterministic-only diagnostics, and verify-repair arms.
- It contains benchmark bridges for diagnosis, seizure type, and medication.
- It includes a substantial label-policy prompt.
- It reports family-level results through the scorer.

But S1 is still not fully decomposed.

The label policy, raw extraction, family bridge, and final adjudication are tightly coupled. The S1 validation result is excellent, but it is hard to say how much of that score comes from:

- The model extracting correct raw clinical facts.
- Prompt text encoding the benchmark policy.
- Deterministic bridge repair.
- Gold label collapse.
- Medication alias normalization.
- Dataset split difficulty.

The S1 stage graph and executor audits are useful because they tested some of these choices. However, those were mostly cap-25 implementation comparisons. They do not yet establish isolated family ceilings or holdout-robust mechanisms.

### S2 and S3 Programs

S2 and S3 mainly extend the field-family surface. They are valuable ladder rungs, but weaker decomposition instruments.

S2 adds investigation and comorbidity. Investigation performs strongly. Comorbidity is much less mature and likely carries label-policy and representability problems.

S3 adds sparse timeline/background families: birth history, onset, epilepsy cause, and when diagnosed. These are exactly the kind of families that should have no-model representability and temporal-candidate audits before being included in a broad prompt. In the current evidence base, they mostly function as complexity additions rather than optimized components.

### S4 and S5 Program

S4 is where the current program most clearly asks too much at once.

The S4 field-family signature asks one model call to extract many heterogeneous families: diagnosis, seizure type, medication, investigation, comorbidity, birth history, onset, epilepsy cause, when diagnosed, seizure frequency, and medication temporality. These families require different evidence windows, different normalization policies, and different adjudication rules.

That broad signature is useful as a stress test. It is not an optimal task decomposition.

S5 improves the reporting surface by narrowing the scored core to diagnosis, seizure type, annotated medication, investigation, and seizure frequency. But several S5 variants still use S4-style broad extraction internally, then score only a subset. This means S5 can look like a core decomposition while still suffering from broad-prompt interference.

The promoted S5 v2b stack is operationally useful:

- It uses frequency pre-vocabulary support.
- It uses an annotated-medication guard.
- It applies a frequency verifier.
- It improved validation micro F1 and frequency precision relative to earlier S5 frequency arms.

But it is not a complete component stack. The frequency verifier bundles multiple decisions: label validity, qualitative evidence, current temporal scope, candidate echo, and rejection. It helps precision, but it does not replace a real event/rate payload or a no-model coverage gate.

The rejected per-family parallel S5 arm is also easy to overinterpret. It rejected one parallel implementation. It did not prove that family decomposition is wrong.

### Primitive and Payload Layer

The primitive layer has several useful mechanisms, but it is uneven.

Implemented or partially implemented pieces include:

- Diagnosis benchmark bridge.
- Seizure-type benchmark bridge.
- Medication benchmark bridge and guard logic.
- Frequency candidate generation.
- Frequency benchmark bridge.
- Frequency verifier support.
- Medication temporality classifier/guards.
- Lightweight section selection.

The most important gap is that some primitives are label-set oriented rather than event oriented.

For seizure frequency, the current candidate builder can produce benchmark-like labels, but the no-model audit showed very low gold coverage. The slot payload is a structured representation of candidate labels, not yet a full frequency event/rate substrate with type association, currentness, evidence, ambiguity, zero windows, and seizure-free intervals.

For medication, the current guard can repair broad S5 over-emission. But there is not yet a first-class current prescription/lifecycle table that separates:

- current medication presence,
- historical medication mention,
- planned start,
- planned stop,
- tapering,
- dose-only evidence,
- non-ASM medication,
- brand/generic alias.

For document structure, `section_note` and `select_context` are useful but too shallow to serve as the final family-span layer. The taxonomy catalog already marks `exect.sections.family_spans.v1` as planned. That remains a major missing substrate.

## Experiment Evidence Audit

### What the Ladder Proved

The clean ladder showed that performance declines as schema complexity increases.

Validation anchors from the synthesis pack:

| Rung | GPT validation micro F1 | Qwen validation micro F1 |
| --- | ---: | ---: |
| S1 | 92.3 | 85.9 |
| S2 | 82.7 | 84.4 |
| S3 | 74.4 | 75.3 |
| S4 | 65.5 | 67.5 |

This is real evidence. It supports the claim that wider schemas are harder.

But the ladder did not establish:

- Component ceilings.
- Optimal family-specific prompts.
- Whether S4 failure is due to frequency, temporality, sparse families, prompt interference, or all of them.
- Whether S3 sparse fields are representable from the available gold and note text.
- Whether S5 should be built from optimized components rather than by trimming an S4-style extractor.

So the ladder should be cited as an unoptimized complexity baseline, not as proof that the current decomposition is right.

### S1 Pipeline Evidence

The S1 audit is the best evidence that benchmark policy matters.

Important results:

- Inline benchmark bridges achieved strong cap-25 performance.
- Raw/no-bridge policy variants regressed sharply.
- Some verify-repair and family-split implementations regressed.
- Medication and seizure hints did not automatically improve the program.

This supports the claim that S1 performance depends heavily on benchmark alignment. It does not yet give a clean family-by-family maximum:

- diagnosis ceiling,
- seizure-type ceiling,
- medication ceiling,
- bridge-only contribution,
- prompt-policy contribution,
- raw extraction contribution,
- holdout sensitivity.

The holdout report makes this gap more important. S1 validation looked strong, but S1 holdout family F1 was materially lower:

- GPT S1 holdout: diagnosis 71.4, seizure type 66.0, annotated medication 92.7.
- Qwen S1 holdout: diagnosis 66.7, seizure type 52.2, annotated medication 93.3.

Medication transfers relatively well. Diagnosis and seizure type do not. That suggests S1 is not fully solved even if validation looked near-ceiling.

### S4/S5 Frequency Evidence

Frequency has the clearest evidence of a missing substrate.

The no-model frequency gold-template audit found:

- 40 validation documents.
- 24 documents with frequency gold.
- 43 gold labels.
- 11 candidate labels.
- 5 matched labels.
- 38 missed labels.
- gold-label coverage 11.6 percent.

By label type, coverage was poor across quantified, qualitative, seizure-free, zero-rate, and other qualitative labels.

This should have been treated as a hard gate: the deterministic candidate substrate was not representative enough to support a candidate-first model grid.

The later S5 frequency work still produced useful gains:

- Pre-verifier frequency F1 was 60.2, with high recall and low precision.
- Post-promotion v1 improved frequency F1 to 72.3, mainly through precision.
- v2b improved full validation frequency F1 to 73.9 for GPT 4.1-mini, with micro F1 85.8.
- Qwen v2b reached validation micro F1 85.4 and frequency F1 71.4.

Those are operational improvements. But they do not close the frequency decomposition question because:

- Candidate coverage was known to be low.
- The verifier improves rejection discipline, not event discovery.
- The current payload is label-oriented rather than event-oriented.
- Holdout frequency remains weak:
  - GPT S5 holdout frequency F1 47.1.
  - Qwen S5 holdout frequency F1 58.7.

The right next step is not another broad S5 verifier tweak. It is a frequency event/rate payload audit.

### Medication Evidence

Medication has two different stories.

In S1, annotated medication is strong. Holdout medication remains high:

- GPT S1 holdout annotated medication F1 92.7.
- Qwen S1 holdout annotated medication F1 93.3.

In S5, medication degraded because broader extraction introduced precision failures. The annotated-medication precision assessment showed:

- S1 frozen medication: precision 90.0, recall 95.7, F1 92.8.
- S5 baseline medication: precision 56.1, recall 97.9, F1 71.3.
- S5 frequency pre-vocab medication: precision 59.0, recall 97.9, F1 73.6.

The no-model guard simulation suggested a large recoverable precision gain:

- Drop non-ASM plus existing bridge: precision 78.0, recall 97.9, F1 86.8.
- Drop non-ASM plus eplim repair: precision 77.0, recall 100.0, F1 87.0.

This is strong evidence of broad-schema interference. Medication itself is not inherently low-ceiling. The stack damaged it.

Medication temporality is different. The tested post-classifier and temporal guards often improved precision at the cost of unacceptable recall loss:

- The planned/taper H1 post-classifier improved precision but reduced F1 from 62.5 to 55.9 and recall from 95.7 to 55.3.
- The S5 A4 temporal medication guard reached precision 100.0 on cap25 but recall collapsed to 79.3.

This suggests the medication family should be decomposed into:

- annotated current medication, which is close to solvable;
- medication lifecycle/temporality, which needs a separate table and may not belong in the headline core until gold policy is clearer.

### Investigation, Comorbidity, and S3 Families

Investigation appears comparatively stable. In holdout:

- GPT S2 investigation F1 94.4.
- Qwen S2 investigation F1 90.4.
- GPT S5 investigation F1 90.4.
- Qwen S5 investigation F1 97.2.

This family may be close to ceiling, but that should still be confirmed in an isolated component run. It is possible that investigation is easy enough that the broad prompt does not damage it much.

Comorbidity is not in the same state. Holdout comorbidity F1 sits near the low-to-mid 50s in S2-S4. It likely needs a representability audit and an overlap analysis with diagnosis, cause, and background history before it is treated as a headline component.

S3 families are sparse and timeline-like. Birth history, onset, epilepsy cause, and when diagnosed should not be optimized by broad-prompt sweep first. They need:

- no-model gold representability,
- temporal candidate inventory,
- patient-versus-family scope checks,
- overlap with diagnosis/comorbidity/cause,
- support counts before any claim of ceiling.

### Holdout Evidence

The holdout report is a warning against validation-only confidence.

Holdout micro F1:

| Rung | GPT holdout micro F1 | Qwen holdout micro F1 |
| --- | ---: | ---: |
| S1 | 77.8 | 71.8 |
| S2 | 70.0 | 67.6 |
| S3 | 66.0 | 65.6 |
| S4 | 57.0 | 62.5 |
| S5 | 69.4 | 73.3 |

The test split is small, so this should not be overclaimed. But it is enough to show that validation improvements are not automatically stable. It also shows that model ordering can change: Qwen S5 beats GPT S5 on holdout despite similar validation anchors.

For decomposition, the implication is simple: tune components on validation, then use holdout only to audit transfer and residual failure modes. Do not chase holdout.

## What We Have Learned

### 1. Complexity Decline Is Real but Under-Explained

The ladder proves that broader schemas hurt performance. It does not explain why.

The decline can reflect:

- More fields.
- Harder fields.
- Noisy fields.
- Sparse fields.
- Wider prompts.
- Cross-family interference.
- Unoptimized candidates.
- Label-policy mismatch.

The next ExECT work must separate these causes.

### 2. Benchmark Alignment Can Dominate Model Ability

S1 bridge results show that benchmark policy alignment can move scores dramatically. A model can know the clinical fact and still miss the benchmark label. Conversely, a bridge can recover benchmark labels even if the model output is not in exact gold form.

This is why every component needs a raw-versus-bridge split.

### 3. Some Families Are High-Ceiling and Interference-Sensitive

Annotated medication is the clearest example. It performs well in S1 and degrades under S5. That is not evidence that medication extraction is intrinsically hard. It is evidence that wide extraction changes model behavior and admits false positives.

The right response is to optimize medication independently, then reintroduce it into stacks while measuring interference.

### 4. Frequency Needs an Event/Rate Payload, Not Just Label Verification

The frequency verifier improved precision, but frequency remains a representation problem. The no-model coverage audit showed that current deterministic candidates miss most gold labels.

The missing payload should represent:

- frequency expression span,
- count,
- period,
- qualitative frequency phrase,
- seizure-free interval,
- zero-rate statement,
- current versus historical scope,
- seizure-type association,
- local section,
- local time window,
- exact evidence,
- ambiguity flags,
- candidate benchmark labels.

Until that exists, frequency experiments are tuning around an unstable substrate.

### 5. Medication Temporality Should Not Be Bundled With Medication

Current medication labels can be optimized separately. Medication temporality needs lifecycle reasoning and unclear gold policy because prescription JSON does not provide a clean native temporality column.

Post-hoc temporality guards can collapse recall. That does not mean temporality is impossible. It means the decomposition is wrong: use a lifecycle table first, then decide whether temporality is headline, diagnostic, or deferred.

### 6. Rejected Implementation Arms Are Not Mechanism Closure

The rejected per-family parallel S5 arm matters. The rejected frequency high-precision arm matters. The rejected medication temporal guard matters.

But none of those prove that:

- family decomposition is bad,
- high-precision frequency is impossible,
- medication temporality is unsalvageable.

They prove those implementations did not work under those settings.

The project should explicitly label arm-level rejections versus mechanism-level closure.

### 7. No-Model Representability Gates Need More Authority

The frequency no-model audit produced a clear warning, but the project still proceeded into later model work. That model work found useful improvements, but it also left the core representation gap unresolved.

Future gates should be stricter:

- If candidate/gold coverage is very low, do not run a broad model grid on that substrate.
- If gold support is sparse or noisy, mark the family diagnostic/deferred before including it in a headline stack.
- If a bridge changes score materially, isolate bridge effects before reporting model effects.

### 8. Holdout Shift Is Now a First-Class Research Object

Validation is where components should be optimized. Holdout is where stability should be audited.

The holdout degradation, especially for diagnosis, seizure type, and frequency, suggests that component-level residual analysis is needed before making broad claims.

## What the Current Experiments Do Not Yet Tell Us

The current evidence does not yet tell us:

- the best achievable diagnosis F1 under a raw/bridge split;
- the best achievable seizure-type F1 when frequency cues are explicitly blocked from creating gold labels;
- the best achievable medication F1 when current prescription list structure is first-class;
- whether investigation is truly at ceiling or just robust to broad prompts;
- whether comorbidity is representable enough to be a headline field;
- whether S3 timeline families have enough support to justify broad-schema inclusion;
- the best achievable seizure-frequency F1 after event/rate payload construction;
- whether medication temporality should remain in S4 or be treated as an auxiliary clinical task;
- which pairwise family interactions help versus hurt;
- how much of S5 loss is due to frequency itself versus medication interference versus broad extractor design;
- whether validation mechanisms transfer to holdout;
- whether Table 1-style benchmark comparisons can be supported without CUI-aware reproduction.

These are the missing questions that should define the next ExECT workstream.

## Revised ExECT Research Program

### Principle 1: Optimize Components Before Stacking

For each component, produce a validation-split ceiling estimate before adding it to a broad stack.

The minimum ceiling report should include:

- family name,
- gold source and policy,
- support count,
- no-model representability,
- raw extraction F1 if available,
- bridge-only or bridge-effect analysis,
- best validation F1,
- precision/recall,
- main residual error categories,
- evidence diagnostic summary,
- whether the family is headline, diagnostic, or deferred.

### Principle 2: Use No-Model Gates First

Every family should get a no-model audit appropriate to its structure.

Examples:

- Diagnosis: can audited diagnosis labels be represented from raw note strings and bridge tables?
- Seizure type: are gold seizure-type surfaces present or inferable under allowed policy?
- Medication: do current prescription/list spans cover gold medications?
- Investigation: do section/list spans cover gold investigations?
- Comorbidity: are gold comorbidity labels explicitly stated and patient-scoped?
- Frequency: do event/rate candidates cover gold frequency labels?
- Medication temporality: do lifecycle rows support current/past/planned/taper labels?

Low representability should block broad tuning until the substrate is repaired or the family is downgraded.

### Principle 3: Treat Pairwise Interactions as Experiments

After isolated ceilings, test pairs before broad stacks:

- Diagnosis + seizure type.
- Seizure type + seizure frequency.
- Medication + medication temporality.
- Medication + seizure frequency, if medication sections distract frequency.
- Investigation + comorbidity.
- Comorbidity + epilepsy cause.
- Onset + when diagnosed.

Each pair should report whether family F1 improves, degrades, or changes error type.

### Principle 4: Stack Only Optimized Components

The next ladder should not be S1/S2/S3/S4/S5 as currently implemented. It should be S1*/S2*/S3*/S4*/S5*: the same reporting surfaces built from optimized components.

Only then can we make a clean claim:

- isolated component ceiling,
- pairwise interaction effect,
- stacked schema effect,
- residual complexity penalty.

## Concrete Next Pulls

### Pull 1: Frequency Event/Rate Payload Audit

Rationale: frequency is the largest unresolved S5 bottleneck and the closest ExECT analogue to the Gan S0 calculation task.

Build or prototype a no-model payload with:

- source section and local line,
- exact evidence span,
- frequency expression span,
- count/rate/period fields,
- qualitative label candidates,
- seizure-free interval candidates,
- zero-rate candidates,
- current versus historical scope,
- seizure-type association,
- multi-label group,
- ambiguity flags,
- candidate benchmark labels.

Definition of done:

- Compare payload candidate labels against validation gold.
- Report coverage, precision, and full-label coverage by document.
- Break down misses by quantified, qualitative, seizure-free, zero-rate, type-associated, and temporal-scope categories.
- Do not run another model grid until coverage is meaningfully better than the current 11.6 percent gold-label coverage baseline.

### Pull 2: S1 Raw/Bridge/Prompt Causal Split

Rationale: S1 validation is strong, but holdout diagnosis and seizure-type transfer is weak.

Run or assemble a component audit for diagnosis and seizure type:

- raw model output before bridge,
- deterministic bridge output,
- prompt-policy effect,
- bridge-only repair count,
- specificity collapse effect,
- false positives from differential/family history,
- holdout residual comparison.

Definition of done:

- Separate diagnosis F1 and seizure-type F1 into raw, bridged, and final stages.
- Identify whether holdout failures are extraction failures, bridge failures, or policy failures.
- Decide whether S1 is actually near ceiling or only validation-optimized.

### Pull 3: Medication Current-Rx and Lifecycle Payload

Rationale: annotated medication is high-ceiling but S5 damages it; medication temporality needs a separate substrate.

Build a medication payload with:

- medication mention,
- normalized alias,
- dose line,
- section/list source,
- current/past/planned/taper status,
- non-ASM flag,
- prescription-list membership,
- evidence span,
- benchmark medication candidate,
- temporality candidate if applicable.

Definition of done:

- Reproduce S1 medication strength from the payload.
- Test whether the S5 AM guard can be replaced or simplified by the payload.
- Quantify which temporality labels are representable without recall collapse.

### Pull 4: Family-Span Payload

Rationale: many ExECT errors are caused by asking the model to infer document geometry and labels simultaneously.

Build `exect.sections.family_spans.v1` as a deterministic or mostly deterministic substrate:

- diagnosis/problem spans,
- seizure description spans,
- medication list spans,
- investigation spans,
- history/background spans,
- frequency spans,
- plan/follow-up spans.

Definition of done:

- For each family, report whether gold evidence tends to appear inside the proposed spans.
- Compare full-note versus family-span prompting for at least S1 and investigation.
- Record whether spans improve precision without recall loss.

### Pull 5: Component Ceiling Registry

Rationale: the project needs a single place to distinguish local ceilings from stacked performance.

Create a table or report that tracks:

- component,
- best validation F1,
- precision,
- recall,
- best run/config,
- model/provider,
- scorer,
- normalization/bridge,
- no-model representability,
- residual category,
- status: headline, diagnostic, deferred, blocked.

Definition of done:

- Existing S1/S4/S5 results are backfilled with caveats.
- Components without isolated ceilings are marked as unknown, not implicitly solved.
- Future stack experiments cite this table.

### Pull 6: Optimized Stack Reconstruction

Rationale: once component ceilings exist, rebuild the ladder.

Construct:

- S1* from optimized diagnosis, seizure type, and medication.
- S2* by adding optimized investigation and only adding comorbidity if representability is adequate.
- S3* only if sparse/timeline families pass no-model gates.
- S4* only if frequency and medication temporality have independent component stories.
- S5* as the optimized core stack.

Definition of done:

- Report per-family deltas from isolated ceilings.
- Report pooled micro F1 only after per-family deltas.
- Attribute losses to specific interactions where possible.
- Compare against the original ladder as an unoptimized baseline.

## Proposed Component Experiment Template

Every component experiment should declare:

- hypothesis,
- family,
- benchmark contract,
- split,
- model/provider,
- program variant,
- scorer,
- bridge/normalization policy,
- no-model substrate,
- one varied factor,
- primary family metric,
- secondary evidence diagnostics,
- stopping rule,
- residual audit plan.

Recommended arm order:

1. No-model representability.
2. Single-family full-note LLM.
3. Single-family family-span LLM.
4. Candidate-payload plus LLM adjudication.
5. Bridge and normalization ablation.
6. Guard/verifier only if the prior arm has a clear precision failure.
7. Holdout audit only after validation selection.

This order prevents the common failure mode where a verifier is tuned to compensate for a missing candidate substrate.

## How to Reinterpret Existing Results

The existing ExECT results remain valuable, but they should be relabeled.

Recommended labels:

- S1 validation result: strong benchmark-aligned S1 baseline, not final proof of diagnosis/seizure-type ceilings.
- S1 bridge/no-bridge gap: evidence that policy alignment matters.
- S2/S3/S4 ladder: unoptimized schema-complexity stress test.
- S4 result: evidence that broad extraction with frequency and temporality is too hard as currently represented.
- S5 v2b: best current operational core stack, not fully decomposed component stack.
- Frequency no-model audit: blocker for candidate-first frequency work until event/rate payload improves.
- Frequency verifier gains: precision-control evidence, not event-discovery closure.
- Annotated-medication guard: evidence of broad-stack medication interference.
- Medication temporality rejected arms: implementation failures, not final proof that lifecycle decomposition cannot work.
- Per-family parallel S5 rejection: rejection of one implementation, not rejection of family-first decomposition.
- Holdout report: transfer audit and residual-prioritization signal, not a tuning target.

## Risks and Caveats

The review is bounded by the current artifact record.

Key caveats:

- Some run metadata is not fully normalized, and several experiment registry rows still have pending backfill.
- The holdout split is small, so holdout differences should be interpreted as warnings and residual-analysis triggers, not definitive model rankings.
- CUI-aware benchmark reproduction remains blocked, limiting any external benchmark claim.
- Frequency gold has known quirks and should be handled under the ExECT audit, not borrowed directly from Gan semantics.
- Medication temporality gold policy is intrinsically fragile because the prescription JSON lacks a native temporality column.
- Pooled micro F1 can hide family-specific degradation and should not be the main optimization metric for component work.

## Bottom Line

Yes, ExECT has tried to do too much at once.

The current ladder proved that complexity hurts. The next research step is to stop treating the ladder as the decomposition. ExECT should be rebuilt around component ceilings: isolate each field family, build the missing deterministic substrates, optimize family F1, test pairwise interactions, and only then stack the optimized components into S1*/S2*/S3*/S4*/S5*.

The highest-value next move is a frequency event/rate payload audit, followed closely by an S1 raw/bridge/prompt causal split and a medication current-Rx/lifecycle payload. Those three pulls would convert the ExECT work from broad-prompt performance chasing into a genuine decomposition study.
