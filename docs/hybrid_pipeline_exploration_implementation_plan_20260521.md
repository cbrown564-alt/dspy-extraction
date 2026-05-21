# Hybrid Pipeline Exploration — Implementation Plan

Date: 2026-05-21  
Status: Active execution plan (companion to `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`)  
Horizon: ~8–12 weeks of GPT-first exploration, then selective Qwen/full validation  
Skill: `.agents/skills/hybrid-pipeline-exploration/SKILL.md`

---

## Current status (2026-05-21)

| Phase | Status | Notes |
| --- | --- | --- |
| 0 — Doctrine | **Done** | Skill, pivot, Kanban, taxonomy |
| 1 — Inventory | **Done** | Mechanism status table; registry notes on canonical rows |
| 2 — Gan Axis 1 | **Done** | Inspection + registry backfill (10 hybrid-grid rows) |
| 3 — Gan Axis 2 | **Done** | Inspection `docs/experiments/gan/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md` |
| 4 — Gan Axis 3 | **Done** | Inspection `docs/experiments/gan/gan_s0_implementation_variant_gpt_cap25_v1_inspection_20260521.md` |
| 5 — ExECT S1 Axes 1–2 | **Done** | Stage-graph + stage-executor cap-25 grids + inspections |
| 5c — Gan validation ladder | **Done** | `docs/experiments/gan/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md` |
| 6 — ExECT optimizer (Axis 3) | **Done** | Rungs 4a–4c cap-25; thesis **not supported** (best 71.7% micro) |
| 6b — ExECT prompt graph (literature) | **Done** | PG0 hold 95.8%; PG1/PG2 reject — `docs/experiments/exect/exect_s1_field_family_prompt_graph_gpt_cap25_v1_inspection_20260521.md` |
| 7 — Qwen / full validation | **Done (arm reject)** | Qwen g2 cap-25 40% monthly vs GPT E1 52% — `docs/experiments/gan/gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1_inspection_20260521.md` |
| 7b — Gan canonical-format port | **Done (hold, cap-25 only)** | C1 +4pp on cap-25; residual 30-record replay null — `docs/experiments/gan/gan_s0_canonical_format_residual_slice_replay_20260521.md` |
| 8 — Gan exact-frequency slot payload | **Done (hold, cap-25)** | S1 +8pp monthly vs S0 52%; residual 30-record replay null — `docs/experiments/gan/gan_s0_exact_frequency_slot_payload_gpt_cap25_v1_inspection_20260521.md` |
| 8b — Gan expanded builders cap-50 confirm | **Done (confirm, arm)** | B0 68% vs pre-expansion 62% (+6pp) — `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_cap50_v1_inspection_20260521.md` |
| 5d — ExECT S4 residual synthesis | **Done** | Full-val read `docs/experiments/exect/exect_s4_residual_error_analysis_20260521.md`; anchors `…071248Z` (GPT) / `…160914Z` (Qwen) |
| 5e — ExECT S4 frequency surface repair (Axis 3) | **Done (reject, arm)** | R1 post-merge −2.9pp vs R0 on cap-25 — `docs/experiments/exect/exect_s4_frequency_surface_repair_gpt_cap25_v1_inspection_20260521.md` |

**Phase 2 headline:** A3 `g2_candidates_adjudicate` (temporal candidates → single-pass adjudicate) leads at **52%** monthly on cap-25; promoted skeleton A5 `g3_candidates_extract_repair` ties direct at **44%**. Verify-repair erases A3 label gains on this slice (A3 vs A5: 15/25 identical).

**Phase 4 headline:** Table/JSON/bullets presentation (**56%** monthly) beats prose control (**52%**, E1 repro) by **+4pp** on cap-25; three formats tie; mechanism class stays open.

**Phase 5a headline:** S1/S4 `g1_l1_policy_bridges` / `g2_raw_post_bridge` tie at **95.8%** micro on cap-25; bridge contribution **+23pp** vs bridge-free S2; S3 verify-repair and S5 family-split **reject (arm)**.

