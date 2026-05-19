# DSPy GEPA And ReAct Best-Practices Deep Dive

Date: 2026-05-19

## Question

Could GEPA and ReAct-style DSPy programs add meaningful value to this clinical extraction project, especially for seizure-event attribution, temporal reasoning, evidence support, and schema-level assignment?

## Sources Reviewed

Local project sources:

- `docs/outline.md`
- `docs/prior_prompt_error_analysis_synthesis.md`
- `docs/previous_gan_frequency_error_analysis.md`
- `docs/exect_section_aware_ablation_design.md`
- `docs/qwen_dspy_latency_policy.md`
- `docs/qwen_local_latency_experiment_20260518.md`
- `src/clinical_extraction/programs/gan_frequency_s0.py`
- `src/clinical_extraction/experiments/config.py`
- `scripts/run_experiment.py`

External primary sources:

- DSPy optimizer docs: https://dspy.ai/learn/optimization/optimizers/
- DSPy GEPA API docs: https://dspy.ai/api/optimizers/GEPA/overview/
- DSPy GEPA tutorial overview: https://dspy.ai/tutorials/gepa_ai_program/
- DSPy structured-information-extraction GEPA tutorial: https://dspy.ai/tutorials/gepa_facilitysupportanalyzer/
- DSPy ReAct API docs: https://dspy.ai/api/modules/ReAct/
- DSPy RAG-as-agent tutorial: https://dspy.ai/tutorials/agents/
- DSPy paper: https://arxiv.org/abs/2310.03714
- GEPA paper: https://arxiv.org/abs/2507.19457
- Instruction optimization for tabular fact verification: https://arxiv.org/abs/2602.17937

Local environment check:

- `uv run python -c "import dspy; ..."` reports DSPy `3.2.1`.
- `dspy.GEPA`, `dspy.ReAct`, and `dspy.SIMBA` are available in the repo environment.

## Best-Practice Takeaways

### 1. Treat DSPy as program design, not prompt gardening

The core DSPy guidance is to define modules, metrics, and train/dev examples, then compile or optimize the program against the metric. This matches the project outline: program variants such as direct extraction, section-aware extraction, extract-verify-repair, and context-injected extraction are the right unit of experiment. Prompt-only edits should remain subordinate to named program variants and reproducible configs.

Implication for this repo: keep every GEPA/ReAct exploration behind an explicit `program_variant`, stable scorer mode, and run artifact. Do not let optimizer-discovered instructions quietly redefine benchmark semantics.

### 2. Use the simplest optimizer that matches the failure mode

The DSPy docs recommend starting with few-shot optimizers when data is small, moving to random-search or MIPROv2 when there is more data and budget, and using GEPA when textual feedback can explain why a trace failed. Our current state already validates that progression:

- BootstrapFewShot helped the synthesis-backed Gan S0 path when evidence was included in the optimizer metric.
- Hand-authored long prompt/example bundles created negative interactions and runtime pressure.
- Local Qwen latency tests show visible ChainOfThought plus BootstrapFewShot is too slow and fragile for routine Qwen3.6:35b work.

Recommended rule: use `BootstrapFewShot` for cheap demo selection, use `GEPA` for instruction refinement from rich failure feedback, and only use MIPROv2/SIMBA/ReAct optimization when the program architecture genuinely needs multi-step or tool behavior.

### 3. GEPA is strongest when the metric returns diagnostic text

GEPA uses execution traces plus natural-language feedback to mutate instructions. The GEPA docs emphasize predictor-level feedback, Pareto candidate selection, logging, and a strong reflection LM. The structured information extraction case study is especially relevant: a three-module classifier improved from about 75.4% to 86.1% after GEPA, and the learned prompt became packed with boundary rules, exclusions, allowed-label constraints, and examples.

That is close to our problem shape. Gan and ExECT failures are not generic "the model is dumb" errors; they are policy-boundary errors:

