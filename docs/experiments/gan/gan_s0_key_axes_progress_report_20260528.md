# Gan S0 Key Axes Progress Report

Date: 2026-05-28
Status: current synthesis
Follows: `docs/experiments/gan/gan_s0_pipeline_decomposition_deep_dive_20260528.md`

## Purpose

This report summarizes the progress made after the Gan S0 pipeline-decomposition
deep dive. It documents where the work stood at the pivot, what changed across
the G1-G7 follow-up sequence, why those changes mattered, what we learned, and
what should happen next.

No new model calls, scorer changes, loader changes, split changes, benchmark
bridge changes, prompt edits, or prediction repairs were made for this report.
It synthesizes existing reports and artifacts.

## Executive Summary

The deep dive reframed Gan S0 as a component-decomposition problem rather than a
generic prompt-improvement loop. Since then, the project has made real progress
on the key axes, but it has not solved the selector or promoted an isolated
ceiling.

The biggest advance is that the problem is now much better localized. Candidate
inventory is strong enough to stop treating coverage as the default bottleneck:
the deterministic substrate emits candidates for 299/299 validation records,
exact-covers 278/299 gold labels, and has Purist/Pragmatic-equivalent coverage
of 292/299 and 295/299. The G2 split then showed that, if target selection were
perfect over the existing candidates, the task can reach 93.3% paper monthly and
94.0% canonical monthly on the full synthetic validation split.

The main remaining failure mode is target semantics: choosing the benchmark
target from competing current quantified, seizure-free, unknown, no-reference,
cluster, and temporal candidates. G4 proved that traceability fields can be
preserved, but the tested explicit reason-code adjudicator regressed to 80.0%
on the old 25-record slice because it selected seizure-free candidates over
gold-compatible quantified candidates. G5 then sharpened the same lesson from a
scorer angle: D1's paper-scorer loss is concentrated in seizure-free gold labels
predicted as `no seizure frequency reference`.

The work has also hardened the evaluation protocol. The old 25-record enriched
slice is now smoke-only. G6 defines `gan_s0_g6_standard50_v1` as the default
mechanism-comparison surface and names targeted challenge sets. G7 preregisters
the next selector: a special-class target-selection arm that changes only target
policy, preserves trace fields, and reports both paper and canonical scorer
views before any full-validation or promotion claim.

## Plain-English Component Map

The decomposition can be read as a sequence of smaller questions. The point is
not to make the system more complicated for its own sake. The point is to stop
asking one model call to find every possible clue, understand time, choose the
right clinical meaning, format the benchmark label, and explain itself all at
once.

