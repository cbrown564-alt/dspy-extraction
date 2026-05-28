# Clinical Extraction Kanban Plan

Status: active steering doc
Last refreshed: 2026-05-28 G4 completion and Gan slice-standard planning
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
   should move G6, E9, or E11 according to the immediate research
   or paper need. Do not add new ExECT schema grids or Gan "better prompt"
   loops unless the varied factor maps to a component in
   `component_ceiling_registry.md`.
2. **ExECT work starts from isolated family questions.** Use the completed
   frequency, medication, S1 raw/bridge/prompt, and family-span substrates to
   measure ceilings or explain interference: family-span decisioning (E9),
   holdout residual attribution (E11), investigation confirmation (E12), and
   the next frequency adjudicator/ranker mechanism after E10.
   Optimized S1*/S2*/S3*/S4*/S5* stacks remain blocked until isolated ceilings
   and pairwise interactions exist.
3. **Gan S0 work stays decomposed.** Use D1 v1.2b and the G1/G2/G3 artifacts to
   separate candidate inventory, temporal anchoring, target selection, label
   construction, and unknown/no-reference policy. G4 is completed as a negative
   same-slice traceability result; use its failure records and the G5
   scorer-mode forensics before trying another seizure-free-versus-quantified
   selector. The 25-record enriched slice is already saturated for selector
   comparisons, so use G6 to decide when a 50-record slice or named challenge
   set should replace more one- or two-label same-slice variation. Use the
   completed G5 rescore pack before any synthetic paper-facing comparison.
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

### G6 - Gan Evaluation Slice Standard And Challenge Sets

- **Outcome:** A decision report defines the default evaluation surface for new
  Gan S0 selector/adjudicator mechanisms: retain 25-record enriched slices only
  for smoke checks, expand standard mechanism comparisons to a 50-record slice,
  introduce named challenge sets, or use both with distinct decision scopes.
- **Dependencies:** G2 model-arm comparison, G3 policy isolation, G4 explicit
  reason-code adjudicator result, and G5 scorer-mode forensics complete.
- **Parallelizable:** yes for no-model slice design and record selection; any
  model-backed reruns should wait until the slice/challenge-set protocol is
  fixed.
- **Owner:** unassigned.
- **Validation:** Report record IDs, label-family strata, gold labels, challenge
  tags, scorer views, denominator effects, and stop rules. Quantify how one-
  and two-record deltas behave on 25-record versus 50-record surfaces, and name
  which challenge sets are intended for target selection, seizure-free versus
  quantified policy, unknown/no-reference policy, candidate coverage, clusters,
  and temporal anchoring.
- **Notes:** The G2/G4 25-record slice is useful but near-saturated: at 25
  records, one label is 4.0pp and two labels are 8.0pp, so many follow-up claims
  would be minor variations around a small number of cases. This card should
  prevent small-slice tuning from masquerading as mechanism progress.

No current ready ExECT card sits ahead of E9/E11. Pull from Backlog only when
the dependency note below names the completed evidence needed for that card.

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
  E3/E4 provide substrates only; E6-E8 plus pairwise interaction work are still
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
- **Medication stack interference is now attributed.** E7 shows S5 medication
  loss is over-emission, not current-Rx coverage failure: S5 has 12 false
  positives and no false negatives, including 8 S5-only false positives, 4
  shared S1/S5 false positives, and 2 recovered S1 false negatives. The next
  medication mechanism should be payload routing or prompt isolation before a
  broader temporality guard.
- **Frequency candidate selection is now split from payload coverage.** E10
  shows the broad event/rate payload is recall-sufficient but not
  prediction-ready: direct promotion scores 22.2% precision, 100.0% recall, and
  36.3% F1. A gold-constrained oracle over the same broad candidates reaches
  100.0% F1, while S5 GPT reaches 73.9% frequency F1. The next frequency
  mechanism should be a candidate adjudicator or ranker against the fixed broad
  payload, not another coverage audit or broad-stack prompt loop.