- Gan: 6-month seizure-free threshold, year-to-date denominators, quarter-as-window versus quarter-as-unit, clusters, multiple seizure types, abstention boundaries, and exact quote support.
- ExECT: benchmark-facing label granularity, diagnosis versus seizure-type leakage, single seizure not becoming epilepsy, current versus planned/historical medications, and evidence support.

GEPA should be a strong fit because our deterministic scorers and error taxonomies can produce feedback such as: "The label used `seizure free` but the seizure-free period is under 6 months, so the benchmark expects a period rate," or "The prediction found a per-cluster count but dropped the cluster-period component."

### 4. ReAct should be a targeted architecture, not the default extractor

DSPy ReAct exposes a loop that alternates thought, tool choice, tool args, observation, and final output. DSPy's RAG-agent tutorial shows that optimizing a ReAct agent can improve recall substantially, but it also makes clear that tool-use agents need careful tracing, optimization, and cost control. A 2026 fact-verification study found instruction optimization improves ReAct behavior, but ReAct agents need careful optimization and can waste calls unless the optimizer teaches more direct tool-use paths.

For this project, ReAct is not attractive as the default full-schema extractor. It is attractive for a bounded, hard subproblem where tools can deterministically answer questions the model currently fumbles:

- retrieve candidate seizure-event sentences
- normalize dates and relative durations
- build an event timeline
- compute frequency denominators
- check candidate labels against Gan canonical forms
- verify exact evidence quotes and offsets
- map extracted facts to schema levels

The agent should have a small action space and a low `max_iters`, and it should produce a final Pydantic-compatible object. The tools should do deterministic computation or retrieval, not outsource open-ended clinical judgment to more LLM calls.

### 5. Optimize the boundary instructions, keep deterministic contracts outside the model

The strongest local evidence says compact benchmark-contract guidance works better than sprawling prompt walls. The synthesis-backed Gan bootstrap improved capped normalized-label accuracy and evidence support while preserving schema validity. The Qwen full-validation analysis shows the remaining Qwen3.6:35b failures are canonicalization and abstention problems, not output budget problems.

Recommended split:

- Let DSPy/GEPA optimize wording around clinical and annotation-policy boundaries.
- Keep canonical label parsing, forbidden surface detection, evidence offset validation, and schema validation deterministic.
- Let ReAct call deterministic tools for temporal arithmetic or candidate-event structuring.
- Do not ask an optimizer to "learn" scorer semantics that can be encoded directly and tested.

## Case-Study Overlap

### GEPA structured IE tutorial

The DSPy structured IE tutorial uses separate modules for urgency, sentiment, and categories, then adds predictor-level feedback. The optimized category prompt learns rules that look like our desired prompts: strict evidence only, allowed categories only, examples of misleading phrases, and exclusion rules.

Project overlap:

- ExECT field families map naturally to separate predictors: diagnosis, seizure type, medication.
- Gan label selection can be decomposed into event detection, temporal policy, label normalization, and evidence quote selection.
- GEPA feedback can target the exact predictor that failed, instead of mutating a monolithic prompt.

### GEPA paper

The GEPA paper frames the optimizer as learning high-level rules from trajectories, tool outputs, and textual reflection, often with fewer rollouts than scalar-reward optimization. This matters for this repo because clinical extraction labels are scarce, full-validation runs are expensive, and failure explanations are rich.

Project overlap:

- We have strong textual diagnostics from audits and error reads.
- We can generate textual feedback from deterministic scorer failure categories.
- We need auditable prompt evolution rather than opaque reinforcement learning.

### ReAct/RAG-agent DSPy tutorial

The ReAct agent tutorial shows a tool loop can be optimized with MIPROv2 and inspected through call history. The score improvement is meaningful, but the setup has additional complexity: tool definitions, trajectories, optimization cost, and save/load state.

Project overlap:

- ReAct could help when the extraction answer depends on multiple intermediate lookups or calculations.
- The strongest candidate is Gan temporal reasoning, not broad ExECT extraction.
- The agent trajectory can become an error-analysis artifact if we save tool calls and observations.

### Tabular fact-verification instruction optimization