| Component | Plain-English meaning | Current best implementation | Example of how it works | What we are still evaluating |
| --- | --- | --- | --- | --- |
| Frequency-content gate | Decide whether the note says anything useful about seizure frequency at all. | Not fully isolated yet. This is mostly handled inside the current candidate builder plus the final adjudicator. | A letter that only discusses medication refills should become `no seizure frequency reference`; a letter saying seizures continue but frequency is unclear should become `unknown`. | How to reliably separate no mention, unclear seizure frequency, and seizure-free status. |
| Candidate inventory | List every possible frequency answer the note might support before choosing one. | Deterministic D1/builder candidate generation. It emits candidates for 299/299 validation records and exact-covers 278/299 gold labels. | If a note says "two seizures in six months" and also "none since March," the system lists both a rate candidate and a seizure-free candidate instead of choosing too early. | The exact-miss cases, especially unusual rates, seizure-free conflicts, and unknown-cluster labels. |
| Temporal anchoring | Work out what time window a frequency belongs to. | D1 v1.2b schema-guard-only date/event payload. It exposes dates and time clues but avoids risky automatic arithmetic. | "Three seizures since January" means something different if the clinic letter is from April versus December. | Whether narrow, seizure-specific date math can help without adding false candidates. Broad arithmetic hurt performance. |
| Target selection | Choose the one candidate that should become the benchmark answer. | Candidate-constrained selection is the best signal so far. G2 showed a high ceiling, but G4's explicit reason-code selector failed as tested. | If the note says "previously weekly, now seizure-free for six months," the selector must decide whether the benchmark answer is the current seizure-free duration or the older weekly rate. | This is the main live bottleneck, especially current quantified frequency versus seizure-free duration. |
| Label construction | Turn the chosen candidate into the exact Gan label format. | Deterministic constructor over selected candidates. G2 constructed 1605/1605 candidate labels with no invalid candidates. | A chosen candidate with numerator `2`, denominator `3`, and unit `month` becomes `2 per 3 month`. | Mostly watching for failures when future selector or candidate changes introduce harder cluster, range, or aggregation cases. |
| Aggregation | Decide whether several mentions should be combined, ranked, or kept separate. | Partly handled by the candidate builder and final adjudicator; not cleanly isolated yet. | "1 focal seizure per month and 2 absence seizures per month" may need a different policy than "weekly last year, monthly now." | When to add rates, when to choose the highest current rate, and when different time windows make aggregation invalid. |
| Unknown versus no-reference policy | Decide whether seizures are mentioned but frequency is unclear, versus there being no seizure-frequency information. | Current best approach is to keep scorer views separate and route the distinction into the next G7 selector. No blind rewrite between special labels. | "Ongoing seizures, unclear how often" is `unknown`; "no seizure discussion in the letter" is `no seizure frequency reference`. | Special-class semantics, especially because the paper scorer and clinical diagnostic scorer treat some labels differently. |
| Evidence and schema checks | Make sure the answer is well-formed and tied back to text in the note. | Diagnostic trace fields and guards. G4 preserved selected-candidate references and construction inputs in 25/25 records. | The report should show which note text supported `2 per 3 month`, which candidate was selected, and how the final label was built. | Traceability is necessary but not enough: G4 showed complete trace fields can still accompany the wrong target choice. |

The short version is: we are now good at finding possible answers, reasonably
good at formatting a chosen answer, and still weakest at choosing the right
answer when a note contains competing signals. The next selector work is aimed
directly at that choice.

## Where We Were At The Deep Dive

The deep dive concluded that the original six-stage framing was directionally
right but too event-centric and too linear. The corrected decomposition was:

1. frequency-content gate;
2. candidate inventory;
3. temporal anchoring;
4. scope and benchmark target selection;
5. canonical label construction and aggregation;
6. unknown versus no-reference policy;
7. evidence and schema validation.

At that point, the strongest operational anchor was builder-gap v1 GPT at 80.6%
canonical monthly on synthetic validation. D1 v1.2b was close at 79.9% canonical
monthly and more scientifically useful as a mechanism baseline because it
exposed structured date/event/candidate payloads.

The deep dive also identified a serious bundling problem. Even D1 still left
target selection, label construction, aggregation, unknown/no-reference policy,
and most certainty decisions inside one final LLM adjudicator call. The next
scientific value was therefore not another broad prompt pass, but component
splits that could say which stage was failing.

## Progress By Axis

