# Session Brief

Last reviewed: 2026-05-22
Status: Pilot memory seed

## Current Active State

The active execution board is `docs/planning/kanban_plan.md`.

Current mode: full model suite alignment on frozen ExECT S1/S4 and Gan F0 surfaces.

Decision scope: model-suite rows are for model-comparison evidence unless an inspection doc explicitly promotes an operational default.

## Active Pulls

| Item | Status | Confidence | Next action | Source |
| --- | --- | --- | --- | --- |
| Qwen 3.6:35b Gan F0 cap-25 | `done` | `direct_source` | Full validation done — `…131822Z`, 64.4% monthly. | `docs/planning/kanban_plan.md` |
| GPT 5.5 frozen full replay | `done` | `direct_source` | Full replay complete. | `docs/planning/kanban_plan.md` |
| Local scaling ladder | `in_progress` | `direct_source` | 9b ladder in flight; 27b deferred overnight. | `docs/planning/kanban_plan.md` |
| Model-profile synthesis | `open` | `inferred_from_sources` | Draft after suite rows mature. | `docs/planning/kanban_plan.md` |

## Current Operational Defaults

| Track | Status | Confidence | Next action | Source |
| --- | --- | --- | --- | --- |
| Gan S0 F0 expanded builders + prose | `operational` | `direct_source` | Use as frozen Gan F0 surface for model-suite comparison. | `docs/planning/kanban_plan.md` |
| ExECT S1 v4_10 + inline bridges | `operational` | `direct_source` | Keep v4_10 as all-track S1 policy unless a new preregistered arm promotes. | `docs/planning/kanban_plan.md` |
| ExECT S4 K0+K1 cause bridge variant | `operational` | `direct_source` | Use current frozen S4 variant; mechanism class remains scoped to documented evidence. | `docs/planning/kanban_plan.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` |

## Important Non-Claims

| Warning | Status | Confidence | Next action | Source |
| --- | --- | --- | --- | --- |
| Gemini Gan F0 lead is not operational promotion | `stale_check` | `direct_source` | Label as model-comparison evidence only. | `docs/planning/kanban_plan.md` |
| Arm rejects are not mechanism rejects unless a mechanism review says so | `open` | `direct_source` | Preserve `decision_scope` in docs, registry rows, and summaries. | `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md` |
| Published ExECTv2 reproduction remains blocked by CUI-aware all-family scoring | `blocked` | `direct_source` | Do not call current ExECT rows published benchmark reproduction. | `docs/planning/kanban_plan.md` |
| Gan real-set reproduction remains blocked by data access | `blocked` | `direct_source` | Treat current Gan work as synthetic validation unless source data changes. | `docs/planning/kanban_plan.md` |
| Do not run two Ollama jobs at once on the Windows laptop | `operational` | `direct_source` | Check active local runs before launching Qwen cap/full jobs. | `docs/planning/kanban_plan.md` |

## Before Starting New Work

Read the relevant skill first, then read the source docs it names. For experiments, default to:

1. `docs/planning/kanban_plan.md`
2. `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`
3. `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`
4. relevant preregistration or inspection docs
5. relevant dataset audit if loaders, labels, scorers, or benchmark interpretation are involved

## Validation Note

On 2026-05-22, within `uv run pytest tests/test_inspection_templates.py tests/test_experiment_registry_validation.py tests/test_export_research_atlas.py`, `tests/test_inspection_templates.py` and `tests/test_export_research_atlas.py` passed. This was rechecked after adding the Phase 2 dream candidate template.

The full command failed in `tests/test_experiment_registry_validation.py::test_repository_experiment_taxonomy_validation_passes_errors_only` because current registry rows contain controlled-vocabulary drift for newer statuses/model tracks and one comparison-group caveat gap:

- `outcome='blocked'`
- `context_strategy='full_note_plus_exect_frequency_structured_slots'`
- `model_track='claude_sonnet46'`
- `model_track='gemini3flash'`
- `comparison_group:exect_s1_qwen_diagnosis_stabilized_v1` mixes model tracks without an explicit exception

This predates the memory seed and is exactly the sort of stale-control issue the memory layer should surface.
