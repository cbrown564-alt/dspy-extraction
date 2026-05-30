# Gan S0 Experiment Map

Status: active guidance
Last updated: 2026-05-30 after G30 standard50 GEPA teacher-runner result

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
| G16 aggregation policy | policy defined | On the G11 exact-miss challenge, 14/21 rows need quantified rate aggregation with missing temporal slots, 2/21 need seizure-free duration policy, 4/21 are candidate-inventory gaps, and 1/21 is outside rate/duration policy. On standard50, 41/50 already have exact options and 4/50 are quantified rate aggregation blocks. |
| G19 post-G16 error attribution | current synthesis / optimization queue | Across builder-gap GPT, D1 v1.2b, G8, G10, and G15 on standard50, there are 65 paper-monthly arm-misses across 29 rows. The leading classes are aggregation blocks with missing temporal slots, unclear or unknown-cluster evidence misrouted as concrete, seizure-free over quantified target selection, and wrong quantified rate/window selection. G20 has now preregistered the aggregation-constructor path, and G17 has defined the special-label policy slice. |
| G20 aggregation constructor preregistration | preregistered deterministic constructor protocol / mechanism open | G20 chooses a deterministic, fixture-first quantified-rate aggregation constructor as the next implementation path. It scopes primary fixtures to the four G19 standard50 aggregation rows and the 21-row G11 exact-miss challenge, while deferring seizure-free duration, unknown/no-reference, cluster flattening, and target selection. |
| G21 aggregation constructor implementation | fixture-tested no-model constructor / mechanism open | G21 implements `gan.frequency.aggregation_constructor.v1` as a separate constructed answer-option surface. Standard50 exact option coverage rises from 41/50 raw to 45/50 combined, and the G11 exact-miss challenge reaches 12/21 constructed exact with 0 deferred or negative-control constructions. This is answer-option coverage, not selector performance. |
| G17 unknown/no-reference policy | current synthesis / special-label policy defined | G17 defines the nine-row G19 special-label slice across unclear-frequency, unknown-cluster, seizure-free/no-reference scorer discordance, and concrete-rate overcall cases. It makes no scorer, loader, split, bridge, candidate-builder, selector, or repair changes and authorizes no deterministic repairs. |
| G22 closed-option target selector | rejected target-selection arm | G22 tested a closed-option selector over raw deterministic temporal candidates plus prediction-time G21 constructed options. Trace fields were complete in 50/50 rows and final labels were copied from selected options, but standard50 paper monthly was 39/50, below builder-gap GPT at 41/50 and the 43/50 stop-rule gate. It regressed on seizure-free-versus-quantified and unknown/no-reference overlays, including five G17 builder-gap regressions. Do not full-validate or promote as tested. |
| G23 selector failure mechanism audit | current synthesis / mechanism framing | Across G8/G10/G15/G22 there are 57 selector arm-misses on standard50; 39/57 have an exact answer option already available. G22's 11 misses split into 6 wrong choices with exact options present and 5 forced wrong choices where G17 unknown labels were absent from the closed-option surface. | Use G23 to design G24: keep closed options as support, but test evidence-first target narration with a constrained special-label escape instead of rerunning closed-option ID selection alone. |
| G25 selector generalization audit | current synthesis / generalization gate | Standard50 remains the default mechanism slice, but its 50-row aggregate is too noisy to promote or kill near-baseline selectors alone. Builder-gap GPT and D1 standard50 scores slightly overstate full-validation paper scores by 2.1pp and 3.4pp, while stored builder-gap frozen-test paper scores drop by 15.5pp (GPT) and 11.1pp (Qwen) versus validation. | Use the G25 gate before spending full-validation, Qwen, or frozen-test budget: 43/50 is an obvious-pass trigger; 39-42/50 needs a preregistered row-ledger exception with no special-label regression; below 39/50 is blocked without an explicit generalization exception. |
| G24 evidence-first selector preregistration | preregistered mechanism card | G24 freezes the next selector interface before model calls: evidence-first target narration, closed-option adequacy decision, constrained `unknown`/`no seizure frequency reference` escape, and construction-aware option priority. | Next pull is the GPT-4.1-mini cap5/standard50 implementation and run under G24. Do not full-validate, run Qwen, or inspect frozen test until the G25 gate is satisfied. |
| G27 evidence-first selector scale-up | validation mechanism arm / test residual diagnostic | G24/G28/G27 evidence-first target selection reaches 247/299 (82.6%) paper monthly on full validation, above builder-gap GPT's stored 239/299 (79.9%), with 100% schema validity and evidence support. Frozen test is essentially tied with builder-gap GPT at 196/301 (65.1%) versus 197/301 (65.4%) and lower on pragmatic category. | Treat as a useful validation mechanism arm, not a new operational default. Frozen-test rows remain residual-analysis evidence only and must not be used to tune G24. |
| G29 validation-residual selector | rejected arm | G29 implemented the validation-residual-family checkpoint under fixed scorer, loader, split, bridge, candidate-builder, constructor, gold-policy, and repair controls. Smoke passed trace and label-contract gates. Full validation reached 243/299 (81.3%) paper monthly, below G27 at 247/299 (82.6%), with 10 gains and 14 regressions. | Do not promote G29 or run a frozen-test check for this arm. Any future Gan selector needs a new G29-aware mechanism card. |
| G30 GEPA teacher-runner | standard50 rejected arm / runtime gate complete / mechanism open | Matched smoke control `gan_s0_g30_evidence_first_control_gpt4_1_mini_smoke6_20260530T200132Z` and corrected GEPA smoke `gan_s0_g30_evidence_first_gepa_gpt4_1_mini_gpt5_5_reflection_smoke6_20260530T200635Z` proved GPT-4.1-mini prediction plus separate GPT-5.5 reflection can run end-to-end. The subsequent standard50 GEPA run `gan_s0_g30_evidence_first_gepa_gpt4_1_mini_gpt5_5_reflection_standard50_20260530T203349Z` used `max_metric_calls=80`, accepted reflected candidates, and improved the compile-set objective from 10.25/16 to 11.1/16, but expanded the final instruction to 14,639 chars and scored 41/50 paper monthly, 42/50 Purist, 43/50 Pragmatic, 50/50 schema-valid, and 44/44 evidence-supported among present quotes. Versus G24/G28 standard50 at 44/50 monthly, the row ledger is 2 fixes, 4 regressions, 5 shared misses, and 39 shared hits. | Reject this arm as tested. Do not full-validate, run Qwen GEPA, inspect frozen test, or scale this policy-wall instruction. Future GEPA work needs a new compact or stripped-prompt mechanism card. |
| R1.1 schema guard Qwen | held diagnostic | 71.3% monthly, 93.3% schema validity; held after R10, not promoted. |

