# Gan S0 Qwen 35B Full-Validation Error Taxonomy

Date: 2026-05-22

## Research Question

What prevents `gan_s0_expanded_builders_prose_full_validation_qwen35b_ollama_20260522T131822Z` from reaching the expected Gan S0 benchmark target of 80%+ Purist category accuracy and 90%+ Pragmatic category accuracy?

## Method

Source artifacts:

- Run directory: `runs/gan_s0_expanded_builders_prose_full_validation_qwen35b_ollama_20260522T131822Z`
- Record report: `gan_s0_expanded_builders_prose_full_validation_qwen35b_ollama_20260522T131822Z_record_report.csv`
- Metrics: `metrics.json`
- Errors: `errors.json`
- Predictions: `predictions.json`
- Config: `config.json`
- Prompt metadata: `prompts.json`

Dataset and scorer context:

- Dataset: Gan 2026 synthetic validation split, `gan_2026_fixed_v1:validation`
- Gold label: `seizure_frequency_number[0]`
- `reference[0]`: secondary difficulty signal, not gold
- Schema: `gan_frequency_s0`
- Program: `gan_frequency_s0_temporal_candidates_single_pass`
- Context: full note plus deterministic temporal candidates
- Model/provider: Qwen 35B via Ollama
- Scorer: `gan_frequency_deterministic_v1`
- Evidence support: diagnostic source-grounding check, not benchmark-facing label scoring

## Headline Results

The run is not primarily failing schema validity or evidence support.

| Metric | Value |
|---|---:|
| Predicted records | 299 |
| Valid predictions | 298 |
| Invalid predictions | 1 |
| Raw exact accuracy | 55.7% |
| Normalized-label accuracy | 55.7% |
| Monthly-frequency accuracy | 64.4% |
| Purist category accuracy | 72.8% |
| Pragmatic category accuracy | 78.9% |
| Evidence quote support | 100.0% |

To reach the stated targets on the 298 valid predictions:

- Purist needs about 22 additional correct category decisions.
- Pragmatic needs about 34 additional correct category decisions.

The deficit is therefore dominated by semantic category selection, especially overuse of `unknown`, rather than JSON validity or quote grounding.

## Error Taxonomy

### 1. Diagnostic-only mismatches

These hurt raw or normalized-label exactness but do not hurt monthly, Purist, or Pragmatic category scoring.

| Class | Count | Interpretation |
|---|---:|---|
| Seizure-free label shape mismatch | 13 | Different duration surface, same category |
| Unknown cluster label shape mismatch | 4 | `unknown, N per cluster` collapsed to `unknown`, same category |
| Monthly-match label surface mismatch | 5 | Surface differs but monthly conversion matches |
| Seizure-free to no-reference monthly match | 3 | Both map to no-seizure-information category |
| Cluster label shape mismatch | 1 | Cluster form collapsed to equivalent rate |

These 26 cases should not drive prompt changes if the near-term target is Purist/Pragmatic accuracy. They matter only if the objective is exact Gan Label Scheme reproduction.

### 2. Operational/schema error

One prediction was invalid:

- `gan_5866`: gold `4 per 6 week`, predicted `4 per 6 week, multiple per cluster`

This is a canonical-label grammar error: the model appended a cluster suffix to a non-cluster rate. It is not a major accuracy bottleneck but is a regression-test candidate for label grammar enforcement.

### 3. Pragmatic category errors

There are 63 Pragmatic category mismatches.

| Direction | Count | Meaning |
|---|---:|---|
| Frequent -> unknown | 12 | Quantified current/high-frequency facts lost to abstention |
| Infrequent -> unknown | 22 | Low-frequency or date-window facts lost to abstention |
| No seizure information -> unknown | 13 | Seizure-free/no-current-events misread as unspecified frequency |
| Unknown -> frequent | 8 | Unspecified windows converted into quantified rates |
| Unknown -> infrequent | 1 | Unspecified count converted into low-frequency rate |
| Unknown -> no seizure information | 1 | Unclear seizure frequency treated as seizure-free/no-reference |
| Frequent -> infrequent | 5 | Denominator/window underestimation |
| Infrequent -> no seizure information | 1 | Recent historical count overwritten by seizure-free status |

The largest single pattern is overuse of `unknown`: 47/63 Pragmatic misses are gold frequent, infrequent, or no-seizure-information cases predicted as `unknown`.

