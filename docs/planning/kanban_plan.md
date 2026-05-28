# Clinical Extraction Kanban Plan

Status: active steering doc
Last refreshed: 2026-05-28 active-priority board prune
Supersedes: the pre-pivot R/A backlog as active priority guidance

This board is current-first. Completed work is summarized only where it changes
active sequencing. The architecture lane is closed as a bottleneck, and the
remaining pulls are organized around two priorities:

1. preserve the simplified architecture so the decomposition program stays easy
   to follow, test, and extend;
2. run experiments around the May 28 component-ceiling research program,
   not around old broad-pipeline improvement loops.

Historical cards, rejected arms, and old backlog detail remain provenance in
`kanban_frozen_threads_history.md`, experiment notes, archive indexes, and run
artifacts. They are not active guidance unless this board,
`current_research_program.md`, or `component_ceiling_registry.md` explicitly
promotes them.

## Current Priorities

1. **Pull component experiments, not broad-pipeline polish.** The active board
   should move E7, E8, E10, G4, G5, or E11 according to the immediate research
   or paper need. Do not add new ExECT schema grids or Gan "better prompt"
   loops unless the varied factor maps to a component in
   `component_ceiling_registry.md`.
2. **ExECT work starts from isolated family questions.** Use the completed
   frequency, medication, S1 raw/bridge/prompt, and family-span substrates to
   measure ceilings or explain interference: medication over-emission (E7),
   family-span prompting (E8/E9), frequency candidate selection (E10),
   holdout residual attribution (E11), and investigation confirmation (E12).
   Optimized S1*/S2*/S3*/S4*/S5* stacks remain blocked until isolated ceilings
   and pairwise interactions exist.
3. **Gan S0 work stays decomposed.** Use D1 v1.2b and the G1/G2/G3 artifacts to
   separate candidate inventory, temporal anchoring, target selection, label
   construction, and unknown/no-reference policy. G4 is the next adjudicator
   design path; G5 is the benchmark-scorer rescore path before any paper-facing
   comparison.
4. **Benchmark and scorer policy are frozen unless explicitly changed.** Gan
   paper comparisons use `gan2026_paper_reproduction`; canonical Gan metrics
   remain diagnostic. ExECT Table 1 reproduction remains blocked until
   CUI-aware all-family scoring exists. Holdout metrics trigger residual
   analysis only; do not tune from holdout.
5. **Architecture is now a constraint, not the main workstream.** C12-C32 closed
   the scoped cleanup and active-authority pass. Ordinary config, run, and
   program factory resolution is active-only by default; historical, rejected,
   and replay/provenance configs require explicit archive/reporting opt-in.
   Additional cleanup needs a new card naming the active runtime contract being
   removed.
6. **Completed work is context, not a pull list.** Use
   `component_ceiling_registry.md` for row-level provenance and this board for
   active sequencing. Frozen C-card/R/A history should not re-enter the board
   unless translated into a current component, benchmark, or runtime-contract
   card.

## Ready

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
  E3/E4 provide substrates only; E6-E10 and pairwise interaction work are still
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
- **Dependencies:** initial component ceiling reports; a new lifecycle target
  policy before treating medication+temporality as a scored pair.
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

## Recent Developments For Context

These are the only completed-work facts that should influence the next pull.
Detailed card history belongs in linked reports, generated artifacts, archive
indexes, and git history.

- **Architecture cleanup is no longer blocking research.** The C12-C20
  decomposition work closed the original P1 monolith risks or reclassified them
  as accepted residual P2/provenance risks. Gan S0, ExECT S0/S1, ExECT S4/S5,
  family primitives, active/archive config resolution, and public stage tests
  now have domain-owned surfaces. This was behavior-preserving cleanup, not new
  scorer or dataset evidence.
- **Active authority is current-only by default.** Historical configs, rejected
  variants, replay/provenance rows, and archived one-off scripts now require
  explicit archive or reporting opt-in. Ordinary config resolution, registry
  validation, and program factories should expose current-authority variants
  only unless a replay/reporting task says otherwise.
- **Static and compatibility cleanup has been spent.** High-confidence
  deadweight was deleted, script entrypoints were classified, current report
  builders moved under `clinical_extraction.evaluation.*`, obsolete facade tests
  were shrunk, and `ruff`/`vulture` were brought clean on `src scripts tests`.
  Do not add more cleanup cards unless they name a concrete active runtime
  contract to remove.
