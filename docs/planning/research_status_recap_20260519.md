# Research Status Recap

Date: 2026-05-19

Use `docs/planning/kanban_plan.md` as the active tracker (session handoff, gates, next pull). Frozen-thread run tables and configs: `docs/planning/kanban_frozen_threads_history.md`. This recap is the narrative research archive.

## Research Question

Where is the project now, what has it discovered so far, what are the main
active research questions, and what should the next experiments clarify?

## Source Artifacts

This recap synthesizes the live planning board and recent research notes:

- `docs/planning/kanban_plan.md`
- `docs/policies/deterministic_foundation_decisions.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/archive/prior-context/prior_prompt_error_analysis_synthesis.md`
- `docs/experiments/gan/gan_s0_full_validation_error_read.md`
- `docs/experiments/gan/gan_s0_post_repair_validation_replay.md`
- `docs/experiments/gan/gan_s0_gepa_harness_run_20260519.md`
- `docs/experiments/gan/gan_s0_gepa_feedback_run_20260519.md`
- `docs/experiments/gan/gan_s0_gepa_qwen35b_probe_run_20260519.md`
- `docs/experiments/gan/gan_s0_gepa_qwen35b_max10000_followup_20260519.md`
- `docs/workstreams/optimizer/qwen_local_latency_experiment_20260518.md`
- `docs/experiments/exect/exect_s0_s1_baseline_design.md`
- `docs/experiments/exect/exect_s0_s1_smoke_inspection.md`
- `docs/experiments/exect/exect_s0_s1_validation_cap25_inspection.md`
- `docs/experiments/exect/exect_section_aware_ablation_design.md`
- `docs/experiments/exect/exect_section_aware_cap25_inspection.md`
- `docs/workstreams/optimizer/dspy_gepa_react_best_practices_deep_dive.md`
- `docs/policies/published_benchmark_metrics.md`

## Current Position

The project has moved beyond the deterministic foundation milestone. The
loaders, gold-source policies, normalization rules, deterministic scorers,
split metadata, artifact layout, and evidence diagnostics are now strong enough
to support model-backed research without silently changing benchmark semantics.

The active research focus is Gan S0 seizure-frequency extraction. Gan is narrow,
well instrumented, and exposes the project's hardest recurring issues in a
compact form: canonical label control, temporal-window reasoning, cluster
formats, abstention boundaries, and source-evidence support.

ExECT S0/S1 is open as the broader-schema anchor, but current evidence supports
keeping the monolithic field-family baseline as the active comparison point. The
first section-aware ablation was useful as a negative result, not as a promoted
architecture.

## What Has Been Discovered

### Deterministic contracts are working

The deterministic foundation is doing the most important quiet work in the
project: it keeps dataset interpretation, scorer semantics, diagnostic metrics,
and benchmark-facing claims separable.

For ExECTv2, the current benchmark-facing S0/S1 view is intentionally limited
to audited diagnosis, seizure type, and annotated medication field families.
Medication temporality, seizure frequency, investigations, history, birth
history, aetiology, onset, and diagnosis-date fields remain deferred until their
source-specific scorer semantics are audited.

For Gan 2026, `seizure_frequency_number[0]` remains the primary gold label.
`reference[0]` is a secondary cross-check and difficulty signal, not an
alternative gold source. Monthly-frequency, Purist category, Pragmatic category,
normalized-label exact match, raw exact match, and evidence support are reported
as distinct meanings.

This matters because many future experiments will be tempting to compare across
models, prompts, and architectures. The current documentation prevents those
comparisons from becoming benchmark claims unless the dataset, split, schema
level, scorer mode, and metric caveats are stable.

### Gan synthesis-backed optimization produced the strongest current reference run

The synthesis-backed Gan S0 path converted prior prompt/error-analysis lessons
into compact DSPy guidance, prioritized locatable-evidence examples, and an
optimizer-only exact-label-plus-evidence metric.

The capped synthesis run improved the first bootstrap result from weak evidence
grounding to useful evidence grounding. On the 25-record cap, schema validity
stayed at `96.0%`, normalized-label accuracy improved from `16.7%` to `37.5%`,
Pragmatic category accuracy improved to `79.2%`, and evidence quote support
rose from `0.0%` to `87.0%`.

The subsequent full Gan validation artifact
`runs/gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z`
is the current best full-validation reference:

| Metric | Value |
|---|---:|
| Records predicted | 299 |
| Schema-valid prediction rate | 97.3% |
| Normalized-label accuracy | 51.5% |
| Monthly-frequency accuracy | 62.9% |
| Purist category accuracy | 70.1% |
| Pragmatic category accuracy | 73.9% |
| Evidence quote support rate | 89.9% |

This result supports the idea that compact benchmark-contract guidance is more
useful than copying large historical prompt bundles into DSPy.

### The safe deterministic Gan repair boundary is small

The post-repair replay over the full-validation Gan artifact changed exactly
three stored predictions by normalizing repairable surface forms:

- quoted special labels such as `"unknown"`
- matching-count denominator ranges such as `1 per 3 week to 1 per 2 week`

The derived replay artifact
`runs/gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_surface_replay_20260518T000000Z`
improved schema validity from `97.3%` to `98.3%`, but benchmark-facing metric
changes were small.

This is an important boundary result. Deterministic postprocessing can safely
normalize one-to-one output surfaces, but the remaining Gan failures require
semantic evidence-aware logic:

- incomplete cluster labels
- `unknown per cluster`
- cluster labels where gold is a simple rate
- null or abstained outputs where a label is required
- `unknown` versus `no seizure frequency reference`
- temporal-window and denominator choices
- non-contiguous or paraphrased evidence

The next semantic repair should therefore be a named verifier/repair or
abstention-calibration variant, not another hidden deterministic scorer change.

### GEPA is operationally available, but not yet a proven quality lever

The GEPA harness is now real rather than theoretical. A capped GPT 4.1-mini run
compiled with `dspy.GEPA`, wrote optimizer logs and compiled state, and exposed
the necessary runtime fixes: exactly one GEPA budget control must be set, a
reflection LM must be provided, and cloudpickle is needed for DSPy dynamic
signature state.

The richer Gan feedback run
`runs/gan_s0_gepa_direct_cap5_gpt4_1_mini_20260519T054057Z` showed the intended
near-term effect on a five-record cap:

| Metric | Earlier harness | Rich-feedback run |
|---|---:|---:|
| Schema-valid prediction rate | 80.0% | 100.0% |
| Normalized-label accuracy | 50.0% | 40.0% |
| Monthly-frequency accuracy | 50.0% | 60.0% |
| Pragmatic category accuracy | 75.0% | 60.0% |
| Evidence quote support rate | 25.0% | 80.0% |

This suggests GEPA feedback can improve schema and evidence behavior, but it
has not yet shown stable label-quality gains. It also introduced prompt-bloat
risk, which must now be treated as a first-class metric.

The local Qwen3.6:35b GEPA probes sharpened the same conclusion. Qwen could run
the GEPA harness end to end, and a larger reflection/output budget improved
some five-record metrics, but compile cost and instruction length grew sharply.
The `max_tokens=10000` follow-up expanded the selected instruction to `10562`
characters / `1819` words, took `535.80s` to compile, and still introduced a
non-canonical label (`several per week`). This does not justify making local
Qwen GEPA a default workflow.

### Local Qwen is viable mainly as direct extraction

The Qwen latency and overnight validation work answered an operational question:
local Qwen can participate in this project, but only under a paced,
direct-extraction policy.

The strongest local-Qwen Gan S0 reference is the Qwen3.6:35b direct full
validation run on 299 records:

- monthly-frequency accuracy: `55.6%`
- Purist category accuracy: `61.7%`
- Pragmatic category accuracy: `69.2%`
- schema validity: `89.0%`
- evidence support: `94.0%`

Raising the default direct completion cap from `256` to `1024` did not improve
monthly-frequency, Purist, Pragmatic, schema-validity, normalized-label, or
invalid-count metrics. It slowed prediction from `6.55` to `9.99` seconds per
record and slightly worsened evidence support.

The main local-Qwen bottleneck is therefore canonical label control and evidence
span behavior, not broad output-budget starvation. Direct-output
canonicalization and evidence-length guardrails are the right next local-Qwen
interventions.

### ExECT label-policy alignment helped, but section-aware architecture regressed

The ExECT S0/S1 path has progressed from smoke-test viability into a meaningful
partial baseline. The first zero-shot smoke validated the runner and artifact
path but was too permissive about clinically plausible labels, planned or
previous medication mentions, and richer seizure-type surfaces.

