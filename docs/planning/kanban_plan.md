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
| **Model suite completion** | `docs/experiments/synthesis/model_suite_qwen27b_full_validation_v1_inspection_20260523.md`, `docs/experiments/synthesis/model_suite_pattern_interpretation_20260522.md` |
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
| **G16 - Broader GPT validation for builder-gap v1** | Review / reconciliation | Full-validation run artifact exists: `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z`; review-only SDK inspection draft flags aggregate lift vs F0 but a slice/full candidate-emission mismatch | G15 | no | Promote a human-reviewed inspection/decision note before registry row, rerun, Qwen transfer, or operational-default change |

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

## Active Priority 2 - Frozen Model Suite Complete

**Status:** Complete / synthesis-only. All planned hosted and local tracks are done, including Qwen3.6:27b.  
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
| Qwen 3.6:27b | 85.7% | 69.3% | 74.9% | Done |

### Active Cards

| Card | Status | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- | --- |
| **M1 - Run Qwen 27b full ladder** | Done | Qwen3.6:27b S1/S4/Gan F0 replay succeeded 3/3: `runs/overnight_logs/qwen27b_model_suite_ladder_20260522_235509.summary.txt`; inspection `docs/experiments/synthesis/model_suite_qwen27b_full_validation_v1_inspection_20260523.md` | Smokes passed; 35b and 9b done | no | Run IDs: `exect_s0_s1_validation_full_qwen27b_ollama_20260522T225513Z`, `exect_s4_validation_full_qwen27b_ollama_20260523T071044Z`, `gan_s0_expanded_builders_prose_full_validation_qwen27b_ollama_20260523T133604Z` |
| **M2 - Update model-suite synthesis table** | Done | Paper-facing model profile table now includes Qwen 27b and 9b with hosted/local tradeoffs, latency, and caveats: `docs/experiments/synthesis/model_suite_pattern_interpretation_20260522.md` | M1 | yes | Synthesis cites exact inspection docs and preserves `decision_scope: arm` |
| **M3 - Decide whether S2/S3 extension is needed** | Deferred / explicit decision needed | Yes/no for `model_suite_exect_s2_s3_extension_v1`; current default is no additional runs unless the paper argument needs mid-ladder validation | model-suite synthesis need | yes | Decision note; no runs by inertia |

### Runtime Rules

- Only one Ollama cap/full job at a time.
- Hosted API jobs can run in parallel with a local Ollama job.
- Qwen 27b ExECT full runs used bounded `num_ctx=65536`; the earlier 262k-context S1 smoke timed out before predictions.
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

**Status:** Promoted / constrained; evening review queue reviewed, selected decisions promoted into this board.  
**Decision source:** `docs/workstreams/cursor_sdk/cursor_sdk_research_workflows_20260523.md`; assessment `docs/workstreams/cursor_sdk/cursor_sdk_value_reliability_assessment_20260523.md`.  
**Scope:** Review-only research operations. Cursor/Composer output is not a benchmark model track, scorer, clinical extractor, DSPy optimizer result, or source-of-truth update.  
**Budget guard:** User-configured Cursor spend limit: GBP 15.

### Purpose

Use the Cursor Python SDK as a background drafting and review assistant for source-heavy research operations: memory candidates, experiment-inspection drafts, paper claim maps, model-compatibility scans, and hygiene reports. The pilot passed, but the authority boundary is now explicit: SDK output stays in draft folders until human/Codex review promotes selected findings.

### Assessment

The SDK is valuable for broad review-only synthesis and drift detection. C1-C3 produced useful drafts with source paths and no source-of-truth edits. Later drafts also surfaced useful technical leads, including a G16 full-validation inspection draft that flagged a slice/full candidate-emission mismatch and a model-compatibility report that identified adapter/config risk.

Reliability is not high enough for unattended mutation in the shared dirty workspace. The `test-mutations` workflow restored `src/clinical_extraction/gan/temporal_candidates.py` to committed HEAD rather than the pre-session dirty baseline, so mutating SDK workflows are blocked unless run in a disposable clone/worktree with explicit rollback guarantees.

### Promoted Evening Queue Decisions

The review-only evening queue completed and produced usable drafts. The selected findings below are promoted as Kanban decisions only; the drafts remain source-linked triage artifacts, not promoted research memory, registry rows, or paper evidence:

