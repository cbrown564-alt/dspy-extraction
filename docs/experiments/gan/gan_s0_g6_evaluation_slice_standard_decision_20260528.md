# Gan S0 G6 Evaluation Slice Standard Decision

Status: active guidance / evaluation-surface protocol
Date: 2026-05-28
Related card: G6 - Gan Evaluation Slice Standard And Challenge Sets

## Research Question

What evaluation surface should new Gan S0 selector and adjudicator mechanisms use before spending
model calls on another small-slice variant?

## Decision

Use both a locked 50-record standard mechanism slice and named challenge sets, with separate decision
scopes.

- `gan_s0_g6_standard50_v1` is the default no-holdout mechanism-comparison slice for new Gan S0
  selector, adjudicator, label-construction, unknown/no-reference, cluster, and temporal-anchoring
  variants.
- The previous G2/G4 enriched 25-record slice is retained only as `gan_s0_g6_traceability_smoke_25`.
  It can check compatibility, trace fields, and fast failure modes, but it cannot promote a new arm.
- Named challenge sets are diagnostic overlays. They can support targeted mechanism decisions only
  when the varied factor matches the challenge-set scope.
- Full synthetic validation remains required before promoting a new Gan S0 operational baseline.
  Real(300), Real(150), or a declared synthetic-only protocol remains required before external
  benchmark claims.

No model calls, scorer changes, loader changes, split changes, bridge changes, prompt edits, or
prediction repairs were made for this decision.

## Source Artifacts