| Axis | Where we were | What changed | What we learned | Current status |
| --- | --- | --- | --- | --- |
| Baseline and benchmark surface | Builder-gap GPT was the synthetic operational default under canonical project metrics; paper-scorer compatibility was newly recognized as primary for Gan-paper comparisons. | G5 rescored builder-gap GPT, builder-gap Qwen, and D1 v1.2b with `gan2026_paper_reproduction`. | Builder-gap GPT remains strongest for synthetic paper-facing tables at 79.9% paper monthly. D1 remains the mechanism baseline at 76.6% paper monthly / 79.9% canonical monthly. | Paper-comparison surface exists for synthetic validation; external Real(300)/Real(150) claims remain blocked. |
| Candidate inventory | The deep dive suspected deterministic candidates were useful but had not isolated full-validation coverage. | G1 measured the deterministic D1/builder substrate against all 299 validation gold labels. | Coverage is strong: 299/299 records have candidates; exact coverage is 278/299; Purist-equivalent coverage is 292/299; Pragmatic-equivalent coverage is 295/299. Exact misses concentrate in quantified-rate, seizure-free, and unknown-cluster patterns. | Coverage gate measured; mechanism open. Do not change the builder casually. |
| Temporal anchoring | R11/R15 had shown D1 date/event structure was useful, but arithmetic and broad guardrails were risky. | D1 v1.2b schema-guard-only was accepted as the mechanism baseline; arithmetic injection and broad relative-anchor guardrails were discarded. | The useful temporal move is structured evidence exposure, not broad date math. Arithmetic should stay diagnostic until a seizure-specific parser exists. | Mechanism open; D1 v1.2b is the active temporal/candidate mechanism baseline. |
| Target selection | The deep dive named current benchmark target selection as the core unresolved stage. | G2 split selection from construction. G2 model arms showed candidate-constrained and seeded-selector slices at 92.0% monthly versus free adjudication at 16.0%. G4 then tested explicit reason-code adjudication. | Constraining the model to candidates helps massively on the enriched slice, but the explicit reason-code G4 arm failed as tested because it chose seizure-free over quantified candidates in five records. | Model-arm slice measured; mechanism open. G4 is a rejected arm, not a rejected mechanism. |
| Label construction and aggregation | Label emission was bundled with target choice, so construction failures were hard to separate from selection failures. | G2 implemented a deterministic label-construction surface over selected candidates. G4 preserved construction inputs and final labels separately. | Construction is not the current bottleneck on these artifacts: G2 constructed 1605/1605 candidate records with 0 invalid candidates, and G4 had no deterministic-construction mismatches. | Constructor surface implemented; keep reporting construction separately from target selection. |
| Unknown/no-reference and special labels | The deep dive warned that `unknown`, `no seizure frequency reference`, and seizure-free labels were being collapsed by broad certainty language and by some scorer views. | G3 probed policy rules on the G2 seeded-selector slice. G5 scorer-mode forensics isolated special-class scorer divergence. G7 now preregisters a special-class selector. | Broad post-hoc policy rules are fragile: G3 changed one record, produced no monthly gain, and reduced pragmatic accuracy by 4pp. The more important issue is special-class target semantics, especially seizure-free duration versus no-reference and quantified-current-frequency conflicts. | Mechanism open; next arm should target special-class selection, not blind deterministic repair. |
| Evidence and schema validation | Evidence/schema checks were necessary but not sufficient, and broad verifier/repair had been neutral or harmful. | G4 demonstrated complete traceability on selected candidate references and construction inputs. G5/G6 require scorer-discordance and trace fields in follow-up reports. | High traceability can coexist with wrong target selection. Evidence/schema fields are useful guards and diagnostics, not proof that the semantic target is correct. | Diagnostic only; preserve trace completeness but do not promote based on it alone. |
| Evaluation surface | The old 25-record enriched slice was useful for fast diagnosis but too denominator-sensitive for promotion. | G6 created `gan_s0_g6_standard50_v1`, retained the old slice as `gan_s0_g6_traceability_smoke_25`, and named challenge sets. | One record is 4.0pp on the old slice and 2.0pp on standard50. A policy-rich standard 50 gives a better mechanism gate while still requiring full validation for promotion. | Operational decision protocol complete. G8 should use G6 surfaces. |
| Non-targeted mechanisms | Entity-first extraction, self-consistency, and optimizer work were tempting broad alternatives. | R12 rejected the entity-first C1 arm. R13 rejected/held self-consistency for Gan S0. R14 kept Qwen GEPA blocked pending a compact hosted-model gate. | More stages or more compute do not automatically decompose the right thing. Context-preserving deterministic candidates are useful; entity-first context stripping, repeated sampling, and instruction bloat are not current high-value routes. | Rejected arms or blocked optimizer path; do not rerun without a new hypothesis. |

