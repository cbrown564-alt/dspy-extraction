# Gan S0 Pipeline Decomposition Deep Dive

Date: 2026-05-28

Status: research synthesis and ablation planning note

Scope: Gan seizure-frequency S0 only. This note builds on
`docs/experiments/synthesis/experimentation_retrospective_report.md` and interprets the later Gan
R11/R12/R13/R15 experiments.

The original synthesis did not change code, scorer semantics, or experiment configs. The
benchmark-alignment addendum below records the later scorer-policy update separately.

Update: the benchmark-alignment policy changed later on 2026-05-28 after reviewing the
author-provided Gan evaluator received on 2026-05-27. Direct Gan 2026 benchmark comparisons should
now lead with `gan2026_paper_reproduction`; `gan_frequency_deterministic_v1` remains a canonical
clinical diagnostic/sensitivity scorer.

## Sources Reviewed

Policy and framing:

- `docs/outline.md`
- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/datasets/gan/gan_scorer_comparison_report.md`
- `data/Gan (2026)/previous_paper_scorer/e_evaluation_synthetic_results.py`
- `data/Gan (2026)/previous_paper_scorer/z_step3_csv2json_and_get_freq.py`
- `data/Gan (2026)/Synthetic Clinical Letters for Seizure Frequency.pdf`, Section 2.6.1
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`
- `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md`
- `docs/experiments/synthesis/experimentation_retrospective_report.md`

Gan S0 experiment and error reports:

- `docs/experiments/gan/gan_s0_temporal_candidate_pivot_20260519.md`
- `docs/experiments/gan/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md`
- `docs/experiments/gan/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md`
- `docs/experiments/gan/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md`
- `docs/experiments/gan/gan_s0_exact_frequency_slot_payload_gpt_cap25_v1_inspection_20260521.md`
- `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_full_validation_rerun_inspection_20260523.md`
- `docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md`
- `docs/experiments/gan/gan_s0_pragmatic_monthly_divergence_analysis_20260524.md`
- `docs/experiments/gan/gan_s0_unknown_overuse_guard_cap25_gpt4_1_mini_rejection_20260524.md`
- `docs/experiments/gan/gan_s0_qwen35b_builder_gap_l2_error_forensics_20260525.md`
- `docs/experiments/gan/gan_s0_r9_recovery_and_exact_policy_summary_20260526.md`
- `docs/experiments/gan/gan_s0_r11_temporal_date_stage_decision_20260528.md`
- `docs/experiments/gan/gan_s0_r12_clines_entity_first_pipeline_gate_decision_20260528.md`
- `docs/experiments/gan/gan_s0_r13_self_consistency_variance_probe_decision_20260528.md`
- `docs/experiments/gan/gan_s0_r14_gepa_failure_postmortem_qwen_gate_design_20260528.md`
- `docs/experiments/gan/gan_s0_r15_d1_guardrail_ablation_decision_20260528.md`
- `docs/experiments/synthesis/test_holdout_evaluation_report_20260527.md`

Program and registry surfaces:

- `src/clinical_extraction/programs/gan_frequency_s0.py`
- `src/clinical_extraction/gan/temporal_candidates.py`
- `src/clinical_extraction/gan/temporal_events.py`
- `src/clinical_extraction/gan/frequency.py`
- `docs/experiments/synthesis/experiment_registry.json`
- `configs/experiments/gan_*.json`

## Question

The proposed decomposition was:

1. Identify all temporal events.
2. Resolve implicit date references.
3. Identify the valid event(s) to pay attention to.
4. Normalise the events to a standard form.
5. If there are multiple events, batch them together into one normalised form.
6. Determine whether there is sufficient certainty to assign a label, or abstain.

This note asks:

- Is that an accurate decomposition for Gan seizure frequency?
- How much of that work is still bundled inside the current program?
- Which experiments tested these components versus other components, and why?

## Short Answer

The proposed framing is directionally right, but it is too event-centric and too linear for the Gan
benchmark.

