# Gan S0 G20 Aggregation Constructor Preregistration

Status: mechanism open / preregistered no-model constructor protocol
Date: 2026-05-29
Related card: G20 - Gan Aggregation Constructor Preregistration
Dataset/split: Gan 2026 synthetic (`gan_2026_fixed_v1:validation`)
Primary surface: `gan_s0_g6_standard50_v1`
Challenge surface: `gan_s0_g6_candidate_coverage_exact_miss`
Model calls: none
Scorer, loader, split, bridge, prompt, model, candidate-builder,
target-selection, and prediction-repair semantics: unchanged.

## Research Question

Can exact closed answer options for Gan S0 be constructed deterministically for
the aggregation-block rows identified by G16 and G19, without changing the
candidate inventory, scorer, selector, or prediction-repair policy?

This card asks only whether the next implementation should be deterministic,
model-mediated, or deferred. It does not implement the constructor and does not
claim a selector improvement.

## Decision

The next implementation should be a **deterministic, fixture-first aggregation
constructor** for quantified-rate rows only.

Do not use a model-mediated constructor for the first pass. G19 shows a compact
and interpretable rate-aggregation block: 16 arm-misses across four standard50
rows, all with category-equivalent candidates but missing exact answer options.
The correct next step is to test whether explicitly supported counts and
observation windows can produce additional answer options before another LLM
selector sees the row.

Do not include seizure-free duration aggregation in the first constructor.
Duration rows remain policy fixtures, but they require a separate duration rule
because seizure-free duration is not the same operation as quantified rate
aggregation.

## Varied Component

The varied component is canonical label construction and aggregation.

The constructor may add a new constructed answer option with structured
provenance. It must not choose the final benchmark target, rewrite existing raw
candidates, repair model predictions, change scorer normalization, or collapse
special labels.

## Motivation From Prior Evidence

G16 defined the rate/duration policy boundary. On the G11 exact-miss challenge,
14/21 rows require quantified rate aggregation with missing temporal slots, 2/21
require seizure-free duration policy, 4/21 are candidate-inventory gaps, and
1/21 is outside rate/duration policy. On standard50, four rows are quantified
rate aggregation blocks and 41/50 already have exact options.

G14 found that most temporal anchoring is already represented by the current
deterministic substrate, but `gan_16772` and `gan_16825` are true temporal-slot
misses on the temporal challenge. G19 then showed that the standard50
aggregation rows remain a leading optimization class across current baselines
and rejected selector arms.

The practical implication is narrow: exact answer-option construction is a
missing interface for some rows, but it is not evidence that target selection is
solved.

## In-Scope Policy Cases

| Policy class | Constructor status | Rule |
| --- | --- | --- |
| `aggregation_required_temporal_slot_missing` | eligible | Construct only when explicit seizure-event counts and an explicit observation window can be represented with traceable source support. |
| `closed_option_already_available` | no-op control | Preserve the existing exact option and emit no replacement. |
| `duration_aggregation_policy_required` | deferred fixture | Report separately; do not construct quantified-rate labels from seizure-free duration evidence. |
| `candidate_inventory_gap_before_aggregation` | negative control | Do not construct when the candidate inventory lacks category-equivalent seizure-frequency support. |
| `outside_rate_duration_aggregation_policy` | negative control | Route unknown, no-reference, and unknown-cluster cases to G17 or cluster policy. |

## Fixture Rows

### Primary Standard50 Fixtures

These are the G19 aggregation-block rows and the primary standard50 constructor
gate:

| Record | Gold label | Current candidate labels | G14/G16 class |
| --- | --- | --- | --- |
| `gan_15997` | `10 per 3 month` | `3 per week`; `4 per month`; `3 per month`; seizure-free and cluster distractors | temporal-slot miss / aggregation required |
| `gan_16772` | `9 per 5 month` | `8 per 2 month`; `11 per 3 month`; `11 per 10 month`; `11 per month`; seizure-free and cluster distractors | temporal-slot miss / aggregation required |
| `gan_16825` | `10 per 6 month` | `12 per 2 month`; `12 per 3 month`; `8 per 3 month`; `8 per 10 month`; `8 per month`; cluster distractor | temporal-slot miss / aggregation required |
| `gan_16335` | `7 per 3 month` | `1 per month`; `4 per 3 month` | temporal-slot miss / aggregation required |

### G11 Exact-Miss Challenge Fixtures

Quantified-rate aggregation fixtures:

`gan_15997`, `gan_16772`, `gan_16825`, `gan_16335`, `gan_1463`,
`gan_9424`, `gan_6094`, `gan_7431`, `gan_16883`, `gan_3355`,
`gan_13290`, `gan_6509`, `gan_4378`, `gan_9526`.

Deferred duration fixtures:

`gan_4996`, `gan_9063`.

Negative controls for candidate-inventory gaps:

`gan_1486`, `gan_15129`, `gan_6296`, `gan_13019`.

Negative control outside rate/duration aggregation:

`gan_10583`.

## Permitted Deterministic Transformations

- Normalize label units only to the already audited Gan label grammar: singular
  time units, numeric counts, numeric ranges, and the literal `multiple` token.
- Sum explicitly supported seizure-event counts when the source evidence states
  the events are part of the same benchmark target scope.
- Represent explicitly stated observation windows such as `past N months`,
  `last N weeks`, or named-month spans when the endpoint and included months are
  source-supported.
- Emit a constructed option as a separate answer-option record with provenance:
  source row, source evidence, contributing candidate IDs or text spans,
  numerator, denominator, unit, derivation kind, and policy class.
