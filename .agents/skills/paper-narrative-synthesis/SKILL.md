---
name: paper-narrative-synthesis
description: Use when converting this project's research material into a paper narrative, outline, manuscript section, abstract, introduction, methods, results, discussion, or revision plan. Trigger when the user wants to turn experiments, methods, results, error analyses, project design decisions, Kanban work, or research notes into a coherent publishable argument while preserving traceability, rigor caveats, and open weak points.
---

# Paper Narrative Synthesis

Use this skill to transform accumulated project work into a paper-shaped argument. The goal is not polished prose alone; the goal is a defensible narrative structure that exposes where the research story is strong, where it is under-evidenced, and what must be looped back into experiments or exposition.

Use alongside `research-synthesis` for artifact-grounded writeups, `research-supervisor-review` for repo-level judgment, and dataset/scorer skills when claims depend on benchmark semantics.

## Starting Context

Read the minimum set needed for the requested paper task:

1. `docs/current_research_program.md`
2. `docs/component_ceiling_registry.md`
3. `docs/planning/kanban_plan.md`, if present
4. `docs/outline.md` as original proposal context when needed
5. recent synthesis, experiment, error-analysis, or workstream docs relevant to the paper claim
6. `docs/experiments/synthesis/program_variant_registry.md` and registry
   summaries when discussing experiments
7. dataset audits before making dataset, label, scorer, or benchmark claims:
   - `docs/datasets/exect/exect_gold_label_audit.md`
   - `docs/datasets/gan/gan_2026_label_audit.md`
8. policy docs that affect interpretation, especially scorer semantics, splits, deterministic foundations, and published benchmark metrics

Read `references/paper_argument_map.md` when building a full outline, introduction, discussion, or paper-wide revision plan.

## Workflow

1. Define the target artifact:
   - paper outline
   - thesis statement and contribution framing
   - section draft
   - argument map
   - weak-point-driven revision plan
2. Extract the raw material:
   - research question
   - datasets and splits
   - methods and pipeline variants
   - deterministic components and typed primitives
   - models/providers
   - scorer modes and normalization rules
   - metrics and error analyses
   - negative results, pivots, and design decisions
3. Build the claim ladder:
   - background problem
   - concrete gap
   - method or system contribution
   - empirical result
   - interpretation
   - limitation
   - next work
4. Separate manuscript claims into:
   - `Supported`: backed by artifacts, runs, tests, or docs
   - `Plausible`: coherent but needs clearer evidence
   - `Expository`: true enough but not yet explained well
   - `Risky`: currently overclaiming or methodologically weak
5. Draft the narrative around decisions, not chronology.
6. Preserve traceability with file paths, run IDs, configs, splits, model names, scorer modes, and metric caveats.
7. End with a revision loop: the smallest writing or experiment steps that would most improve the paper.

## Narrative Heuristics

- Prefer a single central thesis over a catalog of project work.
- Treat engineering architecture as methodology only when it changes validity, reproducibility, or interpretability.
- Explain why deterministic structure and LLM stages are combined, not just that they are.
- Tie each experiment to the decision it was meant to inform.
- Use negative results and pivots to strengthen the story of methodological control.
- Do not hide dataset quirks; convert them into threats to validity, design constraints, or benchmark-policy discussion.
- Avoid claiming clinical usefulness unless the evidence supports the downstream decision context.
- Avoid comparing results across changed scorer semantics unless the text explicitly says the comparison is diagnostic rather than benchmark-equivalent.

## Paper Skeleton

Use this default structure unless the target venue or user request implies a different one:

```markdown
# Working Title

## Thesis
One paragraph stating the paper's core claim and why this project is the right evidence for it.

## Contributions
- ...

## Argument Map
1. Problem and gap
2. Dataset and benchmark constraints
3. Method design
4. Evaluation design
5. Results and error analysis
6. Interpretation and limitations

## Section Plan
### Introduction
### Related Work
### Data and Benchmark Policy
### Methods
### Experiments
### Results
### Discussion
### Limitations
### Reproducibility

## Weak Points To Resolve
| Weak point | Why it matters | Evidence needed | Smallest next action |
| --- | --- | --- | --- |
```

## Completion Criteria

Before finishing, include:

- the drafted outline, section, argument map, or revision plan
- artifacts inspected
- claims that are supported, plausible, expository, or risky
- dataset, split, model/provider, schema level, program variant, scorer mode, and metric caveats where applicable
- the highest-value next revision loop
