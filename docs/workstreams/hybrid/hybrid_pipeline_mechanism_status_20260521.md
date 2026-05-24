# Hybrid Pipeline Mechanism Status

Date: 2026-05-21  
Maintained under: `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`  
Update when an inspection doc with `decision_scope: mechanism` closes a class, or when a new arm reject is recorded.

**Legend:** `open` | `arm-reject` | `operational-freeze` | `mechanism-reject` (rare)

---

## Operational defaults (not mechanism-closed)

| ID | Config / program | decision_scope | Notes |
| --- | --- | --- | --- |
| gan-default | F0 expanded builders + prose | operational | remains full-validation operational default (68.1% monthly GPT anchor) |
| exect-s1-gpt | v4_10 + inline bridges | operational | Ladder + freeze anchor 92.3% micro full |
| exect-ladder-gpt | S2–S4 frozen full runs | operational | Schema complexity series |

---

## Axis 1 — Pipeline stage count / decomposition

| Mechanism class | Status | Evidence |
| --- | --- | --- |
| Optimal stage count for Gan S0 | **open** | Cap-25 grid complete; A3 (`g2_candidates_adjudicate`) leads at 52% monthly — see `docs/experiments/gan/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md` |
| Optimal stage count for ExECT S1 | **open** | D1→L0→L1→L1+policy confounds stages with policy |
| Single-stage sufficient for Gan | **open** | — |
| Three-stage (candidates+VR) necessary for Gan | **open** | Promoted arm is 2–3 stage; Phase 2 isolates stage graph while holding candidate source deterministic |

---

## Axis 2 — Deterministic vs LLM per stage

| Mechanism class | Status | Evidence |
| --- | --- | --- |
| Det temporal candidate generation (Gan) | **operational-freeze** | Expanded builders default 2026-05-21; cap-50 **68%** (+6pp) — `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_cap50_v1_inspection_20260521.md`; full-val F0 **68.1%** (+3.0pp vs VR 65.1%) — **promote operational (arm)** `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_full_validation_v1_inspection_20260521.md`; mechanism class still **open** |
| LLM temporal candidate generation (Gan) | **open** | Cap-25 JSON path rejected as arm (E2/E5 29.2% vs E1 52%); presentation not swept — `docs/experiments/gan/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md` |
| LLM vs det for candidate stage (Gan) | **open** | Directional det > hybrid > LLM on cap-25; mechanism not closed (one LLM format) |
| Verify-repair as second stage (Gan) | **open** | Cap-25 null on monthly; V6≡V0 (52%); det-evidence front-end harmful (V3–V5) — `docs/experiments/gan/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md` |
| Verify-repair (ExECT S1) | **arm-reject** | `exect_s1_verification_verify_repair_cap25` −9.4pp micro |
| Tool-during temporal (Gan H3) | **arm-reject** | `gan_s0_qwen35b_react_temporal_tools` slice — one tool surface |
| Tool-during (general) | **open** | Second tool implementation not tested |
| Pre section-aware context (ExECT) | **arm-reject** | Section-aware cap-25 fail — short-note caveat |
| Pre static vocab lists (ExECT S1/S4) | **arm-reject** | Slice/cap-25 configs in negative-probe synthesis |
| S2 comorbidity atomization bridge (C0/C1) | **open** | Cap-25 null 85.7% all arms — `docs/experiments/exect/exect_s2_comorbidity_surface_bridge_gpt_cap25_v1_inspection_20260521.md` |
| S2 investigation ECG drop guard (I0) | **open** | Cap-25 +5.6pp investigation F1 — `docs/experiments/exect/exect_ladder_investigation_guard_gpt_cap25_v1_inspection_20260521.md` |
| S3 epilepsy_cause CUIPhrase bridge (K0+K1) | **operational-freeze** | S3 full-val +11.1pp cause F1 — `docs/experiments/exect/exect_s3_epilepsy_cause_bridge_gpt_full_validation_v1_inspection_20260521.md`; S3 default variant not yet switched |
| S4 epilepsy_cause CUIPhrase bridge (K0+K1) | **operational-freeze** | S4 full-val +10.6pp cause F1; `EXECT_S4_VARIANT` frozen — `docs/experiments/exect/exect_s4_epilepsy_cause_bridge_gpt_full_validation_v1_inspection_20260521.md` |
| Pre context/candidate (general ExECT) | **open** | Other presentations and tasks not swept |
| Post benchmark bridges (ExECT S1) | **operational-freeze** | Inline bridges in production; diagnostic bridge-free measured |
| Post bridge as only intervention | **open** | Not same as bridge + policy decomposition |

---

## Axis 3 — Implementation variants