- **ExECT substrates exist, but most ceilings are still open.** Frequency
  event/rate payload covers 43/43 validation gold labels but has low precision;
  S1 raw/bridge/prompt attribution exists; medication current-Rx has a no-model
  validation ceiling substrate at 47/47; lifecycle/temporality is diagnostic
  only; family spans have strong evidence coverage but need full-note comparison
  before promotion.
- **Gan S0 has decomposition evidence, not a solved selector.** The candidate
  inventory and target/label split establish useful coverage and selected-slice
  behavior; unknown versus no-reference policy is now isolated enough to guide
  G4. Paper-comparison claims still require G5 rescoring with
  `gan2026_paper_reproduction`.
- **The component registry is the provenance map.** `component_ceiling_registry.md`
  carries row-level model/provider, split, scorer, run/artifact, bridge policy,
  classification, and caveat metadata. This Kanban should not duplicate that
  ledger.

## Frozen Work

The old R/A backlog and completed C-card cleanup lane are frozen as active
pull sources. Keep their evidence, but do not pull from them directly without
translating the work into one of the current cards above or a new card with a
clear active dependency.

## Dependency Notes

- E7 depends on the completed medication payload and E6 ceiling substrate; it
  should explain S5 over-emission before any medication prompt or bridge change.
- E8 depends on the completed family-span payload; E9 is only a decision card
  after E8 compares family spans against the full-note baseline.
- E10 depends on the completed ExECT frequency payload and bridge surfaces; its
  question is candidate selection/adjudication, not another coverage audit.
- G4 depends on G2 target/label split outputs and G3 policy-isolation findings;
  keep target selection, label construction, and unknown/no-reference policy
  separable in artifacts and reports.
- G5 is only needed before paper or benchmark-comparison claims. It does not
  unblock Gan real-note reporting.
- E11 may consume E2, E6/E7, and E10 evidence, but holdout remains residual
  analysis only. Do not tune prompts, scorers, loaders, bridges, or splits from
  holdout.
- B1 stays blocked until isolated component ceilings and pairwise interaction
  evidence exist. Substrates alone are not enough to rebuild optimized stacks.

## Parallelization Opportunities

- **Safe now:** G5 paper-scorer rescore if needed for a paper table; E7, E8,
  E10, G4, and E11 as preregistered component or residual-analysis pulls. These
  should preserve scorer, loader, split, and benchmark bridge semantics.
- **Architecture lane closed as bottleneck:** C31/C32 closed the currently
  scoped active-priority pruning pass. Any new cleanup should start from a
  concrete runtime contract or active-authority ambiguity, not from historical
  card carryover.
- **Single-threaded or carefully sequenced:** future registry/archive
  regeneration and any change to scorer, loader, split, benchmark bridge, or
  shared primitive contracts. ExECT component-ceiling work remains
  sequencing-sensitive where it changes S5, S0/S1, or active runtime contracts.
- **Blocked together:** B1 waits on ExECT component ceilings.
- **Model-call gated:** E3/E4 audits are complete, so any related model run now
  needs a preregistered comparison against the full-note/current-stack baseline;
  any Gan selector full-validation run should wait until G3 policy isolation
  explains the remaining unknown/no-reference and LLM-option tradeoffs. G4
  should begin as a same-slice adjudicator comparison, not a full-validation
  promotion run.

## Recommended Next Pull

1. For research execution, pull **G5, E7, E10, E8, or G4** according to paper
   or experiment need, keeping each run preregistered and component-scoped.
2. For additional pruning, first write a new card that names the runtime
   contract to remove; C31/C32 closed the currently scoped ExECT active-priority
   pruning pass.

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
- Do not describe `archive/configs` as active experiment loadability; active
  config authority lives in `configs/experiments` and the generated registry
  report's active inventory. Archive artifacts remain traceable through docs,
  git history, and explicit replay/reporting opt-ins.
- Treat rejected arms as rejected arms unless a mechanism-level review closes
  the mechanism.
- Holdout metrics trigger residual analysis only; do not tune from holdout.
- Prefer typed payloads, primitives, bridges, and scorer policies over prompt
  bloat and broad mode flags.
