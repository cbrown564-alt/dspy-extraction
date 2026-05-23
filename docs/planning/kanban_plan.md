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
| **Cursor SDK pilot** | `docs/workstreams/cursor_sdk/cursor_sdk_research_workflows_20260523.md` |
| **Cursor SDK assessment** | `docs/workstreams/cursor_sdk/cursor_sdk_value_reliability_assessment_20260523.md` |
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
| **G11 - Build candidate coverage audit** | Done | No-model audit for all 25 enriched-slice records with gold label, current candidate labels, v1.4 prediction, candidate coverage flag, and failure family: `docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md` plus JSON companion | Gan synthesis | yes | `uv run python scripts/audit_gan_candidate_builder_gap.py`; reconciles with 5/25 coverage claim |
| **G12 - Preregister builder-gap variant** | Done | Narrow candidate-builder hypothesis with included/excluded patterns and regression cases before code changes: `docs/experiments/gan/gan_s0_candidate_builder_gap_preregistration_20260523.md` | G11 | after G11 | No prompt/model/scorer changes hidden in the card |
| **G13 - Implement smallest builder expansion** | Done | `gan_s0_candidate_builder_gap_v1` deterministic candidates cover high-value uncovered families without changing scorer semantics | G11, G12 | no | Focused tests added in `tests/test_gan_temporal_candidates.py`; no scorer/prompt/model edits |
| **G14 - Run no-model validation** | Done | Candidate coverage improved from 5/25 to 23/25 on the enriched slice; remaining misses are seizure-free `multiple year` boundary cases | G13 | no | `uv run pytest tests/test_gan_temporal_candidates.py`; `uv run python scripts/validate_primitives.py --errors-only`; `uv run python scripts/audit_gan_candidate_builder_gap.py` |
| **G15 - Run one GPT slice only if coverage improves** | Done | Builder-gap v1 beat v1.4 on the same enriched slice: 92.0% monthly / 96.0% pragmatic / 100% schema and evidence; inspection `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md` | G14 coverage lift met | no | Run `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z`; promotion limited to enriched-slice gate |
| **G16 - Broader GPT validation for builder-gap v1** | Ready / next pull | Test whether the builder expansion generalizes beyond the enriched slice before Qwen transfer or operational default changes | G15 | no | Broader validation metrics plus inspection; compare against F0 expanded builders + prose and v1.4 slice caveats |

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

## Active Priority 4 - Cursor SDK Research Operations

**Status:** Promoted / constrained.  
**Decision source:** `docs/workstreams/cursor_sdk/cursor_sdk_research_workflows_20260523.md`; assessment `docs/workstreams/cursor_sdk/cursor_sdk_value_reliability_assessment_20260523.md`.  
**Scope:** Review-only research operations. Cursor/Composer output is not a benchmark model track, scorer, clinical extractor, DSPy optimizer result, or source-of-truth update.  
**Budget guard:** User-configured Cursor spend limit: GBP 15.

### Purpose

Use the Cursor Python SDK as a background drafting and review assistant for source-heavy research operations: memory candidates, experiment-inspection drafts, paper claim maps, model-compatibility scans, and hygiene reports. The pilot passed, but the authority boundary is now explicit: SDK output stays in draft folders until human/Codex review promotes selected findings.

### Assessment

The SDK is valuable for broad review-only synthesis and drift detection. C1-C3 produced useful drafts with source paths and no source-of-truth edits. Later drafts also surfaced useful technical leads, including a G16 full-validation inspection draft that flagged a slice/full candidate-emission mismatch and a model-compatibility report that identified adapter/config risk.

Reliability is not high enough for unattended mutation in the shared dirty workspace. The `test-mutations` workflow restored `src/clinical_extraction/gan/temporal_candidates.py` to committed HEAD rather than the pre-session dirty baseline, so mutating SDK workflows are blocked unless run in a disposable clone/worktree with explicit rollback guarantees.

### Active Cards

