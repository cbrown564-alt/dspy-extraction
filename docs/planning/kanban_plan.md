# Clinical Extraction Kanban Plan

**Active steering doc** - current execution board for the DSPy clinical extraction research system. Detailed historical ledgers stay in experiment inspections, synthesis notes, Cursor SDK ledgers, and [kanban_frozen_threads_history.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/planning/kanban_frozen_threads_history.md).

**Last refreshed:** 2026-05-24 (C2 run → rejected; C3 complete)

## Steering References

| Purpose | Source |
| --- | --- |
| Core research direction | [outline.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/outline.md) |
| Hybrid research doctrine | [hybrid_pipeline_research_pivot_20260521.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md) |
| Pipeline synthesis | [core_research_questions_pipeline_review_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/synthesis/core_research_questions_pipeline_review_20260524.md) |
| ExECT audit | [exect_gold_label_audit.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/datasets/exect/exect_gold_label_audit.md) |
| Gan audit | [gan_2026_label_audit.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/datasets/gan/gan_2026_label_audit.md) |
| Deterministic scorer guardrails | [deterministic_scorer_semantics.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/policies/deterministic_scorer_semantics.md) |
| Experiment registry | [experiment_registry.json](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/synthesis/experiment_registry.json) |
| Model config backlog | [model_config_compatibility_backlog_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/policies/model_config_compatibility_backlog_20260524.md) |
| Cursor research ops | [cursor_sdk_review_queue_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/workstreams/cursor_sdk/cursor_sdk_review_queue_20260524.md) |
| Cursor implementation orchestration | [cursor-implementation-orchestration skill](file:///c:/Users/cbrow/Code/dspy-extraction/.agents/skills/cursor-implementation-orchestration/SKILL.md) |

## Current Priorities

The current priority is to turn recent ExECT and Gan improvements into clearer next experiments and paper-ready evidence, without reopening settled operational defaults or burying active questions in historical detail.

1. **ExECT S5 core improvement.** S5 now has a usable core surface: diagnosis, seizure type, annotated medication, investigation, and seizure frequency. The narrow annotated-medication guard lifted medication F1 to 88.7% on full validation, so the active bottleneck is now `seizure_frequency` at 60.2% F1.
2. **Cross-dataset Explorer.** The ExECT Explorer now has a static model lens over S1-S5 run artifacts. The next systems/research value is a Gan expansion that shows notes, gold frequency labels, model outputs, deterministic candidates, adjudication, normalization, and scorer outcomes.
3. **Gan residual understanding before more arms.** Gan builder-gap v1 remains the operational default. Multi-stage GEPA G1/G2 regressed on cap-25 and are rejected as arms, so the next Gan work should explain residual failures or test a tightly scoped non-optimizer hypothesis.
4. **Paper result freeze.** Current claims are now scattered across registry rows, inspections, source maps, and synthesis docs. Freeze paper tables from primary artifacts before spending more model budget.
5. **Model/provider readiness.** B6/B7 config-level coverage and Gemini policy checks have been addressed; remaining work is runtime/provider smoke discipline, especially high-context Qwen and broad hosted-provider comparisons.

## Recently Completed Work

| Work | Outcome | Why it matters |
| --- | --- | --- |
| ExECT S5 frequency pre-vocab arm | Full-validation seizure-frequency F1 improved from 45.0% to 60.2%; overall S5 micro F1 reached 77.9%. | Establishes high-recall pre-vocab candidate injection as the current S5 frequency baseline. |
| ExECT high-precision candidate test | High-precision candidate pruning regressed cap-25 frequency recall by 12.0pp and F1 by 4.2pp versus high-recall candidates. | Keeps the next frequency work focused on verification/post-processing or better candidate use, not candidate narrowing. |
| ExECT annotated-medication precision assessment | Identified S5 medication regression as precision leakage from expanded schema context, not recall loss. | Clarified that S5 medication needed a post-prediction guard, not scorer changes. |
| ExECT annotated-medication guard | `exect.medication.am_guard_non_asm_brand_alias.v1` raised full-validation annotated-medication F1 from 73.6% to 88.7% while leaving non-medication S5 families stable. | Clears the immediate S5 medication gate; planned/history/future ASM pruning remains a separate policy-risk arm. |
| ExECT Explorer model lens | Added static catalog building from run artifacts, model/run selection, per-run metrics, and letter-level pipeline traces for ExECT S1-S5. | Creates the template for a Gan Explorer and gives paper/review work a concrete inspection surface. |
| Gan builder-gap residual forensics | Found 58 benchmark-severe misses; major patterns include unknown overuse and pragmatic monthly divergence. | Gives the next Gan work a residual map instead of another blind model arm. |
| Gan multi-year seizure-free helper | Closed two candidate recall gaps and lifted enriched gap-slice candidate coverage from 23/25 to 25/25. | Reinforces that deterministic candidate recall still matters for Gan. |
| Gan multi-stage GEPA G0-G2 | Added configs, stage-attributed feedback, artifact support, and ran cap-25; G1/G2 regressed to 60.0% and 48.0% monthly accuracy. | Rejects these optimizer arms and prevents GEPA from consuming more budget without a new compact-instruction hypothesis. |
| Model adapter coverage | Added offline config-level coverage for production `build_dspy_lm` across model configs and clarified Gemini reasoning behavior. | Reduces provider/config drift before broader model comparisons. |
| Cursor SDK protocol and instrumentation | Established review-only research ops, disposable-worktree mutation protocol, ledgers, draft index, and a separate orchestration skill for implementation work. | Keeps Cursor useful without letting generated drafts or mutation diffs become source-of-truth evidence. |

## Active Pathways

### Pathway A - ExECT S5 Core Lift

**Focus:** Improve S5 benchmark-facing core extraction, especially seizure frequency, while preserving the newly repaired medication precision.

**Outcome:** A stronger ExECT S5 operational candidate with run IDs, configs, scorer mode, metric caveats, and residual analysis suitable for paper/table consideration.

| Card | Status | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- | --- |
| A1. Frequency residual audit | Completed | Classified S5 frequency false positives/false negatives after high-recall pre-vocab injection: qualitative over-emission, temporal/current-scope mismatch, evidence mismatch, normalization/range mismatch, and gold-policy ambiguity. | E5 full-validation runs | yes | Inspection note: [exect_s5_frequency_residual_audit_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/exect/exect_s5_frequency_residual_audit_20260524.md), citing run ID `exect_s5_frequency_pre_vocab_full_gpt4_1_mini_20260524T142823Z`, scorer mode, split, and per-document residual categories. |
| A2. Candidate-constrained frequency verifier | Completed | Case-insensitive matching, casing recovery, relaxed medication control guard, and paraphrasing-prevention instructions improved seizure_frequency F1 to 71.7% on cap-25 (+11.2pp vs baseline, +3.8pp vs buggy verifier). Runs completed and unit tests added. | A1 complete; A2R review complete | no | Run ID: `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini_20260524T194925Z`, walkthrough: [walkthrough.md](file:///C:/Users/cbrow/.gemini/antigravity/brain/6b549eb8-1960-448a-a6ff-feb9b3abc6c3/walkthrough.md), critic review: [exect_s5_frequency_verifier_a2r_regression_review_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/exect/exect_s5_frequency_verifier_a2r_regression_review_20260524.md). |
| A3. Frequency prompt/policy refinement | Completed | Refined extractor and verifier policy rules covering synonyms, zero-rate intervals, diagnostic modifiers, explicit last-seizure year mappings, and directional frequency change labels. Validation F1 rose to 72.3% (+12.1pp vs baseline 60.2%) with recall at 79.1% and precision at 66.7%, with no regressions on other S5 families. | A1 | yes | Run ID: `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_full_gpt4_1_mini_20260524T195813Z`, walkthrough: [walkthrough.md](file:///C:/Users/cbrow/.gemini/antigravity/brain/777de029-ac97-4a5b-a813-1975373697cf/walkthrough.md). |
| A4. Medication temporal evidence guard | Backlog | Separately test planned/history/future ASM pruning for `annotated_medication`. | AM guard promoted; prereg required | after A1/A2 or independent if medication becomes paper blocker | Cap-25 prereg; no silent scorer change; report annotation-policy residuals. |
| A5. S2/S3 middle-ladder reruns | Backlog | Refresh intermediate schema-complexity anchors only if paper tables need them. | Paper table needs | yes | Validation runs and registry rows; caveat that family sets differ by schema rung. |

### Pathway B - Cross-Dataset Explorer

**Focus:** Turn the ExECT Explorer model-lens pattern into a cross-dataset inspection tool.

**Outcome:** Static Explorer views for Gan and ExECT that let reviewers inspect notes, gold labels, model predictions, deterministic candidates, normalization, and scorer outcomes without rerunning models.

| Card | Status | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- | --- |
| B1. Gan data-shape audit for Explorer | Completed | Mapped clinical note structure, check__Seizure Frequency Number gold fields, and reference fields. | Gan audit; operational default run artifacts | yes | Design note checked against `gan_2026_label_audit.md` in `exect-explorer/scripts/build_manifest_gan.py`. |
| B2. Gan static catalog builder | Completed | Implemented in `exect-explorer/scripts/build_model_catalog_gan.py`. Compiles GPT-4.1-mini and Qwen3.6:35b run artifacts. | B1 | after B1 | Builder compiles 2 runs into public `model_catalog_gan.json` without missing links. |
| B3. Gan Explorer UI lane | Completed | Added dataset switcher in `App.jsx` and styling in `styles.css` to toggle between ExECTv2 and Gan 2026. | B2; existing ExECT model lens | after B2 | `npm run build` succeeds; verifies dataset, progress selector, and entity layers load Gan. |
| B4. Shared catalog schema cleanup | Backlog | Generalize only the minimal shared structures needed by ExECT and Gan. | B2/B3 lessons | no | Build remains stable for both datasets; no source loader semantics changed. |

### Pathway C - Gan Frequency Residuals

**Focus:** Improve or explain Gan S0 residual errors after builder-gap v1 without rerunning broad optimizer/model arms.

**Outcome:** A prioritized residual map and at most one tightly scoped next arm with a preregistered hypothesis.

| Card | Status | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- | --- |
| C1. Consolidate Gan residual taxonomy | Completed | Consolidated forensics in `docs/experiments/gan/gan_s0_residual_taxonomy_consolidation_20260524.md`. | Existing forensics and GEPA inspection | yes | Distinguishes unknown overuse, pragmatic monthly divergence, multi-type/cluster errors, and temporal scope mismatches. |
| C2. Unknown-overuse targeted arm — execution | **DONE (rejected)** | Ran v1.5 unknown-overuse guard prompt on enriched cap-25 slice. **Monthly accuracy: 16.0%** — gate (≥ 84%) not met by 68 pp. Arm rejected. Two root causes: (1) Rule 1 (quantified-window preservation) over-fires on ambiguous notes and hallucinates specific rates where `unknown` is correct; (2) `other_semantic_mismatch` records with no deterministic candidates are unaffected because Rule 4 is conditioned on candidates being present. Neither sub-problem was resolved. | C1 | after C1 | Run: `runs/gan_s0_unknown_overuse_guard_cap25_gpt4_1_mini_20260524T201746Z`, rejection report: [gan_s0_unknown_overuse_guard_cap25_gpt4_1_mini_rejection_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/gan/gan_s0_unknown_overuse_guard_cap25_gpt4_1_mini_rejection_20260524.md). |
| C3. Pragmatic monthly divergence analysis | Completed | Classified 16 GPT full-validation `pragmatic_match_monthly_divergence` records: ~6 are fixable extraction failures (count underestimation, multi-type selector), ~5 are window-selection mismatches (moderate fixability), ~5 are scorer-surface boundary artifacts (range-to-point collapse, vague-multiple). Paper-facing: monthly accuracy is primary; pragmatic accuracy (88.6%) should accompany it as a supporting metric with a documented attribution. | C1 | yes | Analysis: [gan_s0_pragmatic_monthly_divergence_analysis_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/gan/gan_s0_pragmatic_monthly_divergence_analysis_20260524.md). No scorer or gold change. |
| C4. Compact optimizer hypothesis | Blocked | Reopen GEPA only if there is a design that constrains instruction length or targets a frozen submodule. | New prereg required | no | Cap-25 prereg; prompt-length gate; no G1/G2 rerun. |

### Pathway D - Paper Evidence Freeze

**Focus:** Convert scattered experiment artifacts into paper-safe tables and claims.

**Outcome:** A frozen source map and draft result tables that cite primary artifacts, not SDK drafts or memory summaries.

| Card | Status | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- | --- |
| D1. Freeze operational-default table | Completed | Froze defaults for Gan S0 (GPT-4.1-mini and Qwen35b) and ExECT S1-S5 in `docs/experiments/synthesis/paper_frozen_operational_defaults_20260524.md`. | Registry and inspection docs | yes | Every row traces to primary run artifacts, listing monthly accuracy, F1 scores, and run IDs. |
| D2. Freeze negative/arm-reject table | Ready | Table of rejected arms with `decision_scope: arm`, comparison group, varied factor, and reason. | Registry and inspections | yes | Avoids mechanism-closure language unless a mechanism review exists. |
| D3. Draft results narrative | Ready | Paper-facing prose for what current evidence supports and what remains open. | D1/D2 | after D1/D2 | Claims match [core_research_questions_pipeline_review_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/synthesis/core_research_questions_pipeline_review_20260524.md). |
| D4. Test/benchmark reporting protocol | Backlog | Define if and when held-out or published benchmark reporting should occur. | Only after dev/full-validation arms justify it | no | Explicit protocol; no accidental test-set spend. |

### Pathway E - Model And Workflow Readiness

**Focus:** Keep provider configs, local model runs, and agent workflows reproducible enough for the next experiments.

**Outcome:** Live runs fail early with useful diagnostics, high-context local configs are used intentionally, and Cursor roles stay separated.

| Card | Status | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- | --- |
| E1. Hosted API key preflight | Completed | Added start-time preflight check warning for missing hosted-provider keys in `src/clinical_extraction/llms.py`. | Model backlog B2 | yes | Verified by tests in `tests/test_experiment_runner.py` asserting warning and ValueErrors. |
| E2. High-context Qwen warning policy | Completed | Added warning in `llms.py` for Ollama configs with large `num_ctx` (>8192) and short timeout (<120.0s) unless marked as stress test. | Model backlog B3 | yes | Unit tests in `tests/test_experiment_runner.py` assert warning trigger and stress-test exemption. |
| E3. Provider smoke ledger discipline | Ready | Before broad model comparisons, record run ID, config, structured-output behavior, schema validity, evidence support, timeout/provider caveats. | Existing smoke docs | yes | Smoke note or registry-compatible ledger entry exists. |
| E4. Cursor implementation campaign setup | Completed | Added a first-class `pathway-a-card` workflow in `scripts/cursor_sdk_workflows.py` with card, lane, brief, prompt-only, and ledger gates. | Orchestration skill | yes, with isolation | Verified in Pathway A Implementation Campaign plan. Diffs are Codex-reviewed before manual promotion. |

## Blocked Or Gated

| Item | Blocker | Release condition | Validation |
| --- | --- | --- | --- |
| Published ExECTv2 reproduction | CUI-aware all-family scoring and original Table 1 alignment remain unresolved. | Explicit reproduction workstream reopened. | CUI-aware scorer, per-item/per-letter metrics, benchmark-reference denominator checks. |
| Gan Real(300)/Real(150) | Real dataset access unavailable. | Data access and preregistered reporting plan. | Data manifest update and benchmark-reporting protocol. |
| GEPA G3/G4 continuation | G1/G2 regressed and produced long policy-wall instructions. | New compact-instruction or submodule-freezing hypothesis. | Cap-25 prereg with prompt-length gate. |
| Test holdout reporting | Development evidence is still moving. | Only for arms clearing dev/full-validation gates with explicit test-reporting config. | Test protocol and frozen scorer semantics. |

## Recommended Next Pull

1. **D2 - Freeze negative/arm-reject table.** Freeze table of rejected arms (now including C2) with decision scope, comparison group, varied factor, and reason. C2 adds a new rejected arm.
2. **D3 - Draft results narrative.** Paper-facing prose for what current evidence supports and what remains open (depends on D1/D2).
3. **Post-C2 Gan: builder extension for `other_semantic_mismatch` records.** C2 forensics confirm that 7/25 enriched-slice failures are records with no deterministic candidates where Rule 4 is inert. The highest-value Gan fix is extending the deterministic builder to produce candidates for these records (infrequent-rate notes where the builder currently returns nothing). This would benefit all future prompt arms, not just unknown-overuse.
4. **Post-C2 Gan: soften Rule 1 and retry.** If the builder extension is not the next pull, a softened v1.5 prompt (Rule 1 restricted to explicit calendar-window phrasing; add hedging for ambiguous notes) could be preregistered as C2b. Do not retry without fixing the root cause.
5. **A4 - Medication temporal evidence guard.** Separately test planned/history/future ASM pruning for `annotated_medication` if medication becomes a paper blocker.

## Parallelization Notes

- A1, B1, C1, D1, and E1/E2 can proceed in parallel because they read different artifacts and do not change shared scorer semantics.
- B2/B3 should wait for B1 because the Gan catalog shape is the shared contract for the UI.
- A2 and A3 should wait for at least a lightweight A1 residual read so they do not optimize the wrong frequency failure mode.
- C2 and C3 depend on C1; do not add new Gan arms until residual categories are reconciled.
- D3 should wait for D1/D2 so the prose inherits frozen table rows instead of restating stale metrics.
- Cursor research-ops remains review-only. Cursor implementation orchestration may write core files only under an explicit mission brief, isolated branch/worktree, domain-skill guardrails, focused tests, and Codex/GPT-5.5 review.

## Operational Defaults

| Track | Default | Evidence / caveat |
| --- | --- | --- |
| Gan S0 | `gan_s0_candidate_builder_gap_v1` on GPT 4.1-mini | 80.6% monthly, 86.0% Purist, 88.6% Pragmatic on Gan synthetic validation; not Gan Real reproduction. |
| Gan Qwen transfer | Builder-gap v1 on Qwen3.6:35b | Accepted transfer; trails GPT monthly accuracy but reaches strong pragmatic accuracy. |
| ExECT S1 | v4_10 + inline bridges | GPT full-validation 92.3% micro on local three-family S1 view. |
| ExECT S2 | Frozen GPT v1.3 | 80.9% micro; comparison anchor only. |
| ExECT S3 | Frozen GPT v1.2 | 72.1% micro; accepted comorbidity gap. |
| ExECT S4 | `exect_s4_field_family_cause_bridge_k0_k1_single_pass` plus medication-temporality G0G2 as best tested MT guard | S4 remains unsolved; cause bridge and MT guard are family-specific operational evidence. |
| ExECT S5 | `exect_s5_frequency_pre_vocab_am_guard_full_gpt4_1_mini` | Frequency F1 60.2%, annotated-medication F1 88.7%, micro F1 81.4% on full validation; seizure frequency remains active bottleneck. |
| Cursor SDK research-ops | Review-only research operations assistant | Drafts are leads, not evidence, until manually promoted from primary artifacts. |
| Cursor implementation orchestration | Codex/GPT-5.5 orchestrates and reviews; Cursor implements scoped isolated cards | Core-file mutation requires branch/worktree isolation, allowed write surfaces, focused tests, and Codex review. |

## Standing Guardrails

- Do not silently change scorer semantics. If scorer behavior changes, update tests and document the interpretation.
- Gan primary gold is `seizure_frequency_number[0]`; `reference[0]` is diagnostic only.
- Distinguish `unknown` from `no seizure frequency reference`.
- Evidence support is diagnostic unless an experiment explicitly makes it prediction-affecting.
- Keep operational defaults separate from mechanism closure.
- Keep arm rejection separate from mechanism rejection; new inspection docs must name `decision_scope`.
- For ExECT, S5 is diagnosis, seizure type, annotated medication, investigation, and seizure frequency. Medication temporality remains outside S5 unless explicitly reopened.
- Keep high-recall ExECT frequency candidates as the baseline; high-precision pruning is rejected as an arm.
- Do not promote SDK-generated prose, Cursor drafts, or source maps as paper evidence unless they point to primary artifacts and are manually verified.
- Do not run broad Gan optimizer/model arms without a preregistered decision question after residual forensics.
- Do not spend test/holdout or published-benchmark reporting budget without an explicit protocol.
