# Experiment Decision / Pre-Registration Template

Date: YYYY-MM-DD  
Status: Planned | In progress | Completed  
Related: `docs/kanban_plan.md`, `docs/experiment_taxonomy_schema.md`, `docs/taxonomy_primitive_catalog.md`

## Research question

One sentence stating what this comparison group decides.

## Fixed controls (all arms)

| Control | Value |
| --- | --- |
| Dataset | |
| Split | |
| Schema / taxonomy | |
| Scorer mode | |
| Clinical task family | |
| Model track | |
| Structured output | |
| Run scope | |

## Comparison group

`<dataset>_<schema>_<factor>_<model_track>_<scope>_v<number>`

**Varied factor:** name the single primary factor unless explicitly multi-factor.

Use `clinical_extraction.experiments.arm_templates.build_comparison_group_id()` when creating new groups.

## Arms

| Arm | Config | Hybrid class | Interleaving | Primitive IDs | Question |
| --- | --- | --- | --- | --- | --- |
| L1 | | `L1_llm_constrained` | `during` | none | |
| H1 | | `H1_post_deterministic` | `during`, `post` | post bridges | |
| H2 | | `H2_pre_deterministic` | `pre`, `during` | candidate primitives | |
| H3 | | `H3_interleaved_tool_hybrid` | `tool_during`, `during` | tool interfaces | |
| H4 | | `H4_deterministic_first_llm_adjudicates` | `pre`, `during`, `post` | candidates + verifier | |
| D1 | | `D1_deterministic_only` | `eval_only` | diagnostic primitives | |

Build configs with `clinical_extraction.experiments.arm_templates.build_experiment_arm_config()`.

## Promotion gates

- Primary metric threshold:
- Regression guardrails (field families that must not drop ≥ N pp):
- Scope required before promote (`cap25` → `full_validation`):

## Normalization and evidence policy

Summarize expected normalization and evidence behavior across arms so post-run inspection does not reinterpret scorer semantics.

## Outcomes (fill after runs)

| Arm | Outcome | Decision doc / inspection |
| --- | --- | --- |
| | | |

## Caveats

- Audit references (`docs/exect_gold_label_audit.md`, `docs/gan_2026_label_audit.md`)
- Rejected or blocked paths
- Comparison validity limits
