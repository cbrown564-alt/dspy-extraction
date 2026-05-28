---
name: hybrid-pipeline-exploration
description: Use when designing experiments, writing inspection or decision docs, updating Kanban, or interpreting results about hybrid DSPy pipelines — stage count, deterministic vs LLM placement per stage, and implementation variants. Enforces arm-reject vs mechanism-reject discipline and GPT cap-25 search grids before narrowing.
---

# Hybrid Pipeline Exploration

Use this skill when a component-level question still needs hybrid pipeline
design: stage count, deterministic-vs-LLM placement, implementation variants,
or arm-vs-mechanism decision discipline. After the 2026-05-28 pivot, this skill
is subordinate to the component-ceiling program rather than the top-level
research frame.

Read first:

- `docs/current_research_program.md` — current component-decomposition doctrine
- `docs/component_ceiling_registry.md` — active component status, baselines, rejected arms, and blocked claims
- `docs/planning/kanban_plan.md` — active execution queue and next pull
- `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md` — historical hybrid doctrine still useful inside component studies
- `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md` — ontology (`L0`–`D1`, interleaving positions)

Read `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`
only when a task explicitly changes hybrid mechanism status. The component
registry is the current authority for active baselines, rejected arms, blocked
claims, and next actions.

Pair with `dspy-experiment-design` and `experiment-run-lifecycle` for configs and runs.

---

## Three Axes (always name which axis a task tests)

| Axis | Question | Primary `varied_factor` examples |
| --- | --- | --- |
| **1** | How many stages / what decomposition? | `pipeline_stage_graph`, `stage_count` |
| **2** | Deterministic vs LLM vs hybrid **at each stage**? | `stage_executor`, `hybrid_balance_class`, `interleaving_positions` |
| **3** | What **implementation** for each stage? | `implementation_variant`, `prompt_policy`, `evidence_strategy`, `example_strategy` |

**Order of operations:** first confirm the component is active in the component
registry and Kanban. Then search Axis 1 -> 2 on capped GPT only when the
component substrate exists; use Axis 3 for implementation variants on a named
component/stage, and reserve Qwen/full validation for preregistered winners.

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

1. **State the active component/stage**, the axis (1, 2, or 3), and one-sentence hypothesis.
2. **Name `stage_graph_id`** when the experiment is a pipeline-decomposition
   study; for component payload work, name the payload/bridge/stage surface instead.
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

## Active Component Order

Follow `docs/planning/kanban_plan.md` and the component registry rather than a
fixed dataset ladder. Current examples include Gan G2 target-selection/label
construction after G1 strata, ExECT medication current-Rx/lifecycle payloads,
and ExECT family-span payloads. Broad ExECT stack reconstruction remains blocked
until component substrates and isolated ceilings exist.

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

- Use `docs/component_ceiling_registry.md` as the primary status ledger after
  the May 28 pivot.
- Maintain **Operational defaults** (frozen configs) separately from **Open mechanism classes**.
- Move a mechanism from `open` → `arm-reject` with inspection link, not prose.
- Move to `mechanism-reject` only after mechanism review section exists.
- Deprioritize "closed probe" reruns unless `implementation_variant` is new in prereg.
- Update the historical hybrid mechanism status doc only when the decision is
  genuinely mechanism-level, not when a component card merely accepts or rejects
  a single arm.

---

## Completion criteria

Before finishing a task under this skill:

- Axis and `decision_scope` stated
- No mechanism-closure language without review
- Run IDs and comparison group cited
- Open cells listed (what was not tested)
- Kanban/registry updated if outcomes changed
- historical hybrid mechanism status updated only if a mechanism-level status
  actually changed
