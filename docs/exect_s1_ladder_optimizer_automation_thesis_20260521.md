# ExECT S1 — Can the Optimizer Replace Hand-Crafted Policy?

Date: 2026-05-21  
Status: **Cap-25 complete** — `docs/exect_s1_ladder_optimizer_automation_inspection_20260521.md`  
Comparison group: `exect_s1_ladder_optimizer_automation_v1`  
Ladder context: `docs/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md` (rungs 0–3 complete)  
Investigation: `docs/dspy_optimizer_investigation_20260521.md`

## Thesis (research question)

Can DSPy compile-time optimization on a **stripped-back** program (L0 bare LLM or L1 schema-only) recover the benchmark F1 we currently obtain only through **hand-authored** v4_10 label policy and inline benchmark bridges — yielding a more **durable, scalable, and generalizable** path than manual prompt engineering?

This is **not** what the earlier optimizer pilot tested. That pilot stacked BootstrapFewShot on **already hand-tuned** v4_10 (`exect_s1_optimizer_bootstrap_cap25`) and regressed (−5.1 pp vs 95.8% cap-25). Rungs 0–3 quantify the hand-craft lift (+36 pp L0→policy on cap-25). **Rungs 4–5 here** test whether compile can **substitute** for that lift.

## What rungs 0–3 already proved

| Rung | Mechanism | Cap-25 micro |
| ---: | --- | ---: |
| L0 | Bare LLM, no policy, no bridges | 60.0% |
| L1 | + schema descriptions | 67.7% |
| L1+policy | v4_10 + inline bridges | ~95.8% (cap-25 ref) / 92.3% full |

Hand-crafting is ~**28 pp** over schema-only L1 on the same slice. The optimizer must close most of that gap **without** v4_10 policy text or `repair_policy=none` inline bridges in the **prediction path**.

## Arms (rungs 4–5)

| Rung | Config | Base prompt | Optimizer | `repair_policy` (eval) | Compile metric |
| ---: | --- | --- | --- | --- | --- |
| 4a | `exect_s1_full_ladder_l0_labeled_cap25_gpt4_1_mini` | `l0_minimal` | LabeledFewShot k=4 | `raw_no_benchmark_bridges` | `exect_field_family_micro_f1`† |
| 4b | `exect_s1_full_ladder_l0_bootstrap_cap25_gpt4_1_mini` | `l0_minimal` | BootstrapFewShot k=4 | `raw_no_benchmark_bridges` | `exect_field_family_micro_f1_raw` |
| 4c | `exect_s1_full_ladder_l1_labeled_cap25_gpt4_1_mini` | `l1_schema` | LabeledFewShot k=4 | `raw_no_benchmark_bridges` | `exect_field_family_micro_f1`† |

†LabeledFewShot does not use the compile metric for search; metric field is recorded for registry consistency.

**Train:** first 40 IDs from `exectv2_fixed_v1:train` (`trainset_size: 40`).  
**Eval:** `exectv2_fixed_v1:validation` cap-25 (25 records).  
**Scorer (eval):** `exect_field_family_deterministic_v1` unchanged.

### Hygiene vs prior bootstrap pilot

| Control | Prior reject pilot | Thesis arms |
| --- | --- | --- |
| Prompt | v4_10 label policy | `l0_minimal` or `l1_schema` |
| Prediction bridges | `repair_policy=none` (inline) | `raw_no_benchmark_bridges` |
| Bootstrap compile metric | bridged micro F1 | **raw** micro F1 (`exect_field_family_micro_f1_raw`) for L0 bootstrap |

## Success / fail criteria (cap-25 eval)

| Outcome | Rule |
| --- | --- |
| **Thesis supported** | Any arm ≥ **93.0%** micro F1 on cap-25 (within **3 pp** of 95.8% hand-crafted ceiling) with no family > 3 pp below L1+policy reference |
| **Partial automation** | Beat L1 zero-shot (67.7%) by ≥ 10 pp but < 93% — demos help extraction, not full policy replacement |
| **Thesis rejected** | Plateau near L0–L1 band (≤ 75% micro) — compile cannot substitute for hand craft on this task |
| **Confound: scorer bridges** | Eval scorer still applies deterministic normalization; a “win” without prediction bridges may mean **scorer-side** alignment, not fully raw generalization — document in inspection |

## Interpretation branches

1. **L0+optimizer ≈ 95%** → pursue scalable compile-first ExECT/Gan workflows; revisit whether v4_10 prose can shrink; test holdout before production claims.
2. **L1+labeled beats L0+labeled but both << 95%** → schema + demos insufficient; policy/bridges remain necessary.
3. **L0+bootstrap ≈ L0+labeled** → demo selection method matters less than base prompt quality.
4. **L0+bootstrap beats L0+labeled** → teacher traces add signal under raw metric (compare to Gan ladder pattern).

## Known limitations (pre-declared)

- Train demos use **raw gold** labels (`make_exect_s0_s1_dspy_examples`), not benchmark-normalized surfaces — may cap compile ceiling.
- LabeledFewShot shows raw gold in demos while eval expects benchmark-facing surfaces after scorer — asymmetry noted in investigation §4.
- Generalization claim requires **full validation + test** confirmation if cap-25 passes; cap-25 is optimistic vs full 40.
- Inline bridges in production may encode benchmark-specific rules; automating via compile does not automatically transfer to new benchmarks without analogous train labels.

## Run order

1. Dry-run all three configs.
2. **L0 + LabeledFewShot** first (cheapest compile, cleanest signal).
3. **L0 + Bootstrap** second (uses raw compile metric).
4. **L1 + LabeledFewShot** third (schema + demos isolation).
5. Inspection `docs/exect_s1_ladder_optimizer_automation_inspection_<date>.md` after all three.

## Commands

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_full_ladder_l0_labeled_cap25_gpt4_1_mini.json --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_full_ladder_l0_bootstrap_cap25_gpt4_1_mini.json --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_full_ladder_l1_labeled_cap25_gpt4_1_mini.json --env-file .env --dry-run

uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_full_ladder_l0_labeled_cap25_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_full_ladder_l0_bootstrap_cap25_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_full_ladder_l1_labeled_cap25_gpt4_1_mini.json --env-file .env
```

## References (fixed anchors)

| Role | Micro F1 | Run / config |
| --- | ---: | --- |
| L0 zero-shot | 60.0% | `exect_s1_full_ladder_l0_cap25_gpt4_1_mini_20260521T003707Z` |
| L1 zero-shot | 67.7% | `exect_s1_full_ladder_l1_cap25_gpt4_1_mini_20260521T003924Z` |
| Hand-crafted cap-25 | 95.8% | `exect_s1_optimizer_baseline_cap25_gpt4_1_mini_20260521T000602Z` |
| v4_10 + bootstrap (reject) | 90.7% | `exect_s1_optimizer_bootstrap_cap25_gpt4_1_mini_20260521T000608Z` |
| L1+policy full | 92.3% | `exect_s1_full_ladder_l1_policy_full_gpt4_1_mini_20260521T004209Z` |
