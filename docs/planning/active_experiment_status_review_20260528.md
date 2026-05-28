# Active Experiment Status Review

Status: active guidance
Date: 2026-05-28
Kanban card: C4 - Active Experiment Status Review

## Context

C3 introduced a typed program variant registry, but the first report still made
it too easy to read "59 loadable experiment configs" as "59 current
experiments." C4 resolves that authority gap. It classifies registry rows and
live config rows by current research use, while preserving replayability for old
runs.

Source artifacts reviewed:

- `docs/current_research_program.md`
- `docs/component_ceiling_registry.md`
- `docs/planning/kanban_plan.md`
- `docs/planning/program_surface_inventory_deletion_map_20260528.md`
- `docs/experiments/synthesis/experiment_registry.json`
- `docs/experiments/gan/gan_s0_r11_temporal_date_stage_decision_20260528.md`
- `docs/experiments/gan/gan_s0_r12_clines_entity_first_pipeline_gate_decision_20260528.md`
- `docs/experiments/gan/gan_s0_r13_self_consistency_variance_probe_decision_20260528.md`
- `docs/experiments/gan/gan_s0_r15_d1_guardrail_ablation_decision_20260528.md`
- `configs/experiments/**/*.json`
- recent local Gan R11-R15 run directories under `runs/`

## Work Completed

- Expanded `ProgramVariantStatusValue` so registry rows can distinguish
  `replay_provenance` and `historical_arm` from current-authority baselines and
  `rejected_arm` rows.
- Added an authority class derived from status:
  `current_authority`, `loadable_replay`, or `blocked`.
- Tightened config matching for generated reports: a config now matches registry
  rows by dataset, schema level, program variant, scorer, exact prompt version,
  implementation variant, and optional taxonomy filters.
- Added a generated config inventory in
  `docs/experiments/synthesis/program_variant_registry.md`; every live config is
  resolved to exactly one variant row and one explicit status.
- Reworded the generated report so "Loadable Config Count" is explicitly a
  replay/provenance count, not an active experiment count.

## Classification Summary

Typed registry rows: 76.

| Status | Variant rows |
| --- | ---: |
| `historical_arm` | 45 |
| `rejected_arm` | 17 |
| `replay_provenance` | 6 |
| `diagnostic_baseline` | 5 |
| `promoted_baseline` | 1 |
| `mechanism_baseline` | 1 |
| `operational_baseline` | 1 |

Live config rows: 59.

| Status | Config rows |
| --- | ---: |
| `diagnostic_baseline` | 21 |
| `replay_provenance` | 11 |
| `rejected_arm` | 10 |
| `operational_baseline` | 6 |
| `promoted_baseline` | 6 |
| `historical_arm` | 4 |
| `mechanism_baseline` | 1 |

Authority classes for live configs:

| Authority class | Config rows |
| --- | ---: |
| `current_authority` | 34 |
| `loadable_replay` | 25 |

Current-authority config rows are not a queue of experiments to rerun. They are
configs attached to rows that current docs still cite as baselines, diagnostic
comparators, or one-shot holdout/residual evidence.

## Status Decisions

- Gan builder-gap v1 remains `promoted_baseline`: synthetic paper-default
  surface, with direct paper-comparison tables still requiring
  `gan2026_paper_reproduction`.
- Gan D1 v1.2b schema-guard-only is `mechanism_baseline`: the best decomposed
  date/event payload baseline after R15.
- Gan D0 and D1 v1 rows are `replay_provenance`: useful R11 ablation controls,
  not current targets.
- Gan D1 v1.2 guardrail and D2 LLM-date arms are `rejected_arm`; broad
  arithmetic/relative-anchor guardrails and LLM specialist date events should
  not be repeated without a new preregistered hypothesis.
- Gan entity-first C1 and self-consistency remain `rejected_arm`; entity-first C0
  is `replay_provenance` as a rejected-grid control.
- ExECT clean ladder S1-S4 rows are `diagnostic_baseline`: current complexity
  stress-test evidence, not component ceilings.
- ExECT S5 v2b is `operational_baseline`: current stacked baseline, not an
  isolated ceiling.
- Remaining no-config old variants are `historical_arm`, preserving loader and
  replay contracts without active steering authority.

## Caveats

- No scorer, dataset loader, split, benchmark bridge, or metric semantics were
  changed.
- `docs/experiments/synthesis/experiment_registry.json` remains provenance and
  still predates the May 28 R11-R15 decisions as a generated atlas source.
- The config inventory classifies runnable configs; it does not inspect every
  run artifact for metric validity.
- Holdout configs stay classified through their parent baseline surfaces, but
  holdout metrics remain residual-analysis triggers only.

## Validation

- `uv run pytest tests/test_program_variant_registry.py -q`
- `uv run python scripts/validate_primitives.py --errors-only`

Additional check attempted:

- `uv run python scripts/validate_experiment_taxonomy.py --errors-only` still
  fails on pre-existing provenance gaps in `experiment_registry.json` (missing
  archived run directories and decision-doc paths). This C4 change did not edit
  the JSON registry or scorer semantics.

The taxonomy registry needs a separate provenance cleanup before it can be used
as a hard gate for archive movement.

## Next Steps

1. Use the registry report's config inventory as the guardrail before any C2
   archive/delete movement.
2. Start E1 or G1 without describing `configs/experiments` loadability as active
   experiment volume.
3. Defer registry-derived atlas/matrix regeneration until X1 backfills component
   ceiling rows and C4 statuses are consumed by the export scripts.
