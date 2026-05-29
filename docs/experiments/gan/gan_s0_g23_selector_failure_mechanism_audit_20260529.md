# Gan S0 G23 Selector Failure Mechanism Audit

Status: current synthesis / failure-mechanism audit
Date: 2026-05-29
Kanban card: G23 - Gan Selector Failure Mechanism Audit
Dataset/split: Gan 2026 synthetic (`gan_2026_fixed_v1:validation`)
Surface: `gan_s0_g6_standard50_v1`
Primary scorer: `gan2026_paper_reproduction` monthly-frequency match, with repair, range, and tolerance disabled
Diagnostic scorer: `gan_frequency_deterministic_v1` canonical monthly-frequency match
Model calls: none
Scorer, loader, split, bridge, prompt, model, candidate-builder, constructor, target-selection, and prediction-repair semantics: unchanged.

## Research Question

Why do the G8, G10, G15, and G22 target-selection arms choose the wrong
answer, especially when a correct answer option is already available?

This audit tests the working hypothesis from the Kanban board: the current
candidate/closed-option interface may be too restrictive for the model, or the
task may be described poorly enough that the model picks a wrong available
candidate even when the answer surface contains the gold-compatible option.

## Method

G23 is a no-model synthesis over existing artifacts. It joins the G19 residual
classes, G17 special-label buckets, G21 exact-option coverage, and G22
before/after ledger. The row-level surface is the locked 50-record G6
mechanism slice. Gold remains `seizure_frequency_number[0]`; `reference[0]`
is used only as a difficulty cross-check.

Source artifacts inspected:

- `docs/experiments/gan/gan_s0_g8_special_class_target_selector_report_20260529.{md,json}`
- `docs/experiments/gan/gan_s0_g10_candidate_ranking_target_selector_report_20260529.{md,json}`
- `docs/experiments/gan/gan_s0_g15_support_aware_target_selector_report_20260529.{md,json}`
- `docs/experiments/gan/gan_s0_g17_unknown_no_reference_policy_20260529.{md,json}`
- `docs/experiments/gan/gan_s0_g19_post_g16_error_attribution_audit_20260529.{md,json}`
- `docs/experiments/gan/gan_s0_g21_aggregation_constructor_report_20260529.{md,json}`
- `docs/experiments/gan/gan_s0_g22_closed_option_target_selector_report_20260529.{md,json}`
- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md`

Run artifacts inspected:

- `archive/runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z/{metrics.json,errors.json,predictions.json}`
- `runs/gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini_20260528T074900Z/{metrics.json,errors.json,predictions.json}`
- `runs/gan_s0_g8_special_class_target_selector_gpt4_1_mini_standard50_20260528T233005Z/{metrics.json,errors.json,predictions.json}`
- `runs/gan_s0_g10_candidate_ranking_target_selector_gpt4_1_mini_standard50_20260529T005458Z/{metrics.json,errors.json,predictions.json}`
- `runs/gan_s0_g15_support_aware_target_selector_gpt4_1_mini_standard50_20260529T013751Z/{metrics.json,errors.json,predictions.json}`
- `runs/gan_s0_g22_closed_option_target_selector_gpt4_1_mini_standard50_20260529T105421Z/{metrics.json,errors.json,predictions.json,prompts.json}`

## Arm Summary

| Arm | Run ID | Paper monthly | Canonical monthly | Decision role |
| --- | --- | ---: | ---: | --- |
| Builder-gap GPT | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` | 41/50 | 42/50 | synthetic operational baseline |
| D1 v1.2b | `gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini_20260528T074900Z` | 40/50 | 42/50 | mechanism baseline |
| G8 class-first selector | `gan_s0_g8_special_class_target_selector_gpt4_1_mini_standard50_20260528T233005Z` | 37/50 | 36/50 | rejected arm |
| G10 candidate-ranking selector | `gan_s0_g10_candidate_ranking_target_selector_gpt4_1_mini_standard50_20260529T005458Z` | 36/50 | 35/50 | rejected arm |
| G15 support-aware selector | `gan_s0_g15_support_aware_target_selector_gpt4_1_mini_standard50_20260529T013751Z` | 31/50 | 30/50 | rejected arm |
| G22 closed-option selector | `gan_s0_g22_closed_option_target_selector_gpt4_1_mini_standard50_20260529T105421Z` | 39/50 | 39/50 | rejected arm, best selector trace ledger |

