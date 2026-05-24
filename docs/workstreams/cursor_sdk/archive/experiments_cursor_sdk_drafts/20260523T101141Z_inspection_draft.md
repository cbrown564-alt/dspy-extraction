# Experiment Inspection Draft

## Scope

| Field | Value |
| --- | --- |
| **Dataset** | `gan_2026` (`data/Gan (2026)/synthetic_data_subset_1500.json`) |
| **Split** | `gan_2026_fixed_v1:validation`, restricted to a fixed 25-record enriched slice (`data/splits/gan_2026_splits.json`) |
| **Model / provider** | GPT 4.1-mini / OpenAI (`configs/models/gan_s0_gpt4_1_mini.json`) |
| **Schema level / field group** | `gan_frequency_s0`; primary gold `check__Seizure Frequency Number.seizure_frequency_number[0]` |
| **DSPy program variant** | `gan_frequency_s0_temporal_candidates_single_pass` |
| **Prompt version** | `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy` (held fixed vs control) |
| **Stage graph / executor** | `g2_candidates_adjudicate` / `det_candidates_llm_adjudicate` |
| **Hybrid class** | `H2_pre_deterministic`, `H4_deterministic_first_llm_adjudicates` |
| **Scorer mode** | `gan_frequency_deterministic_v1` |
| **Normalization rules** | Per `docs/policies/deterministic_scorer_semantics.md`: lowercase/whitespace collapse, plural→singular units, `multiple`→3, range midpoint, monthly rate conversion, cluster multiplication, `unknown`→1000.0, seizure-free/no-reference→0.0 |
| **Evidence policy** | Diagnostic quote/offset support in note text; not overlap with Gan evidence annotations (`metrics.json` caveats) |
| **Comparison group** | `gan_s0_candidate_builder_gap_v1` |
| **Varied factor** | `implementation_variant` = `gan_s0_candidate_builder_gap_v1` deterministic candidate builders in `src/clinical_extraction/gan/temporal_candidates.py` |
| **Run scope** | 25-record diagnostic slice only; `report_on_test_split: false`; not cap25/full validation |
| **Decision scope (this draft)** | **arm** (implementation variant vs v1.4 control on fixed slice); **mechanism** signal (candidate recall as binding constraint); **operational** default unchanged pending broader validation |

**Unknown / not in run artifacts:** full-validation or cap-style metrics; Qwen transfer results; billing reconciliation beyond token counts in run metadata.

---

## Sources Read

- `docs/templates/experiment_decision_template.md`
- `docs/planning/kanban_plan.md` (G11–G16 cards, recommended next pull)
- `docs/policies/deterministic_scorer_semantics.md` (Gan 2026 section)
- `docs/datasets/gan/gan_2026_label_audit.md` (gold source, label taxonomy)
- `docs/experiments/gan/gan_s0_candidate_builder_gap_preregistration_20260523.md`
- `docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md`
- `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md` (prior inspection; not treated as primary evidence here)
- `docs/experiments/gan/gan_s0_policy_pipeline_learning_log.md` (G11–G15 entries)
- `configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice.json`
- `configs/experiments/gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_4_slice.json` (control config pointer)
- `configs/models/gan_s0_gpt4_1_mini.json`
- `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z/config.json`
- `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z/metadata.json`
- `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z/metrics.json`
- `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z/errors.json`
- `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z/predictions.json` (spot-check only)
- `runs/gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_4_slice_20260522T215246Z/metrics.json` (control)

**Not read (missing from supplied pointer):** `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z/prompts.json`; post-run pytest / `validate_primitives` / audit script outputs from the G14 no-model gate.

---

## Run Summary

### Primary run

| Field | Value |
| --- | --- |
| **Run ID** | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z` |
| **Experiment ID** | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice` |
| **Created** | 2026-05-23T09:33:14Z |
| **Artifact root** | `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z/` |
| **Records evaluated** | 25 / 25 valid predictions; 0 invalid |

### Comparison control

| Field | Value |
| --- | --- |
| **Control run ID** | `gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_4_slice_20260522T215246Z` |
| **Control config** | `configs/experiments/gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_4_slice.json` |
| **Held fixed** | Same 25 `record_ids`, prompt, model, context/repair/abstention policies, scorer, structured output strategy |

### No-model gate (pre-run, from audit / preregistration)

| Metric | Baseline | Builder-gap v1 | Source |
| --- | ---: | ---: | --- |
| Exact gold in deterministic candidates | 5/25 (20%) | 23/25 (92%) | `docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md`; preregistration acceptance criteria |