The 2026 fact-verification study is not clinical, but it is a useful cautionary analogy. It compares direct prediction, CoT, ReAct with SQL tools, and CodeAct with Python execution, and finds that ReAct can be competitive but needs careful instruction optimization; optimizers can also teach agents to avoid unnecessary tool calls.

Project overlap:

- Our temporal reasoning problem resembles fact verification over semi-structured evidence.
- Tool use should be measured against direct extraction, not assumed superior.
- Tool-call count, latency, and avoidable calls should be tracked as first-class metrics.

## Recommended Project Opportunities

### Opportunity A: GEPA for Gan S0 direct-extraction instructions

This is the best first GEPA experiment.

Hypothesis: GEPA with rich deterministic feedback will improve Gan S0 direct extraction on temporal-window and canonical-label failures over the current compact synthesis prompt, without increasing prediction-time prompt size as much as manually expanded examples.

Why it fits:

- Gan has a narrow label space.
- The current scorer can already identify invalid labels and category errors.
- Existing error reads supply high-quality textual failure categories.
- `dspy.GEPA` is available in DSPy 3.2.1.

Needed implementation:

- Add `OptimizerConfig.name = "GEPA"` alongside `BootstrapFewShot`.
- Add a GEPA feedback metric with signature `(example, pred, trace=None, pred_name=None, pred_trace=None)`.
- Return both score and feedback. Feedback should name failure categories: exact mismatch, pragmatic mismatch, invalid format, missing evidence, unsupported quote, short seizure-free period incorrectly labeled, year-to-date denominator error, cluster-period dropped, forbidden unit, ambiguous abstention.
- Save GEPA logs, candidate programs, selected instruction, and detailed results under run artifacts.
- Start with GPT 4.1-mini or GPT 5.5 as reflection LM and task LM, not Qwen3.6:35b.

Risk controls:

- Keep benchmark scorer unchanged.
- Use validation only after a capped dev/validation diagnostic.
- Compare to current synthesis BootstrapFewShot and Qwen direct baselines.
- Track prompt length and prediction seconds per record.

### Opportunity B: GEPA for ExECT S0/S1 section-aware field families

This is the second-best GEPA target.

Hypothesis: GEPA predictor-level feedback can reduce ExECT diagnosis/seizure-type leakage and benchmark-label-policy drift in a section-aware field-family architecture.

Why it fits:

- The structured IE GEPA tutorial closely resembles this multi-predictor setup.
- ExECT failures are often field-family-specific.
- Section-aware architecture already exists as a planned/implemented variant.

Needed feedback:

- For diagnosis predictor: no diagnosis from a single seizure event; no diagnosis subtype inferred only from seizure-type wording; preserve audited diagnosis specificity.
- For seizure-type predictor: no seizure type from diagnosis alone; no separate secondary-generalization label unless independently current; preserve audited benchmark surfaces.
- For medication predictor: exclude planned, previous, stopped, or historical medications; require exact evidence.

Risk controls:

- Do not widen beyond S0/S1 while optimizing architecture.
- Keep the deterministic ExECT scorer and label-policy audit fixed.
- Treat GEPA output as a candidate prompt artifact requiring inspection before full validation.

### Opportunity C: ReAct temporal-reasoning probe for Gan hard cases

This is promising, but should be a probe, not the immediate mainline.

Hypothesis: A ReAct module with deterministic temporal and label-validation tools will improve hard Gan cases involving multiple seizure events, seizure-free intervals, cluster patterns, and year-to-date windows compared with direct extraction.

Candidate tools:

- `find_frequency_mentions(note_text) -> list[span]`: deterministic sentence/regex candidate retrieval.
- `extract_temporal_anchors(note_text, clinic_date=None) -> list[anchor]`: dates, months, relative durations, "since", "last", "year to date".
- `compute_elapsed_months(start, end) -> int | None`: deterministic calendar math.
- `canonicalize_gan_label(candidate) -> normalized | error`: existing Gan parsing/scoring utilities.
- `validate_cluster_format(label) -> ok/error`: ensure both cluster period and per-cluster count are present.
- `quote_lookup(note_text, text) -> offsets | null`: exact evidence support.

