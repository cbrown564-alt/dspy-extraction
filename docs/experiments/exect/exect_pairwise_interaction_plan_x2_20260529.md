# ExECT Pairwise Interaction Plan X2

Date: 2026-05-29
Status: preregistered plan; mechanism open
Kanban card: X2 - Pairwise ExECT Interaction Plan

## Research Question

Which ExECT field-family pairs provide useful cross-family support, and which
pairs introduce interference, before optimized families are rebuilt into broader
S1*/S2*/S3*/S4*/S5* stacks?

This plan defines the pairwise tests. It does not run models, change scorers,
change loaders, edit prompts, or promote any pair as solved.

## Taxonomy

Dataset: ExECTv2
Schema complexity: pair-specific project field-family surfaces
Comparison group root: `exect_pairwise_family_interaction_gpt_validation_v1`
Research axis: 1, component assembly graph before broad stacking
stage_graph_id: `pairwise_family_adjudication_v1`
varied_factor: family interaction context versus isolated family context
decision_scope: operational for this plan; arm for each first pairwise run;
mechanism only after at least two arms or two interaction positions are reviewed

## Fixed Controls

| Control | Value |
| --- | --- |
| Dataset/split | ExECTv2 `exectv2_fixed_v1:validation`, 40 documents |
| Holdout policy | Test holdout is residual-audit only and must not tune prompts, scorers, loaders, splits, bridges, or repairs |
| Scorer semantics | Existing project field-family scorers from `docs/policies/deterministic_scorer_semantics.md` |
| Benchmark scope | Project diagnostic/benchmark-facing field-family views, not CUI-aware ExECT Table 1 reproduction |
| Primary metrics | Per-family precision, recall, F1, and support; pooled micro F1 is secondary |
| Evidence diagnostics | Quote support and family-span/candidate coverage are diagnostic, not headline benchmark metrics |
| Model policy | If a pair needs model calls, use GPT 4.1-mini validation search first; Qwen or holdout transfer only after a validation gate |
| Label policy | Apply `docs/datasets/exect/exect_gold_label_audit.md`; do not infer diagnosis from seizure type alone or seizure type from frequency rows. Medication temporality may be used as unscored routing context for annotated-medication extraction, but it must not become a scored medication-status target without a target policy. |

## Support Counts

Counts below come from `load_exect_gold_documents()` filtered to
`exectv2_fixed_v1:validation`, plus the E1/E3 diagnostic payload artifacts where
noted.

| Family | Gold-bearing docs | Gold labels |
| --- | ---: | ---: |
| diagnosis | 31 | 42 |
| seizure_type | 32 | 47 |
| annotated_medication | 29 | 47 |
| investigation | 19 | 30 |
| comorbidity | 25 | 48 |
| seizure_frequency | 24 | 43 |
| birth_history | 7 | 8 |
| onset | 2 | 3 |
| epilepsy_cause | 6 | 7 |
| when_diagnosed | 4 | 4 |

| Pair | Co-docs | Family A labels in co-docs | Family B labels in co-docs | Status |
| --- | ---: | ---: | ---: | --- |
| diagnosis + seizure_type | 27 | 38 diagnosis | 38 seizure type | primary pair |
| seizure_type + seizure_frequency | 21 | 27 seizure type | 40 frequency | primary pair |
| annotated_medication + medication temporality | 29 | 47 medication | 47 loader temporality labels | primary diagnostic-input pair; temporality is unscored, annotated medication is scored |
| investigation + comorbidity | 13 | 21 investigation | 31 comorbidity | primary after E12/inventory gate |
| diagnosis + comorbidity | 18 | 26 diagnosis | 34 comorbidity | secondary diagnostic pair |
| comorbidity + epilepsy_cause | 6 | 19 comorbidity | 7 cause | sparse diagnostic pair |
| annotated_medication + seizure_frequency | 21 | 35 medication | 38 frequency | secondary interference pair |
| onset + when_diagnosed | 0 | 0 onset | 0 when diagnosed | blocked on support |