## Selector Miss Ledger

Across the four selector arms G8, G10, G15, and G22, there are 57
paper-monthly selector arm-misses across 20 unique rows.

| Arm | Selector misses | Exact option available | Exact option absent |
| --- | ---: | ---: | ---: |
| G8 class-first selector | 13 | 10 | 3 |
| G10 candidate-ranking selector | 14 | 9 | 5 |
| G15 support-aware selector | 19 | 14 | 5 |
| G22 closed-option selector | 11 | 6 | 5 |
| **Total selector arm-misses** | **57** | **39** | **18** |

The main finding is that candidate absence is not the dominant selector
failure. In 39/57 selector arm-misses, the G21/G22 surface already contained
an exact gold-compatible option. The model often chose the wrong available
candidate.

The unique-row recurrence pattern is also not random-looking noise:

| Selector arms missing the same row | Unique rows |
| ---: | ---: |
| 4/4 selector arms | 7 |
| 3/4 selector arms | 6 |
| 2/4 selector arms | 4 |
| 1/4 selector arms | 3 |

Failure classes are not mutually exclusive, but the repeated selector-miss
classes are:

| Failure class | Selector arm-miss count | Interpretation |
| --- | ---: | --- |
| `frequency_content_gate__unclear_or_cluster_misrouted_as_concrete` | 20 | Unknown or unclear-frequency gold is represented to the selector as concrete or seizure-free evidence. |
| `aggregation_block__temporal_slot_missing` | 14 | The exact answer requires constructed aggregation or temporal-slot policy. |
| `target_selection__seizure_free_over_quantified` | 11 | Selector chooses seizure-free evidence over benchmark gold-compatible quantified evidence. |
| `target_selection__wrong_quantified_rate_or_window` | 9 | Selector chooses the wrong rate or observation window among available quantified options. |
| `cluster_policy_or_cluster_target_selection` | 4 | Selector flattens or misroutes cluster labels. |
| `target_selection__quantified_vs_abstention` | 1 | Selector chooses the wrong abstention/quantified side. |

## G22 Wrong Rows

G22 is the cleanest trace ledger because closed options were present in 50/50
rows, a selected option was present in 50/50 rows, and the final label was
copied from the selected option in 50/50 rows. Its 11 paper-monthly misses
therefore isolate selection/interface behavior rather than schema validity or
surface-form repair.

| Record | Gold | Exact option? | Selected label | Mechanism read |
| --- | --- | --- | --- | --- |
| `gan_3246` | `2 cluster per month, 4 per cluster` | yes | `4 per month` | Cluster policy flattened cluster rate into a simple monthly rate. |
| `gan_9566` | `unknown` | no | `1 to 2 per 8 week` | Special-label answer absent; closed options force a concrete quantified choice. |
| `gan_12679` | `1 per day` | yes | `1 to 2 per month` | Wrong seizure-type/rate priority despite exact daily option. |
| `gan_16772` | `9 per 5 month` | yes, constructed | `11 per 3 month` | Constructed exact option present but ranked below raw narrower-window option. |
| `gan_16825` | `10 per 6 month` | yes, constructed | `12 per 3 month` | Constructed exact option present but ranked below raw narrower-window option. |
| `gan_10398` | `1 cluster per week, 2 per cluster` | yes | `unknown, 2 per cluster` | Cluster spacing was explicit, but selector chose unknown-spacing cluster option. |
| `gan_16041` | `9 per 3 month` | yes | `9 per 2 month` | Wrong temporal window despite exact option. |
| `gan_5974` | `unknown` | no | `seizure free for 1 year` | Special-label answer absent; closed options force seizure-free choice. |
| `gan_6607` | `unknown` | no | `2 to 3 per month` | Candidate came from migraine frequency; selector reasoned no-reference but had no valid final option. |
| `gan_14002` | `unknown` | no | `seizure free for multiple month` | Candidate came from family-history/no-seizure mention; selector reasoned no-reference but had no valid final option. |
| `gan_11380` | `unknown` | no | `2 per 3 month` | Special-label answer absent; closed options force concrete quantified choice. |