Recommended shape:

- `dspy.ReAct("note_text -> seizure_frequency_number, evidence_text", tools=[...], max_iters=4 or 6)`
- Run only on hard-case slices first, not full validation.
- Compare direct-vs-ReAct on matched cases: hard temporal, cluster, recent seizure-free conflict, year-to-date, multi-type frequency.
- Track tool-call count, invalid-label rate, evidence support, exact/pragmatic match, and latency.

Risks:

- ReAct may over-call tools and become slower than useful.
- Tool observations can distract the model if too verbose.
- If tools are just thin wrappers around LLM reasoning, the architecture adds little.
- Pydantic/schema output can become fragile unless the final answer is constrained.

### Opportunity D: ReAct or ProgramOfThought for deterministic schema-level assignment

This is worth exploring after Gan S0 and ExECT S0/S1 are stable.

Hypothesis: A tool-assisted module can assign extracted details to schema levels by explicitly comparing event/entity candidates against schema contracts.

Candidate use case:

- Build candidate facts first.
- Use deterministic schema-level rules to decide S0/S1/S2/S3/S4 eligibility.
- Ask a small agent to resolve only ambiguous multi-event assignments, with tools exposing schema definitions and already extracted candidates.

This should not come before the simpler field-family and temporal probes. The schema-level surface is too broad for a first ReAct experiment.

## Proposed Experiment Sequence

### Experiment 1: Gan S0 GEPA feedback metric on GPT 4.1-mini

Dataset/split: Gan development for optimization, capped validation for diagnostic evaluation.

Program variant: `gan_frequency_s0_direct_single_pass`.

Fixed controls:

- scorer: `gan_frequency_deterministic_v1`
- structured output: current Pydantic/JSON strategy
- prompt basis: current synthesis guidance
- no ReAct
- no visible ChainOfThought for Qwen-bound runs

Success criteria:

- Schema-valid prediction rate does not regress.
- Evidence quote support stays high.
- Invalid-label count decreases.
- Normalized-label exact and pragmatic category improve on capped validation.
- GEPA-generated instruction is auditable and not bloated.

### Experiment 2: Gan hard-case ReAct probe

Dataset/split: curated hard-case slice from prior Gan error analysis.

Program variant: new `gan_frequency_s0_react_temporal_tools`.

Fixed controls:

- same scorer and schema
- same model as direct comparison
- deterministic tools only

Success criteria:

- ReAct beats direct extraction on hard temporal/window cases.
- Tool-call count remains bounded.
- No schema-validity or evidence-support collapse.
- Improvements survive a second random hard-case slice.

### Experiment 3: ExECT S0/S1 GEPA section-aware optimization

Dataset/split: ExECT validation cap first.

Program variant: `exect_s0_s1_field_family_section_aware`.

Fixed controls:

- audited S0/S1 field families only
- same deterministic scorer
- same sectioning context policy

Success criteria:

- Fewer diagnosis/seizure-type false positives from cross-family leakage.
- Equal or better micro F1.
- Evidence quote support remains stable.

## Recommendation

Use GEPA soon. It aligns unusually well with the project because this repo already has what GEPA needs: deterministic scorers, concrete error categories, benchmark policy audits, and small-but-meaningful train/dev splits. The first production-quality addition should be a GEPA optimizer path for Gan S0 direct extraction with rich textual feedback.

Use ReAct selectively. The highest-value ReAct experiment is not a broad "clinical reasoning agent"; it is a bounded temporal-reasoning agent for Gan hard cases, with deterministic tools for candidate retrieval, calendar math, canonical label validation, and quote support. If that probe works, the pattern can later generalize to schema-level assignment and ExECT multi-event reasoning.

Do not make visible ChainOfThought, BootstrapFewShot, or ReAct the default for Qwen3.6:35b. The local latency artifacts show direct structured extraction is the right routine path for the 35B local model, while optimizer-heavy and agentic paths should be developed on faster/hosted models, then distilled into compact instructions or deterministic tooling for local runs.
