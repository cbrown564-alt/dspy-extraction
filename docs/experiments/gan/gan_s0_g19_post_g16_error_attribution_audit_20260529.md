# Gan S0 G19 Post-G16 Error Attribution Audit

Status: current synthesis / error attribution audit
Date: 2026-05-29
Kanban card: G19 - Gan Post-G16 Error Attribution Audit
Dataset/split: Gan 2026 synthetic (`gan_2026_fixed_v1:validation`)
Surface: `gan_s0_g6_standard50_v1`
Primary scorer: `gan2026_paper_reproduction` monthly-frequency match, with repair, range, and tolerance disabled
Diagnostic scorer: `gan_frequency_deterministic_v1` canonical monthly-frequency match
Model calls: none
Scorer, loader, split, bridge, prompt, model, candidate-builder, target-selection, and prediction-repair semantics: unchanged.

## Research Question

Which residual Gan S0 standard50 failures remain after G16, and which decomposition component should the next Gan card actually target?

G19 exists to prevent another prompt/interface variation from being selected by intuition. This audit consolidates builder-gap GPT, D1 v1.2b, G8, G10, and G15 on the same G6 standard50 rows, then links every paper-monthly miss back to G13 gate behavior, G14 temporal anchoring coverage, G16 aggregation policy, and G5 scorer-mode caveats.

## Method

The row ledger comes from `docs/experiments/gan/gan_s0_g15_support_aware_target_selector_report_20260529.json`, which already contains the five inspected arms on the same 50 records. G13, G14, and G16 artifacts were joined by `record_id`. The primary residual surface is paper-reproduction monthly-frequency mismatch. Canonical monthly-frequency correctness is reported only as a scorer-mode diagnostic.

Gold remains `seizure_frequency_number[0]`. `reference[0]` remains a secondary difficulty signal, not gold.

Source artifacts:

- `docs/experiments/gan/gan_s0_g15_support_aware_target_selector_report_20260529.json`
- `docs/experiments/gan/gan_s0_g13_frequency_content_gate_report_20260529.json`
- `docs/experiments/gan/gan_s0_g14_temporal_anchoring_report_20260529.json`
- `docs/experiments/gan/gan_s0_g16_aggregation_policy_20260529.json`
- `docs/experiments/gan/gan_s0_g5_paper_scorer_rescore_pack_20260528.json`
- `docs/experiments/gan/gan_s0_g5_scorer_mode_forensics_for_g4_20260528.md`

## Arm Summary

| Arm | Run ID | Paper monthly | Canonical monthly | Paper misses | Canonical-only correct | Paper-only correct |
| --- | --- | --- | --- | --- | --- | --- |
| Builder-gap GPT | gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z | 41/50 | 42/50 | 9 | 1 | 0 |
| D1 v1.2b | gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini_20260528T074900Z | 40/50 | 42/50 | 10 | 2 | 0 |
| G8 class-first selector | gan_s0_g8_special_class_target_selector_gpt4_1_mini_standard50_20260528T233005Z | 37/50 | 36/50 | 13 | 0 | 1 |
| G10 candidate-ranking selector | gan_s0_g10_candidate_ranking_target_selector_gpt4_1_mini_standard50_20260529T005458Z | 36/50 | 35/50 | 14 | 0 | 1 |
| G15 support-aware selector | gan_s0_g15_support_aware_target_selector_gpt4_1_mini_standard50_20260529T013751Z | 31/50 | 30/50 | 19 | 0 | 1 |

The selector variants move in the wrong direction on this surface: G8 has 13 paper-monthly misses, G10 has 14, and G15 has 19, versus 9 for builder-gap GPT and 10 for D1 v1.2b.

## Failure Classes

Across five arms there are 65 paper-monthly arm-misses across 29 unique rows.

