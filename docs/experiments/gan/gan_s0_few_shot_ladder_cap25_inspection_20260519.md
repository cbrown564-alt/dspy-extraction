# Gan S0 Few-Shot Optimizer Ladder — Cap-25 Inspection

Date: 2026-05-19  
Dataset/split: `gan_2026` / `gan_2026_fixed_v1:validation` (25-record cap)  
Program variant: `gan_frequency_s0_direct_single_pass`  
Prompt: `gan_frequency_s0_synthesis_v1`  
Scorer: `gan_frequency_deterministic_v1` (unchanged)  
Trainset: 50 development records, synthesis-labeled examples, `synthesis_exact_with_evidence` metric for bootstrap optimizers

## Hypothesis

On the fixed direct Gan S0 path, compare whether label gains come from labeled demonstrations alone (`LabeledFewShot`), from bootstrapped teacher traces (`BootstrapFewShot`), or from search over demo sets (`BootstrapFewShotWithRandomSearch` / `BootstrapRS`).

## Runs

| Optimizer | Run ID |
|-----------|--------|
| LabeledFewShot | `runs/gan_s0_ladder_labeled_fewshot_cap25_gpt4_1_mini_20260519T091940Z` |
| BootstrapFewShot | `runs/gan_s0_ladder_bootstrap_cap25_gpt4_1_mini_20260519T092020Z` |
| BootstrapFewShotWithRandomSearch (8 candidates) | `runs/gan_s0_ladder_bootstrap_rs_cap25_gpt4_1_mini_20260519T092117Z` |

Configs: `configs/experiments/gan_s0_ladder_*_cap25_gpt4_1_mini.json`

## Cap-25 Results (valid predictions only for label metrics)

| Optimizer | Compile (s) | Pred (s/rec) | Schema validity | Norm exact | Monthly | Purist | Pragmatic | Evidence support |
|-----------|------------:|-------------:|----------------:|-----------:|--------:|-------:|----------:|-----------------:|
| LabeledFewShot | 0.0 | 1.32 | 92.0% | **34.8%** | **43.5%** | **56.5%** | **69.6%** | 100.0% |
| BootstrapFewShot | 17.8 | 1.17 | 92.0% | 21.7% | 34.8% | 39.1% | 60.9% | 100.0% |
| BootstrapRS | 166.3 | 1.19 | **96.0%** | 29.2% | 37.5% | 50.0% | 66.7% | 100.0% |

Token usage (compile + predict): LabeledFewShot 90k total; BootstrapFewShot 141k; BootstrapRS 2.36M (629 LM history entries during search).

## Interpretation

1. **Demos help; bootstrapping does not on this slice.** `LabeledFewShot` with four synthesis-labeled demonstrations outperforms both bootstrap arms on every benchmark-facing label metric. Plain `BootstrapFewShot` is strictly worse than labeled-only for normalized exact (−13.1 pp), monthly (−8.7 pp), Purist (−17.4 pp), and Pragmatic (−8.7 pp) at identical schema validity.

2. **Search buys modest recovery, not leadership.** `BootstrapFewShotWithRandomSearch` improves over plain bootstrap (schema +4.0 pp, normalized +7.5 pp, Purist +10.9 pp) but still trails `LabeledFewShot` on all label metrics while adding ~166 s compile time and ~26× token cost versus labeled-only.

3. **Evidence support is not the differentiator.** All three arms reach 100% evidence quote support on valid predictions; optimizer choice here affects canonical label choice, not grounding.

4. **Direct path differs from the historical CoT synthesis baseline.** The full-validation synthesis `BootstrapFewShot` run used `gan_frequency_s0_single_pass` (ChainOfThought) and remains the stronger hosted reference for label accuracy. These ladder results apply to the **direct** program variant only and should not be read as disproving the earlier CoT bootstrap result.

## Decision

- **Do not promote** `BootstrapFewShot` or `BootstrapRS` as the default optimizer on `gan_frequency_s0_direct_single_pass` for hosted GPT 4.1-mini.
- **Prefer** synthesis-labeled `LabeledFewShot` when few-shot demos are needed on the direct path; keep zero-shot direct + verify-repair v2 as the production-quality hosted stack from prior work.
- **Defer** local-Qwen transfer of any optimizer-heavy ladder arm until a hosted winner clearly beats verify-repair v2 on full validation (none do on this cap).

## Validation

- `uv run --extra dev pytest tests/test_gan_s0_program.py tests/test_experiment_configs.py`
- Dry-runs and capped runs for all three ladder configs with `--env-file .env`

## Follow-ups

- Optional: rerun ladder on `gan_frequency_s0_single_pass` to confirm bootstrap still helps CoT on the same 25-record cap.
- Optional: matched direct-only cap-25 without optimizers for strict extraction-only comparison (kanban optional item).