Frequency strata from E1 remain important for pair design: qualitative-change
labels appear in 11 documents / 12 labels, quantified-rate labels in
11 documents / 15 labels, seizure-free labels in 8 documents / 9 labels, and
zero-rate labels in 5 documents / 7 labels. E1 also reports type-associated
frequency gold in 17 documents / 36 labels, temporal-scope gold in
21 documents / 39 labels, and multi-label frequency gold in 15 documents /
34 labels.

Medication lifecycle remains diagnostic under E5. E3 reports 63 current,
11 planned, 9 previous, and 116 unknown lifecycle rows, with 8 taper-or-stop
rows. Among medication gold-bearing validation documents, planned rows occur in
5 documents, previous rows in 6, taper-or-stop rows in 4, and unknown
temporality rows in 26.

## Global Interference Criteria

A pair is supportive when at least one family improves by 3.0 F1 points or more
against its isolated-family comparator, the paired family does not lose more
than 2.0 F1 points, and no prohibited label-policy leak appears.

A pair is neutral when both family F1 scores remain within +/-2.0 points and
error categories do not materially change.

A pair is an interference arm when either family loses 2.0 to 5.0 F1 points, or
when residual categories shift toward known leakage without a compensating
family-level gain.

A pair is a rejected arm when either family loses at least 5.0 F1 points, recall
drops by at least three labels on a support >=20-label family, or the pair
creates a policy breach such as frequency rows generating seizure-type labels,
seizure-type context creating unsupported diagnosis labels, or lifecycle cues
changing benchmark-facing medication scoring.

For sparse support below 20 labels, decide from row-level error counts and
policy breaches rather than percentage deltas alone.

## Pair 1: Diagnosis + Seizure Type

Hypothesis: paired diagnosis and seizure-type adjudication can reduce scope and
specificity errors by letting the model distinguish patient-level epilepsy
diagnosis from seizure-event descriptions, but it can also leak seizure-type
evidence into diagnosis labels.

Support: 27 co-documents, 38 diagnosis labels, and 38 seizure-type labels.

Primary comparator: isolated diagnosis and isolated seizure-type components
built from the E2 raw/bridge/prompt split. The current S1 GPT validation
surface is a diagnostic baseline, not an isolated ceiling.

Primary metrics:

- diagnosis precision, recall, F1 under `exect_field_family_deterministic_v1`
- seizure-type precision, recall, F1 under `exect_field_family_deterministic_v1`
- raw versus benchmark-bridge residual categories
- specificity-collapse, scope, policy, extraction, and bridge error counts

Interference criteria:

- diagnosis false positives from seizure descriptions, family history, or
  differential diagnosis
- seizure-type false positives from diagnosis-only phrases
- loss of benchmark specificity collapse behavior

Stop rule: do not use this pair in S1* unless both families are neutral or
supportive versus isolated comparators and bridge/policy residuals are not
hidden by paired prompting.

## Pair 2: Seizure Type + Seizure Frequency

Hypothesis: seizure-type context can help attach frequency labels to the right
seizure type and current temporal scope, especially in type-associated and
multi-label frequency cases. The main risk is the audited anti-pattern:
frequency rows must not create seizure-type gold labels.

Support: 21 co-documents, 27 seizure-type labels, and 40 frequency labels.
This is the strongest current pair for testing cross-family support in the S5
bottleneck because E1 found 17 type-associated frequency documents and
15 multi-label frequency documents.

Primary comparator: isolated seizure-type component plus an isolated frequency
adjudicator/ranker over the fixed E1 broad payload. Do not compare directly
against a broad S5 prompt loop as the primary evidence.

Primary metrics:

- seizure-type precision, recall, F1
- seizure-frequency precision, recall, F1 using the ExECT frequency slice, not
  Gan monthly normalization
- broad-payload candidate coverage, candidate-constrained oracle gap, and
  adjudication residual categories from E10
