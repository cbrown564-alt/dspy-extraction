# Gan S0 G29 Validation-Residual Selector Preregistration

Status: preregistered mechanism card
Date: 2026-05-29
Kanban card: P1 - Gan Validation-First Selector Follow-Up
Dataset/split: Gan 2026 synthetic (`gan_2026_fixed_v1:validation`)
Primary scorer: `gan2026_paper_reproduction` monthly-frequency match, with
repair, range, and tolerance disabled
Diagnostic scorer: `gan_frequency_deterministic_v1`
Model/provider plan: GPT-4.1-mini / OpenAI for the first cap and validation
execution

## Research Question

Can a validation-first residual-family selector reduce the G27 validation
misses without using frozen-test rows to tune prompt wording, candidate policy,
special-label policy, scorer policy, or prediction repair?

G27 showed that the G24/G28 evidence-first selector is useful on synthetic
validation, but not a new operational default after frozen-test residual
inspection. The next mechanism should therefore target validation-visible
failure families and treat the frozen-test result only as a warning about
transfer risk.

## Target Residual Families

The G29 mechanism targets the G27 full-validation residual shape:

| Residual family | G27 validation signal | In scope for G29 |
| --- | ---: | --- |
| Quantified-rate wrong rate or window | 31 gold quantified-rate misses; 17 quantified-to-quantified pairs | yes |
| Unknown or unclear frequency over-called as seizure-free | 11 unknown-to-seizure-free pairs | yes |
| Quantified rate over-called as seizure-free | 9 quantified-to-seizure-free pairs | yes |
| Unknown or unclear frequency over-called as concrete quantified | 4 unknown-to-quantified pairs | yes |
| Unknown-cluster, cluster, and vague/multiple-rate misses | 1 row each on validation, larger on frozen test | diagnostic only for this card |

Frozen-test residuals make cluster and vague/multiple-rate behavior look more
important for later transfer analysis, but they are not target surfaces for
G29. Do not use frozen-test record IDs, wording, or row examples to design this
arm.

## Hypothesis

The G24 interface improved standard50 and validation partly because it put
evidence narration before answer selection. Its remaining validation misses
suggest the next selector needs an explicit **residual-family adjudication
checkpoint** before final label choice:

1. decide whether the note supports an interpretable current quantified target,
   unclear frequency, seizure freedom, cluster frequency, or no seizure
   reference;
2. only then rank closed options or use the constrained special-label escape;
3. require an explicit conflict note when seizure-free evidence and quantified
   evidence compete;
4. require a temporal-window justification when multiple quantified rates are
   available;
5. preserve cluster and unknown-cluster labels when the closed option surface
   supports them, but treat cluster-policy optimization as diagnostic for this
   card.

The varied factor is the target-selection interface. G29 does not change the
candidate builder, `gan.frequency.aggregation_constructor.v1`, scorer,
benchmark bridge, loader, split, prediction repair, or gold-label policy.

## Proposed Mechanism

Implement a new selector variant, tentatively named
`gan_frequency_s0_validation_residual_family_selector`, with prompt version
`gan_frequency_s0_validation_residual_family_selector_v1_0`.

The model receives the same core context as G24:

- full note text;
- raw deterministic temporal candidates;
- G21 constructed quantified-rate options;
- option IDs, option source, label family, and evidence/support metadata.

The new model-facing trace must add a residual-family checkpoint before the G24
final-choice fields:

- `residual_family_adjudication`;
- `target_signal_type`, one of `quantified_rate`, `seizure_free`,
  `unknown_unclear_frequency`, `no_seizure_frequency_reference`, `cluster`,
  `unknown_cluster`, or `other`;
- `competing_signal_summary`;
- `temporal_window_priority`;
- `seizure_free_vs_quantified_decision`;
- `unknown_or_no_reference_decision`;
- `cluster_preservation_decision`;
- `closed_option_adequacy`;
- `selected_option_id`;
- `selected_option_label`;
- `special_label_escape`;
- `final_label`;
- `final_label_source`.

When `closed_option_adequacy` is adequate, `final_label` must be copied from a
closed option. When no option is adequate, the only allowed final labels remain
`unknown` and `no seizure frequency reference`. G29 does not authorize
free-written quantified rates, duration construction, cluster flattening,
unknown-cluster construction, or post-prediction repair.

## Fixed Controls

- Dataset loader: unchanged Gan 2026 loader.
- Split: `gan_2026_fixed_v1:validation`.
- Gold source: `seizure_frequency_number[0]`.
- Reference policy: `reference[0]` remains a secondary difficulty signal only.
- Primary scorer: `gan2026_paper_reproduction`; repair, range, and tolerance
  disabled.
- Diagnostic scorer: `gan_frequency_deterministic_v1`.
- Candidate builder: current deterministic temporal candidate substrate.
- Constructor: `gan.frequency.aggregation_constructor.v1` unchanged.
- Benchmark bridge and normalization policy: unchanged.
- Prediction repair: none beyond selected-option label copy or constrained
  special-label escape.
