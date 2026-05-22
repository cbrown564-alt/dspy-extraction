# Gan S0 Policy And Hybrid Pipeline Learning Log

Date created: 2026-05-22  
Status: Living research log  
Dataset: Gan 2026 synthetic validation unless otherwise stated  
Primary gold: `check__Seizure Frequency Number.seizure_frequency_number[0]`  
Scorer: `gan_frequency_deterministic_v1`  
Related doctrine: `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`

## Purpose

Gan S0 seizure-frequency extraction is now the project's best controlled playground for testing hybrid deterministic-probabilistic clinical extraction. The task is narrow enough to inspect deeply, but hard enough to expose the key design question:

> Which parts of clinical extraction should be done by deterministic rules, which by LLMs, and which by a staged hybrid pipeline?

This document records policy iterations, candidate-generation designs, prompt-guideline decisions, example strategies, verifier/repair strategies, outcomes, and remaining uncertainty. It should be updated after every meaningful Gan S0 policy change, capped run, full-validation run, or error analysis.

This is not a mechanism-closure document. A failed implementation is an arm result unless a mechanism review explicitly tests multiple reasonable implementations or placements.

## Dataset And Scorer Invariants

- Gan `seizure_frequency_number[0]` is the gold label.
- `reference[0]` is a secondary cross-check and difficulty signal, not alternate gold.
- `unknown` and `no seizure frequency reference` are distinct benchmark categories.
- Raw and normalized exact label match are diagnostics unless an experiment explicitly targets full Label Scheme reproduction.
- Monthly-frequency, Purist category, and Pragmatic category are benchmark-facing under the deterministic Gan scorer.
- Evidence quote support is diagnostic source-grounding unless an experiment defines an evidence-facing optimization objective.
- Scorer semantics should not change during policy iteration unless the change is separately documented and tested.

## Central Research Questions

1. Which candidate answers should be surfaced from the note?
   - Deterministic rules may be precise and auditable but low-coverage.
   - LLM candidate extraction may have broader coverage but can invent denominators or collapse policy distinctions.
   - Hybrid candidate merging may recover coverage but add noise and adjudication burden.

2. What guidelines should the LLM receive?
   - Complete guidelines reduce rare policy errors but can overload the model.
   - Minimal guidelines may preserve robustness on common cases but fail the hard annotation-policy edges.
   - The desired policy may be a compact hierarchy: a few broad rules plus targeted examples.

3. What examples should the LLM receive?
   - Generic few-shot examples help format and stability.
   - The hard cases likely require examples of multi-span temporal aggregation, short seizure-free intervals, cluster spacing ambiguity, and highest-frequency selection.
   - Example choice should be treated as an implementation variant, not a casual prompt edit.

4. How should outputs be verified or corrected?
   - Deterministic correction is safe only for narrow surface repairs.
   - LLM judges can inspect semantics but may over-repair correct labels.
   - A promising pattern is to make the first stage expose candidate answers and ambiguity, then constrain a later adjudicator or verifier.

5. What stage graph is best?
   - Direct extract-only is cheap but collapses all reasoning into one final label.
   - Candidates -> adjudicate currently looks strong.
   - Extract -> verify/repair is sometimes helpful but often confounded by over-repair.
   - Candidate extraction -> ambiguity analysis -> adjudication -> judge remains open.

## Policy Ledger

