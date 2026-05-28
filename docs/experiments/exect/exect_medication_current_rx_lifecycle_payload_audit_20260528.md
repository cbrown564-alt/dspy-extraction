# ExECT Medication Current-Rx And Lifecycle Payload Audit

Date: 2026-05-28
Status: current synthesis; no-model representability gate
Kanban card: E3 - Medication Current-Rx And Lifecycle Payload
Dataset/split: ExECTv2 `validation` (40 documents)
Model/provider: none
Scorer mode: no-model payload-vs-gold coverage audit; no scorer semantics changed

## Summary

The annotation-derived current-Rx payload reproduces **47/47** validation gold medication labels (100.0%) across 29/29 gold-bearing documents.

The note-surface lifecycle view is useful as a diagnostic inventory, but not as a replacement current-Rx substrate: it covers **22/47** gold labels (46.8%) with 78.6% candidate precision.

## Current-Rx Comparison

| Payload view | Gold coverage | Candidate precision | Full-label docs | Gold labels | Candidate labels |
| --- | ---: | ---: | ---: | ---: | ---: |
| Annotated current-Rx payload | 100.0% | 100.0% | 29/29 (100.0%) | 47 | 47 |
| Note lifecycle current candidates | 46.8% | 78.6% | 9/29 (31.0%) | 47 | 28 |

## Lifecycle Inventory

| Case type | Count |
| --- | ---: |
| `dose_line_rows` | 131 |
| `dose_only_rows` | 60 |
| `non_asm_rows` | 4 |
| `planned_rows` | 11 |
| `prescription_list_rows` | 78 |
| `previous_rows` | 9 |
| `taper_or_stop_rows` | 8 |
| `unknown_temporality_rows` | 116 |

## Temporality Decision

- Annotated current-Rx is the headline medication substrate for S1/S5 medication reproduction.
- Lifecycle and temporality remain diagnostic/deferred because ExECT prescription JSON lacks a native temporality column.
- Planned, previous, taper, dose-line, and non-ASM rows should be reported as lifecycle cases before any model-backed temporality target is promoted.

## Dataset And Scorer Caveats

- Gold labels use current `load_exect_gold_documents()` prescription policy.
- Prescription rows are benchmark current-Rx by annotation policy, even when lifecycle cues need separate inspection.
- No loader, split, scorer, or benchmark bridge semantics changed.
- Validation is the component-development split; test remains holdout for residual analysis only.

## Generated Companion

`docs/experiments/exect/exect_medication_current_rx_lifecycle_payload_audit_20260528.json` contains per-document payload rows and lifecycle counts.