- **Family-span prompting failed the first promotion gate.** E8 compared full-note
  S1 clean-ladder prompting with E4 family-span prompting on the same cap-25 GPT
  validation slice. Family-span context covered 116/116 selected-family gold
  annotations and used 88.8% of full-note characters, but micro F1 dropped from
  95.8% to 90.2%, driven by seizure-type F1 falling from 95.4% to 81.8%.
  Route E9 as a rejection/diagnostic-only decision for this arm shape unless a
  narrower mechanism is preregistered.
- **G4 is complete and should not be pulled again as tested.** The explicit
  reason-code adjudicator preserved selected-candidate references and
  label-construction inputs in 25/25 records, but scored only 80.0%
  monthly/pragmatic on the enriched 25-record Gan slice, below the G2
  candidate-constrained and seeded selector baselines. All five misses were
  target-selection failures with seizure-free-over-quantified policy signals.
  Report:
  `docs/experiments/gan/gan_s0_g4_explicit_reason_code_adjudicator_report_20260528.md`.
- **Gan S0 has decomposition evidence, not a solved selector.** The candidate
  inventory and target/label split establish useful coverage and selected-slice
  behavior; unknown versus no-reference policy informed G4 and remains input to
  future selector challenge sets. G5 rescored the current promoted synthetic
  baselines under `gan2026_paper_reproduction`: builder-gap GPT 79.9% monthly,
  builder-gap Qwen 70.2%, and D1 v1.2b 76.6%, with repair/range/tolerance
  disabled.
  The G5 scorer-mode forensics isolate D1's paper-scorer loss as mostly
  special-class target semantics, especially seizure-free gold labels predicted
  as `no seizure frequency reference`; use that note before any Gan selector
  follow-up.
  External Gan benchmark claims remain blocked without Real(300)/Real(150) or
  an explicitly synthetic-only comparison protocol.
- **Gan 25-record selector slices are now denominator-limited.** The G2/G4
  enriched slice is valuable for fast mechanism checks, but one record equals
  4.0pp and two records equal 8.0pp. Future Gan selector claims should first
  pass through G6, which decides whether 50-record standard slices, named
  challenge sets, or both are the right evaluation surface.
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

- E7 completed the medication stack-interference attribution. Treat lifecycle
  categories as diagnostic only; do not change the medication scorer or bundle
  temporality recovery into broad S5 prompts without a new mechanism card.
- E8 completed the family-span cap-slice prompt comparison. E9 can now decide
  whether this prompt shape is rejected, diagnostic-only, or still mechanism-open
  for a narrower follow-up.
- E10 completed the first frequency candidate-selection split. Treat the broad
  payload as fixed recall substrate and pull a new mechanism card for any
  model-backed adjudicator/ranker comparison.
- G4 and any follow-up depend on G2 target/label split outputs, G3
  policy-isolation findings, and the G5 scorer-mode forensics; keep target
  selection, label construction, seizure-free, unknown/no-reference policy, and
  scorer-discordant records separable in artifacts and reports.
- G6 consumes the completed G2/G3/G4/G5 evidence and should be model-call-free
  until the 50-record slice or challenge-set protocol is fixed.
- G5 is complete and should be used for synthetic-only paper-facing Gan tables.
  Its scorer-mode forensics note is G4 follow-up input; it does not unblock Gan
  real-note reporting.
- E11 may consume E2, E6/E7, and E10 evidence, but holdout remains residual
  analysis only. Do not tune prompts, scorers, loaders, bridges, or splits from
  holdout.
- B1 stays blocked until isolated component ceilings and pairwise interaction
  evidence exist. Substrates alone are not enough to rebuild optimized stacks.

## Parallelization Opportunities

- **Safe now:** G6, E9, and E11 as preregistered component or residual-analysis
  pulls. G6 should be no-model evaluation-design work first; any downstream Gan
  selector rerun should preserve scorer, loader, split, and benchmark bridge
  semantics.
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
  explains the remaining unknown/no-reference and LLM-option tradeoffs. Any new
  Gan selector slice rerun should wait for G6 to decide whether the correct
  surface is a 50-record standard slice, named challenge set, or both.

## Recommended Next Pull

1. For Gan selector work, pull **G6** before running another small-slice model
   variant; its first deliverable is an evaluation-surface decision, not model
   calls.
2. For ExECT research execution, pull **E9 or E11** according to paper or
   experiment need.
3. For additional pruning, first write a new card that names the runtime
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
