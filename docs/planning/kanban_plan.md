# Clinical Extraction Kanban Plan

Status: active steering doc
Last refreshed: 2026-05-28 C19 complete; C20 ready
Supersedes: the pre-pivot R/A backlog as active priority guidance

This board is current-first. Completed work is summarized only where it changes
active sequencing, while the remaining architecture cleanup is explicit enough
to pull through completion. The project has two active priority sets:

1. radically simplify the codebase so the decomposition program is easy to
   follow, test, and extend;
2. reorganize experiments around the May 28 component-ceiling research program,
   not around old broad-pipeline improvement loops.

Historical cards, rejected arms, and old backlog detail remain provenance in
`kanban_frozen_threads_history.md`, experiment notes, archive indexes, and run
artifacts. They are not active guidance unless this board, `current_research_program.md`,
or `component_ceiling_registry.md` explicitly promotes them.

## Current Priorities

1. **Finish the architecture/modularity cleanup before new broad model work.**
   The remaining audit gap is no longer an umbrella task: C12-C19 are complete;
   pull C20 to close or explicitly reclassify the residual architecture risks.
2. **Keep behavior-preserving cleanup separate from research claims.** Each
   architecture card must preserve scorer, loader, split, benchmark bridge, and
   replay semantics unless a focused policy/test change explicitly says
   otherwise.
3. **ExECT component ceilings before schema stacking.** Follow
   `experiments/exect/exect_task_deep_review_20260528.md`: no-model gates,
   family payloads, raw/bridge/prompt causal splits, then isolated ceilings,
   pairwise interactions, and only then optimized S1*/S2*/S3*/S4*/S5* stacks.
4. **Gan S0 decomposition before prompt polishing.** Follow
   `experiments/gan/gan_s0_pipeline_decomposition_deep_dive_20260528.md`:
   candidate inventory, temporal anchoring, target selection, label
   construction, aggregation, unknown/no-reference policy, and evidence/schema
   diagnostics as separable components.
5. **Preserve benchmark and scorer discipline.** Gan paper comparisons use
   `gan2026_paper_reproduction`; canonical Gan metrics remain diagnostic.
   ExECT Table 1 reproduction remains blocked until CUI-aware all-family
   scoring exists. Holdout is for residual analysis, not tuning.
6. **Separate active configs from replay configs.** After C19, the 35 JSON
   configs under `configs/experiments/` are current-authority rows; historical,
   rejected, and replay/provenance configs live under `archive/configs/` and are
   still resolvable by basename for reproducibility.

## Ready

### C20 - Modularity Completion Review

- **Outcome:** A final review updates the architecture audit status with what
  was addressed, what remains intentionally retained, file-size/module boundary
  evidence, validation commands, and any residual risk accepted for
  reproducibility.
- **Dependencies:** C12-C19 complete.
- **Parallelizable:** no.
- **Owner:** unassigned.
- **Validation:** Re-run the focused architecture validation matrix from
  C12-C19 plus the full test suite if feasible; update docs only after the
  result is known.
- **Notes:** Completion means the P1 monolith risks are closed or explicitly
  reclassified with rationale. It does not require deleting replay-provenance
  contracts that are still needed for historical runs.

### E5 - Medication Lifecycle Target Policy Decision

- **Outcome:** A short decision note states whether medication lifecycle /
  temporality is benchmark-facing, clinical-diagnostic, deferred, or blocked,
  with the gold/proxy source and scoring caveats explicit.
- **Dependencies:** E3.
- **Parallelizable:** yes; no model calls.
- **Owner:** unassigned.
- **Validation:** Decision cites the E3 lifecycle inventory counts, ExECT gold
  audit prescription-temporality caveat, and `deterministic_scorer_semantics.md`;
  no scorer or loader change occurs unless a follow-up card is created.
- **Notes:** ExECT prescription JSON has no native temporality column. Do not
  treat planned/previous/taper/current status as a headline metric until this
  target policy exists.

### E6 - Medication Isolated Current-Rx Ceiling Probe

