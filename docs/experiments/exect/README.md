# ExECT Experiment Map

Status: active guidance
Last updated: 2026-05-29 after E13 medication payload-routing result and E1-E13 decomposition synthesis

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
| Medication payload routing | rejected arm / mechanism open | E13 tested AM-only versus AM+MT lifecycle-context prompting on validation. AM-only scored 90.3% medication F1; AM+MT scored 82.8% and did not reduce false positives, so the tested lifecycle-context arm is rejected as tested. |
| Family-span prompting | rejected arm / diagnostic substrate | E9 rejects the E8 single-pass S1 family-span replacement arm: E4 `exect.sections.family_spans.v1` covers validation evidence for core families, but E8 cap-25 family-span prompting regressed micro F1 from 95.8% to 90.2%, driven by seizure-type F1 dropping from 95.4% to 81.8%. Keep the substrate diagnostic; do not promote this prompt shape. |
| Holdout residual attribution | current synthesis / diagnostic holdout | E11 attributes S1 transfer loss to diagnosis/seizure-type extraction, bridge, policy, specificity, and scope residuals while medication stays stable. S5 frequency loss is mixed payload-generalization plus adjudication: broad payload coverage drops from 43/43 validation labels to 31/44 holdout labels. |
| Pairwise interaction plan | preregistered plan / mechanism open | X2 defines validation-split support counts, hypotheses, metrics, interference criteria, and stop rules for diagnosis+seizure type, seizure type+frequency, medication+temporality, investigation+comorbidity, and secondary pairs. The May 29 result correction marks the S2/S4 ladder-aligned comparisons as non-answering diagnostics, not completed pairwise evidence. Medication+temporality is a diagnostic-input pair: temporality remains unscored while annotated medication F1 is scored. |
| ExECT Table 1 reproduction | blocked | Requires CUI-aware all-family scorer. |

## Read First

- `exect_task_deep_review_20260528.md` - current decomposition doctrine.
- `exect_decomposed_experiments_research_report_20260529.md` - full current synthesis of the E1-E13 and X2 ExECT decomposition sequence,
  including component findings, card ledger, limitations, and next experiments.
- `exect_frequency_event_rate_payload_audit_20260528.md` - E1 no-model frequency payload coverage gate.
- `exect_frequency_candidate_selection_probe_20260528.md` - E10 no-model frequency candidate-selection split.
- `exect_s1_raw_bridge_prompt_split_audit_20260528.md` - E2 artifact-only S1 causal split.
- `exect_medication_current_rx_lifecycle_payload_audit_20260528.md` - E3 medication current-Rx/lifecycle substrate.
- `exect_medication_lifecycle_target_policy_decision_20260528.md` - E5 lifecycle/temporality target policy decision.
- `exect_medication_current_rx_ceiling_probe_20260528.md` - E6 isolated current-Rx ceiling probe.
- `exect_medication_stack_interference_probe_20260528.md` - E7 S1-vs-S5 medication over-emission attribution.
- `exect_medication_payload_routing_e13_preregistration_20260529.md` - E13 validation-only medication payload-routing / prompt-isolation mechanism card.
- `exect_medication_payload_routing_e13_results_20260529.md` - E13 AM-only versus AM+MT lifecycle-context result and rejected-arm decision.
- `exect_family_span_payload_audit_20260528.md` - E4 typed family-span substrate and cap-slice comparison.
- `exect_family_span_prompt_comparison_e8_results_20260528.md` - E8 full-note versus family-span cap-25 prompt comparison.
- `exect_family_span_promotion_decision_e9_20260528.md` - E9 rejection/diagnostic-substrate decision for the tested family-span prompt arm.
- `exect_holdout_residual_attribution_e11_20260528.md` - E11 diagnostic holdout residual attribution.
- `exect_pairwise_interaction_plan_x2_20260529.md` - X2 pairwise interaction preregistration and support-count plan.
- `exect_pairwise_interaction_results_x2_20260529.md` - X2 design correction; prior S2/S4 ladder-aligned comparisons are diagnostic provenance only.
- `../synthesis/test_holdout_evaluation_report_20260527.md` - holdout warning.
- `../synthesis/paper_result_table_pack_20260525.md` - current paper table pack.
- `../../datasets/exect/exect_gold_label_audit.md` - gold-label policy.
- `../../policies/deterministic_scorer_semantics.md` - implemented field-family scorers.
- `../../policies/published_benchmark_metrics.md` - external benchmark caveats.

## Active Next Work

1. Frequency candidate adjudication/ranking follow-up should account for the E11 payload-transfer caveat before any promotion claim.
2. Preregister validation-only component probes for S1 diagnosis/seizure-type transfer and frequency payload robustness/adjudication before broad stack work.
3. For medication follow-up, write a new prompt-isolation or deterministic routing card that accounts for E13's AM+MT recall regression before another model-backed arm.
4. Use X2 to keep pairwise interaction cards validation-only, support-counted,
   component-isolated, and stop-rule-bound before any broad stack.
5. Use E12 to confirm investigation before calling it solved.
6. Component ceiling reports before any new broad stack.

## Do Not Overread

- S1 validation success does not prove diagnosis or seizure-type ceilings.
- S5 v2b is an operational stacked baseline, not optimal family decomposition.
- S1-S4 ladder comparisons do not count as pairwise interaction evidence.
- Medication temporal guard failures are rejected arms, not proof that lifecycle
  decomposition is impossible.
- Per-family parallel S5 rejection is a rejected implementation, not rejection
  of family-first work.

## Filing Guidance

New ExECT docs should name the family or pairwise interaction under study,
report the scorer, split, model, run IDs, component substrate, and whether the
result is an isolated ceiling, stacked result, diagnostic, rejected arm, or
blocked benchmark claim.
