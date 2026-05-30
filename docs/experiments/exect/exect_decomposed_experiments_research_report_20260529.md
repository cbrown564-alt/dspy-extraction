# ExECT Decomposed Experiments Research Report

Status: current synthesis
Date: 2026-05-29
Scope: ExECTv2 component-decomposition evidence tested so far, E1 through E13 plus X2
Builds on: `docs/experiments/exect/exect_task_deep_review_20260528.md`
Related active authorities: `docs/current_research_program.md`, `docs/component_ceiling_registry.md`, `docs/planning/kanban_plan.md`, `docs/experiments/exect/README.md`

## Research Question

What have the current ExECT decomposed experiments shown about moving from broad
schema ladders to independently measurable field-family components, and what
remains blocked before optimized S1*/S2*/S3*/S4*/S5* stacks are justified?

The practical question is whether ExECT is failing because individual families
are intrinsically low-ceiling, because candidates or benchmark bridges are
missing, because broad prompts create cross-family interference, or because the
current project scorers are not the same as published ExECT Table 1 scoring.

## Executive Summary

The ExECT decomposition work now supports one clear conclusion: the clean
S1-S4 ladder is a useful complexity stress test, but it is not the component
decomposition. Component evidence is now available for seizure frequency,
S1 diagnosis/seizure type bridge effects, medication current-Rx, medication
stack interference, family spans, holdout residual routing, investigation, and
one medication-plus-temporality prompt-routing arm.

The current S5 v2b stack remains the operational stacked baseline, not a
component ceiling: GPT 4.1-mini scores 85.8% micro F1 with 73.9% seizure
frequency F1 on validation, while Qwen3.6:35b scores 85.4% micro F1 with 71.4%
frequency F1. These rows are project field-family scores, not CUI-aware ExECT
Table 1 reproduction.

The strongest isolated ceiling so far is benchmark-facing annotated medication.
The E3/E6 annotation-derived current-Rx payload exactly reproduces 47/47
validation medication labels with 100.0% precision, recall, and F1. Existing
model surfaces sit below that ceiling: S1 GPT medication is 92.8% F1 and S5 GPT
medication is 88.7% F1. E7 shows the S5 loss is mostly over-emission from
planned, historical, other-medication, and annotation-policy contexts.

The strongest open bottleneck is seizure frequency candidate adjudication.
E1 broad event/rate payload covers 43/43 validation frequency gold labels, but
it emits 151 extra candidates and has only 22.2% precision. E10 shows direct
broad-payload promotion is 36.3% F1, while a gold-constrained oracle over the
same candidates reaches 100.0% F1. That localizes the validation problem to
candidate adjudication/ranking and label construction over a high-recall
payload, not to another broad S5 prompt loop.

S1 diagnosis and seizure-type performance remains benchmark-aligned but not
raw-extraction solved. E2 shows full-validation raw S1 is only 68.6% micro F1,
with diagnosis at 61.5% and seizure type at 57.4%. After artifact benchmark
bridges, the same surface reaches 92.3% micro F1, with diagnosis at 93.8% and
seizure type at 90.5%. This is a strong validation anchor, but the bridge
contribution is too large to call raw diagnosis or seizure-type extraction
near ceiling.

The most important negative result is E13. A corrected medication-plus-
temporality interaction arm tested AM-only versus AM+MT lifecycle-context
prompting, with annotated medication as the sole scored endpoint. AM-only
scored 90.3% F1. AM+MT scored 82.8% F1, did not reduce false positives, and
lost six additional recall labels. This rejects the tested lifecycle-context
injection arm, not medication lifecycle decomposition as a mechanism class.

Investigation is the closest thing to solved among non-S1/non-medication
families. E12 confirms near-ceiling investigation performance across stored S5
validation and holdout runs: GPT ranges from 90.4% to 96.7% F1 and Qwen ranges
from 94.9% to 97.2% F1. Remaining errors are mostly minor modifier reasoning
or annotation omissions. This unblocks investigation-plus-comorbidity pairwise
tests, but it does not solve comorbidity.

The X2 correction is important: earlier S1-vs-S2 and S4-guard comparisons were
schema-ladder diagnostics, not valid pairwise interaction evidence. Correct
pairwise work must compare target-component-alone against target-plus-paired-
component context while scoring only the target component. B1 optimized stack
reconstruction remains blocked until enough isolated ceilings and corrected
pairwise evidence exist.

## Method And Controls

Dataset and split:

- Dataset: ExECTv2.
- Development split: `exectv2_fixed_v1:validation`, 40 documents.
- Frozen holdout split: `exectv2_fixed_v1:test`, used for residual analysis
  only, not tuning.
- Current reports use project field-family scoring views, not published
  ExECTv2 CUI-aware Table 1 reproduction.

Benchmark-facing label policy:

- Diagnosis rows are affirmed JSON `Diagnosis` entities with
  `DiagCategory == "Epilepsy"` and `Certainty >= 4`.
- Seizure types come from diagnosis/seizure-type annotations, not from
  seizure-frequency rows.
- Medication scoring uses the annotated prescription/current-Rx view.
  Medication lifecycle and temporality are diagnostic unless a separate target
  policy promotes them.
- Seizure frequency uses ExECT SeizureFrequency annotation surfaces and ExECT
  frequency field-family scoring, not Gan monthly-frequency normalization.
- CUI-aware all-family Table 1 reproduction remains blocked.

Scorer surfaces:

- S1 uses `exect_field_family_deterministic_v1` for diagnosis, seizure type,
  and annotated medication.
- S2-S4 extend field-family scope with their rung-specific deterministic
  scorers.
- S5 uses `exect_s5_core_field_family_deterministic_v1` for diagnosis, seizure
  type, annotated medication, investigation, and seizure frequency.
- Evidence quote support is diagnostic unless a specific experiment changes
  the target.

Experimental controls:

- The E1-E13 synthesis makes no scorer, loader, split, gold, benchmark bridge,
  or holdout-tuning change.
- No holdout result is used to edit prompts or select a new mechanism.
- No broad stack result is treated as an isolated component ceiling unless a
  component-specific report says so.
- Rejected arms are arm-level rejections unless a mechanism review closes the
  whole mechanism class.

## Current Baselines

The clean ladder remains the diagnostic schema-breadth baseline:

| Schema level | GPT validation micro F1 | Qwen validation micro F1 | Current interpretation |
| --- | ---: | ---: | --- |
| S1 | 92.3% | 85.9% | Strong benchmark-aligned anchor; not raw extraction ceiling. |
| S2 | 82.7% | 84.4% | Diagnostic schema-breadth stress test. |
| S3 | 74.4% | 75.3% | Sparse/timeline families remain weak and under-isolated. |
| S4 | 65.5% | 67.5% | Broad frequency and medication-temporality burden. |
| S5 v2b core | 85.8% | 85.4% | Promoted operational stack, not decomposed optimized stack. |

The promoted S5 v2b stack is useful but should not be overread. GPT v2b reaches
85.8% micro F1, with 90.0% diagnosis F1, 84.0% seizure-type F1, 88.7%
annotated-medication F1, 96.7% investigation F1, and 73.9% seizure-frequency
F1. Qwen v2b is near parity at 85.4% micro F1, with slightly higher diagnosis
F1 and lower frequency F1.

Holdout transfer remains a residual warning rather than a tuning surface. E11
shows S1 GPT micro F1 drops from 92.3% validation to 77.8% test, and S5 GPT
drops from 85.8% to 69.4%. S1 loss is concentrated in diagnosis and seizure
type. S5 frequency loss is mixed payload-generalization and adjudication.

## Component Findings

### 1. Frequency Event/Rate Payload And Candidate Selection

E1 changed the frequency story. The archived frequency candidate substrate had
very low coverage, but the broad event/rate payload now covers all 43 validation
frequency gold labels. Coverage holds across quantified-rate, qualitative-
change, seizure-free, zero-rate, type-associated, temporal-scope, and multi-
label strata.

That recall success is not a prediction result. The broad payload emits 194
candidate labels for 43 gold labels, including 151 extras, so candidate
precision is 22.2%. The high-precision payload is not a replacement: it covers
only 58.1% of gold labels and drops all qualitative-change labels.

E10 isolates the open mechanism:

| Surface | Precision | Recall | F1 | Decision |
| --- | ---: | ---: | ---: | --- |
| Broad event/rate payload promoted directly | 22.2% | 100.0% | 36.3% | recall substrate, not prediction surface |
| High-precision payload promoted directly | 19.5% | 58.1% | 29.2% | rejected as replacement substrate |
| Gold-constrained oracle over broad candidates | 100.0% | 100.0% | 100.0% | non-deployable upper bound |
| Existing S4 GPT frequency surface | 42.9% | 48.8% | 45.7% | diagnostic broad-stack surface |
| Existing S5 GPT frequency surface | 69.4% | 79.1% | 73.9% | current stacked operational surface |