### 4. Purist-only or monthly-only errors

Some errors are real but not Pragmatic-breaking.

| Class | Count | Benchmark effect |
|---|---:|---|
| Purist bin boundary within Pragmatic | 17 | Pragmatic correct, Purist wrong |
| Pragmatic match with monthly divergence | 20 | Pragmatic and often Purist still correct, exact monthly wrong |
| Cluster semantic mismatch | 6 | Pragmatic correct, monthly wrong; 1 also Purist wrong |

These explain why monthly-frequency accuracy is much lower than Pragmatic accuracy. They are important for purist improvement and exact reproduction, but less urgent for reaching 90% Pragmatic.

## Mechanistic Failure Modes

### A. Abstention boundary is too conservative

The model often outputs `unknown` when the note contains a usable frequency window. Examples:

- `gan_14485`: deterministic candidate correctly generated `2 per 3 month`, but the model selected `unknown` from the later phrase "no further events reported."
- `gan_13123`: candidate `1 per year`; model selected `unknown`.
- `gan_14881`: candidate `1 per month`; model selected `unknown`.
- `gan_15302`: candidate `1 to 2 per 14 month`; model selected `unknown`.

This is partly bad instruction: the prompt says to choose the highest current quantified seizure-type frequency, but it does not clearly define when a historical count plus "no further events" should remain the answer rather than become `unknown` or seizure-free.

It is also a pipeline flaw: deterministic candidates can contain the gold answer, yet the final adjudicator is free to ignore them without a forced reason, verifier, or candidate-consistency check.

### B. "Current status" is overriding the gold observation window

The model repeatedly treats a later stability statement as cancelling a prior counted event window:

- `gan_14485`: two events in April-July, no further events after July.
- `gan_14250`: two seizures in the following week, then no further seizures.
- `gan_14390`: pair of seizures at medication withdrawal, then stable since.

The instruction gap is that "current" is underspecified. For Gan labels, the gold often preserves the count over the described window even when the patient is now stable. The prompt needs an explicit policy for "counted events followed by no further events."

### C. Seizure-free versus unknown is unstable

Gold no-seizure-information/seizure-free cases are predicted as `unknown` 13 times. The model is treating remission, "no events since last review", or "seizure free for years" as insufficiently quantified rather than as zero-frequency/no-seizure-information.

Examples:

- `gan_13574`, `gan_13598`: gold `seizure free for multiple year`, predicted `unknown`.
- `gan_7872`, `gan_8203`, `gan_8645`: gold seizure-free/no-events interval, predicted `unknown`.

This is instruction-remediable: seizure-free/no-current-events language needs to be explicitly mapped to seizure-free labels when the note gives a duration or review interval.

### D. Unknown is sometimes underused when the denominator is not actually known

The opposite error also appears:

- `gan_9566`: gold `unknown`, predicted `1 to 2 per week` from "one to two events in the morning following nights with less than five hours of rest."
- `gan_14036`, `gan_14081`, `gan_14137`: gold `unknown`, predicted finite rates from counts since treatment/diet changes where the annotation policy treats the window as insufficient.
- `gan_10618`: gold `unknown, 4 to 6 per cluster`, predicted `1 cluster per week, 4 to 6 per cluster`.

This shows the model does not have a stable rule for when a count plus date phrase is enough to define a denominator.

### E. Temporal denominator and calendar-window reasoning remain weak

The model often finds the right kind of evidence but computes the wrong denominator or selects a different window:

- `gan_12871`: gold `5 per 2 month`, predicted `5 per year`.
- `gan_16772`: gold `9 per 5 month`, predicted `9 per 3 month`.
- `gan_2513`: gold `2 to 3 per 2 week`, predicted `2 to 3 per week`.
- `gan_15997`: gold `10 per 3 month`, predicted `8 per 3 month`.
- `gan_1794`: gold `8 per 2 month`, predicted `6 per 2 month`.

This is partly instruction and partly architecture. The current single adjudication call must simultaneously identify the evidence, decide the window, count events, normalize the label, and choose the category. The errors suggest that count/window arithmetic should be externalized or verified.

### F. Cluster/rate distinction is brittle

Cluster errors split into several shapes:

