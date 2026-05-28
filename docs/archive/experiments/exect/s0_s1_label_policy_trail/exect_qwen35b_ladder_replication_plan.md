# ExECT Qwen3.6:35b Ladder Replication Plan

Date: 2026-05-20

## Purpose

Threads B–E froze the ExECT schema ladder on **GPT 4.1-mini** (fast iteration). This plan replicates the **main validation gates** on **Qwen3.6:35b via Ollama** using the same frozen programs, prompt versions, scorers, and splits — to surface model-specific failure modes (structured JSON, label granularity, multi-family drift) without replaying the full v4.x / v1.x micro-iteration arcs.

**Do not compare Qwen ladder metrics to GPT ladder metrics as a single experiment.** Same deterministic scorers and splits; different model track. See `docs/planning/kanban_plan.md` (active board) and `docs/planning/kanban_frozen_threads_history.md` (hosted GPT anchors).

## What we replicate (frozen GPT anchors)

| Thread | Level | Frozen prompt | GPT full anchor | Qwen configs |
| --- | --- | --- | --- | --- |
| B | S0/S1 (3 fam) | `exect_s0_s1_field_family_v4_10_label_policy` | `…221944Z` 92.3% micro | smoke, cap-25, full, regression slice |
| C | S2 (5 fam) | `exect_s2_field_family_v1_3_label_policy` | `…231223Z` 80.9% micro | smoke, cap-25, full |
| D | S3 (9 fam) | `exect_s3_field_family_v1_2_label_policy` | `…235439Z` 72.1% micro | smoke, cap-25, full |
| E | S4 (11 fam) | `exect_s4_field_family_v1_2_label_policy` | `…071248Z` 65.5% micro (11 fam) — **hosted frozen** | smoke, cap-25, full |

## What we skip

- S1 **test holdout** until Qwen S1 full + slice look sane (`exect_s0_s1_validation_test_*` deferred).
- Intermediate label-policy versions (v4.2–v4.9, S2 v1.0–v1.2, S3 v1.0–v1.1).
- Closed GPT ablations: section-aware, verify-repair, diagnosis-recall variant.
- Optimizers on Qwen (`BootstrapFewShot`, GEPA) per `docs/policies/qwen_dspy_latency_policy.md`.
- Re-tuning prompts on validation from Qwen errors (hosted GPT tracks remain frozen).

## Model and program controls

- **Model config:** `configs/models/exect_qwen35b_ollama.json` — raised `max_tokens` + `num_ctx` for long notes and large multi-family JSON (Gan direct `256` is insufficient for ExECT).
- **Program:** same `exect_s*_field_family_single_pass` variants as GPT configs.
- **Structured output:** `provider_json_schema_with_pydantic_validation` first; if schema validity collapses, add a one-off `strict_json_prompt_with_pydantic_validation` smoke before scaling (document in run metadata).
- **No** `ChainOfThought`, **no** optimizer unless explicitly marked overnight.

## Run order (recommended)

Estimate **~319 model calls** for the full matrix below (overnight-friendly on partial GPU offload).

**Overnight queue (Phases 0–2):** run sequentially with logging. **Policy (kanban grill 2026-05-20):** run Phase 0 smokes first (or stop the queue after the first four experiments) and **halt** if any level fails contract (invalid JSON, empty families, scorer errors). Only continue Phases 1–2 when all four smokes pass; try `strict_json_prompt_with_pydantic_validation` smoke for a failing level before scaling.

```powershell
# Phase 0 only (inspect before full queue)
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_smoke_qwen35b_ollama.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s2_smoke_qwen35b_ollama.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s3_smoke_qwen35b_ollama.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s4_smoke_qwen35b_ollama.json --env-file .env

# Phases 0–2 (after Phase 0 pass)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_overnight_exect_qwen35b_queue.ps1
```

Logs: `runs/overnight_logs/exect_qwen35b_ladder_phases_0_1_2_<timestamp>.log` and `.summary.txt`.

**Ollama scheduling (2026-05-20 grill):** run **ExECT Qwen S4 cap-25/full first** on dedicated Ollama; **Gan ReAct slice after** S4 full + `docs/exect_s4_validation_full_qwen35b_ollama_inspection_*.md`. Hosted **GPT temporal-candidates** cap-25/full may run **in parallel** with S4 (no Ollama); does not require ReAct completion.

### Phase 0 — Contract (12 calls)