The oracle result is the scientific hinge: validation frequency is not blocked
by candidate existence after E1. It is blocked by adjudication, ranking, and
some label construction over a high-recall candidate inventory.

Holdout keeps the interpretation cautious. E11 shows broad-payload recall falls
from 43/43 validation labels to 31/44 holdout labels, and the holdout oracle
drops to 82.7% F1. Frequency follow-up should repair or stress-test payload
generalization on validation, then audit holdout residuals without tuning from
them.

### 2. S1 Diagnosis And Seizure-Type Raw/Bridge Split

E2 shows that S1 performance depends heavily on benchmark-policy bridges:

| Surface | Split | Micro F1 | Diagnosis F1 | Seizure-type F1 |
| --- | --- | ---: | ---: | ---: |
| policy raw full validation | validation | 68.6% | 61.5% | 57.4% |
| policy post-bridge full validation | validation | 92.3% | 93.8% | 90.5% |
| Qwen clean validation | validation | 85.9% | 95.1% | 74.2% |
| Qwen clean test holdout | test | 71.8% | 66.7% | 52.2% |

The full-validation bridge effect is +32.3pp diagnosis F1 and +33.1pp
seizure-type F1. That is evidence for the value of the benchmark bridge, but
also evidence against declaring raw diagnosis or raw seizure-type extraction
solved.

E11 confirms that the validation-to-holdout S1 drop is not medication-driven.
S1 GPT loses 14.5pp micro F1 from validation to test, with annotated medication
essentially stable but diagnosis down 22.4pp and seizure type down 24.6pp.
Residual classes expand in extraction, bridge, policy, specificity-collapse,
and scope categories.

The right next S1 work is therefore not another broad S1 prompt loop. It is
family-specific raw/bridge/prompt analysis for diagnosis and seizure type,
including scope, specificity, and bridge behavior under frozen validation
controls.

### 3. Annotated Medication Current-Rx

Medication now has a true isolated ceiling substrate for the benchmark-facing
current-Rx target. E3 shows the annotation-derived current-Rx payload covers
47/47 validation medication labels with 100.0% precision. E6 records that as
an isolated no-model ceiling:

| Surface | Precision | Recall | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E3 annotation current-Rx payload | 100.0% | 100.0% | 100.0% | 47 | 0 | 0 |
| Existing S1 GPT medication surface | 90.0% | 95.7% | 92.8% | 45 | 5 | 2 |
| Existing S5 GPT medication surface | 79.7% | 100.0% | 88.7% | 47 | 12 | 0 |

This is the clearest example of the decomposition pivot paying off. The
benchmark-facing medication component itself is representable. The model and
stack behavior sit below that ceiling.

E7 attributes S5 medication loss to over-emission rather than current-Rx
coverage. S5 adds 8 false positives that S1 avoided, shares 4 false positives
with S1, and recovers the two S1 false negatives. S5 false positives
concentrate in historical/switched evidence, planned/future evidence,
other-medication/non-current sections, and missing-gold or annotation-policy
cases.

### 4. Medication Lifecycle And Temporality

E5 fixes the current target policy: medication lifecycle and temporality are
clinical-diagnostic and deferred, not benchmark-facing medication F1 targets.
The reason is gold-source fidelity. ExECT prescription JSON does not provide a
native temporality column, and the gold audit warns against treating current,
planned, previous, or tapering medication status as reliable benchmark gold.

E3 still makes lifecycle useful as diagnostic inventory:

| Lifecycle case type | Count |
| --- | ---: |
| dose line rows | 131 |
| dose-only rows | 60 |
| prescription-list rows | 78 |
| planned rows | 11 |
| previous rows | 9 |
| taper-or-stop rows | 8 |
| non-ASM rows | 4 |
| unknown-temporality rows | 116 |

E13 then tested one corrected Pair 3 arm: AM-only versus AM+MT lifecycle-
context prompting, with annotated medication as the sole scored endpoint.

| Surface | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E13 AM-only GPT | 42 | 4 | 5 | 91.3% | 89.4% | 90.3% |
| E13 AM+MT lifecycle-context GPT | 36 | 4 | 11 | 90.0% | 76.6% | 82.8% |

The lifecycle-context arm did not reduce the E7 false-positive ledger and lost
six additional current-Rx labels. This rejects the tested context-injection
arm. It does not reject deterministic routing, better payload rendering, or a
future lifecycle-specific task with an explicit gold/proxy policy.