- **Outcome:** A preregistered isolated medication component probe using the E3
  annotation-current-Rx payload, reporting medication precision, recall, F1,
  and residual categories without lifecycle scoring.
- **Dependencies:** E3; E5 only if the probe includes lifecycle labels.
- **Parallelizable:** yes.
- **Owner:** unassigned.
- **Validation:** Compare the isolated medication component against existing S1
  and S5 medication surfaces on validation; report dataset split, model/provider
  if any, scorer mode, bridge/normalization policy, and evidence diagnostics.
- **Notes:** This is the current-Rx ceiling path. Lifecycle rows remain
  diagnostic unless E5 explicitly promotes a target.

### E7 - Medication Stack-Interference Probe

- **Outcome:** A no-model or capped-run analysis attributes S5 medication loss
  to over-emission, non-ASM leakage, historical/planned/taper evidence, dose-only
  rows, or cross-family prompt interference using the E3 payload as the audit
  surface.
- **Dependencies:** E3; E6 helpful if an isolated ceiling is available.
- **Parallelizable:** after E3; coordinate with the S5 stack surface if files
  move.
- **Owner:** unassigned.
- **Validation:** Report S1 versus S5 medication deltas, row-level interference
  categories, and whether an AM guard, payload routing, or prompt isolation is
  the next appropriate mechanism.
- **Notes:** Do not bundle temporality recovery into broad S5 prompts. The goal
  is to explain medication degradation before changing the stack.

### E8 - Family-Span Cap-Slice Prompt Comparison

- **Outcome:** A preregistered cap-slice comparison of full-note prompting versus
  E4 family-span prompting for a narrow target such as S1+investigation or one
  selected family.
- **Dependencies:** E4.
- **Parallelizable:** yes, but keep one family/span surface fixed per run.
- **Owner:** unassigned.
- **Validation:** Report full-note versus family-span prompt substrate, dataset
  split, cap size, model/provider, scorer mode, family F1/precision/recall,
  gold evidence coverage, false-family span counts, and evidence diagnostics.
- **Notes:** This tests typed document geometry. It does not promote the old
  rejected section-aware routing arm unless recall is preserved and the
  preregistered comparison shows a real precision or cost benefit.

### E10 - ExECT Frequency Candidate Selection Split

- **Outcome:** A preregistered component probe separates the completed
  frequency event/rate payload from candidate adjudication and benchmark-label
  construction.
- **Dependencies:** C5 and C8 complete.
- **Parallelizable:** yes, if scorer and bridge semantics are frozen.
- **Owner:** unassigned.
- **Validation:** Compare broad payload, high-precision payload, S4/S5 frequency
  surfaces, and any adjudicator arm on validation. Report split, model/provider
  if any, scorer mode, precision/recall/F1, extra-candidate strata, and whether
  errors are payload coverage, target selection, or label construction.
- **Notes:** C5/C8 cleared recall but not precision. Do not treat the 43/43
  payload coverage result as a frequency ceiling.

## Blocked

### B1 - ExECT Optimized Stack Reconstruction

- **Outcome:** S1*/S2*/S3*/S4*/S5* built from optimized components rather than
  broad prompt ladders.
- **Blocked by:** isolated ceiling reports and pairwise interaction evidence,
  not substrates alone.
- **Parallelizable:** no.
- **Owner:** unassigned.
- **Validation:** Per-family deltas from isolated ceilings, pairwise
  interaction losses, pooled micro F1 as secondary, and holdout residual audit.
- **Notes:** Do not start this until component ceilings exist.
  E3/E4 provide substrates only; E5-E10 and pairwise interaction work are still
  needed before an optimized ExECT stack claim.

### B2 - ExECT Table 1 Benchmark Reproduction

- **Outcome:** Explicit CUI-aware all-family scorer path and benchmark
  reproduction report.
- **Blocked by:** CUI-aware scorer design and replay.
- **Parallelizable:** yes once scorer scope is defined.
- **Owner:** unassigned.
- **Validation:** Report distinguishes published-benchmark metrics from project
  diagnostic field-family metrics.
- **Notes:** Keep separate from S1/S5 local claims.

