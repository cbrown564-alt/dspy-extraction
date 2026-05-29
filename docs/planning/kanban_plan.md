# Clinical Extraction Kanban Plan

Status: active steering doc
Last refreshed: 2026-05-29 completed G21 aggregation constructor implementation
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
   X2 now preregisters pairwise interaction hypotheses, support counts,
   primary metrics, interference criteria, and stop rules. The May 29 X2
   result correction makes clear that schema-ladder comparisons are
   non-answering diagnostics, not completed pairwise evidence. Optimized
   S1*/S2*/S3*/S4*/S5* stacks remain blocked until isolated ceilings and
   corrected component-isolated pairwise interaction evidence exist.
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
   quantified and unknown/no-reference overlays. G11 completed the no-model
   candidate-coverage challenge pass: the locked 21-record G6 exact-miss
   surface remains 0/21 exact, 14/21 Purist-equivalent, and 17/21
   Pragmatic-equivalent. This should not be treated as a simple candidate-builder
   defect because some gold labels require temporal anchoring and aggregation
   across separately reported events. G12 has now explicitly narrowed G10:
   before a new aggregation constructor exists, G10 may test category-level or
   candidate-ranking selection only, not exact closed answer-option
   construction. G10 has now tested that narrowed selector arm and is rejected
   as tested: it reached 36/50 paper monthly on `gan_s0_g6_standard50_v1`,
   below G8 (37/50), D1 v1.2b (40/50), and builder-gap GPT (41/50), with
   complete category/ranking traces but regression on the unknown/no-reference
   overlay. Do not full-validate this arm. G18 is complete for the source-level candidate-interface bug:
   current runtime and the G11 current rows have 0 cases where broad standalone
   abstentions (`unknown`, `no seizure frequency reference`) are offered beside
   concrete frequency candidates. The older G1 lists remain provenance for the
   pre-pruning surface. G13 now supplies the isolated frequency-content gate
   baseline: overall gate accuracy is 244/299 (81.6%), with strong
   quantified-frequency recall (201/203, 99.0%) and no-reference precision
   (10/10 predicted no-reference rows), but weak unclear-frequency recall
   (10/40, 25.0%) and seizure-free recall (23/45, 51.1%). G14 now supplies the
   temporal anchoring diagnostic baseline: standard50 exact candidate coverage
   is 41/50 and temporal-slot coverage is 36/40 applicable rows; the temporal
   challenge set is 13/15 exact and slot-covered, with `gan_16772` and
   `gan_16825` as true temporal-slot misses. G15 then tested an LLM
   support-aware target selector with G13/G14 caveats carried forward and is
   rejected as tested: support context was present for 50/50 records, but paper
   monthly fell to 31/50, below G10 (36/50), G8 (37/50), D1 v1.2b (40/50),
   and builder-gap GPT (41/50), with regressions on target-selection,
   seizure-free-versus-quantified, and unknown/no-reference overlays. Do not
   full-validate G15. G16 now defines the no-model aggregation policy: 16/21
   G11 exact-miss rows are blocked on aggregation or duration policy before
   exact closed-answer options, and standard50 has four quantified rate
   aggregation blocks. Exact closed-option selector claims remain blocked until
   a deterministic constructor or preregistered model mechanism satisfies that
   policy. G19 has now completed the post-G16 attribution audit: across the
   five inspected standard50 arms, the leading arm-miss classes are aggregation
   blocks with missing temporal slots (16 arm-misses / 4 rows), unclear or
   unknown-cluster evidence misrouted as concrete (15 / 6), seizure-free over
   quantified target selection (11 / 6), and wrong quantified rate/window
   selection (11 / 5). G20 preregistered a deterministic, fixture-first
   quantified-rate aggregation constructor for the G19 aggregation block, and
   G21 has now implemented the first scoped constructor: Standard50 exact option
   coverage rises from 41/50 raw to 45/50 combined, and the G11 exact-miss
   challenge reaches 12/21 constructed exact with zero deferred or
   negative-control constructions. This is answer-option coverage, not selector
   performance. G17 has now completed the special-label policy separation:
   the active unknown/no-reference surface is a nine-row slice covering
   unclear-frequency, unknown-cluster, seizure-free/no-reference scorer
   discordance, and concrete-rate overcall cases, with zero deterministic repair
   candidates. Any new selector needs a card that cites the specific G19/G17
   class it intends to reduce.
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

