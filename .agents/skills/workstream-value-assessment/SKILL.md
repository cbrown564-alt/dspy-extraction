---
name: workstream-value-assessment
description: Use when stepping back to assess whether a proposed program, goal, feature, experiment, UI, or workstream has real downstream clinical/research value, evidence, and decision relevance rather than being an overbuilt or intellectually interesting distraction.
---

# Workstream Value Assessment

Use this skill when deciding whether a workstream is worth continuing, expanding, pausing, or reframing.

## Workflow

1. State the workstream in one sentence.
2. Identify the downstream use case:
   - benchmark reproduction or improvement
   - clinical support
   - billing extraction
   - research cohort selection
   - outcome variable construction
   - review tooling or reproducibility infrastructure
3. Identify the decision this workstream will inform.
4. Gather evidence from repo docs, run artifacts, error analyses, literature notes, or stakeholder constraints.
5. Check whether the workstream has a measurable success criterion.
6. Compare expected value against complexity, maintenance cost, and opportunity cost.
7. Decide whether to continue, narrow, defer, or stop.

## Value Questions

- What real user or research decision gets better if this succeeds?
- Which artifact would prove progress: metric, ablation, review queue, validated schema, reproducible run, or documented method?
- Does this unblock a core dependency, or is it polish around an unstable contract?
- Is there evidence that this failure mode matters in current runs?
- Are we building a reusable tool, or just avoiding a hard research decision?
- Could a smaller experiment answer the same question?

## Warning Signs

- broad infrastructure before a narrow benchmark contract is stable
- UI work without a repeated review workflow
- model complexity before deterministic scorer/data fidelity
- new abstractions without a concrete experiment they unlock
- claims of downstream value without a metric, artifact, or user decision

## Completion Criteria

Before finishing, summarize:

- downstream use case
- evidence for value
- success criterion
- opportunity cost and risk
- recommended scope decision