**Phase 5b headline:** E1/E2 `llm_extract_inline_bridges` / `llm_extract_post_bridges` tie at **95.8%**; pre-vocab hint executors E3–E5 **reject (arm)** (−4.9pp to −2.5pp vs E1).

**Phase 6b headline:** PG0 single-pass holds at **95.8%** micro; PG1 parallel per-family **86.5%** and PG2 sequential prompt graph **87.1%** both **reject (arm)**; PG1 vs PG2 null (24/25 identical).

**Phase 5c headline:** V0/V2/V6 hold at **52%** monthly (25/25 valid); V3–V5 fail valid-count gates (det evidence abstains 13/25); V7 span-check **reject** (50% on 16 valid).

**Next session pull (ordered):**

1. ~~ExECT S1 stage-graph + stage-executor cap-25 grids~~ Done
2. ~~Gan validation ladder V0–V7~~ Done
3. ~~Phase 4 + ladder registry backfill~~ Done (`scripts/backfill_hybrid_cap25_registry.py`, +11 rows)
4. ~~ExECT optimizer thesis rungs 4a–4c~~ Done — inspection `docs/experiments/exect/exect_s1_ladder_optimizer_automation_inspection_20260521.md`
5. ~~50-record Gan presentation confirmation (I1 table)~~ Done — **hold (inconclusive)**; 62% tie on 50 (`docs/experiments/gan/gan_s0_implementation_variant_gpt_cap50_v1_inspection_20260521.md`)
6. ~~ExECT S1 field-family prompt graph (literature card)~~ Done — PG0 hold 95.8%; PG1/PG2 reject (arm); inspection `docs/experiments/exect/exect_s1_field_family_prompt_graph_gpt_cap25_v1_inspection_20260521.md`
7. Do **not** mechanism-close bridge placement, verify-repair, or candidate presentation from cap-25 alone
8. ~~**Phase 7:** Run Gan Qwen cap-25 port of `g2_candidates_adjudicate`~~ Done — reject (arm) 40% monthly
9. ~~**Phase 7b:** Implement + cap-25 run Gan canonical-format port~~ Done — C1 hold +4pp normalized exact
10. ~~**Residual-slice replay C0 vs C1**~~ Done — null on 30-record queue (`docs/experiments/gan/gan_s0_canonical_format_residual_slice_replay_20260521.md`); cap-50 confirm **deferred**
11. ~~**Phase 8 scaffold:** Gan exact-frequency slot payload~~ Done — cap-25 S1 hold +8pp monthly; residual null
12. ~~**Expand slot/candidate builders for arithmetic + unknown strata**~~ **Done (builders)** — 19/30 gold-in-candidate on residual queue (`docs/experiments/gan/gan_s0_residual_candidate_builder_expansion_20260521.md`); slot-payload re-run deferred
13. ~~**Residual-slice replay S0/S1 with expanded builders**~~ **Done** — S0 63.3% / S1 60.0% monthly on hard queue; builders dominate; S1 does not beat S0 — `docs/experiments/gan/gan_s0_exact_frequency_slot_payload_residual_slice_replay_v2_20260521.md`
14. ~~**ExECT S4 frequency surface repair prereg + R1 scaffold**~~ **Done** — prereg + cap-25 R0/R1; R1 **reject (arm)** −2.9pp vs R0 — `docs/experiments/exect/exect_s4_frequency_surface_repair_gpt_cap25_v1_inspection_20260521.md`
15. ~~**Cap-50 prose + expanded builders**~~ **Done** — confirm +6pp vs 62% baseline (`docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_cap50_v1_inspection_20260521.md`)
16. ~~**ExECT S4 full-validation residual error analysis**~~ **Done** — `docs/experiments/exect/exect_s4_residual_error_analysis_20260521.md`
17. ~~**Gan full-validation prereg + F0 run**~~ **Done (promote, arm)** — `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_full_validation_v1_inspection_20260521.md`; F0 **68.1%** monthly vs VR **65.1%** (+3.0pp)
18. ~~**ExECT S4 medication precision guard design**~~ **Done** — `docs/experiments/exect/exect_s4_medication_precision_guard_design_20260521.md` (no-model FP taxonomy + tiered G0–G3 guards)
19. ~~**Next (Gan):** execute full-validation F0~~ **Done** — promote operational (arm); run `…T073432Z` vs VR `…130933Z`
20. ~~**ExECT S4 G0 guard cap-25 + full validation**~~ **Done (hold, operational candidate)** — full-val +11.3pp MT precision, +9.5pp MT F1 — `docs/experiments/exect/exect_s4_medication_precision_guard_gpt_full_validation_v1_inspection_20260521.md`
21. ~~**Next (Gan):** execute expanded builders + VR bundle V1~~ **Done (hold, arm)** — V1 **65.8%** monthly; F0 **68.1%** (−2.3pp); pre-exp VR **65.1%** (+0.7pp) — `docs/experiments/gan/gan_s0_expanded_builders_vr_gpt_full_validation_v1_inspection_20260521.md`
22. ~~**Next (Gan, optional):** targeted builder gaps + residual replay~~ **Done** — builders 24/30 gold-in-candidate; replay v3 **76.7%** monthly (+13.4pp vs v2) — `docs/experiments/gan/gan_s0_expanded_builders_residual_slice_replay_v3_20260521.md`
23. **Next (ExECT S4, optional):** frequency Axis 3 only with **new** `implementation_variant` (structured frequency slots / multi-label retention); do **not** rerun R1 post-merge; do **not** port Gan monthly normalization
24. **Defer (ExECT S4):** onset / when-diagnosed / epilepsy-cause / birth-history model spend until annotation-surface policy is decided; use qualitative queue EA0150, EA0016, EA0137, EA0143, EA0059 for cross-family reads