Run all smokes (3 records × 4 levels). Exit: Pydantic-valid predictions, scorer runs, evidence fields present.

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_smoke_qwen35b_ollama.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s2_smoke_qwen35b_ollama.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s3_smoke_qwen35b_ollama.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s4_smoke_qwen35b_ollama.json --env-file .env
```

### Phase 1 — S1 port fidelity (65 calls)

1. `exect_s0_s1_validation_cap25_qwen35b_ollama` (25)
2. `exect_s0_s1_label_policy_regression_slice_qwen35b_ollama` (37) — known failure clusters
3. `exect_s0_s1_validation_full_qwen35b_ollama` (40)

**Read against GPT:** seizure granularity, diagnosis co-list, medication scope; report schema validity and evidence support separately from F1.

### Phase 2 — Ladder breadth (cap-25 then full, 130 calls)

Per level in order S2 → S3 → S4 (dependencies in prompt anchors):

| Step | Config | Calls |
| --- | --- | ---: |
| 2a | `exect_s2_validation_cap25_qwen35b_ollama` | 25 |
| 2b | `exect_s2_validation_full_qwen35b_ollama` | 40 |
| 2c | `exect_s3_validation_cap25_qwen35b_ollama` | 25 |
| 2d | `exect_s3_validation_full_qwen35b_ollama` | 40 | **Done** `…092244Z` 72.2% micro (+0.1pp vs GPT `…235439Z`) — `docs/experiments/exect/exect_s3_validation_full_qwen35b_ollama_inspection_20260520.md` |
| 2e | `exect_s4_validation_cap25_qwen35b_ollama` | 25 |
| 2f | `exect_s4_validation_full_qwen35b_ollama` | 40 |

**Per-level gates before promoting:**

- Cap-25: schema validity ≥ 95%; no systematic empty-family collapse vs GPT error reads.
- Full: per-family F1 table vs frozen GPT anchor; flag **multi-family seizure drift** (seen on GPT S2 v1.0) and **investigation modality** regressions (seen on GPT S3 v1.0).

### Phase 3 — Optional holdout (40 calls)

Only if S1 full is within ~10pp micro F1 of GPT or failure modes are understood:

- `exect_s0_s1_validation_test_qwen35b_ollama` *(config not shipped; add when ready)*

## Config inventory

| Config | Records | Purpose |
| --- | ---: | --- |
| `exect_s0_s1_smoke_qwen35b_ollama.json` | 3 | S1 contract |
| `exect_s0_s1_validation_cap25_qwen35b_ollama.json` | 25 | S1 diagnostic |
| `exect_s0_s1_label_policy_regression_slice_qwen35b_ollama.json` | 37 | S1 known-error replay |
| `exect_s0_s1_validation_full_qwen35b_ollama.json` | 40 | S1 anchor |
| `exect_s2_smoke_qwen35b_ollama.json` | 3 | S2 contract |
| `exect_s2_validation_cap25_qwen35b_ollama.json` | 25 | S2 diagnostic |
| `exect_s2_validation_full_qwen35b_ollama.json` | 40 | S2 anchor |
| `exect_s3_smoke_qwen35b_ollama.json` | 3 | S3 contract |
| `exect_s3_validation_cap25_qwen35b_ollama.json` | 25 | S3 diagnostic |
| `exect_s3_validation_full_qwen35b_ollama.json` | 40 | S3 anchor |
| `exect_s4_smoke_qwen35b_ollama.json` | 3 | S4 contract |
| `exect_s4_validation_cap25_qwen35b_ollama.json` | 25 | S4 diagnostic |
| `exect_s4_validation_full_qwen35b_ollama.json` | 40 | S4 anchor |

## Analysis checklist (per full run)

1. **Schema validity** — invalid JSON / truncated outputs (Qwen-specific).
2. **Evidence support rate** — compare to GPT full runs.
3. **Per-family F1** — never compare pooled micro across S1/S2/S3/S4 family counts.
4. **Cross-level drift** — seizure F1 dropping when families expand (GPT S2 lesson).
5. **Prior Qwen themes** — `docs/archive/prior-context/previous_exect_error_analysis.md`, `docs/archive/prior-context/prior_prompt_error_analysis_synthesis.md` (seizure granularity, ILAE specificity).
6. Record **GPU residency / RAM offload** in run notes.

## Artifacts

After each full validation, add `docs/exect_s{level}_validation_full_qwen35b_ollama_inspection_YYYYMMDD.md` mirroring GPT inspection docs.

Update `docs/planning/kanban_plan.md` (active board) when Qwen phases complete; add Qwen anchor rows to `docs/planning/kanban_frozen_threads_history.md` when replication stabilizes.
