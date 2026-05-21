# First DSPy Schema Sequence

Date: 2026-05-17

## Decision

Run **Gan frequency first**, then expand to **ExECT S0/S1** field-family extraction after the Gan pipeline has one reproducible baseline.

## Rationale

Gan frequency is the smallest clinically meaningful task with mature deterministic infrastructure: primary gold labels, fixed splits, normalization, deterministic scoring, evidence diagnostics, error analysis, and run artifact contracts are already in place. It is therefore the right first DSPy target for testing extraction, evidence capture, verification, and repair without changing scorer semantics.

ExECT S0/S1 should follow once the first Gan module path is stable. That sequence adds schema breadth and field-family complexity without mixing it into the first model-adapter and DSPy-module integration.

## Required Controls

- Dataset and split: `gan_2026`, `gan_2026_fixed_v1`, starting with validation/dev smoke runs before test-set reporting.
- Model/provider: early Mac iteration may use a closed low-cost model; local Qwen runs remain a later target once adapters exist.
- Schema level: `gan_frequency_s0` for the first run; ExECT S0/S1 should be a separate follow-up sequence.
- Program variant: begin with single-pass Gan frequency extraction with evidence, then add context-injected and extract-verify-repair variants as ablations.
- Scorer mode: `gan_frequency_deterministic_v1`.
- Metric caveats: monthly-frequency, Purist category, and Pragmatic category metrics are benchmark-facing; raw exact, normalized-label exact, evidence diagnostics, schema validity, repair, and abstention metrics are diagnostic.

## Kanban Impact

The broad "Build DSPy extraction modules" card should stay blocked until it is split into a narrow first implementation card for Gan S0 frequency extraction. ExECT S0/S1 should remain behind ExECT field-family scorer coverage.
