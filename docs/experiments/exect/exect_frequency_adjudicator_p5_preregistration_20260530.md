# ExECT Frequency Adjudicator P5 Preregistration

Date: 2026-05-30
Status: preregistered mechanism card; validation-only; mechanism open
Kanban card: P5 - ExECT Frequency Adjudicator Design

## Research Question

Can a component-isolated adjudicator or ranker select benchmark-facing seizure
frequency labels from the fixed E1 broad event/rate payload without losing the
payload's validation recall?

This card does not run models, change loaders, change splits, change scorer
semantics, change benchmark bridges, edit prediction repair, or tune from
holdout rows.

## Taxonomy

Dataset: ExECTv2
Split: `exectv2_fixed_v1:validation`
Clinical task family: seizure frequency
Schema complexity: frequency-only component surface
Comparison group root: `exect_frequency_adjudicator_p5_validation_v1`
Research axis: component isolation before broad stack reconstruction
stage_graph_id: `frequency_payload_adjudication_v1`
varied_factor: adjudication policy over the fixed broad event/rate payload
intended_decision: arm-level evidence for frequency isolated ceiling and X2
Pair 2 readiness
decision_scope: arm until at least one independent adjudicator and one simpler
ranker or rule-based comparator are reviewed under the same controls

## Fixed Controls

| Control | Value |
| --- | --- |
| Dataset/split | ExECTv2 `exectv2_fixed_v1:validation`, 40 documents |
| Holdout policy | E11 holdout rows are residual-analysis evidence only; do not tune prompts, payloads, bridges, scorers, splits, repair, or candidate rules from holdout |
| Candidate payload | E1 broad event/rate payload from `docs/experiments/exect/exect_frequency_event_rate_payload_audit_20260528.json` |
| Baseline payload metrics | 43/43 validation gold labels covered; 194 candidate labels; 151 extras; 22.2% direct-promotion precision |
| Scorer | Seizure-frequency slice of `exect_s4_field_family_deterministic_v1` under current ExECT frequency label policy |
| Benchmark bridge | Existing `exect.frequency.benchmark_bridge.v1`; no new mapping or Gan monthly normalization |
| Scored endpoint | ExECT seizure frequency labels only |
| Model policy | GPT 4.1-mini validation smoke before full validation if a model-backed arm is implemented |
| Stack policy | S4/S5 broad-stack surfaces are comparators, not component ceilings |

## Motivation

E1 makes frequency representability plausible on validation: the fixed broad
event/rate payload covers quantified-rate, qualitative-change, seizure-free,
zero-rate, type-associated, temporal-scope, and multi-label gold cases. E10
shows why that is not enough: direct payload promotion reaches only 36.3% F1
because the payload emits many extra candidates, while a gold-constrained oracle
over the same candidates reaches 100.0% F1.

The validation bottleneck is therefore candidate adjudication, ranking, and a
small amount of label-construction error, not another broad S5 prompt loop.
E11 adds a transfer caveat: holdout frequency loss includes payload coverage
gaps, so this card can only support a validation component-ceiling claim. It
cannot by itself promote a holdout-ready frequency stack.

## Candidate Arms

| Arm | Input / context | Output scored | Purpose |
| --- | --- | --- | --- |
| Direct broad payload | All E1 broad candidates promoted as predictions | Seizure frequency | Fixed low-precision substrate baseline from E10 |
| S5 GPT stack comparator | Stored S5 v2b GPT frequency predictions | Seizure frequency | Current stacked operational comparator, not isolated |
| Candidate ranker | E1 broad candidates rendered with note evidence, candidate source, type-associated flag, and temporal-scope cues | Selected frequency labels | Test whether a compact selector can approach the oracle without broad-stack interference |
| Candidate adjudicator | Same fixed candidates plus explicit keep/drop rationale per candidate | Selected frequency labels and diagnostic decisions | Test whether richer per-candidate adjudication improves precision while preserving recall |
| Rule-first negative or support comparator | Deterministic source-priority or high-precision-first ordering over the same candidates | Selected frequency labels | Check whether the lift requires model adjudication or only a simple ordering heuristic |

Implement only one model-backed arm after the deterministic comparator is
available. If the first model-backed arm fails the smoke validity gate, inspect
artifacts before adding the second model-backed arm.

## Primary Metrics

- seizure-frequency precision, recall, F1, TP, FP, and FN;
- direct-payload versus adjudicated precision/recall delta;
- oracle gap relative to the E10 gold-constrained broad-candidate oracle;
- candidate precision/recall by label type: `quantified_rate`,
  `qualitative_change`, `seizure_free`, and `zero_rate`;
- stratified performance for type-associated, temporal-scope, and multi-label
  documents;
- error counts for `adjudication_missed_broad_candidate`,
  `target_selection_extra_candidate`, and `label_construction_not_in_broad_payload`.

## Validity Gates

Before full validation, a capped smoke run must show:

- predictions parse into the current frequency schema;
- the arm selects only from or explicitly references the fixed E1 broad
  candidate surface unless the output is classified as a label-construction
  residual;
- qualitative-change, seizure-free, and zero-rate candidates are not silently
  pruned by a quantified-rate-only rule;
- no scorer, loader, split, benchmark bridge, candidate payload, or repair
  semantics changed;
- artifacts preserve per-document candidate lists, selected labels, rejected
  labels, evidence snippets, and residual class hooks.

## Stop Rules

Promote a tested adjudicator arm as supportive only if it beats the stored S5
GPT frequency F1 of 73.9% on validation or matches it within 2.0 F1 points while
substantially reducing false positives versus S5 and preserving at least 41/43
gold-label recall.

Reject the tested arm if recall falls below the S5 GPT validation recall of
79.1%, if qualitative-change or seizure-free recall regresses relative to S5,
if the arm depends on holdout-specific wording, or if it changes scorer,
payload, bridge, split, or repair semantics.

Classify as diagnostic or neutral if precision improves over direct payload
promotion but remains below S5 GPT without a clear residual class that motivates
a second preregistered arm.

## Reporting Requirements

The result note must report:

- dataset, split, model/provider if any, config, run ID, scorer, and frequency
  component surface;
- direct payload, deterministic comparator, model-backed arm, S4 GPT, and S5
  GPT metrics under the same seizure-frequency scorer slice;
- label-type and case-stratum tables for quantified-rate, qualitative-change,
  seizure-free, zero-rate, type-associated, temporal-scope, and multi-label
  cases;
- row-level residual ledger for false positives and false negatives, including
  whether each error is adjudication, label construction, or payload coverage;
- whether the result is supportive, neutral, rejected arm, diagnostic only, or
  blocked;
- an explicit caveat that holdout rows remain residual-analysis evidence only.

## References

- `docs/experiments/exect/exect_frequency_event_rate_payload_audit_20260528.md`
- `docs/experiments/exect/exect_frequency_candidate_selection_probe_20260528.md`
- `docs/experiments/exect/exect_holdout_residual_attribution_e11_20260528.md`
- `docs/experiments/exect/exect_decomposed_experiments_research_report_20260529.md`
- `docs/component_ceiling_registry.md`
- `docs/datasets/exect/exect_gold_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/taxonomy/taxonomy_primitive_catalog.md`