### 5. Family-Span Payload And Prompting

E4 implemented `exect.sections.family_spans.v1` as a typed document-geometry
payload. It emits 816 validation spans and covers gold evidence well:
diagnosis/problem 56/56, seizure 49/49, medication 53/53, investigation 33/33,
frequency 44/44, and history/background 85/89.

On the first 25 validation documents, the S1-plus-investigation family-span
context covered 116/116 selected-family gold annotations while using 29,319 of
33,029 full-note characters, or 88.8% of the full-note prompt substrate.

E8 tested whether that substrate could replace full-note S1 prompting on a
matched cap-25 slice:

| Arm | Micro F1 | Diagnosis F1 | Seizure-type F1 | Medication F1 | Evidence support |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full note | 95.8% | 97.6% | 95.4% | 94.9% | 97.3% |
| Family span | 90.2% | 97.6% | 81.8% | 94.7% | 95.8% |

E9 correctly rejects this single-pass family-span replacement arm. The loss is
not caused by absent gold offsets, since cap-slice evidence coverage was
complete. The likely mechanism is span rendering and false-family context
changing seizure-type adjudication while buying only modest character savings.

Family spans remain a diagnostic substrate and may support narrower mechanisms,
but they are not an operational prompt-routing default.

### 6. Investigation

E12 confirms investigation as near ceiling using stored S5 validation and
holdout runs:

| Run / model | Split | F1 | Precision | Recall | Support |
| --- | --- | ---: | ---: | ---: | ---: |
| GPT 4.1-mini | validation | 96.7% | 96.7% | 96.7% | 30 |
| GPT 4.1-mini | test | 90.4% | 89.2% | 91.7% | 36 |
| Qwen3.6:35b | validation | 94.9% | 96.6% | 93.3% | 30 |
| Qwen3.6:35b | test | 97.2% | 97.2% | 97.2% | 36 |

The remaining mismatches are small and clinically interpretable: modifier logic
around EEGs confirming psychogenic non-epileptic events, incidental findings,
unknown scan result handling, and gold annotation omissions. Investigation does
not need the same immediate component-optimization spend as frequency,
diagnosis/seizure type, or medication routing.

This confirms investigation as near ceiling and unblocks corrected
investigation-plus-comorbidity pairwise tests. It does not solve comorbidity.

### 7. Pairwise Interactions

X2 defines the pairwise interaction contract and then corrects a false start.
The key rule is that pairwise interactions cannot be inferred from schema rung
comparisons. S1 versus S2 is not a clean investigation-plus-comorbidity test.
S4 baseline versus S4 medication-temporality guards is not a clean
medication-plus-temporality test.

Correct pairwise arms must compare:

- target component alone;
- target component plus paired component context or payload;
- target component as the sole scored endpoint;
- paired component as diagnostic context unless explicitly scoped otherwise.

E13 is the first corrected Pair 3 execution, and it rejects the AM+MT lifecycle-
context arm as tested. Pair 4 remains open, with E12 now providing the
investigation-side ceiling context. Pair 1 diagnosis plus seizure type and Pair
2 seizure type plus frequency still require isolated comparators before they
can be run cleanly.

## E1-E13 And X2 Card Ledger

