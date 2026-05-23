# Session Brief

Last reviewed: 2026-05-23
Status: Promoted memory seed (updated after Cursor SDK pilot validation)

## Current Active State

The active execution board is `docs/planning/kanban_plan.md`.

Primary execution mode is Gan S0 deterministic candidate-builder gap follow-through (G16 broader GPT validation). Model-suite finish (M1 Qwen 27b) is Priority 2, not the top pull.

Decision scope: model-suite rows are for model-comparison evidence unless an inspection doc explicitly promotes an operational default.

## Active Pulls

| Item | Status | Confidence | Next action | Source |
| --- | --- | --- | --- | --- |
| G16 — broader GPT validation for `gan_s0_candidate_builder_gap_v1` | `ready` | `direct_source` | Execute broader GPT validation over full split / cap sample. | `docs/planning/kanban_plan.md` |
| Local scaling ladder | `done` | `direct_source` | Qwen 3.5:9b column done; Qwen 3.6:27b ready / next Ollama pull when idle. | `docs/planning/kanban_plan.md` |
| Qwen 3.6:35b Gan F0 cap-25 | `done` | `direct_source` | Full validation done — `…131822Z`, 64.4% monthly. | `docs/planning/kanban_plan.md` |
| GPT 5.5 frozen full replay | `done` | `direct_source` | Full replay complete. | `docs/planning/kanban_plan.md` |
| Model-profile synthesis | `open` | `inferred_from_sources` | Draft after suite rows mature. | `docs/planning/kanban_plan.md` |

## Current Operational Defaults

| Track | Status | Confidence | Next action | Source |
| --- | --- | --- | --- | --- |
| Gan S0 F0 expanded builders + prose | `operational` | `direct_source` | Remains full-validation operational default (68.1% monthly GPT anchor). | `docs/planning/kanban_plan.md` |
| Gan S0 v1.4 no-example policy | `operational` | `direct_source` | Enriched-slice GPT control (36.0% monthly on enriched residuals). | `docs/planning/kanban_plan.md` |
| ExECT S1 v4_10 + inline bridges | `operational` | `direct_source` | Keep v4_10 as all-track S1 policy unless a new preregistered arm promotes. | `docs/planning/kanban_plan.md` |
| ExECT S4 K0+K1 cause bridge variant | `operational` | `direct_source` | Use current frozen S4 variant; mechanism class remains scoped to documented evidence. | `docs/planning/kanban_plan.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` |

## Important Non-Claims

| Warning | Status | Confidence | Next action | Source |
| --- | --- | --- | --- | --- |
| Builder-gap v1 slice lift is slice-gate evidence only | `arm` | `direct_source` | 92.0% monthly / 96.0% pragmatic on enriched 25-record slice is not operational promotion. Full-validation generalization pending G16. Primary run: `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z`. | `docs/planning/kanban_plan.md` |
| No-model coverage audit | `arm` | `direct_source` | Deterministic builders contained exact gold label for 5/25 enriched-slice records before G13; 23/25 after builder-gap v1 (G14). Treat enriched slice as search/diagnostic surface, not population estimate. | `docs/planning/kanban_plan.md` |
| Do not transfer failed GPT-first arms to Qwen | `arm` | `direct_source` | GPT-first arms G5/G6/G6b/G7/G9 failed; do not transfer to Qwen without preregistered transferability question. | `docs/planning/kanban_plan.md` |
| Gemini Gan F0 lead is not operational promotion | `stale_check` | `direct_source` | Gemini 3 Flash 75.3% monthly on Gan F0 is model-comparison evidence only (decision_scope: arm); does not override F0 operational default. | `docs/planning/kanban_plan.md` |
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
6. For Gan S0 builder-gap work, also read `docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md` and linked G11–G15 artifacts before code or promotion decisions.

## Validation Note

On 2026-05-23, within `uv run pytest tests/test_inspection_templates.py tests/test_experiment_registry_validation.py tests/test_export_research_atlas.py`, all tests passed. Registry taxonomy validation test `test_repository_experiment_taxonomy_validation_passes_errors_only` passed, indicating that the previously reported taxonomy drift has been resolved or cataloged.

Note: No registry rows were found for `gan_s0_candidate_builder_gap` work until added via review promotion on 2026-05-23.
