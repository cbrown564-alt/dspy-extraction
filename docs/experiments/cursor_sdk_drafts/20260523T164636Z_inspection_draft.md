# Experiment Inspection Draft

**Topic:** G16 builder-gap full-validation reconciliation  
**Run pointer:** `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z`  
**Draft status:** Review-only. Not a source-of-truth decision doc. Do not cite for paper claims unless reconciled to primary run artifacts.

---

## Scope

| Field | Value |
| --- | --- |
| **Dataset** | Gan 2026 synthetic (`gan_2026`) |
| **Split** | `gan_2026_fixed_v1:validation` — 299 records (`data/splits/gan_2026_splits.json`; `configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation.json`) |
| **Model / provider** | GPT 4.1-mini / OpenAI, temperature 0.0 (`configs/models/gan_s0_gpt4_1_mini.json`) |
| **Schema level / field group** | `gan_frequency_s0`; primary gold `check__Seizure Frequency Number.seizure_frequency_number[0]` (`docs/policies/deterministic_scorer_semantics.md`, `docs/datasets/gan/gan_2026_label_audit.md`) |
| **DSPy program variant** | `gan_frequency_s0_temporal_candidates_single_pass` |
| **Prompt version** | `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy` |
| **Implementation variant (varied factor)** | `gan_s0_candidate_builder_gap_v1` |
| **Stage graph / executor** | `g2_candidates_adjudicate` / `det_candidates_llm_adjudicate` |
| **Hybrid class** | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates |
| **Scorer mode** | `gan_frequency_deterministic_v1` |
| **Normalization rules** | Lowercase/whitespace collapse; plural→singular units; `multiple`→3; range midpoints; cluster→monthly conversion; `unknown`→1000.0; seizure-free / no-reference→0.0 (`docs/policies/deterministic_scorer_semantics.md`) |
| **Evidence policy** | Diagnostic quote/offset support in note text (not Gan annotation overlap); repair `artifact_bridge_surface_normalization_only`; verifier `none` |
| **Run scope** | Full validation (299/299 scored); test split not reported (`report_on_test_split: false`) |
| **Decision scope (intended)** | `arm` — G16 confirmatory run per `docs/planning/kanban_plan.md`; not an operational-default change by itself |
| **Comparison group** | `gan_s0_candidate_builder_gap_v1` |
| **Evidence policy for this draft** | Primary artifacts only for metrics and candidate-emission claims; incident report used as secondary hypothesis, not standalone proof |

---

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
- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/experiments/gan/gan_s0_candidate_builder_gap_preregistration_20260523.md`
- `docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md`
- `docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.json`
- `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md`
- `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_full_validation_v1_inspection_20260521.md` (F0 control)
- `docs/experiments/gan/gan_s0_g16_candidate_builder_gap_incident_report.md` (secondary RCA)
- `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z/predictions.json` (G15 slice comparator)
- `docs/experiments/synthesis/experiment_registry.json` (slice row present; full-validation row absent)
- `src/clinical_extraction/gan/temporal_candidates.py` (current HEAD mapping check — post-run workspace)

**Missing / not discoverable:**

- Git commit SHA recorded in run metadata (**unknown**)
- Paired v1.4 **full-validation** control on the same 299 records (**not found** in configs/docs searched)
- Registry row for this full-validation run (**absent**; slice run is registered)

---

## Run Summary

### Primary run

| Field | Value | Source |
| --- | --- | --- |
| **Run ID** | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z` | `metadata.json` |
| **Experiment ID** | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation` | `config.json` |
| **Created** | 2026-05-23T16:15:24Z | `metadata.json` |
| **Records evaluated** | 299 / 299 valid scored (0 invalid, 0 missing within split) | `metrics.json`, error analysis |
| **Runtime** | ~323 s total; ~1.08 s/record; ~299 model calls | `metrics.json` |
| **Token usage** | 1,080,725 prompt + 12,820 completion | `metrics.json` |

### Metrics (valid predictions only; n=299)

| Metric | Accuracy | Correct | Role |
| --- | ---: | ---: | --- |
| **Monthly frequency** | **75.9%** | 227/299 | Benchmark-facing |
| **Purist category** | **81.3%** | 243/299 | Benchmark-facing |
| **Pragmatic category** | **85.6%** | 256/299 | Benchmark-facing |
| **Normalized-label exact** | 67.2% | 201/299 | Diagnostic |
| **Schema valid** | 100.0% | 299/299 | Diagnostic |
| **Evidence quote support** | 100.0% | 295/299 | Diagnostic (4 records with empty evidence spans) |

95% bootstrap CIs (`metrics.json`): monthly 71.2–80.9%; pragmatic 81.6–89.6%.

### Comparison controls

| Control | Run / source | Monthly | Purist | Pragmatic | Norm exact | Schema | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| **Operational F0 default** | `gan_s0_expanded_builders_prose_full_validation_gpt4_1_mini_20260521T073432Z` via `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_full_validation_v1_inspection_20260521.md` | 68.1% | 75.5% | 81.5% | 56.0% | 99.7% | Prompt `v1_1` + `cand_prose_expanded_builders_v1` — **not single-factor matched** |
| **v1.4 slice control** | `gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_4_slice_20260522T215246Z` via slice inspection | 36.0% | 44.0% | 56.0% | 28.0% | 100% | 25 enriched records only |
| **Builder-gap v1 slice (G15)** | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z` via slice inspection | 92.0% | 92.0% | 96.0% | 84.0% | 100% | Same prompt/model/scorer; enriched slice |
| **v1.4 full validation** | unknown | unknown | unknown | unknown | unknown | unknown | **Not located** |