| Card | Status | Main contribution | Claim boundary |
| --- | --- | --- | --- |
| E1 | current synthesis / coverage gate passed | Broad frequency event/rate payload covers 43/43 validation frequency gold labels but emits 151 extra candidates. | Recall substrate only; adjudication open. |
| E2 | diagnostic causal split | S1 full-validation raw 68.6% micro rises to 92.3% after benchmark bridge; diagnosis and seizure-type bridge effects exceed 32pp. | Strong validation anchor, not raw extraction ceiling. |
| E3 | current synthesis / no-model gate | Annotation-derived current-Rx payload covers 47/47 medication gold labels; lifecycle rows catalogued diagnostically. | Current-Rx substrate, not lifecycle scoring. |
| E4 | current synthesis / document-geometry substrate | Family spans cover core-family validation evidence and emit measurable false-family spans. | Diagnostic substrate only. |
| E5 | active guidance | Medication lifecycle/temporality kept clinical-diagnostic and deferred. | No benchmark-facing lifecycle F1 without new target policy. |
| E6 | isolated ceiling / no-model oracle substrate | Medication current-Rx payload reaches 100.0% F1; S1 and S5 model surfaces remain below it. | Annotation-derived ceiling substrate, not deployed extractor. |
| E7 | diagnostic stack-interference attribution | S5 medication loss is over-emission: 12 FP, 0 FN, with 8 S5-only FP. | Interference attribution, not prompt-isolation proof by itself. |
| E8 | rejected arm | Family-span S1 cap-25 prompt loses 5.5pp micro and 13.6pp seizure-type F1 versus full note. | Rejects this full-note replacement arm, not typed spans. |
| E9 | active guidance | Classifies E8 as rejected arm while preserving `exect.sections.family_spans.v1` as diagnostic substrate. | Future span work needs narrower preregistration. |
| E10 | diagnostic component split | Broad frequency direct promotion 36.3% F1; gold-constrained oracle over broad candidates 100.0% F1. | Candidate adjudication open; payload coverage not ceiling. |
| E11 | current synthesis / diagnostic holdout | Routes holdout loss: S1 diagnosis/seizure transfer; S5 frequency payload-generalization plus adjudication; medication current-Rx transfers. | Holdout residual analysis only, no tuning. |
| E12 | near ceiling confirmed | Investigation F1 ranges 90.4%-97.2% across stored validation and holdout S5 runs. | Investigation near ceiling; comorbidity still open. |
| E13 | rejected arm / mechanism open | AM+MT lifecycle-context scores 82.8% F1 versus AM-only 90.3%, with no FP reduction and six extra recall losses. | Rejects tested lifecycle-context arm only. |
| X2 | preregistered plan / design correction | Defines component-isolated pairwise tests and corrects prior ladder-aligned comparisons as non-answering. | Pairwise evidence remains open except E13 arm rejection. |

## Interpretation

### ExECT now has substrates, but not enough ceilings

The decomposition pivot has produced useful substrates: frequency event/rate
candidates, medication current-Rx/lifecycle inventories, family spans, and raw
versus bridge S1 audit surfaces. But only medication current-Rx and
investigation have strong ceiling-like evidence. Frequency has high-recall
coverage but open adjudication. Diagnosis and seizure type have strong
benchmark-aligned validation metrics, but raw extraction and holdout transfer
remain unsolved.

### Benchmark bridges are essential and must stay visible

E2 is the warning label for all S1 claims. Benchmark bridges can convert a weak
raw extraction surface into a strong project-score surface. That is legitimate
under the current benchmark-facing policy, but it means reports must separate
raw clinical extraction, bridge-normalized labels, and final scored outputs.

### Frequency is a selection problem on validation and a payload-transfer problem on holdout

On validation, E1/E10 show the broad payload contains all gold answers but too
many extras. On holdout, E11 shows the payload itself misses more labels.
Therefore the next frequency work needs two layers: validation-only
adjudicator/ranker development over the fixed broad payload, plus a later
transfer audit that checks whether the payload itself generalizes.

### Medication is high-ceiling but stack-sensitive

Medication is not intrinsically low-ceiling under the current benchmark target.
The current-Rx substrate is exact. The model errors are stack and interface
errors: S5 broad context over-emits, while E13 lifecycle context overburdens
the medication-only arm and loses recall. Medication follow-up should test a
new prompt-isolation or deterministic routing mechanism, not turn lifecycle
rows into benchmark-facing labels.

### Typed document geometry is promising but not a default prompt replacement

E4/E8/E9 make the family-span result unusually clean: the substrate covers the
gold evidence, but the prompt replacement still regresses. That means future
span work should narrow the mechanism, for example one-family adjudication or
candidate evidence filtering, instead of repeating S1 full-note replacement.

### Pairwise evidence is mostly still missing

X2 prevents an easy mistake: schema ladder deltas are not pairwise interaction
evidence. E13 gives one corrected negative arm. Investigation is ready for Pair
4 because E12 confirms it is near ceiling. Diagnosis plus seizure type and
seizure type plus frequency still need isolated comparators before interaction
claims are meaningful.

## Limitations And Threats To Validity

- Current metrics are project field-family diagnostics, not CUI-aware ExECTv2
  Table 1 reproduction.
- Validation has 40 documents; family support counts can be small, especially
  for sparse S3 families.
- Holdout has 40 documents and is used only for residual analysis.
- E13 is one prompt-context arm, not a mechanism closure for medication
  lifecycle decomposition.
- E8 is cap-25 only and rejects a prompt-routing shape, not family spans as a
  substrate.
- E12 uses stored S5 runs rather than a fresh investigation-only model run, but
  the consistency across validation and holdout supports the near-ceiling
  classification.
