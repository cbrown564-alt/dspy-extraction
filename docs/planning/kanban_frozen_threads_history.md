# Kanban Frozen Threads — Historical Detail

**Archived from:** `docs/planning/kanban_plan.md` (2026-05-20 refresh)  
**Purpose:** Preserve run IDs, metric tables, configs, and freeze decisions for completed or frozen tracks without bloating the active board.  
**Active tracker:** `docs/planning/kanban_plan.md`  
**Narrative archive:** `docs/planning/research_status_recap_20260519.md`

Run IDs below use the `…` prefix for the timestamp suffix under `runs/` (e.g. `…071248Z` → `runs/exect_s4_validation_full_gpt4_1_mini_20260520T071248Z`).

---

## Thread A — Gan temporal-candidates v1.1 (local Qwen) — Tier 1 promoted

**Status:** Tier 1 signed; default local Gan S0 path. Post–tier-1 engineering (B1/B2/ReAct/hosted port) lives on the active board.

**Hypothesis:** Infrequent quantified rates need temporal event decomposition + confirm-first verifier guards. Pivot: `docs/experiments/gan/gan_s0_temporal_candidate_pivot_20260519.md`.

| Stage | Status | Run | Headline |
| --- | --- | --- | --- |
| Regression slice (14) | Cleared | `…180329Z` | 100% monthly, schema, evidence; 10/10 original, 4/4 infrequent |
| Cap-25 validation | Cleared | `…183213Z` | 44% monthly (+6.5pp vs direct cap-25), 100% schema (25/25), 100% evidence |
| Full validation (299) | Done | `…230324Z` | 65.8% monthly, 75.5% Purist, 82.6% Pragmatic; 99.7% schema, 100% evidence |
| Promotion decision | Tier 1 — Promote | `docs/experiments/gan/gan_s0_temporal_candidates_v1_1_full_validation_decision_20260519.md` | Beats Qwen direct full (+9.9pp monthly); ties GPT verify-repair monthly with higher evidence |
| Slice replay from full | Done | same run + fixture | 14/14 valid; 100% all metrics on regression slice |

**Program:** `gan_frequency_s0_temporal_candidates_verify_repair_v1_1` — `src/clinical_extraction/programs/gan_frequency_s0.py`  
**Config:** `configs/experiments/gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails.json`

**Anchors:**

| Path | Monthly | Evidence | Notes |
| --- | ---: | ---: | --- |
| Temporal v1.1 full (promoted) | 65.8% | 100% | `…230324Z` |
| GPT verify-repair v2 full | 65.4% | 92.7% | Hosted quality ceiling |
| Qwen direct guardrails full | 55.9% | 99.6% | `…102249Z` |
| Qwen direct cap-25 v2 | 37.5% | 100% | Cap-25 monthly anchor |

**Error analysis:** `docs/experiments/gan/gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_error_analysis.md`, `docs/experiments/gan/gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_from_full_validation_error_analysis.md`

**Stratified note:** `gold_pragmatic=infrequent` monthly 51.0% (51 records) — main residual bucket on full validation.

**Post–tier-1 engineering (completed on active board):**

| Step | Run | Outcome |
| --- | --- | --- |
| B1 expand `temporal_candidates.py` | `…232514Z` | 14/14 slice; gold-in-candidates 10/14 |
| B2 model event table | `…235058Z` | 14/14; event-table rescue guard for `gan_14881` |

---

## Thread B — ExECT S0/S1 monolithic label policy (GPT 4.1-mini) — frozen

**Status:** Stop micro-iteration. v4.10 frozen dev anchor (`…221944Z` 92.3% micro, 40 validation). One-shot test holdout (`…222615Z` 77.8%). Breadth handed to S2–S4 ladder.

**Detail:** `docs/experiments/exect/exect_s0_label_policy_v4_10_implementation.md`  
**Regression slice:** `data/fixtures/exect_s0_label_policy_error_regression_slice.json` (37 records — safety only)

| Stage | Run | Micro F1 |
| --- | --- | ---: |
| v4.10 full (40) — frozen dev | `…221944Z` | 92.3% |
| v4.10 test (40) — one-shot | `…222615Z` | 77.8% |
| v4.10 cap-25 | `…221936Z` | 95.8% |

**Frozen configs:** `exect_s0_s1_smoke_gpt4_1_mini.json`, `exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json`, `exect_s0_s1_validation_test_gpt4_1_mini.json`

