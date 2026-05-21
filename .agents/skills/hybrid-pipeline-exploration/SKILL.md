---
name: hybrid-pipeline-exploration
description: Use when designing experiments, writing inspection or decision docs, updating Kanban, or interpreting results about hybrid DSPy pipelines — stage count, deterministic vs LLM placement per stage, and implementation variants. Enforces arm-reject vs mechanism-reject discipline and GPT cap-25 search grids before narrowing.
---

# Hybrid Pipeline Exploration

Use this skill for the project's **active research program** after the 2026-05-21 pivot.

Read first:

- `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md` — doctrine
- `docs/planning/kanban_plan.md` — active execution queue (implementation plan retired 2026-05-21)
- `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md` — ontology (`L0`–`D1`, interleaving positions)
- `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` — open vs arm-reject vs operational freeze

Pair with `dspy-experiment-design` and `experiment-run-lifecycle` for configs and runs.

---

## Three Axes (always name which axis a task tests)

| Axis | Question | Primary `varied_factor` examples |
| --- | --- | --- |
| **1** | How many stages / what decomposition? | `pipeline_stage_graph`, `stage_count` |
| **2** | Deterministic vs LLM vs hybrid **at each stage**? | `stage_executor`, `hybrid_balance_class`, `interleaving_positions` |
| **3** | What **implementation** for each stage? | `implementation_variant`, `prompt_policy`, `evidence_strategy`, `example_strategy` |

**Order of operations:** search Axis 1 → 2 on GPT cap-25 → Axis 3 on winning skeletons → Qwen/full validation for winners only.

Do **not** run Axis 3 sweeps to discover stage count or det/LLM placement.

---

## Decision scope (mandatory)

Every inspection, preregistration, and registry update must state:

```text
decision_scope: operational | arm | mechanism
```

| Scope | Meaning | Requirements |
| --- | --- | --- |
| `operational` | Default for reproducibility | May freeze config; does not close science |
| `arm` | This config under these controls failed/succeeded | One comparison group, one `varied_factor`, cite run IDs |
| `mechanism` | Hypothesis class unlikely across implementations | Mechanism review: ≥2 arms OR ≥2 positions/implementations; explicit in inspection |

**Forbidden without mechanism review:**

- "H2 is rejected"
- "verify-repair is closed"
- "tool-during failed"
- "optimizers don't work"
- "hybrid placement is answered"

**Allowed:**

- "reject (arm): `exect_s1_verification_verify_repair_cap25` under group X"
- "operational freeze: Gan `g3_det_candidates_vr` until Phase 3 completes"
- "open mechanism: LLM temporal candidate generation"

---

## Experiment design checklist

Before creating configs or running models:

1. **State the axis** (1, 2, or 3) and one-sentence hypothesis.
2. **Name `stage_graph_id`** — stable ID for pipeline decomposition (see implementation plan).
3. **Fix controls:** dataset, split, cap, model (GPT 4.1-mini for search), scorer, schema.
4. **One primary `varied_factor`** per comparison group unless preregistered factorial.
5. **Tag taxonomy:** `comparison_group`, `hybrid_balance_class`, `interleaving_positions`, `program_architecture`.
6. **Preregister gates** — cap-25 is for **ranking/search**, not mechanism closure on null.
7. **Compose primitives** — use `arm_templates` / catalog; new det/LLM stage slots need new variant IDs, not silent program edits.

---

## Comparison group naming

```text
<dataset>_<schema>_<axis-factor>_<model>_cap25_v<number>
```

Examples:

- `gan_s0_pipeline_stage_graph_gpt_cap25_v1`
- `gan_s0_stage_executor_gpt_cap25_v1`
- `exect_s1_pipeline_stage_graph_gpt_cap25_v1`

---

## Inspection doc template (add to every new inspection)

```markdown
## Taxonomy
Dataset:
Schema complexity:
Comparison group:
Research axis: 1 | 2 | 3
stage_graph_id:
varied_factor:
decision_scope: arm | mechanism | operational

## Arms (table)
| arm_id | run_id | headline metric | gate |

## Outcomes
| arm_id | outcome | decision_scope | Notes |

## Mechanism review (required only if claiming mechanism reject or promote)
- Arms cited:
- Implementations/positions tested:
- Conclusion:

## Open cells (explicit)
- What this study did NOT test:
```

---

## Dataset order

1. **Gan S0** — Axis 1–2 first (cleaner task, temporal bottleneck).
2. **ExECT S1** — Axis 1–2 with `bridge_mode` documented (`inline` | `post_module` | `none_diagnostic`).
3. **ExECT S2–S4** — only after S1 skeleton candidates exist.
4. **Qwen** — confirmatory port of cap-25 winners.

---

## Interaction with other skills

| Situation | Also use |
| --- | --- |
| Loaders, splits, gold quirks | `dataset-audit-first` |
| Scorer changes | `gold-scorer-integrity` |
| New primitives / adapters | `taxonomy-primitive-design` |
| Running configs | `experiment-run-lifecycle` |
| ExECT label policy text | `exect-label-policy-alignment` |
| Kanban updates | `plan-to-kanban` after grid prereg |
| Writing synthesis | `research-synthesis` — distinguish operational vs mechanism |

---

## When updating Kanban or registry

- Maintain **Operational defaults** (frozen configs) separately from **Open mechanism classes**.
- Move a mechanism from `open` → `arm-reject` with inspection link, not prose.
- Move to `mechanism-reject` only after mechanism review section exists.
- Deprioritize "closed probe" reruns unless `implementation_variant` is new in prereg.

---

## Completion criteria

Before finishing a task under this skill:

- Axis and `decision_scope` stated
- No mechanism-closure language without review
- Run IDs and comparison group cited
- Open cells listed (what was not tested)
- Kanban/registry updated if outcomes changed
- `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` updated if mechanism status changed