- Medication lifecycle labels are cue-derived diagnostics, not benchmark gold.
- Frequency rows must not be used to create seizure-type gold labels.

## Current Research Status

| Component | Current status | Evidence |
| --- | --- | --- |
| Clean S1-S4 ladder | diagnostic baseline | Paper table pack, E11 |
| S5 v2b core stack | promoted stacked baseline | S5 v2b GPT/Qwen validation rows |
| Frequency event/rate payload | coverage gate passed; adjudication open | E1, E10 |
| S1 diagnosis/seizure raw/bridge split | mechanism open | E2, E11 |
| Medication current-Rx | isolated ceiling / no-model oracle substrate | E3, E6 |
| Medication lifecycle / temporality | clinical-diagnostic / deferred | E3, E5, E13 |
| Medication stack interference | current synthesis / mechanism open | E7, E13 |
| Family spans | diagnostic substrate; prompt arm rejected | E4, E8, E9 |
| Investigation | near ceiling confirmed | E12 |
| Comorbidity | mechanism open | X2, ladder diagnostics |
| Pairwise interactions | preregistered plan; mostly open | X2, E13 |
| Optimized S1*/S2*/S3*/S4*/S5* stack | blocked | B1, component registry |
| ExECT Table 1 reproduction | blocked benchmark claim | published benchmark policy |

## Next Experiments

1. Build a validation-only frequency adjudicator/ranker over the fixed E1 broad
   payload. Report candidate precision/recall, oracle gap, type-associated and
   multi-label strata, and label-construction residuals. Do not tune from
   holdout.
2. Design isolated diagnosis and seizure-type ceiling comparators from E2.
   Report raw extraction, bridge effect, specificity collapse, scope errors,
   and policy residuals separately.
3. Write a new medication prompt-isolation or deterministic routing card that
   accounts for E13. The next arm should avoid the rejected AM+MT lifecycle-
   context injection shape and should use E7 rows as a before/after ledger.
4. Run corrected Pair 4 only after defining the comorbidity side. Use E12 as
   the investigation comparator, then test investigation-only versus
   investigation-plus-comorbidity and comorbidity-only versus comorbidity-plus-
   investigation.
5. Keep family spans as a diagnostic substrate until a narrower mechanism is
   preregistered with a full-note or current-stack comparator.
6. Keep B1 optimized stack reconstruction blocked until isolated ceilings and
   component-isolated pairwise evidence are available.

## Source Artifacts Used

- `docs/README.md`
- `docs/current_research_program.md`
- `docs/component_ceiling_registry.md`
- `docs/planning/kanban_plan.md`
- `docs/experiments/exect/README.md`
- `docs/datasets/exect/exect_gold_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md`
- `docs/taxonomy/taxonomy_primitive_catalog.md`
- `docs/experiments/exect/exect_task_deep_review_20260528.md`
- `docs/experiments/exect/exect_frequency_event_rate_payload_audit_20260528.md`
- `docs/experiments/exect/exect_frequency_candidate_selection_probe_20260528.md`
- `docs/experiments/exect/exect_s1_raw_bridge_prompt_split_audit_20260528.md`
- `docs/experiments/exect/exect_medication_current_rx_lifecycle_payload_audit_20260528.md`
- `docs/experiments/exect/exect_medication_lifecycle_target_policy_decision_20260528.md`
- `docs/experiments/exect/exect_medication_current_rx_ceiling_probe_20260528.md`
- `docs/experiments/exect/exect_medication_stack_interference_probe_20260528.md`
- `docs/experiments/exect/exect_family_span_payload_audit_20260528.md`
- `docs/experiments/exect/exect_family_span_prompt_comparison_e8_results_20260528.md`
- `docs/experiments/exect/exect_family_span_promotion_decision_e9_20260528.md`
- `docs/experiments/exect/exect_holdout_residual_attribution_e11_20260528.md`
- `docs/experiments/exect/exect_investigation_isolated_ceiling_e12_20260529.md`
- `docs/experiments/exect/exect_pairwise_interaction_plan_x2_20260529.md`
- `docs/experiments/exect/exect_pairwise_interaction_results_x2_20260529.md`
- `docs/experiments/exect/exect_medication_payload_routing_e13_results_20260529.md`
- `docs/experiments/synthesis/paper_result_table_pack_20260525.md`
- `docs/experiments/synthesis/test_holdout_evaluation_report_20260527.md`