| Failure class | Arm-misses | Unique rows | Affected components | Interpretation |
| --- | --- | --- | --- | --- |
| `aggregation_block__temporal_slot_missing` | 16 | 4 | aggregation, temporal_anchoring, candidate_inventory | Aggregation block with missing temporal slot |
| `frequency_content_gate__unclear_or_cluster_misrouted_as_concrete` | 15 | 6 | frequency_content_gate, unknown_no_reference_policy, target_selection | Frequency-content gate or unclear-frequency policy misroutes unclear/cluster evidence as concrete |
| `target_selection__seizure_free_over_quantified` | 11 | 6 | target_selection | Target selection chooses seizure-free over quantified evidence |
| `target_selection__wrong_quantified_rate_or_window` | 11 | 5 | target_selection, temporal_window_selection | Target selection chooses the wrong quantified rate or temporal window |
| `target_selection__quantified_vs_abstention` | 5 | 4 | target_selection, unknown_no_reference_policy | Target selection chooses abstention/unknown despite quantified gold |
| `scorer_mode_discordance__canonical_only_correct` | 3 | 2 | scorer_mode_caveat, target_selection | Scorer-mode discordance: canonical monthly correct, paper monthly wrong |
| `cluster_policy_or_cluster_target_selection` | 3 | 3 | target_selection, label_construction, cluster_policy | Cluster policy or cluster target-selection miss |
| `unknown_no_reference_policy__over_concrete` | 1 | 1 | unknown_no_reference_policy, target_selection | Unknown/no-reference policy chooses concrete frequency for unclear gold |

No standard50 paper-monthly miss is a safe deterministic surface repair. The failures are semantic target-selection errors, special-label policy errors, cluster/rate policy errors, scorer-mode caveats, or exact answer-option construction blocks.

## Row-Level Ledger