One additional correction matters for interpreting this whole note: "benchmark" should mean the
Gan paper's evaluator when the goal is like-for-like comparison. The current decomposition work
optimized mostly under `gan_frequency_deterministic_v1`, which is useful for clinical diagnostics
but not the primary comparison surface now that the author-provided evaluator is available.

The Gan S0 task is not simply "find all dated events, normalize them, then abstain if uncertain."
The benchmark is a single-label task whose gold label is `seizure_frequency_number[0]`, with
`reference[0]` useful as diagnostic evidence but not the scoring target. Many hard notes contain
multiple seizure mentions, seizure-free intervals, cluster descriptions, vague frequency language,
historical references, and unknown/no-reference boundary cases. The decisive problem is often not
whether a temporal event was found, but whether the system selected the benchmark-relevant current
frequency policy from competing mentions.

A cleaner decomposition is:

1. Frequency-content gate: decide whether the note contains seizure-frequency-relevant clinical
   content at all, separate from whether the answer is `unknown`.
2. Candidate inventory: enumerate all frequency-bearing candidates, including seizure events,
   seizure-free intervals, cluster/per-cluster structures, multi-type frequencies, vague frequency
   cues, and unknown cues.
3. Temporal anchoring: resolve clinic date, explicit dates, relative references, current-window
   cues, and elapsed intervals only when the denominator is supported.
4. Scope and target selection: decide which candidates are current, seizure-relevant,
   benchmark-relevant, and highest-priority under Gan policy.
5. Canonical label construction: build the exact Gan label surface for the selected candidate or
   selected candidate group.
6. Aggregation and arbitration: combine event counts only when they share a legitimate denominator;
   otherwise choose among candidates rather than batching them blindly.
7. Certainty and benchmark abstention policy: distinguish a valid `unknown` label from
   `no seizure frequency reference`, invalid output, and true abstention.
8. Evidence and schema validation: keep these as cross-cutting diagnostics or guarded repair stages,
   not as the primary semantic decision engine unless an experiment explicitly tests that objective.

Stages 2-7 are still heavily bundled in the current best programs. The R11 D1 date-event stage makes
candidate and temporal structure more explicit, but the final adjudicator still performs current-scope
selection, label construction, aggregation, unknown/no-reference policy, and most certainty decisions
in one LLM call.

## Benchmark Alignment Addendum

The author-provided evaluator changes what should count as primary Gan S0 evaluation. Section 2.6.1
of the paper defines the label-scheme surfaces we should ask the model to produce: `unknown`,
`no seizure frequency reference`, seizure-free durations, ordinary rates, cluster rates, and
`unknown, N per cluster`. Our prompts and schema mostly rediscovered that grammar, but future
example selection and label-construction work should treat that section as the source of truth for
surface forms.

The evaluator code supplied by the author is the source of truth for paper-comparison scoring. It
differs from our canonical clinical scorer in exactly the places that can create comparison noise:
`no seizure frequency reference` is collapsed into the unknown class, `multiple` is context
dependent, ranges are averaged over final rate bounds, and 365-day/30-day constants are used.

That means future Gan reports should have two explicit layers:

- Primary benchmark comparison: `gan2026_paper_reproduction`, with repair/range/tolerance options
  reported if enabled.
- Diagnostic clinical analysis: `gan_frequency_deterministic_v1`, especially for preserving the
  clinically meaningful `unknown` versus `no seizure frequency reference` distinction.

The decomposition claims below should therefore be reread as mechanism/diagnostic claims unless the
underlying run has been rescored with `gan2026_paper_reproduction`.

## Why The Original Six Stages Need Revision