No implementation card is currently ready by default. The next pull should be a
new scoped card: either an ExECT validation-only mechanism card from E11/X2, or
a Gan selector/adjudicator card that explicitly cites the G19/G17 class it
targets and uses the G21 constructed-option surface with a row-level before/after
ledger.

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

## Recent Developments For Context

These are the only completed-work facts that should influence the next pull.
Detailed card history belongs in linked reports, generated artifacts, archive
indexes, and git history.

- **X2 pairwise interaction results were corrected as non-answering.** The
  earlier Pair 4 S1-versus-S2 and Pair 3 S4-guard comparisons followed schema
  ladder surfaces, so they are diagnostic provenance only and do not promote or
  reject the pairwise mechanisms. Corrected Pair 3 must compare annotated
  medication alone against annotated medication plus medication temporality,
  with annotated medication as the sole scored endpoint. Corrected Pair 4 must
  use investigation-only and comorbidity-only directional component arms rather
  than S1 versus S2. B1 remains blocked. Report:
  `docs/experiments/exect/exect_pairwise_interaction_results_x2_20260529.md`.
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
- **E12 investigation ceiling is confirmed.** Analysis across validation and
  test splits shows the isolated investigation component reaches 90.4% - 97.2%
  F1. Mismatches are minor and driven by gold omissions and clinical reasoning
  modifier boundaries (e.g. EEG psychogenic confirmation). The component is classified
  as near ceiling, unblocking Pair 4 (investigation + comorbidity) interaction tests.
  Report: `docs/experiments/exect/exect_investigation_isolated_ceiling_e12_20260529.md`.
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
- **G9 routed the next Gan pull to candidate inventory.** The no-model G8
  failure inspection found 13 standard-50 paper-monthly misses: 4
  candidate-coverage exact misses, 3 seizure-free-over-quantified target
  selection failures, 3 unknown-policy target selection failures, and 3
  quantified target-selection/temporal-anchoring failures. All four named
  exact-miss standard-50 records (`gan_15997`, `gan_16772`, `gan_16825`,
  `gan_16335`) lack the exact gold label in the current candidate inventory,
  which routed G11 before G10. Report:
  `docs/experiments/gan/gan_s0_g9_exact_miss_failure_inspection_20260529.md`.
- **G11 completed the candidate-inventory challenge-set pass.** The locked G6
  `gan_s0_g6_candidate_coverage_exact_miss` challenge set remains 0/21 exact,
  14/21 Purist-equivalent, and 17/21 Pragmatic-equivalent. Compared with the
  stored G1 substrate, 20 rows changed because the current runtime prunes broad
  abstention options when concrete frequency candidates are present. The four
  G9 standard50 exact-miss records are still 0/4 exact but 4/4
  Purist/Pragmatic-equivalent. This does not mean the raw candidate builder
  must emit aggregate labels that never appear verbatim in the note. It means
  G10 needs an aggregation-aware answer-option surface, or a narrower
  category-level selector claim. Report:
  `docs/experiments/gan/gan_s0_g11_candidate_inventory_challenge_set_pass_20260529.md`.
- **G18 source-level abstention candidate gating is complete.** The current G11
  report and a full validation recompute show 0 rows where standalone
  `unknown` or `no seizure frequency reference` appear beside concrete
  frequency candidates. The focused temporal-candidate regression
  `test_temporal_candidates_drop_abstention_options_when_frequency_candidates_exist`
  passes. Treat the old G1 abstention-heavy labels as provenance, not the
  active candidate surface. Abstention-only `unknown` versus
  `no seizure frequency reference` cases are routed to G13.
- **G13 completed the isolated frequency-content gate report.** The no-model
  gate over the current deterministic temporal candidate substrate reaches
  244/299 validation accuracy (81.6%). Quantified-frequency presence is
  high-recall at 201/203 (99.0%), and no-reference predictions are precise
  (10/10), but unclear-frequency recall is 10/40 (25.0%) and seizure-free
  recall is 23/45 (51.1%). The main source-level errors are unknown or
  seizure-free gold rows routed to quantified-frequency presence, so temporal
  anchoring and selector analyses must account for gate errors before
  attributing misses to those stages. Report:
  `docs/experiments/gan/gan_s0_g13_frequency_content_gate_report_20260529.md`.
