# Clinical Extraction Kanban Plan

Status: active steering doc
Last refreshed: 2026-05-29 G9/G10 Gan follow-up cards
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

1. **Use E11 as a completed residual router, not a tuning source.** E11
   attributes the ExECT validation-to-holdout drop without scorer, loader,
   split, bridge, prompt, prediction-repair, or artifact changes. S1 loss is
   concentrated in diagnosis/seizure-type transfer while medication is stable;
   S5 frequency loss is mixed payload-generalization plus adjudication.
2. **ExECT work starts from isolated family questions.** Use the completed
   frequency, medication, S1 raw/bridge/prompt, and family-span substrates to
   measure ceilings or explain interference: investigation confirmation (E12),
   validation-only S1 transfer probes, frequency payload
   robustness/adjudication, and medication payload routing or prompt isolation.
   Optimized S1*/S2*/S3*/S4*/S5* stacks remain blocked until isolated ceilings
   and pairwise interactions exist.
3. **Gan S0 work stays decomposed.** Use D1 v1.2b and the G1/G2/G3 artifacts to
   separate candidate inventory, temporal anchoring, target selection, label
   construction, and unknown/no-reference policy. G4 is completed as a negative
   same-slice traceability result; use its failure records and the G5
   scorer-mode forensics before trying another seizure-free-versus-quantified
   selector. G6 now fixes the evaluation surface: use the old 25-record
   enriched slice only for smoke checks, use `gan_s0_g6_standard50_v1` for
   default mechanism comparisons, and use named challenge sets only with their
   declared decision scopes. Use the completed G5 rescore pack before any
   synthetic paper-facing comparison. For plain-English handoff language, use
   `docs/experiments/gan/gan_s0_key_axes_progress_report_20260528.md`: we are
   now strong at finding possible answers and formatting a chosen answer, but
   still weakest at choosing the right answer when a note contains competing
   signals. G8 completed the G7 class-first selector as a rejected arm: trace
   fields were complete, but standard50 paper monthly was 37/50, below D1
   (40/50) and builder-gap GPT (41/50), with regressions on seizure-free versus
   quantified and unknown/no-reference overlays.
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

### G9 - Gan G8 Exact-Miss And Special-Class Failure Inspection

- **Outcome:** No-model inspection of the G8 standard-50 failures decides
  whether the four standard-50 exact-miss records require a candidate-inventory
  challenge-set pass before another selector run, and separates
  candidate-coverage failures from target-selection or label-policy failures.
- **Dependencies:** G8 report
  `docs/experiments/gan/gan_s0_g8_special_class_target_selector_report_20260529.md`;
  G6 standard/challenge surfaces; G1 candidate inventory substrate; G2
  target/label split; G5 scorer-mode forensics.
- **Parallelizable:** yes, with ExECT mechanism-card drafting. Do not run in
  parallel with another Gan selector model call.
- **Owner:** unassigned.
- **Validation:** Produce a record-level inspection table for the 13 G8
  paper-monthly misses, with special focus on the four standard-50 exact-miss
  records (`gan_15997`, `gan_16772`, `gan_16825`, `gan_16335`). Include
  candidate labels, whether gold is present in candidates, selected label,
  target semantic class, reason code, challenge tags, and a decision on whether
  candidate inventory is the next bottleneck.
- **Notes:** No model calls and no scorer, loader, split, bridge,
  candidate-builder, or prediction-repair changes. The output should route the
  next pull to either G10 or G11.

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

### G10 - Gan Standard50 Candidate-Constrained/Answer-Options Comparator

- **Outcome:** Preregistered model-backed comparison on
  `gan_s0_g6_standard50_v1` directly compares a candidate-constrained or
  answer-options selector against D1 v1.2b and builder-gap GPT on the same
  records.
- **Dependencies:** G9 decides candidate inventory is adequate for this
  comparator, or G11 has closed the exact-miss candidate-coverage issue; G6
  evaluation surface; G8 negative report; stored D1 and builder-gap GPT
  predictions.
- **Parallelizable:** only after G9 routing. Do not overlap with other local
  model-backed Gan selector runs.
- **Owner:** unassigned.
- **Validation:** Dry-run config first, then standard-50 model run. Report both
  `gan2026_paper_reproduction` and `gan_frequency_deterministic_v1`,
  per-challenge overlays, pairwise deltas versus D1 and builder-gap GPT, trace
  fields, and stop rule. Do not full-validate unless the selector shows at
  least two-record monthly lift over the relevant comparator, no paper-metric
  regression, and no targeted-overlay regression.
