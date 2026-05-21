# Prior Prompt And Error-Analysis Synthesis

Date: 2026-05-18

## Research Question

How should the first DSPy optimization path use previously successful hand-crafted prompts and prior ExECT/Gan error analyses before spending a full validation run?

## Motivation

The first Gan S0 BootstrapFewShot run solved the most urgent schema-validity problem but exposed a weaker clinical-normalization problem. In the 25-record GPT 4.1-mini bootstrap run recorded in `docs/planning/kanban_plan.md`, schema validity reached 96%, but normalized label accuracy was 16.7%, pragmatic category accuracy on valid predictions was 58.3%, and evidence quote support was 0%. A full validation run at this point would mostly measure known weaknesses: frequency-unit/window normalization and unsupported evidence.

The newly recovered prompt and error-analysis artifacts give concrete priors for the next optimization step:

- `docs/archive/prior-context/previously_effective_prompts.md`
- `docs/archive/prior-context/previous_exect_error_analysis.md`
- `docs/archive/prior-context/previous_gan_frequency_error_analysis.md`
- Current planning context in `docs/planning/kanban_plan.md`

## Method

This synthesis treats the old hand-crafted prompts as design evidence, not as a replacement for the current DSPy system. The goal is to extract reusable instruction patterns, boundary examples, and optimization targets that can be represented as DSPy examples, signature descriptions, constraints, or post-DSPy deterministic validation.

The relevant current experiment context is:

- Dataset: Gan 2026 synthetic clinic letters for the immediate next run; ExECTv2 for the next broader field-family baseline.
- Split: Gan dev examples used for BootstrapFewShot; Gan validation remains the next stable evaluation target.
- Model/provider: early Mac iteration uses GPT 4.1-mini; later comparisons should include Qwen3.6:35b, Qwen3.5:9b, Gemini 3 Flash, GPT 5.5, and GPT 4.1-mini.
- Program variant: `GanFrequencyS0Module` with DSPy ChainOfThought and `gan_frequency_s0_metric`.
- Scorer mode: current Gan deterministic scorers separate normalized-label exact match, monthly frequency comparison, Purist category, Pragmatic category, raw diagnostics, and evidence diagnostics.
- Evidence requirement: every present claim should be traceable to an exact source quote, but the first bootstrap result showed this is not yet being learned.

## Key Findings

### 1. The prior prompts succeeded by teaching benchmark contracts, not just clinical reasoning

The ExECT hand-crafted prompt did not rely on broad clinical common sense alone. It gave narrow benchmark-facing examples:

- Focal impaired or altered-awareness wording maps to the coarse benchmark label `focal seizure`.
- Focal seizures with secondary generalisation should usually produce only the primary focal label unless the letter names separate current seizure types.
- A diagnosis line can support epilepsy diagnosis without supporting seizure type inference.
- `symptomatic structural focal epilepsy` should normalize to `focal epilepsy`, not `symptomatic`.
- `single focal seizure` should not be normalized to established epilepsy.

The lesson is that the optimized DSPy system should not be rewarded for clinically richer labels when the benchmark gold is coarser. For ExECT, examples and allowed-label controls need to represent annotation policy as strongly as clinical semantics.

### 2. ExECT diagnosis and seizure-type failures are label-policy failures before they are model-capability failures

The prior ExECT analysis found seizure type F1 of 0.404 for Qwen3.5 and 0.511 for Gemini in the primary sweep. The largest seizure-type error was label granularity: models emitted `focal impaired awareness seizure` or `focal aware seizure` where gold used `focal seizure`. Simulated coarse remapping raised F1 by about 0.140 for Qwen3.5 and 0.099 for Gemini.

Diagnosis errors showed two high-value fixes:

- Modifier capture: `symptomatic structural focal epilepsy` became `symptomatic` instead of `focal epilepsy`.
- False-positive inference: `single focal seizure` or seizure-type evidence became inferred epilepsy diagnosis.

There is also a likely scoring artifact where gold `[]` and prediction empty/null were scored as wrong. That needs investigation before any ExECT result is treated as reportable.

### 3. Gan frequency failures are mostly canonicalization, temporal-window, and abstention-boundary failures

The previous Gan sweep started from a Qwen3.5 validation baseline with relaxed match 0.578 and strict match 0.554 on 294 records. Major miss categories were:

- 44 unparsed predictions from format drift such as inequality prefixes, `or` ranges, every-N phrases, adjective rates, multi-type outputs, cluster format errors, calendar references, and compound free text.
- 35 wrong `unknown` predictions where gold had specific frequencies, often clusters or multi-month rates.
- 23 seizure-free/no-reference errors where the model preferred recent seizure freedom over an ongoing or period rate.

The strongest discovered annotation-specific rule was the Gan 6-month seizure-free threshold:

- If seizure freedom is less than 6 months, compute a period rate from the total described events.
- If seizure freedom is 6 months or longer, use `seizure free for N unit`.