### B3 - Gan Real-Note Reporting

- **Outcome:** Preregistered protocol for real-note Gan reporting.
- **Blocked by:** dataset access, approval, and reporting protocol.
- **Parallelizable:** after access.
- **Owner:** unassigned.
- **Validation:** Protocol states split, scorer, normalization rules, and what
  can be compared to synthetic validation.

## Backlog

### X2 - Pairwise ExECT Interaction Plan

- **Outcome:** A preregistered plan for diagnosis+seizure type,
  seizure type+frequency, medication+temporality, investigation+comorbidity,
  and other high-value pairwise interactions.
- **Dependencies:** initial component ceiling reports; E5 before treating
  medication+temporality as a scored pair.
- **Parallelizable:** after E1-E4.
- **Owner:** unassigned.
- **Validation:** Each pair has hypothesis, support counts, primary family
  metrics, interference criteria, and stop rule.

### E9 - Family-Span Promotion Or Rejection Decision

- **Outcome:** A decision note classifies family-span prompting as promoted,
  diagnostic-only, rejected arm, or still mechanism-open.
- **Dependencies:** E8.
- **Parallelizable:** after E8.
- **Owner:** unassigned.
- **Validation:** Decision cites the E4 no-model coverage audit, E8 cap-slice
  results, full-note baseline, false-family span counts, and recall/cost
  tradeoffs.
- **Notes:** Promotion requires evidence against a full-note baseline. Existence
  of `exect.sections.family_spans.v1` is substrate evidence only.

### G4 - Gan Explicit Reason-Code Adjudicator

- **Outcome:** A preregistered Gan S0 adjudicator that emits explicit
  target-selection reason codes, selected-candidate references, and exact label
  construction inputs separately from the final benchmark-facing label.
- **Dependencies:** G2 model-arm comparison complete; G3 unknown/no-reference
  policy probe complete.
- **Parallelizable:** yes for same-slice adjudicator design from G3 outputs;
  implementation should stay single-threaded with any Gan S0 artifact/metadata
  contract changes.
- **Owner:** unassigned.
- **Validation:** Compare against free adjudication, candidate-constrained
  adjudication, and the seeded answer-options selector surrogate on the same
  validation slice first; report both `gan2026_paper_reproduction` and
  canonical scorer views, selected reason-code distributions, unsupported
  candidate cases, and whether errors are target-selection, label-construction,
  policy, or evidence failures.
- **Notes:** This is the explicit follow-up to the G2 seeded
  reason-code/answer-options surrogate. G3 has pinned down policy-isolation
  cues; do not promote or full-validate a new adjudicator until it beats the
  same-slice baselines under both scorer views.

### G5 - Gan Paper-Scorer Rescore Pack

- **Outcome:** Current promoted Gan synthetic baselines are rescored under
  `gan2026_paper_reproduction` before any benchmark-comparison table or paper
  claim uses them.
- **Dependencies:** Current promoted Gan baseline artifacts remain available.
- **Parallelizable:** yes; no model calls unless a missing baseline must be
  regenerated by a separate preregistered card.
- **Owner:** unassigned.
- **Validation:** Report canonical versus paper-reproduction scorer views,
  repair/range/tolerance options, dataset split, config/run IDs, and the
  synthetic-only caveat.
- **Notes:** This routes the registry paper-comparison action. It does not
  unblock Real(300) or Real(150) reporting by itself.

### E11 - ExECT Holdout Residual Attribution

- **Outcome:** A residual-analysis report attributes S1 and S5 holdout drops to
  raw extraction, benchmark bridges, prompt policy, stack interference, family
  support, or scorer/label-policy effects without tuning from holdout.
- **Dependencies:** E2 complete; E10, E6, and E7 helpful where frequency or
  medication residuals dominate.
- **Parallelizable:** yes for artifact replay and no-model error bucketing.
- **Owner:** unassigned.
- **Validation:** Report validation versus test split, family-level metrics,
  residual categories, raw/bridge/prompt/stack attribution where available, and
  explicit confirmation that no scorer, loader, split, bridge, or prompt was
  tuned from holdout.
