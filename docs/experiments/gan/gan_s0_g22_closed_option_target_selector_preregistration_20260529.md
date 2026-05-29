# Gan S0 G22 Closed-Option Target Selector Preregistration

Status: preregistered mechanism card
Date: 2026-05-29
Kanban card: G22 - Gan Closed-Option Target Selection Ledger
Dataset/split: Gan 2026 synthetic (`gan_2026_fixed_v1:validation`)
Primary surface: `gan_s0_g6_standard50_v1`
Primary scorer: `gan2026_paper_reproduction` monthly-frequency match, with
repair, range, and tolerance disabled
Diagnostic scorer: `gan_frequency_deterministic_v1` canonical monthly-frequency
match

## Research Question

Can a model choose the correct Gan S0 benchmark target when the answer surface is
closed to indexed raw and constructed options, rather than rerunning the G8
class-first, G10 candidate-ranking, or G15 support-aware prompt shapes?

## Hypothesis

Presenting raw deterministic temporal candidates plus prediction-time G21-style
constructed quantified-rate options as closed answer options will improve
standard50 target selection without changing scorer, loader, split, benchmark
bridge, candidate-builder, constructor, label-construction, or prediction-repair
semantics.

## Mechanism

The new program variant is
`gan_frequency_s0_closed_option_target_selector`, prompt version
`gan_frequency_s0_closed_option_target_selector_v1_2`.

The model receives:

- the full note text;
- a JSON closed-answer-option list containing raw deterministic temporal
  candidates;
- deterministic quantified-rate constructed options emitted by
  `gan.frequency.aggregation_constructor.v1`.

The model must return `selected_option_id`; the final label is copied from the
selected option. The model is not allowed to free-write, repair, normalize, or
invent a label outside the option list.

Constructed options are generated from note text at prediction time in
open-attempt mode and are de-duplicated against raw candidate labels. They are
not gated by gold labels, `reference`, G19 row classes, G17 buckets, or baseline
predictions. G19/G17/G21 information is used only after the run as a row-ledger
overlay.

## Fixed Controls

- Dataset loader: unchanged Gan 2026 loader.
- Split: `gan_2026_fixed_v1:validation`; G6 standard50 record IDs.
- Gold source: `seizure_frequency_number[0]`.
- Reference policy: `reference[0]` remains a secondary difficulty signal only.
- Primary scorer: `gan2026_paper_reproduction`; repair/range/tolerance disabled.
- Diagnostic scorer: canonical `gan_frequency_deterministic_v1`.
- Candidate builder: current deterministic temporal candidate substrate.
- Constructor: `gan.frequency.aggregation_constructor.v1`; no mutation of raw
  candidate records.
- Prediction repair: none beyond closed-option label copy.
- Few-shot policy: none.

## Required Smoke Gate

Before standard50, run
`configs/experiments/gan_s0_g22_closed_option_target_selector_gpt4_1_mini_cap5.json`.

The cap5 smoke passes only if:

- predictions exist for all 5 records;
- `closed_answer_options` is present for all 5 records;
- `selected_closed_answer_option` is present for all non-fallback records;
- any constructed option is reported in `constructed_answer_options`;
- final labels are copied from selected options, not free-written.

Cap5 metrics are traceability diagnostics only.

## Standard50 Comparator

Run
`configs/experiments/gan_s0_g22_closed_option_target_selector_gpt4_1_mini_standard50.json`
only after the cap5 smoke gate clears.

Compare G22 against the same standard50 arms used by G19:

- builder-gap GPT;
- D1 v1.2b schema guard;
- G8 class-first selector;
- G10 candidate-ranking selector;
- G15 support-aware selector.

## Row-Level Ledger Contract

The G22 report must include a before/after ledger keyed by `record_id` with:

- gold label;
- G19 failure class or `none`;
- G17 bucket when applicable;
- raw option labels;
- constructed option labels;
- selected option ID, source, and label;
- selected option family;
- builder-gap, D1, G8, G10, G15, and G22 paper-monthly correctness;
- canonical diagnostic correctness;
- improvement/regression tags against each baseline;
- whether a constructed option was available but not selected;
- whether a selected constructed option was paper-monthly correct.

Keep G19 classes separate:

- `aggregation_block__temporal_slot_missing`;
- `frequency_content_gate__unclear_or_cluster_misrouted_as_concrete`;
- `target_selection__seizure_free_over_quantified`;
- `target_selection__wrong_quantified_rate_or_window`;
- `target_selection__quantified_vs_abstention`;
- `scorer_mode_discordance__canonical_only_correct`;
- `cluster_policy_or_cluster_target_selection`;
- `unknown_no_reference_policy__over_concrete`.

Keep G17 strata separate:

- unknown cluster misrouted as concrete;
- unknown misrouted as concrete quantified evidence;
- unknown misrouted as seizure-free evidence;
- unknown overcalled as a concrete rate despite a correct G13 gate;
- seizure-free/no-reference scorer-mode discordance.

## Stop Rule

G22 is eligible for a later full-validation gate only if standard50:

- reaches at least a two-record paper-monthly lift over the best current
  standard50 baseline;
- has no motivating-overlay regression on target selection,
  seizure-free-versus-quantified, or unknown/no-reference;
- has no G17 nine-row special-label ledger regression against builder-gap GPT;
- preserves closed-option trace fields for all records.

If the stop rule fails, classify G22 as a rejected arm, not a closure of Gan S0
target selection.

## Source Artifacts

- `docs/experiments/gan/gan_s0_g19_post_g16_error_attribution_audit_20260529.json`
- `docs/experiments/gan/gan_s0_g17_unknown_no_reference_policy_20260529.json`
- `docs/experiments/gan/gan_s0_g21_aggregation_constructor_report_20260529.json`
- `docs/experiments/gan/gan_s0_g15_support_aware_target_selector_report_20260529.json`
- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md`