- **G14 completed the temporal anchoring diagnostic pass.** The no-model report
  over current deterministic temporal candidates found 41/50 standard50 exact
  candidate coverage and 36/40 temporal-slot coverage on temporally applicable
  rows. On `gan_s0_g6_temporal_anchoring`, exact and slot coverage are 13/15;
  `gan_16772` and `gan_16825` are true temporal-slot misses, while standard50
  gate-confused rows remain G13 upstream caveats. The decision is not to expand
  fragile arithmetic or broad relative-anchor guards from this pass; route
  remaining exact misses to aggregation-aware answer construction before another
  target-selection claim.
  Report:
  `docs/experiments/gan/gan_s0_g14_temporal_anchoring_report_20260529.md`.
- **G12 completed the answer-option routing decision.** On the locked G6
  exact-miss challenge set, raw options remain 0/21 exact, 14/21
  Purist-equivalent, and 17/21 Pragmatic-equivalent. The current constructed
  aggregate subset is still 0/21 exact, with 11/21 Purist-equivalent and 13/21
  Pragmatic-equivalent coverage. Therefore G10 was allowed to proceed only as a
  category-level/candidate-ranking selector comparison; exact closed answer
  options now require G16 aggregation policy, or a separate deterministic
  aggregation constructor with fixture tests informed by G14. G10 has
  since completed and been rejected as tested. Report:
  `docs/experiments/gan/gan_s0_g12_answer_option_surface_20260529.md`.
- **G10 completed the narrowed category-ranking selector arm.** The model-backed
  run on `gan_s0_g6_standard50_v1` preserved the fixed scorer, loader, split,
  bridge, candidate builder, label-construction, and prediction-repair controls.
  Category decisions and candidate rankings were present in 50/50 predictions,
  but the arm reached only 36/50 paper monthly and 70.0% canonical monthly,
  below builder-gap GPT (41/50), D1 v1.2b (40/50), and G8 (37/50) on the same
  records. The unknown/no-reference overlay fell to 4/10. Do not full-validate
  or promote this arm; exact closed answer-option construction remains blocked
  on G16 or a separate deterministic aggregation constructor informed by G14.
  Report:
  `docs/experiments/gan/gan_s0_g10_candidate_ranking_target_selector_report_20260529.md`.
- **G15 completed the support-aware target selector arm and rejected it as
  tested.** The model-backed run on `gan_s0_g6_standard50_v1` preserved scorer,
  loader, split, benchmark bridge, candidate-builder, label-construction, and
  prediction-repair controls. Support context was present in 50/50 predictions,
  with selected-candidate references and label-construction inputs present in
  49/50, but the arm reached only 31/50 paper monthly and 60.0% canonical
  monthly. It regressed against builder-gap GPT, D1 v1.2b, G8, and G10 on the
  motivating target-selection and seizure-free-versus-quantified overlays, and
  scored 5/10 on unknown/no-reference. Do not full-validate or promote this
  arm; pull G16 aggregation policy or a separately preregistered deterministic
  aggregation constructor before another exact-label claim.
  Report:
  `docs/experiments/gan/gan_s0_g15_support_aware_target_selector_report_20260529.md`.
- **G20 preregistered the aggregation-constructor path.** The design chooses a
  deterministic, fixture-first quantified-rate constructor rather than a
  model-mediated first pass or deferral. It names the four G19 standard50
  aggregation rows, the 21 G11 exact-miss challenge fixtures, permitted
  transformations, forbidden repairs, expected coverage gates, and scorer
  caveats. It does not implement the constructor or make a performance claim.
  Report:
  `docs/experiments/gan/gan_s0_g20_aggregation_constructor_preregistration_20260529.md`.
- **G21 implemented the quantified-rate aggregation constructor.** The new
  `gan.frequency.aggregation_constructor.v1` primitive emits separate
  constructed answer options for G16-eligible quantified-rate rows and preserves
  raw temporal candidates unchanged. Standard50 exact option coverage rises from
  41/50 raw to 45/50 combined; the G11 exact-miss challenge reaches 11/21
  constructed exact, passing the 10/14 quantified-rate fixture gate, with 0
  constructions for deferred duration, inventory-gap, or outside-policy rows.
  This is answer-option coverage only, not selector performance. Report:
  `docs/experiments/gan/gan_s0_g21_aggregation_constructor_report_20260529.md`.