- Plain rate inflated into cluster form: `1 per day` -> `1 cluster per day, multiple per cluster`
- Cluster collapsed to rate: `1 cluster per 2 week, 3 per cluster` -> `3 per 2 week`
- Unknown cluster spacing converted into known cluster rate: `unknown, 4 to 6 per cluster` -> `1 cluster per week, 4 to 6 per cluster`
- Per-cluster count softened to `multiple`: `2 cluster per month, 4 per cluster` -> `2 cluster per month, multiple per cluster`

This looks like a mix of instruction and schema pressure. The model knows the cluster syntax, but it does not reliably decide when "multiple events in a period" is a cluster versus an ordinary count.

### G. Highest-current-frequency selection is not reliably applied

Some frequent cases are undercalled because the model selects a lower-frequency seizure type or a less relevant sentence:

- `gan_16938`: gold `2 per week`; predicted `2 per 2 month` by selecting generalized tonic-clonic seizures rather than the higher current absence frequency.
- `gan_12562`: gold `1 per day`; predicted `4 per week`.
- `gan_12667`: gold `1 per day`; predicted `1 to 2 per month`.

This is an instruction problem that likely needs explicit examples: if multiple seizure types are present, select the highest current epileptic seizure frequency unless the note clearly marks it as historical, non-epileptic, or irrelevant.

### H. Evidence support is now too permissive as a diagnostic

Evidence quote support is reported as 100%, but the artifacts contain repaired evidence spans such as one-word quotes (`They`, `She`) after `truncated_to_note_span` repair. There are 17 truncated evidence repairs, and at least several occur in benchmark-severe errors.

This does not directly lower Purist/Pragmatic scoring, but it weakens the diagnostic value of evidence metrics. A valid offset is not necessarily clinically meaningful evidence for the normalized label.

## Instruction Gaps Not Yet Fully Described

The current synthesis guidance says:

- output canonical Gan labels
- choose the highest current quantified seizure-type frequency
- use full cluster format
- use year-to-date months elapsed since January
- treat a quarter as an observation window
- use seizure-free labels only for seizure freedom of 6 months or longer
- return exact contiguous quotes

The observed errors suggest missing policy text:

1. If a note gives counted events in a defined historical/current window and then says "no further events", preserve the counted-window label unless the note gives a seizure-free interval of at least 6 months.
2. Do not convert "no further events", "stable since", or "no seizures since X" to `unknown`; use seizure-free/no-seizure-information policy when the interval is explicit, or preserve the preceding count if the counted window is the only frequency.
3. Use `unknown` when a count is given without a usable denominator or when a trigger-conditioned phrase does not specify occurrence rate across time.
4. Distinguish "events grouped together when they happen" from "clusters occurring at a known interval"; if cluster spacing is not stated, use `unknown, N per cluster`.
5. When deterministic temporal candidates are supplied, treat them as privileged candidate answers and explicitly justify any override.
6. When multiple seizure types are mentioned, select the highest current epileptic seizure frequency, not necessarily the most severe seizure type or the most recent sentence.
7. Define how dates imply denominators: calendar months between first and last event, year-to-date, since treatment start, since last review, and "last quarter" need separate examples.

## Pipeline Flaws

1. Candidate generation has low coverage. Only 42/298 valid predictions had deterministic temporal candidates. Many denominator/count errors had no candidate context at all.
2. Candidate adjudication is weak. In 9 Pragmatic misses, the deterministic candidate list contained the gold label, but the model overrode it.
3. There is no semantic verifier. The artifact bridge repairs surface forms but does not check whether the selected evidence supports the selected label, denominator, cluster structure, or abstention.
4. Evidence validation checks quote/offset support, not claim support. This allows valid but clinically unhelpful evidence spans to pass.
5. The schema output collapses the final answer into one label without requiring structured intermediate fields such as event count, window count, window unit, current-vs-historical decision, cluster spacing, and per-cluster count.
6. The single-pass adjudicator is carrying too many responsibilities: evidence selection, temporal interpretation, count arithmetic, cluster/rate classification, abstention policy, and canonical formatting.

## Opportunities For Improvement

Highest expected value:

1. Add an abstention and seizure-free policy block with examples for "counted events + no further events", "seizure-free for years", "no events since last review", and "count without denominator".
2. Make deterministic candidates harder to ignore: require the model to either select one candidate or provide a structured override reason from a small enum.
3. Add a verifier/repair pass focused only on benchmark-severe semantic failures: unknown overuse, unknown underuse, seizure-free/no-reference confusion, and candidate override errors.
4. Expand deterministic candidate builders for the exact weak patterns: dated first/last events, "last episode on DATE", "since treatment start", month-by-month calendars, inter-seizure intervals, and cluster spacing/per-cluster phrases.
5. Add structured intermediate fields before final label normalization. The final label should be derived or checked from fields such as `event_count`, `window_count`, `window_unit`, `cluster_count`, and `events_per_cluster`.

Medium expected value:

6. Add few-shot examples for high-current-frequency selection across multiple seizure types.
7. Add cluster/rate examples where repeated events are not clusters, and where cluster spacing is unknown.
8. Tighten evidence diagnostics to require minimum useful quote length and semantic support, not only valid offsets.

Lower immediate value:

9. Improve exact label-surface fidelity for seizure-free duration and unknown cluster labels. This helps raw/normalized label accuracy but not the Purist/Pragmatic target.
10. Add a deterministic grammar repair for non-cluster rates with accidental cluster suffixes. This addresses the one invalid prediction but will not move category accuracy much.

## Interpretation

The supervisor-facing interpretation is directionally right: the model usually finds seizure-frequency-relevant text and can emit valid schema/evidence. The remaining bottleneck is reasoning from relevant text to the annotation-policy-correct canonical label.

However, this run adds two important refinements:

1. The largest failure mode is not general inability to understand frequency expressions. It is policy instability around abstention, seizure freedom, and whether a prior counted window remains the answer when the current status says "no further events."
2. Deterministic temporal candidates help only if the adjudicator is constrained or verified. This run contains cases where the deterministic candidate exactly matches gold and the final model still predicts `unknown`.

The path to 80%+ Purist and 90%+ Pragmatic is probably not another broad LLM call. It is a narrower harness change: stronger policy examples, higher candidate coverage, candidate-aware adjudication, and a focused semantic verifier.

## Caveats

- This is validation-split analysis, not held-out test reporting.
- Evidence support is diagnostic and currently likely overestimates clinically meaningful grounding.
- Some Gan labels reflect construction-time annotation policy rather than a unique clinical truth; `reference[0]` disagreements remain difficulty signals, not alternate gold.
- The analysis is based on Qwen 35B Ollama for this specific program and prompt; model-specific sensitivity may differ for GPT/Gemini.

## Next Experiments

1. Prompt-only policy patch: add the missing abstention/current-window/seizure-free examples and rerun a capped set enriched for the 63 Pragmatic misses.
2. Candidate-override ablation: require selection from deterministic candidates when present unless an explicit override reason is emitted.
3. Candidate-builder expansion: add deterministic builders for "last episode on DATE", "no further events since", month-by-month calendars, inter-seizure intervals, and "since treatment start" counts.
4. Focused verifier: run a cheap second pass only when the prediction is `unknown`, when gold-like candidates exist, or when the label is cluster-shaped.
5. Evidence-support hardening: add a diagnostic semantic-support check and minimum quote-length rule so evidence metrics distinguish valid offsets from useful clinical evidence.

## Implemented Follow-Up Setup

The first next experiment is now codified without changing the frozen model-comparison run or scorer semantics:

- Prompt version: `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy`
- Config: `configs/experiments/gan_s0_qwen35b_error_taxonomy_policy_cap25.json`
- Slice fixture: `data/fixtures/gan_s0_qwen35b_20260522_pragmatic_error_slice.json`

The v1.4 prompt patch targets the taxonomy's dominant residual mode: quantified or seizure-free/no-information gold labels predicted as `unknown`. It adds explicit policy for the supervisor-facing Gan grouping rule: group multiple recent events into the relevant observation window, and when several separate current event frequencies or seizure types are stated, choose the most frequent note-supported rate. It also adds policy for counted windows followed by "no further events", multi-year seizure freedom/no-events language, trigger-conditioned counts without denominators, candidate override discipline, and cluster/rate distinction.

The 25-record slice is selected from the 63 Pragmatic category mismatches in `gan_s0_expanded_builders_prose_full_validation_qwen35b_ollama_20260522T131822Z`. It is a regression gate, not a full-validation claim. Gan `seizure_frequency_number[0]` remains the gold label; `reference[0]` remains a secondary difficulty signal; evidence support remains diagnostic.
