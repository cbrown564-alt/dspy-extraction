# ExECT Experiment Map

Status: active guidance
Last updated: 2026-05-28

## Current Question

ExECT is now a component-ceiling study. The schema ladder remains useful, but it
is no longer the main decomposition.

The current program is:

1. define benchmark contract and gold policy per family;
2. expose document structure and family spans;
3. build mention/event/candidate inventories;
4. bridge candidates into benchmark labels;
5. optimize within-family adjudication;
6. test pairwise interactions;
7. rebuild stacked schemas only after isolated ceilings exist.

## Current Baselines

| Surface | Status | Evidence |
| --- | --- | --- |
| Clean S1-S4 ladder | diagnostic baseline | Complexity stress test; not proof of component ceilings. |
| S5 v2b core stack | promoted baseline | GPT 85.8% micro / 73.9% frequency F1; Qwen 85.4% / 71.4% validation. |
| Holdout report | active risk | S1 and S5 frequency drops require residual analysis before new claims. |
| ExECT Table 1 reproduction | blocked | Requires CUI-aware all-family scorer. |

## Read First

- `exect_task_deep_review_20260528.md` - current decomposition doctrine.
- `../synthesis/test_holdout_evaluation_report_20260527.md` - holdout warning.
- `../synthesis/paper_result_table_pack_20260525.md` - current paper table pack.
- `../../datasets/exect/exect_gold_label_audit.md` - gold-label policy.
- `../../policies/deterministic_scorer_semantics.md` - implemented field-family scorers.
- `../../policies/published_benchmark_metrics.md` - external benchmark caveats.

## Active Next Work

1. Frequency event/rate payload no-model audit.
2. S1 raw extraction versus bridge versus prompt-policy causal split.
3. Medication current-Rx and lifecycle payload.
4. Family-span/list payload.
5. Component ceiling reports before any new broad stack.

## Do Not Overread

- S1 validation success does not prove diagnosis or seizure-type ceilings.
- S5 v2b is an operational stacked baseline, not optimal family decomposition.
- Medication temporal guard failures are rejected arms, not proof that lifecycle
  decomposition is impossible.
- Per-family parallel S5 rejection is a rejected implementation, not rejection
  of family-first work.

## Filing Guidance

New ExECT docs should name the family or pairwise interaction under study,
report the scorer, split, model, run IDs, component substrate, and whether the
result is an isolated ceiling, stacked result, diagnostic, rejected arm, or
blocked benchmark claim.
