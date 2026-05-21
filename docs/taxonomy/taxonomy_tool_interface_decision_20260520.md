# Taxonomy Tool Interface Decision

Date: 2026-05-20  
Status: Decision recorded (Card 17)  
Related: `docs/taxonomy/taxonomy_primitives_workstream_plan_20260520.md`, `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md`, `docs/experiments/gan/gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails_inspection_20260520.md`, `src/clinical_extraction/interleaving_adapters.py`

## Question

How much should the primitive workstream generalize tool-facing interfaces after the Gan ReAct H3 probe failed?

## Decision

Build a **minimal, comparison-ready tool interface**, not a broad tool-wrapper framework.

### In scope now

1. **Interleaving adapter surfaces** already expose `tool_during` for candidate primitives via `ToolDuringSurface` in `src/clinical_extraction/interleaving_adapters.py`.
2. **Typed registry metadata** for tool primitives such as `gan.frequency.temporal_tool.v1`, including required `tool_affordance` control mode and `tool_during` interleaving position.
3. **Experiment arm templates** that can compose H3 arms when a future comparison group explicitly varies `tool_during` interleaving.
4. **Negative-control documentation**: Gan ReAct remains the reference result for rejecting H3 as a default path.

### Out of scope now

1. A generic tool registry that wraps every primitive as a callable ReAct tool.
2. ExECT bounded ReAct tool modules unless a pre-registered comparison group requires them after ≥2pp GPT full-validation gain on a non-tool arm.
3. Making H3 the default hybrid balance class for any dataset or field family.
4. Building production-grade tool orchestration (retries, caching, provider-specific tool schemas) beyond what a single bounded comparison needs.

## Rationale

The Gan regression slice showed that **pre-injected deterministic candidates (H2/H4) beat tool-during reasoning (H3)** on the same temporal knowledge:

- ReAct H3: 42.9% monthly on valid predictions, 50% schema validity.
- Temporal-candidates B1: perfect slice monthly accuracy with the same underlying rules exposed before adjudication.

Tool-during interleaving changes the scientific variable. It should remain available for explicit comparisons, but the failed probe is sufficient negative control for ExECT S1 unless a revised H1/H2 arm shows meaningful gain first.

## Implementation boundary

| Layer | Responsibility |
| --- | --- |
| Primitive core | Deterministic invoke path independent of interleaving position |
| Interleaving adapter | Position-specific renderers (`pre`, `during`, `tool_during`, `post`, `eval_only`) |
| Program / ReAct module | Wires tool-during surfaces into a bounded DSPy program when an H3 config is run |
| Experiment config | Declares H3 only when `varied_factor` includes interleaving position or hybrid balance class |

New tool primitives must:

- declare `tool_affordance` and `tool_during` in metadata,
- reuse the same core invoke function as pre/during surfaces,
- ship with deterministic adapter tests before any model-backed H3 run.

## Default paths

| Track | Default hybrid class | Tool-during status |
| --- | --- | --- |
| Gan frequency | H2/H4 temporal-candidates | H3 rejected; reference only |
| ExECT S1 | L1 prompt policy + post bridges | H3 deferred |
| ExECT S4 | L1 + family-specific post bridges | H3 not planned |

## Revisit triggers

Re-open broad tool-wrapper work only when:

1. A pre-registered H3 comparison group is approved in `docs/planning/kanban_plan.md`, or
2. A new field family shows a specific hypothesis that tool-during access beats pre-injection for the same knowledge source, or
3. Schema-validity or latency constraints from the Gan probe are addressed with a materially different H3 design.

Until then, tool interfaces stay at the adapter plus metadata layer already implemented in Card 12.