- Few-shot policy: none.
- Frozen test: blocked from mechanism design and wording changes.

## Validation-First Smoke Slice

Use validation rows only. The cap smoke should include these G27 validation
residual examples:

| Record | G27 residual role |
| --- | --- |
| `gan_10751` | unknown gold over-called as seizure-free. |
| `gan_11380` | G17 unknown row over-called as concrete quantified evidence. |
| `gan_12679` | quantified-rate gold with wrong temporal-window/rate selection. |
| `gan_13019` | quantified-rate gold over-called as `unknown`. |
| `gan_14485` | quantified-rate gold over-called as seizure-free. |
| `gan_10618` | unknown-cluster gold over-called as concrete rate; diagnostic only. |

The smoke passes only if all required trace fields are present, final labels
obey the closed-option or constrained-escape contract, and no frozen-test
examples or wording have been introduced.

## Validation Execution Plan

G29 should be evaluated on validation, not frozen test, with the same scorer
and controls as G27. Standard50 may still be reported as a mechanism slice, but
it is not sufficient for promotion because G29 targets G27 full-validation
residual families.

Report these rows and strata before interpreting aggregate accuracy:

- all G27 validation monthly mismatches;
- G17 special-label rows that appear in validation;
- G21 constructed-option rows;
- quantified-rate wrong-window rows;
- unknown-to-seizure-free and unknown-to-quantified rows;
- quantified-to-seizure-free and quantified-to-unknown rows;
- cluster and vague/multiple-rate rows as diagnostic transfer-risk strata only.

## Ledger Contract

The G29 report must include a before/after ledger keyed by `record_id` with:

- gold label and label family;
- reference label as difficulty context;
- G27 prediction label, final-label source, selected option, and correctness;
- G29 residual-family checkpoint fields;
- G29 selected option, special-label escape, final label, and correctness;
- G13 gate status when available;
- G17 bucket when applicable;
- G21 constructed-exact flag when applicable;
- G22 and G28/G27 correctness when available;
- paper-reproduction monthly, Purist, and Pragmatic correctness;
- canonical monthly correctness as diagnostic;
- improvement/regression tags against G27 and builder-gap GPT;
- whether the row is part of a preregistered target residual family;
- whether any gain depends on scorer repair, prediction repair, range credit,
  or tolerance credit.

## Decision Rules

G29 may proceed from smoke to full validation only if trace completeness and
label-copy/escape constraints pass.

Classify the arm as promising validation mechanism evidence only if it:

- improves G27 paper monthly accuracy on validation by at least 6 records or
  produces a clearly positive paired ledger on the targeted residual families;
- reduces unknown-to-seizure-free and quantified-to-seizure-free mistakes
  without increasing unknown-to-quantified mistakes;
- reduces quantified wrong-window mistakes without lowering pragmatic category
  accuracy;
- creates no new schema-validity or evidence-support failures;
- keeps scorer, loader, split, bridge, candidate-builder, constructor, and
  prediction-repair semantics fixed.

Reject the arm as tested if it:

- repeats the G8/G10/G15 broad prompt shapes;
- makes special-label behavior worse than G27 on the validation target rows;
- relies on frozen-test rows or frozen-test wording;
- free-writes quantified labels outside the closed options;
- improves monthly accuracy only by collapsing scorer-mode distinctions.

Even if G29 succeeds on validation, it is not an operational default until a
separate frozen-test residual check is explicitly authorized and frozen before
inspection. Any later frozen-test check remains diagnostic and must not feed
back into this prompt.

## Non-Goals

G29 does not:

- tune from frozen test;
- change scorer semantics;
- change splits, loaders, gold-label policy, bridge policy, or prediction
  repair;
- add new deterministic candidates or mutate G21 construction;
- solve cluster-policy or vague/multiple-rate transfer behavior;
- make Real(300) or Real(150) benchmark claims.

## Source Artifacts

- `docs/current_research_program.md`
- `docs/component_ceiling_registry.md`
- `docs/planning/kanban_plan.md`
- `docs/experiments/gan/README.md`
- `docs/experiments/gan/gan_s0_g17_unknown_no_reference_policy_20260529.md`
- `docs/experiments/gan/gan_s0_g19_post_g16_error_attribution_audit_20260529.md`
- `docs/experiments/gan/gan_s0_g21_aggregation_constructor_report_20260529.md`
- `docs/experiments/gan/gan_s0_g22_closed_option_target_selector_report_20260529.md`
- `docs/experiments/gan/gan_s0_g23_selector_failure_mechanism_audit_20260529.md`
- `docs/experiments/gan/gan_s0_g24_selector_interface_preregistration_20260529.md`
- `docs/experiments/gan/gan_s0_g25_selector_generalization_audit_20260529.md`
- `docs/experiments/gan/gan_s0_g27_full_validation_test_residual_selector_report_20260529.md`
- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md`

## Decision

G29 is complete as a preregistration card. It authorizes a future implementation
card for a validation-residual-family selector under the fixed controls above.
It does not authorize frozen-test tuning, scorer changes, candidate changes, or
operational-default promotion.