| Workflow | Canonical draft / log | Key finding | Follow-up |
| --- | --- | --- | --- |
| G16 inspection draft | `docs/experiments/cursor_sdk_drafts/20260523T164636Z_inspection_draft.md` | Promote as a **stale-check / rerun-risk finding**: G16 full-validation artifact exists (`...161524Z`) and beats F0 aggregate monthly **75.9% vs 68.1%**, but enriched-slice replay collapses **92.0% -> 32.0%** with 19/25 empty candidate lists. Do not promote G16 to operational default, registry row, paper evidence, or Qwen transfer gate from this artifact alone | Write promoted Gan inspection under `docs/experiments/gan/`; confirm run-time code state and candidate parity; likely rerun only after builder parity is verified |
| Paper claim-map refresh | `docs/experiments/cursor_sdk_drafts/20260523T164746Z_paper_synthesis_draft.md` | Promote as a **paper stale-check finding**: the draft is useful as a claim/run map, but its Gan Claim 1 still anchors on older verify-repair promotion language and must be reconciled against the current F0 operational default and unresolved G16 builder-gap evidence | Do not reuse paper claims until registry + current Kanban defaults are checked; mark verify-repair-as-default wording stale |
| Post-refresh hygiene scan | `docs/workstreams/cursor_sdk/hygiene_scans/20260523T164844Z_hygiene_scan.md` | Promote as **operational hygiene guidance**: the main drift has moved from priority-memory mismatch to execution bookkeeping, especially G16 inspection/registry gaps, stale workflow-index routing, and synthesis/navigation defaults | Use scan findings to drive G16 decision note, workflow-index refresh, and synthesis-default cleanup |
| Model-compatibility follow-up | `docs/workstreams/cursor_sdk/compatibility/20260523T164950Z_model_compatibility_report.md` | Promote as a **validation backlog input**: production uses `build_dspy_lm`, while `build_chat_adapter` tests can give false confidence for Ollama/Gemini; Qwen context/timeout and hosted output-budget coverage remain validation gaps | Add targeted config/adapter tests before changing provider configs; no provider config patches are promoted by this draft |
| Memory pass | `docs/memory/dreams/20260523T165051Z_cursor_sdk_memory_pass_candidate.md` | Promote as **memory-routing guidance**: G16 is now reconciliation/decision work, not first execution; slice registry row exists, full-validation row does not | Mirror only source-verified rows into promoted memory after G16 inspection is updated |

### Active Cards