- **Notes:** This must not be another special-class-label expansion of the same
  class-first prompt. The mechanism under test is candidate-constrained or
  answer-options selection with scorer, loader, split, bridge,
  candidate-builder, and prediction-repair semantics preserved.

### G11 - Gan Candidate-Inventory Challenge-Set Pass

- **Outcome:** If G9 finds the four exact-miss records are candidate-coverage
  failures, design and run a candidate-inventory pass on a focused
  exact-miss/challenge surface before making another selector claim.
- **Dependencies:** blocked until G9 routes exact-miss failure to candidate
  inventory.
- **Parallelizable:** after G9, but not with changes to the candidate-builder
  contract.
- **Owner:** unassigned.
- **Validation:** No-model candidate-coverage report over the named challenge
  set, with gold exact/Purist/Pragmatic coverage, candidate diff versus the G1
  substrate, and an explicit decision on whether candidate-builder changes are
  needed before G10.
- **Notes:** This card should remain blocked unless G9 identifies candidate
  inventory as the bottleneck.

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
- **Family-span prompting is closed as a rejected arm.** E8 compared full-note
  S1 clean-ladder prompting with E4 family-span prompting on the same cap-25 GPT
  validation slice. Family-span context covered 116/116 selected-family gold
  annotations and used 88.8% of full-note characters, but micro F1 dropped from
  95.8% to 90.2%, driven by seizure-type F1 falling from 95.4% to 81.8%.
  E9 classifies the E8 single-pass S1 family-span replacement arm as a rejected
  arm while preserving `exect.sections.family_spans.v1` as a diagnostic
  document-geometry substrate. Do not rerun the same broad context-substitution
  arm; reopen only with a narrower preregistered mechanism and an explicit
  comparator.
- **E11 attributed the ExECT holdout drop without tuning.** S1 GPT drops from
  92.3% to 77.8% micro because diagnosis and seizure-type transfer degrade
  sharply while medication is stable. S5 GPT frequency drops from 73.9% to
  47.1% F1 through both payload-generalization and adjudication: broad payload
  coverage is 43/43 labels on validation but 31/44 on holdout. Medication
  current-Rx remains representable on holdout at 53/53 labels, so S5 medication
  loss is stack behavior rather than a substrate failure. Report:
  `docs/experiments/exect/exect_holdout_residual_attribution_e11_20260528.md`.
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
- **G6 fixed the Gan selector evaluation surface.** The G2/G4 enriched slice is
  now `gan_s0_g6_traceability_smoke_25` and is smoke-only: one record equals
  4.0pp and two records equal 8.0pp. New selector/adjudicator mechanisms should
  use `gan_s0_g6_standard50_v1` for default slice comparisons, named challenge
  sets only for their declared component scope, and full validation before any
  baseline promotion. Decision report:
  `docs/experiments/gan/gan_s0_g6_evaluation_slice_standard_decision_20260528.md`.
- **G7 preregistered the next Gan selector mechanism.** The preregistration
  narrows the next model-backed arm to target-selection policy for special
  classes: quantified current frequency versus seizure-free duration,
  unknown/no-reference boundaries, and scorer-discordance preservation. It
  requires `gan_s0_g6_standard50_v1` for mechanism comparison, keeps the old
  25-record slice smoke-only, reports both Gan scorer views, and forbids
  scorer, loader, split, bridge, candidate-builder, or prediction-repair
  changes. Protocol:
  `docs/experiments/gan/gan_s0_g7_special_class_target_selector_preregistration_20260528.md`.
- **G8 rejected the class-first special-selector arm as tested.** The smoke run
  preserved target semantic class, selected-candidate reference,
  label-construction inputs, adjudication JSON, and D1 date/event payload in
  25/25 records, so it passed the traceability stop rule. The standard50 run
  scored 37/50 paper monthly and 36/50 canonical monthly, below D1 v1.2b
  (40/50 paper) and builder-gap GPT (41/50 paper) on the same records. It also
  regressed on seizure-free versus quantified (13/21 versus D1 17/21) and
  unknown/no-reference (6/10 versus D1 9/10). Do not full-validate this arm.
  Report:
  `docs/experiments/gan/gan_s0_g8_special_class_target_selector_report_20260529.md`.
