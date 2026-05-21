# Clinical Extraction Kanban Plan

**Active steering doc** — execution board, operational defaults, and next pulls.

| | |
| --- | --- |
| **Core direction** | `docs/outline.md` |
| **Research doctrine** | `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md` |
| **Mechanism index** | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` |
| **Big-picture synthesis** | `docs/workstreams/hybrid/hybrid_deterministic_placement_research_synthesis_20260521.md` |
| **Agent skill** | `hybrid-pipeline-exploration` |
| **Registry** | `docs/experiments/synthesis/experiment_registry.json` |
| **Scorer / dataset guardrails** | `docs/policies/deterministic_scorer_semantics.md`, `docs/datasets/exect/exect_gold_label_audit.md`, `docs/datasets/gan/gan_2026_label_audit.md` |
| **Frozen run tables** | `docs/planning/kanban_frozen_threads_history.md` |
| **Retired phased plan** | `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md` (archive only) |

**Last refreshed:** 2026-05-21 — hybrid cap-25 sprint complete; Kanban restored as sole active queue.

---

## Next step

### Replay Gemini under current S-level architecture

**Status:** **Ready to run** (preregister first).

**Goal:** Decide whether prior Gemini champion evidence still matters under **today’s** frozen programs, scorers, bridges, and splits — not under Round-2 direct/verify-repair Gan arms.

| Step | Scope | Notes |
| --- | --- | --- |
| 1 | **Preregister** comparison group `exect_gemini_ladder_replay_v1` | Single-factor: `model_track` = gemini; fixed program variants, bridge policy, scorer, split |
| 2 | **ExECT S1 full validation** | Same production-shaped variant as GPT anchor (`92.3%` micro, `…221944Z`); compare to GPT and Qwen (`79.0%`) |
| 3 | **ExECT S4 full validation** | Frozen `exect_s4_field_family_cause_bridge_k0_k1_single_pass` + current medication guard path; compare to GPT (`65.5%`, `…071248Z`) and Qwen (`67.5%`, `…160914Z`) |
| 4 | **Optional Gan F0** | Port **expanded builders + prose** monthly leader (`68.1%` GPT F0, `…073432Z`) only if paper needs a three-provider Gan table |

**Historical Gemini (stale architecture — do not treat as current defaults):**

- Gan direct full: `…101710Z` — 63.9% monthly (direct path, pre–temporal-candidates promotion)
- Gan VR cap-25: `…101555Z` — evidence +8.6pp vs direct but schema/Purist regress — **no VR scale-up**

**Gates:** same splits and scorers as GPT/Qwen anchors; report as **model-comparison** evidence (`decision_scope: arm`); do not mechanism-close hybrid placement from Gemini alone.

**Skills:** `model-config-compatibility`, `experiment-run-lifecycle`, `dspy-experiment-design`, `dataset-audit-first`.

**Parallel hygiene (non-blocking):** fixture-to-real reality-gap audit (Literature card backlog).

---

## Current research focus

**Mode (post-hybrid sprint):** Confirmatory **model comparison** and research hygiene — not new GPT cap-25 placement grids unless a new preregistered mechanism opens.

**Doctrine (unchanged):** Distinguish **reject (arm)** vs **reject (mechanism)** vs **operational freeze**. Operational defaults are not mechanism-closed. See pivot doc and `hybrid-pipeline-exploration` skill.

**Three-axis program (2026-05-21):** Gan and ExECT cap-25 grids for stage graph, executor, and targeted Axis-3 cells are **complete**. Outcomes live in inspection docs and `hybrid_pipeline_mechanism_status_20260521.md`; do not rerun identical probe configs.

### Experimentation model

| Phase | Rule |
| --- | --- |
| Search | GPT 4.1-mini cap-25 — rank arms; accept nulls |
| Confirm | Slice / full validation for cap-25 winners per prereg |
| Qwen | Port winning cells only |
| Comparison groups | One primary `varied_factor` per group; name axis in prereg |

---

## Operational defaults (frozen for runs)

| Track | Default | Evidence |
| --- | --- | --- |
| **Gan S0** | Expanded builders + prose (F0); temporal-candidates + VR remains engineering baseline | F0 full val **68.1%** monthly (`…073432Z`) vs VR **65.1%** |
| **ExECT S1** | GPT v4_10 + inline bridges | **92.3%** micro full (`…221944Z`) |
| **ExECT S2–S3** | GPT frozen ladder | S2 **80.9%**, S3 **72.1%** micro |
| **ExECT S4** | `EXECT_S4_VARIANT` = `exect_s4_field_family_cause_bridge_k0_k1_single_pass`; G0 medication precision guard hold | **65.5%** micro GPT (`…071248Z`); cause bridge +10.6pp cause F1 full |

**Open mechanism classes** (grid-search if revisiting): optimal stage count; LLM vs det candidate generation; S1 bridge placement; per-family det on S2–S4. Full table: `hybrid_pipeline_mechanism_status_20260521.md`.

---

## What we know now

### Gan S0 seizure frequency

- **Monthly leader:** F0 expanded builders prose **68.1%** full validation (+3.0pp vs pre-expansion VR 65.1%).
- **Cap-25 search:** `g2_candidates_adjudicate` 52% monthly; table/JSON/bullets +4pp vs prose; Qwen port of g2 **arm-reject** (40%).
- **Operational bundle:** temporal-candidates + verify-repair v1.1 — mechanism placement still **open** on cap-25 evidence alone.

### ExECT S1–S4 ladder

| Schema | GPT 4.1-mini | Qwen35b | Read |
| --- | ---: | ---: | --- |
| S1 | 92.3% | 79.0% | Qwen lags narrow S1 policy surface |
| S2 | 80.9% | 82.6% | Qwen ≈ GPT |
| S3 | 72.1% | 72.2% | Matched |
| S4 | 65.5% | 67.5% | Qwen +2.0pp pooled micro; per-family mixed |

**S4 residual burden (GPT):** medication_temporality precision (52 FP); seizure_frequency 45.7% F1. Frequency R1 post-merge and structured slots S2 **do not promote** (arm-reject / inconclusive). Sparse families: policy memo done; bridge work before model sweeps.

**S1–S3 ladder work (done):** Cause bridge K0+K1 promoted S3→S4; investigation guard I0 +5.6pp cap-25; comorbidity cap-25 null, +14pp on 6-doc residual slice.

### DSPy optimizers

Bootstrap cap-25 **reject** on S1; full ladder rungs 0–3 explain ~25pp bridge contribution. Optimizer automation thesis **not supported**. Further compile rungs (BootstrapRS, GEPA) **deferred** until train-demo alignment is fixed.

### Taxonomy primitives

Infrastructure **shipped**; compose primitives for new runs. Blocked: published ExECT CUI pack; Gan Real(300)/Real(150) (data access).

---

## Hybrid exploration sprint (complete)

All cards below are **Done** unless noted. Inspection paths are the source of truth.

| Block | Outcome headline |
| --- | --- |
| Doctrine + inventory | Pivot, skill, mechanism table, registry `decision_scope` retag |
| Gan Axis 1 stage-graph | A3 `g2_candidates_adjudicate` hold 52%; A1/A2/A4/A5 reject (arm) |
| Gan Axis 2 executor | E1/E2 directional; mechanism class open |
| Gan Axis 3 presentation | Table/JSON/bullets 56% vs prose 52% |
| Gan validation ladder | V0/V2/V6 hold; V3–V5/V7 reject |
| Gan Qwen + builders + F0 | Qwen reject; F0 **68.1%** full promote (arm) |
| ExECT S1 stage-graph + executor | 95.8% micro; bridges +23pp; PG0 hold / PG1–PG2 reject |
| ExECT S1 optimizer thesis | Not supported (best 71.7% micro cap-25) |
| ExECT S4 frequency / sparse policy | R1 reject; S2 null; sparse policy memo done |
| ExECT S4 medication G0 | Full val hold operational candidate |
| ExECT S1–S3 bridges | Cause K0+K1 full val; S4 frozen; I0 investigation guard |

**No Gan or ExECT placement grids queued.**

---

## Follow-up tables

### Literature-informed

| Card | Status |
| --- | --- |
| Gan S0 retrieval ablation | Done — R2 hold |
| Gan S0 validation ladder | Done |
| ExECT S1 field-family prompt graph | Done — PG0 hold; PG1/PG2 reject |
| Run metadata audit | Done |
| Fixture-to-real reality-gap audit | **Backlog** |

### Prior-best reanalysis

| Card | Status |
| --- | --- |
| Gan canonical-format port + residual replay | Done — cap-25 hold; slice null |
| ExECT S4 frequency repair R1 | Done — reject (arm) |
| ExECT S4 frequency structured slots S2 | Done — inconclusive |
| ExECT S4 sparse-family policy memo | Done |
| **Replay Gemini under current architecture** | **Next** — see § Next step |

---

## Backlog and deferred

| Item | Status | Note |
| --- | --- | --- |
| Published ExECTv2 reproduction | Blocked | CUI-aware all-family scoring |
| Gan Real(300)/Real(150) | Blocked | Data access |
| Broad ExECT architecture matrix | Deferred | Reopen only with preregistered matrix |
| Optimizer rungs 6–7 (BootstrapRS, GEPA) | Deferred | After train-demo alignment |
| Test holdout confirmation | Deferred | Arms clearing dev + cap gates |
| New ExECT S4 frequency variant | Optional | Only with **new** variant ID; do not rerun R1/S2 |
| Gemini replay (old Gan direct/VR) | **Superseded** | Use current S1/S4 replay in § Next step |

### Lane A clean factor-isolation (GPT)

**Complete** — verification, evidence, prompt, optimizer, and ladder rungs 0–3 on validation. See `exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md`, `gan_s0_lane_a_gpt_cap25_inspection_20260521.md`, `exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md`.

---

## Current decisions (selected)

| Decision | Position |
| --- | --- |
| Active queue | **`docs/planning/kanban_plan.md`** — implementation plan retired |
| Research doctrine | Three-axis exploration; arm vs mechanism language |
| Gan monthly leader | F0 expanded builders prose (68.1% full) |
| Gan default engineering path | Temporal-candidates + VR v1.1 |
| ExECT S4 variant | Frozen K0+K1 cause bridge (2026-05-21) |
| ExECT S4 frequency repair | R1 reject; S2 inconclusive — no rerun unchanged |
| ExECT S1 GPT v4_11 (cap-25) | Reject on GPT |
| ExECT S1 optimizer bootstrap | Reject |
| Qwen S1 v4_11 full | Hold promote blocked |
| Next model work | **Gemini S1 + S4 replay** under frozen variants |

Full decision history and arm-reject guardrails: `exect_negative_probe_synthesis_20260520.md`, `kanban_frozen_threads_history.md`.

---

## Long-term arc

1. **Complete** hybrid cap-25 search (Gan + ExECT placement and targeted Axis-3 cells).
2. **Now:** Gemini replay on frozen S1/S4 (+ optional Gan F0) for model-comparison evidence.
3. **Hygiene:** fixture reality-gap; optional run-manifest metadata improvements from metadata audit.
4. **Later:** published benchmark reproduction when CUI/real-set blockers clear; optimizer compile rungs only with full ladder discipline.
5. Keep registry `decision_scope` and mechanism status doc current; treat Lane A and negative probes as **arm libraries**, not closure.

---

## Reference links (stable)

- Literature review: `docs/planning/multi_stage_llm_clinical_extraction_literature_review_20260521.md`
- Optimizer investigation: `docs/workstreams/optimizer/dspy_optimizer_investigation_20260521.md`
- Taxonomy ontology: `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md`
- ExECT support map: `docs/experiments/exect/exect_field_family_deterministic_support_map_20260520.md`
- Prior-best reanalysis: `docs/experiments/synthesis/prior_best_vs_current_best_reanalysis_20260521.md`
- Phase roadmap (historical): `docs/planning/next_major_phases_20260520.md`