| Card | Status | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- | --- |
| **C1 - Test automated research-memory pass** | Done | Prompt rehearsal plus live review-only candidate written to `docs/memory/dreams/20260523T093633Z_cursor_sdk_memory_pass_candidate.md`; candidate is useful for C4 scoring but not promoted memory | Cursor SDK setup; Windows bridge-discovery patch in `scripts/cursor_sdk_workflows.py` | yes | `uv run python scripts/cursor_sdk_workflows.py check`; `uv run python scripts/cursor_sdk_workflows.py memory-pass`; reviewed against `docs/memory/README.md` promotion checklist |
| **C2 - Test experiment-inspection draft worker** | Done | Draft produced for G15 slice (`20260523T101141Z_inspection_draft.md`); names metadata, accuracy, run facts, and lists required human checks | Cursor SDK setup; run/config pointer | yes | Draft names dataset, split, model/provider, program variant, scorer mode, normalization rules, evidence policy, caveats, and required human checks |
| **C3 - Test background repo hygiene scan** | Done | Hygiene scan completed (`20260523T101227Z_hygiene_scan.md`); identified 12 findings ranked by risk | Cursor SDK setup | yes | Findings are source-linked and do not propose direct scorer, dataset, registry, or operational-default changes |
| **C4 - Decide whether to keep Cursor SDK workflow** | Done | SDK workflows promoted/accepted on 2026-05-23; SDK remains as review-only operations assistant | C1, C2, C3 | no | At least two useful drafts and zero source-of-truth edits by the SDK agent before promotion |
| **C5 - Run targeted G16 inspection draft** | Done / promoted as stale-check | Canonical review-only draft: `docs/experiments/cursor_sdk_drafts/20260523T164636Z_inspection_draft.md`; earlier draft `...163121Z` is superseded. Decision: G16 artifact is not promotion-ready because candidate-emission parity is inconsistent | G16 artifact exists; SDK guardrails | yes | Draft lists primary run artifacts, controls, scorer mode, caveats, and required human checks; no Kanban/registry edits |
| **C6 - Run paper claim-map refresh** | Done / promoted as paper stale-check | Canonical review-only draft: `docs/experiments/cursor_sdk_drafts/20260523T164746Z_paper_synthesis_draft.md`; earlier `...160219Z` is superseded. Decision: useful claim map, but stale verify-repair default language is explicitly quarantined | registry and synthesis docs available | yes | Source-linked; no paper reuse until current Kanban defaults, registry rows, and G16 caveats are reconciled |
| **C7 - Run post-refresh hygiene scan** | Done / promoted as hygiene backlog | Fresh drift report: `docs/workstreams/cursor_sdk/hygiene_scans/20260523T164844Z_hygiene_scan.md`; identifies G16 bookkeeping gap, stale workflow-index routing, synthesis defaults, and SDK draft indexing needs | C4 assessment | yes | Findings are ranked by risk and keep source-of-truth edits as follow-up cards only |
| **C8 - Run model-compatibility follow-up** | Done / promoted as validation backlog | Canonical review-only report: `docs/workstreams/cursor_sdk/compatibility/20260523T164950Z_model_compatibility_report.md`; earlier `...160418Z` is superseded. Decision: adapter/config risks warrant targeted tests, not immediate provider config changes | model configs and adapter code | yes | Report proposes validations/tests only; no config or adapter patches |
| **C9 - Constrain mutating SDK workflows** | Blocked in shared workspace | `test-mutations` and any SDK code-edit workflow may run only in a disposable clone/worktree, never against the current dirty workspace | disposable worktree plus rollback protocol | no | Pre/post `git status`; rollback restores disposable worktree only; no source-of-truth file in main workspace changed |
| **C10 - Review and promote selected SDK drafts** | Done for Kanban scope | Canonical C5-C8 drafts selected; decisions promoted into this board only, with prompt-only/superseded stubs labeled by canonical pointers above | C5-C8 completed | yes | Promotion checklist passed for Kanban decisions; no draft claim promoted without primary artifact path |
| **C11 - Refresh SDK workflow index / source docs** | Ready | Align `docs/workstreams/cursor_sdk/cursor_sdk_research_workflows_20260523.md` header/status and `docs/memory/workflow_index.md` routing with the promoted review-only operating mode | C10 | yes | Source docs point to canonical draft folders, mutating-workflow block, and review-only scope |

### Guardrails

- SDK outputs are drafts only; humans/Codex promote any accepted changes.
- Do not expose or print `CURSOR_API_KEY`.
- Do not send real sensitive clinical data through this workflow.
- Do not let SDK-generated prose become evidence for paper claims unless it points to primary artifacts.
- If a draft conflicts with dataset audits, policies, run artifacts, configs, or registry rows, trust the primary artifact.
- Do not run mutating SDK workflows in the shared dirty workspace. Use review-only commands by default.
- Keep long local Ollama inference out of Cursor/IDE background shells; use detached PowerShell launchers and log monitoring instead.

### Completed Evening Queue

The 2026-05-23 evening queue ran the review-only drafting workflows, and C10 has promoted the selected decisions into this board. Do not rerun these commands for the same topics unless a reviewer requests a refresh after source docs change. The next SDK action is C11 source-doc/workflow-index alignment, not more unattended drafting.

Do not run `test-mutations` unless a clean disposable worktree has been created and explicitly selected as the target.

## Recommended Next Pull

1. **G16 reconciliation / decision note** with canonical run ID, candidate-emission parity check, full-validation metrics, residual errors, and rerun criteria.
2. **C11 - Refresh SDK workflow index / source docs** so the promoted review-only operating mode is visible outside the Kanban while draft-only claims stay quarantined.
3. **Model-suite S2/S3 extension decision** only if the paper needs middle-ladder model-profile evidence; otherwise keep the frozen suite complete and move on.

Parallel work is cleanest as: one person/agent reconciles G16 artifacts and decides whether a rerun is needed, another checks whether the completed model suite needs registry/paper-claim backfill, and a separate reviewer handles C11 SDK source-doc alignment. Source-changing Gan candidate work should stay single-threaded because it changes the shared Gan candidate contract.

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

