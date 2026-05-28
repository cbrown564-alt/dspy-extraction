# ExECT Experiment Map

Status: active guidance
Last updated: 2026-05-28

## Current Question

ExECT is now a component-ceiling study. The schema ladder remains useful, but it
is no longer the main decomposition.

The current program is:

1. define benchmark contract and gold policy per family;
2. expose document structure and family spans;
3. build mention/event/candidate inventories;
4. bridge candidates into benchmark labels;
5. optimize within-family adjudication;
6. test pairwise interactions;
7. rebuild stacked schemas only after isolated ceilings exist.

## Current Baselines

| Surface | Status | Evidence |
| --- | --- | --- |
| Clean S1-S4 ladder | diagnostic baseline | Complexity stress test; not proof of component ceilings. |
| S5 v2b core stack | promoted baseline | GPT 85.8% micro / 73.9% frequency F1; Qwen 85.4% / 71.4% validation. |
| Frequency event/rate payload | current synthesis / adjudication open | Broad deterministic payload covers 43/43 validation gold labels but emits 151 extra candidates. E10 shows direct broad-payload promotion is only 36.3% F1, while a gold-constrained oracle over the same candidates reaches 100.0% F1; selection/adjudication remains open. |
| S1 raw/bridge/prompt split | current synthesis | GPT S1 full validation is near ceiling only after benchmark bridges; Qwen test holdout transfer drop keeps S1 validation-aligned rather than mechanism-solved. |
| Medication current-Rx ceiling | isolated ceiling / no-model oracle substrate | E6 annotation-derived current-Rx payload scores 100.0% medication F1 on validation; S1 GPT scores 92.8% and S5 GPT scores 88.7% on the same target. Lifecycle rows remain diagnostic/deferred. |
| Medication stack interference | current synthesis | E7 attributes S5 medication loss to over-emission: S5 adds 8 false positives that S1 avoided, mostly planned/future, historical/switched, other-medication, and annotation-policy cases, while recovering both S1 false negatives. |
| Family-span prompting | rejected arm / mechanism open | E4 `exect.sections.family_spans.v1` covers validation evidence for core families, but E8 cap-25 family-span prompting regressed micro F1 from 95.8% to 90.2%, driven by seizure-type F1 dropping from 95.4% to 81.8%. Keep the substrate diagnostic; do not promote this prompt shape. |
| Holdout report | active risk | S1 and S5 frequency drops require residual analysis before new claims. |
| ExECT Table 1 reproduction | blocked | Requires CUI-aware all-family scorer. |

## Read First

- `exect_task_deep_review_20260528.md` - current decomposition doctrine.
- `exect_frequency_event_rate_payload_audit_20260528.md` - E1 no-model frequency payload coverage gate.
- `exect_frequency_candidate_selection_probe_20260528.md` - E10 no-model frequency candidate-selection split.
- `exect_s1_raw_bridge_prompt_split_audit_20260528.md` - E2 artifact-only S1 causal split.
- `exect_medication_current_rx_lifecycle_payload_audit_20260528.md` - E3 medication current-Rx/lifecycle substrate.
- `exect_medication_lifecycle_target_policy_decision_20260528.md` - E5 lifecycle/temporality target policy decision.
- `exect_medication_current_rx_ceiling_probe_20260528.md` - E6 isolated current-Rx ceiling probe.
- `exect_medication_stack_interference_probe_20260528.md` - E7 S1-vs-S5 medication over-emission attribution.
- `exect_family_span_payload_audit_20260528.md` - E4 typed family-span substrate and cap-slice comparison.
- `exect_family_span_prompt_comparison_e8_results_20260528.md` - E8 full-note versus family-span cap-25 prompt comparison.
- `../synthesis/test_holdout_evaluation_report_20260527.md` - holdout warning.
- `../synthesis/paper_result_table_pack_20260525.md` - current paper table pack.
- `../../datasets/exect/exect_gold_label_audit.md` - gold-label policy.
- `../../policies/deterministic_scorer_semantics.md` - implemented field-family scorers.
- `../../policies/published_benchmark_metrics.md` - external benchmark caveats.

## Active Next Work

1. Route E9 as a family-span promotion/rejection decision using E4 and E8.
2. Frequency candidate adjudication/ranking follow-up against the fixed E1/E10 broad payload.
3. Medication payload-routing/prompt-isolation follow-up before any broad stack.
4. Component ceiling reports before any new broad stack.

## Do Not Overread

- S1 validation success does not prove diagnosis or seizure-type ceilings.
- S5 v2b is an operational stacked baseline, not optimal family decomposition.
- Medication temporal guard failures are rejected arms, not proof that lifecycle
  decomposition is impossible.
- Per-family parallel S5 rejection is a rejected implementation, not rejection
  of family-first work.

## Filing Guidance

New ExECT docs should name the family or pairwise interaction under study,
report the scorer, split, model, run IDs, component substrate, and whether the
result is an isolated ceiling, stacked result, diagnostic, rejected arm, or
blocked benchmark claim.
