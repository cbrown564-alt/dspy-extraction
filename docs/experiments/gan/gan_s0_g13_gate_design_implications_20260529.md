# Gan S0 G13 Gate Design Implications

Status: current synthesis / design note
Date: 2026-05-29
Related card: G13 - Gan Isolated Frequency-Content Gate Evaluation and Refinement
Primary artifact: `docs/experiments/gan/gan_s0_g13_frequency_content_gate_report_20260529.json`

## Research Question

How should the G13 frequency-content gate result inform Gan S0 pipeline design
without turning the deterministic candidate builder into an overly complex
shadow extractor?

## Motivation

G13 measured the current deterministic temporal candidate substrate as an
isolated source-level gate over the Gan 2026 synthetic validation split
(`gan_2026_fixed_v1:validation`). The headline result is mixed:

- overall gate accuracy: 244/299 (81.6%);
- quantified-frequency presence recall: 201/203 (99.0%);
- no-reference precision: 10/10 predicted no-reference rows (100.0%);
- unclear-frequency recall: 10/40 (25.0%);
- seizure-free recall: 23/45 (51.1%).

This is useful, but it should not be interpreted as a mandate to keep adding
deterministic rules until the gate becomes a full semantic adjudicator. The
project's current decomposition goal is to provide the LLM with better
structured support while preserving the LLM as the main reader and policy
reasoner for clinically subtle cases.

## Method

The G13 report used no model calls. It reused the current deterministic temporal
candidate substrate and collapsed candidate labels into four gate classes:

- `no_reference`;
- `unknown_unclear_frequency`;
- `seizure_free`;
- `quantified_frequency_presence`.

Gold labels came from
`check__Seizure Frequency Number.seizure_frequency_number[0]`. The Gan audit
distinction between `unknown` and `no seizure frequency reference` remained in
force. `reference[0]` was treated only as a secondary difficulty signal.

Fixed controls:

- no scorer change;
- no loader or split change;
- no benchmark bridge change;
- no prompt or model change;
- no target-selection change;
- no prediction-repair change.

## What The Result Means

The current deterministic substrate is strong as a high-recall support layer.
It almost always surfaces some candidate when a quantified frequency is present.
This is desirable because downstream LLM adjudication should not have to rediscover
every possible rate, cluster, date, and seizure-free option from scratch.

However, the substrate is weak as a final content-state classifier. It often
finds a quantified-looking candidate in notes whose gold label is actually
`unknown` or seizure-free. The problem is not simply missing regex coverage.
The problem is that the correct decision often requires clinical and benchmark
policy reasoning:

- Does a number describe overall seizure frequency, or only burden within a
  cluster?
- Does a trigger-conditioned pattern imply a calendar rate, or is the trigger
  frequency unspecified?
- Is a historical event count superseded by current seizure freedom?
- Is the note truly no-reference, or does it mention seizure activity whose
  frequency is unclear?

These are LLM-facing adjudication questions, not good targets for an expanding
deterministic candidate builder.

## Examples From G13

### Trigger-conditioned pattern over-quantified

`gan_9566`

- Gold: `unknown`
- Gate prediction: `quantified_frequency_presence`
- Candidate labels: `1 per month`; `1 to 2 per 8 week`
- Gold evidence: simple partial seizures happen after lack of sleep, usually
  one to two events after nights with less than five hours of rest.

The deterministic support finds numbers and a time window. But the clinical
interpretation depends on how often the trigger occurs. Without that, the
overall seizure frequency is not safely quantified. This is a good example of
why the LLM should reason over a candidate plus a caveat, rather than receive a
deterministic verdict that the note is quantified.

### Cluster burden without spacing

`gan_10618`

- Gold: `unknown, 4 to 6 per cluster`
- Gate prediction: `quantified_frequency_presence`
- Candidate labels include: `unknown, 4 to 6 per cluster`; `4 to 6 per day`;
  `2 cluster per 2 week, multiple per cluster`
- Gold evidence: four to six short spells grouped together on days when they
  occur.

The right support is to expose the per-cluster burden and explicitly mark that
cluster spacing is unresolved. A deterministic rule that tries to decide the
final rate from partial ingredients risks converting an unclear cluster pattern
into a false calendar frequency.

### Seizure-free evidence drowned by historical/event-like candidates

`gan_13574`

- Gold: `seizure free for multiple year`
- Gate prediction: `quantified_frequency_presence`
- Candidate labels include: `seizure free for multiple year`; `1 to 2 per year`
- Gold evidence: currently in long-term remission, seizure free for years.

The correct seizure-free candidate exists. The error comes from class priority:
the gate treats any quantified candidate as enough to classify the note as
quantified. This again argues against hard deterministic routing. The better
support is to present both candidates with status metadata and let the LLM
decide which one reflects the benchmark target.

### True no-reference is comparatively safe

