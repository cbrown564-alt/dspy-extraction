# Gan S0 Experiment Map

Status: active guidance
Last updated: 2026-05-29 after G16 aggregation policy

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
| G13 frequency-content gate | diagnostic gate baseline | 244/299 validation gate accuracy using the current deterministic temporal candidate substrate. Quantified-frequency presence recall is 99.0%, but unclear-frequency recall is 25.0% and seizure-free recall is 51.1%. |
| G14 temporal anchoring | diagnostic component measured | On `gan_s0_g6_standard50_v1`, exact candidate coverage is 41/50 and temporal-slot coverage is 36/40 applicable rows. On `gan_s0_g6_temporal_anchoring`, exact and slot coverage are 13/15; the two slot misses are `gan_16772` and `gan_16825`. |
| G15 support-aware target selector | rejected target-selection arm | Support context was present in 50/50 standard50 predictions, but paper monthly was 31/50, below builder-gap GPT, D1 v1.2b, G8, and G10. Do not full-validate or promote as tested. |
| G16 aggregation policy | policy defined / exact constructor blocked | On the G11 exact-miss challenge, 14/21 rows need quantified rate aggregation with missing temporal slots, 2/21 need seizure-free duration policy, 4/21 are candidate-inventory gaps, and 1/21 is outside rate/duration policy. On standard50, 41/50 already have exact options and 4/50 are quantified rate aggregation blocks. |
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
- `gan_s0_g9_exact_miss_failure_inspection_20260529.md` - G9 no-model failure inspection; all four G8 standard-50 exact-miss records lack the exact gold label in raw candidates, which routed G11 before G10.
- `gan_s0_g11_candidate_inventory_challenge_set_pass_20260529.md` - G11 no-model challenge-set pass; the locked 21-record G6 exact-miss surface remains 0/21 exact, 14/21 Purist-equivalent, and 17/21 Pragmatic-equivalent. Its current rows differ from stored G1 on 20 rows because broad abstentions are now pruned when concrete candidates are present.
- `gan_s0_g12_answer_option_surface_20260529.md` - G12 no-model answer-option decision; current constructed aggregate options exact-cover 0/21, so G10 is authorized only as a category-level/candidate-ranking selector until a new aggregation constructor exists.
- `gan_s0_g13_frequency_content_gate_report_20260529.md` - G13 isolated gate report; the current deterministic gate is strong for quantified-frequency presence and no-reference precision, but weak for unclear-frequency and seizure-free recall.
- `gan_s0_g13_gate_design_implications_20260529.md` - follow-up design note arguing that G13 should guide LLM support/adjudication surfaces, not a deterministic rule-expansion campaign.
- `gan_s0_g14_temporal_anchoring_report_20260529.md` - G14 no-model temporal anchoring report; standard50 and temporal challenge coverage with G13 gate caveats carried separately.
- `gan_s0_g10_candidate_ranking_target_selector_report_20260529.md` - G10 narrowed category-ranking selector result; traces were complete, but the arm is rejected as tested at 36/50 paper monthly on standard50, below G8, D1, and builder-gap GPT.
- `gan_s0_g15_support_aware_target_selector_report_20260529.md` - G15 support-aware target selector result; support traces were complete, but the arm is rejected as tested at 31/50 paper monthly on standard50 with motivating-overlay regressions.
- `gan_s0_g16_aggregation_policy_20260529.md` - G16 no-model rate/duration aggregation policy; exact closed-answer selector claims remain blocked until a constructor or preregistered model mechanism satisfies the policy.
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
2. Treat G10 as complete and rejected as tested. Its category-ranking traces
   were complete, but standard50 paper monthly was 36/50, below G8 (37/50), D1
   (40/50), and builder-gap GPT (41/50), with unknown/no-reference regression.
   Any new selector/adjudicator lane needs a new mechanism card. Exact closed
   answer-option construction remains blocked because the G12 constructed
   aggregate view exact-covers 0/21 locked exact-miss rows.
3. Treat G15 as complete and rejected as tested. Explicit support metadata,
   G13 gate caveats, and G14 temporal caveats did not improve the selector:
   standard50 paper monthly was 31/50, below G10 (36/50), G8 (37/50), D1
   (40/50), and builder-gap GPT (41/50).
4. Treat G16 as complete for policy definition, not as a constructor. Exact
   closed-answer selector claims remain blocked until a deterministic
   aggregation constructor or preregistered model mechanism is tested against
   the G16 policy. G17 unknown/no-reference policy is now the ready semantic
   policy follow-up.
5. Treat G13 as the source-level gate baseline before future selector work: do
   not attribute unclear-frequency or seizure-free gate misses to target
   selection until the G13 false-positive/false-negative rows are accounted for.
   Use the G13 design-implications note to keep deterministic candidates as LLM
   support rather than as a growing semantic adjudicator.
6. Treat G14 as the temporal anchoring diagnostic baseline: the current
   deterministic substrate covers most temporal challenge rows, but two true
   temporal-slot misses remain. Do not expand fragile arithmetic or broad
   relative-anchor guards from G14; route remaining exact misses to
   aggregation-aware answer construction before another target-selection arm.
7. Use G6 surfaces for any new selector/adjudicator execution: the old enriched
   25-record slice is smoke-only, `gan_s0_g6_standard50_v1` is the default
   mechanism-comparison surface, and named challenge sets are diagnostic
   overlays.
8. Keep the G4 negative result, G5 scorer-mode forensics, and G8/G9/G10/G15
   reports as required context for any seizure-free, quantified-rate, unknown,
   no-reference, support-aware, or candidate-constrained selector.
9. Keep arithmetic and broad relative-anchor guardrails diagnostic-only until a
   seizure-specific parser exists.
10. Use the G5 rescore pack for synthetic-only paper-facing tables; Real(300)
   and Real(150) benchmark reporting remains blocked.

## Filing Guidance

New Gan docs should state which decomposition component they touch and whether
their decision scope is `arm`, `mechanism`, `operational`, `diagnostic`, or
`blocked`.