## Read First

- `gan_s0_pipeline_decomposition_deep_dive_20260528.md` - current decomposition doctrine.
- `gan_s0_g1_g22_research_report_20260529.md` - full current synthesis of the G1-G22 Gan S0 decomposition sequence, including component findings, card ledger, limitations, and next experiments.
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
- `gan_s0_g19_post_g16_error_attribution_audit_20260529.md` - G19 no-model residual attribution over standard50; use this row ledger before G17, G20, or any new selector/adjudicator mechanism.
- `gan_s0_g20_aggregation_constructor_preregistration_20260529.md` - G20 no-model constructor preregistration; use it before implementing exact answer-option construction.
- `gan_s0_g21_aggregation_constructor_report_20260529.md` - G21 fixture-tested quantified-rate constructor report; use it before any closed-option selector card.
- `gan_s0_g22_closed_option_target_selector_preregistration_20260529.md` - G22 preregistered closed-option selector protocol.
- `gan_s0_g22_closed_option_target_selector_report_20260529.md` - G22 standard50 result and before/after ledger; use it before any new Gan selector card.
- `gan_s0_g23_selector_failure_mechanism_audit_20260529.md` - G23 no-model selector failure mechanism audit; use it to frame G24 around evidence-first target narration, special-label escape, and construction-aware option priority.
- `gan_s0_g25_selector_generalization_audit_20260529.md` - G25 no-model sample-size and validation-to-test audit; use its gate before authorizing full-validation, Qwen, or frozen-test selector checks.
- `gan_s0_g24_selector_interface_preregistration_20260529.md` - G24 preregistered evidence-first selector interface; use it before building or running the next GPT standard50 selector arm.
- `gan_s0_g27_full_validation_test_residual_selector_report_20260529.md` - G27 full-validation and frozen-test residual result; use it as residual evidence without tuning from test rows.
- `gan_s0_g29_validation_residual_selector_preregistration_20260529.md` - G29 validation-residual-family selector preregistration.
- `gan_s0_g29_validation_residual_selector_results_20260529.md` - G29 implementation and validation result; rejected as tested.
- `gan_s0_g30_gepa_teacher_runner_preregistration_20260530.md` - G30 hosted GEPA teacher-runner preregistration.
- `gan_s0_g30_gepa_teacher_runner_smoke_results_20260530.md` - G30 hosted GEPA smoke result; runtime/config gate complete before the standard50 follow-up.
- `gan_s0_g30_gepa_teacher_runner_standard50_results_20260530.md` - G30 standard50 GEPA result; optimizer capacity exercised, but the arm is rejected at 41/50 paper monthly.
- `gan_s0_g17_unknown_no_reference_policy_20260529.md` - G17 no-model special-label policy separation; use it before any new unknown/no-reference, unknown-cluster, seizure-free/no-reference, or unclear-frequency selector mechanism.
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
4. Treat G16 as complete for policy definition and G21 as complete for the first
   quantified-rate constructor. G21 passed the G20 fixture gates but creates
   answer options only; it does not select a target label or cover duration,
   special labels, clusters, or inventory gaps.