**Deltas vs operational F0 (same 299-record split; interpretive framing only):** monthly **+7.8 pp**, purist **+5.8 pp**, pragmatic **+4.1 pp**, normalized exact **+11.2 pp**.

### Enriched 25-record replay inside this full run

Using preregistered IDs from `docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.json` replayed against `analysis/records.jsonl` and `predictions.json`:

| Metric | G15 slice run | Same 25 IDs in G16 full run |
| --- | ---: | ---: |
| Monthly accuracy | 92.0% (23/25) | **32.0% (8/25)** |
| Purist accuracy | 92.0% | **44.0% (11/25)** |
| Pragmatic accuracy | 96.0% | **48.0% (12/25)** |
| Records with **empty** `temporal_candidate_labels` | not applicable at slice scale | **19/25** |

### Slice vs full candidate-emission discrepancy (primary artifact)

For several enriched-slice records, identical note text (`prompt_note_text_char_count` matches) shows candidates on the slice run but **empty** candidates on this full run:

| Record | Slice candidates | Full candidates | Slice pred | Full pred |
| --- | --- | --- | --- | --- |
| `gan_13058` | `2 per 7 month` | `[]` | `2 per 7 month` | `1 per 3 week` |
| `gan_14792` | `1 per month` | `[]` | `1 per month` | `unknown` |
| `gan_15442` | `1 cluster per 4 day, 2 per cluster` | `[]` | correct cluster | `unknown` |

Sources: `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z/predictions.json` vs `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z/predictions.json`.

### Deterministic candidate diagnostics (full split)

- Gold label present in candidate set: **39/299 (13.0%)** (`docs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_error_analysis.md`)
- Leading benchmark-severe failure class: `other_semantic_mismatch` (26 scored misses)
- 13 pragmatic-only successes (pattern `0001`); 72 benchmark-severe misses overall
- Operational monthly failure rate: 24.1%; worst stratum `gold_pragmatic=infrequent` at 39.2% monthly

---

## Interpretation

### Facts (comparison group `gan_s0_candidate_builder_gap_v1`, full validation)

1. This run exceeds the documented operational F0 monthly anchor on the same split: **75.9% vs 68.1%** (`metrics.json`; F0 from `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_full_validation_v1_inspection_20260521.md`).
2. The G15 mechanism signal **does not replay** inside this run: enriched-slice monthly falls from **92.0% to 32.0%** on the same 25 record IDs.
3. Primary artifacts show a **candidate-emission gap**: 19/25 enriched IDs have empty `temporal_candidate_labels` in this full run despite non-empty candidates on the slice run for the same notes.
4. Full-split deterministic gold-in-candidates recall is **13.0% (39/299)**, far below the post-G13 no-model audit expectation of **23/25 on the enriched slice** (`docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md`).
5. Schema validity is perfect (100%); evidence quote support is 100% on 295/299 records with 4 no-evidence-span predictions on no-reference-type outputs (`metrics.json`).

### Interpretation (scoped; not paper evidence)

- **Aggregate lift vs F0 is confounded.** This arm uses the v1.4 error-taxonomy prompt; F0 uses v1.1 + prose expanded builders (`docs/planning/kanban_plan.md`, F0 inspection). The +7.8 pp monthly delta cannot be attributed cleanly to builder-gap v1 without a matched-prompt full-validation control.
- **This G16 artifact likely did not execute the same builder surface that passed G15.** The slice→full enriched replay and empty-candidate fields are consistent with the incident report’s hypothesis that `IMPLEMENTATION_VARIANT_TO_PRESENTATION` lacked `"gan_s0_candidate_builder_gap_v1"` at run time, disabling deterministic preconditioning (`docs/experiments/gan/gan_s0_g16_candidate_builder_gap_incident_report.md`). **Uncertainty:** run-time git SHA is not recorded in run metadata; RCA is secondary to prediction artifacts.
- **Beating F0 on monthly is an `arm`-scope signal worth review**, but it does not satisfy preregistered operational promotion logic and does not validate G13/G15 mechanism claims on full validation (`docs/experiments/gan/gan_s0_candidate_builder_gap_preregistration_20260523.md`; Kanban still lists F0 as operational default).
- **Mechanism closure remains `open`:** even where candidates exist, adjudication failures (`other_semantic_mismatch`, unknown-over-quantified, cluster collapse) dominate residual errors on the full split.

### Post-run workspace note (uncertainty boundary)

At inspection time on current HEAD:

- `src/clinical_extraction/gan/temporal_candidates.py` **now includes** `"gan_s0_candidate_builder_gap_v1": "prose"` (lines 21–28)
- `uv run pytest tests/test_gan_temporal_candidates.py` → **49 passed**
- `uv run python scripts/audit_gan_candidate_builder_gap.py` → **23/25** gold-in-candidates on enriched slice

This indicates recovery **after** the G16 run timestamp, not proof that G16 ran with the recovered code. **Do not treat current HEAD state as retroactive validation of this run.**

---

## Caveats

| Category | Caveat |
| --- | --- |
| **Scorer** | Unchanged `gan_frequency_deterministic_v1`; normalized-label exact is diagnostic only (`docs/policies/deterministic_scorer_semantics.md`). Seizure-free shape mismatches can be monthly/category-correct but normalized-wrong (15 `seizure_free_label_shape_mismatch` in error analysis). |
| **Dataset / gold** | Primary gold is `seizure_frequency_number[0]`; `reference[0]` is not gold (`docs/datasets/gan/gan_2026_label_audit.md`). Corpus includes `hard_case`, `row_ok`, and label-reference disagreement strata. |
| **Cap / full / test** | Full validation only; test split not reported. Enriched 25-record slice is diagnostic, not a performance estimator (`docs/experiments/gan/gan_s0_candidate_builder_gap_preregistration_20260523.md`). |
| **Comparison validity** | No v1.4 full-validation control on 299 records located. F0 comparison crosses prompt version and presentation. |
| **Run integrity** | Slice vs full candidate mismatch on identical records raises **`stale_check`** before any promote/hold decision. |
| **Registry / billing** | Full-validation run absent from `docs/experiments/synthesis/experiment_registry.json`; slice run is registered. ~1.09M prompt tokens on OpenAI (`metrics.json`). |
| **Incident context** | G13 code-loss and SDK rollback narrative in incident report is plausible but **not independently verified** via run metadata git SHA. |
| **Evidence policy** | 4/299 predictions lack evidence spans but remain schema-valid (`metrics.json`: e.g. `gan_11411`, `gan_11734`, `gan_11804`, `gan_11874`). |

---

## Decision Recommendation

**Recommendation: `needs-review` (with `rerun` as the likely next action).**

| Option | Rationale |
| --- | --- |
| **Do not promote** | Kanban F0 remains operational default; F0 comparison is confounded; `decision_scope` is `arm`, not `operational`. |
| **Do not reject-as-tested outright** | Aggregate monthly beats F0 anchor (+7.8 pp); schema/evidence gates pass — signal worth reconciling, not discarding. |
| **Do not hold silently** | Enriched replay (32% vs 92%) and candidate-emission mismatch undermine confidence that this run validates G13/G15. |
| **Prefer rerun after review** | Once builder parity with G15 is confirmed (mapping + passing tests + non-empty candidates on enriched IDs), rerun `configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation.json`. |

**Decision scopes:**

| Scope | Status |
| --- | --- |
| `operational` | **blocked** — F0 remains default per Kanban; confounded F0 comparison |
| `arm` | **open / needs-review** — aggregate metrics favorable; mechanism artifact inconsistent |
| `mechanism` | **open** — candidate recall low on full split in this artifact; adjudication failures dominate |
| `stale_check` | **flagged** — slice vs full candidate mismatch; run may not reflect intended implementation variant |
| `blocked` | Qwen transfer remains blocked until trustworthy GPT full validation (`docs/planning/kanban_plan.md`, preregistration model gate) |

---

## Required Human Checks

1. **Verify builder parity:** Diff `temporal_candidate_labels` for all 25 enriched IDs between slice run `...093314Z` and full run `...161524Z`; confirm whether G13 builders were active at full-run time.
2. **Confirm code state at run time:** Identify git commit for slice run, full run, and current HEAD; reconcile with incident report timeline.
3. **Re-run no-model audit on accepted commit:** `uv run python scripts/audit_gan_candidate_builder_gap.py` — expect 23/25 if G13 intact (`docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md`).
4. **Confirm tests on accepted commit:** `uv run pytest tests/test_gan_temporal_candidates.py` — expect pass before any rerun billing.
5. **Add missing control (recommended):** v1.4 no-example **full validation** on the same 299 records to isolate prompt vs builder effects.
6. **Registry hygiene:** Add full-validation inspection row to `docs/experiments/synthesis/experiment_registry.json` with `decision_scope: arm`, canonical run ID, and metric caveats — **only after human accepts/rejects this draft**.
7. **Inspect enriched-slice regressions:** Manually review `gan_13058`, `gan_13149`, `gan_14792`, `gan_14821`, `gan_15442`, `gan_15168`, `gan_15193` in `analysis/records.jsonl` and `predictions.json`.
8. **Evidence edge cases:** Confirm whether 4 no-span “no seizure frequency reference” predictions are acceptable under current evidence policy.
9. **Do not use this draft for paper claims** until primary run artifacts are reconciled and, if needed, superseded by a verified rerun with recorded commit SHA.