| Record | Gold | Missed by | Failure class | G13/G14/G16 links |
| --- | --- | --- | --- | --- |
| `gan_14485` | `2 per 3 month` | G8 class-first selector, G10 candidate-ranking selector, G15 support-aware selector | `target_selection__seizure_free_over_quantified` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_6532` | `unknown, multiple per cluster` | G8 class-first selector, G10 candidate-ranking selector | `frequency_content_gate__unclear_or_cluster_misrouted_as_concrete` | G13 unknown_unclear_frequency -> quantified_frequency_presence (mismatch); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_13123` | `1 per year` | G15 support-aware selector | `target_selection__seizure_free_over_quantified` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_4702` | `multiple per day` | D1 v1.2b | `target_selection__quantified_vs_abstention` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_1794` | `8 per 2 month` | Builder-gap GPT | `target_selection__wrong_quantified_rate_or_window` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_15306` | `2 to 3 per 15 month` | G8 class-first selector, G10 candidate-ranking selector, G15 support-aware selector | `target_selection__seizure_free_over_quantified` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_7894` | `seizure free for multiple year` | Builder-gap GPT, D1 v1.2b | `scorer_mode_discordance__canonical_only_correct` | G13 seizure_free -> seizure_free (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_3246` | `2 cluster per month, 4 per cluster` | G15 support-aware selector | `cluster_policy_or_cluster_target_selection` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_4113` | `1 per 1 to 2 day` | Builder-gap GPT, D1 v1.2b, G15 support-aware selector | `target_selection__quantified_vs_abstention`<br>`target_selection__seizure_free_over_quantified`<br>`target_selection__wrong_quantified_rate_or_window` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_14881` | `1 per month` | G8 class-first selector, G15 support-aware selector | `target_selection__seizure_free_over_quantified` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_4709` | `multiple per day` | Builder-gap GPT, D1 v1.2b | `target_selection__quantified_vs_abstention` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_9566` | `unknown` | G8 class-first selector, G10 candidate-ranking selector, G15 support-aware selector | `frequency_content_gate__unclear_or_cluster_misrouted_as_concrete` | G13 unknown_unclear_frequency -> quantified_frequency_presence (mismatch); G14 upstream_g13_gate_caveat; G16 outside_rate_duration_aggregation_policy |
| `gan_12679` | `1 per day` | G8 class-first selector, G10 candidate-ranking selector, G15 support-aware selector | `target_selection__wrong_quantified_rate_or_window` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_15997` | `10 per 3 month` | Builder-gap GPT, D1 v1.2b, G8 class-first selector, G10 candidate-ranking selector, G15 support-aware selector | `aggregation_block__temporal_slot_missing` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 temporal_slot_miss; G16 aggregation_required_temporal_slot_missing |
| `gan_17287` | `1 per 1 to 2 day` | Builder-gap GPT | `target_selection__wrong_quantified_rate_or_window` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_16772` | `9 per 5 month` | Builder-gap GPT, D1 v1.2b, G8 class-first selector, G10 candidate-ranking selector, G15 support-aware selector | `aggregation_block__temporal_slot_missing` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 temporal_slot_miss; G16 aggregation_required_temporal_slot_missing |
| `gan_16825` | `10 per 6 month` | G8 class-first selector, G10 candidate-ranking selector, G15 support-aware selector | `aggregation_block__temporal_slot_missing` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 temporal_slot_miss; G16 aggregation_required_temporal_slot_missing |
| `gan_10398` | `1 cluster per week, 2 per cluster` | G15 support-aware selector | `cluster_policy_or_cluster_target_selection` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_16041` | `9 per 3 month` | Builder-gap GPT, D1 v1.2b, G8 class-first selector, G10 candidate-ranking selector, G15 support-aware selector | `target_selection__wrong_quantified_rate_or_window` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_12465` | `1 per day` | Builder-gap GPT | `target_selection__quantified_vs_abstention` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_804` | `1 per month` | D1 v1.2b | `cluster_policy_or_cluster_target_selection` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_22` | `3 per day` | G15 support-aware selector | `target_selection__seizure_free_over_quantified` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_16335` | `7 per 3 month` | G8 class-first selector, G10 candidate-ranking selector, G15 support-aware selector | `aggregation_block__temporal_slot_missing` | G13 quantified_frequency_presence -> quantified_frequency_presence (match); G14 temporal_slot_miss; G16 aggregation_required_temporal_slot_missing |
| `gan_5974` | `unknown` | G8 class-first selector, G10 candidate-ranking selector, G15 support-aware selector | `frequency_content_gate__unclear_or_cluster_misrouted_as_concrete` | G13 unknown_unclear_frequency -> seizure_free (mismatch); G14 upstream_g13_gate_caveat; G16 outside_rate_duration_aggregation_policy |
| `gan_6607` | `unknown` | G10 candidate-ranking selector, G15 support-aware selector | `frequency_content_gate__unclear_or_cluster_misrouted_as_concrete` | G13 unknown_unclear_frequency -> quantified_frequency_presence (mismatch); G14 upstream_g13_gate_caveat; G16 outside_rate_duration_aggregation_policy |
| `gan_6387` | `unknown` | D1 v1.2b | `unknown_no_reference_policy__over_concrete` | G13 unknown_unclear_frequency -> unknown_unclear_frequency (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_8264` | `seizure free for 4 month` | D1 v1.2b | `scorer_mode_discordance__canonical_only_correct` | G13 seizure_free -> seizure_free (match); G14 exact_temporal_candidate_present; G16 closed_option_already_available |
| `gan_14002` | `unknown` | G10 candidate-ranking selector, G15 support-aware selector | `frequency_content_gate__unclear_or_cluster_misrouted_as_concrete` | G13 unknown_unclear_frequency -> seizure_free (mismatch); G14 upstream_g13_gate_caveat; G16 outside_rate_duration_aggregation_policy |
| `gan_11380` | `unknown` | G8 class-first selector, G10 candidate-ranking selector, G15 support-aware selector | `frequency_content_gate__unclear_or_cluster_misrouted_as_concrete` | G13 unknown_unclear_frequency -> quantified_frequency_presence (mismatch); G14 upstream_g13_gate_caveat; G16 outside_rate_duration_aggregation_policy |

## Interpretation

### 1. Aggregation is a real structural block, but it is not the whole problem

G16's `aggregation_required_temporal_slot_missing` class accounts for 16 arm-misses on four standard50 rows: `gan_15997`, `gan_16772`, `gan_16825`, and `gan_16335`. The first two are missed by all five inspected arms. This is the cleanest G20 input because exact closed answer options are not yet supported by the current candidate surface.

### 2. Unknown and unclear-frequency failures are broader than no-reference string confusion

The special-label slice is not merely `unknown` versus `no seizure frequency reference`. The repeated rows include unclear-frequency and unknown-cluster cases that the G13 gate routes toward concrete quantified or seizure-free evidence: `gan_6532`, `gan_9566`, `gan_5974`, `gan_6607`, `gan_14002`, and `gan_11380`. G17 should therefore cover unknown/no-reference boundaries plus unclear-frequency-over-concrete and unknown-cluster policy.

### 3. G8/G10/G15 mostly introduce closed-option target-selection regressions

Many G8/G10/G15 misses occur where G14 says the exact candidate already exists and G16 says `closed_option_already_available`. The main repeated patterns are seizure-free-over-quantified choices and wrong quantified temporal-window choices. This rejects the tested prompt/interface shapes, not target selection as a mechanism class.

### 4. Scorer-mode discordance remains important but smaller on standard50

Canonical-only correct rows are `gan_7894` and `gan_8264`, where paper-facing semantics penalize seizure-free gold predicted as `no seizure frequency reference`. This matches the G5 forensics: it is a benchmark target-semantics issue, not a reason to rewrite predictions after the fact.

### 5. Evidence/schema is not the active standard50 bottleneck

All inspected standard50 predictions were scored for every arm. No G19 residual class is an evidence-support or schema-validity failure. Evidence and schema checks remain diagnostic gates, but the observed bottleneck is semantic selection and exact answer-option construction.

## Optimization Queue

| Rank | Next card | Rows | Affected row IDs | Recommendation |
| --- | --- | --- | --- | --- |
| 1 | G20 - Gan Aggregation Constructor Preregistration | 4 | `gan_15997`, `gan_16335`, `gan_16772`, `gan_16825` | Preregister exact answer-option construction and duration/rate fixture policy before implementing a constructor or rerunning exact closed-option selectors. |
| 2 | G17 - Gan Unknown vs. No-Reference Policy Separation | 9 | `gan_11380`, `gan_14002`, `gan_5974`, `gan_6387`, `gan_6532`, `gan_6607`, `gan_7894`, `gan_8264`, `gan_9566` | Scope G17 beyond a string distinction: include unclear-frequency, unknown-cluster, seizure-free/no-reference scorer discordance, and concrete-rate overcalls. |
| 3 | New G-card - Closed-Option Target Selection Ledger | 16 | `gan_10398`, `gan_12465`, `gan_12679`, `gan_13123`, `gan_14485`, `gan_14881`, `gan_15306`, `gan_16041`, `gan_17287`, `gan_1794`, `gan_22`, `gan_3246`, `gan_4113`, `gan_4702`, `gan_4709`, `gan_804` | Do not rerun G8/G10/G15 prompt shapes; preregister a narrower comparator over rows with exact candidates already available. |

## Decision

G19 is complete as a no-model error-attribution audit. The next Gan pull should not be another broad selector prompt. The strongest sequenced path is:

1. Pull G20 to preregister an aggregation/duration constructor against the four standard50 aggregation-block rows and the G11 exact-miss challenge rows.
2. Pull G17 with the G19 special-label slice, scoped to unclear-frequency, unknown-cluster, seizure-free/no-reference scorer discordance, and concrete-rate overcalls.
3. Only then open a new closed-option target-selection card, with a before/after ledger for the G19 row classes it intends to reduce.

## Companion Artifact

`docs/experiments/gan/gan_s0_g19_post_g16_error_attribution_audit_20260529.json` contains the row-level residual ledger, per-arm failure counts, scorer-mode crosstabs, affected components, and recommended next-card queue.
