# Gan S0 G7 Special-Class Target Selector Preregistration

Status: mechanism open / preregistered selector protocol
Date: 2026-05-28
Related card: G7 - Gan G6 Special-Class Target Selector Preregistration

## Research Question

Can a Gan S0 target selector preserve benchmark-facing special-class semantics
for seizure-free duration, current quantified frequency, unknown frequency, and
no seizure-frequency reference while retaining the traceability guarantees that
G4 demonstrated?

## Hypothesis

A selector that first classifies the target semantic class, then selects an
indexed candidate within that class, will reduce the G4 seizure-free-over-
quantified failures without hiding label-construction or scorer-discordance
signals inside a final frequency label.

## Varied Component

The varied component is scope and benchmark target selection.

This protocol does not change candidate inventory, temporal anchoring, canonical
label construction, scorer semantics, dataset loading, split definitions,
benchmark bridge behavior, evidence diagnostics, or prediction repair.

## Motivation From Prior Evidence

G4 proved that an explicit adjudicator can preserve selected-candidate
references and label-construction inputs, but the tested arm scored only 80.0%
monthly/pragmatic on the old enriched 25-record slice. All five misses were
target-selection failures where seizure-free-duration candidates won over
gold-compatible quantified candidates.

G5 scorer-mode forensics sharpened the target. D1 v1.2b's paper-scorer loss is
concentrated in seizure-free gold labels predicted as
`no seizure frequency reference`. That is a benchmark-facing special-class
semantic error, not a deterministic arithmetic or label-construction error.

G6 fixes the evaluation surface for this follow-up: the old 25-record slice is
smoke-only, `gan_s0_g6_standard50_v1` is the default mechanism-comparison
surface, and named challenge sets can only support claims within their declared
scope.

## Method

- Dataset: Gan 2026 synthetic.
- Split: `gan_2026_fixed_v1:validation`.
- Gold source: `check__Seizure Frequency Number.seizure_frequency_number[0]`.
- Reference policy: `reference[0]` is a secondary cross-check and difficulty
  signal, not gold.
- Model/provider: GPT-4.1-mini / OpenAI for the first model-backed arm unless a
  later config explicitly declares a different model track.
- Mechanism baseline: D1 v1.2b schema-guard date/event payload.
- Synthetic paper baseline: builder-gap v1 GPT remains the paper-default
  baseline and is not replaced by this slice protocol.
- Benchmark-facing scorer: `gan2026_paper_reproduction`, with repair, range,
  and tolerance options disabled unless a later report explicitly changes and
  labels them.
- Diagnostic scorer: `gan_frequency_deterministic_v1`.
- Primary evaluation surface: `gan_s0_g6_standard50_v1`.
- Smoke surface: `gan_s0_g6_traceability_smoke_25`, traceability and fast
  compatibility only.
- Challenge overlays:
  `gan_s0_g6_seizure_free_vs_quantified`,
  `gan_s0_g6_unknown_no_reference_policy`,
  `gan_s0_g6_target_selection_standard`, and, if cluster labels are touched,
  `gan_s0_g6_cluster_policy`.

## Planned Selector Shape

The model should emit structured adjudication metadata before any final label is
accepted:

1. Target semantic class:
   `frequency_present_quantified`, `seizure_free_duration`,
   `seizures_referenced_frequency_unclear`,
   `no_seizure_frequency_reference`, `cluster_spacing_unknown`, or
   `malformed_or_unsupported_surface`.
2. Selected candidate reference and candidate index.
3. Selected candidate evidence text.
4. Target-selection reason code.
5. Label-construction inputs: numerator, denominator, unit, cluster count,
   seizures per cluster, special-label flag, and source candidate.
6. Final benchmark-facing label.
7. Scorer-discordance flags for paper-only, canonical-only, both-correct, and
   both-wrong monthly correctness.

The final label must remain downstream of target selection and construction
metadata. A final label alone is not sufficient evidence that the arm selected
the right target.

## Fixed Controls