G22 wrong rows split into two different failure mechanisms:

- **Exact option available, wrong choice:** 6/11 G22 misses. These are true
  target-selection or task-framing failures: cluster flattening, wrong rate or
  window, and constructed-option deprioritization.
- **Exact option absent, wrong forced choice:** 5/11 G22 misses. These are all
  G17 unknown rows where the active option surface did not include a correct
  special-label answer. The closed-option interface prevents the model from
  returning the clinically/benchmark-correct abstention.

## Mechanism Distinctions

### Candidate Absence

Candidate absence is a real problem only for the special-label subset, not the
broad selector surface. G21 gives combined exact option coverage for 45/50
standard50 rows. Across all four selector arms, 39/57 misses occur despite an
exact option being available. For G22, the five exact-absent wrong rows are all
unknown-special-label rows: `gan_9566`, `gan_5974`, `gan_6607`, `gan_14002`,
and `gan_11380`.

This argues against a general "add more candidates" card. It argues for a
special-label escape or freer target narration when the available option list
does not contain an adequate benchmark label.

### Option Overload

Option overload is plausible for the exact-available wrong rows, but it is not
the whole explanation. The six G22 exact-available wrong rows had 4, 8, 7, 8,
9, and 7 closed options, respectively. The hardest rows contain multiple
quantified windows, duplicate raw options, seizure-free distractors, cluster
variants, and sometimes a constructed G21 option.

The clearest overload pattern is not merely "too many options"; it is
**undifferentiated option priority**. In `gan_16772` and `gan_16825`, the
constructed exact G21 option was present, but the model selected a raw
narrower-window quantified option. In `gan_10398`, explicit cluster spacing
was present, but the model selected the unknown-spacing cluster option.

### Closed-Option Restriction

The closed-option interface is helpful as a traceability and label-copying
guard, but too restrictive when the option set is wrong or incomplete. G22
corrected 18 baseline/selector misses, selected constructed options correctly
for `gan_15997` and `gan_16335`, and copied final labels from selected options
in 50/50 rows. Those are useful properties.

The same restriction fails on the five G17 unknown rows with no exact option.
Two examples expose the mismatch sharply:

- `gan_6607`: the selected evidence is migraine frequency, and the model's
  reason-code says no seizure-frequency data are present, but the final label
  is forced to the only closed option, `2 to 3 per month`.
- `gan_14002`: the model's reason-code says no seizure-frequency information
  is present, but the final label is forced to `seizure free for multiple
  month`.

Therefore the next selector should not abandon closed options wholesale. It
should keep closed options as support, but allow an evidence-first decision to
reject all options or emit a constrained special-label answer when the option
surface is inadequate.

### Poor Task Description

G22's prompt guidance includes useful rules, but the trace suggests that the
task framing under-specifies the benchmark target in multi-signal rows. The
selector repeatedly explains its wrong choice as if it followed a sensible
local policy:

- `gan_12679`: selects `1 to 2 per month` as the current generalized
  tonic-clonic frequency even though the gold-compatible option is `1 per day`
  from daily absences.
- `gan_16772` and `gan_16825`: selects a raw current window over a constructed
  aggregate option.
- `gan_3246`: selects a simple `4 per month` rate instead of the full cluster
  label.
- `gan_10398`: selects unknown cluster spacing despite explicit weekly cluster
  spacing in the same evidence.

The selector is not simply ignoring evidence. It is following an insufficiently
specified priority scheme for benchmark label choice. G24 should therefore test
a changed reasoning interface, not another label-list prompt with the same
implicit target policy.

