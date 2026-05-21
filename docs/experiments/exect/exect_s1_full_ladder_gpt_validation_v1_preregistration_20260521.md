# ExECT S1 Full Reference Ladder — GPT Validation v1 Pre-Registration

Date: 2026-05-21  
Status: **Rungs 0–3 complete** — inspection `docs/experiments/exect/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md`; rungs 4–7 unlocked  
Comparison group: `exect_s1_full_ladder_gpt_validation_v1`  
Supersedes: `docs/experiments/exect/exect_s1_full_ladder_gpt_dev_v1_preregistration_20260521.md` (dev-split draft; not executed)  
Investigation: `docs/workstreams/optimizer/dspy_optimizer_investigation_20260521.md` (dev-first protocol amended here for Lane A comparability)  
Kanban: `docs/planning/kanban_plan.md` (Lane A optimizer ladder)

## Research question

On ExECT S1 with **GPT 4.1-mini**, what is the incremental value of each reference ladder rung — from deterministic feasibility (D1) through bare LLM (L0), schema-only LLM (L1), and hand-authored policy (L1+policy) — on the **same validation split** used by Lane A factor-isolation and frozen GPT anchors?

## Hypothesis

Manual v4_10 policy and inline bridges (L1+policy) will substantially exceed L0/L1/D1 on validation, establishing whether optimizer rungs 4–7 are worth probing. Lower rungs use the **cap-25 validation slice**; L1+policy uses **full validation (40)** so the policy ceiling is directly comparable to frozen production anchors.

## Split policy (amended 2026-05-21)

| Rung | Eval split | Scope | Rationale |
| --- | --- | --- | --- |
| D1, L0, L1 | `exectv2_fixed_v1:validation` | cap-25 | Matches Lane A factor-isolation and optimizer pilot; comparable to 95.8% micro cap-25 anchor |
| L1+policy | `exectv2_fixed_v1:validation` | full (40) | Matches `exect_s0_s1_validation_full_gpt4_1_mini` and other frozen S1 anchors |

**Train** (`exectv2_fixed_v1:train`, 120 records) remains reserved for **optimizer compile trainsets only** (rungs 4–7). Do not use train for rungs 0–3 reporting in this comparison group. See `docs/policies/dataset_splits_policy.md`.

**Test holdout** remains out of scope until a separate confirmation prereg.

## Fixed controls (all rungs)

| Control | Value |
| --- | --- |
| Dataset | `exect_v2` |
| Schema | `exect_s0_s1_field_family` |
| Scorer | `exect_field_family_deterministic_v1` |
| Model | GPT 4.1-mini (`configs/models/gan_s0_gpt4_1_mini.json`) |
| Verification | `none` |
| `report_on_test_split` | `false` |

## Varied factor

`ladder_rung` — one primary addition per rung; no stacked optimizer demos on rungs 0–3.

## Arms (rungs 0–3)

| Rung | ID | Config | Scope | `hybrid_balance_class` | `prompt_version` | `repair_policy` |
| ---: | --- | --- | --- | --- | --- | --- |
| 0 | D1 | `exect_s1_full_ladder_d1_cap25_gpt4_1_mini.json` | cap-25 | `D1_deterministic_only` | `exect_s0_s1_field_family_d1_feasibility` | `raw_no_benchmark_bridges` |
| 1 | L0 | `exect_s1_full_ladder_l0_cap25_gpt4_1_mini.json` | cap-25 | `L0_llm_only` | `exect_s0_s1_field_family_l0_minimal` | `raw_no_benchmark_bridges` |
| 2 | L1 | `exect_s1_full_ladder_l1_cap25_gpt4_1_mini.json` | cap-25 | `L1_llm_constrained` | `exect_s0_s1_field_family_l1_schema` | `raw_no_benchmark_bridges` |
| 3 | L1+policy | `exect_s1_full_ladder_l1_policy_full_gpt4_1_mini.json` | full (40) | `L1_llm_constrained` | `exect_s0_s1_field_family_v4_10_label_policy` | `none` (inline bridges) |