The v2 and v3 prompt-policy follow-ups corrected medication scope, aligned
diagnosis labels with the current audited scorer vocabulary, added a narrow
fused seizure-type bridge, and added ExECT evidence diagnostics. On the
three-record smoke, v3 reached `100.0%` micro F1 and `90.0%` evidence support,
but that was correctly treated as a smoke result, not a performance estimate.

The larger ExECT cap-25 monolithic run is the more useful anchor:

| Metric | Value |
|---|---:|
| Micro precision | 68.8% |
| Micro recall | 79.5% |
| Micro F1 | 73.7% |
| Diagnosis F1 | 60.5% |
| Seizure-type F1 | 65.8% |
| Annotated-medication F1 | 92.1% |
| Evidence quote support | 92.1% |

The section-aware ablation held dataset, split, scorer, schema level, prompt
version, deterministic bridges, and model fixed, changing only the program
variant. It underperformed:

| Metric | Monolithic | Section-aware |
|---|---:|---:|
| Micro F1 | 73.7% | 65.6% |
| Diagnosis F1 | 60.5% | 44.9% |
| Seizure-type F1 | 65.8% | 59.7% |
| Annotated-medication F1 | 92.1% | 88.9% |
| Evidence quote support | 92.1% | 75.5% |

The evidence regression was especially informative. The section-aware framing
encouraged heading-shaped synthetic evidence such as `Diagnosis: Focal epilepsy`
or `Medication: Keppra...`, which often did not exist as exact source text.

The conclusion is not that section-aware extraction is permanently bad. It is
that simple section selection plus thin family-specific prompts is not enough.
The monolithic ExECT baseline should remain the active anchor until a stronger
architecture hypothesis explains why the negative result should change.

## Main Active Questions

### Can GEPA improve Gan label quality without producing prompt bloat?

The project now has the ingredients GEPA needs: deterministic scorers,
failure-category feedback, benchmark-policy audits, and small train/dev splits.
The unresolved question is whether GEPA can produce compact, transferable
benchmark-boundary guidance rather than long, brittle instruction text.

This is important because Gan's remaining failures are exactly the kind of
policy-boundary failures GEPA should, in principle, learn from: seizure-free
thresholds, year-to-date denominators, cluster completeness, forbidden units,
and abstention boundaries. If GEPA cannot improve this focused task cleanly, it
is unlikely to be the right first tool for broader ExECT optimization.

### Where should Gan semantic repair live?

The deterministic postprocessor has reached its safe boundary. Remaining
failures require interpreting evidence and choosing between clinically plausible
labels. The active question is whether the next improvement should be:

- an extract-verify-repair variant
- an abstention-calibration variant
- a ReAct temporal-tools probe
- richer direct-extraction feedback and examples

This matters because repair can easily inflate metrics by hiding model errors
inside postprocessing. The project needs repair rates, abstention rates,
coverage, evidence support, and extraction-only metrics reported separately.

### Can local Qwen be made reliable through direct-path controls?

Local Qwen3.6:35b is feasible for direct Gan validation, but current failures
are not solved by larger completion budgets or optimizer-heavy prompts. The
active question is whether narrower controls can reduce invalid labels and
evidence problems:

- canonical label vocabulary enforcement
- cluster-format retention
- forbidden unit handling (`quarter`, `fortnight`)
- forbidden lexical alternatives (`few`, `several`)
- evidence-length and quote-boundary guardrails

This matters because local models are valuable for cost, privacy, and iteration,
but only if they can remain reproducible and reasonably efficient.

### Is ExECT still mostly a label-policy problem, or does it need stronger architecture?

The ExECT cap-25 result shows a mixture of label-policy drift,
surface-normalization errors, and cross-family leakage. The section-aware
negative result means the first architecture attempt did not solve the leakage
and worsened evidence grounding.

The active question is whether the next ExECT gain should come from monolithic
prompt/GEPA label-policy optimization, stronger per-family prompts, better
field-family disentangling, or an explicit verify/repair stage.

This matters because ExECT is the broader clinical schema proving ground. If the
project widens ExECT too early, it risks conflating schema breadth, architecture,
label policy, evidence support, and scorer caveats.

### When is ReAct worth the complexity?

The best-practices review argues that ReAct should not be a default extractor.
The highest-value probe is bounded Gan temporal reasoning with deterministic
tools for candidate frequency retrieval, temporal anchors, denominator math,
canonical label validation, cluster validation, and quote lookup.

This matters because tool-use can either clarify hard temporal cases or become
an expensive source of new failure modes. The project should only use ReAct
where deterministic tools answer a specific hard subproblem that direct
extraction is known to fumble.