- No changes to Gan loader behavior.
- No changes to `gan_2026_fixed_v1:validation` split membership.
- No changes to the primary gold field.
- No use of `reference[0]` as gold.
- No scorer repairs, prediction repairs, tolerance options, or range-credit
  options unless explicitly reported as a separate scorer view.
- No deterministic rewrite between `seizure free for ...`, `unknown`, and
  `no seizure frequency reference`.
- No candidate-builder changes before separately reporting
  `gan_s0_g6_candidate_coverage_exact_miss`.
- No claim from the old 25-record slice beyond traceability smoke.

## Required Diagnostics

- Paper monthly, Purist, and Pragmatic metrics.
- Canonical monthly, Purist, and Pragmatic metrics as diagnostic sensitivity.
- Record-level scorer-discordance table.
- Confusion counts across target semantic classes.
- Separate error classes for candidate coverage, target selection, label
  construction, unknown/no-reference policy, seizure-free policy, cluster
  policy, temporal anchoring, evidence support, and schema validity.
- Trace completeness counts for selected-candidate reference, candidate index,
  selected evidence, reason code, construction inputs, final label, and scorer
  flags.
- Pairwise deltas against the G4 explicit reason-code adjudicator and the G2
  candidate-constrained / seeded-selector slice baselines where records overlap.

## Decision Rules

- A smoke run on `gan_s0_g6_traceability_smoke_25` may only gate compatibility.
  It cannot promote or reject the mechanism class.
- A standard-50 arm must show at least a two-record monthly lift over the
  relevant G6-aligned comparator, no worse paper-reproduction monthly score, and
  no regression on the challenge tag that motivated the mechanism.
- A one-record standard-50 improvement is directional only.
- A challenge-set-only result may reject the tested arm or justify a broader
  comparison, but it cannot promote a default selector.
- Full synthetic validation is required before replacing any operational Gan S0
  baseline.
- Real(300), Real(150), or a declared synthetic-only protocol remains required
  before any external Gan benchmark claim.

## Stop Rules

Stop after smoke and do not run the standard 50 if trace fields are incomplete,
selected-candidate references are missing, final labels cannot be tied back to
construction inputs, or scorer views are not reported separately.

Stop after the standard 50 and do not full-validate if the arm regresses on
`gan2026_paper_reproduction`, collapses seizure-free duration into no-reference
without explicit support, or improves aggregate monthly accuracy while
worsening the targeted special-class challenge set.

## Taxonomy

- Dataset: `gan_2026`
- Schema complexity: `gan_s0`
- Clinical task family: `frequency`
- Program architecture: `special_class_target_selector`
- Hybrid balance class: `H2_pre_deterministic`, `L1_llm_constrained`,
  `H4_deterministic_first_llm_adjudicates`, `H1_post_deterministic`
- Interleaving positions: `pre`, `during`, `post`, `eval_only`
- Primitive IDs:
  `gan.frequency.temporal_candidates.v1`,
  `gan.frequency.label_policy_bridge.v1`,
  `gan.frequency.evidence_guard.v1`
- Varied factor: `target_selection_policy`
- Comparison group: `gan_s0_g7_special_class_target_selector_gpt4_standard50_v1`
- Decision scope: `arm` for a first standard-50 run; mechanism closure would
  require a later review across more than one arm or position.

## Source Artifacts

- `docs/current_research_program.md`
- `docs/component_ceiling_registry.md`
- `docs/planning/kanban_plan.md`
- `docs/experiments/gan/README.md`
- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md`
- `docs/taxonomy/taxonomy_primitive_catalog.md`
- `docs/experiments/gan/gan_s0_g4_explicit_reason_code_adjudicator_report_20260528.md`
- `docs/experiments/gan/gan_s0_g5_paper_scorer_rescore_pack_20260528.md`
- `docs/experiments/gan/gan_s0_g5_scorer_mode_forensics_for_g4_20260528.md`
- `docs/experiments/gan/gan_s0_g6_evaluation_slice_standard_decision_20260528.md`

## Caveats

This is a preregistration only. It makes no new performance claim, performs no
model calls, and changes no implementation or scorer semantics.