- **Notes:** This routes the registry holdout-transfer action. Findings can
  motivate validation-only component probes, not holdout-driven prompt edits.

### E12 - Investigation Isolated Ceiling Confirmation

- **Outcome:** A narrow isolated investigation-family probe or decision note
  states whether broad-stack investigation performance is enough to classify the
  component as near ceiling, still diagnostic, or blocked by family-contract
  ambiguity.
- **Dependencies:** Initial component ceiling reports; X2 helpful if
  investigation is tested as part of an interaction pair.
- **Parallelizable:** yes, if scorer and bridge semantics stay frozen.
- **Owner:** unassigned.
- **Validation:** Report support counts, validation split, model/provider if
  any, scorer mode, precision/recall/F1, modality/result normalization policy,
  and any holdout residual caveat as diagnostic only.
- **Notes:** This routes the registry investigation action. Broad-stack
  stability is not enough by itself to call the investigation component solved.

## Done Or Frozen

The old R/A backlog is frozen as active guidance. Keep its evidence, but do not
pull from it directly without translating the work into one of the current
cards above. Detailed completion notes live in linked reports, generated
artifacts, and git history; this section only keeps the steering implications.

| Evidence | Current interpretation |
| --- | --- |
| C1-C4 architecture and registry cleanup, 2026-05-28 | The cleanup map, typed program variant registry, and active-status review exist. The live config tree remains loadable, but active authority is now separated from replay/provenance rows. |
| C10 registry provenance and Gan analysis script cleanup, 2026-05-28 | Historical cap-25 registry backfill specs moved to `docs/archive/experiments/synthesis/pre_component_pivot/hybrid_cap25_registry_backfill_manifest_20260528.json`; `scripts/backfill_hybrid_cap25_registry.py` now loads retained provenance instead of carrying static rows; `scripts/analyze_gan_frequency_run.py` exposes explicit canonical versus paper-reproduction scorer mode and paper options. Focused C10 export and Gan scorer tests passed. |
| C11 stage-level test surface split, 2026-05-28 | Public characterization tests now cover the intended replacement surfaces before broad monolithic retirement: Gan S0 routing/artifact/evidence guards in `tests/test_gan_s0_stage_surfaces.py`, Gan candidate inventory in `tests/test_gan_candidate_inventory.py`, Gan target-selection/label-construction in `tests/test_gan_target_label_split.py`, ExECT S1 raw/bridge/final artifact boundaries in `tests/test_exect_s1_boundary_surfaces.py`, ExECT frequency bridge/post-merge primitives in `tests/test_exect_frequency_primitives.py`, and ExECT S5 stack/frequency-verifier surfaces in `tests/test_exect_s5_frequency_verifier.py`. Validation: `uv run pytest tests/test_gan_s0_program.py tests/test_gan_candidate_inventory.py tests/test_gan_target_label_split.py tests/test_gan_s0_stage_surfaces.py tests/test_exect_s0_s1_program.py tests/test_exect_s1_boundary_surfaces.py tests/test_exect_frequency_primitives.py tests/test_exect_s4_program.py tests/test_exect_s5_frequency_verifier.py -q` passed. C18 consumed these replacement surfaces and is complete. |
| C12 unified archive path resolution, 2026-05-28 | `src/clinical_extraction/paths.py` now owns active/archive config and run resolution. Config loading, registry validation, ExECT residual-slice loading, residual replay scripts, explorer catalogs, and Gan G2 arm loading use the shared helpers; no configs or run directories were archived or renamed. Validation: `uv run pytest tests/test_experiment_configs.py tests/test_experiment_registry_validation.py -q`; explorer/residual smoke suites passed. |
| C13 program metric surface migration, 2026-05-28 | Gan S0 optimizer and feedback metrics now live in `clinical_extraction.gan.s0.metrics`; ExECT S0/S1 field-family optimizer metrics now live in `clinical_extraction.exect.s0_s1.metrics`. The program files re-export legacy imports for config/artifact compatibility. Validation: `uv run pytest tests/test_gan_s0_program.py tests/test_gan_scoring.py tests/test_gan_paper_reproduction_scoring.py tests/test_exect_s0_s1_program.py tests/test_exect_scoring.py -q` passed. Scorer semantics and benchmark caveats were preserved. |
| C14 Gan S0 program package decomposition, 2026-05-28 | `programs/gan_frequency_s0.py` is now a compatibility facade over `clinical_extraction.gan.s0.signatures`, `date_events`, `modules`, `optimizer_setup`, existing routing/candidate/target-selection/bridge modules, and metric surfaces. Builder-gap v1 and D1 v1.2b fixed-record parity tests were added. Validation: `uv run pytest tests/test_gan_s0_package_decomposition.py tests/test_gan_s0_program.py tests/test_gan_temporal_candidates.py tests/test_gan_slot_payload.py tests/test_gan_s0_stage_surfaces.py tests/test_gan_scoring.py tests/test_gan_paper_reproduction_scoring.py -q`; config/registry import validation also passed. Scorer semantics, Gan gold policy, and `unknown`/`no seizure frequency reference` separation were preserved. |
| C15 ExECT S0/S1 program package decomposition, 2026-05-28 | `programs/exect_s0_s1.py` is now an import-compatible facade over `clinical_extraction.exect.s0_s1` modules for constants, prompt/repair routing, signatures, DSPy modules, prediction artifact assembly, optimizer setup, and metric surfaces. Optimizer metrics now use the domain artifact assembly directly, and a facade parity characterization test locks the compatibility boundary. Validation: pre-refactor S0/S1 boundary suite passed; post-refactor `uv run pytest tests/test_exect_s0_s1_program.py tests/test_exect_s1_boundary_surfaces.py tests/test_exect_diagnosis_primitives.py tests/test_exect_medication_primitives.py tests/test_exect_scoring.py tests/test_exect_loader.py -q` passed; `uv run pytest tests/test_experiment_configs.py tests/test_experiment_arm_templates.py tests/test_exect_s1_split_audit.py -q` passed; `uv run pytest tests/test_exect_s4_program.py tests/test_exect_s5_scoring.py tests/test_exect_s5_frequency_verifier.py -q` passed. ExECT JSON gold policy, diagnosis specificity collapse, seizure-type bridge behavior, medication CUIPhrase/brand normalization, scorer semantics, loader behavior, and split contracts were preserved. |
| C16 ExECT S5 core split from S4, 2026-05-28 | S5 verifier signatures, verifier modules, pre-vocab/AM-guard/frequency-verify wrappers, and parallel S5-core module now live under `clinical_extraction.exect.s5_signatures` and `clinical_extraction.exect.s5_modules`, with stack metadata and guards retained in `clinical_extraction.exect.s5_stack`. `programs/exect_s4.py` remains an import-compatible facade and still routes legacy S4/S5 variants. Validation: `uv run pytest tests/test_exect_s4_program.py tests/test_exect_s5_scoring.py tests/test_exect_s5_frequency_verifier.py -q` passed; `uv run pytest tests/test_experiment_configs.py tests/test_experiment_registry_validation.py tests/test_experiment_runner.py -q` passed. This was behavior-preserving architecture work only; S5 v2b remains an operational stacked baseline, not an isolated component ceiling. |
| C17 ExECT primitive family module split, 2026-05-28 | `clinical_extraction.exect.primitives` is now an import-compatible facade over family-owned diagnosis, seizure-type, medication, and frequency primitive modules. Internal payload, interleaving, fixture, S0/S1, S2, S4, and S5 imports now use the family modules where appropriate. Primitive IDs and benchmark bridge behavior were preserved; registry implementation refs now point to the family modules. Validation: focused primitive suites plus `tests/test_exect_primitive_module_split.py` passed; `uv run python scripts/validate_primitives.py --errors-only` exited 0 with warnings for existing catalog/adapter/doc-ref gaps and no errors; S0/S1, S4/S5, payload, fixture, interleaving, config, and registry smoke suites passed. |
| C18 monolithic test retirement, 2026-05-28 | Direct private-helper assertions that blocked module-boundary cleanup were retired or moved behind public stage/domain surfaces. Gan S0 evidence/constrained-verifier guards, context-window assembly, and no-reference policy are covered through `clinical_extraction.gan.s0.prediction_bridge` / `gan.s0.modules` surfaces and `tests/test_gan_s0_stage_surfaces.py`; ExECT S1 diagnosis/medication boundary behavior is covered through `clinical_extraction.exect.s0_s1.prediction_artifacts` and `tests/test_exect_s1_boundary_surfaces.py`; ExECT S4 frequency, medication-temporality, and investigation recovery are covered through `clinical_extraction.exect.frequency_primitives`, `medication_primitives`, `investigation_primitives`, and slot-payload tests. Legacy program facades remain compatible; scorer, loader, split, and benchmark bridge semantics were preserved. Validation: focused C18 target suite `uv run pytest tests/test_gan_s0_stage_surfaces.py tests/test_gan_s0_program.py tests/test_exect_s1_boundary_surfaces.py tests/test_exect_s0_s1_program.py tests/test_exect_frequency_primitives.py tests/test_exect_frequency_slot_payload.py tests/test_exect_medication_temporality_primitives.py tests/test_exect_investigation_primitives.py tests/test_exect_s4_program.py tests/test_exect_s5_frequency_verifier.py -q` passed (283 tests); scorer/loader/primitive matrix passed (132 tests); config/registry matrix passed (255 tests); `uv run python scripts/validate_primitives.py --errors-only` exited 0 with existing warnings only; full suite `uv run pytest -q` passed (1030 tests, 16 warnings). |
| C5/C8 ExECT frequency substrate, 2026-05-28 | Broad frequency payload covers 43/43 validation gold labels and 24/24 gold-bearing documents, but broad precision is 22.2%; selection/adjudication is the active problem. |
| C6/C7/C9 boundary splits, 2026-05-28 | Gan S0 routing/bridge, ExECT S1 boundary metadata, and ExECT S5 stack surfaces were extracted as behavior-preserving architecture work. Use them for stage attribution; do not infer new metric claims. |
| E2 S1 raw/bridge/prompt split, 2026-05-28 | S1 validation strength depends heavily on benchmark bridges; holdout transfer drops keep diagnosis and seizure-type mechanisms open. |
| E3 medication payload, 2026-05-28 | Annotation-derived current-Rx payload reproduces 47/47 validation medication gold labels; lifecycle/temporality remains diagnostic or deferred until E5 decides the target policy. |
| E4 family-span payload, 2026-05-28 | `exect.sections.family_spans.v1` gives high evidence coverage and a cap-slice substrate; it is not promoted over full-note prompting until E8/E9. |
| G1/G2 Gan target split evidence, 2026-05-28 | Restrained high-recall deterministic candidates now cover 278/299 exact gold labels in G1, 292/299 Purist-equivalent labels, and 295/299 Pragmatic-equivalent labels; the G2 candidate-constrained arm has 299/299 selectable candidate support with no invalid candidate labels. Keep the remaining exact misses as a parser/adjudicator queue rather than forcing brittle 100% deterministic exact recall. |
| G3 Gan unknown vs no-reference policy probe, 2026-05-28 | Post-adjudication rules simulated on G2 predictions shows that checking option ambiguity flags successfully isolates policy choices (e.g. abstaining on uncertain denominators), trading off category accuracy for conservative precision. |
| X1 component ceiling registry backfill, 2026-05-28 | `component_ceiling_registry.md` now preserves row-level model/provider, split, scorer, config/run or artifact, bridge/normalization policy, classification, and caveat metadata for promoted baselines, diagnostic substrates, rejected arms, active risks, and blocked benchmark claims. |
| X3 registry matrix refresh, 2026-05-28 | `experiment_registry_matrix_20260520.md` is regenerated as a post-pivot registry-derived methods/provenance view with explicit R11-R15, X1, C4, C10, and May 28 component-pivot caveats. The obsolete research atlas exporter, tests, and generated outputs are removed. The matrix is not current steering authority without `component_ceiling_registry.md` and `program_variant_registry.md`. |
| C19 archive and obsolete-surface deletion, 2026-05-28 | Rejected, historical, and replay/provenance configs moved from `configs/experiments/` to `archive/configs/`, while `resolve_config_path` keeps basename replay working. Historical one-off scripts moved from `scripts/` to `archive/scripts/`, the program variant report now separates active and archived config inventory, and the live config tree contains current-authority rows only. Full suite validation passed (1002 tests). |
| Gan rejected or blocked arms, 2026-05-28 | CLINES-style entity-first prompting, self-consistency, broad relative-anchor guardrails, and Qwen GEPA without compact-delta clearance are not active pulls. |
| ExECT S5 v2b and holdout report | S5 v2b remains the operational stacked baseline. Holdout drops are residual-analysis triggers, not tuning targets or component-ceiling evidence. |