| Proposed stage | Keep? | Revision |
| --- | --- | --- |
| Identify all temporal events | Partly | Replace with candidate inventory. Frequency-bearing content includes events, intervals, clusters, vague current frequency, unknown cues, and no-reference cases. |
| Resolve implicit date references | Yes | Keep as temporal anchoring, but only calculate elapsed windows when the anchor and denominator are clinically tied to seizure frequency. R15 showed broad arithmetic injection is harmful. |
| Identify valid event(s) to pay attention to | Yes | This is the core scope/target-selection stage. It should decide current vs historical, seizure vs non-seizure, highest current rate, and benchmark policy. |
| Normalise events to standard form | Partly | Split into candidate-structure normalization and final Gan label construction. The existing scorer normalization is post-prediction; it does not decide the label. |
| Batch multiple events into one normalised form | Partly | Aggregation is conditional. Some mentions should be summed, some should be highest-selected, and some should remain separate because they use different seizure types or windows. |
| Determine certainty or abstain | Yes, but rename | Gan has benchmark labels for `unknown` and `no seizure frequency reference`. Treating these as generic abstentions collapses distinct error modes. |

## Evidence From Dataset And Error Audits

The Gan audit guidance matters because the benchmark is single-label despite multi-event notes:

- Gold label target: `seizure_frequency_number[0]`, not `reference[0]`.
- `unknown` and `no seizure frequency reference` are distinct labels.
- Multi-event and conflict patterns are common enough that a single-pass prompt can look correct while
  still making the wrong benchmark selection.

The multi-event validation stratification made this concrete:

- Strict multi/highest-selection records underperformed simpler records.
- Seizure-free conflict records underperformed records without such conflict.
- Unknown-with-event-mention records were especially difficult.
- Gold multi-span evidence records were much harder than ordinary records.

The practical implication is that decomposition should focus less on generic event extraction and more
on candidate selection policy, denominator control, and benchmark-label construction.

## Current Program Bundling

### Base Adjudicator

`GanFrequencyS0Signature` in `src/clinical_extraction/programs/gan_frequency_s0.py` still bundles
most semantic work into one prediction:

- identify whether the note contains seizure-frequency evidence;
- decide current versus historical scope;
- choose highest current frequency when multiple seizure types or periods appear;
- map vague and quantified language to canonical Gan labels;
- preserve cluster syntax;
- distinguish seizure-free, unknown, and no-reference cases;
- emit evidence and confidence.

This means the base adjudicator spans candidate inventory, temporal reasoning, target selection, label
construction, aggregation, certainty policy, and evidence selection.

### Deterministic Temporal Candidates

`src/clinical_extraction/gan/temporal_candidates.py` exposes `GanTemporalFrequencyCandidate` and
`build_temporal_frequency_candidates_from_note`.

This is useful, but it is not a general "all temporal events" extractor. It is a targeted
candidate-label builder. Candidate objects already contain canonical labels and derivations, so this
stage partially performs:

- frequency-content detection;
- candidate construction;
- some temporal-window interpretation;
- some canonical label construction.

The final LLM then decides whether to trust, reject, merge, or override those candidates.

### D1 Date-Event Payload

`GanDateEventPayload` and `build_deterministic_date_event_payload` in
`src/clinical_extraction/programs/gan_frequency_s0.py` make R11/R15 D1 more decomposed than the older
builder-gap program.

D1 exposes:

- clinic date;
- temporal anchors;
- seizure events;
- seizure-free intervals;
- cluster events;
- current-window cues;
- candidate labels;
- evidence text;
- diagnostic arithmetic.

But the payload is built from the same targeted candidate machinery. It is therefore a structured
view over candidate-label evidence, not an independent event table with exhaustive event recall. D1
helps the adjudicator see temporal structure, but it does not isolate target selection, aggregation,
or abstention as separately measured stages.

### Verifier/Repair

`GanFrequencyS0VerifierSignature` tries to confirm, repair, or abstain after a draft answer. In
practice, validation-ladder and expanded-builder experiments showed this extra stage is usually neutral
or harmful for monthly accuracy. The verifier also bundles multiple things:

- evidence checking;
- schema repair;
- cluster repair;
- unknown/no-reference policy;
- current-frequency repair.

Because it is broad, it is not yet a clean certainty-only or evidence-only component.

### Scorer Normalization