The frozen architecture suite compares model tracks on the same S1/S4/Gan F0 surfaces and is now complete for planned tracks. Gemini 3 Flash leads Gan F0 monthly (**75.3%**) but is model-comparison only; Qwen 27b leads S4 pooled micro (**69.3%**) while GPT 5.5 remains the strongest hosted S4 track (**68.7%**). GPT 4.1-mini remains the S1 anchor (**92.3%**). Local Qwen scaling is not monotonic: Qwen 27b beats 35b and 9b on all three suite surfaces, but with heavy partial-offload latency.

### Optimizer And Taxonomy Arc

Bootstrap/optimizer probes did not support optimizer automation as the near-term path for S1 or Gan S0. Manual, audit-grounded policy and deterministic scaffolding produced the strongest current evidence. Taxonomy primitives and registry metadata are in place; new deterministic candidate work should compose from typed primitives and run primitive validation after changes.

## Current Decisions

| Decision | Position |
| --- | --- |
| Active queue | `docs/planning/kanban_plan.md` only |
| Research doctrine | Keep arm rejection separate from mechanism closure |
| Primary engineering | Gan deterministic candidate-builder gap analysis |
| Primary model execution | None active for frozen model suite; model execution focus returns to preregistered Gan follow-ups |
| Gan failed GPT-first arms | Do not transfer G5/G6/G6b/G7/G9 to Qwen |
| Gan v1.4 policy | Strongest no-example GPT enriched-slice control |
| Gan F0 model default | Expanded builders + prose remains full-validation operational default |
| ExECT S1 policy | v4_10 all tracks; v4.12 reject at cap-25 |
| Model suite | Model-comparison only; no operational promotion from leaderboard results |
| Gemini/GPT 5.5/Claude results | Useful for model profile, not mechanism closure |
| Qwen 27b model-suite ladder | Done; closes planned S1/S4/Gan F0 coverage |
| S2/S3 model-suite extension | Deferred unless paper needs it; decide explicitly before running |
| Cursor SDK pilot | Review-only research-operations assistant; not part of benchmark extraction or scoring |
| Cursor SDK evening queue | C5-C8 reviewed; selected decisions promoted into Kanban as stale-check, hygiene, memory-routing, and validation-backlog guidance only |
| Cursor SDK G16 finding | G16 full-validation artifact is reconciliation/rerun-risk evidence, not operational promotion, paper evidence, registry promotion, or Qwen transfer clearance |
| Cursor SDK paper draft | Useful claim map, but stale verify-repair default language is quarantined until reconciled against F0 and G16 |
| Cursor SDK compatibility draft | Validation backlog input only; no adapter or provider config changes promoted from the draft |
| Mutating SDK workflows | Blocked in shared dirty workspace; disposable clone/worktree required |

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
- Model suite Qwen 27b completion: `docs/experiments/synthesis/model_suite_qwen27b_full_validation_v1_inspection_20260523.md`
- Model suite synthesis: `docs/experiments/synthesis/model_suite_pattern_interpretation_20260522.md`
- Qwen v4.12 reject: `docs/experiments/exect/exect_s1_qwen_v4_12_diagnosis_stabilized_cap25_inspection_20260521.md`
- Hybrid mechanism status: `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`
- Deterministic placement synthesis: `docs/workstreams/hybrid/hybrid_deterministic_placement_research_synthesis_20260521.md`
- Cursor SDK workflow pilot: `docs/workstreams/cursor_sdk/cursor_sdk_research_workflows_20260523.md`
- Cursor SDK evening hygiene scan: `docs/workstreams/cursor_sdk/hygiene_scans/20260523T164844Z_hygiene_scan.md`
- Cursor SDK G16 inspection draft: `docs/experiments/cursor_sdk_drafts/20260523T164636Z_inspection_draft.md`
- Cursor SDK paper claim-map draft: `docs/experiments/cursor_sdk_drafts/20260523T164746Z_paper_synthesis_draft.md`
- Cursor SDK model-compatibility draft: `docs/workstreams/cursor_sdk/compatibility/20260523T164950Z_model_compatibility_report.md`
- Cursor SDK memory candidate: `docs/memory/dreams/20260523T165051Z_cursor_sdk_memory_pass_candidate.md`
