# ExECT Medication Lifecycle Target Policy Decision

Date: 2026-05-28
Status: active guidance
Kanban card: E5 - Medication Lifecycle Target Policy Decision
Decision scope: benchmark contract / clinical diagnostic boundary; no scorer, loader, split, or model-output change

## Decision

Medication lifecycle / temporality is **clinical-diagnostic and deferred**, not a benchmark-facing headline target for the current ExECT component-ceiling program.

The benchmark-facing medication target remains annotated current-Rx reproduction through the existing `annotated_medication` / prescription view. Lifecycle labels such as `current`, `planned`, `previous`, `taper_or_stop`, `dose_line`, and `unknown_temporality` may be reported as diagnostic strata for residual analysis, stack-interference attribution, and future task design, but they must not be used as medication F1 headline metrics until reliable temporality gold or an explicit proxy-scoring protocol exists.

## Evidence

E3 showed that the annotation-derived current-Rx payload covers the existing validation medication gold exactly: **47/47** labels across **29/29** gold-bearing documents, with **100.0%** candidate precision under the no-model payload-vs-gold audit.

The note-surface lifecycle current candidates are not an adequate replacement scoring substrate: they cover only **22/47** validation medication gold labels (**46.8%**) across **9/29** gold-bearing documents, although candidate precision is **78.6%**.

The E3 lifecycle inventory is still useful diagnostic material:

| Lifecycle case type | Count |
| --- | ---: |
| `dose_line_rows` | 131 |
| `dose_only_rows` | 60 |
| `non_asm_rows` | 4 |
| `planned_rows` | 11 |
| `prescription_list_rows` | 78 |
| `previous_rows` | 9 |
| `taper_or_stop_rows` | 8 |
| `unknown_temporality_rows` | 116 |

## Gold And Proxy Source

The gold/proxy source for benchmark-facing medication remains the ExECT JSON `Prescription` annotation loaded by `load_exect_gold_documents()`, normalized through the current medication benchmark bridge.

There is no native prescription temporality column in ExECT JSON or `MarkupPrescriptions.csv`. The gold audit explicitly warns that prescription annotations do not reliably distinguish current, planned, previous, or tapering medication status. Therefore lifecycle status cannot be treated as annotation-faithful gold.

Lifecycle values in E3 are note-surface, cue-derived proxy labels. They are appropriate for:

- clinical diagnostic summaries;
- row-level residual categories;
- E7 stack-interference attribution;
- preregistering a future lifecycle-specific task contract.

They are not appropriate for:

- headline medication precision, recall, or F1;
- ExECT Table 1 reproduction claims;
- changing S1/S5 medication scorer semantics;
- treating planned/previous/taper mentions as false positives or false negatives against current-Rx gold.

## Scoring Caveats

`docs/policies/deterministic_scorer_semantics.md` already fixes the current rule: medication metrics use the annotated prescription view and intentionally do not score planned/current status as benchmark-facing because ExECT prescription gold lacks reliable temporality.

This E5 decision preserves that scorer boundary. No deterministic repair, benchmark bridge, loader, split, or scorer behavior changes with this note.

Future lifecycle scoring would require a follow-up card that defines one of these explicitly:

- an annotation-reproduction target with richer prescription attributes;
- a clinically corrected proxy target with documented adjudication rules;
- a diagnostic-only classifier report that does not enter benchmark-facing medication F1;
- a blocked decision if reliable gold/proxy support cannot be established.

## Implications For Active Cards

E6 should proceed as an isolated **current-Rx** ceiling probe using the E3 annotation-current-Rx payload and should report medication precision, recall, and F1 without lifecycle scoring.

E7 may use lifecycle categories to explain S5 medication loss, including over-emission, non-ASM leakage, historical/planned/taper evidence, and dose-only rows. It should report those categories as diagnostic attribution strata, not as lifecycle target performance.

Pairwise medication+temporality work remains deferred until a separate preregistered lifecycle target policy defines the gold/proxy source and scorer mode.

## References

- `docs/experiments/exect/exect_medication_current_rx_lifecycle_payload_audit_20260528.md`
- `docs/experiments/exect/exect_medication_current_rx_lifecycle_payload_audit_20260528.json`
- `docs/datasets/exect/exect_gold_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md`