**S4 residual headline (full validation, GPT v1.2):** pooled micro **65.5%**; dominant burden is **medication_temporality** precision (52 FP, 62.5% F1) and **seizure_frequency** (45.7% F1, 28 FP / 22 FN). Sparse surface families (onset, when_diagnosed) are poor F1 but low support — not primary search budget. See Phase 5d.

---

## Goals

1. Answer **Axis 1** (stage count / decomposition) with clean cap-25 comparisons on Gan S0, then ExECT S1.  
2. Answer **Axis 2** (det vs LLM vs hybrid per stage) for the top 2–3 stage graphs from Axis 1.  
3. Run **Axis 3** implementation sweeps only on winning skeletons.  
4. Retag historical outcomes as **operational freeze**, **reject (arm)**, or **open mechanism** — never upgrade to mechanism reject without review.

---

## Phase 0 — Doctrine and tooling (week 0)

| Task | Deliverable | Owner |
| --- | --- | --- |
| Publish pivot report | `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md` | Done |
| Add agent skill | `.agents/skills/hybrid-pipeline-exploration/SKILL.md` | Done |
| Embed in Kanban | `docs/planning/kanban_plan.md` § Three-axis program | Done |
| Update `dspy-experiment-design` | Arm vs mechanism + link to skill | Done |
| Update `AGENTS.md` | List new skill | Done |
| Taxonomy schema note | `docs/taxonomy/experiment_taxonomy_schema.md` § `decision_scope` | Done |
| Soften prior synthesis header | `hybrid_deterministic_placement_research_synthesis_20260521.md` | Done |
| Negative-probe guardrail | `exect_negative_probe_synthesis_20260520.md` preamble | Done |

**Exit:** Any agent prompt can say `Use hybrid-pipeline-exploration` and get consistent doctrine.

---

## Phase 1 — Inventory and retag (week 0–1)

