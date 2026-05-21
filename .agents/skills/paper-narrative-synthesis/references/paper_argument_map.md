# Paper Argument Map

Use this reference when building a full paper outline, introduction, discussion, or revision plan.

## Core Question

Ask: what should the reader believe after this paper that they would not believe from the project logs alone?

Prefer a thesis shaped like:

```text
For clinical extraction under noisy benchmark labels, a hybrid pipeline that combines deterministic typed structure with targeted LLM stages can improve reproducibility and interpretability, but only when dataset policy, scorer semantics, and error analysis are treated as first-class method components.
```

Revise the thesis to fit the actual evidence. Do not keep this template if the artifacts do not support it.

## Claim Ladder

| Level | Question | Evidence to look for |
| --- | --- | --- |
| Problem | What clinical extraction failure matters? | outline, dataset audits, error analyses |
| Gap | Why are generic LLM extraction runs insufficient? | benchmark quirks, scorer caveats, prior run failures |
| Method | What did this project build or compare? | architecture docs, configs, primitives, DSPy programs |
| Control | How were claims kept reproducible? | split policy, scorer policy, preregistration, run metadata |
| Result | What changed in metrics or errors? | experiment reports, registry, inspections |
| Interpretation | What mechanism explains the result? | ablations, qualitative error analysis, primitive placement notes |
| Limitation | What remains uncertain? | failed runs, residual queues, audit caveats |

## Paper-Level Weak Points

Track weak points as part of the writing artifact:

| Weak point type | Signal | Productive response |
| --- | --- | --- |
| Rigor gap | claim lacks run/config/scorer trace | inspect artifact or weaken claim |
| Exposition gap | evidence exists but reader cannot follow | add section, figure, table, or definitions |
| Coherence gap | workstreams do not support one thesis | narrow thesis or split story |
| Design gap | project architecture obscures factor isolation | add ablation framing or limitation |
| Benchmark gap | label policy affects interpretation | foreground dataset audit and scorer semantics |

## Recommended Figures And Tables

- dataset and field-family overview
- pipeline schematic with deterministic and LLM stages
- experiment matrix keyed by dataset, split, schema level, model, and scorer
- benchmark results table with scorer caveats
- error taxonomy table
- claim-to-evidence matrix
- limitations table linking threat, consequence, and mitigation
