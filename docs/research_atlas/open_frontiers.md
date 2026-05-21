# Open Frontiers

Generated: 2026-05-21

This view is lifted from the Kanban plan so the atlas stays connected to active research operations.

## Active Work

**Current mode:** three-axis hybrid-pipeline exploration (GPT cap-25 grids first).

Completed carryover: **`exect_s1_seizure_prompt_policy_qwen_v1`** — Hold (promote blocked); full `…231850Z` (seizure 74.2%, +18.5pp). Inspection `docs/exect_s1_seizure_prompt_policy_qwen_v1_inspection_20260520.md`.

Completed carryover: Lane A GPT factor-isolation cap-25 groups for Gan and ExECT S1 are now arm evidence, not mechanism closure.

**Next model-backed comparison group:** `exect_s1_pipeline_stage_graph_gpt_cap25_v1` — ExECT S1 Axis 1 stage-graph grid (Gan Phases 2–4 complete). Gan presentation sweep: `docs/gan_s0_implementation_variant_gpt_cap25_v1_inspection_20260521.md`.

**Gan stage-graph Axis 1 cap-25 complete (2026-05-21):**

| Arm | `stage_graph_id` | Monthly | Outcome |
| --- | --- | ---: | --- |
| A3 | `g2_candidates_adjudicate` | 52.0% | hold → Phase 3 anchor |
| A1/A2/A4/A5 | various | 44.0% | reject (arm) |

Inspection: `docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md`

**Cap-25 complete (2026-05-20):**

| Arm | Run | Seizure F1 | Gate |
| --- | --- | ---: | --- |
| GPT v4_11 | `…214222Z` | 93.9% (−1.5pp vs v4_10) | Pass |
| Qwen v4_11 | `…214425Z` | 78.3% (+11.6pp vs `…210432Z`) | Pass (amended — diagnosis −2.6pp waived) |

**Lane Q closed:** v4_11 full `…231850Z` — promote blocked (mismatch docs 14, diagnosis −5.1pp); Qwen production stays v4_10 H1.

No runs in flight. S1 interleaving GPT v2 + Qwen v1 and all S1/S4 family-isolated GPT probes **closed**.

**Lane A cap-25 complete (2026-05-21):** Inspection `docs/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md` — prompt **reject v4_11 on GPT**; verification **reject verify-repair** (−9.4pp micro); evidence **hold standard**, reject soft. No full-validation follow-ups for these three groups.

**Lane A preregistered — Gan configs next:**

| Card | Preregistration | Next step | Blocker |
| --- | --- | --- | --- |
| Gan S0 verification ablation | `docs/gan_s0_verification_gpt_validation_v1_preregistration_20260521.md` | **Cap-25 complete — hold (null factor)** | Inspection `docs/gan_s0_lane_a_gpt_cap25_inspection_20260521.md` |
| Gan S0 evidence-policy ablation | `docs/gan_s0_evidence_policy_gpt_validation_v1_preregistration_20260521.md` | **Cap-25 complete — reject optional & span-check** | Span-check abstained 7/25; not comparable |
| Gan S0 prompt-policy ablation | `docs/gan_s0_prompt_policy_gpt_validation_v1_preregistration_20260521.md` | **Cap-25 complete — hold guardrails +4pp; reject synthesis** | Optional error-read on 6 label diffs |
| ExECT S1 prompt-policy ablation | `docs/exect_s1_prompt_policy_gpt_validation_v1_preregistration_20260521.md` | **Cap-25 done — reject v4_11 (GPT)** | None |
| ExECT S1 verification ablation | `docs/exect_s1_verification_gpt_validation_v1_preregistration_20260521.md` | **Cap-25 done — reject verify-repair** | None |
| ExECT S1 evidence-policy ablation | `docs/exect_s1_evidence_policy_gpt_validation_v1_preregistration_20260521.md` | **Cap-25 done — hold standard** | None |
| ExECT S1 optimizer pilot | `docs/exect_s1_optimizer_gpt_cap25_v1_preregistration_20260521.md` | **Cap-25 complete — reject bootstrap** | Inspection `docs/exect_s1_optimizer_gpt_cap25_v1_inspection_20260521.md` |
| ExECT S1 full ladder rungs 0–3 | `docs/exect_s1_full_ladder_gpt_validation_v1_preregistration_20260521.md` | **Complete** | Inspection `docs/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md` |
| ExECT S1 optimizer automation thesis | `docs/exect_s1_ladder_optimizer_automation_thesis_20260521.md` | **Ready — configs scaffolded** | L0/L1 + compile without hand-crafted policy |

## Recommended Next Pull

1. **Gan Axis 2 prereg:** `docs/gan_s0_stage_executor_gpt_cap25_v1_preregistration_20260521.md` — det vs LLM vs hybrid candidate generation on `g2_candidates_adjudicate`.
2. **Implement + run** executor grid cap-25; inspect with `decision_scope: arm`.
3. **Registry backfill** for Phase 2 (5 rows) and Phase 3 when runs land.
4. **Consolidation:** Refresh registry matrix / atlas after new rows land.

## Ready After Consolidation

### Gan stage-executor queue

