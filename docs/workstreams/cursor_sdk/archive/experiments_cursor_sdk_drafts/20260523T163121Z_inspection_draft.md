# Experiment Inspection Draft

## Scope

| Field | Value |
| --- | --- |
| **Dataset** | Gan 2026 synthetic (`gan_2026`) |
| **Split** | `gan_2026_fixed_v1:validation` — 299 records (`data/splits/gan_2026_splits.json`) |
| **Model / provider** | GPT 4.1-mini / OpenAI (`configs/models/gan_s0_gpt4_1_mini.json`; temperature 0.0) |
| **Schema level / field group** | `gan_frequency_s0` — primary gold `check__Seizure Frequency Number.seizure_frequency_number[0]` |
| **DSPy program variant** | `gan_frequency_s0_temporal_candidates_single_pass` |
| **Prompt version** | `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy` |
| **Implementation variant (varied factor)** | `gan_s0_candidate_builder_gap_v1` |
| **Stage graph / executor** | `g2_candidates_adjudicate` / `det_candidates_llm_adjudicate` (`configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation.json`) |
| **Hybrid class** | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates |
| **Scorer mode** | `gan_frequency_deterministic_v1` |
| **Normalization rules** | Per `docs/policies/deterministic_scorer_semantics.md`: lowercase/whitespace collapse; plural→singular units; `multiple`→3; range midpoints; cluster→monthly rate conversion; `unknown`→1000.0; seizure-free / no-reference→0.0 |
| **Evidence policy** | Diagnostic quote/offset support in note text (not Gan annotation overlap); repair policy `artifact_bridge_surface_normalization_only`; verifier `none` |
| **Run scope** | Full validation (299/299 scored); not test split (`report_on_test_split: false`) |
| **Decision scope (intended)** | `arm` — confirmatory G16 run; not an operational-default change by itself (`docs/planning/kanban_plan.md` G16) |
| **Comparison group** | `gan_s0_candidate_builder_gap_v1` |

## Sources Read

- `configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation.json`
- `configs/models/gan_s0_gpt4_1_mini.json`
- `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z/config.json`
- `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z/metadata.json`
- `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z/metrics.json`
- `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z/predictions.json`
- `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z/analysis/summary.json`
- `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z/analysis/records.jsonl`
- `docs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_error_analysis.md`
- `docs/templates/experiment_decision_template.md`
- `docs/planning/kanban_plan.md` (G11–G16, operational defaults)
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/deterministic_foundation_decisions.md`
- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/experiments/gan/gan_s0_candidate_builder_gap_preregistration_20260523.md`
- `docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md`
- `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md`
- `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_full_validation_v1_inspection_20260521.md` (F0 control)
- `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z/predictions.json` (slice comparator)
- `docs/experiments/synthesis/experiment_registry.json` (no row for this run — checked by pattern search)

**Missing / not read:** paired v1.4 **full-validation** control run on the same 299 records; registry row for this run; `docs/policies/deterministic_scorer_semantics.md` does not define builder-gap-specific semantics (expected — scorer unchanged).

## Run Summary

### Primary run

| Field | Value |
| --- | --- |
| **Run ID** | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z` |
| **Experiment ID** | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation` |
| **Created** | 2026-05-23T16:15:24Z |
| **Records evaluated** | 299 / 299 valid scored (0 invalid, 0 missing within split) |
| **Runtime** | ~323 s total; ~1.08 s/record prediction; ~299 model calls |
| **Token usage** | 1,080,725 prompt + 12,820 completion (`metrics.json`) |

### Metrics (valid predictions only; 299 denominator)

| Metric | This run | Count | Role |
| --- | ---: | ---: | --- |
| **Monthly frequency** | **75.9%** | 227/299 | Benchmark-facing |
| **Purist category** | **81.3%** | 243/299 | Benchmark-facing |
| **Pragmatic category** | **85.6%** | 256/299 | Benchmark-facing |
| **Normalized-label exact** | 67.2% | 201/299 | Diagnostic |
| **Schema valid** | 100.0% | 299/299 | Diagnostic |
| **Evidence quote support** | 100.0% | 295/299 | Diagnostic (4 records with empty evidence spans) |

95% bootstrap CIs (from `metrics.json`): monthly 71.2–80.9%; pragmatic 81.6–89.6%.

### Comparison controls (same split unless noted)