## Dependency Notes

- C1-C4 are complete enough to guide cleanup, but the modularity review shows
  the core program monoliths are still open. C12-C19 are complete; C20 is the
  active architecture completion gate that should reclassify or close the P1
  risks.
- C12 is complete and should be reused before archive moves or path-sensitive
  cleanup. It centralizes config/run fallback behavior so future file movement
  does not create path drift across loaders, registry validation, residual
  analysis, and explorer catalog scripts.
- C13 is complete: Gan and ExECT S0/S1 optimizer metric surfaces now live behind
  domain-owned metric modules while program-file legacy imports remain stable.
- C14 is complete: Gan S0 program signatures, date/event payload helpers,
  DSPy modules, optimizer setup, and variant factory now live under
  `clinical_extraction.gan.s0`, while the legacy program path remains an
  import-compatible facade.
- C15 is complete: ExECT S0/S1 constants, prompt/repair routing, signatures,
  DSPy modules, prediction artifact assembly, optimizer setup, and metric
  surfaces now live under `clinical_extraction.exect.s0_s1`, while the legacy
  program path remains an import-compatible facade.
- C16 is complete: ExECT S5 verifier signatures/modules and S5-core parallel
  stack wiring now live under `clinical_extraction.exect.s5_signatures` and
  `clinical_extraction.exect.s5_modules`, while `programs/exect_s4.py` remains
  an import-compatible facade. Do not interpret this architecture cleanup as a
  new S5 component result.