## What Changed And Why

### G1 converted candidate inventory from belief to measured substrate

Before G1, candidate coverage was inferred from successful programs and error
analysis. G1 made it explicit with a no-model coverage report over the full
synthetic validation split.

This mattered because it separated "the system did not find the right
frequency-bearing content" from "the system found plausible candidates but chose
or constructed the wrong benchmark label." The high candidate count distribution
also matters: 245/299 records have four or more candidates. Gan S0 is therefore
not usually a sparse retrieval problem. It is often an arbitration problem.

### G2 split target selection from label construction

G2 turned the deep dive's proposed split into an executable scaffold. The
candidate-constrained oracle reached 93.3% monthly under the paper scorer and
94.0% under the canonical scorer. The deterministic constructor handled all
1605 candidate records without invalid outputs.

This changed the interpretation of the ceiling. The existing candidate substrate
contains enough signal to support performance well above the current promoted
synthetic baseline, but only if the selector chooses the benchmark-relevant
candidate. That makes target selection the next high-value model-backed stage.

### G2 model arms showed the selector interface matters

On the enriched 25-record slice, free full-note adjudication scored 16.0%
monthly, while candidate-constrained and seeded reason-code/answer-options arms
both reached 92.0% monthly. The seeded surrogate reached 100.0% pragmatic.

This was not a promotion claim because the slice is diagnostic. But it strongly
supported the mechanism hypothesis that constrained target selection can recover
errors hidden inside broad one-shot adjudication.

### G3 showed broad special-label rules are not enough

G3 applied unknown/no-reference, weak-rate-to-unknown, and seizure-free conflict
rules to the G2 seeded-selector slice. It produced no monthly gain and reduced
Pragmatic accuracy by 4.0pp after changing one record from a rate to `unknown`.

That result does not close special-label work. It says the next policy should
not be a broad post-hoc rule bundle. The distinction must be made inside
target-selection semantics, with evidence and candidate context still visible.

### G4 proved traceability, but rejected the tested adjudicator arm

G4 added the trace fields the deep dive wanted: explicit reason code, selected
candidate reference, and label-construction inputs. Those fields were present
in 25/25 records, and there were no unsupported selected-candidate cases or
construction mismatches.

But performance fell to 80.0% monthly/pragmatic on the old enriched slice. All
five misses were target-selection failures with policy signals, mostly choosing
seizure-free candidates over gold-compatible quantified candidates. This is a
valuable negative result: the report can now say the failure is not evidence,
schema, or construction. It is target semantics.

### G5 put scorer alignment on a firmer footing

G5 made `gan2026_paper_reproduction` available for synthetic paper-facing
tables. It rescored stored predictions without new model calls:

| Baseline | Paper monthly | Canonical monthly | Interpretation |
| --- | ---: | ---: | --- |
| Builder-gap v1 GPT | 79.9% | 80.6% | Synthetic paper-default baseline remains strongest. |
| Builder-gap v1 Qwen | 70.2% | 70.7% | Accepted local transfer, not hosted parity. |
| D1 v1.2b schema guard GPT | 76.6% | 79.9% | Best mechanism baseline, but paper scorer exposes special-class loss. |

The scorer-mode forensics were more important than the aggregate table. D1 had
14 canonical-only-correct records, all seizure-free gold labels predicted as
`no seizure frequency reference`. The canonical scorer treats both as 0/month,
but the paper scorer preserves their benchmark-facing special-class difference.

This is exactly the kind of issue the next selector must expose instead of
hiding inside a final label.

### G6 fixed the evaluation surface

G6 responded to the denominator problem in G2/G4. The old enriched 25-record
slice is now `gan_s0_g6_traceability_smoke_25` and cannot promote a new arm.
The default mechanism comparison surface is now `gan_s0_g6_standard50_v1`,
with named challenge overlays for target selection, seizure-free versus
quantified policy, unknown/no-reference policy, candidate coverage exact misses,
cluster policy, and temporal anchoring.

