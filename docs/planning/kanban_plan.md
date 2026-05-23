# Clinical Extraction Kanban Plan

**Active steering doc** — sole execution board, operational defaults, and next pulls (`docs/planning/kanban_plan.md` only; no top-level alias).

| | |
| --- | --- |
| **Core direction** | `docs/outline.md` |
| **Research doctrine** | `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md` |
| **Mechanism index** | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` |
| **Big-picture synthesis** | `docs/workstreams/hybrid/hybrid_deterministic_placement_research_synthesis_20260521.md` |
| **Agent skill** | `hybrid-pipeline-exploration` |
| **Registry** | `docs/experiments/synthesis/experiment_registry.json` |
| **Model suite prereg** | `docs/experiments/synthesis/model_suite_frozen_architecture_v1_preregistration_20260522.md` |
| **Gan policy/pipeline log** | `docs/experiments/gan/gan_s0_policy_pipeline_learning_log.md` |
| **Scorer / dataset guardrails** | `docs/policies/deterministic_scorer_semantics.md`, `docs/datasets/exect/exect_gold_label_audit.md`, `docs/datasets/gan/gan_2026_label_audit.md` |
| **Frozen run tables** | `docs/planning/kanban_frozen_threads_history.md` |
| **Retired phased plan** | `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md` (archive only) |

**Last refreshed:** 2026-05-23 — **Targeted examples min7 rejected as tested for promotion** (36.0% monthly, 56.0% pragmatic, 100.0% schema/evidence; tied v1.4 with mixed per-record rescues/regressions); **G7 candidate-constrained verifier rejected as tested for promotion** (36.0% monthly, 56.0% pragmatic, 100.0% schema/evidence; tied v1.4 while adding a second LLM pass); **G6 multiple-answer + deterministic selector rejected as tested on GPT 4.1-mini slice** (0.0% monthly/pragmatic; 100.0% schema; strict option filtering collapsed most records to `unknown`); **G5 LLM event-table candidate stage rejected as tested** (8.3% monthly, 37.5% pragmatic, 96.0% schema); **G3 policy-density mini-grid complete** (v1.4 strongest no-example control: 36.0% monthly, 56.0% pragmatic); **Qwen 9b model-suite ladder done** (S1 **79.4%**, S4 **64.0%**, Gan F0 **65.9%** monthly); Qwen 35b Gan F0 full done (`…131822Z`, **64.4%**); **next Ollama pull: Qwen 27b overnight**; Gan S0 policy/pipeline runway is primary engineering (`gan_s0_policy_pipeline_learning_log.md`).

---

## Key workstream: Gan S0 policy and hybrid pipeline runway

**Status:** **Active priority** — learning log `docs/experiments/gan/gan_s0_policy_pipeline_learning_log.md`; current implementation seed `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy`.

**Goal:** Treat Gan seizure-frequency extraction as the focused research playground for policy iteration and hybrid deterministic-probabilistic pipeline design. The immediate research target is not another one-off prompt tweak; it is a disciplined runway that decides which work belongs in deterministic candidate generation, LLM candidate extraction, LLM adjudication, examples, and verifier/repair.

**Decision discipline:** GPT 4.1-mini is the rapid search model; Qwen 3.6:35b is the deep local evaluation model for informative cells. A failed implementation is **reject (arm)** unless a mechanism review explicitly tests multiple implementations or placements.

### Research axes for this runway

| Axis | Question | Current read | Next need |
| --- | --- | --- | --- |
| Candidate selection | Which possible frequency answers should be surfaced? | Deterministic expanded builders are the best current default but low coverage remains | Test LLM event-table / multiple-answer candidates without closing the mechanism from prior JSON failure |
| Guideline density | How much policy text should the adjudicator see? | v1.1 under-specifies grouped events / no-further-events; v1.4 may be more complete but heavier | Compare v1.1, v1.4, and compact hierarchy on same slice |
| Examples | Which examples move hard cases without broad regressions? | Generic LabeledFewShot did not unlock infrequent temporal aggregation | Build targeted examples for grouped events, highest frequency, cluster ambiguity, trigger-conditioned unknown |
| Verification / repair | Should outputs be corrected, and by whom? | Unconstrained VR over-repairs; adjudicate-then-VR was neutral in one slice | Test candidate-constrained judge and deterministic selector over multiple proposed answers |
| Evaluation | How do we avoid fooling ourselves? | Enriched slices explain failure modes but do not estimate full validation | Use slice gates for search, then full validation only for winners |

### Active runway cards

| Card | Status | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- | --- |
| **G1 — Run v1.4 policy slice on GPT 4.1-mini** | Done | Compare v1.4 vs v1.1: flat pragmatic (56%) but +12pp monthly (36%) and normalized (28%) | v1.4 config + slice done | yes | Metrics + brief inspection appended to learning log |
| **G2 — Run v1.4 policy slice on Qwen 35b** | Done | 16.0% monthly (4/25) and 20.0% pragmatic (5/25) on slice. Moved Qwen off unknown default on hard cases, but introduced short-term stability regression cases (e.g., predicting recent stability as seizure-free instead of rate) | G1 | after G1 | Metrics, prediction deltas, over-quantification check |
| **G3 — Preregister policy-density mini-grid** | Done | GPT slice done: compact hierarchy rejected as tested (28.0% monthly, 48.0% pragmatic); v1.4 remains strongest no-example policy control (36.0% monthly, 56.0% pragmatic) | learning log | yes | Config dry run; focused tests pass; inspection `gan_s0_policy_density_gpt_slice_v1_inspection_20260522.md` |
| **G4 — Design targeted example families** | Done | Curated plan for grouped events, short stability after counted events, highest-current-frequency, YTD, trigger-conditioned unknown, cluster ambiguity, and no-reference boundary | none | yes | Example rationale recorded in `gan_s0_targeted_example_families_plan_20260522.md` before model spend |
| **G5 — Prototype LLM event-table candidate stage** | Done | Reject as tested on GPT slice: 8.3% monthly (2/24 valid), 37.5% pragmatic, 96.0% schema, 100% evidence. Event table found evidence rows but did not preserve count/window slots well enough for final adjudication. | G3/G4 helpful but not required | yes | Inspection `gan_s0_event_table_candidate_gpt_slice_v1_inspection_20260522.md` |
| **G6 — Prototype multiple-answer + deterministic selector** | Done | Reject as tested on GPT slice: 0.0% monthly/pragmatic; 100.0% schema; strict answer-option parsing/evidence filtering left most records with no usable candidates and fallback `unknown` | compact hierarchy from G3; G5 failure constraints | yes | Inspection `gan_s0_multiple_answer_selector_gpt_slice_v1_inspection_20260522.md` |
| **G7 — Candidate-constrained judge / verifier** | Done | Reject as tested for promotion: tied v1.4 on same GPT slice (36.0% monthly, 56.0% pragmatic) with 100.0% schema/evidence, but added a second LLM pass and mostly confirmed unchanged labels | G1/G3 plus G5/G6 failure constraints | yes | Inspection `gan_s0_candidate_constrained_verifier_gpt_slice_v1_inspection_20260522.md` |
| **G9 — Test targeted examples min7** | Done | Reject as tested for promotion: tied v1.4 on same GPT slice (36.0% monthly, 56.0% pragmatic, 100.0% schema/evidence) with mixed rescues (`gan_16750`, `gan_15442`, `gan_16645`) and regressions (`gan_14881`, `gan_15193`, `gan_16529`) | G4 design + v1.4 control | yes | Inspection `gan_s0_targeted_examples_min7_gpt_slice_v1_inspection_20260523.md` |
| **G8 — Update learning log after every run** | In Progress | `gan_s0_policy_pipeline_learning_log.md` remains source of truth for policy rationale/outcomes | every Gan policy run | no | New dated entry with run IDs, metrics, caveats, next cells |

### Immediate pull order

1. **G6b seeded hybrid answer options (GPT-first)** — G7 and targeted examples min7 did not improve over v1.4; the next informative cell should test hybrid deterministic+LLM answer options seeded with deterministic candidates and raw rejected options preserved.
2. **Qwen Transfers** — Run confirmatory checks on Qwen 3.6:35b for winning configurations only; do not transfer G5/G6/G7 failed GPT-first arms.

**Do not:** run broad grids or early stage prototypes on Qwen 3.6:35b; use GPT 4.1-mini as the rapid search model to filter first.

**Parallel Execution Note:** Since GPT 4.1-mini runs are hosted (API-backed), they should be launched in parallel terminal sessions while Qwen runs (like the Qwen 27b model-suite ladder) run locally via Ollama.

---

## Secondary workstream: Full model suite alignment

**Status:** **Finish in flight / secondary** — comparison group `model_suite_frozen_architecture_v1` — `docs/experiments/synthesis/model_suite_frozen_architecture_v1_preregistration_20260522.md`.

**Goal:** Run the **same frozen programs**, scorers, and splits across the full target model set for **model-comparison evidence only** (`decision_scope: arm`). Do not mechanism-close hybrid placement or swap operational defaults from model sweeps alone.

**GPT 4.1-mini** remains the **search and reproducibility anchor** (cap-25 discovery, frozen full-validation references). It is not a missing row in the suite — it is the fixed baseline other tracks compare against.

### Target model set

| Model track | Provider | Model config | Smoke | Status |
| --- | --- | --- | --- | --- |
| **Gemini 3 Flash** | Google | `configs/models/gan_s0_gemini3_flash.json` (`gemini-3-flash-preview`) | Done | **Full replay done** — S1 **89.9%**, S4 **63.2%**, Gan F0 **75.3%** monthly |
| **Gemini 3.1 Flash-Lite** | Google | `configs/models/gan_s0_gemini31_flash_lite.json` | Done | **Replay done** — ExECT S1/S4 + Gan F0 |
| **Claude Sonnet 4.6** | Anthropic | `configs/models/gan_s0_claude_sonnet_4_6_anthropic.json` (`claude-sonnet-4-6`) | Done | **Full replay done** — S1 **81.8%**, S4 **65.1%**, Gan F0 **73.0%** monthly |
| **Qwen 3.6:35b** | Ollama (local) | `configs/models/gan_s0_qwen35b_ollama.json` | Done (Win) | **Column done** — ExECT S1/S4 v4.10 full; Gan F0 full **64.4%** monthly (`…131822Z`) |
| **Qwen 3.6:27b** | Ollama (local) | `configs/models/gan_s0_qwen27b_ollama.json`, `configs/models/exect_qwen27b_ollama.json` | Done (Win) | **Full ladder ready** — smokes pass; configs + `scripts/start_qwen27b_model_suite_ladder_detached.ps1`; execute after 35b Gan F0 full |
| **Qwen 3.5:9b** | Ollama (local) | `configs/models/gan_s0_qwen9b_ollama.json`, `configs/models/exect_qwen9b_ollama.json` | Done (Win) | **Full ladder done** — S1 **79.4%**, S4 **64.0%**, Gan F0 **65.9%** monthly (`…180406Z` / `…190626Z` / `…201156Z`) |
| **GPT 5.5** | OpenAI | `configs/models/gan_s0_gpt5_5_openai.json` | Done | **Full replay done** — S1 **85.7%**, S4 **68.7%**, Gan F0 **74.9%** monthly (`…114349Z` / `…115403Z` / `…121010Z`) |

Reference: `docs/policies/model_config_smoke_tests.md`, `model-config-compatibility` skill. Hosted API keys are loaded from the local `.env`; the Claude config expects `ANTHROPIC_API_KEY`.

### Frozen comparison surfaces (same across tracks)

| Surface | Schema | Frozen program / variant | GPT 4.1-mini anchor | Varied factor |
| --- | --- | --- | --- | --- |
| **ExECT S1** | S0/S1 field family | `exect_s0_s1_field_family_single_pass` + v4_10 policy | **92.3%** micro (`…221944Z`) | `model_track` |
| **ExECT S4** | S4 eleven-family | `exect_s4_field_family_cause_bridge_k0_k1_single_pass` | **65.5%** micro (`…071248Z`) | `model_track` |
| **Gan S0 F0** | seizure frequency | `g2_candidates_adjudicate` + `cand_prose_expanded_builders_v1` | **68.1%** monthly (`…073432Z`) | `model_track` |

**Do not** compare stale Round-2 or pre-F0 arms (e.g. Gemini direct full `…101710Z`, old Gan VR) without explicit architecture caveat.

**Excluded from this suite:** ExECT S2/S3 (deferred — `model_suite_exect_s2_s3_extension_v1` if paper needs mid-ladder validation). Qwen S1 v4.12 (separate arm; **reject at cap-25**).

### Coverage matrix (frozen architecture replay)

| Model | ExECT S1 full | ExECT S4 full | Gan F0 full | Inspection / prereg |
| --- | --- | --- | --- | --- |
| GPT 4.1-mini | **92.3%** freeze | **65.5%** freeze | **68.1%** freeze | Anchor — not varied |
| Gemini 3.1 Flash-Lite | **90.3%** done | **66.8%** done | **72.6%** done | `exect_gemini_ladder_replay_v1_inspection_20260521.md` |
| Gemini 3 Flash | **89.9%** done | **63.2%** done | **75.3%** done | `model_suite_gemini3_flash_full_validation_v1_inspection_20260522.md` |
| Claude Sonnet 4.6 | **81.8%** done | **65.1%** done | **73.0%** done | `model_suite_claude_sonnet_4_6_full_validation_v1_inspection_20260522.md` |
| Qwen 3.6:35b | 79.0% (v4.10) | 67.5% | **64.4%** done (`…131822Z`) | cap-25 `gan_s0_expanded_builders_prose_qwen_cap25_v1_inspection_20260522.md` |
| Qwen 3.6:27b | **Ready** | **Ready** | **Ready** | Deferred overnight — `start_qwen27b_model_suite_ladder_detached.ps1` |
| Qwen 3.5:9b | **79.4%** done | **64.0%** done | **65.9%** done | `model_suite_qwen9b_full_validation_v1_inspection_20260522.md` |
| GPT 5.5 | **85.7%** done | **68.7%** done | **74.9%** done | `model_suite_gpt5_5_full_validation_v1_inspection_20260522.md` |

### Sequencing

**Runtime:** one Windows laptop — hosted API calls (GPT 4.1-mini sweeps) may run **in parallel** (in separate terminal windows/sessions) with one Ollama job (local Qwen runs); **never two Ollama jobs at once**.

| Phase | Scope | Notes |
| --- | --- | --- |
| **0 — Provider plumbing (first)** | ~~Claude Sonnet 4.6 smokes~~ **done**; ~~Qwen 3.6:27b config + tag + smokes~~ **done**; ~~Qwen 3.5:9b smoke~~ **done** | Local smokes pass; hosted full replays unblocked; 27b ExECT uses bounded `num_ctx=65536` after 262k-context timeout |
| **1 — Complete 35b column** | ~~Gan F0 Qwen cap-25~~ **done** → ~~full validation (299)~~ **done** (`…131822Z`, 64.4% monthly) | Cap-25 48.0%; full 64.4%; S1 v4.12 **reject (arm)** |
| **2 — Hosted full replays** | Gemini 3 Flash, GPT 5.5 on S1/S4/Gan F0 | Port from 3.1 Flash-Lite / GPT 4.1-mini templates |
| **3 — Claude full replay** | ~~S1/S4/Gan F0~~ **Done** | `…090828Z` / `…093634Z` / `…095634Z` |
| **4 — Local scaling ladder** | ~~Qwen **9b** full ladder~~ **done** → Qwen **27b** overnight | 9b inspection `model_suite_qwen9b_full_validation_v1_inspection_20260522.md`; 27b: `start_qwen27b_model_suite_ladder_detached.ps1` |
| **5 — Synthesis** | Provider tables + ExECT model-profile memo | Registry + paper-facing; Gemini Gan F0 **model-comparison only** |

**Gates:** same splits and scorers as GPT anchors; v4_10 S1 policy on **all** tracks; report per-family breakdown on S4; record latency, tokens, and billing for hosted tracks; Ollama residency for local tracks.

**Skills:** `model-config-compatibility`, `experiment-run-lifecycle`, `dspy-experiment-design`, `windows-portability`.

---

## Secondary active pulls under model suite

### Qwen S1 v4.12 diagnosis-stabilized follow-up

**Status:** **Done — reject (arm) at cap-25** — inspection `docs/experiments/exect/exect_s1_qwen_v4_12_diagnosis_stabilized_cap25_inspection_20260521.md`.

**Goal:** Preserve the Qwen v4.11 S1 seizure-type lift while repairing the diagnosis regression that blocked promotion.

| Step | Scope | Notes |
| --- | --- | --- |
| 1 | ~~**Implement v4.12 prompt policy**~~ | **Done** — `exect_s0_s1_field_family_v4_12_label_policy`; prompt-only, no scorer/bridge change |
| 2 | ~~**Preregister + configs**~~ | **Done** — `docs/experiments/exect/exect_s1_qwen_v4_12_diagnosis_stabilized_preregistration_20260521.md`; configs under `configs/experiments/exect_s1_qwen_v4_12_diagnosis_stabilized_*.json` |
| 3 | ~~**GPT cap-25 guardrail**~~ | **Done** — `…095259Z`: micro **93.8%**, diagnosis **97.6%**, seizure **92.3%** (−2.0pp vs v4_10 cap-25 95.8%; within cap-25 guardrail noise) |
| 4 | ~~**Qwen cap-25**~~ | **Reject (arm)** — `…095620Z`: micro **83.8%**, diagnosis **97.6%** (+2.4pp vs v4_10 cap), seizure **66.7%** (+0pp vs v4_10 cap; **−11.6pp vs v4_11 cap**); prereg +8pp seizure gate failed |
| 5 | ~~**Qwen full validation**~~ | **Blocked** — cap-25 gate did not pass |
| 6 | ~~**Inspection + registry**~~ | **Done** — cap-25 inspection + registry updated |

**Baselines:** Qwen v4.10 H1 full `…210722Z` (micro 79.0%, diagnosis 95.1%, seizure 55.7%); held Qwen v4.11 full `…231850Z` (micro 84.3%, diagnosis 90.0%, seizure 74.2%).

**Gates:** full validation should keep seizure within 2pp of v4.11, improve diagnosis by at least 3pp over v4.11, and avoid medication regression ≥2pp versus v4.10. Promotion remains blocked if diagnosis stays near 90.0%.

**Skills:** `exect-label-policy-alignment`, `dspy-experiment-design`, `experiment-run-lifecycle`.

*Model suite track:* Qwen 3.6:35b · ExECT S1 surface.

---

### Qwen Gan F0 port (three-provider table)

**Status:** **Full validation done** — `runs/gan_s0_expanded_builders_prose_full_validation_qwen35b_ollama_20260522T131822Z` (**64.4%** monthly, 99.7% schema, 100% evidence, ~14.5 s/rec, 74%/26% CPU/GPU).

**Goal:** Complete the Gan S0 **F0** model-comparison table with Qwen3.6:35b on the same `cand_prose_expanded_builders_v1` skeleton as GPT (**68.1%** monthly) and Gemini (**72.6%**).

| Step | Scope | Notes |
| --- | --- | --- |
| 1 | ~~**Preregister** Qwen arm~~ | **Done** — `gan_s0_expanded_builders_prose_qwen_full_validation_v1_preregistration_20260521.md` |
| 2 | ~~**Smoke** (3 records)~~ | **Done** — `…095443Z`: schema **100%**, evidence **100%**; 74%/26% CPU/GPU offload |
| 3 | ~~**Cap-25 gate**~~ | **Done** — `…091442Z`: monthly **48.0%**, schema **100%**, evidence **100%**; duplicate cache replay `…104242Z` |
| 4 | ~~**Full validation** (299)~~ | **Done** — `…131822Z`: monthly **64.4%**, schema **99.7%**, evidence **100%** |

**Gates:** cap-25 schema/evidence gates **passed**; full run is confirmatory model-comparison only (`decision_scope: arm`).

*Model suite track:* Qwen 3.6:35b · Gan F0 surface.

---

### Model suite — provider plumbing (phase 0)

**Status:** **Done — local provider plumbing complete** — hosted full replays and local scaling ladder unblocked.

| Model | Next action |
| --- | --- |
| Claude Sonnet 4.6 | ~~Full validation~~ **Done** — inspection `model_suite_claude_sonnet_4_6_full_validation_v1_inspection_20260522.md` |
| Qwen 3.6:27b | ~~Confirm Ollama tag; add model config; smoke all 3 surfaces~~ **Done** — tag `qwen3.6:27b`; Gan F0 `runs/gan_s0_expanded_builders_prose_smoke_qwen27b_ollama_20260522T091754Z` (schema/evidence 100%); ExECT S1 `runs/exect_s0_s1_smoke_qwen27b_ollama_20260522T095301Z` (micro 94.7%, evidence 100%); ExECT S4 `runs/exect_s4_smoke_qwen27b_ollama_20260522T102006Z` (micro 68.0%, evidence 100%) |
| Qwen 3.5:9b | ~~Run pending smoke on Windows (`gan_s0_qwen9b_ollama.json`)~~ **Done** — `runs/gan_s0_smoke_qwen9b_ollama_20260522T092032Z` (schema/evidence 100%; compatibility only) |
| Gemini 3 Flash | ~~Port frozen-architecture configs~~ **Done** — inspection `model_suite_gemini3_flash_full_validation_v1_inspection_20260522.md` |
| GPT 5.5 | ~~Full replay~~ **Done** — inspection `model_suite_gpt5_5_full_validation_v1_inspection_20260522.md` |

---

### Replay Gemini under current S-level architecture

**Status:** **Done** — inspection `docs/experiments/exect/exect_gemini_ladder_replay_v1_inspection_20260521.md`.

**Goal:** Decide whether prior Gemini champion evidence still matters under **today’s** frozen programs, scorers, bridges, and splits — not under Round-2 direct/verify-repair Gan arms.

| Step | Scope | Notes |
| --- | --- | --- |
| 1 | ~~**Preregister** comparison group `exect_gemini_ladder_replay_v1`~~ | **Done** — `exect_gemini_ladder_replay_v1_preregistration_20260521.md`; configs under `configs/experiments/exect_*_gemini31_flash_lite.json` |
| 1b | ~~**S1/S4 smoke** (3 records each)~~ | **Done** — `…093432Z` / `…093445Z` |
| 2 | ~~**ExECT S1 full validation**~~ | **Done** — Gemini **90.3%** micro (`…093501Z`); GPT 92.3%, Qwen 79.0% |
| 3 | ~~**ExECT S4 full validation**~~ | **Done** — Gemini **66.8%** micro (`…093556Z`); GPT 65.5%, Qwen 67.5%* |
| 4 | **Optional Gan F0** | Port **expanded builders + prose** monthly leader — **Done** Gemini 72.6% vs GPT 68.1% |

**Historical Gemini (stale architecture — do not treat as current defaults):**

- Gan direct full: `…101710Z` — 63.9% monthly (direct path, pre–temporal-candidates promotion)
- Gan VR cap-25: `…101555Z` — evidence +8.6pp vs direct but schema/Purist regress — **no VR scale-up**

**Gates:** same splits and scorers as GPT/Qwen anchors; report as **model-comparison** evidence (`decision_scope: arm`); do not mechanism-close hybrid placement from Gemini alone.

**Skills:** `model-config-compatibility`, `experiment-run-lifecycle`, `dspy-experiment-design`, `dataset-audit-first`.

**Parallel hygiene (non-blocking):** fixture-to-real reality-gap audit — done (`fixture_to_real_reality_gap_audit_20260521.md`).

---

## Current research focus

**Mode:** **Gan S0 policy and hybrid pipeline exploration** — policy iteration, candidate-generation design, example strategy, and verifier/repair placement on the seizure-frequency task. The model suite remains a secondary finish-in-flight workstream for frozen-architecture model comparison.

**Doctrine (unchanged):** Distinguish **reject (arm)** vs **reject (mechanism)** vs **operational freeze**. Operational defaults are not mechanism-closed. See pivot doc and `hybrid-pipeline-exploration` skill.

**Three-axis program (2026-05-21):** Prior Gan and ExECT cap-25 grids for stage graph, executor, and targeted Axis-3 cells remain the evidence base. The new Gan runway reopens **implementation and policy search** on the winning Gan skeleton and adjacent open mechanisms; do not rerun identical probe configs without a new implementation variant.

### Experimentation model

| Phase | Rule |
| --- | --- |
| Search | GPT 4.1-mini slices/cap-25 — ALL broad policy, density grids, example families, candidate stage prototypes, and verifier sweeps run here first to rank and select candidates. Can be run in parallel with local Ollama scaling runs. |
| Confirm | Qwen 3.6:35b — run only for key confirmatory evaluations of successful GPT-derived configurations or specific transferability tests. |
| Model suite | Secondary: finish **frozen** S1/S4/Gan F0 target tracks; one `model_track` factor |
| Qwen local | Detached launchers on Windows; no IDE background for cap-25/full; run in parallel/offline |
| Comparison groups | One primary `varied_factor` per group; name axis in prereg |

---

## Operational defaults (frozen for runs)

| Track | Default | Evidence |
| --- | --- | --- |
| **Gan S0** | Expanded builders + prose (F0); temporal-candidates + VR remains engineering baseline | F0 full val **68.1%** monthly (`…073432Z`) vs VR **65.1%** |
| **ExECT S1** | **v4_10 + inline bridges on all tracks** | GPT **92.3%** micro full (`…221944Z`); Qwen v4.12 **reject (arm)** at cap-25; v4.11 full held on diagnosis drift |
| **ExECT S2–S3** | GPT frozen ladder | S2 **80.9%**, S3 **72.1%** micro |
| **ExECT S4** | `EXECT_S4_VARIANT` = `exect_s4_field_family_cause_bridge_k0_k1_single_pass`; G0 medication precision guard hold | **65.5%** micro GPT (`…071248Z`); cause bridge +10.6pp cause F1 full |

**Open mechanism classes** (grid-search if revisiting): optimal stage count; LLM vs det candidate generation; S1 bridge placement; per-family det on S2–S4. Full table: `hybrid_pipeline_mechanism_status_20260521.md`.

---

## What we know now

### Gan S0 F0 (expanded builders prose, full validation)

| Model | Monthly | Notes |
| --- | ---: | --- |
| GPT 4.1-mini | 68.1% | Operational arm promote (search anchor) |
| Gemini 3.1 Flash-Lite | **72.6%** | Model-comparison only — **no operational promotion** |
| Gemini 3 Flash | **75.3%** | Model-comparison only — leads suite on monthly; S4 pooled micro below anchors |
| Claude Sonnet 4.6 | **73.0%** | Model-comparison only — 98.0% schema, ~5 s/rec |
| Qwen 3.6:35b | **64.4%** full | `gan_s0_expanded_builders_prose_qwen_cap25_v1_inspection_20260522.md` |
| Qwen 3.5:9b | **65.9%** full | Model-comparison only — 92.3% schema; ~7.4 s/rec; `model_suite_qwen9b_full_validation_v1_inspection_20260522.md` |
| GPT 5.5 | **74.9%** | Model-comparison only — S1 below GPT anchor; S4/Gan F0 above |

### ExECT S1–S4 ladder (GPT anchor vs partial suite)

| Schema | GPT 4.1-mini | Qwen 3.6:35b | Qwen 3.5:9b | Gemini 3.1 Flash-Lite | Gemini 3 Flash | Claude Sonnet 4.6 | Read |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| S1 | 92.3% | 79.0% (v4.10) | **79.4%** | 90.3% | **89.9%** | 81.8% | GPT 5.5 **85.7%** — seizure_type gap vs GPT |
| S2 | 80.9% | 82.6% | — | — | — | Qwen ≈ GPT; Gemini not replayed |
| S3 | 72.1% | 72.2% | — | — | — | Qwen matched; Gemini not replayed |
| S4 | 65.5% | 67.5% | **64.0%** | 66.8% | **63.2%** | 65.1% | GPT 5.5 **68.7%** — above GPT anchor; Flash below |

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
| Fixture-to-real reality-gap audit | Done — `docs/experiments/synthesis/fixture_to_real_reality_gap_audit_20260521.md` |

### Prior-best reanalysis

| Card | Status |
| --- | --- |
| Gan canonical-format port + residual replay | Done — cap-25 hold; slice null |
| ExECT S4 frequency repair R1 | Done — reject (arm) |
| ExECT S4 frequency structured slots S2 | Done — inconclusive |
| ExECT S4 sparse-family policy memo | Done |
| **Full model suite alignment** | **Secondary finish-in-flight** — see § Secondary workstream |
| **Replay Gemini 3.1 Flash-Lite** | **Done** — ExECT + Gan F0 |
| **Qwen Gan F0 port** | **35b + 9b full done** — 27b ladder next |

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
| Gemini replay (old Gan direct/VR) | **Superseded** | Use frozen-architecture suite in § Secondary workstream |
| Claude Sonnet 4.6 model config | **Full replay done** | S1 **81.8%**, S4 **65.1%**, Gan F0 **73.0%** monthly (`…090828Z` / `…093634Z` / `…095634Z`) |
| Qwen 3.6:27b model config | **Smokes pass** | Phase 0 done; full ladder after 35b column. ExECT config uses bounded `num_ctx=65536`; 262k-context S1 attempt `runs/exect_s0_s1_smoke_qwen27b_ollama_20260522T092112Z` timed out before predictions. |
| Qwen 3.5:9b full ladder | **Done** | S1 **79.4%**, S4 **64.0%**, Gan F0 **65.9%** monthly (`…180406Z` / `…190626Z` / `…201156Z`) |
| Gemini 3 Flash frozen replay | **Done** | S1 **89.9%**, S4 **63.2%**, Gan F0 **75.3%** monthly (`…111119Z` / `…111330Z` / `…111541Z`) |
| GPT 5.5 frozen replay | **Done** | S1 **85.7%**, S4 **68.7%**, Gan F0 **74.9%** monthly |
| ExECT S2/S3 model suite extension | **Deferred** | `model_suite_exect_s2_s3_extension_v1` if paper needs it |

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
| Qwen S1 v4.12 | **Reject (arm) at cap-25** — diagnosis restored, seizure lift lost |
| Qwen S1 v4.12 full | **Blocked** — cap-25 gate failed |
| Gan policy/pipeline runway | **Major active priority** — living log + v1.4 policy slice ready; GPT rapid search before Qwen deep eval |
| Model suite workstream | **Secondary finish-in-flight** — eight tracks (3 local Qwen + 4 hosted + GPT anchor) on frozen S1/S4/Gan F0; phase-0 local plumbing complete |
| Model suite prereg | `model_suite_frozen_architecture_v1_preregistration_20260522.md` |
| ExECT S1 policy | **v4_10 all tracks** — v4_12 reject (arm) |
| Gemini Gan F0 lead | **Model-comparison only** — no operational promotion |
| Next Ollama pull | **Qwen 27b overnight** (`start_qwen27b_model_suite_ladder_detached.ps1`) |
| Next engineering | **Gan targeted examples or G6b seeded hybrid answer options** (primary) + **27b model-suite ladder** when Ollama idle |
| Hosted full replays | **GPT 5.5 done** — Gemini 3 Flash + Claude **done** |
| Local scaling order | 35b **done** → **9b done** → **27b overnight** |

Full decision history and arm-reject guardrails: `exect_negative_probe_synthesis_20260520.md`, `kanban_frozen_threads_history.md`.

---

## Long-term arc

1. **Complete** hybrid cap-25 search (Gan + ExECT placement and targeted Axis-3 cells).
2. **Now:** **Gan S0 policy/pipeline runway** — rapid GPT search over policy density, candidate extraction, examples, and verifier/repair; Qwen 35b deep evaluation for winners. G5/G6 candidate-stage arms and G7 candidate-constrained verification are rejected as tested for promotion; next pull should improve candidate coverage or add targeted examples.
3. **In flight:** **Full model suite alignment** — Qwen **9b done**; Qwen **27b** overnight; hosted full replays done.
4. **Next synthesis:** convert Gan policy/pipeline outcomes into a staged hybrid design recommendation, then update mechanism status only when evidence warrants it.
5. **Later:** published benchmark reproduction when CUI/real-set blockers clear; optimizer compile rungs only with full ladder discipline.
6. Keep registry `decision_scope` and mechanism status doc current; treat Lane A and negative probes as **arm libraries**, not closure.

---

## Reference links (stable)

- Literature review: `docs/planning/multi_stage_llm_clinical_extraction_literature_review_20260521.md`
- Optimizer investigation: `docs/workstreams/optimizer/dspy_optimizer_investigation_20260521.md`
- Taxonomy ontology: `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md`
- ExECT support map: `docs/experiments/exect/exect_field_family_deterministic_support_map_20260520.md`
- Prior-best reanalysis: `docs/experiments/synthesis/prior_best_vs_current_best_reanalysis_20260521.md`
- Hosted model matrix (historical): `docs/experiments/gan/gan_s0_hosted_model_comparison_matrix.md`
- Gemini 3.1 replay: `docs/experiments/exect/exect_gemini_ladder_replay_v1_inspection_20260521.md`
- Gan F0 Gemini: `docs/experiments/gan/gan_s0_expanded_builders_prose_gemini_full_validation_v1_inspection_20260521.md`
- Qwen Gan F0 prereg: `docs/experiments/gan/gan_s0_expanded_builders_prose_qwen_full_validation_v1_preregistration_20260521.md`
- Qwen Gan F0 cap-25: `docs/experiments/gan/gan_s0_expanded_builders_prose_qwen_cap25_v1_inspection_20260522.md`
- Gan policy/pipeline learning log: `docs/experiments/gan/gan_s0_policy_pipeline_learning_log.md`
- Model suite umbrella prereg: `docs/experiments/synthesis/model_suite_frozen_architecture_v1_preregistration_20260522.md`
- v4_12 cap-25 reject: `docs/experiments/exect/exect_s1_qwen_v4_12_diagnosis_stabilized_cap25_inspection_20260521.md`