| Task | Deliverable |
| --- | --- |
| Mechanism status table | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` — open / arm-reject / operational-freeze per mechanism class |
| Registry notes pass | High-value rows: add `"decision_scope": "arm"` or `"operational"` in `notes` (no bulk backfill of 80+ exploratory rows required in week 1) |
| Reopen deferred Gan arm | Preregister `gan_s0_stage_graph_axis1_v1` including **temporal-candidates without repair** and **LLM candidate ID** cells |

**Exit:** Kanban “Open mechanisms” and “Operational defaults” tables are authoritative; no doc claims mechanism closure without review.

---

## Phase 2 — Gan S0 Axis 1: stage-graph grid (week 1–2) — **DONE**

**Comparison group:** `gan_s0_pipeline_stage_graph_gpt_cap25_v1`  
**Fixed:** `gan_2026_fixed_v1:validation` cap-25, GPT 4.1-mini, `gan_frequency_deterministic_v1`, v1.1 prompt family where LLM stages exist, guardrails slice order.  
**Varied:** `pipeline_stage_graph` (Axis 1)  
**Executor control:** where a candidate-generation stage exists, use the current deterministic temporal candidate primitive only. LLM and hybrid candidate generation are **not** part of this group; they move to Phase 3 so Axis 1 does not mix decomposition with executor placement.

| Arm ID | `stage_graph_id` | Description |
| --- | --- | --- |
| A1 | `g1_direct` | Single-pass extract+normalize (L1 baseline) |
| A2 | `g2_extract_repair` | Extract → repair/normalize (no pre candidates) |
| A3 | `g2_candidates_adjudicate` | Deterministic temporal candidates → LLM adjudicate (no VR pass) — **new program variant** |
| A4 | `g3_extract_verify_repair` | Extract → verify → repair without pre candidates |
| A5 | `g3_candidates_extract_repair` | Current promoted skeleton: deterministic temporal candidates → extract/adjudicate → repair |

**Implementation tasks:**

| # | Task | Status |
| --- | --- | --- |
| 1 | Preregistration: `docs/experiments/gan/gan_s0_pipeline_stage_graph_gpt_cap25_v1_preregistration_20260521.md` | Done |
| 2 | Programs: `temporal_candidates_single_pass` + `stage_graph_id` metadata in `gan_frequency_s0.py` | Done |
| 3 | Config batch: `configs/experiments/gan_s0_stage_graph_*_cap25_gpt4_1_mini.json` (5 arms) | Done |
| 4 | Cap-25 runs: `…T012156Z`–`…T012243Z` | Done |
| 5 | Inspection: `docs/experiments/gan/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md` | Done |
| 6 | Registry rows: one per arm, `decision_scope: arm` | **Done** — `scripts/backfill_hybrid_cap25_registry.py` |

**Cap-25 results (monthly frequency):**

| Arm | `stage_graph_id` | Run ID suffix | Monthly | Outcome |
| --- | --- | --- | ---: | --- |
| A3 | `g2_candidates_adjudicate` | `…T012204Z` | **52.0%** | hold → Phase 3 anchor |
| A1 | `g1_direct` | `…T012156Z` | 44.0% | reject (arm) |
| A2 | `g2_extract_repair` | `…T012200Z` | 44.0% | reject (arm) |
| A4 | `g3_extract_verify_repair` | `…T012239Z` | 44.0% | reject (arm); label-duplicate of A2 |
| A5 | `g3_candidates_extract_repair` | `…T012243Z` | 44.0% | reject (arm); label-duplicate of A1 |

**Gates (cap-25):** monthly frequency, schema validity, evidence support; proceed to full validation only for arms within 3pp of best arm or with qualitatively new failure insight.

**Exit:** Ranked stage graphs under deterministic candidate-source control; **no mechanism reject** for verify-repair, candidate generation, or multi-stage pipelines from this phase alone. **Met.**

---

## Phase 3 — Gan S0 Axis 2: per-stage executor grid (week 2–4) — **NEXT SESSION**

**Comparison group:** `gan_s0_stage_executor_gpt_cap25_v1`  
**Fixed:** Primary anchor `g2_candidates_adjudicate` (Phase 2 cap-25 winner, 52% monthly). Secondary optional anchor `g3_candidates_extract_repair` to test whether VR restores or destroys gains vs A3 on matched records.  
**Varied:** `stage_executor` for **candidate generation stage** and optionally **repair stage**

| Cell | Candidate stage | Adjudication stage | Repair stage | Priority |
| --- | --- | --- | --- | --- |
| E1 | deterministic | LLM | none | Required — reproduces A3 baseline |
| E2 | LLM | LLM | none | Required — first LLM candidate isolation |
| E3 | det + LLM merge | LLM | none | If preregistered |
| E4 | deterministic | LLM | LLM VR | Optional — explains A3 vs A5 gap |
| E5 | LLM | LLM | LLM VR | Optional — full LLM candidate + VR |

**Phase 2 context for Phase 3 design:**

- A3 (candidates → adjudicate, no VR) beats A5 (candidates → adjudicate → VR) by **+8pp** monthly on cap-25 despite sharing 15/25 labels with A1/A5.
- Operational default (`g3_candidates_extract_repair`) did **not** win the Axis 1 search on this slice — Phase 3 must test **candidate source**, not assume det-candidates + VR is optimal.
- E4/E5 are diagnostic for the VR stage; primary mechanism question is E1 vs E2 (and E3 if implemented).

**Implementation tasks (next session):**

| # | Task | Status |
| --- | --- | --- |
| 1 | Preregistration: `docs/experiments/gan/gan_s0_stage_executor_gpt_cap25_v1_preregistration_20260521.md` | Done |
| 2 | Implement `llm_temporal_candidates` program path; optional det+LLM merge variant | Done |
| 3 | Add `stage_executor` taxonomy field on configs (extend `ExperimentTaxonomy` if needed) | Done |
| 4 | Equalize prompt budget / context tokens across det vs LLM candidate arms (document in prereg) | Done |
| 5 | Config batch: `configs/experiments/gan_s0_stage_executor_*_cap25_gpt4_1_mini.json` (5–8 arms) | Done |
| 6 | Cap-25 run + inspection with `decision_scope: arm` | Done |
| 7 | **Mechanism review** only if ≥2 candidate implementations agree directionally | Done (directional; class stays open) |

**Exit:** Evidence on “who should build temporal candidates”; operational default update only if arm wins by preregistered margin on cap-25 **and** confirms on 50-record slice or full validation.

---

## Phase 4 — Gan S0 Axis 3: implementation sweep (week 4–5) — **DONE**

**Scope:** Winning graph + executor from Phases 2–3.  
**Varied:** `implementation_variant` — candidate presentation (table vs JSON vs prose vs bullets).

| # | Task | Status |
| --- | --- | --- |
| 1 | Preregistration: `docs/experiments/gan/gan_s0_implementation_variant_gpt_cap25_v1_preregistration_20260521.md` | Done |
| 2 | `format_temporal_candidates_for_prompt` presentation modes + taxonomy field | Done |
| 3 | Config batch: `gan_s0_impl_i{0..3}_*` (4 arms) | Done |
| 4 | Cap-25 runs + inspection | Done |
| 5 | Registry rows | **Done** — `scripts/backfill_hybrid_cap25_registry.py` |

**Cap-25 results (monthly frequency):**

| Arm | implementation_variant | Run suffix | Monthly | Outcome |
| --- | --- | --- | ---: | --- |
| I1 | `cand_table_v1` | `…T013745Z` | **56.0%** | hold |
| I2 | `cand_json_v1` | `…T013756Z` | **56.0%** | hold |
| I3 | `cand_bullets_v1` | `…T013808Z` | **56.0%** | hold |
| I0 | `cand_prose_v1` | `…T013740Z` | 52.0% | reject (arm); E1 repro |

**Exit:** Non-prose presentations beat prose on cap-25; mechanism class “candidate presentation” remains **open** (cap-25 only, tied arms).

---

## Phase 5 — ExECT S1 Axis 1–2 (week 5–8)

**Caveat:** Bridges and label policy confound raw extraction; document `bridge_mode` in every arm (`inline` | `post_module` | `none_diagnostic`).

### 5a — Stage graph (Axis 1) — **DONE**

**Comparison group:** `exect_s1_pipeline_stage_graph_gpt_cap25_v1`

| Arm | Graph | Status |
| --- | --- | --- |
| S1 | `g1_l1_policy_bridges` (production-shaped) | hold — 95.8% micro |
| S2 | `g1_l1_policy_no_bridges` (diagnostic) | hold (diagnostic) — 72.8% |
| S3 | `g2_extract_verify` (verify-repair, bridges off) | reject (arm) — 72.8%, null vs S2 |
| S4 | `g2_raw_post_bridge` (extract → bridge only) | hold — 95.8%, ties S1 |
| S5 | `g3_family_split_merge` (per-family extract → merge) | reject (arm) — 83.3% |

**Cap-25 headline:** S1/S4 tie at **95.8%** micro; inline bridge contribution **+23pp** vs bridge-free (S2). Inspection: `docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md`.

### 5b — Per-stage executor (Axis 2) — **DONE**

On fixed graph `g1_l1_policy_bridges`, vary bridge placement and pre-vocab hint executors.

**Cap-25 results:**

| Arm | `stage_executor` | Micro F1 | Outcome |
| --- | --- | ---: | --- |
| E1 | `llm_extract_inline_bridges` | **95.8%** | hold |
| E2 | `llm_extract_post_bridges` | **95.8%** | hold (null vs E1) |
| E5 | `det_medication_hints_llm_extract` | 93.3% | reject (arm) |
| E4 | `det_seizure_hints_llm_extract` | 92.8% | reject (arm) |
| E3 | `det_all_family_hints_llm_extract` | 90.9% | reject (arm) |

Inspection: `docs/experiments/exect/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md`.

**Do not** claim “H2 pre-vocab closed” without new `implementation_variant` IDs in prereg.

### 5d — ExECT S4 post-full-validation synthesis (week 8+) — **DONE (synthesis); targeted Axis 3 queue open**

**Source:** `docs/experiments/exect/exect_s4_residual_error_analysis_20260521.md`  
**Anchors:** GPT `runs/exect_s4_validation_full_gpt4_1_mini_20260520T071248Z` (65.5% micro); Qwen `runs/exect_s4_validation_full_qwen35b_ollama_20260520T160914Z` (67.5% micro). Treat as **separate model tracks** — Qwen wins pooled micro but GPT wins diagnosis/seizure_type; do not collapse to a single ranking.

**Problem-type split (drives next prereg, not one “better S4 prompt”):**

| Class | Families | Support | Residual shape | Hybrid-program implication |
| --- | --- | ---: | --- | --- |
| Scope / precision | `medication_temporality`, `annotated_medication` | High | 52 MT FPs (GPT); non-ASM leakage; planned/previous over-tag | Axis 3 **narrow precision guard**; prior broad H1 post-classifier **arm-reject** (recall collapse) — do not rerun |
| S4 frequency templates | `seizure_frequency` | Medium | Qualitative co-labels, multi-label blocks, prose≠gold template | ExECT-specific repair only; **not** Gan monthly normalization; R1 post-merge **arm-reject** on cap-25 |
| Sparse annotation surfaces | `onset`, `when_diagnosed`, `epilepsy_cause`, `birth_history` | 3–8 | Plausible clinical outputs ≠ CUIPhrase-like gold | Policy decision before model budget; pooled S4 micro is a poor objective here |
| Near ceiling | `investigation`, `diagnosis`, `seizure_type` | — | v1.2 guard solved investigation; diagnosis ~91% | Freeze as regression guards in any S4 Axis 3 prereg |

**Completed Axis 3 cell (frequency):**

| Arm | `implementation_variant` | Frequency F1 (cap-25) | Outcome |
| --- | --- | ---: | --- |
| R0 | control (v1.2 inline bridge) | 51.0% | hold |
| R1 | post-merge note-anchored repair | 48.1% | **reject (arm)** −2.9pp |

Inspection: `docs/experiments/exect/exect_s4_frequency_surface_repair_gpt_cap25_v1_inspection_20260521.md`. Open cells: structured frequency-slot output, narrower merge policies, prompt/example variants — each needs a **new** variant ID.

**Queued ExECT S4 work (ordered):**

| # | Task | Axis | Gate / note |
| --- | --- | --- | --- |
| 1 | Medication precision guard prereg | 3 | No-model FP taxonomy: non-ASM vs planned/previous vs brand/generic; target MT precision without H1-style recall collapse |
| 2 | Frequency structured-slot or template-retention variant | 3 | ≥+3pp `seizure_frequency` F1 on cap-25; no ≥2pp regression on investigation, seizure_type, annotated_medication |
| 3 | Sparse-family surface policy memo | — | Annotation-faithful vs clinical-normalized vs defer until CUI reproduction |
| 4 | Cross-family qualitative queue | — | EA0150, EA0016, EA0137, EA0143, EA0059 (+ EA0052, EA0136, EA0153, EA0109, EA0179); tag scorer-surface vs over-extraction vs evidence |

**Do not** mechanism-close “S4 hybrid placement” or “frequency repair” from cap-25 R1 alone. Evidence guards may help precision but broad abstention **arm-rejects** from prior work.

---

## Phase 6 — Optimizer as Axis 3 only (week 6–8, parallel-safe)

Resume `exect_s1_ladder_optimizer_automation_v1` **only as Axis 3** on stripped L0/L1 graphs from ExECT ladder — label as `implementation_variant: optimizer_*`, not as architecture discovery.

Gan optimizer cells attach to **winning stage graph** from Phase 2, not direct-only historical ladder.

---

## Phase 7 — Qwen and full validation (week 8+)

| Trigger | Action |
| --- | --- |
| Cap-25 arm wins by preregistered gate | 50-record slice or full 299/40 validation |
| Mechanism review passes | Update operational default in Kanban + registry `freeze`/`promote` with `decision_scope: operational` |
| Qwen | Port **winning cell** only — same `stage_graph_id` and executor tags |
| ExECT S4 full-val residual read complete | Targeted Axis 3 on **medication guard** and **new frequency variant** only; sparse families deferred per `docs/experiments/exect/exect_s4_residual_error_analysis_20260521.md` |
| Gan expanded builders cap-50 confirm | Full-validation prereg for prose + expanded builders (primary Gan confirm path) |

---

## Engineering enablers (ongoing)

| Enabler | Purpose | Priority | Status |
| --- | --- | --- | --- |
| `stage_graph_id` on program variants | Axis 1 explicit in configs/registry | P0 | **Done** — `ExperimentTaxonomy.stage_graph_id`, `GAN_FREQUENCY_S0_STAGE_GRAPH_BY_VARIANT` |
| `stage_executor` taxonomy field | Axis 2 tagging | P0 | **Done** — `ExperimentTaxonomy.stage_executor`, configs E1–E5 |
| `decision_scope` in inspection template | Arm vs mechanism | P0 (docs/templates) | Done |
| Config generator script | Batch cap-25 grids from matrix YAML | P1 — `scripts/scaffold_stage_graph_experiments.py` (planned) | Pending |
| Mechanism status doc | Living open/closed table | P0 | Done; updated post Phase 2 |
| Fractional factorial planner | Reduce arm count while covering Axis 2 | P2 | Pending |

---

## Kanban card mapping

| Card | Phase | Axis | Status |
| --- | --- | --- | --- |
| Gan stage-graph cap-25 grid | 2 | 1 | **Done** |
| Gan stage-executor cap-25 grid | 3 | 2 | **Done** |
| Gan implementation sweep | 4 | 3 | **Done** |
| ExECT S1 stage-graph grid | 5a | 1 | **Done** |
| ExECT S1 executor/bridge grid | 5b | 2 | **Done** |
| ExECT S4 residual synthesis | 5d | — | **Done** — `docs/experiments/exect/exect_s4_residual_error_analysis_20260521.md` |
| ExECT S4 frequency surface repair | 5e | 3 | **Done** — R1 reject (arm); R0 hold |
| Gan expanded builders full validation | 7 | 3 | **Done** — F0 promote 68.1% monthly; V1 hold 65.8%; inspections `…073432Z` / `…074513Z` |
| ExECT S4 medication precision guard | 5d queue | 3 | **Done** — G0 hold operational candidate; full-val `docs/experiments/exect/exect_s4_medication_precision_guard_gpt_full_validation_v1_inspection_20260521.md` |
| Optimizer automation thesis | 6 | 3 | **Done** — 4a–4c reject thesis; partial hold 4a/4c |
| Mechanism status maintenance | 1 | — | Ongoing |
| Phase 2–3 registry backfill | 2–3 | — | **Done** (`scripts/backfill_hybrid_cap25_registry.py`) |
| Phase 4 + validation ladder registry backfill | 4, 5c | — | **Done** (+11 rows) |

**Deprioritized until Phase 3 advances:** broad “closed probe” reruns, Qwen interleaving ports, published benchmark reproduction, ExECT S1 stage-graph grid.

---

## Metrics and gates (all phases)

- **Primary:** dataset-appropriate headline (Gan monthly frequency; ExECT field-family micro F1)  
- **Diagnostics:** schema validity, evidence support, per-stratum tables where preregistered  
- **Cap-25 role:** **search** — accept nulls; rank arms; do not mechanism-reject on null alone  
- **Full validation role:** **confirm** top 1–2 arms per comparison group  

---

## Risks

| Risk | Mitigation |
| --- | --- |
| Config explosion | Cap-25 only; preregister grids; generator script |
| Bridge confound on ExECT | Tag `bridge_mode`; run bridge-free diagnostics in parallel |
| S4 pooled micro hides family divergence | Rank and preregister per-family; GPT vs Qwen as separate tracks |
| Gan frequency mechanisms ported to ExECT | ExECT S4 wants template/co-label surfaces; Gan monthly normalization is wrong target |
| Sparse S4 families inflate “easy wins” | Fix surface policy before cap-25 sweeps on onset/when-diagnosed/cause/birth |
| Retag churn | Mechanism status doc; incremental registry notes |
| Re-litigating old arms | Negative-probe doc = repeat guardrail only; includes S4 H1 temporality, H2 pre-vocab, R1 post-merge |

---

## Definition of done (program level)

The pivot succeeds when:

1. Gan **candidate-source** (det vs LLM) has a cap-25 matrix with inspection and ranked arms. — **Phase 3**
2. At least **four** `stage_graph_id` values have cap-25 metrics on Gan. — **Done** (five graphs: `g1_direct`, `g2_extract_repair`, `g2_candidates_adjudicate`, `g3_extract_verify_repair`, `g3_candidates_extract_repair`)
3. Kanban lists **≥10 open mechanism classes** and **≤5 operational defaults**. — Done
4. Zero inspection docs use “mechanism rejected” without mechanism review section. — Done so far
5. Hybrid placement question is answered **per dataset × task family × stage graph**, not globally. — In progress (Gan Axis 1 partial)
