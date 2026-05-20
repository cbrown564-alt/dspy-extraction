# Supervisor Review Rubric

Use this rubric for substantial repository-wide or workstream-level reviews.

## 1. Research Direction

- Is the current work tied to `docs/outline.md` or an explicit later research decision?
- Is the immediate research question clear enough to decide what evidence would count as progress?
- Is the work positioned as benchmark reproduction, benchmark improvement, ablation, infrastructure, downstream adaptation, or research synthesis?
- Is there a plausible paper/thesis claim that this work can eventually support?

## 2. Dataset And Label Fidelity

- Have relevant audits been read before changing loaders, schemas, scorers, or evaluation logic?
- Are raw labels preserved separately from normalized labels where that distinction matters?
- Are ExECTv2 and Gan quirks represented faithfully rather than smoothed into clinical intuition?
- Are unknown, absent, negated, historical, current, planned, and resolved facts distinguished?
- For Gan, is `seizure_frequency_number[0]` treated as the gold label and `reference` as secondary cross-check?

## 3. Scorer And Metric Integrity

- Are scorer semantics explicit, tested, and stable?
- Are changed metric definitions documented before comparing new and old results?
- Do reports state normalization rules, caveats, and scorer mode?
- Do metrics reflect the field's actual difficulty: evidence support, temporality, negation, normalization, and schema validity?
- Are ambiguous gold cases surfaced rather than silently erased?

## 4. Experiment Design

- Is there a named hypothesis?
- Are dataset, split, schema level, DSPy program variant, model/provider, scorer, and artifacts defined before running?
- Is only one factor changed at a time unless testing an interaction?
- Is the baseline reproducible?
- Are failed examples preserved for error analysis?
- Does the run answer a decision, or merely produce another number?

## 5. Reproducibility

- Are configs, prompts, compiled programs, predictions, reports, and run metadata preserved?
- Are random seeds, split IDs, model IDs, provider settings, and local environment assumptions recorded?
- Can another agent rerun the same experiment from committed docs/configs?
- Are Windows/macOS portability assumptions under control?

## 6. Clinical And Evidence Rigor

- Are extracted clinical facts backed by evidence unless explicitly metadata?
- Does evidence support the normalized interpretation, not only a nearby quote?
- Are seizure frequency temporal windows handled carefully?
- Are diagnosis specificity, certainty, and medication current-versus-historical status handled according to benchmark policy?
- Are label-policy differences distinguished from clinical disagreement?

## 7. Scope And Opportunity Cost

- Is this work the smallest thing that reduces the biggest uncertainty?
- Is it unlocking benchmark fidelity, experiment validity, or downstream decision value?
- Is the repo accumulating abstractions without a near-term experiment that uses them?
- Could a smaller test, capped run, or manual audit answer the same question?
- Should the current work continue, narrow, defer, or stop?

## 8. Researcher Development

- Is the user being given decisions they can own rather than just task lists?
- Are recommendations teaching the method: why this matters, what evidence is needed, and what would change the conclusion?
- Is feedback direct enough to prevent drift but specific enough to act on?
- Does the review help the user become less dependent on supervision over time?

## Supervisor Judgment Scale

Use this language when helpful:

- `Green`: aligned, evidenced, and worth continuing.
- `Amber`: valuable but needs tighter scope, tests, documentation, or decision framing.
- `Red`: likely to invalidate comparisons, waste effort, or distract from the core research contribution.

## Suggested Closing

End with the next concrete supervisory instruction, for example:

- "Do not run broader model comparisons until the scorer contract is frozen and tested."
- "Pull the smallest card that validates Gan gold loading against the audit."
- "Write the experiment card before implementing the new DSPy variant."
- "Document the scorer caveat before interpreting this metric."