- **Gan S0 now has a plain-English component handoff.** The key-axes progress
  report translates the decomposition into reader-facing components:
  frequency-content gate, candidate inventory, temporal anchoring, target
  selection, label construction, aggregation, unknown/no-reference policy, and
  evidence/schema checks. The practical summary is that current systems are
  strong at finding possible answers and reasonably good at formatting a chosen
  answer, while the open bottleneck is choosing the right answer when a note
  contains competing signals. Report:
  `docs/experiments/gan/gan_s0_key_axes_progress_report_20260528.md`.
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
- E8 completed the family-span cap-slice prompt comparison, and E9 rejected the
  tested S1 family-span replacement arm while preserving the span substrate as
  diagnostic. Any follow-up needs a narrower preregistered mechanism.
- E10 completed the first frequency candidate-selection split. Treat the broad
  payload as fixed recall substrate and pull a new mechanism card for any
  model-backed adjudicator/ranker comparison.
- G4 and any follow-up depend on G2 target/label split outputs, G3
  policy-isolation findings, and the G5 scorer-mode forensics; keep target
  selection, label construction, seizure-free, unknown/no-reference policy, and
  scorer-discordant records separable in artifacts and reports.
- G6 completed the no-model evaluation-surface decision. Any new Gan selector
  mechanism card should name whether it targets the 50-record standard slice,
  a named challenge set, or full validation, and must preserve scorer, loader,
  split, and benchmark bridge semantics.
- G8 completed the first G7-protocol model-backed arm and rejected the
  class-first special-class prompt as tested. Another Gan selector pull should
  either compare a standard50 candidate-constrained/answer-options selector
  directly or first inspect the G8 standard50 exact-miss and special-class
  failures; do not rerun the same class-first prompt shape.
- G9 is the required no-model gate before G10 or G11. It should classify the G8
  misses by candidate coverage, target-selection failure, and label-policy
  failure before any new Gan selector call.
- G10 is blocked until G9 says exact-miss candidate coverage is adequate for a
  selector comparison, or until G11 closes a candidate-inventory gap.
- G11 starts only if G9 routes the exact-miss failures to candidate inventory.
  It should not mutate candidate-builder behavior without a separate scoped
  implementation card.
- The Gan key-axes progress report is the handoff reference for plain-English
  component names. Use it to keep G8 interpretation centered on the actual
  failure stage rather than on implementation jargon.
- G5 is complete and should be used for synthetic-only paper-facing Gan tables.
  Its scorer-mode forensics note is G4 follow-up input; it does not unblock Gan
  real-note reporting.
- E11 completed the primary holdout residual attribution. Treat it as a router
  for validation-only follow-ups; do not tune prompts, scorers, loaders,
  bridges, repairs, or splits from holdout rows.
- B1 stays blocked until isolated component ceilings and pairwise interaction
  evidence exist. Substrates alone are not enough to rebuild optimized stacks.

## Parallelization Opportunities

- **Safe now:** pull G9 for a no-model G8 failure inspection, draft a new
  validation-only ExECT mechanism card from E11 findings before any model
  calls, or do error-analysis/readme cleanup tied to completed Gan artifacts.
  Any downstream Gan selector/adjudicator run must use the G6
  evaluation-surface protocol and preserve scorer, loader, split, benchmark
  bridge, candidate-builder, and prediction-repair semantics.
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
  needs a preregistered comparison against the full-note/current-stack baseline.
  G10 and other Gan selector model calls wait on G9 routing, and any Gan
  selector full-validation run should wait until the standard-50 mechanism has
  cleared its stop rule. G11 candidate-inventory work waits unless G9 identifies
  candidate coverage as the bottleneck.

## Recommended Next Pull

1. Pull G9 first: inspect the G8 standard-50 misses and decide whether the four
   exact-miss records are a candidate-inventory problem or a selector/policy
   problem.
2. In parallel, draft the ExECT validation-only mechanism card from E11 for S1
   transfer, frequency payload robustness/adjudication, or medication payload
   routing. Holdout rows remain residual evidence only.
3. If G9 says candidate inventory is adequate, pull G10 and compare the
   standard-50 candidate-constrained/answer-options selector directly against
   D1. If not, pull G11 before G10.
4. For additional pruning, first write a new card that names the runtime
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
