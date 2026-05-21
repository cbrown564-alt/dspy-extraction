# Gan S0 Semantic Optimizer Cap-25 Inspection (2026-05-19)

## Purpose

Measure whether `BootstrapFewShot` with the new `semantic_frequency_with_evidence` optimizer metric improves monthly/Purist accuracy and preserves evidence support versus the synthesis exact-label optimizer and verify-repair v2 anchor on the same 25-record GPT 4.1-mini validation cap.

## Artifacts

- Semantic bootstrap (this run): `runs/gan_s0_semantic_bootstrap_cap25_gpt4_1_mini_20260519T100255Z`
- Config: `configs/experiments/gan_s0_semantic_bootstrap_cap25_gpt4_1_mini.json`

Anchors (same cap, unchanged `gan_frequency_deterministic_v1` scorer):

- Verify-repair v2: `runs/gan_s0_verify_repair_cap25_gpt4_1_mini_20260519T084511Z`
- Synthesis bootstrap (direct ladder): `runs/gan_s0_ladder_bootstrap_cap25_gpt4_1_mini_20260519T092020Z`
- LabeledFewShot (direct ladder): `runs/gan_s0_ladder_labeled_fewshot_cap25_gpt4_1_mini_20260519T091940Z`

## Cap-25 Results (valid predictions only for label metrics)

| Variant | Compile (s) | Pred (s/rec) | Schema validity | Norm exact | Monthly | Purist | Pragmatic | Evidence support |
|---------|------------:|-------------:|----------------:|-----------:|--------:|-------:|----------:|-----------------:|
| Semantic bootstrap | 0.3 | 1.69 | **96.0%** | 20.8% | 33.3% | **41.7%** | **66.7%** | 100.0% |
| Synthesis bootstrap (direct) | 17.8 | 1.17 | 92.0% | 21.7% | 34.8% | 39.1% | 60.9% | 100.0% |
| LabeledFewShot (direct) | 0.0 | 1.32 | 92.0% | **34.8%** | **43.5%** | **56.5%** | **69.6%** | 100.0% |
| Verify-repair v2 | — | ~2.8 | 92.0% | **26.1%** | 34.8% | **47.8%** | 69.6% | 91.3% |

Token usage: 97,547 total (96,491 prompt + 1,056 completion); 75 estimated model calls.

## Interpretation

1. **Evidence support holds.** Semantic bootstrap reaches 100% evidence quote support on valid predictions with no evidence-support regression versus the direct ladder arms.

2. **Semantic metric does not beat verify-repair v2 on monthly/Purist.** Monthly frequency (33.3%) trails verify-repair v2 (34.8%) and LabeledFewShot (43.5%). Purist category (41.7%) trails verify-repair v2 (47.8%) and LabeledFewShot (56.5%).

3. **Semantic bootstrap vs synthesis bootstrap is mixed.** The semantic objective slightly improves Purist (+2.6 pp) and Pragmatic (+5.8 pp) versus synthesis bootstrap on the direct path, with a modest schema-validity gain (+4.0 pp), but normalized exact and monthly frequency are flat or slightly worse.

4. **Bootstrap remains weaker than labeled demos.** LabeledFewShot still leads all label metrics on this cap regardless of optimizer metric. The semantic metric change alone does not fix the bootstrap underperformance pattern documented in the few-shot ladder inspection.

5. **Failure modes are semantic, not evidence.** Dominant errors are label mismatches, monthly-frequency drift, incomplete cluster labels (`gan_10618`), and over-abstention to `unknown` or `no seizure frequency reference` on frequent cases.

## Promotion Gate (kanban)

| Criterion | Met? |
|-----------|------|
| Monthly/Purist improved vs verify-repair v2 | No |
| Evidence support preserved | Yes (100%) |
| Schema validity acceptable | Yes (96.0%) |
| Clear win vs synthesis exact-label bootstrap | Partial (Purist/Pragmatic only) |

**Decision:** Do **not** promote semantic bootstrap to full validation yet. Verify-repair v2 remains the hosted quality anchor. Next optimizer work should test `semantic_frequency_with_evidence` with `LabeledFewShot` (metric-neutral at compile time but paired demos) or a semantic GEPA feedback pass rather than scaling plain bootstrap.

## Validation

- `uv run --extra dev pytest tests/test_experiment_configs.py tests/test_gan_s0_program.py`
- Dry-run and capped run with `--env-file .env`