This is progress in research discipline, not performance. It prevents a one- or
two-record slice swing from steering the next mechanism claim.

### G7 preregistered the next selector instead of launching another broad run

G7 narrows the next model-backed arm to one varied component:
`target_selection_policy`. It fixes candidate inventory, temporal anchoring,
label construction, scorer semantics, dataset loading, split definitions,
evidence diagnostics, and prediction repair.

The planned selector must emit target semantic class, selected candidate index,
selected evidence, reason code, construction inputs, final benchmark-facing
label, and scorer-discordance flags. This is the direct successor to the deep
dive's recommendation to separate target choice from label construction and
special-label policy.

## What We Have Learned

1. Candidate inventory is no longer the default bottleneck.

   The deterministic substrate is high recall on the full validation split. It
   still has exact misses, but most near-term gains should come from selection
   and policy rather than another broad builder pass.

2. Target selection is the live bottleneck.

   G2 showed the ceiling available when candidates are selected correctly. G4
   showed the main failure when a selector is made traceable but still chooses
   the wrong special class. The dominant question is now: which current
   benchmark target should win when quantified rates, seizure-free statements,
   clusters, vague cues, unknowns, and no-reference candidates compete?

3. Label construction is more tractable than target choice.

   The deterministic constructor validated every candidate record in G2, and
   G4 did not fail through construction mismatches. This does not mean
   construction is solved for all future candidate changes, but it is not the
   current limiting component under the existing substrate.

4. The canonical scorer is clinically useful but too forgiving for some paper
   target semantics.

   The D1 seizure-free versus no-reference pattern shows why every future Gan
   report needs both scorer views. `gan2026_paper_reproduction` should lead
   paper-facing tables, while `gan_frequency_deterministic_v1` remains a
   diagnostic view for clinical monthly-frequency analysis.

5. Traceability is necessary, not sufficient.

   G4's trace fields worked, but the arm underperformed. The next selector must
   use traceability to expose the semantic decision, not treat trace presence as
   evidence of correctness.

6. More decomposition is only useful when it preserves the right context.

   D1 deterministic date/event payloads help. LLM-only date/event stages,
   entity-first context stripping, broad arithmetic injection, broad anchor
   guardrails, self-consistency, and GEPA instruction bloat have not helped as
   tested. The decomposition should stay component-specific and benchmark-aware.

## Current State Of The Key Axes

| Component | Current classification | Best evidence | Next action |
| --- | --- | --- | --- |
| Paper-comparison surface | synthetic paper-scorer surface available / external benchmark claim blocked | G5 rescore pack | Use G5 for synthetic-only paper-facing tables; do not claim Real(300)/Real(150) reproduction. |
| Evaluation surface | operational decision protocol | G6 standard50 and challenge sets | Use G6 for G8 and later selector/adjudicator comparisons. |
| Synthetic operational default | promoted baseline | Builder-gap v1 GPT, 79.9% paper monthly / 80.6% canonical monthly | Keep as paper-default until full-validation replacement. |
| Mechanism baseline | operational default | D1 v1.2b, 76.6% paper monthly / 79.9% canonical monthly | Use for mechanism experiments because it exposes the structured payload. |
| Candidate inventory | coverage gate measured / mechanism open | G1 299/299 any candidate; 278/299 exact | Use exact-miss challenge set before changing candidate builders. |
| Temporal anchoring | mechanism open | R11/R15 D1 decisions | Keep arithmetic diagnostic-only until a seizure-specific parser exists. |
| Target selection | model-arm slice measured / mechanism open | G2 92.0% slice arms; G4 80.0% rejected arm | Execute G8 under G7 protocol. |
| Label construction | constructor surface implemented / mechanism open | G2 1605/1605 constructed; G4 no construction mismatches | Keep separated in reports; do not retune unless construction errors appear. |
| Unknown/no-reference policy | mechanism open | G3 negative policy probe; G5 special-class forensics | Treat as target semantics, not blind repair. |
| Evidence/schema | diagnostic only | G4 complete trace fields despite target failures | Keep as gates and diagnostics. |

