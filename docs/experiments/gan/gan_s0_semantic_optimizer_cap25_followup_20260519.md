# Gan S0 Semantic Optimizer Cap-25 Follow-Up (2026-05-19)

## Purpose

Test whether `semantic_frequency_with_evidence` helps when paired with **LabeledFewShot** or **semantic GEPA feedback**, after plain semantic `BootstrapFewShot` failed to beat verify-repair v2 on monthly/Purist at cap-25.

## Artifacts

| Variant | Run | Config |
|---------|-----|--------|
| Semantic LabeledFewShot | `runs/gan_s0_semantic_labeled_fewshot_cap25_gpt4_1_mini_20260519T100621Z` | `configs/experiments/gan_s0_semantic_labeled_fewshot_cap25_gpt4_1_mini.json` |
| Semantic GEPA | `runs/gan_s0_semantic_gepa_cap25_gpt4_1_mini_20260519T100648Z` | `configs/experiments/gan_s0_semantic_gepa_cap25_gpt4_1_mini.json` |

Anchors (same cap):

- Verify-repair v2: `runs/gan_s0_verify_repair_cap25_gpt4_1_mini_20260519T084511Z`
- Semantic bootstrap: `runs/gan_s0_semantic_bootstrap_cap25_gpt4_1_mini_20260519T100255Z`
- Synthesis LabeledFewShot: `runs/gan_s0_ladder_labeled_fewshot_cap25_gpt4_1_mini_20260519T091940Z`

## Cap-25 Results

| Variant | Compile (s) | Pred (s/rec) | Schema | Norm exact | Monthly | Purist | Pragmatic | Evidence |
|---------|------------:|-------------:|-------:|-----------:|--------:|-------:|----------:|---------:|
| Semantic LabeledFewShot | 0.0 | 0.01 | 92.0% | **34.8%** | 43.5% | **56.5%** | 69.6% | **100%** |
| Synthesis LabeledFewShot | 0.0 | 1.32 | 92.0% | **34.8%** | **43.5%** | **56.5%** | **69.6%** | **100%** |
| Semantic bootstrap | 0.3 | 1.69 | **96.0%** | 20.8% | 33.3% | 41.7% | 66.7% | 100% |
| Semantic GEPA (`max_metric_calls=16`) | 0.4 | 0.00* | 92.0% | 26.1% | 34.8% | 47.8% | 69.6% | **34.8%** |
| Verify-repair v2 | — | ~2.8 | 92.0% | 26.1% | 34.8% | 47.8% | 69.6% | 91.3% |

\*Semantic GEPA prediction timing reflects a compile-only baseline pass; GEPA consumed the metric budget on the initial 50-example eval and did not run reflection iterations.

## Interpretation

### LabeledFewShot + semantic metric

The semantic compile metric is **neutral** for `LabeledFewShot`: every cap-25 metric matches the synthesis `synthesis_exact_with_evidence` labeled-fewshot ladder run exactly. `LabeledFewShot` injects fixed labeled demos and does not use the compile metric for demo selection, so changing the metric name alone does not change behavior.

**Implication:** Further semantic work should not repeat LabeledFewShot under a renamed metric; demo content or verifier/repair policy must change instead.

### Semantic GEPA

GEPA with `semantic_frequency_with_evidence_feedback` and `max_metric_calls=16` completed after a single base evaluation over 50 train examples (0 reflection iterations). Cap-25 prediction metrics match **verify-repair v2 on monthly/Purist/Pragmatic** but **evidence support collapses to 34.8%** (15 unsupported-quote errors), identical to unguarded direct extraction on this slice.

**Implication:** Do not scale semantic GEPA until the budget supports real reflection and prompt-length is monitored. The failure mode is evidence-quote formatting, not monthly/Purist scoring.

## Promotion Gate

| Criterion | Semantic LabeledFewShot | Semantic GEPA |
|-----------|-------------------------|---------------|
| Monthly/Purist vs verify-repair v2 | Partial (Purist yes, monthly no) | No |
| Evidence preserved | Yes | **No** |
| Beats semantic bootstrap | Yes (labels) | Mixed |
| Worth full validation | **No** | **No** |

**Decision:** Do **not** promote semantic full validation via either path. Verify-repair v2 full validation remains the hosted quality anchor. Semantic optimizer work should pivot to **verifier/repair** or **demo/policy content** changes, not renamed compile metrics on LabeledFewShot or under-budget GEPA.

## Validation

- `uv run --extra dev pytest tests/test_experiment_configs.py -k "semantic_labeled or semantic_gepa"`
- Dry-runs and capped runs with `--env-file .env`
