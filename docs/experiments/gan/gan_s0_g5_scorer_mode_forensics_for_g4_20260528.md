# Gan S0 G5 Scorer-Mode Forensics For G4

Status: current synthesis / G4 follow-up input
Date: 2026-05-28
Related cards: G5 - Gan Paper-Scorer Rescore Pack; G4 - Gan Explicit Reason-Code Adjudicator

## Research Question

What does the G5 paper-versus-canonical scorer divergence reveal about the next
Gan S0 adjudicator follow-up, and why should future G4-style selectors carry
explicit reason codes rather than only emit a final seizure-frequency label?

## Motivation

G5 made the paper-facing scorer surface available for current synthetic Gan S0
baselines. The headline result is easy to flatten into a single table: builder
gap GPT stays strongest under the paper scorer, while D1 v1.2b loses more
ground than it does under the canonical scorer.

The deeper signal is not the aggregate drop by itself. The important question is
whether scorer divergence is random numeric noise, broad label-construction
failure, or a specific benchmark target-selection problem. This matters because
the G4 line is supposed to adjudicate target selection, label construction, and
unknown/no-reference policy separately.

## Source Artifacts

- `docs/experiments/gan/gan_s0_g5_paper_scorer_rescore_pack_20260528.md`
- `docs/experiments/gan/gan_s0_g5_paper_scorer_rescore_pack_20260528.json`
- `archive/runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z/predictions.json`
- `archive/runs/gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z/predictions.json`
- `runs/gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini_20260528T074900Z/predictions.json`
- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md`

## Method

This was a post-hoc per-record inspection of the same stored synthetic
validation predictions rescored in G5. No model calls, scorer changes, loader
changes, split changes, prompt edits, or prediction repairs were made.

For each baseline, each validation prediction was scored under:

- `gan2026_paper_reproduction`, with repair, prediction-range credit, and error
  tolerance all disabled.
- `gan_frequency_deterministic_v1`, the canonical project diagnostic scorer.

The inspection then cross-tabbed monthly-frequency match status under the two
scorer modes and grouped scorer-discordant records by coarse label family:
`simple_rate`, `multiple`, `cluster`, `seizure_free`, `unknown`, and
`no_reference`.

Primary gold remains
`check__Seizure Frequency Number.seizure_frequency_number[0]`. `reference[0]`
is a secondary cross-check and difficulty signal only.

## Aggregate Result From G5

| Baseline | Paper monthly | Canonical monthly | Paper-canonical monthly | Valid paper/canonical |
| --- | ---: | ---: | ---: | ---: |
| Builder-gap v1 GPT | 79.9% | 80.6% | -0.7pp | 299/299 |
| Builder-gap v1 Qwen | 70.2% | 70.7% | -0.5pp | 299/297 |
| D1 v1.2b schema guard GPT | 76.6% | 79.9% | -3.3pp | 299/298 |

The aggregate table says D1 is still a useful mechanism baseline, but it is more
sensitive to paper-scorer semantics than builder-gap GPT. That is the symptom,
not the diagnosis.

## Scorer-Discordance Cross-Tab

Counts below compare monthly-frequency correctness under canonical and
paper-reproduction scorer views on the same records.

| Baseline | Both correct | Both wrong | Canonical only correct | Paper only correct | Canonical invalid |
| --- | ---: | ---: | ---: | ---: | ---: |
| Builder-gap v1 GPT | 237 | 56 | 4 | 2 | 0 |
| Builder-gap v1 Qwen | 206 | 85 | 4 | 4 | 2 |
| D1 v1.2b schema guard GPT | 224 | 56 | 14 | 5 | 1 |

The D1 row is the important one for G4. D1 does not have more "both wrong"
records than builder-gap GPT; both have 56. The extra paper-scorer loss is
mostly scorer-discordant, not a general extraction collapse.

## Discordance Families

### Builder-gap v1 GPT

Canonical-only correct:

| Gold family | Prediction family | Count |
| --- | --- | ---: |
| `seizure_free` | `no_reference` | 3 |
| `simple_rate` | `multiple` | 1 |

Paper-only correct:

| Gold family | Prediction family | Count |
| --- | --- | ---: |
| `simple_rate` | `simple_rate` | 1 |
| `unknown` | `no_reference` | 1 |

### Builder-gap v1 Qwen

Canonical-only correct:

| Gold family | Prediction family | Count |
| --- | --- | ---: |
| `simple_rate` | `multiple` | 2 |
| `cluster` | `cluster` | 1 |
| `seizure_free` | `no_reference` | 1 |

Paper-only correct:

| Gold family | Prediction family | Count |
| --- | --- | ---: |
| `simple_rate` | `multiple` | 3 |
| `simple_rate` | `simple_rate` | 1 |

Canonical-invalid examples were malformed surfaces: `q2 - 3wk` and
`many per month`. The paper-reproduction scorer accepted them under its
compatibility behavior; that is a scorer-mode difference, not evidence that the
canonical parser should be loosened by default.

### D1 v1.2b Schema Guard GPT

Canonical-only correct:

| Gold family | Prediction family | Count |
| --- | --- | ---: |
| `seizure_free` | `no_reference` | 14 |

Paper-only correct:

| Gold family | Prediction family | Count |
| --- | --- | ---: |
| `unknown` | `no_reference` | 2 |
| `unknown` | `simple_rate` | 1 |
| `simple_rate` | `simple_rate` | 1 |
| `cluster` | `simple_rate` | 1 |

D1's canonical-only set is not mixed. All 14 cases are seizure-free gold labels
predicted as `no seizure frequency reference`.

## What This Is Telling Us

The main signal is a special-class target-selection problem, not a general
numeric conversion problem.

Builder-gap GPT is robust across scorer views: its paper monthly score is only
0.7pp below its canonical monthly score, and only six records flip between the
two scorer modes. That suggests the promoted baseline is not leaning heavily on
a scorer-specific loophole.

D1 is different. Its paper monthly score is 3.3pp below its canonical score, but
the cross-tab shows the drop is concentrated in scorer-discordant records. D1
has the same number of records that are wrong under both scorers as builder-gap
GPT, but it has 14 canonical-only correct records, all of the same family:
`seizure_free` gold predicted as `no seizure frequency reference`.

That means D1 is often detecting the broad clinical state "no current seizures"
but failing the benchmark-facing distinction between:

- a seizure-free duration statement, such as `seizure free for multiple month`;
  and
- absence of seizure-frequency information, `no seizure frequency reference`.

Those two labels collapse to the same numeric monthly value under the canonical
project scorer because both imply 0 seizures/month. They do not collapse under
the paper-reproduction scorer, where `no seizure frequency reference` follows
the author evaluator's unknown-like special-class behavior, while seizure-free
labels remain currently-no-seizure frequency statements.

So the paper-scorer penalty is doing something useful: it exposes that D1 is
not preserving the benchmark target semantics for seizure-free statements. The
canonical scorer is still clinically interpretable as a monthly-rate diagnostic,
but it is too forgiving for this specific benchmark-facing target-selection
decision.

## Why This Happens

The two scorer modes answer different questions.

`gan_frequency_deterministic_v1` asks whether the predicted and gold labels
convert to the same project-canonical monthly frequency. In that view,
seizure-free and no-reference labels both map to 0 seizures/month.

`gan2026_paper_reproduction` asks whether the prediction is compatible with the
author-provided evaluator. In that view, paper special-class policy matters:
`unknown` and `no seizure frequency reference` are treated together, while
seizure-free labels remain no-current-seizure frequency statements. This makes
`seizure free for multiple month` versus `no seizure frequency reference` a
benchmark-relevant distinction even when the monthly value is 0 in the
canonical diagnostic view.

The smaller flips around `multiple`, day/week constants, cluster conversion, and
malformed Qwen surfaces are real, but they are not the dominant D1 pattern. For
G4, the highest-value design response is not broad deterministic repair. It is
explicit adjudication of special-class target semantics.

## Implications For G4 Follow-Up

Any G4 follow-up should make the target-selection reason explicit before it
emits the final benchmark-facing label.

Recommended reason-code dimensions:

- `frequency_present_quantified`: a current quantified frequency is present.
- `seizure_free_duration`: the target is a seizure-free duration statement.
- `seizures_referenced_frequency_unclear`: seizures are referenced but the
  frequency is not interpretable.
- `no_seizure_frequency_reference`: no seizure-frequency information is present.
- `cluster_spacing_unknown`: seizures per cluster are present but cluster
  spacing is unknown.
- `malformed_or_unsupported_surface`: the candidate label cannot be parsed under
  the active scorer contract.

Any follow-up should store at least these fields separately:

- selected candidate reference and candidate index;
- selected candidate evidence text;
- target-selection reason code;
- label-construction inputs, including numerator, denominator, unit, cluster
  count, seizures per cluster, special-label flag, and source candidate;
- final benchmark-facing label;
- scorer-discordance flags for canonical-only and paper-only correctness.

The key design rule is: do not let a final label hide whether the model chose
the wrong target or constructed the right target incorrectly. In this analysis,
D1's major paper-scorer gap is mostly target semantics, not arithmetic.

## Deterministic Repair Boundary

These findings do not justify a deterministic postprocessor that rewrites
`no seizure frequency reference` into seizure-free, or vice versa. That decision
requires reading the note and selecting the right clinical target.

Narrow surface repair can still be appropriate for one-to-one malformed labels,
but special-class confusions are semantic. They belong in G4 adjudication,
verifier logic, prompt examples, or explicit reason-code comparison, not in a
blind scorer-side repair.

## G4 Reference Checklist

When reviewing or extending G4, check that the report:

- compares both `gan2026_paper_reproduction` and
  `gan_frequency_deterministic_v1` on the same records;
- reports scorer-discordant records, not only aggregate monthly accuracy;
- stratifies special labels separately from numeric rate labels;
- separates candidate coverage, target selection, label construction,
  unknown/no-reference policy, schema validity, and evidence support;
- treats seizure-free versus no-reference as a benchmark-facing target-selection
  decision;
- preserves `seizure_frequency_number[0]` as gold and uses `reference[0]` only
  as a difficulty signal;
- keeps Real(300)/Real(150) benchmark reporting blocked unless those datasets
  or an explicitly synthetic-only protocol are available.

## Non-Claims And Caveats

- This note is synthetic-validation forensics only; it is not Real(300),
  Real(150), or a published Gan benchmark reproduction.
- It is a post-hoc diagnostic read over stored predictions, not a new model run.
- It does not change scorer semantics.
- It does not promote D1 over builder-gap GPT for paper-facing tables.
- It does not reopen or promote G4 as tested. It gives any G4 follow-up a
  sharper target: preserve special-class target semantics while retaining the
  decomposed date/event payload.