| Policy / mechanism | Rationale | Implemented as | Outcome so far | Remaining uncertainty |
| --- | --- | --- | --- | --- |
| Canonical Gan surfaces and singular units | Avoid schema-invalid labels and surface fragmentation | Base `GanFrequencyS0Signature`; deterministic label normalization | Mostly stable; invalid outputs now rare | Exact Label Scheme reproduction still much lower than category accuracy |
| `unknown` vs `no seizure frequency reference` distinction | Gan scorer treats these as separate categories | Direct guardrails v2.2 and later policies | Direct Qwen fixed original no-content/unknown slice targets | Verifiers can still over-repair `unknown` to no-reference |
| Six-month seizure-free threshold | Gold often computes a rate for short seizure-free windows instead of using seizure-free label | Direct guardrails, verifier rules, temporal candidate policies | Helped earlier baseline failures; still unstable in Qwen full validation | Some gold labels use `seizure free for multiple month`, so exact duration policy remains nuanced |
| Year-to-date denominator | Gold uses months elapsed since January, not full year | Direct policy and candidate builders | Direct path handles examples like January/February YTD | Verifier previously regressed `9 per month` to `9 per 12 month` |
| Full cluster syntax | Cluster labels require spacing and per-cluster count | Direct policy and deterministic surface bridge boundaries | Direct path can preserve `multiple per cluster` | LLM verifier and adjudicator still sometimes strip or invent cluster spacing |
| Deterministic temporal candidates | Externalize count/window extraction as auditable hints | `gan.frequency.temporal_candidates.v1`; `g2_candidates_adjudicate` arms | Best GPT full monthly arm uses expanded deterministic candidates + single-pass adjudication: 68.1% monthly | Candidate coverage remains low; many severe errors have no candidate |
| Candidate presentation variants | Presentation may change whether the LLM trusts or uses candidates | Prose vs table cap-25/cap-50 sweeps | Table cap-25 +4pp did not replicate on cap-50; mostly label-neutral | JSON/bullets/full validation not closed; presentation may matter for Qwen differently |
| Expanded deterministic builders | Add coverage for recurring weak temporal patterns | `cand_prose_expanded_builders_v1` | GPT full validation F0: 68.1% monthly, +3.0pp vs prior VR anchor | Expanded builders shift errors; they do not solve abstention/current-window policy |
| Verify-repair after extraction | Second pass can catch semantic and evidence errors | Direct verify-repair, temporal-candidates verify-repair, validation ladder | Hosted GPT VR was viable; Qwen verifier over-repaired; expanded-builders VR full validation was 65.8%, below F0 68.1% | Verify-repair placement and policy remain open; current arms do not close the mechanism |
| LLM candidate generation | Test whether LLM can replace deterministic candidate builder | Stage-executor E2/E5 JSON candidate arms | GPT cap-25 LLM candidates underperformed det candidates: 29.2% vs 52.0% monthly | Only one LLM candidate format tested; mechanism remains open |
| Hybrid candidate merge | Combine deterministic precision with LLM coverage | Stage-executor E3 | GPT cap-25 hybrid was between det and LLM-only: 41.7% monthly | Merge policy and candidate schema not searched |
| Evidence span-check as prediction-affecting gate | Prevent ungrounded outputs | Validation ladder V7 and evidence checks | Caused abstention pressure; rejected as tested arm | Diagnostic semantic evidence support remains open |
| v1.4 error-taxonomy policy | Address Qwen overuse of `unknown` and candidate overrides | `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy`; `gan_s0_qwen35b_error_taxonomy_policy_cap25.json` | Config and 25-record slice prepared; not yet run | Need GPT rapid check and Qwen deep evaluation |

## Major Experiments And What They Teach

### Direct Guardrails And Qwen Regression Slice

Artifacts:

- `docs/experiments/gan/gan_s0_qwen_regression_slice_three_way_walkthrough_20260519.md`
- `data/fixtures/gan_s0_qwen_error_regression_slice.json`

What was tested:

- Direct Qwen guardrails v2.2.
- Verify-repair v2.3.
- LabeledFewShot with v2.2.

What we learned:

- Direct guardrails stabilized known policy boundaries: original 10 slice targets were 10/10.
- Direct guardrails still failed all four infrequent quantified-over-`unknown` cases.
- Verify-repair moved all four infrequent cases off `unknown`, but only one was exact and it broke several previously correct cases.
- LabeledFewShot was a stability tweak, not an infrequent-temporal aggregation solution.

Interpretation:

Prompt text alone can encode common policy boundaries, but hard temporal aggregation needs either better candidates, structured intermediate outputs, targeted examples, or constrained verification.