- Preserve raw candidate options and their evidence unchanged.
- Report category-equivalent coverage separately from exact constructed-option
  coverage.

## Forbidden Repairs

- Do not infer the constructed answer from the gold label during runtime; gold is
  allowed only inside fixture expected outputs.
- Do not rewrite `unknown`, `no seizure frequency reference`, unknown-cluster,
  or seizure-free labels into quantified-rate labels.
- Do not flatten cluster labels into simple rates unless a later cluster-policy
  card explicitly preregisters that operation.
- Do not choose the final target label. The constructor creates options only;
  target selection remains a separate component.
- Do not use `reference[0]` as gold or as an answer-construction target.
- Do not enable scorer repair, prediction repair, range credit, or tolerance
  credit to make constructed options look correct.
- Do not add broad date arithmetic or relative-anchor guardrails beyond
  seizure-frequency evidence explicitly represented in the row.
- Do not construct labels for `candidate_inventory_gap_before_aggregation`,
  `outside_rate_duration_aggregation_policy`, or deferred duration fixtures.

## Expected Metrics And Gates

Construction coverage is not selector performance. It should be reported as
candidate/answer-option coverage before any model-backed selector run.

| Surface | Baseline exact option coverage | Expected constructor target | Gate |
| --- | ---: | ---: | --- |
| `gan_s0_g6_standard50_v1` | 41/50 | up to 45/50 if all four standard50 aggregation rows construct exact options | At least 3/4 G19 aggregation rows construct exact options, with 0 changes to closed-option rows. |
| `gan_s0_g6_candidate_coverage_exact_miss` | 0/21 | up to 14/21 quantified-rate exact constructed options | At least 10/14 quantified-rate fixtures construct exact options, with 0 constructed options for the 7 deferred or negative-control rows. |
| deferred duration fixtures | 0/2 | 0/2 in the first pass | No quantified-rate construction is allowed. |
| inventory-gap and outside-policy controls | 0/5 | 0/5 | Any constructed option here fails the gate. |

If the standard50 gate passes, a later selector/adjudicator card may compare
closed-option target selection with a row-level before/after ledger. That later
card must still use `gan2026_paper_reproduction` as the benchmark-facing scorer
and `gan_frequency_deterministic_v1` only as a diagnostic view.

## Required Diagnostics For Implementation

- Constructor fixture table with record ID, policy class, expected action,
  constructed label, source evidence, contributing candidate records, and
  pass/fail result.
- Standard50 answer-option coverage before and after construction.
- G11 exact-miss challenge answer-option coverage before and after construction.
- Counts for exact constructed option, category-equivalent only,
  no-construction negative control, deferred duration, and inventory gap.
- Separate flags for temporal-slot construction, event-count aggregation,
  duration-policy deferral, cluster-policy deferral, and special-label deferral.
- No-op regression report for all rows where exact options already exist.
- Scorer-mode caveat stating that construction coverage is not paper monthly,
  Purist, Pragmatic, or canonical monthly performance.

## Stop Rules

Stop before selector work if the constructor mutates raw candidates, changes the
scorer inputs for existing closed-option rows, or emits constructed options for
negative-control rows.

Stop before full validation if the standard50 exact-option coverage does not
increase by at least three rows, or if any reported gain depends on scorer
repair, prediction repair, tolerance, range credit, or using `reference[0]` as
gold.

Stop before duration work unless a separate preregistration defines a
seizure-free duration constructor and fixture policy.

## Taxonomy

- Dataset: `gan_2026`
- Schema complexity: `gan_s0`
- Clinical task family: `frequency`
- Decomposition stage: label construction and aggregation
- Program architecture: deterministic aggregation constructor
- Hybrid balance class: `H1_post_deterministic`, `eval_only_diagnostic`
- Interleaving positions: `post`, `eval_only`
- Existing primitive IDs:
  `gan.frequency.temporal_candidates.v1`,
  `gan.frequency.label_policy_bridge.v1`,
  `gan.frequency.evidence_guard.v1`
- Candidate primitive ID for a later registry review, not registered by this
  document:
  `gan.frequency.aggregation_constructor.v1`
- Varied factor: `answer_option_construction`
- Comparison group: pre-constructor current deterministic candidate surface
- Decision scope: mechanism preregistration; implementation and promotion remain
  separate cards.

## Source Artifacts

- `docs/current_research_program.md`
- `docs/component_ceiling_registry.md`
- `docs/planning/kanban_plan.md`
- `docs/experiments/gan/README.md`
- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md`
- `docs/taxonomy/taxonomy_primitive_catalog.md`
- `docs/experiments/gan/gan_s0_g11_candidate_inventory_challenge_set_pass_20260529.md`
- `docs/experiments/gan/gan_s0_g14_temporal_anchoring_report_20260529.md`
- `docs/experiments/gan/gan_s0_g16_aggregation_policy_20260529.md`
- `docs/experiments/gan/gan_s0_g19_post_g16_error_attribution_audit_20260529.md`
- `docs/experiments/gan/gan_s0_g19_post_g16_error_attribution_audit_20260529.json`

## Caveats

This is a preregistration only. It makes no new performance claim, performs no
model calls, and changes no implementation, scorer, loader, split, bridge,
candidate-builder, target-selection, or prediction-repair semantics.

External Gan benchmark claims remain blocked without Real(300)/Real(150) access
or an explicitly synthetic-only comparison protocol.