Uncovered no-model families: `seizure_free_over_unknown` for `gan_13574`, `gan_13598` (preregistered exclusion).

### Benchmark metrics (25-record slice)

| Metric | v1.4 control | Builder-gap v1 | Delta | 95% CI (builder-gap) |
| --- | ---: | ---: | ---: | --- |
| Monthly frequency accuracy | 36.0% | **92.0%** | +56.0 pp | 0.80–1.00 |
| Pragmatic category accuracy | 56.0% | **96.0%** | +40.0 pp | 0.88–1.00 |
| Purist category accuracy | 44.0% | **92.0%** | +48.0 pp | 0.80–1.00 |
| Normalized-label accuracy (diagnostic) | 28.0% | **84.0%** | +56.0 pp | 0.68–0.96 |
| Raw exact accuracy (diagnostic) | 28.0% | **84.0%** | +56.0 pp | 0.68–0.96 |
| Schema valid prediction rate | 100% | 100% | 0 | 1.00–1.00 |
| Evidence quote support rate | 100% | 100% | 0 | 1.00–1.00 |

Sources: `runs/.../metrics.json` for both runs.

### Error counts (builder-gap run)

From `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z/metrics.json`:

- Monthly frequency mismatches: **2** (`gan_15168`, `gan_15193`)
- Pragmatic category mismatches: **1** (`gan_15168`)
- Purist category mismatches: **2** (`gan_15168`, `gan_15193`)
- Normalized-label mismatches: **4** (includes 2 seizure-free records)
- `schema.missing_prediction: 1475` reflects full-dataset gold count vs 25-record slice scope, not run failure

### Runtime / cost (facts)

- Prediction: ~28.5 s total; ~1.14 s/record; 25 model calls
- Tokens: 50,380 prompt + 1,080 completion = 51,460 total
- Source: `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z/metrics.json` → `runtime`

### Rescue pattern (interpretive summary backed by primary artifacts)

14 records that missed monthly frequency under v1.4 control were corrected under builder-gap v1, including quantified windows, cluster label `gan_15442`, and several prior `unknown` predictions. Record-level rescue table is in `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md`; primary verification should use paired `predictions.json` from both runs.

### External baseline not in comparison group

Kanban states F0 expanded builders + prose remains the **operational full-validation default** at **68.1%** monthly on full validation (`docs/planning/kanban_plan.md`). That run is **not** part of this slice comparison and was **not** re-read here.

---

## Interpretation

**Facts (comparison group: builder-gap v1 vs v1.4 control, same enriched 25-record slice, GPT 4.1-mini, fixed prompt/scorer):**

1. Preregistered no-model coverage gate passed (23/25 > 5/25).
2. Model gate passed on all benchmark-facing metrics with large deltas (+40 to +56 pp).
3. Schema validity and evidence grounding did not regress (both 100%).
4. Residual failures concentrate in **vague-multiple adjudication** (`gan_15168`, `gan_15193`) where candidates are now present but the model abstained or undercounted.
5. Two **seizure-free** records remain normalized-label mismatches but are monthly/category-correct under current scorer semantics (both map to no-seizure-information monthly rate 0.0).

**Interpretation (scoped, not paper-grade):**

Within this **enriched diagnostic slice**, incomplete deterministic candidate recall—not prompt, verifier, or model track—was likely the dominant upstream bottleneck for v1.4. Expanding builders to include exact gold labels for 23/25 records translated into adjudication lift when the same GPT prompt and model selected from the enriched candidate surface. This supports a **mechanism hypothesis** that `g2_candidates_adjudicate` arms are candidate-recall-limited on hard temporal patterns, but it does **not** close the mechanism (only one builder variant, one model, one slice).

**Uncertainty:**

- Slice was selected from Qwen pragmatic-category mismatches (`config.json` metric caveats; preregistration research caveat)—lift may not generalize.
- Builders are regex-style, phrase-tied helpers; broader validation may expose overfitting or new failure modes.
- Whether builder-gap v1 beats or complements F0 expanded builders on full validation is **unknown** from this run.

---

## Caveats

### Scorer / metrics

- Primary benchmark gold is `seizure_frequency_number[0]` only; `reference[0]` is secondary (`docs/datasets/gan/gan_2026_label_audit.md`, `docs/policies/deterministic_scorer_semantics.md`).
- Normalized-label and raw exact are **diagnostic**, not benchmark-facing, unless an experiment explicitly targets Label Scheme reproduction.
- Evidence metrics check deterministic quote/offset support in note text, not Gan annotation overlap.