**L0/L1 boundary:** structured JSON output held constant. L0 = minimal signature; L1 = schema-oriented descriptions without benchmark policy examples; L1+policy = v4_10 + inline bridges.

**D1 boundary:** no LLM calls; note-anchored substring match; bridges disabled in prediction path.

## Run order

1. Dry-run all four configs (`--dry-run`).
2. Run **D1 cap-25** first (fast, no model cost).
3. Run **L0 cap-25 → L1 cap-25 → L1+policy full (40)**.
4. Inspection `docs/exect_s1_full_ladder_gpt_validation_v1_inspection_<date>.md`.
5. Registry rows with canonical run IDs.

Rungs 4–5 (optimizer automation thesis) unlocked after rung 3 gate pass — see **`docs/experiments/exect/exect_s1_ladder_optimizer_automation_thesis_20260521.md`**. These test whether L0/L1 + DSPy compile can match hand-crafted policy without v4_10 or inline bridges in the prediction path. Rungs 6–7 (BootstrapRS, GEPA) remain deferred until rung 4–5 inspection.

**Distinction:** rungs 0–3 measure *how much* hand-crafting helps. Rungs 4–5 test whether the optimizer can *replace* it.

## Primary metrics

| Rung | Primary metric | Records |
| --- | --- | ---: |
| D1, L0, L1 | Pooled micro F1 on **cap-25 validation** | 25 |
| L1+policy | Pooled micro F1 on **full validation** | 40 |

Report sequential deltas on the **cap-25 slice** for D1/L0/L1. Compare L1+policy full (40) to `exect_s0_s1_validation_full_gpt4_1_mini` (92.3% micro) and cap-25 v4_10 (95.8%).

## Validation gates (rungs 0–3)

| Transition | Proceed rule |
| --- | --- |
| D1 → L0 | Always run |
| L0 → L1 | Always run |
| L1 → L1+policy | Always run |
| L1+policy → rung 4+ | L1+policy micro F1 ≥ L1 cap-25 + **2pp** on comparable slice **or** L1+policy full ≥ 90% micro with no family regression > 3pp vs cap-25 L1 |

## In-group and frozen references

| Role | Run / config | Micro F1 | Slice |
| --- | --- | ---: | --- |
| Optimizer baseline (in-group) | `exect_s1_optimizer_baseline_cap25_gpt4_1_mini` | 95.8% | cap-25 |
| GPT v4_10 cap-25 (frozen) | `exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T221936Z` | 95.8% | cap-25 |
| GPT v4_10 full (frozen) | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` | 92.3% | full 40 |
| Optimizer bootstrap (reject) | `exect_s1_optimizer_bootstrap_cap25_gpt4_1_mini_20260521T000608Z` | 90.7% | cap-25 |

L1+policy in this ladder should match optimizer baseline / v4_10 cap-25 on micro F1 if controls are aligned (`repair_policy=none`, same prompt).

## Implementation prerequisites

- [x] L0/L1/D1 program scaffolding in `exect_s0_s1.py`
- [x] Four validation configs under `configs/experiments/exect_s1_full_ladder_*_{cap25,full}_gpt4_1_mini.json`
- [x] Taxonomy `varied_factor: ladder_rung`
- [x] Model-backed runs (2026-05-21)
- [x] Inspection doc

## Commands

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_full_ladder_d1_cap25_gpt4_1_mini.json --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_full_ladder_l0_cap25_gpt4_1_mini.json --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_full_ladder_l1_cap25_gpt4_1_mini.json --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_full_ladder_l1_policy_full_gpt4_1_mini.json --env-file .env --dry-run

# D1 first (no model spend)
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_full_ladder_d1_cap25_gpt4_1_mini.json --env-file .env

# L0 → L1 cap-25, then L1+policy full
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_full_ladder_l0_cap25_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_full_ladder_l1_cap25_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_full_ladder_l1_policy_full_gpt4_1_mini.json --env-file .env
```

## Explicit non-goals

- Development-split ladder reporting for rungs 0–3
- Optimizer compile rungs 4–7 in this wave (separate prereg; compile on dev, eval on validation)
- Test-holdout confirmation
- Qwen ladder port
