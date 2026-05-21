# ExECT S1 Optimizer Pilot — Clean GPT Ablation Pre-Registration

Date: 2026-05-21  
Status: **Complete — cap-25 inspected 2026-05-21**  
Comparison group: `exect_s1_optimizer_gpt_cap25_v1`  
Kanban: `docs/kanban_plan.md` (Lane A, Phase 2)

## Research question

On ExECT S1 with **GPT 4.1-mini**, does a **BootstrapFewShot-compiled** prompt improve cap-25 micro F1 versus the frozen v4_10 single-pass baseline, when split, schema, scorer, and program architecture are fixed?

## Hypothesis

A small dev-set bootstrap (field-family micro F1 metric) can improve medication/seizure normalization on cap-25 without the latency cost of verify-repair. Full validation is out of scope until cap-25 shows ≥ 2pp micro gain.

## Blocker (resolved 2026-05-21)

`scripts/run_experiment.py` previously raised:

```text
Only Gan S0 experiments currently support DSPy optimization.
```

**Implemented:** `compile_exect_s0_s1_module` with train split `exectv2_fixed_v1:train` (first 40 train IDs via `trainset_size`), optimizer metric `exect_field_family_micro_f1`, and frozen benchmark scorer unchanged for evaluation.

Configs:

- `configs/experiments/exect_s1_optimizer_baseline_cap25_gpt4_1_mini.json`
- `configs/experiments/exect_s1_optimizer_bootstrap_cap25_gpt4_1_mini.json`

Dry-run both configs before model-backed cap-25 execution.

## Fixed controls (both arms)

| Control | Value |
| --- | --- |
| Dataset | `exect_v2` |
| Eval split | `exectv2_fixed_v1:validation` (cap-25) |
| Train split | `exectv2_fixed_v1:train` (optimizer only; 40-record cap via `trainset_size`) |
| Schema | `exect_s0_s1_field_family` |
| Scorer | `exect_field_family_deterministic_v1` |
| Model | GPT 4.1-mini |
| Program | `exect_s0_s1_field_family_single_pass` |
| `repair_policy` | `none` |
| Verification | `none` |

## Varied factor

`optimizer_strategy`

## Arms

| Arm | `optimizer_strategy` | `example_strategy` | Config (planned) |
| --- | --- | --- | --- |
| **Frozen baseline** | `zero_shot_or_prompt_only` | manual policy examples (v4_10) | `exect_s1_optimizer_baseline_cap25_gpt4_1_mini.json` |
| **Bootstrap compiled** | `bootstrapped` | BootstrapFewShot on dev | `exect_s1_optimizer_bootstrap_cap25_gpt4_1_mini.json` |

### Optimizer config (planned)

```json
{
  "name": "BootstrapFewShot",
  "metric_name": "exect_field_family_micro_f1",
  "max_bootstrapped_demos": 4,
  "max_labeled_demos": 4,
  "max_rounds": 1,
  "trainset_size": 40
}
```

Metric name is provisional — must map to a deterministic dev-set metric that does not leak validation labels.

## Frozen baseline reference

`exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` — 92.3% micro full. Cap-25 baseline to be measured in-group (do not assume full-scale cap-25 parity).

## Run order

1. Implement ExECT compile path + metric in `run_experiment.py` / program module.
2. Unit test: compile on 3 dev records, predict 1 validation record.
3. Dry-run both configs.
4. Cap-25 baseline vs compiled.
5. Inspection `docs/exect_s1_optimizer_gpt_cap25_v1_inspection_<date>.md` — **cap-25 only**.
6. Registry rows.

Full validation (40) deferred unless cap-25 shows ≥ 2pp micro F1 and schema ≥ 95%.

## Primary metric

**Pooled micro F1** on cap-25 validation records.

## Diagnostic metrics

- Per-family F1
- Compiled demo count and artifact hash
- Schema-valid rate
- Compile duration and token cost
- Optimizer metric vs benchmark scorer delta (must be reported separately)

## Cap-25 gate

| Outcome | Rule |
| --- | --- |
| **Proceed to full-validation design** | Micro F1 ≥ baseline + 2pp **and** schema ≥ 95% **and** no family regression > 3pp |
| **Hold** | +1pp to +2pp micro with clean schema |
| **Reject** | Null or negative micro delta **or** schema < 90% |

## Scope limits

- No GEPA / MIPRO in this pilot.
- No Qwen compile until GPT cap-25 promotes.
- Optimizer metric must not silently become the benchmark claim.

## Artifacts checklist

- [x] `compile_exect_s0_s1_module` (or equivalent)
- [x] Optimizer metric implementation + tests
- [x] Two cap-25 configs
- [x] Compiled state artifact path documented
- [x] Inspection doc
- [x] Registry rows with `varied_factor: optimizer_strategy`