- **G17 completed the special-label policy separation.** The G19 special-label
  slice is now a nine-row policy surface, not a binary string distinction:
  `gan_6532`, `gan_9566`, `gan_5974`, `gan_6607`, `gan_6387`, `gan_14002`,
  `gan_11380`, `gan_7894`, and `gan_8264`. It separates unclear-frequency
  misroutes, unknown-cluster policy, unknown-over-concrete, and seizure-free/no-
  reference scorer-mode discordance. It made no scorer, loader, split, bridge,
  prompt, model, candidate-builder, target-selection, or prediction-repair
  changes, and found 0 deterministic repair candidates. Report:
  `docs/experiments/gan/gan_s0_g17_unknown_no_reference_policy_20260529.md`.
- **Gan S0 now has a plain-English component handoff.** The key-axes progress
  report translates the decomposition into reader-facing components:
  frequency-content gate, candidate inventory, temporal anchoring, target
  selection, label construction, aggregation, unknown/no-reference policy, and
  evidence/schema checks. The practical summary is that current systems are
  strong at finding possible answers and reasonably good at formatting a chosen
  answer, while the open bottleneck is choosing the right answer when a note
  contains competing signals. Report:
  `docs/experiments/gan/gan_s0_key_axes_progress_report_20260528.md`.
- **X2 preregistered ExECT pairwise interaction tests.** The plan defines
  validation-split support counts, hypotheses, primary family metrics,
  interference criteria, and stop rules for diagnosis+seizure type,
  seizure type+frequency, medication+temporality, investigation+comorbidity,
  and secondary pairs. Medication+temporality is active as a diagnostic-input
  pair where temporality is unscored and annotated medication F1 is the scored
  endpoint. Holdout remains residual-audit only. Plan:
  `docs/experiments/exect/exect_pairwise_interaction_plan_x2_20260529.md`.
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
- G9 completed the required no-model gate before G10/G11 and routed the next
  Gan pull to candidate inventory.
- G11 completed the candidate-inventory exact-miss pass and found that raw
  inventory labels are not sufficient as exact answer options for aggregation
  cases.
- G18 completed the source-level cleanup before selector work: broad abstention
  candidates are no longer active universal answer options when concrete
  frequency evidence is already represented. Older G1 rows document the
  pre-pruning surface; G11 current rows document the active surface.
- G10 completed the narrowed category-level/candidate-ranking claim authorized
  by G12 and was rejected as tested. G21 now supplies the first deterministic
  quantified-rate constructed-option surface, but target selection remains a
  separate card.
- G12 did not mutate scorer, loader, split, benchmark bridge, prompt, model, or
  prediction-repair semantics.
- G13 established the baseline for the frequency-content gate. G15 carried
  G13's false-positive and false-negative rows as caveats, but the support-aware
  selector still regressed as a prompt/interface arm.
- G14 established the temporal anchoring diagnostic baseline. G15 carried
  `gan_16772` and `gan_16825` as temporal-slot upstream caveats rather than
  treating those exact misses as pure selector failures.
- G15 completed the support-aware selector authorized by G12/G13/G14 and is
  rejected as tested. It is evidence that support metadata alone is not enough,
  not closure of target selection as a mechanism class.
- G16 completed the rate/duration aggregation policy pass. The no-model policy
  report leaves scorer, loader, split, bridge, prompt, model,
  candidate-builder, target-selection, and prediction-repair semantics
  unchanged. On the G11 exact-miss challenge, 14/21 rows need quantified rate
  aggregation with missing temporal slots, 2/21 need seizure-free duration
  policy, 4/21 are candidate-inventory gaps, and 1/21 is outside rate/duration
  policy. On standard50, 41/50 already have exact options, 4/50 are quantified
  rate aggregation blocks, and 5/50 are outside rate/duration policy. Exact
  closed-answer selector claims remain blocked until a deterministic constructor
  or preregistered model mechanism is tested. Report:
  `docs/experiments/gan/gan_s0_g16_aggregation_policy_20260529.md`.