- type-associated, temporal-scope, multi-label, qualitative-change,
  quantified-rate, seizure-free, and zero-rate strata

Interference criteria:

- seizure-type false positives sourced from frequency-only rows
- frequency over-emission from copied seizure-type context
- label-construction values outside the fixed broad payload without explicit
  justification

Stop rule: a paired arm must improve frequency adjudication by at least
3.0 F1 points or materially reduce type-associated residuals while preserving
seizure-type F1 within 2.0 points. Any frequency-to-seizure-type policy leak
rejects the arm regardless of aggregate F1.

## Pair 3: Annotated Medication + Medication Temporality

Status: active diagnostic-input pair. Medication temporality is not scored as a
benchmark-facing target under E5, but it can be used as a diagnostic context or
routing signal whose effect is measured on scored annotated-medication F1.

Hypothesis: medication lifecycle/temporality rows can improve annotated
current-Rx precision by helping the extractor or router suppress planned,
previous, taper, non-current, or unknown-temporality medication mentions while
preserving current prescription recall. The scored endpoint is annotated
medication only; lifecycle status remains an explanatory variable, not a
headline label.

Support: annotated medication has 29 gold-bearing documents and 47 labels.
Loader medication-temporality labels mirror those 47 prescription rows as
current by policy. E3 diagnostic rows add 11 planned, 9 previous, 8
taper-or-stop, and 116 unknown-temporality rows, but these are not medication
F1 labels.

Primary comparator: E6 annotated current-Rx no-model ceiling, the S1 GPT
medication surface, and E7 S1-versus-S5 medication interference attribution.

Primary metrics:

- annotated medication precision, recall, F1 only
- diagnostic lifecycle row counts and S5 over-emission categories
- current-Rx payload routing or prompt-isolation behavior
- recall-preservation on E6 annotation-derived current-Rx labels
- false-positive reduction in planned, previous, taper, dose-line,
  other-medication/non-current, and missing-gold/annotation-policy strata

Interference criteria:

- any annotated medication recall loss caused by broad temporality pruning
- planned, previous, taper, or unknown rows treated as benchmark labels rather
  than diagnostic inputs
- precision gains that come from over-pruning current-Rx dose lines or
  annotation-policy current prescriptions

Stop rule: promote only as an annotated-medication interaction arm if medication
F1 improves by at least 3.0 points or medication precision improves by at least
5.0 points with recall loss no greater than 1 label on validation. Reject the
arm if annotated-medication recall drops by more than 1 label, if lifecycle
status is reported as a benchmark-facing F1 target, or if temporal pruning
removes annotation-current prescriptions. A separate lifecycle target policy is
needed only for claims about temporality extraction quality itself.

## Pair 4: Investigation + Comorbidity

Hypothesis: investigation extraction may be close to ceiling in broad stacks,
while comorbidity remains support-sensitive and prone to background-history
scope errors. Pairing these families tests whether investigation/workup context
helps patient-history filtering or merely adds medical-history distractors.

Support: 13 co-documents, 21 investigation labels, and 31 comorbidity labels.

Primary comparator: E12 isolated investigation confirmation plus a no-model or
diagnostic comorbidity representability pass. Do not call investigation solved
from broad-stack stability alone.

Primary metrics:

- investigation precision, recall, F1 under the S2/S5 investigation view
- comorbidity precision, recall, F1 under the S2/S3 comorbidity view
- planned/refused/future investigation leakage
- patient-history versus family-history/background leakage

Interference criteria:

- completed-investigation labels confused with planned or refused workup
- comorbidity false positives from investigation indication text
- comorbidity false negatives caused by over-filtering seizure-history-adjacent
  patient history

Stop rule: pairwise work waits for E12 or an equivalent isolated investigation
decision. If investigation is near ceiling, the pair must preserve
investigation within 1.0 F1 point and either improve comorbidity residuals or
remain neutral. If comorbidity support remains too noisy, keep the pair
diagnostic.