- C17 is complete: ExECT primitive imports now route through family-owned
  diagnosis, seizure-type, medication, and frequency modules while
  `clinical_extraction.exect.primitives` remains the legacy facade.
- C18 is complete: monolithic private-helper assertions that had public
  replacement surfaces have been retired from the Gan S0, ExECT S0/S1, and
  ExECT S4 parity tests. The retained monolithic tests are now compatibility
  and integration parity nets rather than blockers for module extraction.
- C19 is complete: archived configs now live under `archive/configs/`, archived
  scripts live under `archive/scripts/`, and generated program-variant
  navigation separates active and archived config inventory.
- C20 is now the completion gate: rerun a strict architecture review and update
  the audit status only after the code, tests, registry, and archive/delete path
  are actually settled.
- The typed program variant registry preserves loadable contracts and classifies
  registry/config rows as current-authority, replay/provenance, historical,
  rejected, blocked, or diagnostic.
- C6-C9 completed the first behavior-preserving architecture extractions: Gan
  S0 routing/bridge surfaces, ExECT S1 boundary metadata, ExECT frequency
  payload/bridge surfaces, and the ExECT S5 stack boundary. C18 has now consumed
  those surfaces for monolithic private-helper retirement.
- E2, E3, and E4 are complete as no-model/artifact-only ExECT decomposition
  audits, and G1 is complete as a no-model Gan candidate-inventory coverage
  report. ExECT frequency candidate-selection design can now consume C8; E3/E4
  follow-ups should use the completed substrates for isolated medication or
  family-span comparison plans, not broad-stack model runs.