### Temporal-Candidate Pivot

Artifact:

- `docs/experiments/gan/gan_s0_temporal_candidate_pivot_20260519.md`

What was tested or concluded:

- The blocker shifted from schema/evidence/surface repair to temporal window selection.
- The project introduced deterministic temporal candidates as a scaffold for count/window reasoning.

What we learned:

- Hard cases require identifying event mentions, dates, counts, seizure-free intervals, and candidate denominators before final-label selection.
- Direct extraction often avoids overclaiming by saying `unknown`.
- Verifier-only approaches can hallucinate denominators if not given structured candidate evidence.

Interpretation:

The core task should be decomposed. Final-label extraction is too compressed for the hardest records.

### Stage Graph Search

Artifact:

- `docs/experiments/gan/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md`

Fixed controls:

- GPT 4.1-mini.
- Validation cap-25.
- Gan S0 deterministic scorer.

Arms:

- Direct extract-only.
- Extract -> repair.
- Candidates -> adjudicate.
- Extract -> verify -> repair.
- Candidates -> extract -> repair.

What we learned:

- `g2_candidates_adjudicate` led the cap-25 stage-graph grid at 52.0% monthly.
- Verify-repair-oriented graphs tied lower at 44.0% monthly.
- This is an arm-level result, not proof that verify-repair is useless.

Interpretation:

Candidate surfacing before adjudication is a strong current skeleton. It is the best anchor for policy and implementation iteration.

### Candidate-Source Executor Search

Artifact:

- `docs/experiments/gan/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md`

What was tested:

- Deterministic candidates.
- LLM JSON candidates.
- Hybrid deterministic + LLM candidates.
- Optional VR after adjudication.

What we learned:

- Deterministic candidates + LLM adjudication led at 52.0% monthly.
- Hybrid candidate generation was lower at 41.7%.
- LLM-only candidate generation was lower at 29.2%.
- Adjudicate-then-VR was label-neutral on this slice.

Interpretation:

Deterministic candidates are the best tested candidate source, but LLM candidate generation remains open because only one JSON candidate implementation was tested.

### Candidate Presentation

Artifacts:

- `docs/experiments/gan/gan_s0_implementation_variant_gpt_cap25_v1_inspection_20260521.md`
- `docs/experiments/gan/gan_s0_implementation_variant_gpt_cap50_v1_inspection_20260521.md`

What we learned:

- Table presentation beat prose by +4pp on cap-25.
- The advantage disappeared on cap-50: both prose and table were 62.0% monthly.
- Candidate presentation was mostly label-neutral, but not completely.

Interpretation:

Presentation is not closed. The right interface may depend on model, policy density, candidate schema, and whether candidates are soft hints or hard options.

### Expanded Deterministic Builders

Artifacts:

- `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_full_validation_v1_inspection_20260521.md`
- `docs/experiments/gan/gan_s0_expanded_builders_vr_gpt_full_validation_v1_inspection_20260521.md`

What we learned:

- Expanded builders + single-pass adjudication reached 68.1% monthly on GPT full validation.
- This beat the prior temporal-candidates verify-repair anchor by +3.0pp monthly.
- Expanded builders + VR reached 65.8% monthly, improving slightly over pre-expansion VR but below single-pass F0.
- Pragmatic and Purist tradeoffs did not uniformly favor the monthly leader.

Interpretation:

More deterministic candidate coverage helps, but verify-repair placement and objective need more design. The best monthly arm is not necessarily the best category or interpretability arm.

### Qwen 35B Full-Validation Error Taxonomy

Artifact:

- `docs/experiments/gan/gan_s0_qwen35b_20260522_error_taxonomy.md`

Run:

- `gan_s0_expanded_builders_prose_full_validation_qwen35b_ollama_20260522T131822Z`

Results:

- Monthly: 64.4%.
- Purist: 72.8%.
- Pragmatic: 78.9%.
- Evidence quote support: 100.0%.
- Valid predictions: 298/299.

What we learned:

- The bottleneck is semantic policy selection, not schema validity or quote support.
- 47/63 Pragmatic misses are gold frequent, infrequent, or no-seizure-information cases predicted as `unknown`.
- In 9 Pragmatic misses, deterministic candidates contained the gold label but Qwen still overrode or ignored them.
- The model often treats later stability as cancelling a prior counted observation window.

Interpretation:

The immediate next lever is policy/adjudication discipline around `unknown`, seizure-free status, grouped recent events, and candidate override, not another broad generic prompt.

## Current Policy Hypothesis

The current working hypothesis is:

> Gan frequency extraction should use a staged policy where a candidate stage exposes possible count/window/cluster/seizure-free interpretations, and an adjudicator applies a compact hierarchy of Gan annotation rules to select the benchmark-facing label.

The current compact hierarchy should include:

1. If no clinical seizure-frequency content exists, output `no seizure frequency reference`.
2. If seizures are discussed but no count/window or cluster spacing can be interpreted, output `unknown`.
3. Group multiple recent events into the relevant observation window when the note supports a shared denominator.
4. If several current seizure types or event frequencies are stated, choose the most frequent note-supported rate.
5. Counted events followed by "no further events" remain the counted-window label unless seizure freedom is at least 6 months.
6. Seizure-free/no-events language maps to seizure-free/no-information only when the note supports the interval policy.
7. Trigger-conditioned counts without a calendar-time denominator remain `unknown`.
8. Cluster labels require both cluster spacing and per-cluster count; if spacing is unknown but per-cluster count is known, use `unknown, N per cluster`.
9. Candidate overrides require explicit justification from source text.

This hierarchy is partly implemented in v1.4 prompt policy, but the run has not yet been executed.

## Open Design Space

### Candidate Selection

Options to test:

- Deterministic builders only.
- LLM emits candidate labels.
- LLM emits candidate event table, not final labels.
- Deterministic + LLM merge with duplicate and plausibility filters.
- LLM emits multiple possible correct answers plus ambiguity flags; deterministic policy chooses among them.
- Deterministic rules generate candidates, then LLM adds missing candidates only when coverage is low.

Open questions:

- Is low deterministic coverage the main limitation, or is candidate adjudication the main limitation?
- Should candidates be soft hints, hard options, or ranked alternatives?
- Can deterministic rules safely choose among LLM-proposed candidates using monthly value, cluster completeness, and policy flags?

### Guideline Density

Options to test:

- Minimal: broad grouping/highest-frequency/unknown/no-reference rules.
- Medium: broad rules plus cluster and seizure-free threshold.
- Full: current v1.4-style policy block with candidate override discipline.
- Examples-first: short rules plus targeted examples.
- Adaptive: provide extra policy only when deterministic pre-analysis flags ambiguity.

Open questions:

- Does full policy improve hard cases but degrade common cases?
- Can guidelines be moved from prompt prose into structured fields and verifier checks?
- Is Qwen more sensitive than GPT to long policy text?

### Examples

High-value example families:

- Counted events followed by "no further events" but seizure-free interval < 6 months.
- Multiple seizure types where the less severe type is more frequent.
- Year-to-date denominator in January and February.
- Trigger-conditioned events with no denominator -> `unknown`.
- Cluster per-time known vs per-cluster known but spacing unknown.
- Multi-month event aggregation from named months or dated events.
- Seizure-free/no-events interval that should map to no-seizure-information category.

Open questions:

- Should examples be embedded in the main prompt, selected dynamically, or retrieved by failure mode?
- Are examples more useful for candidate generation, adjudication, or verification?
- Can GPT-generated examples transfer to Qwen without overfitting prompt style?

### Verification And Repair

Options to test:

- No verifier: single adjudication.
- Confirm-only judge: check whether the answer follows policy, without repair.
- Judge with enum decision: confirm, reject_to_candidate, reject_to_unknown, reject_to_no_reference, repair_cluster_surface.
- LLM verifier sees candidate table and selected label, not raw note only.
- Deterministic post-checks only for grammar and candidate consistency.
- LLM outputs all possible answers and ambiguity; deterministic selection applies policy.
- LLM first extracts candidates/ambiguities; second LLM adjudicates; deterministic final validation checks grammar and candidate support.