Ready for next session. Phase 2 ranked `g2_candidates_adjudicate` (52% monthly) over operational skeleton `g3_candidates_extract_repair` (44%). First implementation: `llm_temporal_candidates` program path.

### Gan stage-graph queue (complete)

Done. `docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md`.

### Optional Gan model-interaction robustness slice

Only run this if the Gan narrative needs model-interaction evidence after the clean GPT factor groups. Keep the same records, scorer, schema, and temporal-candidates architecture across GPT and Qwen.

## Blocked Or Deferred

### Published ExECTv2 benchmark reproduction

Blocked on CUI-aware all-family scoring. Current ExECT numbers are local field-family diagnostics, not published Table 1 reproduction.

Use `dataset-audit-first` and `gold-scorer-integrity` before touching this.

### Published Gan real-set reproduction

Blocked on access to Gan Real(300)/Real(150) style data. Current Gan claims are fixed synthetic validation claims.

### Broad ExECT architecture ablation

Deferred. S1 interleaving v1/v2 and S4 family-isolated probes are complete; reopen only after a promotable single-factor arm exists or for an explicit pre-registered architecture matrix.

### Optimizer scale-up

ExECT S1 cap-25 bootstrap is complete and rejected. Broader optimizer scale-up remains deferred until the reference ladder is interpreted under the three-axis plan.

## Current Decisions

| Decision | Current position |
| --- | --- |
| Research doctrine | **Three-axis exploration** — `docs/hybrid_pipeline_research_pivot_20260521.md` |
| Experiment loop | Explore primarily on GPT 4.1-mini; reserve Qwen35b for selected high-value focus experiments |
| Gan default architecture | Temporal-candidates verify-repair (`H2` + `H4`) |
| Gan next experiment | Axis 1 stage-graph grid with deterministic candidate-source control |
| Gan ReAct H3 | **arm-reject** (one tool surface); mechanism open |
| ExECT S1 interleaving Qwen v1 | **Complete — reject port** — full bridge Δ +12.8pp micro; H1 null vs Qwen anchor; does not close GPT seizure gap |
| ExECT next experiment | Axis 1 stage-graph grid on S1 after Gan Phase 2, with bridge mode documented |
| Lane A policy | **New clean experiments only** — do not recategorize old bundled rows as the clean evidence base |
| ExECT S1 seizure H2 slice | **Reject** — 83.3% vs 91.5% seizure_type F1 on 15-record slice (−8.2pp) |
| ExECT S1 seizure L1 slice | **Hold (slice reference)** — 91.5% seizure_type F1 |
| ExECT S4 temporality error-read | **Done** — dose-only unknown-abstention caused recall collapse; planned/taper slice 4/19 FNs; no taper retune |
| ExECT S4 temporality H1 full | **Reject** — 56.5% vs 46.4% MT precision (+10.1pp) but −6.6pp MT F1 on full validation (40) |
| ExECT S4 temporality H1 cap-25 | **Hold (cap-25 only)** — gate passed on 25 records; full validation rejected |
| ExECT S4 temporality L1 full | **Hold (full-validation reference)** — 46.4% MT precision |
| ExECT S4 frequency H2 pre-vocab | **Reject** — 47.1% vs 49.1% seizure_frequency F1 on cap-25 (−2.0pp) |
| ExECT medication H2 slice | **Reject** — 95.1% vs 98.3% medication F1 on 14-record Rx-heavy slice (−3.2pp) |
| ExECT interleaving v2 registry | **Done** — four rows in `exect_s1_interleaving_gpt_validation_v2` |
| ExECT S1 interleaving H1 (v2) | **Hold (null vs production L1)** — 92.3% full micro; bridges match `repair_policy=none` |
| ExECT S1 interleaving L1 raw (v2) | **Diagnostic** — 68.6% full micro without bridges; ~24pp bridge contribution measured |
| ExECT S1 interleaving H1 (v1) | **Superseded** — v1 null explained by always-on bridges; see v2 inspection |
| ExECT S1 interleaving H2 | **Reject** — pre-vocab regressed full micro to 87.5% (−4.8pp vs L1) |
| ExECT S1 interleaving H3 | **Defer** — no positive signal from H1/H2 |
| Registry policy | Taxonomy fields required for new configs or registry rows |
| Benchmark claims | Keep separate from local validation until scorer/data blockers clear |
| Mass historical backfill | Defer low-value exploratory Gan direct rows |
| Gan Qwen H1 full (verify-repair, no temporal candidates) | **Skip** for now — hard-slice H1 regressed; temporal-candidates promoted; full run unlikely to change default |
| ExECT S1 GPT prompt policy v4_11 (cap-25) | **Reject on GPT** — 93.9% seizure F1 vs 95.4% v4_10 (−1.5pp); Qwen port remains separate |
| ExECT S1 GPT verify-repair (cap-25) | **Reject** — 86.4% micro vs 95.8% single-pass (−9.4pp) |
| ExECT S1 GPT evidence policy (cap-25) | **Hold standard** — strict null (+0.6pp micro); soft reject (−3.1pp seizure, −4.4pp evidence) |
| ExECT Qwen S4 full | **Hold** as local ladder anchor (`…160914Z`); +2.0pp pooled micro vs GPT but weaker seizure/diagnosis per-family |