**Findings:** Monolithic label-policy + bridges beats section-aware; cap-25 optimistic ~7–9pp vs full; verify-repair / diagnosis-recall closed on validation.

---

## Thread C — ExECT S2 field expansion (GPT 4.1-mini) — frozen at v1.3

**Status:** Stop micro-iteration. v1.3 full validation is the S2 baseline for the schema ladder.

**Design:** `docs/experiments/exect/exect_s2_field_expansion_design.md`  
**Program:** `exect_s2_field_family_single_pass` — `src/clinical_extraction/programs/exect_s2.py`  
**Scorer:** `exect_s2_field_family_deterministic_v1` (5 families)  
**Prompt:** `exect_s2_field_family_v1_3_label_policy`

| Stage | Run | Headline |
| --- | --- | --- |
| Smoke (3) | `…223951Z` | 3/3 contract |
| Cap-25 v1 (baseline) | `…224038Z` | 66.4% micro; seizure 40.0% (S2-only regression vs S1) |
| Cap-25 v1.2 | `…225836Z` | 84.1% micro; comorbidity 74.3%; seizure 83.1% |
| Cap-25 v1.1 | `…225159Z` | 79.7% micro; seizure 80.6%; comorbidity 53.8% |
| Full v1.3 (40) | `…231223Z` | 80.9% micro; comorbidity 69.3%; jerk FP 0 |
| Full v1.2 | `…230407Z` | 80.6% micro; comorbidity 63.6%; 7× jerk FP |

**Cap-25 v1.1 family breakdown (`…225159Z` vs v1 `…224038Z` vs S1 cap-25 `…221936Z`):**

| Family | v1.1 | v1 | S1 cap-25 (3 fam) |
| --- | ---: | ---: | ---: |
| Micro (5 fam) | 79.7% | 66.4% | 95.8% |
| Seizure | 80.6% | 40.0% | 95.4% |
| Diagnosis | 83.7% | 88.4% | — |
| Medication | 91.8% | 81.7% | — |
| Investigation | 90.9% | 85.7% | n/a |
| Comorbidity | 53.8% | 49.0% | n/a |

**Label-policy arc:** v1.1 `docs/experiments/exect/exect_s2_label_policy_v1_1_implementation.md`; v1.2 `docs/experiments/exect/exect_s2_label_policy_v1_2_implementation.md`; v1.3 `docs/experiments/exect/exect_s2_label_policy_v1_3_implementation.md`  
**Inspections:** `docs/experiments/exect/exect_s2_validation_cap25_gpt4_1_mini_inspection_20260519.md`, `docs/experiments/exect/exect_s2_validation_full_gpt4_1_mini_inspection_20260520.md`

**Configs:** `exect_s2_smoke_gpt4_1_mini.json`, `exect_s2_validation_cap25_gpt4_1_mini.json`, `exect_s2_validation_full_gpt4_1_mini.json`

**Do not:** retune S1 bridges on validation; compare 5-family micro F1 to S1-only 95.8% cap-25 as if same metric.

---

## Thread D — ExECT S3 field expansion (GPT 4.1-mini) — frozen at v1.2

**Status:** Stop micro-iteration. v1.2 full validation is the S3 baseline. **Accepted gap:** comorbidity full F1 59.8% vs S2 v1.3 69.3% (−9.5pp, same 40 records).

**Design:** `docs/experiments/exect/exect_s2_s4_schema_ladder_design.md`, `docs/experiments/exect/exect_s3_phase1_overlap_policy.md`  
**Program:** `exect_s3_field_family_single_pass` — `src/clinical_extraction/programs/exect_s3.py`  
**Scorer:** `exect_s3_field_family_deterministic_v1` (9 families)  
**Prompt:** `exect_s3_field_family_v1_2_label_policy`

| Stage | Run | Headline |
| --- | --- | --- |
| Smoke (3) | `…233117Z` | 3/3 contract |
| Full v1.0 | `…233810Z` | Investigation collapse (10.3% F1) |
| Full v1.1 | `…234907Z` | Investigation fixed; seizure 32.7% |
| Cap-25 v1.2 | `…235349Z` | 78.1% micro (9 fam); seizure 88.2%; investigation 93.8% |
| Full v1.2 — frozen | `…235439Z` | 72.1% micro (9 fam); seizure 78.1%; investigation 93.1% |

**Full v1.2 vs frozen S2 v1.3 (same 40 records):**