- G19 completed the post-G16 error attribution audit with no model, scorer,
  loader, split, bridge, prompt, candidate-builder, target-selection, or
  prediction-repair changes. On `gan_s0_g6_standard50_v1`, builder-gap GPT,
  D1 v1.2b, G8, G10, and G15 produce 65 paper-monthly arm-misses across 29
  unique rows. The largest classes are aggregation blocks with missing temporal
  slots (16 arm-misses / 4 rows), unclear or unknown-cluster evidence misrouted
  as concrete (15 / 6), seizure-free over quantified target selection (11 / 6),
  and wrong quantified rate/window selection (11 / 5). There are 0 deterministic
  repair candidates and 0 schema/evidence residuals on this surface. Report:
  `docs/experiments/gan/gan_s0_g19_post_g16_error_attribution_audit_20260529.md`.
- G17 completed unknown vs. no-reference policy separation downstream of the
  completed G15 negative arm, G16 special-class routing, and the G19
  special-label slice. Future special-label selector work needs a new mechanism
  card and a before/after ledger for the nine G17 rows.
- G20 completed the aggregation-constructor preregistration downstream of G19,
  G14, and G16. G21 completed the scoped quantified-rate constructor and passed
  the fixture gates; target selection remains separate.
- The Gan key-axes progress report is the handoff reference for plain-English
  component names. Use it to keep G8 interpretation centered on the actual
  failure stage rather than on implementation jargon.
- G5 is complete and should be used for synthetic-only paper-facing Gan tables.
  Its scorer-mode forensics note is G4 follow-up input; it does not unblock Gan
  real-note reporting.
- E11 completed the primary holdout residual attribution. Treat it as a router
  for validation-only follow-ups; do not tune prompts, scorers, loaders,
  bridges, repairs, or splits from holdout rows.
- X2 completed the pairwise interaction preregistration. Use it for support
  counts, hypotheses, metrics, interference criteria, and stop rules before
  drafting diagnosis+seizure type, seizure type+frequency,
  investigation+comorbidity, medication+frequency, or medication+temporality
  follow-ups. Do not use S1-S4 ladder comparisons as pairwise evidence; each
  follow-up needs target-component-alone versus target-plus-paired-component
  arms.
- B1 stays blocked until isolated component ceilings and pairwise interaction
  evidence exist. Substrates alone are not enough to rebuild optimized stacks.

## Parallelization Opportunities

- **Safe now:** draft a new validation-only ExECT mechanism card from E11
  findings before any model calls, or do readme/report cleanup tied to completed
  Gan artifacts. Any
  downstream Gan selector/adjudicator run must use the G6 evaluation-surface
  protocol, cite the G19/G17 failure class it targets, use the G21 constructed
  option surface only if its scope matches, and preserve scorer, loader, split,
  benchmark bridge, candidate-builder, and prediction-repair semantics.
- **Architecture lane closed as bottleneck:** C31/C32 closed the currently
  scoped active-priority pruning pass. Any new cleanup should start from a
  concrete runtime contract or active-authority ambiguity, not from historical
  card carryover.
- **Single-threaded or carefully sequenced:** future registry/archive
  regeneration, and any change to scorer, loader, split, benchmark bridge, or
  shared primitive contracts. ExECT component-ceiling work remains
  sequencing-sensitive where it changes S5, S0/S1, or active runtime contracts.
- **Blocked together:** B1 waits on ExECT component ceilings.
- **Model-call gated:** E3/E4 audits are complete, so any related model run now
  needs a preregistered comparison against the full-note/current-stack baseline.
  G10 and G15 selector lanes are complete and rejected as tested. Any new Gan
  selector/adjudicator lane needs to cite the completed G19 failure class plus a
  new preregistered mechanism card, and any full-validation run should wait
  until the standard-50 mechanism has cleared its stop rule.

## Recommended Next Pull

1. Draft the ExECT validation-only mechanism card from E11 for S1
   transfer, frequency payload robustness/adjudication, or medication payload
   routing, using X2 for pairwise support counts and stop rules. Holdout rows
   remain residual evidence only.
2. Reopen Gan target selection only with a new mechanism card that explicitly
   accounts for G19's failure classes, G17's special-label strata, G15's
   support-aware regression, and the G21 constructed-option surface. The next
   target-selection card should preserve a row-level before/after ledger rather
   than rerunning the G8/G10/G15 prompt shapes.
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
- New Gan experiments must cite the G19 failure class they intend to reduce and
  preserve a row-level before/after ledger for that class.
- Prefer typed payloads, primitives, bridges, and scorer policies over prompt
  bloat and broad mode flags.
