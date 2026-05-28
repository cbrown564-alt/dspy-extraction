# ExECT Frequency Event/Rate Payload Audit

Date: 2026-05-28
Status: current synthesis; no-model representability gate
Kanban card: E1 - ExECT Frequency Event/Rate Payload Gate
Dataset/split: ExECTv2 `validation` (40 documents)
Model/provider: none
Scorer mode: no-model candidate-vs-gold coverage audit; no scorer semantics changed

## Summary

The broad deterministic ExECT frequency payload now covers **43/43** validation gold labels (100.0%), up from the archived 11.6% gold-label coverage baseline.

That clears the coverage part of E1, but it does not close the component: the broad payload emits 151 extra validation candidate labels and has 22.2% candidate precision against gold. The next component stage should adjudicate or rank candidates before using this as a model pre-vocabulary substrate.

## Candidate Mode Comparison

| Mode | Gold coverage | Candidate precision | Full-label docs | Gold labels | Candidate labels | Extra labels |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Broad event/rate payload | 100.0% | 22.2% | 24/24 (100.0%) | 43 | 194 | 151 |
| High-precision payload | 58.1% | 19.5% | 8/24 (33.3%) | 43 | 128 | 103 |

## Coverage By Gold Label Type

| Mode | Label type | Gold | Matched | Coverage |
| --- | --- | ---: | ---: | ---: |
| Broad | `qualitative_change` | 12 | 12 | 100.0% |
| Broad | `quantified_rate` | 15 | 15 | 100.0% |
| Broad | `seizure_free` | 9 | 9 | 100.0% |
| Broad | `zero_rate` | 7 | 7 | 100.0% |
| High precision | `qualitative_change` | 12 | 0 | 0.0% |
| High precision | `quantified_rate` | 15 | 15 | 100.0% |
| High precision | `seizure_free` | 9 | 3 | 33.3% |
| High precision | `zero_rate` | 7 | 7 | 100.0% |

## Coverage By Gold Case Stratum

| Mode | Stratum | Documents | Gold labels | Matched | Coverage | Full-label docs |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Broad | `type_associated` | 17 | 36 | 36 | 100.0% | 17 |
| Broad | `temporal_scope` | 21 | 39 | 39 | 100.0% | 21 |
| Broad | `multi_label` | 15 | 34 | 34 | 100.0% | 15 |
| High precision | `type_associated` | 17 | 36 | 24 | 66.7% | 7 |
| High precision | `temporal_scope` | 21 | 39 | 25 | 64.1% | 8 |
| High precision | `multi_label` | 15 | 34 | 22 | 64.7% | 5 |

## Document-Level Validation

| Document | Gold labels | Broad candidates | Broad status | High-precision status |
| --- | --- | --- | --- | --- |
| `EA0008` | `1 per 3 week`<br>`frequency increased` | 4 | full | partial (1/2) |
| `EA0026` | `15 per 4 month` | 6 | full | full |
| `EA0047` | `1 per 1 week`<br>`2 per 1 day` | 10 | full | full |
| `EA0048` | `0 per 3 week` | 8 | full | full |
| `EA0050` | `1 per 1 week`<br>`frequency decreased`<br>`infrequent` | 3 | full | partial (1/3) |
| `EA0059` | `infrequent`<br>`seizure free since 2015`<br>`seizure free since 2017` | 5 | full | partial (2/3) |
| `EA0061` | `0 per 10 year`<br>`0 per 3 year` | 6 | full | full |
| `EA0068` | `infrequent`<br>`seizure free` | 2 | full | partial (0/2) |
| `EA0069` | `1 per 1 week`<br>`4 per 3 week`<br>`frequency increased` | 5 | full | partial (2/3) |
| `EA0098` | `frequency increased`<br>`seizure free since 2019` | 4 | full | partial (1/2) |
| `EA0102` | `seizure free` | 4 | full | partial (0/1) |
| `EA0124` | `0 per 3 year`<br>`1 per 1 week` | 5 | full | full |
| `EA0125` | `frequency increased` | 2 | full | partial (0/1) |
| `EA0131` | `frequency increased` | 5 | full | partial (0/1) |
| `EA0135` | `1 per 6 month` | 1 | full | full |
| `EA0136` | `0 per 3 year`<br>`0 per 5 year`<br>`frequency same` | 9 | full | partial (2/3) |
| `EA0137` | `2 per 1 year`<br>`seizure free` | 7 | full | partial (1/2) |
| `EA0142` | `seizure free` | 6 | full | partial (0/1) |
| `EA0143` | `0 per 5 year`<br>`seizure free` | 4 | full | partial (1/2) |
| `EA0150` | `1 per 1 month`<br>`1 per 1 year` | 5 | full | full |
| `EA0170` | `1 per 1 month`<br>`infrequent` | 4 | full | partial (1/2) |
| `EA0173` | `seizure free` | 2 | full | partial (0/1) |
| `EA0174` | `frequency increased` | 2 | full | partial (0/1) |
| `EA0188` | `1 per 1 day`<br>`1 per 1 month` | 5 | full | full |

## Interpretation

- The event/rate payload is now a recall-sufficient substrate on validation: quantified, qualitative, seizure-free, zero-rate, type-associated, temporal-scope, and multi-label gold cases are all covered by the broad mode.
- Precision is still low because broad candidates intentionally preserve multiple plausible benchmark labels. Treat them as an inventory, not final predictions.
- The high-precision mode is not a safe replacement: it misses qualitative-change labels by design and covers only a minority of full-label documents.
- The result supports moving from E1 coverage auditing to candidate selection/adjudication, not another broad S5 prompt loop.

## Dataset And Scorer Caveats

- Gold labels use the current `load_exect_gold_documents()` frequency policy over ExECT SeizureFrequency annotations.
- Frequency rows are not used as seizure-type gold.
- No loader, split, scorer, or benchmark-bridge semantics changed.
- Validation is the component-development split; test remains holdout for residual analysis only.

## Generated Companion

`docs/experiments/exect/exect_frequency_event_rate_payload_audit_20260528.json` contains per-document gold rows, annotation strata, candidate records, and mode summaries.