### Dataset / split

- 25-record enriched slice is a **search/diagnostic surface**, not a full-validation estimate (preregistration; run `metric_caveats`).
- Slice enrichment bias toward Qwen pragmatic failures may inflate apparent lift vs population validation split.
- `counts.gold_records: 1500` and missing-prediction error bucket are artifacts of scorer evaluating against full gold file while predicting only 25 IDs.

### Cap / full / test

- This is neither cap25 nor full validation; `validation_ladder_rung: null` in config.
- Test split not reported (`report_on_test_split: false`).

### Validation / promotion boundaries

- Qwen transfer explicitly **blocked** until GPT slice beats v1.4 or a preregistered transferability question is answered (preregistration model gate; kanban G15/G16).
- Operational Gan default remains F0 expanded builders + prose until G16 broader GPT validation (`docs/planning/kanban_plan.md`).

### Implementation / stale checks

- Seizure-free `multiple year` boundary deliberately excluded from builders (preregistration); residual normalized-label misses expected there.
- Post-run test/audit command success for G14 not independently verified in this draft.
- Prior inspection doc exists at `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md`; reconcile before treating as canonical.

### Billing

- Token usage recorded; dollar cost not in run artifacts.

---

## Decision Recommendation

**promote** — scoped to the **arm / enriched-slice gate** for `gan_s0_candidate_builder_gap_v1` vs v1.4 control.

**Rationale:**

- Preregistered acceptance criteria met: no-model coverage 23/25 > 5/25; GPT slice beats v1.4 on all benchmark metrics with no schema/evidence regression.
- Kanban G15 outcome aligns with pass at enriched-slice gate (`docs/planning/kanban_plan.md`).
- Provides a strong **mechanism signal** for candidate-recall work without claiming full-validation or operational superiority.

**Explicit non-promotions (same recommendation, different scopes):**

| Scope | Status | Rationale |
| --- | --- | --- |
| **operational** | **hold** | F0 full-validation default unchanged; G16 broader GPT validation required |
| **mechanism closure** | **open** | Single implementation variant on biased slice; LLM candidate / verifier mechanisms not closed |
| **Qwen transfer** | **blocked** | Preregistration and kanban block until broader GPT validation |
| **paper claims** | **needs-review** | Slice n=25; cite primary run artifacts only |

Do **not** **reject-as-tested** — the variant clearly beat the preregistered control. Do **not** **rerun** the same slice unless artifact integrity is questioned.

---

## Required Human Checks

Before promoting this draft into `docs/experiments/` as a canonical inspection/decision note:

1. **Pairwise prediction audit:** Confirm all 14 claimed rescues by diffing `predictions.json` between builder-gap and v1.4 control runs (do not rely solely on the prior inspection table).
2. **Residual error review:** Manually inspect `gan_15168`, `gan_15193`, `gan_13574`, `gan_13598` notes and candidate surfaces in `predictions.json` to classify as adjudication vs builder vs policy-boundary failures.
3. **No-model gate reconfirmation:** Re-run or verify logs for `uv run pytest tests/test_gan_temporal_candidates.py`, `scripts/validate_primitives.py --errors-only`, and `scripts/audit_gan_candidate_builder_gap.py` at the commit tied to this run.
4. **Decision scope labeling:** Mark decision as **arm** (enriched-slice pass) and **mechanism signal** (candidate recall); explicitly **hold operational** default until G16.
5. **G16 planning:** Specify broader validation config (full validation vs cap sample), comparison arms (builder-gap v1 vs F0 expanded builders + prose vs v1.4), and regression guardrails from kanban.
6. **Scorer/dataset invariants:** Confirm no edits to `frequency.py`, `scoring.py`, or benchmark metric semantics since preregistration (git diff vs G12 baseline).
7. **Duplicate-doc reconciliation:** Decide whether this supersedes, merges with, or references `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md`.
8. **Kanban update:** If accepted, update G15/G16 card status and learning log only through the normal human review path—not from this draft alone.
9. **Bootstrap / n=25 caveat:** Ensure any promoted doc states 95% CIs are wide (e.g., monthly lower bound 0.80) and discourages over-interpretation.
10. **Billing sign-off:** Optional cost check against OpenAI usage for ~51k tokens on 25 records if budget tracking is required.

---

*Draft only. Not canonical evidence. Primary artifacts: `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z/` and preregistration/audit docs cited above.*