Open questions:

- Is a verifier helpful only when constrained to candidates?
- Can deterministic checks detect candidate override errors without reading the whole note?
- Should correction be prediction-affecting or diagnostic until it proves net benefit?

## Candidate Pipeline Hypotheses To Preserve

These should remain open even if one arm fails:

1. **LLM candidate extraction is open.** E2/E5 failed for one JSON candidate implementation, not for all LLM candidate strategies.
2. **Verify-repair is open.** Some VR arms over-repaired, but adjudicate-then-VR was neutral on one slice and could be useful with candidate-constrained decisions.
3. **Tool-during is open.** One ReAct implementation failed; structured tools or policy calculators may still help.
4. **Examples are open.** LabeledFewShot did not solve infrequent cases, but targeted examples for the exact ambiguity families have not been systematically tested.
5. **Deterministic candidate generation is not enough.** It is the best current default, but low coverage and candidate override failures remain.
6. **Policy compression is open.** We do not yet know whether v1.4's complete guidance or a shorter hierarchy performs better.

## Running Log Entries

### 2026-05-22 - v1.4 Error-Taxonomy Policy Prepared

Context:

Qwen 35B full-validation F0 had high schema validity and evidence support but missed 63 Pragmatic categories, dominated by overuse of `unknown`. The supervisor clarified a broad gold-policy rule: group multiple recent events together; if several separate event frequencies exist, choose the most frequent.

Work completed:

- Added prompt version `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy`.
- Added config `configs/experiments/gan_s0_qwen35b_error_taxonomy_policy_cap25.json`.
- Added slice `data/fixtures/gan_s0_qwen35b_20260522_pragmatic_error_slice.json`.
- Updated `docs/experiments/gan/gan_s0_qwen35b_20260522_error_taxonomy.md`.

Observations:

- Raw Gan generation analyses support the supervisor rule: highest-frequency language appears in 433/1500 analyses; short seizure-free/no-further-event logic appears in 91/1500.
- Deterministic dated-event grouping candidates matched gold in 9/9 full-dataset cases detected by the current builder.
- In the Qwen full-validation errors, 16 Pragmatic misses involved highest-frequency language, 11 involved no-further-events/short seizure-free logic, and 8 involved grouped event-window logic.

Interpretation:

The v1.4 policy patch is justified as a targeted test of the dominant Qwen residuals and known Gan construction policy. It should be evaluated first on the 25-record enriched slice, then with GPT as a fast search model, then with Qwen only if it clears a useful gate.

Caveats:

- The slice is enriched for over-`unknown`; it cannot estimate full-validation performance.
- The raw analyses are generated artifacts and may encode construction-time policy more directly than a model can infer from the letter alone.
- Stronger policy text may create over-quantification regressions on true `unknown` records.

Next steps:

- Run v1.4 policy on GPT 4.1-mini for rapid feedback. (Done)
- Compare v1.4 against v1.1 on the same 25-record slice. (Done)
- If useful, port to Qwen 35B and inspect regressions before full validation.

### 2026-05-22 - G1: Run v1.4 Policy Slice vs v1.1 Baseline on GPT 4.1-mini

Context:
Evaluate the v1.4 error-taxonomy prompt policy (which incorporates supervisor heuristics about grouping recent events, highest-frequency selection, and candidate overrides) on a 25-record slice of Qwen 35b pragmatic-category errors, using GPT 4.1-mini as the rapid search anchor.

Work completed:
Compared the baseline v1.1 prompt against the patched v1.4 policy on the 25-record slice.

Artifacts:
- Config: `configs/experiments/gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_1_slice.json` and `configs/experiments/gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_4_slice.json`
- Run IDs:
  - Baseline v1.1: `gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_1_slice_20260522T215239Z`
  - Policy v1.4: `gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_4_slice_20260522T215246Z`