- `docs/planning/kanban_plan.md`
- `docs/current_research_program.md`
- `docs/component_ceiling_registry.md`
- `docs/experiments/gan/README.md`
- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md`
- `docs/experiments/gan/gan_s0_candidate_inventory_coverage_report_20260528.json`
- `docs/experiments/gan/gan_s0_target_label_split_g2_report_20260528.json`
- `docs/experiments/gan/gan_s0_g2_model_arm_comparison_20260528.json`
- `docs/experiments/gan/gan_s0_g3_policy_probe_report.json`
- `docs/experiments/gan/gan_s0_g4_explicit_reason_code_adjudicator_report_20260528.json`
- `docs/experiments/gan/gan_s0_g5_paper_scorer_rescore_pack_20260528.md`
- `docs/experiments/gan/gan_s0_g5_scorer_mode_forensics_for_g4_20260528.md`

## Dataset And Scorer Policy

- Dataset/split: Gan 2026 synthetic validation split, `gan_2026_fixed_v1:validation`.
- Gold source: `check__Seizure Frequency Number.seizure_frequency_number[0]`.
- Reference policy: `reference[0]` is a secondary cross-check and difficulty signal, not gold.
- Benchmark-facing scorer: `gan2026_paper_reproduction`, with repair, range, and tolerance options
  reported whenever enabled.
- Diagnostic project scorer: `gan_frequency_deterministic_v1`, preserving the clinical distinction
  between `unknown` and `no seizure frequency reference`.
- Challenge tags come from G1/G2 no-model strata and audited label families. They do not change
  scorer semantics.

## Denominator Effects

| Surface | Records | One-record delta | Two-record delta | Decision scope |
| --- | ---: | ---: | ---: | --- |
| `gan_s0_g6_traceability_smoke_25` | 25 | 4.0pp | 8.0pp | smoke only; no promotion |
| `gan_s0_g6_standard50_v1` | 50 | 2.0pp | 4.0pp | default mechanism comparison |
| Full validation | 299 | 0.3pp | 0.7pp | promotion and baseline replacement |

The G2/G4 slice is too denominator-sensitive for further one- or two-record arm claims. A 50-record
surface still is not a benchmark, but it halves the slice-level point swing and forces broader
coverage across special labels, clusters, unknown/no-reference cases, and temporal conflicts.

## Standard 50 Selection Protocol

The standard 50 was selected without looking at new model outputs. Selection used the validation
records from the G1 candidate-inventory artifact, preserved deterministic validation-split order
within each family, and applied fixed family quotas:

| Family | Target | Actual |
| --- | ---: | ---: |
| `quantified_rate` | 25 | 25 |
| `seizure_free` | 8 | 8 |
| `unknown` | 6 | 6 |
| `cluster` | 5 | 5 |
| `no_reference` | 3 | 3 |
| `vague_or_multiple_rate` | 2 | 2 |
| `unknown_cluster` | 1 | 1 |

This is a challenge-balanced mechanism slice, not an unbiased estimate of validation performance.
It intentionally gives rare benchmark-policy families enough support to detect regressions.

Hard-stratum coverage in `gan_s0_g6_standard50_v1`:

| Stratum | Records |
| --- | ---: |
| `cluster` | 24 |
| `gold_evidence_multispan` | 2 |
| `label_reference_disagreement` | 10 |
| `multi_highest` | 14 |
| `no_reference` | 3 |
| `seizure_free_conflict` | 21 |
| `unknown_with_events` | 6 |
| `vague_frequency` | 10 |

Challenge-tag coverage in `gan_s0_g6_standard50_v1`:

| Challenge tag | Records |
| --- | ---: |
| `candidate_coverage` | 4 |
| `cluster` | 24 |
| `seizure_free_vs_quantified` | 21 |
| `target_selection` | 43 |
| `temporal_anchoring` | 15 |
| `unknown_no_reference` | 10 |
| `vague_frequency` | 10 |

## Standard 50 Record Ledger

| Record | Gold label | Family | Strata | Challenge tags |
| --- | --- | --- | --- | --- |
| `gan_14485` | `2 per 3 month` | `quantified_rate` | `multi_highest`, `seizure_free_conflict`; `row_ok=false` | `target_selection`, `seizure_free_vs_quantified`, `temporal_anchoring` |
| `gan_6532` | `unknown, multiple per cluster` | `unknown_cluster` | `cluster`, `label_reference_disagreement`, `vague_frequency`; `hard_case` | `target_selection`, `unknown_no_reference`, `cluster`, `vague_frequency` |
| `gan_10434` | `multiple cluster per week, 2 to 3 per cluster` | `cluster` | `cluster`, `label_reference_disagreement`, `seizure_free_conflict`, `vague_frequency`; `hard_case` | `target_selection`, `seizure_free_vs_quantified`, `cluster`, `vague_frequency` |
| `gan_4956` | `seizure free for 7 month` | `seizure_free` | `cluster`, `label_reference_disagreement`, `seizure_free_conflict`; `hard_case` | `target_selection`, `seizure_free_vs_quantified`, `cluster` |
| `gan_13123` | `1 per year` | `quantified_rate` | `multi_highest`, `seizure_free_conflict` | `target_selection`, `seizure_free_vs_quantified`, `temporal_anchoring` |
| `gan_4702` | `multiple per day` | `vague_or_multiple_rate` | `cluster`, `multi_highest`, `vague_frequency` | `target_selection`, `cluster`, `temporal_anchoring`, `vague_frequency` |
| `gan_10052` | `4 cluster per 3 month, multiple per cluster` | `cluster` | `cluster`, `vague_frequency` | `target_selection`, `cluster`, `vague_frequency` |
| `gan_2609` | `1 per day` | `quantified_rate` | `cluster`, `multi_highest` | `target_selection`, `cluster`, `temporal_anchoring` |
| `gan_1794` | `8 per 2 month` | `quantified_rate` | `multi_highest` | `target_selection`, `temporal_anchoring` |
| `gan_15306` | `2 to 3 per 15 month` | `quantified_rate` | `seizure_free_conflict` | `target_selection`, `seizure_free_vs_quantified` |
| `gan_7894` | `seizure free for multiple year` | `seizure_free` | `label_reference_disagreement`, `seizure_free_conflict`, `vague_frequency`; `hard_case` | `target_selection`, `seizure_free_vs_quantified`, `vague_frequency` |
| `gan_3246` | `2 cluster per month, 4 per cluster` | `cluster` | `cluster` | `target_selection`, `cluster` |
| `gan_4113` | `1 per 1 to 2 day` | `quantified_rate` | `cluster` | `target_selection`, `cluster` |
| `gan_14881` | `1 per month` | `quantified_rate` | `seizure_free_conflict` | `target_selection`, `seizure_free_vs_quantified` |
| `gan_536` | `1 per 2 day` | `quantified_rate` | `none` | `target_selection` |
| `gan_4709` | `multiple per day` | `vague_or_multiple_rate` | `cluster`, `vague_frequency` | `target_selection`, `cluster`, `vague_frequency` |
| `gan_9566` | `unknown` | `unknown` | `seizure_free_conflict`, `unknown_with_events` | `target_selection`, `seizure_free_vs_quantified`, `unknown_no_reference` |
| `gan_12679` | `1 per day` | `quantified_rate` | `cluster`, `multi_highest`, `seizure_free_conflict` | `target_selection`, `seizure_free_vs_quantified`, `cluster`, `temporal_anchoring` |
| `gan_1584` | `11 per month` | `quantified_rate` | `cluster`, `multi_highest` | `target_selection`, `cluster`, `temporal_anchoring` |
| `gan_15997` | `10 per 3 month` | `quantified_rate` | `cluster`, `seizure_free_conflict`; `exact_miss` | `target_selection`, `seizure_free_vs_quantified`, `candidate_coverage`, `cluster` |
| `gan_17287` | `1 per 1 to 2 day` | `quantified_rate` | `multi_highest`, `seizure_free_conflict` | `target_selection`, `seizure_free_vs_quantified`, `temporal_anchoring` |
| `gan_16251` | `14 per 4 month` | `quantified_rate` | `cluster` | `target_selection`, `cluster` |
| `gan_16772` | `9 per 5 month` | `quantified_rate` | `gold_evidence_multispan`; `exact_miss` | `target_selection`, `candidate_coverage`, `temporal_anchoring` |
| `gan_16825` | `10 per 6 month` | `quantified_rate` | `cluster`, `gold_evidence_multispan`, `multi_highest`, `seizure_free_conflict`; `exact_miss` | `target_selection`, `seizure_free_vs_quantified`, `candidate_coverage`, `cluster`, `temporal_anchoring` |
| `gan_12950` | `7 per 3 month` | `quantified_rate` | `multi_highest` | `target_selection`, `temporal_anchoring` |
| `gan_10047` | `2 cluster per 3 month, multiple per cluster` | `cluster` | `cluster`, `vague_frequency` | `cluster`, `vague_frequency` |
| `gan_12810` | `5 per 2 month` | `quantified_rate` | `none` | `target_selection` |
| `gan_10398` | `1 cluster per week, 2 per cluster` | `cluster` | `cluster` | `target_selection`, `cluster` |
| `gan_16041` | `9 per 3 month` | `quantified_rate` | `none` | `target_selection` |
| `gan_714` | `2 per day` | `quantified_rate` | `cluster`, `multi_highest` | `target_selection`, `cluster`, `temporal_anchoring` |
| `gan_12465` | `1 per day` | `quantified_rate` | `multi_highest` | `target_selection`, `temporal_anchoring` |
| `gan_4011` | `1 per month` | `quantified_rate` | `seizure_free_conflict` | `target_selection`, `seizure_free_vs_quantified` |
| `gan_804` | `1 per month` | `quantified_rate` | `cluster`, `multi_highest`, `seizure_free_conflict` | `target_selection`, `seizure_free_vs_quantified`, `cluster`, `temporal_anchoring` |
| `gan_22` | `3 per day` | `quantified_rate` | `cluster`, `multi_highest` | `target_selection`, `cluster`, `temporal_anchoring` |
| `gan_16335` | `7 per 3 month` | `quantified_rate` | `none`; `exact_miss` | `target_selection`, `candidate_coverage` |
| `gan_3867` | `3 per day` | `quantified_rate` | `none` | `target_selection` |
| `gan_13574` | `seizure free for multiple year` | `seizure_free` | `cluster`, `label_reference_disagreement`, `seizure_free_conflict`, `vague_frequency`; `hard_case` | `target_selection`, `seizure_free_vs_quantified`, `cluster`, `vague_frequency` |
| `gan_5974` | `unknown` | `unknown` | `seizure_free_conflict`, `unknown_with_events` | `target_selection`, `seizure_free_vs_quantified`, `unknown_no_reference` |
| `gan_6607` | `unknown` | `unknown` | `cluster`, `unknown_with_events` | `unknown_no_reference`, `cluster` |
| `gan_8564` | `seizure free for 6 month` | `seizure_free` | `label_reference_disagreement`, `seizure_free_conflict`; `hard_case` | `target_selection`, `seizure_free_vs_quantified` |
| `gan_6387` | `unknown` | `unknown` | `unknown_with_events` | `unknown_no_reference` |
| `gan_8264` | `seizure free for 4 month` | `seizure_free` | `label_reference_disagreement`, `seizure_free_conflict`; `hard_case` | `target_selection`, `seizure_free_vs_quantified` |
| `gan_14002` | `unknown` | `unknown` | `unknown_with_events` | `unknown_no_reference` |
| `gan_11380` | `unknown` | `unknown` | `cluster`, `unknown_with_events` | `target_selection`, `unknown_no_reference`, `cluster` |
| `gan_11408` | `no seizure frequency reference` | `no_reference` | `no_reference`; `row_ok=false` | `unknown_no_reference` |
| `gan_11841` | `no seizure frequency reference` | `no_reference` | `no_reference`; `row_ok=false` | `unknown_no_reference` |
| `gan_7818` | `seizure free for 2 year` | `seizure_free` | `label_reference_disagreement`, `seizure_free_conflict`; `hard_case` | `target_selection`, `seizure_free_vs_quantified` |
| `gan_13598` | `seizure free for multiple year` | `seizure_free` | `cluster`, `label_reference_disagreement`, `seizure_free_conflict`, `vague_frequency`; `hard_case` | `target_selection`, `seizure_free_vs_quantified`, `cluster`, `vague_frequency` |
| `gan_13595` | `seizure free for multiple year` | `seizure_free` | `cluster`, `label_reference_disagreement`, `seizure_free_conflict`, `vague_frequency`; `hard_case` | `target_selection`, `seizure_free_vs_quantified`, `cluster`, `vague_frequency` |
| `gan_11874` | `no seizure frequency reference` | `no_reference` | `no_reference`; `row_ok=false` | `unknown_no_reference` |

## Named Challenge Sets

| Challenge set | Records | Intended scope |
| --- | ---: | --- |
| `gan_s0_g6_traceability_smoke_25` | 25 | Legacy G2/G4 compatibility and traceability smoke checks only. |
| `gan_s0_g6_target_selection_standard` | 43 | Current target choice across multiple candidates, conflicts, and high-candidate-count notes. |
| `gan_s0_g6_seizure_free_vs_quantified` | 21 | Seizure-free duration versus current quantified-frequency policy. |
| `gan_s0_g6_unknown_no_reference_policy` | 10 | `unknown`, `no seizure frequency reference`, and unknown-cluster boundary behavior. |
| `gan_s0_g6_candidate_coverage_exact_miss` | 21 | Candidate-inventory exact-label misses from G1; use before changing candidate builders. |
| `gan_s0_g6_cluster_policy` | 24 | Cluster and per-cluster construction, spacing, and policy decisions. |
| `gan_s0_g6_temporal_anchoring` | 15 | Multi/highest and multi-span temporal-denominator selection. |

### Challenge Set Record IDs

`gan_s0_g6_traceability_smoke_25`:
`gan_13058`, `gan_13123`, `gan_13149`, `gan_13190`, `gan_13574`, `gan_13598`,
`gan_14214`, `gan_14250`, `gan_14485`, `gan_14562`, `gan_14628`, `gan_14689`,
`gan_14792`, `gan_14821`, `gan_14881`, `gan_14965`, `gan_14973`, `gan_15127`,
`gan_15168`, `gan_15193`, `gan_15302`, `gan_15442`, `gan_16529`, `gan_16645`,
`gan_16750`.

`gan_s0_g6_target_selection_standard`:
`gan_14485`, `gan_6532`, `gan_10434`, `gan_4956`, `gan_13123`, `gan_4702`,
`gan_10052`, `gan_2609`, `gan_1794`, `gan_15306`, `gan_7894`, `gan_3246`,
`gan_4113`, `gan_14881`, `gan_536`, `gan_4709`, `gan_9566`, `gan_12679`,
`gan_1584`, `gan_15997`, `gan_17287`, `gan_16251`, `gan_16772`, `gan_16825`,
`gan_12950`, `gan_12810`, `gan_10398`, `gan_16041`, `gan_714`, `gan_12465`,
`gan_4011`, `gan_804`, `gan_22`, `gan_16335`, `gan_3867`, `gan_13574`,
`gan_5974`, `gan_8564`, `gan_8264`, `gan_11380`, `gan_7818`, `gan_13598`,
`gan_13595`.

`gan_s0_g6_seizure_free_vs_quantified`:
`gan_14485`, `gan_10434`, `gan_4956`, `gan_13123`, `gan_15306`, `gan_7894`,
`gan_14881`, `gan_9566`, `gan_12679`, `gan_15997`, `gan_17287`, `gan_16825`,
`gan_4011`, `gan_804`, `gan_13574`, `gan_5974`, `gan_8564`, `gan_8264`,
`gan_7818`, `gan_13598`, `gan_13595`.

`gan_s0_g6_unknown_no_reference_policy`:
`gan_6532`, `gan_9566`, `gan_5974`, `gan_6607`, `gan_6387`, `gan_14002`,
`gan_11380`, `gan_11408`, `gan_11841`, `gan_11874`.

`gan_s0_g6_candidate_coverage_exact_miss`:
`gan_15997`, `gan_16772`, `gan_16825`, `gan_16335`, `gan_10583`, `gan_1463`,
`gan_9424`, `gan_6094`, `gan_1486`, `gan_7431`, `gan_16883`, `gan_4996`,
`gan_3355`, `gan_15129`, `gan_9063`, `gan_13290`, `gan_6509`, `gan_4378`,
`gan_6296`, `gan_13019`, `gan_9526`.

`gan_s0_g6_cluster_policy`:
`gan_6532`, `gan_10434`, `gan_4956`, `gan_4702`, `gan_10052`, `gan_2609`,
`gan_3246`, `gan_4113`, `gan_4709`, `gan_12679`, `gan_1584`, `gan_15997`,
`gan_16251`, `gan_16825`, `gan_10047`, `gan_10398`, `gan_714`, `gan_804`,
`gan_22`, `gan_13574`, `gan_6607`, `gan_11380`, `gan_13598`, `gan_13595`.

`gan_s0_g6_temporal_anchoring`:
`gan_14485`, `gan_13123`, `gan_4702`, `gan_2609`, `gan_1794`, `gan_12679`,
`gan_1584`, `gan_17287`, `gan_16772`, `gan_16825`, `gan_12950`, `gan_714`,
`gan_12465`, `gan_804`, `gan_22`.

## Stop Rules

- A new Gan selector or adjudicator may run on the 25-record smoke slice first, but promotion requires
  the 50-record standard slice and then full validation.
- A slice-level mechanism claim on `gan_s0_g6_standard50_v1` requires at least a two-record monthly
  lift, no worse paper-reproduction monthly score, and no regression on the challenge tag that
  motivated the mechanism. One-record improvements are treated as directional only.
- A challenge-set-only run can reject a targeted arm or justify a fuller comparison, but it cannot
  promote a new default.
- Candidate-builder changes must report `gan_s0_g6_candidate_coverage_exact_miss` before any
  adjudicator claim.
- Unknown/no-reference, seizure-free, and cluster changes must report both `gan2026_paper_reproduction`
  and `gan_frequency_deterministic_v1`.
- Holdout or real-note metrics remain residual-analysis triggers only unless a separate protocol
  explicitly authorizes external reporting.

## Interpretation

G6 changes the evaluation surface, not the model. The main scientific effect is to prevent more Gan
S0 work from making claims on a 25-record slice where a single label moves the headline by 4.0pp.

The 50-record standard is deliberately more policy-rich than a random validation sample: it contains
rare special labels, cluster forms, no-reference cases, and temporal conflicts. That makes it useful
for deciding whether a mechanism deserves full-validation cost. It should not be described as a new
benchmark or as an unbiased validation estimate.

The next Gan selector card should name which component it varies, use the standard 50 or the relevant
challenge set, preserve scorer modes, and keep target selection, label construction, evidence, and
special-label policy separable in artifacts.