| Mechanism class | Status | Evidence |
| --- | --- | --- |
| Prompt v4_11 (GPT S1) | **arm-reject** | cap-25 seizure −1.5pp |
| Prompt v4_11 (Qwen S1) | **operational-freeze** | Hold promote blocked; seizure +18.5pp full |
| Evidence soft (ExECT S1) | **arm-reject** | cap-25 |
| Evidence span-check (Gan) | **arm-reject** | V7 + Lane A on g2 skeleton; 9/25 abstentions cap-25 — `docs/experiments/gan/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md` |
| Bootstrap optimizer (ExECT S1) | **arm-reject** | cap-25 −5.1pp |
| DSPy optimizers (general) | **open** | ExECT stripped L0/L1 compile **arm-reject** for policy substitution (best 71.7% cap-25) — `docs/experiments/exect/exect_s1_ladder_optimizer_automation_inspection_20260521.md` |
| GEPA (Gan) | **arm-reject** | historical full |
| Multi-stage GEPA over Gan candidate/adjudicator or verify-repair skeleton | **open** | Newly preregistered workstream distinguishes this from historical direct GEPA arm reject; see `docs/workstreams/optimizer/gan_s0_multistage_gepa_workstream_20260524.md` |
| ReAct interface (Gan) | **arm-reject** | one implementation |
| Candidate table vs JSON vs prose (Gan) | **open** | Cap-25: +4pp table vs prose; **cap-50 confirm null** (62% tie) — `docs/experiments/gan/gan_s0_implementation_variant_gpt_cap50_v1_inspection_20260521.md` |
| Canonical format examples (Gan adjudicate) | **open** | Cap-25 C1 +4pp exact (arm hold); residual 30-record replay null — `docs/experiments/gan/gan_s0_canonical_format_residual_slice_replay_20260521.md` |
| Candidate-constrained verifier (Gan G7) | **arm-reject** | GPT enriched slice tied v1.4 (36.0% monthly, 56.0% pragmatic) while adding a second LLM pass; 100.0% schema/evidence and no free-form drift, but no promotion lift — `docs/experiments/gan/gan_s0_candidate_constrained_verifier_gpt_slice_v1_inspection_20260522.md` |
| Targeted examples min7 (Gan) | **arm-reject** | GPT enriched slice tied v1.4 (36.0% monthly, 56.0% pragmatic, 100.0% schema/evidence) with mixed rescues/regressions; example mechanism remains open — `docs/experiments/gan/gan_s0_targeted_examples_min7_gpt_slice_v1_inspection_20260523.md` |
| Seeded hybrid answer options (Gan G6b) | **arm-reject** | GPT enriched slice underperformed v1.4 (16.0% monthly, 20.0% pragmatic, 100.0% schema/evidence on 8 supported-evidence predictions); deterministic seeds rescued four exact records, but LLM option selection introduced false no-reference/zero-rate errors and 14/25 fallback `unknown` — `docs/experiments/gan/gan_s0_seeded_answer_options_gpt_slice_v1_inspection_20260523.md` |
| Gan S0 policy/pipeline synthesis | **operational-freeze** | Decision synthesis keeps v1.4 as no-example GPT slice control and F0 expanded builders + prose as full-validation operational default; builder-gap audit/prereg/v1 slice completed (G11–G15); next pull is G16 broader validation — `docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md` |
| Gan S0 candidate-builder gap v1 (G15) | **arm** | GPT slice lift (92.0% monthly / 96.0% pragmatic on enriched 25-record slice); slice-gate evidence only, operational default unchanged pending G16 — `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md` |
| ExECT S4 frequency structured slots | **open** | Cap-25 S2 null vs R0 (51.0% F1); mechanism class open — `docs/experiments/exect/exect_s4_frequency_structured_slots_gpt_cap25_v1_inspection_20260521.md` |
| ExECT S4 sparse-family prompt sweeps | **policy-gated / deferred** | Policy memo selects bridge-first; no cap-25 model spend until bridge scaffolds — `docs/experiments/exect/exect_s4_sparse_family_surface_policy_20260521.md` |

---

## Repeat guardrail (arm configs — do not rerun without new prereg)

See `docs/experiments/exect/exect_negative_probe_synthesis_20260520.md` for ExECT probe **config IDs**.  
These are **arm-reject**, not mechanism-reject for the rows in that doc.

---

## Next status updates expected

- Preregister expanded builders + VR bundle (`g3_candidates_extract_repair`) vs F0 adjudicate-only anchor — **Done** `docs/experiments/gan/gan_s0_expanded_builders_vr_gpt_full_validation_v1_preregistration_20260521.md`
- Execute V1 full validation and inspection — **Done** `docs/experiments/gan/gan_s0_expanded_builders_vr_gpt_full_validation_v1_inspection_20260521.md` (hold; F0 remains monthly leader)
- ExECT S4 medication precision guard full-validation L1/G0 pair
- Gan deterministic candidate-builder gap analysis on enriched slice (G11–G15) — **Done** on 2026-05-23
- G16 broader GPT validation of candidate-builder gap v1 on full validation split
- Targeted builder gaps: seizure-type priority, long-window cluster phrasing