- Metrics:
  - v1.1 Baseline: Pragmatic Accuracy = 56.0% (14/25), Monthly Accuracy = 24.0% (6/25), Normalized Accuracy = 16.0% (4/25)
  - v1.4 Policy: Pragmatic Accuracy = 56.0% (14/25), Monthly Accuracy = 36.0% (9/25) [+12.0pp], Normalized Accuracy = 28.0% (7/25) [+12.0pp]
- Error analysis:
  Forensics performed on 6 shifting records (3 resolved, 3 regressed):
  - **Resolved (Incorrect -> Correct) [3 cases]**:
    - `gan_13190`: Gold `1 per 5 month`. v1.1 predicted `seizure free for 5 month` (over-abstention/ignored breakthrough event). v1.4 correctly outputted `1 per 5 month`.
    - `gan_14214`: Gold `2 to 4 per month`. v1.1 predicted `unknown` (abstained due to recent short seizure freedom). v1.4 predicted `2 to 4 per month` (correctly calculated over the 1-month observation window).
    - `gan_14881`: Gold `1 per month`. v1.1 predicted `unknown`. v1.4 correctly extracted `1 per month`.
  - **Regressed (Correct -> Incorrect) [3 cases]**:
    - `gan_14689`: Gold `3 per 2 month` (pragmatic: frequent). v1.1 predicted `2 per month` (Matches Pragmatic). v1.4 predicted `2 per 2 month` (NoMatch, pragmatic: infrequent).
    - `gan_15442`: Gold `1 cluster per 4 day, 2 per cluster`. v1.1 predicted `1 cluster per day, 2 per cluster` (Matches Pragmatic). v1.4 regressed to `unknown`.
    - `gan_16750`: Gold `6 per 7 month`. v1.1 predicted `2 per 6 month` (Matches Pragmatic). v1.4 regressed to `unknown`.

Policy / pipeline factor changed:
Prompt policy block (`gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy`).

Fixed controls:
GPT 4.1-mini, g2 candidates-adjudicate architecture, deterministic candidates.

Observations:
- Exact numeric and monthly match accuracy improved significantly (+12.0pp), showing that the policy successfully guides the model to resolve numbers instead of defaulting to unknown.
- Major over-abstention instances on 3 records were fixed.
- However, for extremely complex notes (e.g. fluctuating cluster frequencies or multiple spaced seizure types over long periods), the policy's strictness caused the model to regress to `unknown` or make subtle errors in denominator period matching (e.g. `2 per 2 month` instead of `3 per 2 month`).

Interpretation:
The v1.4 policy resolves severe over-abstention and numbers mismatch errors, but its strictness introduces minor regressions on records with highly complex/fluctuating patterns. Since exact monthly/normalized accuracy increased by 12pp, G2 (Qwen 35b execution) is fully justified.

Caveats:
The 25-record slice is highly enriched for over-abstention and does not estimate full-validation performance.

Decision scope:
Arm search.

Open cells:
Verify whether local Qwen 35B shows similar metric improvements and similar regression tendencies under this policy.

Next steps:
- Run v1.4 policy on Qwen 35B (cap-25 slice) detached and inspect results. (Done)

### 2026-05-22 - G2: Run v1.4 Policy Slice on Qwen 3.6:35b

Context:
Evaluate the transferability of the v1.4 error-taxonomy prompt policy (heuristics on recent event grouping, highest frequency selection, and candidate overrides) to the local Qwen 3.6:35b model using the same 25-record pragmatic-category error regression slice.

Work completed:
Executed the `gan_s0_qwen35b_error_taxonomy_policy_cap25` run configuration on the 25-record slice via local Ollama.

