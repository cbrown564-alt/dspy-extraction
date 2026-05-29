# ExECT Medication Payload Routing E13 Preregistration

Date: 2026-05-29
Status: preregistered mechanism card; validation-only; mechanism open
Kanban card: E13 - Medication Payload Routing / Prompt Isolation

## Research Question

Can an annotated-medication component preserve current-Rx recall while reducing
the S5 over-emission caused by planned, previous, taper, non-current, and
annotation-policy medication contexts?

This card does not run models, change scorers, change loaders, change splits,
change benchmark bridges, edit prediction repair, or promote medication
temporality as a benchmark-facing target.

## Taxonomy

Dataset: ExECTv2
Split: `exectv2_fixed_v1:validation`
Clinical task family: annotated medication
Schema complexity: medication-only component surface
Comparison group root: `exect_medication_payload_routing_e13_validation_v1`
Research axis: component isolation before broad stack reconstruction
stage_graph_id: `medication_payload_routing_v1`
varied_factor: medication-only context versus medication context plus
diagnostic lifecycle/routing signal
intended_decision: arm-level mechanism evidence for X2 Pair 3
decision_scope: arm until at least two routing or prompt-isolation positions are
reviewed

## Fixed Controls

| Control | Value |
| --- | --- |
| Dataset/split | ExECTv2 `exectv2_fixed_v1:validation`, 40 documents |
| Holdout policy | Holdout rows from E11 are residual-routing evidence only; do not tune from holdout |
| Scorer | Medication-only slice of `exect_field_family_deterministic_v1` |
| Scored endpoint | Annotated medication only |
| Lifecycle policy | Diagnostic context only under E5; lifecycle/temporality is not scored |
| Medication ceiling substrate | E6 annotation-derived current-Rx payload, 47/47 validation labels |
| Stack-interference substrate | E7 row-level S5 over-emission ledger |
| Benchmark bridge | Existing medication normalization and bridge policy only |
| Model policy | If model-backed, GPT 4.1-mini validation search first with capped smoke before full validation |

## Motivation

E6 shows that annotated current-Rx is representable at 100.0% F1 on validation
through the annotation-derived current-Rx payload. The problem is not gold
coverage. E7 shows that S5 loses medication precision by adding 12 false
positives with 0 false negatives: 8 are S5-only, 4 are shared with S1, and the
main strata are historical/switched, planned/future, missing-gold or annotation
policy, and other-medication/non-current section evidence.

E11 keeps this validation-only: medication remains relatively stable on holdout,
and holdout residuals must not become prompt, scorer, loader, bridge, split, or
repair tuning inputs.

## Arms

| Arm | Input / context | Output scored | Purpose |
| --- | --- | --- | --- |
| AM-only | Medication-only component context without diagnostic lifecycle routing | Annotated medication only | Establish the matched isolated medication comparator |
| AM+MT-route | Same medication component plus E3/E5 diagnostic lifecycle or routing signal | Annotated medication only | Test whether lifecycle-aware routing reduces false positives without recall loss |
| AM+MT-prompt-isolation | Same note scope but explicit instruction to classify planned, previous, taper, and non-current evidence as diagnostic context only | Annotated medication only | Test a prompt-isolation alternative if routing cannot be composed cleanly |

Run only one AM+MT arm first. The second AM+MT arm should wait for the first
arm's residual review unless the first arm fails the smoke validity gate before
full validation.

## Primary Metrics

- annotated medication precision, recall, F1, TP, FP, and FN
- recall-preservation against the 47 E6 annotation-current labels
- false-positive reduction on the 12 E7 S5 false-positive rows
- category counts for historical/switched, planned/future, taper/stop,
  dose-line, other-medication/non-current, missing-gold/annotation-policy, and
  unknown-temporality strata

## Validity Gates

Before full validation, a capped smoke run must show:

- predictions parse into the current annotated-medication schema;
- lifecycle or temporality fields, if emitted for diagnostics, are not scored as
  medication labels;
- no scorer, loader, split, bridge, or repair semantics changed;
- row-level outputs retain enough evidence to classify E7 residual categories.

## Stop Rules

Promote the tested arm only if annotated medication F1 improves by at least 3.0
points versus the matched AM-only comparator, or precision improves by at least
5.0 points with recall loss no greater than 1 label on validation.

Reject the tested arm if annotated-medication recall drops by more than 1 label,
if lifecycle status is reported as a benchmark-facing F1 target, if temporal
pruning removes annotation-current prescriptions, or if the arm hides
missing-gold/annotation-policy cases as true precision gains.

Classify as neutral if both AM-only and AM+MT remain within +/-2.0 F1 points and
row-level residual strata do not materially change.

## Reporting Requirements

The result note must report:

- dataset, split, model/provider if any, config, run ID, scorer, and component
  surface;
- AM-only and AM+MT metrics under the same scorer;
- row-level before/after ledger for the 12 E7 false positives and the 2 S1 false
  negatives recovered by S5;
- evidence diagnostics for planned, previous, taper, non-current,
  unknown-temporality, and annotation-policy cases;
- whether the result is supportive, neutral, interference, rejected arm,
  blocked, or diagnostic only;
- open cells and what cannot be inferred about broader S5 stacking.

## References

- `docs/experiments/exect/exect_medication_current_rx_lifecycle_payload_audit_20260528.md`
- `docs/experiments/exect/exect_medication_lifecycle_target_policy_decision_20260528.md`
- `docs/experiments/exect/exect_medication_current_rx_ceiling_probe_20260528.md`
- `docs/experiments/exect/exect_medication_stack_interference_probe_20260528.md`
- `docs/experiments/exect/exect_holdout_residual_attribution_e11_20260528.md`
- `docs/experiments/exect/exect_pairwise_interaction_plan_x2_20260529.md`
- `docs/datasets/exect/exect_gold_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
