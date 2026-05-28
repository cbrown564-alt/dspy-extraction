# ExECT Family-Span Payload Audit

Date: 2026-05-28
Status: current synthesis; no-model representability gate
Kanban card: E4 - Family-Span Payload
Dataset/split: ExECTv2 `validation` (40 documents)
Model/provider: none
Scorer mode: no-model span-vs-gold evidence coverage audit; no scorer semantics changed

## Summary

The typed `exect.sections.family_spans.v1` payload emits 816 validation spans across diagnosis/problem, seizure, medication, investigation, history/background, frequency, and plan/follow-up families.

On the first 25 validation documents, the S1-plus-investigation family-span context uses 29319/33029 characters (88.8% of the full-note prompt substrate) while covering 116/116 gold annotations (100.0%).

## Gold Evidence Coverage By Family

| Family | Gold annotations | Covered | Coverage |
| --- | ---: | ---: | ---: |
| `diagnosis_problem` | 56 | 56 | 100.0% |
| `seizure` | 49 | 49 | 100.0% |
| `medication` | 53 | 53 | 100.0% |
| `investigation` | 33 | 33 | 100.0% |
| `history_background` | 89 | 85 | 95.5% |
| `frequency` | 44 | 44 | 100.0% |

## False-Family Span Count

| Span family | Count |
| --- | ---: |
| `diagnosis_problem` | 26 |
| `frequency` | 36 |
| `history_background` | 12 |
| `investigation` | 24 |
| `medication` | 23 |
| `plan_follow_up` | 55 |
| `seizure` | 59 |

## Interpretation

- The family-span payload is a typed document-geometry substrate, not a promoted section-filtering arm.
- Coverage and false-family counts should gate any future family-span prompting run against a full-note baseline.
- Plan/follow-up spans are retained as routing context but have no current benchmark gold family in this audit.

## Dataset And Scorer Caveats

- Gold evidence coverage uses existing annotation offsets and audited inclusion policy for diagnosis and seizure-type rows.
- No loader, split, scorer, or benchmark bridge semantics changed.
- Validation is the component-development split; test remains holdout for residual analysis only.

## Generated Companion

`docs/experiments/exect/exect_family_span_payload_audit_20260528.json` contains per-document spans, gold annotation coverage, and false-family rows.