| Family | S3 v1.2 | S2 v1.3 | Δ | Note |
| --- | ---: | ---: | ---: | --- |
| Seizure | 78.1% | 71.0% | +7.1pp | Nine-family pass OK |
| Investigation | 93.1% | 90.0% | +3.1pp | v1.1 bridge held |
| Comorbidity | 59.8% | 69.3% | −9.5pp | Accepted at freeze |
| Medication | 81.4% | 90.0% | −8.6pp | Monitor; no S3 re-tuning |
| Diagnosis | 92.5% | 88.9% | +3.6pp | — |
| Micro F1 | 72.1% (9 fam) | 80.9% (5 fam) | — | Not comparable scope |

**Label-policy arc:** v1.1 `docs/experiments/exect/exect_s3_label_policy_v1_1_implementation.md`; v1.2 `docs/experiments/exect/exect_s3_label_policy_v1_2_implementation.md`  
**Inspection:** `docs/experiments/exect/exect_s3_validation_full_gpt4_1_mini_inspection_20260520.md`

**Configs:** `exect_s3_smoke_gpt4_1_mini.json`, `exect_s3_validation_cap25_gpt4_1_mini.json`, `exect_s3_validation_full_gpt4_1_mini.json`

---

## Thread E — ExECT S4 schema ladder (GPT 4.1-mini) — frozen at v1.2

**Status:** Hosted GPT breadth arc complete at S4 v1.2. No v1.3 validation tuning unless a targeted regression slice surfaces a clear bridge gap.

**Gold policy:** `docs/experiments/exect/exect_s4_gold_policy.md`  
**Scorer:** `exect_s4_field_family_deterministic_v1` (11 families)

| Step | Run | Headline |
| --- | --- | --- |
| S4 smoke / cap-25 / full v1.0 | `…000944Z` / `…001157Z` / `…001602Z` | 63.4% micro (11 fam); freq 25.6% |
| S4 v1.1 cap-25 / full | `…064206Z` / `…064751Z` | freq 45.2% (+19.6pp vs v1.0) |
| S4 v1.2 cap-25 / full — frozen | `…070616Z` / `…071248Z` | 65.5% micro; freq 45.7%; investigation 96.7% (+10.5pp vs v1.1) |

**Frozen anchors (hosted GPT):**

| Level | Run | Headline |
| --- | --- | --- |
| S2 full v1.3 | `…231223Z` | 80.9% micro (5 fam); comorbidity 69.3% |
| S3 full v1.2 | `…235439Z` | 72.1% micro (9 fam); investigation 93.1%; seizure 78.1% |
| S4 full v1.0 | `…001602Z` | 63.4% micro (11 fam); freq 25.6%; Rx temporality 65.2% |
| S4 full v1.1 | `…064751Z` | 65.6% micro (11 fam); freq 45.2%; Rx temporality 67.2% |
| S4 full v1.2 | `…071248Z` | 65.5% micro (11 fam); freq 45.7%; investigation 96.7%; Rx temporality 62.5% |

**Label-policy arc:** v1.1 `docs/experiments/exect/exect_s4_label_policy_v1_1_implementation.md`; v1.2 `docs/experiments/exect/exect_s4_label_policy_v1_2_implementation.md`  
**Inspections:** `docs/experiments/exect/exect_s4_validation_full_gpt4_1_mini_inspection_20260520.md`, `docs/experiments/exect/exect_s4_validation_full_v1_1_gpt4_1_mini_inspection_20260520.md`, `docs/experiments/exect/exect_s4_validation_full_v1_2_gpt4_1_mini_inspection_20260520.md`

**Full v1.0 vs frozen S3 v1.2 (same 40):** investigation 93.3% (hold); seizure 78.8% (+0.7pp); medication 72.0% (−9.4pp); comorbidity 57.1% (−2.7pp). New S4 families: frequency weak; temporality usable.

**Configs:** `exect_s4_smoke_gpt4_1_mini.json`, `exect_s4_validation_cap25_gpt4_1_mini.json`, `exect_s4_validation_full_gpt4_1_mini.json`

---

## Consolidated freeze decisions (2026-05-20)

| Question | Decision |
| --- | --- |
| S2→S4 baseline | S2 v1.3 `…231223Z` + S3 v1.2 `…235439Z` |
| Freeze S3 with comorbidity gap? | Yes — 59.8% vs S2 69.3% accepted |
| Freeze S4 at v1.2 on hosted GPT? | Yes — freq 45.7% accepted as documented limitation |
| Continue ExECT v4.x on validation? | No — frozen at v4.10 |
| S2 seizure regression root cause | Model output drift in multi-family pass; v1.1 recovered cap-25 |