| Card | Status | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- | --- |
| **C1 - Test automated research-memory pass** | Done | Prompt rehearsal plus live review-only candidate written to `docs/memory/dreams/20260523T093633Z_cursor_sdk_memory_pass_candidate.md`; candidate is useful for C4 scoring but not promoted memory | Cursor SDK setup; Windows bridge-discovery patch in `scripts/cursor_sdk_workflows.py` | yes | `uv run python scripts/cursor_sdk_workflows.py check`; `uv run python scripts/cursor_sdk_workflows.py memory-pass`; reviewed against `docs/memory/README.md` promotion checklist |
| **C2 - Test experiment-inspection draft worker** | Done | Draft produced for G15 slice (`20260523T101141Z_inspection_draft.md`); names metadata, accuracy, run facts, and lists required human checks | Cursor SDK setup; run/config pointer | yes | Draft names dataset, split, model/provider, program variant, scorer mode, normalization rules, evidence policy, caveats, and required human checks |
| **C3 - Test background repo hygiene scan** | Done | Hygiene scan completed (`20260523T101227Z_hygiene_scan.md`); identified 12 findings ranked by risk | Cursor SDK setup | yes | Findings are source-linked and do not propose direct scorer, dataset, registry, or operational-default changes |
| **C4 - Decide whether to keep Cursor SDK workflow** | Done | SDK workflows promoted/accepted on 2026-05-23; SDK remains as review-only operations assistant | C1, C2, C3 | no | At least two useful drafts and zero source-of-truth edits by the SDK agent before promotion |
| **C5 - Run targeted G16 inspection draft** | Ready / evening-suitable | Review-only draft reconciles `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z`, F0 control, slice-vs-full candidate mismatch, and rerun criteria | G16 artifact exists; SDK guardrails | yes | Draft lists primary run artifacts, controls, scorer mode, caveats, and required human checks; no Kanban/registry edits |
| **C6 - Run paper claim-map refresh** | Ready / evening-suitable | Draft paper claim map ties current Gan/model-suite claims to run IDs, metrics, decision scopes, and unsupported claims | registry and synthesis docs available | yes | `paper-synthesis` output includes exact run IDs and flags unsupported or post-narrative claims |
| **C7 - Run post-refresh hygiene scan** | Ready / evening-suitable | Fresh drift report after this Kanban refresh; checks memory, mechanism status, workflow index, registry gaps, and SDK routing | C4 assessment | yes | Findings are ranked by risk and keep source-of-truth edits as follow-up cards only |
| **C8 - Run model-compatibility follow-up** | Ready / evening-suitable | Draft provider/config compatibility review for local Qwen, hosted Gemini/OpenAI/Anthropic, adapter paths, and smoke-test gaps | model configs and adapter code | yes | Report proposes validations/tests only; no config or adapter patches |
| **C9 - Constrain mutating SDK workflows** | Blocked in shared workspace | `test-mutations` and any SDK code-edit workflow may run only in a disposable clone/worktree, never against the current dirty workspace | disposable worktree plus rollback protocol | no | Pre/post `git status`; rollback restores disposable worktree only; no source-of-truth file in main workspace changed |

### Guardrails

- SDK outputs are drafts only; humans/Codex promote any accepted changes.
- Do not expose or print `CURSOR_API_KEY`.
- Do not send real sensitive clinical data through this workflow.
- Do not let SDK-generated prose become evidence for paper claims unless it points to primary artifacts.
- If a draft conflicts with dataset audits, policies, run artifacts, configs, or registry rows, trust the primary artifact.
- Do not run mutating SDK workflows in the shared dirty workspace. Use review-only commands by default.
- Keep long local Ollama inference out of Cursor/IDE background shells; use detached PowerShell launchers and log monitoring instead.

### Evening-Suitable Queue

These can run autonomously for a multi-hour evening pass because they only draft review artifacts:

1. `uv run python scripts/cursor_sdk_workflows.py inspection-draft --topic "G16 builder-gap full-validation reconciliation" --run-dir runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z`
2. `uv run python scripts/cursor_sdk_workflows.py paper-synthesis --topic "post-G16 model-suite and Gan builder-gap paper claim map"`
3. `uv run python scripts/cursor_sdk_workflows.py hygiene-scan`
4. `uv run python scripts/cursor_sdk_workflows.py model-compatibility`
5. `uv run python scripts/cursor_sdk_workflows.py memory-pass`

Do not run `test-mutations` tonight unless a clean disposable worktree has been created and explicitly selected as the target.

## Recommended Next Pull

1. **G16 - Broader GPT validation** for `gan_s0_candidate_builder_gap_v1` before Qwen transfer or operational promotion.
2. **G16 inspection / decision note** with full/cap metrics, residual errors, and overfit caveat.
3. **M1 - Qwen 27b model-suite ladder** when Ollama is idle; do not let it block hosted GPT validation if API work is available.

Parallel work is cleanest as: one person/agent reconciles G16 artifacts and decides whether a rerun is needed, another prepares M2/model-suite synthesis shell or checks registry/model-suite docs, and a separate background Cursor SDK session runs C5-C8 review-only drafts. Source-changing Gan candidate work should stay single-threaded because it changes the shared Gan candidate contract.

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
| Cursor SDK pilot | Review-only research-operations assistant; not part of benchmark extraction or scoring |

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
- Cursor SDK workflow pilot: `docs/workstreams/cursor_sdk/cursor_sdk_research_workflows_20260523.md`
