# Synthesis And Paper Evidence Map

Status: active guidance
Last updated: 2026-05-28

This folder contains multiple generations of synthesis. Most are historical
evidence, not active steering. Use this map before citing any synthesis doc.

## Current Paper/Claim Surfaces

| Doc | Status | Use |
| --- | --- | --- |
| `paper_result_table_pack_20260525.md` | paper evidence | Current manuscript table pack, but Gan benchmark-comparison tables still need `gan2026_paper_reproduction` rescoring. |
| `paper_claims_caveats_20260525.md` | paper evidence | Supported and unsupported claim language. |
| `test_holdout_evaluation_report_20260527.md` | current synthesis / active risk | One-shot holdout report; use as transfer warning, not tuning feedback. |
| `l1_2_s5_local_vs_closed_comparison_20260525.md` | paper evidence | Local-vs-closed ExECT S5 comparison. |

## Superseded Or Historical Surfaces

| Doc family | Status | Reason |
| --- | --- | --- |
| `../../archive/experiments/synthesis/pre_component_pivot/experiment_registry_matrix_20260520.md` | superseded | Generated from an older registry export. Do not use as current navigation. |
| `../../archive/experiments/synthesis/pre_component_pivot/experiments_methods_results_20260520.md` and `../../archive/experiments/synthesis/pre_component_pivot/experiments_narrative_report_20260520.md` | archive | Early synthesis before May 24-28 refocus. |
| `../../archive/experiments/synthesis/pre_component_pivot/paper_*_20260524.md` | archive / paper evidence | Preserved for provenance; superseded by May 25 table pack and May 28 decomposition pivot unless explicitly cited. |
| model-suite inspection docs | diagnostic only | Model-profile evidence, not operational defaults unless a current index promotes the row. |
| `experimentation_retrospective_report.md` | superseded synthesis | Useful historical bridge to the pivot, but R11-R15 and the decomposition docs now supersede its next-pull guidance. |

## Registry Status

`program_variant_registry.md` is the C4 current-authority/loadable-replay status
view for program variants and live experiment configs.

`experiment_registry_matrix_20260520.md` was refreshed by X3 after the May 28
component pivot, R11-R15 Gan decisions, X1 component-ceiling backfill, C4
authority classes, and C10 provenance cleanup. It remains a registry-derived
methods/provenance view, not current steering authority by itself.

`experiment_registry.json` remains useful provenance. The old research atlas
export has been deleted. Use `component_ceiling_registry.md` and
`program_variant_registry.md` before treating matrix rows as current pulls,
baselines, rejected arms, blocked claims, or diagnostic-only evidence.

## New Synthesis Rule

Any new synthesis must say what it supersedes and must link to
`../../component_ceiling_registry.md` if it changes active component status.