The gate predicted `no_reference` for 10 rows, and all 10 were correct. This
suggests that a deterministic no-reference fast path may be useful when there
is genuinely no seizure-frequency evidence. But this should stay conservative:
the harder boundary is not predicted no-reference; it is deciding whether
seizure-context notes with unclear frequency should be `unknown` rather than
no-reference or quantified.

## Design Interpretation

The deterministic layer should be a support layer with bounded responsibilities:

1. Surface plausible candidate labels and evidence snippets.
2. Preserve ambiguity rather than resolving it prematurely.
3. Add lightweight metadata that helps the LLM reason:
   - candidate family;
   - evidence span;
   - whether the candidate is trigger-conditioned;
   - whether cluster burden is known but spacing is unknown;
   - whether the candidate is historical, current, or seizure-free;
   - whether the candidate is a direct rate or a derived rate.
4. Avoid final semantic decisions when the distinction depends on policy,
   clinical context, or competing signals.

The LLM should remain responsible for:

- selecting the benchmark target among competing candidates;
- deciding whether trigger-conditioned events are quantifiable;
- distinguishing cluster burden from cluster frequency;
- deciding whether seizure-free status supersedes historical event counts;
- separating `unknown` from `no seizure frequency reference` when seizure
  context exists but frequency is unclear.

## Pipeline Implications

Recommended pipeline posture:

1. Candidate builder remains recall-oriented and bounded.
2. Candidate builder emits structured support, not final gate authority.
3. LLM adjudicator receives:
   - the note or relevant snippets;
   - candidate list;
   - candidate family/status metadata;
   - explicit caveats for trigger-conditioned, cluster-spacing-unknown, and
     seizure-free/conflict cases.
4. The LLM produces the final content class and benchmark label with a reason
   code.
5. Deterministic validation checks schema validity and obvious policy violations
   after the LLM, but does not silently rewrite semantic decisions.

This avoids a fragile path where each G13 error class becomes another regex or
priority rule. That path would likely improve one challenge set while creating
new regressions in target selection, temporal anchoring, and special-class
policy.

## Instruction Implications

Future LLM instructions should emphasize adjudication over mechanical
candidate copying. The useful instruction pattern is:

```text
Use the candidate list as support, not as a menu that must be copied.
First decide the frequency-content state:
1. no seizure-frequency reference,
2. seizure activity mentioned but frequency unclear,
3. seizure-free duration,
4. quantified seizure frequency.

Then choose the benchmark label.
```

For trigger-conditioned events:

```text
Do not convert trigger-conditioned events into an overall calendar frequency
unless the note states how often those trigger-linked seizures occur over a
calendar interval. If events occur only after missed medication, poor sleep,
illness, stress, alcohol, or another trigger, and the trigger frequency is not
specified, use unknown.
```

For clusters:

```text
Separate cluster burden from cluster frequency. If the note gives seizures per
cluster but not how often clusters occur, use "unknown, N per cluster" rather
than inventing a rate per day, week, month, or year.
```

For seizure freedom:

```text
Do not let historical event counts override current seizure-free status. If the
note says the patient is currently seizure-free for a qualifying duration, use
the seizure-free label unless there is current breakthrough evidence after that
interval.
```

For no-reference versus unknown:

```text
Use "no seizure frequency reference" only when the note lacks seizure-frequency
information entirely. Use "unknown" when seizure activity, episodes, clusters,
triggers, or seizure status are discussed but the frequency cannot be
quantified.
```

## Risks If We Overbuild The Deterministic Gate

- The candidate builder becomes a hidden target selector.
- Rule priority starts encoding benchmark policy in scattered places.
- Improvements on `unknown` or seizure-free rows may regress quantified recall.
- Aggregation and temporal anchoring errors become harder to attribute because
  source-level rules have already collapsed ambiguity.
- The LLM receives less useful uncertainty information because the deterministic
  layer has already forced a class.

## Recommended Follow-Up

Do not turn G13 into a deterministic refinement campaign.

Instead, use G13 as a design constraint for G12/G14/G15:

- G12 should define answer-option/support surfaces that preserve raw candidates
  and constructed/aggregate possibilities without requiring exact labels to
  appear in the raw inventory.
- G14 should evaluate temporal anchoring while carrying G13 gate-error caveats,
  so source-level content confusions are not counted as pure date/window
  failures.
- G15 should test an LLM selector/adjudicator that explicitly receives candidate
  support plus ambiguity metadata and is instructed to reason over the content
  class before choosing the final Gan label.

The smallest useful engineering step is to design candidate-support metadata for
LLM adjudication, not to add more deterministic final-class rules.

## Claim Status

This note is current synthesis, not a promoted mechanism. It interprets G13 as
evidence that the deterministic substrate is useful support but not a sufficient
semantic gate. The claim remains tentative until a G15-style LLM adjudicator
uses the support surface and shows whether the LLM can improve unknown,
seizure-free, and quantified-conflict decisions without losing quantified
recall.
