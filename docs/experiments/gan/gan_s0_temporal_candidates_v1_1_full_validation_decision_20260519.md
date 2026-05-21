# Gan S0 Temporal-Candidates v1.1 Full Validation — Promotion Decision

Date: 2026-05-19  
Status: **Tier 1 — Promote** (full validation complete `…230324Z`)

## Purpose

Assign promotion tier for `gan_frequency_s0_temporal_candidates_verify_repair_v1_1` after the full Gan validation run completes, using a pre-registered packet (grill-with-docs 2026-05-19).

## Taxonomy

- **Dataset:** gan_2026
- **Schema complexity:** gan_s0
- **Clinical task family:** frequency
- **Hybrid balance class:** H2_pre_deterministic, H4_deterministic_first_llm_adjudicates
- **Interleaving positions:** pre, during, post
- **Varied factor:** program_architecture
- **Comparison group:** gan_s0_architecture_qwen_validation_v1
- **Outcome:** promote

## Artifacts

| Role | Path |
| --- | --- |
| Candidate run | `runs/gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T230324Z` |
| Config | `configs/experiments/gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails.json` |
| Qwen direct anchor | `runs/gan_s0_qwen35b_direct_full_validation_guardrails_20260519T102249Z` |
| Hosted quality anchor | `runs/gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z` |
| Slice fixture | `data/fixtures/gan_s0_qwen_error_regression_slice.json` |
| Cap-25 gate | `runs/gan_s0_qwen35b_temporal_candidates_verify_repair_cap25_guardrails_validation_20260519T183213Z` |

## Promotion tiers (pre-registered)

| Tier | Condition | Action |
| --- | --- | --- |
| **1 — Promote** | Full validation monthly ≥ Qwen direct full (~55.9%), or within ~1pp if schema ≥ 99% and evidence ≥ 99.5% | Default local Qwen Gan S0 path; update kanban Session Handoff |
| **2 — Specialist** | Monthly between cap-25 direct (~37.5%) and full direct, **and** slice B + strata C show infrequent/regression wins without E regressions | Keep variant documented; next engineering = B1 (expand `temporal_candidates.py`) |
| **3 — Pivot** | Monthly ≤ cap-25 temporal (~44%) or E violations at scale | No promote; B2 model event table before ReAct/hosted port |

**E regression guard (veto / tier 3):** wrong YTD, stripped cluster, `unknown`→`no reference`, short seizure-free — shapes from `docs/experiments/gan/gan_s0_temporal_candidate_pivot_20260519.md`.

**Engineering fork after tier 2/3:** B1 regex candidates → B2 model event table → ReAct bounded probe → hosted GPT port of guards (only after local tier 1 or tier 2 with slice B re-cleared).

## Parallel work (pre-tier)

**ExECT (Track B):** Hosted GPT 4.1-mini label-policy iteration runs **in parallel** with this Gan full validation — see `docs/planning/kanban_plan.md` § Execution Model and `docs/planning/research_drift_audit_20260519.md` § Parallel ExECT Work. v4.2 is the current ExECT anchor (`…202626Z`, 78.5% micro F1 full). Cap-25 remains diagnostic only; no section-aware promotion; no scorer changes.

**Blocked until Gan tier signed:** B1/B2/ReAct/**hosted Gan** port; **Gan** prompt edits unrelated to candidate policy; GEPA; Gemini verify-repair scale-up; gold-ambiguity implementation.

## Promotion packet checklist

- [x] **A** — Full-split analyzer markdown (299 records)
- [x] **B** — Same run, 14-record slice via `--record-ids-file` (failure_mode breakdown)
- [x] **C** — Stratified table: `gold_pragmatic=infrequent`, `hard_case`, invalid/abstain
- [x] **D** — Anchor comparison table (this doc § Headline metrics)
- [x] **E** — Full-split regression guard checklist (verifier repair failure shapes)
- [x] **F** — Defer hosted port / ReAct / GEPA until tier ≥ 2 on slice B

### E regression guard spot-check (2026-05-20)

All 14 regression-slice records replayed from full validation (`…230324Z`) with **all_metrics_match** — no E-regression veto:

| Failure mode | Records | Full-split result |
| --- | --- | --- |
| unknown_vs_no_reference | `gan_10509`, `gan_10751`, `gan_11221` | gold `unknown` preserved |
| no_clinical_content_null_output | `gan_11733` | gold `no seizure frequency reference` |
| year_to_date_denominator | `gan_12810` | `5 per 2 month` |
| highest_current_quantified_frequency | `gan_12130`, `gan_12823` | `multiple per week`, `9 per month` |
| incomplete_cluster_label | `gan_10052` | full cluster surface preserved |
| cluster_multiplier_preservation | `gan_10003` | `multiple per cluster` preserved |
| short_seizure_free_threshold | `gan_10410` | `1 cluster per week, 3 to 4 per cluster` (not short seizure-free) |
| infrequent_quantified_over_unknown | 4 records | 4/4 monthly |

Full-split residual E-adjacent shapes (outside regression slice) are diagnostic-only (`seizure_free_label_shape_mismatch`, `seizure_free_to_no_reference_monthly_match`) or isolated (`unknown_vs_seizure_free` ×1) — not veto-level on the pre-registered slice.

## Commands (run when predictions complete)

```powershell
$run = "runs/gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T183614Z"

# A — full split
uv run python scripts/analyze_gan_frequency_run.py $run `
  --split-name gan_2026_fixed_v1:validation `
  --markdown docs/experiments/gan/gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_error_analysis.md

# B — 14-record regression slice from same artifacts
uv run python scripts/analyze_gan_frequency_run.py $run `
  --split-name gan_2026_fixed_v1:validation `
  --record-ids-file data/fixtures/gan_s0_qwen_error_regression_slice.json `
  --markdown docs/experiments/gan/gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_from_full_validation_error_analysis.md
```

## Headline metrics (fill after A–F)

| Metric | Temporal v1.1 full | Qwen direct full `…102249Z` | GPT verify-repair `…084732Z` |
| --- | ---: | ---: | ---: |
| Records analyzed | 299 (298 valid) | 299 | 299 |
| Schema-valid rate | 99.7% | 94.0% | 96.7% |
| Monthly-frequency accuracy | **65.8%** | 55.9% | 65.4% |
| Purist category accuracy | **75.5%** | 61.9% | 72.7% |
| Pragmatic category accuracy | **82.6%** | 70.5% | 79.2% |
| Evidence quote support | **100.0%** | 99.6% | 92.7% |

## Slice replay (fill after B)

| Stratum | Target | Result |
| --- | --- | --- |
| Original policy/cluster rows (10) | 10/10 monthly | **10/10** |
| Infrequent quantified (4) | ≥3/4 monthly (gate history: 4/4 on dedicated slice run) | **4/4** |
| Per `failure_mode` | No cluster/YTD/unknown regressions vs pivot doc | **Pass** (see E spot-check) |

## Decision

- **Assigned tier:** **1 — Promote**
- **Signed:** 2026-05-20 (E-regression spot-check cleared; promotion packet A–F complete)
- **Next pull:** ~~**B1** expand `temporal_candidates.py` → re-run 14-record slice~~ **Done** (`…232514Z` 14/14) → **B2** model event table
