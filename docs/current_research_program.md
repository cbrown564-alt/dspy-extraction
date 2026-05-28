# Current Research Program

Status: active guidance
Last updated: 2026-05-28
Supersedes: broad-pipeline-winning as the primary organizing frame

## Core Pivot

The project is now a component decomposition study.

The previous work produced useful operational defaults, but the May 28 Gan and
ExECT deep dives show that the next scientific value is not more broad-stack
polishing. The active research question is:

> What are the independently optimizable clinical extraction components, what
> ceiling can each component reach under frozen scorer and dataset policy, and
> how much performance is lost when optimized components are stacked?

## What Stops Now

- No new broad ExECT schema grids until missing component substrates have
  no-model representability gates.
- No new Gan "better prompt" loops unless the varied factor maps to one of the
  decomposition stages in `component_ceiling_registry.md`.
- No holdout-driven tuning. Holdout results are residual-analysis triggers only.
- No published benchmark claims unless the report uses the explicit benchmark
  scorer and dataset caveats in `policies/published_benchmark_metrics.md`.
- No mechanism closure from a failed arm unless a mechanism-level review says so.

## What Becomes Active

### Gan S0

Gan is a single-label seizure-frequency benchmark, but the task is not just date
math. The active decomposition is:

1. frequency-content gate;
2. candidate inventory;
3. temporal anchoring;
4. scope and benchmark target selection;
5. canonical label construction and aggregation;
6. unknown versus no-reference policy;
7. evidence and schema validation.

Use builder-gap v1 GPT as the synthetic paper-default baseline, but rescore with
`gan2026_paper_reproduction` for direct benchmark-comparison tables. Use D1 v1.2b
as the mechanism baseline because it exposes the most structured date/event
payload without the harmful arithmetic and anchor guardrails.

### ExECT

ExECT is no longer organized around "S1 to S5 gets harder" as the main story.
The clean ladder remains an unoptimized complexity baseline. The active program
is:

1. define benchmark contract and gold policy per family;
2. expose document structure and family spans;
3. build mention, event, and candidate inventories;
4. bridge raw candidates into benchmark-facing labels;
5. optimize within-family adjudication;
6. test pairwise family interactions;
7. rebuild stacked schemas only after isolated ceilings are known.

The immediate ExECT pulls are frequency event/rate payload, S1 raw/bridge/prompt
causal split, medication current-Rx/lifecycle payload, family-span payload, and
a component ceiling registry.

## Active Entry Points

- `README.md`
- `component_ceiling_registry.md`
- `planning/kanban_plan.md`
- `experiments/gan/README.md`
- `experiments/exect/README.md`
- `experiments/synthesis/README.md`

## Evidence Discipline

Experiment notes remain evidence, not guidance. A note becomes current guidance
only when a current index says what decision it supports and with what status:
`promoted baseline`, `mechanism open`, `rejected arm`, `blocked`, or
`superseded`.

## External Claim Discipline

- Gan direct paper comparisons must use `gan2026_paper_reproduction` and report
  repair/range/tolerance options.
- Gan canonical project metrics using `gan_frequency_deterministic_v1` are
  diagnostic or sensitivity views.
- ExECT Table 1 reproduction remains blocked until CUI-aware all-family scoring
  exists.
- Synthetic validation and one-shot holdout are internal research evidence, not
  deployment validation.
