# Gan S0 GPT Temporal-Candidates v1.1 Full Validation — Promotion Decision

Date: 2026-05-20  
Status: **Hosted — Promote** (full validation complete `…130933Z`)

## Purpose

Assign the hosted Gan S0 default path after porting `gan_frequency_s0_temporal_candidates_verify_repair_v1_1` from local Qwen Tier 1 to GPT 4.1-mini (Option A). This note closes the cap-25 → full 299 gate chain documented in `docs/kanban_plan.md` and `configs/experiments/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails.json`.

**Scope:** Hosted GPT track only. Local Qwen Tier 1 (`…230324Z`) and the ReAct bounded probe remain on separate promotion criteria.

## Taxonomy

- **Dataset:** gan_2026
- **Schema complexity:** gan_s0
- **Clinical task family:** frequency
- **Hybrid balance class:** H2_pre_deterministic, H4_deterministic_first_llm_adjudicates
- **Interleaving positions:** pre, during, post
- **Varied factor:** program_architecture
- **Comparison group:** gan_s0_architecture_gpt_validation_v1
- **Outcome:** promote

## Artifacts

| Role | Path |
| --- | --- |
| Candidate run | `runs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z` |
| Config | `configs/experiments/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails.json` |
| Cap-25 gate (promote) | `runs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_cap25_guardrails_validation_20260520T130724Z` |
| Cap-25 hold (pre-bridge) | `runs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_cap25_guardrails_validation_20260520T125302Z` |
| Hosted anchor (superseded) | `runs/gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z` |
| Local Tier 1 reference | `runs/gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T230324Z` |
| Slice fixture | `data/fixtures/gan_s0_qwen_error_regression_slice.json` |
| Full error analysis | `docs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_error_analysis.md` |
| Slice replay analysis | `docs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_regression_slice_from_full_validation_error_analysis.md` |

## Pre-registered promotion tiers (hosted port)

| Tier | Condition | Action |
| --- | --- | --- |
| **Promote** | Full monthly within **1pp** of verify-repair v2 full (65.4%) **and** evidence ≥ verify-repair v2 (92.7%) **and** schema ≥ 99% | Replace verify-repair v2 as default **hosted** Gan S0 path; record in frozen-thread history |
| **Hold** | Monthly below verify-repair cap-25 (34.8%) **or** evidence < 90% at cap-25 **or** monthly >1pp below verify-repair v2 full without compensating evidence gain | Do not launch full 299; forensics on bridge/guards |
| **Reject** | Monthly ≤ cap-25 temporal (~44%) at full scale **or** schema < 95% **or** evidence regression vs verify-repair v2 full | Abandon hosted temporal port; keep verify-repair v2 anchor |

**Cap-25 launch gates (pre-full, already cleared at `…130724Z`):** monthly ≥ 40%, schema 100%, evidence ≥ 90%, no evidence regression vs verify-repair cap-25 (`…084511Z`, 91.3% evidence).

**E regression guard (document, not full-split veto for hosted):** wrong YTD, stripped cluster, `unknown`→quantified rate, `unknown`→seizure-free, short seizure-free — shapes from `docs/gan_s0_temporal_candidate_pivot_20260519.md`. Full-split monthly tie with verify-repair v2 plus evidence lift is sufficient for hosted promote; slice E misses are tracked for ReAct/hosted follow-up, not as a veto when aggregate gates pass.

## Promotion packet checklist

- [x] **A** — Full-split analyzer markdown (299 records)
- [x] **B** — 14-record regression slice replay from same artifacts
- [x] **C** — Stratified table: `gold_pragmatic=infrequent`, `hard_case`, invalid/abstain
- [x] **D** — Anchor comparison table (this doc § Headline metrics)
- [x] **E** — E-regression spot-check on regression slice (documented; not a hosted veto)
- [x] **F** — Cap-25 decision note chain closed (bridge fix `…130724Z` → full `…130933Z`)

## Headline metrics

| Metric | GPT temporal full `…130933Z` | GPT verify-repair v2 `…084732Z` | Qwen temporal v1.1 `…230324Z` |
| --- | ---: | ---: | ---: |
| Records analyzed | 299 (298 valid) | 299 (289 valid) | 299 (298 valid) |
| Schema-valid rate | **99.7%** | 96.7% | 99.7% |
| Monthly-frequency accuracy | **65.1%** (CI 59.7–70.5%) | 65.4% (CI 59.5–70.9%) | 65.8% (CI 61.1–71.1%) |
| Purist category accuracy | **76.5%** | 72.7% | 75.5% |
| Pragmatic category accuracy | **84.2%** | 79.2% | 82.6% |
| Evidence quote support | **100.0%** | 92.7% | 100.0% |
| Normalized-label exact (diagnostic) | 52.3% | 52.9% | 55.4% |
| Runtime | ~18.5 min (~3.7 s/record) | — | — |

**Gate read:** Monthly is **−0.3pp** vs verify-repair v2 (within 1pp). Evidence **+7.3pp**, schema **+3.0pp**, Purist **+3.8pp**, Pragmatic **+5.0pp** vs the superseded hosted anchor. Monthly is **−0.7pp** vs local Qwen temporal — expected; hosted port does not claim local Tier 1 parity.

## Stratified residuals (full split)

