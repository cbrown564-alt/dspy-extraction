---
name: paper-critical-review
description: Use when critically reviewing a paper outline, manuscript draft, section draft, abstract, argument map, results narrative, or planned paper for rigor, coherence, weak points, missing exposition, unsupported claims, methodological threats, narrative gaps, or project-design issues that undermine the paper. Trigger for paper critique, adversarial review, reviewer-2 pass, claim audit, narrative coherence review, rigor review, or deciding what experiments or explanations are needed before submission.
---

# Paper Critical Review

Use this skill to critique the paper as both a research artifact and a narrative artifact. The aim is to identify where the manuscript's argument outruns the evidence, where project design has created narrative incoherence, and what concrete loop would most improve rigor.

Use alongside `research-supervisor-review` for repo-level supervision, `gold-scorer-integrity` for metric claims, `dataset-audit-first` for benchmark claims, and `research-drift-audit` when the paper story seems to diverge from the original research plan.

## Starting Context

Read the paper draft, outline, section, or argument map first. Then inspect only the evidence needed to verify its claims:

1. `docs/outline.md`
2. `docs/planning/kanban_plan.md`, if the draft claims planned or completed scope
3. experiment reports, preregistrations, inspections, and registry entries cited or implied by the draft
4. scorer, split, and benchmark policy docs when metrics are discussed
5. dataset audits when the paper makes ExECTv2 or Gan claims:
   - `docs/datasets/exect/exect_gold_label_audit.md`
   - `docs/datasets/gan/gan_2026_label_audit.md`

Read `references/review_rubric.md` for a full manuscript critique or when preparing a structured revision plan.

## Review Workflow

1. State the paper's apparent thesis in one sentence.
2. List the main claims the paper needs readers to believe.
3. For each claim, classify support:
   - `Strong`: directly supported by artifacts and methods
   - `Thin`: plausible but under-evidenced
   - `Unclear`: support may exist but is not visible in the draft
   - `Overclaim`: wording exceeds the evidence
4. Evaluate the paper on two axes:
   - methodological rigor
   - narrative coherence
5. Identify design-to-narrative leaks:
   - unclear experiment sequencing
   - inconsistent schema levels or field groups
   - scorer semantics that changed midstream
   - dataset-policy caveats not integrated into the story
   - broad architecture work without a named claim
6. Recommend the smallest revision loop:
   - rewrite only
   - add exposition
   - run or rerun an experiment
   - repair traceability
   - narrow the thesis
   - split into separate papers or sections

## Critical Dimensions

- thesis specificity
- contribution novelty and scope control
- benchmark and dataset fidelity
- method reproducibility
- experiment design and ablation discipline
- metric validity and scorer stability
- error-analysis depth
- relation between deterministic and LLM components
- clinical label-policy alignment
- treatment of negative results
- limitations and threats to validity
- internal narrative order
- reader confidence after each section

## Output Shape

Use this shape for normal reviews:

```markdown
## Apparent Thesis

## Strongest Parts

## Major Risks
| Risk | Severity | Evidence | Fix |
| --- | --- | --- | --- |

## Claim Audit
| Claim | Support | Problem | Needed revision |
| --- | --- | --- | --- |

## Narrative Coherence

## Methodological Rigor

## Recommended Revision Loop
1. ...
2. ...
3. ...
```

For short drafts, compress the structure. For full manuscript review, cite paths, run IDs, configs, and metric files wherever possible.

## Review Rules

- Lead with the highest-risk issues, not copyediting.
- Distinguish missing evidence from missing exposition.
- Treat a confusing story as a research signal: it may reveal unclear project design, not just weak prose.
- Do not ask for more experiments by reflex; first decide whether narrowing or explaining would solve the issue.
- Prefer actionable fixes: paragraph move, claim rewording, figure/table addition, ablation, artifact audit, or limitation wording.
- Preserve promising ideas even when the current framing is weak.

## Completion Criteria

Before finishing, include:

- draft or outline reviewed
- evidence artifacts inspected
- highest-risk unsupported or unclear claim
- whether the next loop is writing, analysis, experiment, or scope control
- one to three concrete next actions
