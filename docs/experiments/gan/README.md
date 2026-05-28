# Gan S0 Experiment Map

Status: active guidance
Last updated: 2026-05-29 after G8 special-class selector result

## Current Question

Gan S0 is now a decomposition problem, not a generic prompt-improvement track.

The system must separate:

1. frequency-content gate;
2. candidate inventory;
3. temporal anchoring;
4. scope and benchmark target selection;
5. canonical label construction and aggregation;
6. unknown versus no-reference policy;
7. evidence and schema validation.

## Current Baselines

| Surface | Status | Evidence |
| --- | --- | --- |
| Builder-gap v1 GPT | promoted baseline / synthetic operational default | 80.6% monthly canonical validation; 79.9% monthly under `gan2026_paper_reproduction` in G5. |
| Builder-gap v1 Qwen | accepted local transfer | 70.7% monthly canonical validation; 70.2% monthly under `gan2026_paper_reproduction`; not hosted parity. |
| D1 v1.2b schema guard only | mechanism baseline | 79.9% monthly canonical validation; 76.6% monthly under `gan2026_paper_reproduction`; best current structured date/event payload baseline. |
| R1.1 schema guard Qwen | held diagnostic | 71.3% monthly, 93.3% schema validity; held after R10, not promoted. |

## Read First

- `gan_s0_pipeline_decomposition_deep_dive_20260528.md` - current decomposition doctrine.
- `gan_s0_candidate_inventory_coverage_report_20260528.md` - G1 no-model candidate inventory coverage by label family and hard stratum.
- `gan_s0_target_label_split_g2_report_20260528.md` - G2 ablation plan plus no-model target-selection/label-construction split scaffold.
- `gan_s0_g2_model_arm_comparison_20260528.md` - G2 same-slice model comparison of free adjudication, candidate-constrained adjudication, and seeded reason-code/answer-options selector surrogate.
- `gan_s0_g4_explicit_reason_code_adjudicator_report_20260528.md` - G4 explicit reason-code adjudicator result; traceability worked, but the tested arm did not promote because it chose seizure-free candidates over quantified candidates on five enriched-slice records.
- `gan_s0_g5_paper_scorer_rescore_pack_20260528.md` - G5 synthetic-validation paper-scorer rescore pack for current promoted baselines.
- `gan_s0_g5_scorer_mode_forensics_for_g4_20260528.md` - G5 scorer-discordance analysis for G4 follow-up and special-class target-selection design.
- `gan_s0_g6_evaluation_slice_standard_decision_20260528.md` - G6 decision: use a locked 50-record mechanism slice plus named challenge sets; keep the old 25-record enriched slice as smoke-only.
- `gan_s0_g7_special_class_target_selector_preregistration_20260528.md` - G7 preregistration for the next special-class target selector; varies target-selection policy only and requires G6-aligned smoke/standard evaluation before any full-validation claim.
- `gan_s0_g8_special_class_target_selector_report_20260529.md` - G8 result; traceability passed, but the class-first selector is rejected as tested because it underperformed D1 and builder-gap GPT on standard50 and regressed on the motivating special-class overlays.
- `gan_s0_r15_d1_guardrail_ablation_decision_20260528.md` - D1 mechanism baseline.
- `gan_s0_r11_temporal_date_stage_decision_20260528.md` - date/event stage decision.
- `gan_s0_r12_clines_entity_first_pipeline_gate_decision_20260528.md` - entity-first rejected arm.
- `gan_s0_r13_self_consistency_variance_probe_decision_20260528.md` - self-consistency rejected arm.
- `gan_s0_r14_gepa_failure_postmortem_qwen_gate_design_20260528.md` - optimizer gate.
- `../../datasets/gan/gan_2026_label_audit.md` - gold and scorer policy.

## Do Not Treat As Active Guidance

Older files about temporal candidates, verify-repair, expanded builders, prompt
policy, GEPA, retrieval, and targeted examples are evidence. They prevent
repeating failed arms, but they no longer define the research program unless
listed above or in `../../component_ceiling_registry.md`.

## Active Next Work

1. Treat G8 as a rejected arm, not a mechanism closure. Do not full-validate or
   rerun the same class-first special-selector prompt shape.
2. Before another Gan selector model call, use the G8 failure read to choose
   between a standard50 candidate-constrained/answer-options comparator and a
   no-model exact-miss/special-class failure inspection.
3. Use G6 surfaces for any new selector/adjudicator execution: the old enriched
   25-record slice is smoke-only, `gan_s0_g6_standard50_v1` is the default
   mechanism-comparison surface, and named challenge sets are diagnostic
   overlays.
4. Keep the G4 negative result, G5 scorer-mode forensics, and G8 report as
   required context for any seizure-free, quantified-rate, unknown, or
   no-reference selector.
5. Keep arithmetic and broad relative-anchor guardrails diagnostic-only until a
   seizure-specific parser exists.
6. Use the G5 rescore pack for synthetic-only paper-facing tables; Real(300)
   and Real(150) benchmark reporting remains blocked.

## Filing Guidance

New Gan docs should state which decomposition component they touch and whether
their decision scope is `arm`, `mechanism`, `operational`, `diagnostic`, or
`blocked`.