## Secondary Pairs

| Pair | Hypothesis | Support | Next gate |
| --- | --- | ---: | --- |
| diagnosis + comorbidity | Patient-history and diagnostic labels overlap in scope; the pair may prevent family-history/differential leakage or amplify it. | 18 co-docs, 26 diagnosis labels, 34 comorbidity labels | Run only after diagnosis ceiling and comorbidity representability are available. |
| comorbidity + epilepsy_cause | Cause and comorbidity can share phrases but score independently. | 6 co-docs, 19 comorbidity labels, 7 cause labels | Sparse diagnostic inspection only; no promotion claim from validation percentages. |
| annotated_medication + seizure_frequency | Medication/follow-up sections may distract frequency currentness or help temporal context. | 21 co-docs, 35 medication labels, 38 frequency labels | Run after isolated frequency adjudicator and medication payload routing; medication F1 must not regress. |
| onset + when_diagnosed | Timeline families are clinically related but have no validation co-support. | 0 co-docs | Blocked until a broader or different split target is explicitly scoped. |

## Sequencing

1. Confirm or classify investigation through E12 before starting
   investigation+comorbidity as a scored pair.
2. Build isolated diagnosis and seizure-type ceiling comparators from E2 before
   diagnosis+seizure-type paired prompting.
3. Build an isolated frequency adjudicator/ranker over the fixed E1 broad
   payload before seizure-type+frequency.
4. Run medication+temporality as a diagnostic-input pair only: temporality may
   route or explain the prediction, but annotated medication remains the sole
   scored endpoint unless a future lifecycle target policy exists.
5. Use secondary sparse pairs for diagnostic residual classification, not
   promotion claims.

## Reporting Requirements

Each pairwise run or no-model inspection must report:

- dataset, split, record scope, model/provider if any, schema surface, scorer,
  and comparison group
- pair support counts and full-label document counts
- isolated comparator metrics and paired metrics
- per-family precision, recall, F1, TP, FP, FN, and residual categories
- evidence diagnostics and family-span/candidate coverage if those substrates
  are used
- whether the result is supportive, neutral, interference, rejected arm, blocked,
  or diagnostic only
- open cells: what the pair did not test and what cannot be inferred

## Caveats

- Current ExECT project scorers are partial field-family scorers, not
  CUI-aware ExECT Table 1 reproduction.
- Holdout evidence from E11 routes residual questions but cannot tune the pair
  designs.
- Medication lifecycle rows are diagnostic under E5. They may affect annotated
  medication predictions only through a preregistered routing or prompt-isolation
  arm; scorer semantics remain annotated current-Rx only.
- Family-span prompting is not promoted by E8/E9; spans may be used only with a
  narrower preregistered mechanism and a full-note/current-stack comparator.
- Rejected first arms reject those arm shapes only. Mechanism closure requires a
  mechanism review with at least two arms or interaction positions.

## References

- `docs/component_ceiling_registry.md`
- `docs/planning/kanban_plan.md`
- `docs/experiments/exect/README.md`
- `docs/experiments/exect/exect_s1_raw_bridge_prompt_split_audit_20260528.md`
- `docs/experiments/exect/exect_frequency_event_rate_payload_audit_20260528.md`
- `docs/experiments/exect/exect_frequency_candidate_selection_probe_20260528.md`
- `docs/experiments/exect/exect_medication_current_rx_lifecycle_payload_audit_20260528.md`
- `docs/experiments/exect/exect_medication_lifecycle_target_policy_decision_20260528.md`
- `docs/experiments/exect/exect_medication_current_rx_ceiling_probe_20260528.md`
- `docs/experiments/exect/exect_medication_stack_interference_probe_20260528.md`
- `docs/experiments/exect/exect_family_span_promotion_decision_e9_20260528.md`
- `docs/experiments/exect/exect_holdout_residual_attribution_e11_20260528.md`
- `docs/datasets/exect/exect_gold_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md`
