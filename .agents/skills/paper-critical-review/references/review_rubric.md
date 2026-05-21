# Paper Critical Review Rubric

Use this reference for a full manuscript, outline, or claim audit.

## Severity Scale

- `P0`: invalidates a main claim or makes comparisons misleading
- `P1`: seriously weakens credibility or reviewer confidence
- `P2`: causes confusion or undercuts persuasion but is fixable in revision
- `P3`: polish, ordering, or local clarity

## Claim Audit Questions

For each main claim, ask:

1. What exact artifact supports this?
2. Is the dataset split explicit?
3. Is the model/provider explicit?
4. Is the schema level or field family explicit?
5. Is the DSPy program or pipeline variant explicit?
6. Is the scorer mode and normalization rule explicit?
7. Are changed scorer semantics or benchmark-policy caveats disclosed?
8. Does the evidence show the claimed mechanism, or only a performance difference?
9. Could a reviewer reproduce the comparison from the manuscript?
10. Is a simpler explanation still plausible?

## Common Failure Modes

| Failure mode | Why it matters | Usual fix |
| --- | --- | --- |
| Chronology masquerades as argument | readers see activity, not contribution | reorder around claims and decisions |
| Architecture over-description | method feels complex without payoff | tie each component to validity or an ablation |
| Metric overclaim | benchmark caveats are hidden | add scorer/dataset policy and narrow wording |
| Missing negative results | design looks arbitrary | include pivots and failed paths as controls |
| Weak mechanism claim | results do not prove why improvement happened | add ablation, error analysis, or softer wording |
| Vague clinical value | paper implies impact beyond evidence | specify decision context or move to future work |
| Split inconsistency | reviewer cannot trust comparisons | repair traceability and rerun if needed |
| Result-story mismatch | strongest evidence supports a different thesis | revise thesis before polishing prose |

## Revision Loop Types

- `Writing loop`: evidence exists; prose/order/definitions need work.
- `Analysis loop`: artifacts exist; synthesis, tables, or error taxonomy are missing.
- `Experiment loop`: a claim needs an ablation, rerun, cap removal, or validation split.
- `Traceability loop`: run IDs, configs, metric files, or scorer versions are not recoverable.
- `Scope loop`: one paper is trying to carry multiple incompatible stories.

Recommend the cheapest loop that resolves the highest-severity issue.