## What Comes Next

The next pull is G8: execute the G7 special-class target selector under the
G6 evaluation protocol.

The minimum useful sequence is:

1. Run the G7 selector on `gan_s0_g6_traceability_smoke_25` only to check schema,
   trace fields, selected-candidate references, construction inputs, final-label
   linkage, and both scorer views.
2. If smoke passes, run `gan_s0_g6_standard50_v1` as the default mechanism
   comparison.
3. Report paper monthly/Purist/Pragmatic as benchmark-facing and canonical
   monthly/Purist/Pragmatic as diagnostic sensitivity.
4. Include challenge overlays for target selection, seizure-free versus
   quantified, and unknown/no-reference. Include cluster only if the arm touches
   cluster policy.
5. Preserve error classes for candidate coverage, target selection, label
   construction, unknown/no-reference policy, seizure-free policy, cluster
   policy, temporal anchoring, evidence support, and schema validity.
6. Do not full-validate unless standard50 shows at least a two-record monthly
   lift over the relevant comparator, no paper-scorer regression, and no
   regression on the motivating challenge set.

The next work should not:

- change scorer semantics;
- use `reference[0]` as gold;
- repair special-class labels deterministically without reading the note;
- treat the old 25-record slice as a promotion surface;
- change candidate builders before reporting the G6 exact-miss challenge set;
- run another broad prompt, unknown guard, entity-first stage graph,
  self-consistency arm, or optimizer pass without a new preregistered mechanism.

## Source Artifacts Used

- `docs/experiments/gan/gan_s0_pipeline_decomposition_deep_dive_20260528.md`
- `docs/experiments/gan/gan_s0_candidate_inventory_coverage_report_20260528.md`
- `docs/experiments/gan/gan_s0_target_label_split_g2_report_20260528.md`
- `docs/experiments/gan/gan_s0_g2_model_arm_comparison_20260528.md`
- `docs/experiments/gan/gan_s0_g3_policy_probe_report.md`
- `docs/experiments/gan/gan_s0_g4_explicit_reason_code_adjudicator_report_20260528.md`
- `docs/experiments/gan/gan_s0_g5_paper_scorer_rescore_pack_20260528.md`
- `docs/experiments/gan/gan_s0_g5_scorer_mode_forensics_for_g4_20260528.md`
- `docs/experiments/gan/gan_s0_g6_evaluation_slice_standard_decision_20260528.md`
- `docs/experiments/gan/gan_s0_g7_special_class_target_selector_preregistration_20260528.md`
- `docs/experiments/gan/gan_s0_r11_temporal_date_stage_decision_20260528.md`
- `docs/experiments/gan/gan_s0_r12_clines_entity_first_pipeline_gate_decision_20260528.md`
- `docs/experiments/gan/gan_s0_r13_self_consistency_variance_probe_decision_20260528.md`
- `docs/experiments/gan/gan_s0_r14_gepa_failure_postmortem_qwen_gate_design_20260528.md`
- `docs/experiments/gan/gan_s0_r15_d1_guardrail_ablation_decision_20260528.md`
- `docs/experiments/gan/README.md`
- `docs/component_ceiling_registry.md`
- `docs/planning/kanban_plan.md`
- `docs/current_research_program.md`
- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md`

## Claim Boundaries

- This is a synthetic-validation synthesis, not a Real(300), Real(150), or
  published Gan benchmark reproduction claim.
- No row here promotes an isolated component ceiling. The component registry
  remains the authority for status.
- G4 is rejected as an arm, not as a mechanism class.
- G7 is a preregistration, not a result.
- Holdout or real-note reporting remains blocked unless a separate protocol
  explicitly authorizes it.