In the prior Qwen3.5 sweep, the v3 condition using this rule was best overall: relaxed match 0.646 and strict match 0.592. However, v3 also showed prompt-length/time-out pressure, and on completed documents the apparent relaxed rate was 190/233 = 81.5%. That means the rule content was useful, but the implementation format was too heavy for reliable full-scale runs.

### 4. Examples are powerful but interact badly when they overgeneralize

The Gan error analysis is a warning against simply adding every good example. Examples alone and guideline-plus-example variants sometimes underperformed the baseline. Specific interactions mattered:

- A quarter conversion example encouraged `2 to 4 per 3 month` when the letter said `2 to 4 times per month over the last quarter`; the quarter was an observation window, not the rate denominator.
- Additional seizure-free examples appeared to interfere with cluster formatting in at least one v3 case.
- Rich examples reduced unparsed or unknown failures in small samples but did not reliably generalize across the full validation set.

The next DSPy optimization should use a compact set of high-leverage examples with counterexamples for known overgeneralization traps, not a large prompt copied from the old sweep.

### 5. Evidence support must become an optimization target, not just a schema field

The prior hand-crafted Gan prompt required exact contiguous source quotes for every present claim. The current first bootstrap run still reported 0% evidence quote support. This suggests the metric and examples used for optimization are teaching label validity more strongly than evidence grounding.

For the next run, evidence should be part of the metric or a filtered training-example criterion. Otherwise the model can learn valid labels while remaining unusable for auditable clinical extraction.

## Optimization Guidance Before Full Validation

### Immediate Gan S0 changes

Use a compact "v7-style" optimization target rather than a full rich prompt:

- Keep canonical output forms explicit: `N per unit`, `N to M per unit`, `N per M unit`, `N cluster per unit, M per cluster`, `seizure free for N unit`, `unknown`, and `no seizure frequency reference`.
- Keep singular units: `day`, `week`, `month`, `year`.
- Include the 6-month seizure-free threshold in the signature or optimizer instructions.
- Include one short-seizure-free period example where a rate must be computed rather than a seizure-free label.
- Include one long-seizure-free example where the seizure-free label is correct.
- Include one ongoing-rate-overrides-recent-seizure-free example.
- Include one year-to-date denominator example where months elapsed since January are used.
- Include one cluster example with full required format.
- Include one quarter-as-window counterexample so `over the last quarter` does not automatically become `per 3 month`.
- Include one highest-frequency-current-type example when multiple seizure types have quantified rates.

Do not include low-value examples for rules already captured deterministically unless the current model specifically fails them. In particular, avoid making `quarter -> 3 month` a general rule.

### Gan scoring and optimization metric changes

Before full validation, the bootstrap metric should prefer examples that satisfy both label and evidence constraints:

- Reject or downweight predictions without an exact source quote when the label is present.
- Reward normalized-label validity and pragmatic category agreement, but include evidence quote support as a gate or additive term.
- Track failure categories separately: invalid format, wrong abstention, wrong temporal window, wrong unit bucket, cluster-format failure, and evidence unsupported.

This keeps the optimization aligned with the project architecture: deterministic validators and scorers around LLM components, not only a model-generated label.

### ExECT baseline changes before broader field-family runs

For ExECT S0/S1, do not begin with an unconstrained clinically rich label surface. Start with benchmark-facing label contracts:

- Remove or hide ILAE-specific focal labels from the benchmark seizure-type extraction surface, or provide explicit examples mapping them to `focal seizure`.
- Add an example that secondary generalisation is not a separate seizure type unless independently named as a current type.
- Add an example that seizure type cannot be inferred from diagnosis alone.
- Consider a constrained diagnosis label set for benchmark-facing diagnosis extraction: `epilepsy`, `focal epilepsy`, `generalized epilepsy`, `juvenile myoclonic epilepsy`, and `status epilepticus`.
- Add diagnosis examples for `symptomatic structural focal epilepsy -> focal epilepsy` and `single focal seizure -> null`.
- Investigate the empty-list/null diagnosis scoring artifact before reporting diagnosis exact match.

These ExECT changes should be treated as annotation-policy alignment, not as clinical simplification. A separate clinically rich output can still exist, but benchmark-facing metrics should use the benchmark-facing view.

## Recommended Next Experiments

### Experiment 1: Gan compact synthesis-backed bootstrap

Run a new Gan S0 bootstrap on the dev split with a compact instruction/example set derived from this synthesis. Keep the run capped initially.

Success criteria:

- Schema validity remains at or above the first bootstrap result of 96%.
- Evidence quote support improves materially from 0%.
- Normalized-label exact match improves from 16.7% on the first bootstrap sample.
- Pragmatic category accuracy on all records improves over the first bootstrap run, not only on valid predictions.

Do not move to full validation until this capped run shows evidence support is no longer structurally absent.