- G3 is complete as a post-adjudication policy probe; use its ambiguity-flag
  findings to keep unknown/no-reference policy separate from new adjudicator
  prompt design.
- G4 is the explicit reason-code adjudicator follow-up, but it should consume
  G3 policy outputs rather than baking unknown/no-reference decisions into a new
  prompt surface.
- G5 is the registry-routed paper-scorer rescore pack; it is only needed before
  benchmark-comparison tables or paper claims, and it does not create Real(300)
  or Real(150) evidence.
- E5 is the policy gate before medication lifecycle/temporality can become a
  scored target. E6 is the current-Rx ceiling path; E7 is the stack-interference
  path. E8 tests the family-span mechanism, and E9 is the promotion/rejection
  decision after that comparison.
- E11 routes holdout residual attribution without tuning from holdout. E12
  routes the registry's unproven investigation-near-ceiling action.
- B1 is blocked until component substrates and isolated ceilings exist,
  including medication current-Rx and family-span follow-ups where they affect
  the optimized stack.
- C11 is complete: replacement public stage-level tests now cover Gan S0
  candidate inventory, target selection, label construction, bridge/evidence
  guards, artifact assembly, ExECT S1 raw/bridge/final boundaries, ExECT
  frequency bridge/post-merge primitives, and ExECT S5 stack/frequency-verifier
  surfaces. C18 consumed these surfaces and is now complete.