## Expected Next Findings

### Gan GEPA feedback should clarify whether optimizer text can stay compact

The next richer-feedback Gan GEPA comparison should show whether failure-text
feedback improves label validity, temporal-window handling, cluster behavior,
and evidence support simultaneously. The key expected finding is not just a
metric delta; it is whether the selected instruction remains auditable and
short enough to be a practical program artifact.

If it works, GEPA becomes the near-term path for generating benchmark-contract
rules. If it fails or keeps bloating, the project should pivot toward explicit
verifier/repair or ReAct probes for the hardest Gan subproblems.

### Qwen direct-path cleanup should clarify the local-model ceiling

Canonicalization and evidence guardrails should reveal whether local
Qwen3.6:35b's full-validation gap is mostly output-control friction or deeper
task reasoning weakness.

If invalid labels drop without evidence regression, Qwen can become a stable
member of the fixed-condition model comparison matrix. If semantic errors remain
dominant, Qwen may still be useful for local smoke tests but not as a leading
quality candidate without distilled guidance from hosted-model experiments.

### ExECT monolithic optimization should clarify the next architecture decision

The next ExECT work should likely start from the monolithic cap-25 anchor and
optimize label policy before reopening section-aware architecture. This should
clarify whether the remaining diagnosis and seizure-type failures are mostly
prompt-contract failures or true architecture limitations.

If monolithic policy optimization improves F1 and evidence support, sectioning
can stay parked. If it does not, a second architecture design should explicitly
address the first section-aware failure: weak per-family policy grounding and
synthetic evidence echoing.

### A bounded Gan ReAct probe should clarify whether tools help temporal reasoning

A hard-case ReAct probe should be judged on matched direct-vs-tool results:
exact/pragmatic match, invalid-label rate, evidence support, tool-call count,
latency, and examples of wins and losses.

The expected useful finding is not that agents are globally better. It is
whether deterministic tools can help on specific Gan cases involving multiple
events, recent seizure freedom, clusters, year-to-date denominators, and
multi-type frequency assignment.

## Why These Questions Matter

The central research risk is not that the models cannot extract anything. They
can. The risk is that apparent improvements come from changing hidden contracts:
different gold interpretations, different scorer semantics, broader or narrower
label surfaces, repaired outputs that are not labeled as repairs, or metrics
reported without evidence caveats.

The current project structure is valuable because it turns those risks into
explicit experiment factors. Gan S0 functions as the tight reference task for
testing optimizer feedback, local-model behavior, evidence support, and temporal
reasoning. ExECT S0/S1 functions as the broader-schema anchor for testing
field-family policy, label granularity, and architecture choices.

The next phase should therefore prioritize experiments that answer one question
at a time:

- Can optimizer feedback improve Gan without prompt bloat?
- Can local Qwen direct extraction be tightened without heavy reasoning?
- Can ExECT monolithic label-policy optimization beat the current cap-25 anchor?
- Can tool-use solve bounded temporal hard cases better than direct extraction?

Keeping those questions separate will make the eventual model and architecture
comparisons much more credible.

## Recommended Next Pull

The live Kanban recommendation is still well aligned with the evidence:

1. Enrich the Gan S0 GEPA feedback metric from the current exact-label-plus-evidence harness to the planned failure taxonomy.
2. Re-run the Gan S0 GEPA capped diagnostic before opening the ReAct temporal-tools probe.
3. Tighten Gan direct-output canonicalization for local Qwen without changing scorer semantics.
4. Add an evidence-length guardrail for Gan direct extraction.
5. Keep Qwen3.6:35b on direct extraction by default.
6. Keep the monolithic ExECT S0/S1 baseline as the active comparison anchor.

## Caveats

The Gan full-validation work is on the repo's synthetic validation split, not
the published Gan real-letter benchmark set. Gan category accuracy is partially
aligned with published category evaluation but should not be described as
published benchmark reproduction.

The ExECT S0/S1 metrics are partial field-family diagnostics, not full ExECTv2
paper reproduction. The current repo does not yet implement CUI/feature-aware
scoring across all ExECT annotation families.

Several reported GEPA and Qwen comparisons are capped five-record probes. They
are useful for operational and failure-shape learning, not stable quality
estimates.

Evidence quote support remains diagnostic unless an experiment explicitly makes
it part of an optimizer metric. Evidence repair behavior should continue to be
tagged separately from exact model-provided quote support.