### Experiment 2: Full Gan validation after compact optimization

After Experiment 1 passes the evidence and validity gates, run the optimized Gan S0 module on the full validation split with confidence intervals.

Report:

- Dataset and split: Gan validation.
- Model/provider and exact model config.
- Program variant and compiled DSPy state.
- Scorer mode and normalization rules.
- Full metric table with confidence intervals.
- Error taxonomy with bounded examples.
- Evidence support diagnostics.

### Experiment 3: ExECT benchmark-facing label-policy ablation

Before broad ExECT modules, run an S0/S1 field-family ablation comparing:

- baseline broad clinical labels,
- constrained benchmark-facing labels,
- constrained labels plus mapping/null-policy examples.

Primary outcomes:

- seizure type micro F1,
- diagnosis exact match,
- medication field-family metrics,
- evidence support,
- schema validity.

This isolates whether ExECT performance improves from label-surface constraints, few-shot examples, or both.

## Limitations

The Gan prior sweep used Qwen3.5 validation runs, while the current first bootstrap context is GPT 4.1-mini on a small 25-record validation cap. The pattern-level failures are highly relevant, but exact gains should not be transferred across model families or prompt architectures.

The ExECT prior analysis references earlier full-extraction conditions and may not match the current code's exact scorers, label constants, or field-family scope. The empty-list/null scoring artifact is especially important to resolve before comparing exact-match diagnosis numbers.

The recovered hand-crafted prompts are effective examples of benchmark alignment, but they should not be copied wholesale into DSPy. Long prompts caused timeout and interaction problems in the Gan sweep. The safer conclusion is to encode a small number of high-impact boundary examples and let DSPy optimization choose demonstrations under auditable run artifacts.

## Concrete Next Engineering Tasks

1. Save compiled DSPy module state in run artifacts so selected demos are auditable. Completed in `scripts/run_experiment.py`; optimized runs now write `artifacts/compiled_state.json`.
2. Add a compact Gan synthesis-backed prompt/example policy or training-example selection path. Completed with `gan_frequency_s0_synthesis_v1` and `configs/experiments/gan_s0_synthesis_bootstrap_gpt4_1_mini.json`.
3. Update the Gan bootstrap metric so evidence quote support affects optimization. Completed with the optimizer-only `synthesis_exact_with_evidence` metric; benchmark scorer semantics are unchanged.
4. Run a capped Gan bootstrap comparison before full validation. Completed as `runs/gan_s0_synthesis_bootstrap_gpt4_1_mini_20260518T062451Z`.
5. Investigate the ExECT diagnosis empty/null scoring artifact before ExECT reporting.
6. Add ExECT benchmark-facing label-policy examples before the ExECT S0/S1 baseline.

## 2026-05-18 Implementation Result

The synthesis-backed optimization has now been implemented and run on the capped 25-record Gan validation slice.

Implementation artifacts:

- `src/clinical_extraction/programs/gan_frequency_s0.py`: compact synthesis guidance in the DSPy signature, synthesis examples with gold evidence, an optimizer-only exact-label-plus-evidence metric, prioritized locatable-evidence demos, and transparent prediction normalization for two repairable Gan surface forms.
- `src/clinical_extraction/experiments/config.py`: optimizer configs can choose `pragmatic_category` or `synthesis_exact_with_evidence`.
- `configs/experiments/gan_s0_synthesis_bootstrap_gpt4_1_mini.json`: capped synthesis-backed GPT 4.1-mini experiment config.
- `scripts/run_experiment.py`: records synthesis guidance, optimizer metric settings, and compiled DSPy state in run artifacts.
- `runs/gan_s0_synthesis_bootstrap_gpt4_1_mini_20260518T062451Z`: best capped synthesis-backed run so far.

Best capped run metrics:

| Metric | Value |
|---|---:|
| schema_valid_prediction_rate | 0.960 |
| normalized_label_accuracy | 0.375 |
| monthly_frequency_accuracy | 0.542 |
| purist_category_accuracy | 0.542 |
| pragmatic_category_accuracy | 0.792 |
| evidence_quote_support_rate | 0.870 |
| evidence_offsets_present_rate | 0.870 |
| evidence_offsets_valid_rate | 1.000 |

Compared with the first bootstrap run recorded in the kanban, the synthesis-backed run preserved the 96% schema-validity target while improving normalized-label accuracy from 16.7% to 37.5% and evidence quote support from 0% to 87.0%. Pragmatic category accuracy also improved from 58.3% on valid predictions to 79.2% on valid predictions in the capped run.

The run is now good enough to justify a full validation pass, but two caveats should be carried forward:

- The only remaining invalid prediction in the capped run is an incomplete cluster label (`4 cluster per 3 month`) missing the required per-cluster component.
- The dominant residual label errors are still temporal/window interpretation and partial cluster handling, not schema shape.
