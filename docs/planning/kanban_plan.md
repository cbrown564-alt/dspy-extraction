# Clinical Extraction Kanban Plan

**Active steering doc** - sole execution board, operational defaults, and next pulls (`docs/planning/kanban_plan.md` only; no top-level alias).

| | |
| --- | --- |
| **Core direction** | `docs/outline.md` |
| **Research doctrine** | `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md` |
| **Mechanism index** | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` |
| **Big-picture synthesis** | `docs/workstreams/hybrid/hybrid_deterministic_placement_research_synthesis_20260521.md` |
| **Gan policy log** | `docs/experiments/gan/gan_s0_policy_pipeline_learning_log.md` |
| **Gan decision synthesis** | `docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md` |
| **Model suite prereg** | `docs/experiments/synthesis/model_suite_frozen_architecture_v1_preregistration_20260522.md` |
| **Frozen run archive** | `docs/planning/kanban_frozen_threads_history.md` |
| **Scorer / dataset guardrails** | `docs/policies/deterministic_scorer_semantics.md`, `docs/datasets/exect/exect_gold_label_audit.md`, `docs/datasets/gan/gan_2026_label_audit.md` |

**Last refreshed:** 2026-05-23. The board is now split into active pulls first, compact historical synthesis second. Detailed completed run ledgers live in the linked logs/inspections rather than inline here.

## Active Priority 1 - Gan S0 Candidate-Builder Gap Work

**Status:** Ready / primary.  
**Decision source:** `docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md`.  
**Working control:** `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy` on the fixed 25-record enriched slice.  
**Operational full-validation default:** Gan F0 expanded builders + prose, GPT 4.1-mini full validation **68.1%** monthly (`...073432Z`).  
**Search model:** GPT 4.1-mini first. Do not transfer failed G5/G6/G6b/G7/G9 arms to Qwen.

### Why This Is The Top Pull

The GPT-first policy/pipeline runway reached a decision point:

| Arm | Slice result | Decision |
| --- | ---: | --- |
| v1.4 no-example control | 36.0% monthly, 56.0% pragmatic, 100% schema/evidence | Keep as GPT slice control |
| Compact hierarchy | 28.0% monthly, 48.0% pragmatic | Reject as tested |
| G5 event table | 8.3% monthly, 37.5% pragmatic | Reject as tested |
| G6 answer selector | 0.0% monthly/pragmatic | Reject as tested |
| G6b seeded answer options | 16.0% monthly, 20.0% pragmatic | Reject as tested |
| G7 candidate-constrained verifier | 36.0% monthly, 56.0% pragmatic | Reject for promotion; ties v1.4 with a second LLM pass |
| G9 targeted examples min7 | 36.0% monthly, 56.0% pragmatic | Reject for promotion; mixed rescues/regressions |

The key finding is candidate coverage, not schema validity or evidence support: current deterministic builders contain the exact gold label for only **5/25** enriched-slice records. Coverage is strong only for counted-window/no-further-events cases and weak or absent for infrequent quantified, frequent quantified, seizure-free, vague-multiple, and cluster-frequency residuals.

### Current Hypothesis

Gan S0 should stay on the `g2_candidates_adjudicate` skeleton, but the next useful improvement is a no-model deterministic candidate-builder gap pass. A verifier or selector cannot repair an empty or incomplete candidate surface; an LLM option layer currently adds schema-valid but semantically wrong `unknown`, no-reference, and zero-rate choices.

### Active Cards

| Card | Status | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- | --- |
| **G11 - Build candidate coverage audit** | Ready | A no-model table for all 25 enriched-slice records with gold label, current candidate labels, v1.4 prediction, candidate coverage flag, and failure family | Gan synthesis | yes | New inspection artifact under `docs/experiments/gan/`; table reconciles with 5/25 coverage claim |
| **G12 - Preregister builder-gap variant** | Ready | A narrow candidate-builder hypothesis with explicit included/excluded patterns and regression cases before code changes | G11 | after G11 | Short prereg/section in inspection; no prompt/model changes hidden in the card |
| **G13 - Implement smallest builder expansion** | Ready | Deterministic candidates for the highest-value uncovered families without changing scorer semantics | G11, G12 | no | Focused tests in `tests/test_gan_temporal_candidates.py`; no unrelated pipeline edits |
| **G14 - Run no-model validation** | Ready | Candidate coverage improves on the enriched slice without broad grammar or primitive regressions | G13 | no | `uv run pytest tests/test_gan_temporal_candidates.py`; `uv run python scripts/validate_primitives.py --errors-only`; coverage audit rerun |
| **G15 - Run one GPT slice only if coverage improves** | Blocked | Compare v1.4 control against builder-gap variant on the same enriched slice | G14 coverage lift | no | Monthly/pragmatic/schema/evidence metrics plus inspection; promotion requires clear lift or preregistered diagnostic value |

### Candidate Families To Consider First

| Family | Why it matters | Example target surface |
| --- | --- | --- |
| Long-window quantified counts | Recurrent exact misses where the note supports a count over a multi-month interval | `2 per 7 month`, `5 per 13 month`, `multiple per 13 month` |
| Grouped recent counts | Gold often groups multiple recent events into the elapsed observation window | counted recent events with implied denominator |
| Cluster spacing plus per-cluster count | Current builders miss cluster labels when spacing and per-cluster count are separated | `1 cluster per 4 day, 2 per cluster` |
| Seizure-free / no-seizure-information boundaries | Some records have no candidate for seizure-free multi-year or no-current-seizure information | seizure-free/no-information category labels |
| Frequent quantified residuals | Current exact coverage is 0/3 in the enriched-slice failure taxonomy | high-frequency current rates |

### Guardrails

- Do not change Gan scorer semantics.
- Preserve raw evidence/prediction artifacts; evidence support remains diagnostic unless a run says otherwise.
- Treat the enriched 25-record slice as a search/diagnostic surface, not a full-validation estimate.
- Do not run Qwen for this work until a GPT slice beats v1.4 or answers a preregistered transferability question.
- Keep failed LLM candidate/verifier/example implementations as arm rejects, not mechanism closure.

## Active Priority 2 - Frozen Model Suite Finish-In-Flight

**Status:** Secondary. Most hosted and local tracks are done; Qwen 27b full ladder is the remaining clean pull when Ollama is idle.  
**Comparison group:** `model_suite_frozen_architecture_v1`.  
**Scope:** model-comparison evidence only (`decision_scope: arm`). Do not promote operational defaults or close hybrid mechanisms from model-suite leaderboard results.

### Frozen Surfaces

| Surface | Frozen program / variant | GPT 4.1-mini anchor | Varied factor |
| --- | --- | ---: | --- |
| ExECT S1 | `exect_s0_s1_field_family_single_pass` + v4_10 policy | 92.3% micro (`...221944Z`) | `model_track` |
| ExECT S4 | `exect_s4_field_family_cause_bridge_k0_k1_single_pass` | 65.5% micro (`...071248Z`) | `model_track` |
| Gan S0 F0 | `g2_candidates_adjudicate` + `cand_prose_expanded_builders_v1` | 68.1% monthly (`...073432Z`) | `model_track` |

### Coverage Matrix

| Model | ExECT S1 full | ExECT S4 full | Gan F0 full | Status |
| --- | ---: | ---: | ---: | --- |
| GPT 4.1-mini | 92.3% | 65.5% | 68.1% | Anchor, not varied |
| Gemini 3.1 Flash-Lite | 90.3% | 66.8% | 72.6% | Done |
| Gemini 3 Flash | 89.9% | 63.2% | 75.3% | Done |
| Claude Sonnet 4.6 | 81.8% | 65.1% | 73.0% | Done |
| GPT 5.5 | 85.7% | 68.7% | 74.9% | Done |
| Qwen 3.6:35b | 79.0% | 67.5% | 64.4% | Done |
| Qwen 3.5:9b | 79.4% | 64.0% | 65.9% | Done |
| Qwen 3.6:27b | Ready | Ready | Ready | Next Ollama pull |

### Active Cards

| Card | Status | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- | --- |
| **M1 - Run Qwen 27b full ladder** | Ready when Ollama idle | Full S1/S4/Gan F0 replay for the remaining local model track | Smokes pass; 35b and 9b done | no, single Ollama job | Detached launcher `scripts/start_qwen27b_model_suite_ladder_detached.ps1`; inspections for all three surfaces |
| **M2 - Update model-suite synthesis table** | Ready after M1 | Paper-facing model profile table with hosted/local tradeoffs, latency, and caveats | M1 if including 27b | yes after M1 outputs | Registry and synthesis docs cite exact runs and metrics |
| **M3 - Decide whether S2/S3 extension is needed** | Deferred | Explicit yes/no for `model_suite_exect_s2_s3_extension_v1` | model-suite synthesis need | yes | Decision note; no runs unless paper argument needs mid-ladder validation |

### Runtime Rules

- Only one Ollama cap/full job at a time.
- Hosted API jobs can run in parallel with a local Ollama job.
- Qwen 27b ExECT config uses bounded `num_ctx=65536`; the earlier 262k-context S1 smoke timed out before predictions.
- Report S4 per-family F1, not pooled micro alone.
- Record latency, tokens/billing for hosted tracks, and Ollama residency/latency for local tracks.

## Active Priority 3 - Research Memory And Mechanism Hygiene

**Status:** Ongoing maintenance.  
**Purpose:** Keep the active board from becoming the historical log again.

| Card | Status | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- | --- |
| **R1 - Keep learning logs as source of detailed run history** | In Progress | New Gan policy/model-backed outcomes go to `gan_s0_policy_pipeline_learning_log.md`, not into full Kanban prose | every meaningful Gan run | yes | Kanban links to the log and records only decision-relevant headline |
| **R2 - Keep mechanism status aligned** | In Progress | Arm rejects do not become mechanism closure unless supported by a mechanism review | synthesis/inspection updates | yes | `hybrid_pipeline_mechanism_status_20260521.md` matches active decisions |
| **R3 - Preserve frozen detail in the archive** | Done / maintenance | Old run IDs, freeze decisions, and completed ladders stay in `kanban_frozen_threads_history.md` | none | yes | Active board remains pull-oriented |

## Recommended Next Pull

1. **G11 - Candidate coverage audit** over the 25-record Gan enriched slice.
2. **G12/G13 - Builder-gap preregistration and smallest deterministic implementation** for uncovered candidate families.
3. **G14 - No-model validation** with focused tests, primitive validation, and coverage rerun.
4. **G15 - One GPT slice only if candidate coverage improves.**
5. **M1 - Qwen 27b model-suite ladder** when Ollama is idle; do not let it block no-model Gan engineering.

Parallel work is cleanest as: one person/agent does G11-G14, another prepares M2 synthesis shell or checks registry/model-suite docs. G13 should stay single-threaded because it changes the shared Gan candidate contract.

## Operational Defaults

| Track | Default | Evidence / caveat |
| --- | --- | --- |
| Gan S0 | Expanded builders + prose F0 for full-validation model comparisons; v1.4 no-example policy is current GPT enriched-slice control | F0 GPT full **68.1%** monthly; v1.4 slice **36.0%** monthly on enriched residuals |
| ExECT S1 | v4_10 + inline bridges on all tracks | GPT full **92.3%** micro; Qwen v4.12 rejected at cap-25 |
| ExECT S2 | Frozen GPT v1.3 | **80.9%** micro; five-family scope |
| ExECT S3 | Frozen GPT v1.2 | **72.1%** micro; accepted comorbidity gap |
| ExECT S4 | `exect_s4_field_family_cause_bridge_k0_k1_single_pass` | GPT full **65.5%** micro; frequency remains weak |

## Historical Summary

The long historical logs are consolidated here so the active board can stay focused. Full run IDs, configs, and freeze decisions are in `docs/planning/kanban_frozen_threads_history.md` and linked inspection docs.

### Gan S0 Arc

Gan S0 became the controlled playground for hybrid deterministic-probabilistic extraction. Early direct guardrails and optimizer/few-shot probes stabilized schema/evidence but did not solve infrequent temporal aggregation. The temporal-candidate pivot introduced deterministic candidate surfacing before adjudication; local Qwen v1.1 reached **65.8%** monthly with 100% evidence and became the local Tier 1 path.

The 2026-05-21 hybrid sprint tested stage graphs, candidate executors, candidate presentation, validation ladders, retrieval, and prior-best reanalysis. The strongest full-validation GPT arm became F0 expanded builders + prose at **68.1%** monthly. That remains the operational full-validation Gan default, while recent GPT enriched-slice policy work shows the next bottleneck is deterministic candidate coverage rather than more generic prompt/example/verifier work.

### ExECT Schema Ladder Arc

ExECT S1 v4.10 is frozen as the GPT dev anchor (**92.3%** micro on validation). S2 v1.3 is frozen at **80.9%** micro, S3 v1.2 at **72.1%**, and S4 v1.2/K0+K1 cause bridge at **65.5%**. The ladder supports the research claim that schema breadth increases extraction burden and that deterministic bridges help some families, but S4 seizure frequency and medication temporality remain major residual weaknesses.

Qwen S1 v4.12 was rejected at cap-25: diagnosis recovered but the intended seizure-type lift did not survive. ExECT S2/S3 model-suite extension is deferred unless the paper needs hosted validation of the mid-ladder Qwen-vs-GPT claim.

### Model Suite Arc

The frozen architecture suite compares model tracks on the same S1/S4/Gan F0 surfaces. Hosted tracks are mostly complete: Gemini 3 Flash leads Gan F0 monthly (**75.3%**) but is model-comparison only; GPT 5.5 leads S4 among completed hosted tracks (**68.7%**) while underperforming GPT 4.1-mini on S1. Local Qwen scaling currently shows 35b stronger on S4 than 9b, while Gan F0 remains below the best hosted tracks. Qwen 27b is the remaining local ladder row.

### Optimizer And Taxonomy Arc

Bootstrap/optimizer probes did not support optimizer automation as the near-term path for S1 or Gan S0. Manual, audit-grounded policy and deterministic scaffolding produced the strongest current evidence. Taxonomy primitives and registry metadata are in place; new deterministic candidate work should compose from typed primitives and run primitive validation after changes.

## Current Decisions

| Decision | Position |
| --- | --- |
| Active queue | `docs/planning/kanban_plan.md` only |
| Research doctrine | Keep arm rejection separate from mechanism closure |
| Primary engineering | Gan deterministic candidate-builder gap analysis |
| Primary model execution | Qwen 27b full ladder when Ollama idle |
| Gan failed GPT-first arms | Do not transfer G5/G6/G6b/G7/G9 to Qwen |
| Gan v1.4 policy | Strongest no-example GPT enriched-slice control |
| Gan F0 model default | Expanded builders + prose remains full-validation operational default |
| ExECT S1 policy | v4_10 all tracks; v4.12 reject at cap-25 |
| Model suite | Model-comparison only; no operational promotion from leaderboard results |
| Gemini/GPT 5.5/Claude results | Useful for model profile, not mechanism closure |
| S2/S3 model-suite extension | Deferred unless paper needs it |

## Backlog And Deferred

| Item | Status | Trigger |
| --- | --- | --- |
| Published ExECTv2 reproduction | Blocked | CUI-aware all-family scoring |
| Gan Real(300)/Real(150) | Blocked | Data access |
| Test holdout confirmation | Deferred | Only for arms clearing dev/cap gates |
| Broad ExECT architecture matrix | Deferred | Reopen only with preregistered matrix |
| Optimizer rungs 6-7 / GEPA | Deferred | After train-demo alignment or a narrow Gan S0 GEPA prereg |
| New ExECT S4 frequency variant | Optional | Requires new variant ID; do not rerun R1/S2 unchanged |
| Targeted Gan examples | Optional | Only as narrow single-family packs after candidate coverage work |
| LLM candidate extraction | Open mechanism | Needs stricter candidate schema and numeric slots before another model spend |
| Candidate-constrained verification | Open mechanism | Revisit only after candidate recall improves |

## Reference Links

- Literature review: `docs/planning/multi_stage_llm_clinical_extraction_literature_review_20260521.md`
- Frozen history: `docs/planning/kanban_frozen_threads_history.md`
- Gan policy learning log: `docs/experiments/gan/gan_s0_policy_pipeline_learning_log.md`
- Gan policy synthesis: `docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md`
- Gan Qwen error taxonomy: `docs/experiments/gan/gan_s0_qwen35b_20260522_error_taxonomy.md`
- Model suite preregistration: `docs/experiments/synthesis/model_suite_frozen_architecture_v1_preregistration_20260522.md`
- Qwen v4.12 reject: `docs/experiments/exect/exect_s1_qwen_v4_12_diagnosis_stabilized_cap25_inspection_20260521.md`
- Hybrid mechanism status: `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`
- Deterministic placement synthesis: `docs/workstreams/hybrid/hybrid_deterministic_placement_research_synthesis_20260521.md`