- C10 completed the provenance cleanup needed before generated registry
  navigation is refreshed: historical cap-slice backfill rows are retained in
  an archive manifest, and Gan analysis scripts now expose scorer mode and
  paper-reproduction options explicitly.
- X3 is complete: the registry matrix is refreshed as a post-pivot
  methods/provenance view with explicit authority caveats. Future regenerations
  should use the C19 active/archive inventory split so archived surfaces do not
  make navigation stale again.

## Parallelization Opportunities

- **Safe now:** C20 architecture completion review; G5 paper-scorer rescore if
  needed for a paper table; E5 medication lifecycle policy decision. These
  should preserve scorer, loader, split, and benchmark bridge semantics.
- **Architecture lane now in progress:** C20 should review the completed C12-C19
  extraction/archive lane, update residual risks, and decide whether any P1
  monolith concerns remain active.
- **Research lane still safe, but secondary:** E6, E8, E10, G4, and E11 remain
  valid work, but new broad model/prompt changes should wait until the current
  architecture lane is no longer the bottleneck.
- **Single-threaded or carefully sequenced:** C20 completion review, future
  registry/archive regeneration, and any change to scorer, loader, split,
  benchmark bridge, or shared primitive contracts.
- **Blocked together:** B1 waits on ExECT component ceilings.
- **Model-call gated:** E3/E4 audits are complete, so any related model run now
  needs a preregistered comparison against the full-note/current-stack baseline;
  any Gan selector full-validation run should wait until G3 policy isolation
  explains the remaining unknown/no-reference and LLM-option tradeoffs. G4
  should begin as a same-slice adjudicator comparison, not a full-validation
  promotion run.

## Recommended Next Pull

1. **C20 - Modularity Completion Review** should close the architecture lane by
   updating audit status, residual risks, and validation evidence.
2. **Then resume research-lane pulls** such as G5, E5, E6, E10, and E8
    according to paper/experiment need.

## Standing Guardrails

- Do not silently change scorer semantics; update tests and documentation when
  semantics change.
- Do not compare metrics across changed scorer modes unless the report says so
  explicitly.
- Use `gan2026_paper_reproduction` for Gan paper-comparison tables.
- Keep Gan canonical `unknown` and `no seizure frequency reference` distinct
  except inside explicitly named paper-reproduction scorer views.
- Treat ExECT clean ladder results as diagnostic baselines, not component
  ceilings.
- Do not describe `archive/configs` loadability as active experiment count;
  active config authority lives in `configs/experiments` and the generated
  registry report's active inventory.
- Treat rejected arms as rejected arms unless a mechanism-level review closes
  the mechanism.
- Holdout metrics trigger residual analysis only; do not tune from holdout.
- Prefer typed payloads, primitives, bridges, and scorer policies over prompt
  bloat and broad mode flags.