| Stratum | Monthly (valid only) | Notes |
| --- | ---: | --- |
| `gold_pragmatic=frequent` | 62.9% | 151 valid |
| `gold_pragmatic=infrequent` | 43.1% | 51 valid — main residual bucket (same pattern as Qwen full) |
| `gold_pragmatic=unknown` | 55.0% | 40 valid |
| `gold_pragmatic=no_seizure_information` | 98.2% | 56 valid |
| `hard_case=true` | 71.8% | 39 valid |

## Slice replay (14-record regression fixture)

| Stratum | Target | GPT temporal `…130933Z` | Qwen temporal `…230324Z` |
| --- | --- | --- | --- |
| All metrics on slice | Diagnostic | **8/14** monthly (57.1%) | 14/14 (100%) |
| Original policy/cluster rows (10) | No E-regression vs pivot doc | **7/10** monthly | 10/10 |
| Infrequent quantified (4) | ≥3/4 monthly | **1/4** monthly | 4/4 |
| Per `failure_mode` | See E spot-check below | Mixed | Pass |

Slice underperformance vs local Qwen is expected on a 14-record stress fixture and does **not** block hosted promote given full-split tie with verify-repair v2 and superior evidence/schema/category metrics.

### E regression guard spot-check (slice replay)

| Failure mode | Records | GPT full-split result |
| --- | --- | --- |
| `unknown_vs_no_reference` | `gan_10509`, `gan_10751`, `gan_11221` | `gan_10509` **pass** (`unknown`); `gan_10751` **fail** (`unknown`→cluster); `gan_11221` **fail** (`unknown`→seizure-free) |
| `no_clinical_content_null_output` | `gan_11733` | **pass** (`no seizure frequency reference`) |
| `year_to_date_denominator` | `gan_12810` | **pass** (`5 per 2 month`) |
| `highest_current_quantified_frequency` | `gan_12130`, `gan_12823` | `gan_12130` **fail** (`multiple per week`→`3 per year`); `gan_12823` **pass** (monthly match; surface `9 per 1 month`) |
| `incomplete_cluster_label` | `gan_10052` | **pass** (full cluster surface) |
| `cluster_multiplier_preservation` | `gan_10003` | **pass** (`multiple per cluster` preserved) |
| `short_seizure_free_threshold` | `gan_10410` | **pass** (`1 cluster per week, 3 to 4 per cluster`) |
| `infrequent_quantified_over_unknown` | `gan_13123`, `gan_14485`, `gan_14881`, `gan_15306` | `gan_13123` **pass**; `gan_14485` **fail** (monthly 0.33 vs 0.67); `gan_14881` **fail** (`1 per month`→`unknown`); `gan_15306` **fail** (overcalled) |

**Residual invalid (full split):** `gan_338` — `"many per month"` failed normalization (`could not convert string to float: 'many'`). Single-record schema miss; does not block promote.

## Cap-25 → full trajectory

| Stage | Run | Monthly | Schema | Evidence | Decision |
| --- | --- | ---: | ---: | ---: | --- |
| Cap-25 hold (pre-bridge) | `…125302Z` | 44% | 100% | 84% | Hold — evidence bridge gap |
| Cap-25 promote | `…130724Z` | 44% | 100% | 100% | Launch full 299 (`_guard_evidence_text` bridge fix) |
| Full validation | `…130933Z` | 65.1% | 99.7% | 100% | **Promote** hosted default |

Cap-25 monthly (44%) was intentionally **not** extrapolated to full scale; full validation monthly converged to verify-repair v2 / Qwen temporal band as expected.

## Decision

- **Assigned tier:** **Hosted — Promote**
- **Supersedes:** GPT verify-repair v2 full (`…084732Z`) as default hosted Gan S0 path
- **Does not supersede:** Local Qwen temporal Tier 1 (`…230324Z`) — remains default for local/Ollama track until ReAct probe completes
- **Signed:** 2026-05-20 (promotion packet A–F complete; cap-25 chain closed)
- **Next pull:** ExECT Qwen S4 full + inspection doc; then Gan ReAct bounded probe (Ollama dedicated). Optional: hosted slice forensics on `gan_10751`, `gan_11221`, `gan_12130`, infrequent quartet — only if ReAct probe fails and hosted prompt/guard iteration is reconsidered.

## Commands (reproducibility)

```powershell
$run = "runs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z"

# A — full split
uv run python scripts/analyze_gan_frequency_run.py $run `
  --split-name gan_2026_fixed_v1:validation `
  --markdown docs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_error_analysis.md

# B — 14-record regression slice from same artifacts
uv run python scripts/analyze_gan_frequency_run.py $run `
  --split-name gan_2026_fixed_v1:validation `
  --record-ids-file data/fixtures/gan_s0_qwen_error_regression_slice.json `
  --markdown docs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_regression_slice_from_full_validation_error_analysis.md
```

## Metric caveats

- Fixed Gan synthetic **validation** split only — not published Gan benchmark reproduction.
- `gan_frequency_deterministic_v1` scorer unchanged; temporal candidates are deterministic hints.
- Verify-repair doubles model calls vs direct extraction; latency not comparable to direct-only runs.
- Monthly, Purist, and Pragmatic are benchmark-facing; normalized-label exact and evidence diagnostics are supporting metrics.
- Bootstrap CIs overlap between GPT temporal full and verify-repair v2 on monthly — treat as **tie**, not a proven monthly gain.
