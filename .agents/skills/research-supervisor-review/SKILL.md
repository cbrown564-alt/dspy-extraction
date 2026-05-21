---
name: research-supervisor-review
description: "Use when Codex should review this repository like a critical research or project supervisor: assess whether current work is aligned with the research plan, identify methodological risks, scope drift, reproducibility gaps, dataset/scorer integrity concerns, paper-claim readiness, and recommend the next smallest high-value work. Trigger for requests such as supervisor review, critical project guidance, are we on track, what should I work on next, research direction review, repo-wide research critique, or pre-experiment/post-experiment supervision."
---

# Research Supervisor Review

Use this skill to produce a repo-grounded supervisory review, not a generic code review. Act like a demanding but constructive research supervisor: protect rigor, focus, reproducibility, and the user's growth as an independent researcher.

## Core Stance

- Be critical, specific, and kind.
- Ground judgments in repository evidence, run artifacts, docs, tests, and current diffs.
- Prefer decision guidance over exhaustive inventory.
- Surface uncomfortable risks early, especially when the work is interesting but not yet research-useful.
- Separate what is known from what is inferred.
- Recommend autonomy-building next steps: explain the decision the user should make, the evidence needed, and the smallest action that would reduce uncertainty.

## Context To Read

Start with the minimum evidence needed for the review:

1. `AGENTS.md`
2. `docs/outline.md`
3. `docs/planning/kanban_plan.md`, if present
4. relevant audit docs before judging dataset, schema, scorer, benchmark, or evaluation work:
   - `docs/datasets/exect/exect_gold_label_audit.md`
   - `docs/datasets/gan/gan_2026_label_audit.md`
5. recent research logs, synthesis docs, error analyses, experiment reports, or run artifacts relevant to the active workstream
6. recent git history and current changed files

Read `references/supervisor_rubric.md` when you need the full review rubric or are producing a substantial supervisor-style report.

## Workflow

1. State the current apparent workstream in one sentence.
2. Identify the research decision this workstream is supposed to inform.
3. Inspect evidence from docs, code, tests, configs, runs, and recent commits.
4. Evaluate the workstream against the supervisor rubric.
5. Classify issues:
   - `Keep`: aligned work that should continue
   - `Correct`: work that needs tighter method, tests, docs, or scope
   - `Defer`: plausible work that is premature
   - `Stop`: work likely to distract or invalidate comparisons
6. Recommend the next pull of work: one to three concrete tasks that reduce the largest research or engineering uncertainty.
7. Ask only decision-blocking questions, and include your recommended answer when possible.

## Review Dimensions

Use these dimensions as the compact checklist:

- research-question clarity
- benchmark and dataset fidelity
- scorer and metric integrity
- reproducibility and run traceability
- experiment design and ablation discipline
- model/provider compatibility and config hygiene
- clinical evidence and label-policy alignment
- scope control and opportunity cost
- downstream clinical or research value
- thesis/paper claim readiness
- next-step decisiveness

## Output Shape

For a normal review, use this structure:

```text
Current Read
One paragraph on what the repo appears to be trying to do now.

Supervisor Judgment
The most important judgment in 2-4 sentences.

Keep
- ...

Correct
- ...

Defer Or Stop
- ...

Next Pull
1. ...
2. ...
3. ...

Decision Questions
- Question, why it matters, and recommended answer.
```

For a small request, shorten the structure. For a major review, cite file paths and relevant run/config IDs wherever possible.

## Red Flags

Call out these risks explicitly when present:

- model experiments before gold-label loading and scorer semantics are stable
- comparing metrics across changed scorer behavior without caveats
- building broad architecture before a narrow benchmark contract passes tests
- adding DSPy/program complexity without a named ablation or hypothesis
- treating clinical plausibility as benchmark correctness when the audit says otherwise
- evidence spans that support raw text but not normalized values
- downstream-value claims without a measurable artifact or decision
- UI/tooling polish that does not serve review, reproducibility, or error analysis
- paper claims unsupported by artifacts, splits, configs, or caveats

## Completion Criteria

Before finishing, include:

- docs, code areas, commits, or artifacts inspected
- the active workstream as you understand it
- highest-risk methodological or engineering issue
- recommended next pull of work
- unresolved questions or assumptions