### Wrong Clinical Or Benchmark Target Policy

The dominant exact-available misses are target-policy errors: which seizure
type, which temporal window, whether to preserve clusters, and whether to use
constructed aggregate options. Some of these policies are clinically natural
but benchmark-wrong, or locally plausible but incompatible with the Gan label
scheme. The next arm must separate clinical interpretation from final
benchmark-label selection.

### Scorer-Mode Discordance

Scorer-mode discordance is smaller than the selector bottleneck on standard50.
G19 had three canonical-only-correct arm-misses across two rows, `gan_7894`
and `gan_8264`. G22 scores 39/50 under both paper and canonical monthly views,
so its current failure is not primarily scorer-mode collapse.

Reports must still keep scorer modes separated. These rows are benchmark
semantics caveats, not deterministic repair candidates.

### Temporal-Window Confusion

Temporal-window confusion remains a major part of the exact-available miss
surface. Across selector arms, wrong quantified rate/window accounts for nine
selector arm-misses, and aggregation/temporal-slot rows account for fourteen.
G22 still misses `gan_16041`, `gan_16772`, and `gan_16825` after G21
construction, which means answer-option construction alone is not sufficient:
the selector needs a construction-aware priority rule.

### Special-Label Confusion

Special-label confusion is the biggest G22 regression against builder-gap GPT.
G22 scores 5/10 on the unknown/no-reference overlay, while builder-gap GPT is
10/10. The five G17 builder-gap regressions are `gan_9566`, `gan_5974`,
`gan_6607`, `gan_14002`, and `gan_11380`.

The mechanism is not a simple `unknown` versus `no seizure frequency reference`
string confusion. It is upstream gate/candidate presentation plus a closed
selector that lacks an "available options do not support a seizure-frequency
label" escape path.

### Small-Sample Noise

Standard50 remains a mechanism surface, not a promotion surface. One record is
2 percentage points, and G22's run-level bootstrap interval for monthly
accuracy is broad (`0.66` to `0.88`). Small-sample noise can affect arm ranking
between 36/50, 37/50, 39/50, 40/50, and 41/50.

But noise does not explain the repeated row-level pattern. Seven rows are
missed by all four selector arms, and thirteen rows are missed by at least
three selector arms. The mechanism conclusion is therefore stable enough for a
preregistration card, while G25 remains necessary before deciding whether a
lower-standard50 arm deserves full validation or test-residual inspection.

## Decision

G23 is complete as a no-model failure-mechanism audit.

The next selector should **relax and reframe** the closed-option interface, not
repeat G8/G10/G15/G22. The best-supported G24 hypothesis is:

> Evidence-first target narration with constrained final output will reduce
> special-label forced-choice errors and constructed-option deprioritization
> compared with closed-option ID selection alone.

The next selector should keep scorer, loader, split, benchmark bridge,
candidate-builder, G21 constructor, and prediction-repair semantics fixed. It
should vary only the model-facing selection interface.

Minimum G24 requirements:

- Start from evidence-first reasoning before option ranking.
- Let the model say that no closed option is adequate, but constrain the final
  fallback to allowed Gan special labels.
- Preserve selected option IDs when an option is used.
- Preserve a row-level before/after ledger for the G17 rows, the G21
  constructed-option rows (`gan_15997`, `gan_16772`, `gan_16825`,
  `gan_16335`), and the exact-available target-selection rows
  (`gan_3246`, `gan_10398`, `gan_12679`, `gan_16041`).
- Report `gan2026_paper_reproduction` as primary and canonical metrics as
  diagnostics.
- Do not full-validate or run Qwen until G24 and G25 define the mechanism and
  generalization gate.

## Residual Risk

This audit uses stored standard50 artifacts only. It does not estimate
generalization behavior across full validation or frozen test residual rows.
G25 remains the right next no-model card for sample-size and generalization
policy before another model-call batch is promoted beyond the standard50
mechanism slice.