`src/clinical_extraction/gan/frequency.py` normalizes labels for scoring and provides monthly,
Purist, and Pragmatic categories. This is clean post-prediction normalization, but it does not solve
prediction-time selection. It should not be mistaken for the pipeline's event-normalization stage.

## Experiments Mapped To Components

### Experiments That Most Directly Tested Decomposition

| Experiment | Component tested | Result | Interpretation |
| --- | --- | --- | --- |
| Pipeline stage graph A1-A5, 2026-05-21 | Coarse stage graph: direct, extract+repair, candidates->adjudicate, verify/repair variants | Candidates->adjudicate was best on cap25 at 52% monthly. | First evidence that deterministic candidates are useful as an upstream stage. |
| Stage executor E1-E5, 2026-05-21 | Candidate source: deterministic, LLM, hybrid, verifier/repair | Deterministic candidates beat LLM candidates and hybrid on the cap slice. | The useful mechanism was not "more LLM decomposition"; it was reliable candidate construction. |
| Slot payload, 2026-05-21 | Structured count/window/cluster slot presentation | +8pp on cap25, but residual replay was null. | Partial test of event/count/window representation, but it did not generalize as an independent mechanism. |
| R11 date-stage grid D0-D3, 2026-05-28 | Deterministic date-event payload vs LLM date events vs hybrid | D1 deterministic date-events won on cap25; LLM date-events failed badly; hybrid added no clear gain. | Best current evidence for explicitly separating temporal/candidate structure before adjudication. |
| R15 D1 guardrail ablation, 2026-05-28 | D1 payload guardrails and arithmetic injection | D1 v1.2b schema guard only reached 79.9%; arithmetic injection and relative-anchor guardrails regressed. | Temporal arithmetic should remain diagnostic until it is more precise. |
| R12 entity-first C0/C1, 2026-05-28 | Entity-first pipeline graph | Entity-first collapsed for GPT and Qwen. | Broad entity extraction lost local frequency context; not all decomposition is helpful. |

### Experiments That Tested Certainty, Evidence, Or Repair

| Experiment | Component tested | Result | Interpretation |
| --- | --- | --- | --- |
| Validation ladder V0-V7, 2026-05-21 | Verify/repair, plausibility checks, evidence quote guards | Deterministic evidence/prediction-affecting guards caused abstention or denominator harm; verifier/repair was mostly neutral. | Evidence and certainty checks need narrow objectives and strict gates. |
| Unknown-overuse guard, 2026-05-24 | Prompt-level certainty/unknown correction | Rejected; over-corrected true unknowns into rates. | Unknown/no-reference cannot be fixed by a broad instruction. |
| R1.1 invalid-schema analysis, 2026-05-26 | Invalid label surfaces | Most invalids were label-policy failures, not JSON failures. | Schema validity is necessary but not the hard part. |

### Experiments That Mostly Tested Other Components

| Experiment family | Main factor | Why it mattered |
| --- | --- | --- |
| Candidate builder-gap v1 | Deterministic candidate coverage | This became the operational default at 80.6% validation monthly because candidate recall and exact policy examples were the biggest immediate bottleneck. |
| Expanded builders and canonical examples | Builder coverage and prompt examples | Improved operational performance but did not isolate target selection from label construction. |
| Candidate presentation variants | Prompt surface | Small or inconsistent gains; presentation was not the main ceiling. |
| Qwen/GPT model comparisons | Model transfer | Showed local Qwen is competitive on category metrics but lower on exact monthly labels. |
| R13 self-consistency | Compute allocation and aggregation | No variance and no gain on the tested slice. |
| R14 GEPA | Optimizer-generated instruction changes | Failed; instruction bloat and objective mismatch hurt semantics. |
| Holdout evaluation | Generalization check | Validation-to-test drop showed the apparent ceiling was split-sensitive. |

## How Many Experiments Were Component Tests?

There are two useful ways to count this.

From the experiment registry, Gan has 105 rows, but many are historical or pending backfill. The
clearest decomposition categories in the registry are:

- `pipeline_stage_graph`: 5 rows.
- `stage_executor`: 5 rows.
- `validation_ladder_rung`: 7 rows.

That is roughly 10 clearly stage-graph/executor rows, or 17 rows if validation-ladder certainty and
evidence checks are included. The rest are mostly implementation variants, prompt/policy variants,
model-track comparisons, evidence strategy, examples, optimizer attempts, and backfilled legacy rows.

From the current cleaned `configs/experiments` inventory, there are 28 Gan configs:

- 9 `stage_executor`;
- 4 `pipeline_stage_graph`;
- 6 `implementation_variant`;
- 4 `compute_allocation_and_aggregation_policy`;
- 3 `model_track`;
- 1 `verification_strategy`;
- 1 `program_architecture`.

So the newer configuration set is more decomposition-oriented: 13 of 28 current configs are direct
stage-graph or stage-executor tests. That shift is mainly due to R11/R12.

At the documented run-arm level, the cleanest component tests are:

- 5 A-series stage-graph arms;
- 5 E-series stage-executor arms;
- 8 R11 date-stage runs across GPT and Qwen;
- 4 R12 entity-first runs across GPT and Qwen;
- 7 validation-ladder arms for verifier/evidence/certainty behavior.

That gives about 22 run-level stage-graph/executor tests, or about 29 if the validation ladder is
counted as certainty/evidence decomposition. Many other experiments were valuable, but they were not
clean tests of the proposed pipeline components.

## Why So Much Work Tested Other Components

The historical sequence makes sense:

1. Early runs had basic operational issues: schema validity, evidence support, prompt reliability, and
   direct extraction errors.
2. Error forensics then showed that semantic window selection, cluster handling, and unknown/no-reference
   boundaries were the persistent bottleneck.
3. Deterministic candidate builders gave the first large operational gain, so experiments naturally
   emphasized builder coverage and prompt policy before clean mechanism isolation.
4. Model transfer mattered because the project needs local/non-frontier viability, so Qwen/GPT comparisons
   were not optional even though they do not directly decompose the task.
5. R11/R12 finally moved toward cleaner component isolation, but the winning D1 arm is still an
   arm-level improvement, not a fully separated mechanism proof.

In short: the project optimized for getting a reliable Gan S0 baseline before optimizing for a fully
factorized scientific explanation of the pipeline.

## Current Ceiling Signals

The best validation anchors now are:

- Builder-gap v1 GPT: 80.6% monthly, 86.0% Purist, 88.6% Pragmatic.
- D1 v1.2b GPT: 79.9% monthly, 84.9% Purist, 87.6% Pragmatic.

D1 v1.2b is within 0.7pp of builder-gap v1 and is more decomposed, so it is the better baseline for
future mechanism studies. Builder-gap v1 remains the stronger paper-reporting operational default.

The holdout result is the main caution:

- GPT builder-gap v1 dropped from 80.6% validation monthly to 65.4% holdout monthly.
- Qwen builder-gap v1 dropped from 70.7% validation monthly to 59.1% holdout monthly.

This means the next "maximum threshold" should not be defined by validation-only gains. The real
threshold should require improvement or at least non-regression on hard strata and a holdout-like
evaluation protocol.

## Recommended Gan-Only Decomposition Plan

### Baseline

Use two baselines for different purposes:

- Paper-comparison baseline: builder-gap v1 GPT, rescored with `gan2026_paper_reproduction`.
- Mechanism baseline: D1 v1.2b schema-guard-only GPT, because it exposes the most structured
  candidate/date payload without the harmful arithmetic and relative-anchor additions.
- Diagnostic canonical baseline: the prior `gan_frequency_deterministic_v1` result table, retained
  for clinical error analysis and scorer-sensitivity comparisons.

### Stage 1: Candidate Inventory Coverage

Measure this before adding more LLM stages.

Outputs to audit:

- candidate label present;
- candidate evidence span;
- candidate type: event count, seizure-free interval, cluster, vague frequency, unknown cue,
  no-reference cue, multi-type frequency;
