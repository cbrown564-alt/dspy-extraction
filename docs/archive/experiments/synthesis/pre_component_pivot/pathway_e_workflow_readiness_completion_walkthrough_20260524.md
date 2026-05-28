# Pathway E — Workflow Readiness Completion Walkthrough

Date: 2026-05-24  
Pathway: E — Workflow Readiness  
Status: **Complete**  
decision_scope: pathway closure (operational discipline; no scorer or model-output changes)

## Pathway Outcome

Pathway E established workflow gates for safe experiment execution. E3 closes the final open card by freezing a **provider smoke ledger** that records run ID, config, structured-output strategy, schema validity, and evidence support before broad model comparisons.

| Card | Status | Artifact |
| --- | --- | --- |
| E1. API key preflight | **Done** (pre-existing) | `.env` preflight discipline |
| E2. Qwen high-context warning | **Done** (pre-existing) | [qwen_dspy_latency_policy.md](../../policies/qwen_dspy_latency_policy.md) |
| E3. Provider smoke ledger | **Done** | [provider_smoke_ledger_20260524.md](../../policies/provider_smoke_ledger_20260524.md) |
| E4. Cursor implementation workflow | **Retired** (historical) | Cursor SDK workstream archived; project-local Cursor skills removed after discount expiry |

## E3 Summary

Compiled canonical smoke entries for all model-suite tracks used in `model_suite_frozen_architecture_v1`:

| Provider track | Model-suite gate | Notes |
| --- | --- | --- |
| GPT 5.5 | Pass (F0 + S1 + S4) | Full suite completed 2026-05-22 |
| Gemini 3 Flash | Pass (F0 + S1 + S4); partial legacy 1-record | Label sample failure documented |
| Gemini 3.1 Flash-Lite | Pass | GA model id confirmed |
| Claude Sonnet 4.6 | Pass | Windows 2026-05-22 |
| Qwen3.6:27b | Pass | Bounded `num_ctx=65536` for ExECT |
| Qwen3.6:35b | Pass (direct + F0 + S1 + S4) | Legacy 1-record incomplete |
| Qwen3.5:9b | Pass (legacy Gan only) | Secondary track |
| GPT 4.1-mini | Pass (S1 + S4); partial legacy Gan | Anchor predates F0 smoke surface |

Ledger rows trace to primary `runs/*/metrics.json` artifacts. No new model budget was spent for E3 closure.

## Gate Discipline Now Enforced

Before scheduling full validation on a **new** provider track:

1. Offline adapter/config tests pass.
2. Smoke config dry-run passes.
3. Smoke run completes with standard artifacts.
4. Ledger row added with schema/evidence rates.
5. Full validation proceeds only on Pass (or documented Partial with F0 pass).

## Validation Performed

- Smoke metrics cross-checked against local `runs/*/metrics.json` for canonical run IDs cited in model-suite inspection docs (2026-05-22).
- Offline tests: `uv run pytest tests/test_llm_adapters.py tests/test_model_comparison_configs.py tests/test_experiment_configs.py -q`
- No scorer, gold-label, or registry semantics changed.

## Files Created

- `docs/policies/provider_smoke_ledger_20260524.md`
- `docs/experiments/synthesis/pathway_e_workflow_readiness_completion_walkthrough_20260524.md`

## Files Updated

- `docs/planning/kanban_plan.md`
- `docs/policies/model_config_smoke_tests.md` (ledger cross-reference)
- `docs/memory/workflow_index.md` (routing to ledger)
