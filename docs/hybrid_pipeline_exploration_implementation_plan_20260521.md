# Hybrid Pipeline Exploration — Implementation Plan

Date: 2026-05-21  
Status: Active execution plan (companion to `docs/hybrid_pipeline_research_pivot_20260521.md`)  
Horizon: ~8–12 weeks of GPT-first exploration, then selective Qwen/full validation  
Skill: `.agents/skills/hybrid-pipeline-exploration/SKILL.md`

---

## Current status (2026-05-21)

| Phase | Status | Notes |
| --- | --- | --- |
| 0 — Doctrine | **Done** | Skill, pivot, Kanban, taxonomy |
| 1 — Inventory | **Done** | Mechanism status table; registry notes on canonical rows |
| 2 — Gan Axis 1 | **Done** | Inspection + registry backfill (10 hybrid-grid rows) |
| 3 — Gan Axis 2 | **Done** | Inspection `docs/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md` |
| 4 — Gan Axis 3 | **Done** | Inspection `docs/gan_s0_implementation_variant_gpt_cap25_v1_inspection_20260521.md` |
| 5–7 | **Next** | ExECT S1 stage-graph grid unblocked |

**Phase 2 headline:** A3 `g2_candidates_adjudicate` (temporal candidates → single-pass adjudicate) leads at **52%** monthly on cap-25; promoted skeleton A5 `g3_candidates_extract_repair` ties direct at **44%**. Verify-repair erases A3 label gains on this slice (A3 vs A5: 15/25 identical).

**Phase 4 headline:** Table/JSON/bullets presentation (**56%** monthly) beats prose control (**52%**, E1 repro) by **+4pp** on cap-25; three formats tie; mechanism class stays open.

**Next session pull (ordered):**

1. ~~Gan Axis 3 implementation sweep~~ Done — `gan_s0_implementation_variant_gpt_cap25_v1`
2. **ExECT S1 stage-graph prereg + cap-25 grid** (`exect_s1_pipeline_stage_graph_gpt_cap25_v1`) — document `bridge_mode` every arm
3. Optional: 50-record slice on `cand_table_v1` (or tie-break winner) before operational presentation change
4. Do **not** mechanism-close candidate presentation from cap-25 alone

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
| Publish pivot report | `docs/hybrid_pipeline_research_pivot_20260521.md` | Done |
| Add agent skill | `.agents/skills/hybrid-pipeline-exploration/SKILL.md` | Done |
| Embed in Kanban | `docs/kanban_plan.md` § Three-axis program | Done |
| Update `dspy-experiment-design` | Arm vs mechanism + link to skill | Done |
| Update `AGENTS.md` | List new skill | Done |
| Taxonomy schema note | `docs/experiment_taxonomy_schema.md` § `decision_scope` | Done |
| Soften prior synthesis header | `hybrid_deterministic_placement_research_synthesis_20260521.md` | Done |
| Negative-probe guardrail | `exect_negative_probe_synthesis_20260520.md` preamble | Done |

**Exit:** Any agent prompt can say `Use hybrid-pipeline-exploration` and get consistent doctrine.

---

## Phase 1 — Inventory and retag (week 0–1)

| Task | Deliverable |
| --- | --- |
| Mechanism status table | `docs/hybrid_pipeline_mechanism_status_20260521.md` — open / arm-reject / operational-freeze per mechanism class |
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
| 1 | Preregistration: `docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_preregistration_20260521.md` | Done |
| 2 | Programs: `temporal_candidates_single_pass` + `stage_graph_id` metadata in `gan_frequency_s0.py` | Done |
| 3 | Config batch: `configs/experiments/gan_s0_stage_graph_*_cap25_gpt4_1_mini.json` (5 arms) | Done |
| 4 | Cap-25 runs: `…T012156Z`–`…T012243Z` | Done |
| 5 | Inspection: `docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md` | Done |
| 6 | Registry rows: one per arm, `decision_scope: arm` | **Pending** |

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
| 1 | Preregistration: `docs/gan_s0_stage_executor_gpt_cap25_v1_preregistration_20260521.md` | Done |
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
| 1 | Preregistration: `docs/gan_s0_implementation_variant_gpt_cap25_v1_preregistration_20260521.md` | Done |
| 2 | `format_temporal_candidates_for_prompt` presentation modes + taxonomy field | Done |
| 3 | Config batch: `gan_s0_impl_i{0..3}_*` (4 arms) | Done |
| 4 | Cap-25 runs + inspection | Done |
| 5 | Registry rows | Pending (post-inspection) |

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

### 5a — Stage graph (Axis 1)

**Comparison group:** `exect_s1_pipeline_stage_graph_gpt_cap25_v1`

| Arm | Graph |
| --- | --- |
| S1 | `g1_l1_policy_bridges` (production-shaped) |
| S2 | `g1_l1_policy_no_bridges` (diagnostic) |
| S3 | `g2_extract_verify` (verify-repair, bridges off) |
| S4 | `g2_raw_post_bridge` (extract → bridge only) |
| S5 | `g3_family_split_merge` (per-family extract → merge) — optional if program support exists |

### 5b — Per-stage executor (Axis 2)

On fixed graph, vary:

- diagnosis / seizure / medication: LLM extract vs det-assisted pre-candidates (new shapes, not replay of rejected slice configs)
- bridge: inline vs post (diagnostic for **placement** of benchmark policy)

**Do not** claim “H2 pre-vocab closed” without new `implementation_variant` IDs in prereg.

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
| ExECT S1 stage-graph grid | 5a | 1 | **Ready** (Gan Axis 3 complete) |
| ExECT S1 executor/bridge grid | 5b | 2 | Pending |
| Optimizer automation thesis | 6 | 3 | Deferred |
| Mechanism status maintenance | 1 | — | Ongoing |
| Phase 2–3 registry backfill | 2–3 | — | **Done** (`scripts/backfill_hybrid_cap25_registry.py`) |
| Phase 4 registry backfill | 4 | — | Pending |

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
| Retag churn | Mechanism status doc; incremental registry notes |
| Re-litigating old arms | Negative-probe doc = repeat guardrail only |

---

## Definition of done (program level)

The pivot succeeds when:

1. Gan **candidate-source** (det vs LLM) has a cap-25 matrix with inspection and ranked arms. — **Phase 3**
2. At least **four** `stage_graph_id` values have cap-25 metrics on Gan. — **Done** (five graphs: `g1_direct`, `g2_extract_repair`, `g2_candidates_adjudicate`, `g3_extract_verify_repair`, `g3_candidates_extract_repair`)
3. Kanban lists **≥10 open mechanism classes** and **≤5 operational defaults**. — Done
4. Zero inspection docs use “mechanism rejected” without mechanism review section. — Done so far
5. Hybrid placement question is answered **per dataset × task family × stage graph**, not globally. — In progress (Gan Axis 1 partial)