- whether the gold label is present in candidates;
- whether a gold-equivalent Purist or Pragmatic category is present;
- hard-stratum tags: multi/highest, seizure-free conflict, cluster, unknown-with-events.

Reason: existing gains came from deterministic candidate coverage, and both Qwen and GPT failures often
occur when no useful candidate is present.

### Stage 2: Temporal Anchoring

Keep date arithmetic diagnostic until it has a stricter trigger.

Future ablation:

- D1 v1.2b payload without arithmetic candidates;
- deterministic arithmetic only when explicit seizure-event dates and a shared denominator are found;
- no injection into candidate labels unless a preflight precision audit passes.

Reason: R15 showed broad arithmetic candidate injection regressed performance.

### Stage 3: Scope And Target Selection

Make the final adjudicator expose its selected candidate and reason code.

Suggested reason codes:

- current_highest_frequency;
- current_single_frequency;
- seizure_free_current_window;
- cluster_frequency;
- vague_current_frequency;
- historical_only_rejected;
- no_frequency_content;
- frequency_unknown_despite_content;
- conflicting_current_candidates.

Then ablate:

- free adjudication;
- candidate-constrained adjudication;
- candidate-constrained adjudication with explicit reason-code requirement;
- reason-code-only selector followed by deterministic label constructor.

Reason: most residual severe errors are target-selection and label-policy errors, not raw JSON errors.

### Stage 4: Label Construction And Aggregation

Separate selected-candidate choice from exact label emission.

Potential ablation:

- LLM selects a candidate or candidate group;
- deterministic constructor emits the canonical Gan label where possible;
- LLM emits only for unsupported/free-text cases.

This is especially relevant for:

- per-cluster labels;
- multiple events in the same denominator;
- range-to-point ambiguity;
- monthly denominator conversions;
- frequent/infrequent boundary cases.

### Stage 5: Unknown And No-Reference Policy

Do not use a broad unknown-overuse prompt guard.

Instead, test a narrow post-adjudication classifier only on records where the draft label is one of:

- `unknown`;
- `no seizure frequency reference`;
- a quantified rate with weak evidence;
- seizure-free interval in conflict with event mentions.

Reason: the rejected unknown-overuse guard showed that broad certainty instructions can convert true
unknown labels into false quantified rates.

### Stage 6: Evidence And Schema

Keep schema guardrails, but do not let evidence validators rewrite semantic predictions except in
narrow, preregistered cases.

Useful evidence checks:

- evidence quote exists in note;
- evidence quote supports the selected candidate;
- selected candidate supports exact label surface.

The third check is the important one, but it is also the hardest and should be measured separately
from monthly accuracy.

## Recommended Stop Rule For The Gan-Only Push

The "maximum threshold" should be operationalized before running many more variants. A practical stop
rule:

- stop promoting new Gan S0 variants when two consecutive clean component ablations fail to improve
  validation monthly accuracy by at least 1pp without reducing Purist/Pragmatic category accuracy or
  schema validity;
- require no regression on the hard strata that motivated the component;
- before claiming a new ceiling, run a holdout-like or locked validation check because the current
  validation-to-test drop is large.

This prevents chasing cap-slice noise while still allowing targeted component work where the error
taxonomy predicts gains.

## Bottom Line

The right next decomposition is not "all temporal events -> dates -> normalized batch -> abstain." It
is:

1. enumerate benchmark-relevant frequency candidates;
2. anchor only the temporal information needed to justify denominators;
3. select the current benchmark target under Gan policy;
4. construct the exact canonical label;
5. aggregate only when the clinical denominator supports aggregation;
6. distinguish `unknown`, `no seizure frequency reference`, invalid output, and true abstention;
7. keep evidence/schema as measured guardrails.

The current best programs expose some of stages 1-3, especially in D1, but stages 3-6 remain bundled
inside the final adjudicator. The next high-value ablations should split target selection from label
construction, and unknown/no-reference policy from general semantic repair.