Artifacts:
- Config: `configs/experiments/gan_s0_qwen35b_error_taxonomy_policy_cap25.json`
- Run: `runs/gan_s0_qwen35b_error_taxonomy_policy_cap25_20260522T220226Z/`
- Metrics:
  - Pragmatic Category Accuracy = 20.0% (5/25) [baseline: 0%]
  - Monthly Frequency Accuracy = 16.0% (4/25)
  - Purist Category Accuracy = 20.0% (5/25)
  - Schema Validity = 100.0% (25/25)
  - Evidence Quote Support = 100.0% (25/25)
- Error analysis:
  - Exact String Matches: 2/25 (`gan_14250`, `gan_15302`).
  - Shifting off the default `unknown` label on hard records succeeded.
  - However, in several cases the model regressed by predicting a rate of seizure-freedom when stable short-term instead of the correct rate (e.g. `gan_14214` predicted `seizure free for 1 month` instead of gold `2 to 4 per month`, `gan_14485` gold `2 per 3 month` predicted as `seizure free for 1 month`, and `gan_14821` gold `1 per month` predicted as `seizure free for 1 month`).

Policy / pipeline factor changed:
Prompt policy block (`gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy`).

Fixed controls:
Qwen 3.6:35b, `g2_candidates_adjudicate` architecture, deterministic candidates.

Observations:
- The prompt policy successfully pushed the local model to quantify rather than abstaining with `unknown` on hard cases, but the model over-interpreted brief stability windows (e.g. "no seizures in 4 weeks" following active events) as meaning the patient is seizure-free, rather than calculating the rate of events in the observation period.

Interpretation:
- The Qwen run takes significantly longer than GPT-4.1-mini hosted runs. Since broad experimentation sweeps (density mini-grids, targeted examples, stage-graph variants) are needed to find stable ways to balance rates vs stability windows, all broad experimentation must run exclusively on GPT 4.1-mini first. Qwen 35b is reserved strictly for final transferability and confirmatory checks.

Caveats:
- The 25-record slice is highly enriched for baseline pragmatic error cases and is not a general validation set.

Decision scope:
- Arm search/transferability check.

Open cells:
- Resolve how to balance stability statements against quantified event rates (to be searched on GPT 4.1-mini in G3 and G4).

Next steps:
- Execute G3 (GPT-first) policy-density mini-grid on GPT 4.1-mini.
- Execute G4 (GPT-first) targeted example families on GPT 4.1-mini.

## Update Template


Use this template for future updates:

```markdown
### YYYY-MM-DD - Short Policy Or Pipeline Update

Context:

Work completed:

Artifacts:

- Config:
- Run:
- Metrics:
- Error analysis:

Policy / pipeline factor changed:

Fixed controls:

Observations:

Interpretation:

Caveats:

Decision scope:

Open cells:

Next steps:
```

## Immediate Planning Implications

Before spending more Qwen time, use GPT 4.1-mini to rapidly test:

1. Prompt policy density: v1.1 vs v1.4 vs compact hierarchy.
2. Candidate selection mode: deterministic final candidates vs LLM event-table candidates vs LLM multiple-answer candidates.
3. Verification mode: none vs candidate-constrained judge vs deterministic selector over proposed candidates.
4. Example strategy: no examples vs targeted examples for the top ambiguity families.

Then use Qwen 3.6:35B for deep evaluation of the most informative cells, not broad grid search.

## References

- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/taxonomy/taxonomy_primitive_catalog.md`
- `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`
- `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`
- `docs/experiments/gan/gan_s0_temporal_candidate_pivot_20260519.md`
- `docs/experiments/gan/gan_s0_qwen_regression_slice_three_way_walkthrough_20260519.md`
- `docs/experiments/gan/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md`
- `docs/experiments/gan/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md`
- `docs/experiments/gan/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md`
- `docs/experiments/gan/gan_s0_implementation_variant_gpt_cap50_v1_inspection_20260521.md`
- `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_full_validation_v1_inspection_20260521.md`
- `docs/experiments/gan/gan_s0_expanded_builders_vr_gpt_full_validation_v1_inspection_20260521.md`
- `docs/experiments/gan/gan_s0_qwen35b_20260522_error_taxonomy.md`