| Control | Run / source | Monthly | Purist | Pragmatic | Norm exact | Schema | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| **Operational F0 default** | `gan_s0_expanded_builders_prose_full_validation_gpt4_1_mini_20260521T073432Z` per `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_full_validation_v1_inspection_20260521.md` | 68.1% | 75.5% | 81.5% | 56.0% | 99.7% | Different prompt (`v1_1` + prose) and `cand_prose_expanded_builders_v1` — **not a single-factor arm match** |
| **v1.4 slice control** | `gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_4_slice_20260522T215246Z` per slice inspection | 36.0% | 44.0% | 56.0% | 28.0% | 100% | 25-record enriched slice only |
| **Builder-gap v1 slice** | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z` per `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md` | 92.0% | 92.0% | 96.0% | 84.0% | 100% | Same prompt/model/scorer; 25 enriched records |
| **v1.4 full validation** | unknown | unknown | unknown | unknown | unknown | unknown | **Not found** in configs/docs searched |

**Deltas vs operational F0 (interpretation only):** monthly **+7.8 pp**, purist **+5.8 pp**, pragmatic **+4.1 pp**, normalized exact **+11.2 pp**, schema **+0.3 pp** (299/299 vs 298/299 valid).

### Enriched 25-record replay inside this full run

Using the preregistered enriched-slice ID set from `docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md` and `runs/.../analysis/records.jsonl`:

| Metric | Slice run (G15) | Same 25 IDs in this full run |
| --- | ---: | ---: |
| Monthly accuracy | 92.0% (23/25) | **32.0% (8/25)** |
| Candidate gold coverage (no-model audit) | 23/25 | 13.0% split-wide gold-in-candidates (39/299) per error analysis |

### Deterministic candidate diagnostics

- Gold label present in candidate set: **39/299 (13.0%)** (`docs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_error_analysis.md`).
- Leading benchmark-severe failure class: `other_semantic_mismatch` (26 scored misses).
- 13 **pragmatic-only** successes (pattern `0001`); 72 benchmark-severe misses overall.
- Operational failure rate (monthly): 24.1% overall; worst stratum `gold_pragmatic=infrequent` at 39.2% monthly.

### Slice vs full candidate-emission discrepancy (primary artifact)

For several enriched-slice records, **the same note** (matching `prompt_note_text_char_count`) shows candidates on the slice run but **empty** `temporal_candidate_labels` on this full run:

| Record | Slice candidates | Full candidates | Slice pred | Full pred |
| --- | --- | --- | --- | --- |
| `gan_13058` | `2 per 7 month` | `[]` | `2 per 7 month` | `1 per 3 week` |
| `gan_14792` | `1 per month` | `[]` | `1 per month` | `unknown` |
| `gan_14821` | `1 per month` | `[]` | `1 per month` | `unknown` |
| `gan_15442` | `1 cluster per 4 day, 2 per cluster` | `[]` | correct cluster | `unknown` |

Sources: `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z/predictions.json` vs `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z/predictions.json`.

## Interpretation

**Facts (comparison group `gan_s0_candidate_builder_gap_v1`, full validation):**

1. This run exceeds the documented operational F0 monthly anchor (75.9% vs 68.1%) on the same 299-record split (`metrics.json`; F0 from `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_full_validation_v1_inspection_20260521.md`).
2. The aggregate lift does **not** reproduce the G15 slice mechanism signal on the same enriched 25 records: monthly falls from 92.0% to 32.0% when those IDs are evaluated inside this run.
3. Primary artifacts show a **candidate-emission gap** between the slice and full runs for key enriched records, with full-run predictions reverting toward v1.4-like outputs when candidates are absent (e.g. `gan_13058`: `1 per 3 week`).
4. Full-split deterministic recall remains low (13.0% gold-in-candidates), so most errors are still not candidate-recall-limited on this run.
5. Schema validity is perfect (100%); evidence quote support is 100% on 295/299 records with 4 no-evidence-span predictions on “no seizure frequency reference”-type outputs (`metrics.json` error examples).

**Interpretation (scoped to comparison group; not paper evidence):**

- The aggregate monthly gain vs F0 is **confounded**: this arm uses the v1.4 error-taxonomy prompt, while F0 uses v1.1 + prose presentation (`docs/planning/kanban_plan.md`, F0 inspection). The lift cannot be attributed cleanly to builder-gap v1 alone without a matched-prompt control or a v1.4 full-validation baseline.
- The slice→full regression on enriched IDs, combined with empty `temporal_candidate_labels` in full-run predictions, suggests this full-validation artifact may **not** represent the same builder surface that passed G15, rather than a benign generalization story alone. **Uncertainty:** code state at run time vs current workspace was not fully reconstructed; see caveats.
- Beating F0 on monthly is an **`arm`-scope** signal worth review, but it does not meet preregistered promotion logic for operational default change (`docs/experiments/gan/gan_s0_candidate_builder_gap_preregistration_20260523.md`; Kanban still lists F0 as operational default).
- Mechanism closure remains **`open`**: even when candidates exist, adjudication still fails (`other_semantic_mismatch`, unknown-over-quantified, cluster collapse).

## Caveats

| Category | Caveat |
| --- | --- |
| **Scorer** | Unchanged `gan_frequency_deterministic_v1`; normalized-label and raw exact are diagnostic only (`docs/policies/deterministic_scorer_semantics.md`). Seizure-free shape mismatches can be monthly/category-correct but normalized-wrong (15 `seizure_free_label_shape_mismatch` in error analysis). |
| **Dataset / gold** | Primary gold is `seizure_frequency_number[0]`; `reference[0]` is not gold (`docs/datasets/gan/gan_2026_label_audit.md`). 197/1446 clinical records have label-reference disagreement corpus-wide; stratification includes `hard_case`, `row_ok`. |
| **Cap / full / test** | Full validation only; test split not reported. Enriched 25-record slice is a diagnostic search surface, not a performance estimator (`docs/experiments/gan/gan_s0_candidate_builder_gap_preregistration_20260523.md`). |
| **Comparison validity** | No v1.4 full-validation control on 299 records located. F0 comparison crosses prompt version and presentation (`v1_1` prose vs `v1_4` no-example). |
| **Run integrity** | Slice vs full candidate mismatch on identical records raises a **stale_check / rerun** flag before any promote/hold decision. |
| **Registry / billing** | Run not present in `docs/experiments/synthesis/experiment_registry.json`. ~1.09M tokens on OpenAI for this run (`metrics.json`). |
| **Workspace drift (uncertainty)** | At inspection time, `tests/test_gan_temporal_candidates.py` reports **12 failing** builder-gap-related tests (including `test_enriched_gap_slice_gold_label_coverage_improves`). This was not the run-time environment on 2026-05-23 and may or may not explain the slice/full artifact gap — **needs human verification**. |
| **Evidence policy** | 4/299 predictions lack evidence spans but still score as valid schema (`metrics.json`). |

## Decision Recommendation

**Recommendation: `needs-review` (with `rerun` as the likely next action).**

**Rationale:**

- **Do not promote** to operational default: Kanban F0 remains default; comparison to F0 is confounded by prompt/version differences; `decision_scope` is `arm`, not `operational` (`docs/planning/kanban_plan.md`).
- **Do not reject-as-tested** outright: aggregate monthly **does** beat the F0 anchor (+7.8 pp), and schema/evidence gates pass — there is a signal worth reconciling.
- **Do not hold silently**: the enriched-slice replay (32% vs 92%) and slice/full candidate-emission mismatch undermine confidence that this run validates G13/G15 mechanism claims.
- **`rerun` preferred after review** if builder parity with the slice run can be confirmed (same commit, passing `tests/test_gan_temporal_candidates.py`, matching `temporal_candidate_labels` on enriched IDs).

**Decision scopes:**

| Scope | Status |
| --- | --- |
| `operational` | **blocked** — F0 remains default per Kanban; confounded F0 comparison |
| `arm` | **open / needs-review** — aggregate metrics favorable; mechanism artifact inconsistent |
| `mechanism` | **open** — candidate recall still low on full split; adjudication failures dominate |
| `stale_check` | **flagged** — slice vs full candidate mismatch |
| `blocked` | Qwen transfer still blocked until GPT validation is trustworthy (`docs/planning/kanban_plan.md`) |

## Required Human Checks

1. **Verify builder parity:** Diff `temporal_candidate_labels` in predictions for all 25 enriched IDs between slice run `...093314Z` and this full run `...161524Z`; confirm whether G13 builders were active at full-run time.
2. **Confirm code state:** Identify git commit used for each run; reconcile with current failing `tests/test_gan_temporal_candidates.py` (12 failures at inspection).
3. **Re-run no-model audit:** `uv run python scripts/audit_gan_candidate_builder_gap.py` on current HEAD; expect 23/25 coverage if G13 is intact (`docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md`).
4. **Add missing control (optional but recommended):** v1.4 no-example **full validation** on the same 299 records to isolate prompt vs builder effects.
5. **Registry hygiene:** Add inspection row to `docs/experiments/synthesis/experiment_registry.json` with `decision_scope: arm`, canonical run ID, and metric caveats — only after human accepts/rejects this draft.
6. **Promotion gate check vs F0:** If rerun confirms builders, re-evaluate monthly/purist/pragmatic against F0 with explicit note that prompt versions differ; do not treat as operational promotion without matched controls.
7. **Inspect enriched-slice regressions:** Manually review `gan_13058`, `gan_13149`, `gan_14792`, `gan_14821`, `gan_15442`, `gan_15168`, `gan_15193` in `analysis/records.jsonl` and `predictions.json`.
8. **Evidence edge cases:** Confirm whether 4 no-span “no seizure frequency reference” predictions are acceptable under current evidence policy (`metrics.json` examples `gan_11411`, `gan_11734`, `gan_11804`, `gan_11874`).
9. **Do not use this draft for paper claims** until primary run artifacts are reconciled and, if needed, superseded by a verified rerun.