5. Treat G17 as complete for special-label policy separation, not as a selector.
   Future unknown/no-reference or special-label mechanisms must preserve the
   nine-row G17 ledger and separate unclear-frequency, unknown-cluster,
   seizure-free/no-reference scorer discordance, and concrete-rate overcall
   cases before aggregating paper-facing metrics.
6. Treat G22 as complete and rejected as tested. The closed-option ID-selection
   mechanism preserved traces but reached 39/50 paper monthly on standard50,
   below builder-gap GPT at 41/50 and below the 43/50 stop-rule gate. It is
   useful as a row-level ledger for future work, not as a full-validation
   candidate.
7. Treat G23 as complete for selector failure mechanism analysis. It shows
   candidate absence is not the broad bottleneck: across G8/G10/G15/G22,
   39/57 selector arm-misses had an exact answer option available. G24 should
   test a reframed evidence-first selector with a constrained special-label
   escape and construction-aware option priority, not another closed-option
   ID-selection rerun.
8. Treat G25 as complete for selector run-scope policy. Standard50 remains the
   default mechanism-comparison slice, but a 50-row aggregate is not a
   promotion surface. A future selector gets full validation either by an
   obvious 43/50 standard50 pass with clean overlays, or by a 39-42/50
   preregistered row-ledger exception with no new special-label regression.
   Below 39/50 remains blocked without an explicit generalization exception.
9. Treat G24/G28/G27 as complete for the GPT-4.1-mini evidence-first selector
   scale-up. The arm improves full synthetic validation but does not improve
   frozen-test monthly accuracy over builder-gap GPT, so it is not a new
   operational default.
10. Treat G29 as complete and rejected as tested. It preserved trace completeness
   and the closed-option / constrained-escape contract, but full validation
   regressed versus G27: 243/299 paper monthly versus 247/299, with 10 gains and
   14 regressions. Do not promote G29 or run frozen-test inspection for this arm.
11. Treat G30 as complete for the hosted GEPA teacher-runner smoke and rejected
   standard50 arm. The corrected smoke proved the runner can use GPT-4.1-mini
   for predictions and GPT-5.5 for reflection. The standard50 follow-up used
   `max_metric_calls=80`, accepted reflected candidates, and improved its
   16-record compile objective, but scored only 41/50 paper monthly versus
   G24/G28 at 44/50 and below the G25 43/50 gate. It does not authorize full
   validation, frozen-test inspection, Qwen GEPA, or scaling the accepted
   14,639-character policy-wall instruction. Future GEPA work needs a new
   compact or stripped-prompt mechanism card.
12. Treat G13 as the source-level gate baseline before future selector work: do
   not attribute unclear-frequency or seizure-free gate misses to target
   selection until the G13 false-positive/false-negative rows are accounted for.
   Use the G13 design-implications note to keep deterministic candidates as LLM
   support rather than as a growing semantic adjudicator.
13. Treat G14 as the temporal anchoring diagnostic baseline: the current
   deterministic substrate covers most temporal challenge rows, but two true
   temporal-slot misses remain. Do not expand fragile arithmetic or broad
   relative-anchor guards from G14; route remaining exact misses to
   aggregation-aware answer construction before another target-selection arm.
14. Use G6 surfaces for any new selector/adjudicator execution: the old enriched
   25-record slice is smoke-only, `gan_s0_g6_standard50_v1` is the default
   mechanism-comparison surface, and named challenge sets are diagnostic
   overlays.
15. Keep the G4 negative result, G5 scorer-mode forensics, and G8/G9/G10/G15/G17/G19/G20/G21/G22/G23/G24/G25/G27/G29/G30
   reports as required context for any seizure-free, quantified-rate, unknown,
   no-reference, support-aware, aggregation-constructor, or
   candidate-constrained selector.
16. Keep arithmetic and broad relative-anchor guardrails diagnostic-only until a
   seizure-specific parser exists.
17. Use G19's queue and G23's mechanism framing before choosing the next Gan
   selector: G20 preregistered
   the aggregation-constructor path, G21 implemented the quantified-rate option
   surface, G17 defined the special-label slice, and G22 tested one
   closed-option selector that failed the stop rule. G23 then showed the next
   selector should relax/reframe the interface, not rerun the same shape. G24
   is that preregistered mechanism; G29 is the rejected validation-residual
   follow-up after G27. Any later selector needs a new card and a
   G22-, G27-, and G29-aware before/after ledger, with G25's
   standard50/full-validation/test gate applied before any model-call scale-up.
   Do not tune from frozen-test rows.
18. Use the G5 rescore pack for synthetic-only paper-facing tables; Real(300)
   and Real(150) benchmark reporting remains blocked.

## Filing Guidance

New Gan docs should state which decomposition component they touch and whether
their decision scope is `arm`, `mechanism`, `operational`, `diagnostic`, or
`blocked`.
