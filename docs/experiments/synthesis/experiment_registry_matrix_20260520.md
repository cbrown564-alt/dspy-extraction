# Experiment Registry Matrix (Paper-Ready Export)

Status: X3 refreshed registry-derived export / methods and provenance view
Authority: provenance and methods drafting only; current component status lives in `docs/component_ceiling_registry.md`, and active/replay config authority lives in `docs/experiments/synthesis/program_variant_registry.md`.
Refresh scope: generated after the May 28 component pivot, R11-R15 Gan decisions, X1 component-ceiling backfill, C4 authority classes, and C10 provenance cleanup. The legacy experiment registry remains the row source; use the authority docs above before treating any row as current.

**Generated:** 2026-05-29  
**Source:** `docs/experiments/synthesis/experiment_registry.json` (registry_rows=215)  
**Filter mode:** `curated`  
**Exported rows:** 156

Grouped by `comparison_group`, then dataset, schema, model, and run scope. Compare rows only within the same comparison group and respect `metric_caveats` on each registry row.

## Caveats

- Individual run directories remain attached in artifact_paths; canonical_run_id is the latest local metric-bearing run for each experiment_id unless later curated.
- Retrospective taxonomy fields are inferred from config/run metadata and should be reviewed before paper-facing analysis.
- Step 3 curated the first canonical anchor rows; non-anchor retrospective rows may still contain generated tags pending later backfill.
- Step 4 added comparison_groups arrays for curated rows that legitimately participate in more than one analysis; comparison_group remains the primary group for simple consumers.
- This is the Step 1 registry seed; controlled vocabularies and validation are planned in later steps.
- 2026-05-26 refresh added curated rows for current ExECT clean-ladder/S5 defaults and late Gan R9 recovery artifacts; these rows are documentation hygiene and do not change scorer semantics.
- Gan R9 recovery rows identify validation candidates only; Gan test-holdout selection still requires an explicit promotion/holdout review.
- 2026-05-26 A2 added the ExECT S5 GPT 5.5 fixed-stack anchor as closed-model comparison evidence; it does not change the S5 operational default.
- This table is for methods/results drafting; it is not published ExECTv2 Table 1 or Gan Real-set reproduction.
- Do not treat rows as current pulls unless the C4 authority class and component-ceiling registry also promote them.
- Regenerate after registry updates: `uv run python scripts/export_experiment_registry_matrix.py`.

## exect_gemini_ladder_replay_v1

Rows: 4

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s0_s1_validation_full_gemini31_flash_lite` | exect_v2 | exect_s1 | gemini | single_pass | L1_llm_constrained | during, eval_only | full_validation | **hold** | micro_f1=90.3% | [inspection](docs/experiments/exect/exect_gemini_ladder_replay_v1_inspection_20260521.md) |
| `exect_s0_s1_smoke_gemini31_flash_lite` | exect_v2 | exect_s1 | gemini | single_pass | L1_llm_constrained | during, eval_only | smoke | **hold** | — | [inspection](docs/experiments/exect/exect_gemini_ladder_replay_v1_preregistration_20260521.md) |
| `exect_s4_validation_full_gemini31_flash_lite` | exect_v2 | exect_s4 | gemini | single_pass | H1_post_deterministic, L1_llm_constrained | during, post, eval_only | full_validation | **hold** | micro_f1=66.8% | [inspection](docs/experiments/exect/exect_gemini_ladder_replay_v1_inspection_20260521.md) |
| `exect_s4_smoke_gemini31_flash_lite` | exect_v2 | exect_s4 | gemini | single_pass | H1_post_deterministic, L1_llm_constrained | during, post, eval_only | smoke | **hold** | — | [inspection](docs/experiments/exect/exect_gemini_ladder_replay_v1_preregistration_20260521.md) |

## exect_qwen_replication_validation_v1

Rows: 4

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s0_s1_validation_full_ollama` | exect_v2 | exect_s1 | qwen35b | single_pass | L1_llm_constrained | during, eval_only | full_validation | **hold** | micro_f1=79.0% | [inspection](docs/planning/research_drift_audit_20260520.md) |
| `exect_s2_validation_full_ollama` | exect_v2 | exect_s2 | qwen35b | single_pass | L1_llm_constrained | during, eval_only | full_validation | **hold** | micro_f1=82.6% | [inspection](docs/planning/research_drift_audit_20260520.md) |
| `exect_s3_validation_full_ollama` | exect_v2 | exect_s3 | qwen35b | single_pass | L1_llm_constrained | during, eval_only | full_validation | **hold** | micro_f1=72.2% | [inspection](docs/experiments/exect/exect_s3_validation_full_qwen35b_ollama_inspection_20260520.md) |
| `exect_s4_validation_full_ollama` | exect_v2 | exect_s4 | qwen35b | single_pass | L1_llm_constrained | during, eval_only | full_validation | **hold** | micro_f1=67.5% | [inspection](docs/experiments/exect/exect_s4_validation_full_qwen35b_ollama_inspection_20260520.md) |

## exect_qwen_s4_cap25_gate_v1

Rows: 1

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s4_validation_cap25_ollama` | exect_v2 | exect_s4 | qwen35b | single_pass | L1_llm_constrained | during, eval_only | cap25 | **exploratory** | micro_f1=72.4% | [inspection](pending_backfill) |

## exect_s1_architecture_gpt_cap25_v1

Rows: 3

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s0_s1_section_aware_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | section_aware | H2_pre_deterministic | pre, during | cap25 | **reject** | micro_f1=65.6% | [inspection](docs/experiments/exect/exect_section_aware_cap25_inspection.md) |
| `exect_s0_s1_validation_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during, eval_only | cap25 | **exploratory** | micro_f1=95.8% | [inspection](pending_backfill) |
| `exect_s0_s1_verify_repair_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | verify_repair | H1_post_deterministic | during, post | cap25 | **exploratory** | micro_f1=83.8% | [inspection](pending_backfill) |

## exect_s1_clean_ladder_qwen_validation_v1

Rows: 1

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_clean_ladder_v2_diagnosis_stable_full_ollama` | exect_v2 | exect_s1 | qwen35b | field_family_prompt_graph | H1_post_deterministic | during, post | full_validation | **freeze** | micro_f1=85.9% | [inspection](docs/experiments/exect/exect_s1_clean_ladder_qwen_validation_v1_inspection_20260525.md) |

## exect_s1_evidence_policy_gpt_validation_v1

Rows: 3

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_evidence_soft_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **reject** | micro_f1=95.1% | [inspection](docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md) |
| `exect_s1_evidence_standard_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **hold** | micro_f1=95.8% | [inspection](docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md) |
| `exect_s1_evidence_strict_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **hold** | micro_f1=96.3% | [inspection](docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md) |

## exect_s1_field_family_prompt_graph_gpt_cap25_v1

Rows: 3

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_prompt_graph_pg1_parallel_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | field_family_parallel | L1_llm_constrained | during | cap25 | **reject** | micro_f1=86.5% | [inspection](docs/experiments/exect/exect_s1_field_family_prompt_graph_gpt_cap25_v1_inspection_20260521.md) |
| `exect_s1_prompt_graph_pg2_sequential_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | field_family_prompt_graph | L1_llm_constrained | during | cap25 | **reject** | micro_f1=87.1% | [inspection](docs/experiments/exect/exect_s1_field_family_prompt_graph_gpt_cap25_v1_inspection_20260521.md) |
| `exect_s1_prompt_graph_pg0_single_pass_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **hold** | micro_f1=95.8% | [inspection](docs/experiments/exect/exect_s1_field_family_prompt_graph_gpt_cap25_v1_inspection_20260521.md) |

## exect_s1_full_ladder_gpt_validation_v1

Rows: 4

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_full_ladder_d1_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | D1_deterministic_only | eval_only | cap25 | **exploratory** | micro_f1=58.4% | [inspection](docs/experiments/exect/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md) |
| `exect_s1_full_ladder_l0_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L0_llm_only | during | cap25 | **exploratory** | micro_f1=60.0% | [inspection](docs/experiments/exect/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md) |
| `exect_s1_full_ladder_l1_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **exploratory** | micro_f1=67.7% | [inspection](docs/experiments/exect/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md) |
| `exect_s1_full_ladder_l1_policy_full` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during, eval_only | full_validation | **hold** | micro_f1=92.3% | [inspection](docs/experiments/exect/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md) |

## exect_s1_generalization_gpt_test_v1

Rows: 1

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s0_s1_validation_test` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during, eval_only | test_holdout | **hold** | micro_f1=77.8% | [inspection](docs/experiments/exect/exect_s0_label_policy_v4_10_implementation.md) |

## exect_s1_interleaving_gpt_validation_v1

Rows: 4

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_interleaving_h1_post_bridge_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | H1_post_deterministic | during, post | cap25 | **exploratory** | micro_f1=95.8% | [inspection](docs/experiments/exect/exect_s1_interleaving_gpt_validation_v1_inspection_20260520.md) |
| `exect_s1_interleaving_h2_pre_vocab_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | H2_pre_deterministic | pre, during | cap25 | **exploratory** | micro_f1=90.9% | [inspection](docs/experiments/exect/exect_s1_interleaving_gpt_validation_v1_inspection_20260520.md) |
| `exect_s1_interleaving_h1_post_bridge` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | H1_post_deterministic | during, post | full_validation | **hold** | micro_f1=92.3% | [inspection](docs/experiments/exect/exect_s1_interleaving_gpt_validation_v1_inspection_20260520.md) |
| `exect_s1_interleaving_h2_pre_vocab` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | H2_pre_deterministic | pre, during | full_validation | **reject** | micro_f1=87.5% | [inspection](docs/experiments/exect/exect_s1_interleaving_gpt_validation_v1_inspection_20260520.md) |

## exect_s1_interleaving_gpt_validation_v2

Rows: 4

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_interleaving_h1_post_bridge_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | H1_post_deterministic | during, post | cap25 | **exploratory** | micro_f1=95.8% | [inspection](docs/experiments/exect/exect_s1_interleaving_gpt_validation_v2_inspection_20260520.md) |
| `exect_s1_interleaving_l1_raw_no_bridges_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **exploratory** | micro_f1=72.8% | [inspection](docs/experiments/exect/exect_s1_interleaving_gpt_validation_v2_inspection_20260520.md) |
| `exect_s1_interleaving_h1_post_bridge` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | H1_post_deterministic | during, post | full_validation | **hold** | micro_f1=92.3% | [inspection](docs/experiments/exect/exect_s1_interleaving_gpt_validation_v2_inspection_20260520.md) |
| `exect_s1_interleaving_l1_raw_no_bridges` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | full_validation | **exploratory** | micro_f1=68.6% | [inspection](docs/experiments/exect/exect_s1_interleaving_gpt_validation_v2_inspection_20260520.md) |

## exect_s1_interleaving_qwen_validation_v1

Rows: 4

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_interleaving_h1_post_bridge_cap25_ollama` | exect_v2 | exect_s1 | qwen35b | single_pass | H1_post_deterministic | during, post | cap25 | **hold** | micro_f1=80.7% | [inspection](docs/experiments/exect/exect_s1_interleaving_qwen_validation_v1_inspection_20260520.md) |
| `exect_s1_interleaving_l1_raw_no_bridges_cap25_ollama` | exect_v2 | exect_s1 | qwen35b | single_pass | L1_llm_constrained | during | cap25 | **exploratory** | micro_f1=71.4% | [inspection](docs/experiments/exect/exect_s1_interleaving_qwen_validation_v1_inspection_20260520.md) |
| `exect_s1_interleaving_h1_post_bridge_ollama` | exect_v2 | exect_s1 | qwen35b | single_pass | H1_post_deterministic | during, post | full_validation | **hold** | micro_f1=79.0% | [inspection](docs/experiments/exect/exect_s1_interleaving_qwen_validation_v1_inspection_20260520.md) |
| `exect_s1_interleaving_l1_raw_no_bridges_ollama` | exect_v2 | exect_s1 | qwen35b | single_pass | L1_llm_constrained | during | full_validation | **exploratory** | micro_f1=66.2% | [inspection](docs/experiments/exect/exect_s1_interleaving_qwen_validation_v1_inspection_20260520.md) |

## exect_s1_ladder_optimizer_automation_v1

Rows: 3

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_full_ladder_l0_bootstrap_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | optimizer_compiled_single_pass | L0_llm_only | during | cap25 | **pending** | — | [inspection](docs/experiments/exect/exect_s1_ladder_optimizer_automation_thesis_20260521.md) |
| `exect_s1_full_ladder_l0_labeled_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | optimizer_compiled_single_pass | L0_llm_only | during | cap25 | **pending** | — | [inspection](docs/experiments/exect/exect_s1_ladder_optimizer_automation_thesis_20260521.md) |
| `exect_s1_full_ladder_l1_labeled_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | optimizer_compiled_single_pass | L1_llm_constrained | during | cap25 | **pending** | — | [inspection](docs/experiments/exect/exect_s1_ladder_optimizer_automation_thesis_20260521.md) |

## exect_s1_medication_pre_vocab_slice_gpt_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_interleaving_h2_medication_pre_vocab_slice` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | H2_pre_deterministic | pre, during | slice | **reject** | micro_f1=92.0% | [inspection](docs/experiments/exect/exect_s1_medication_pre_vocab_slice_gpt_inspection_20260520.md) |
| `exect_s1_interleaving_l1_baseline_medication_slice` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | slice | **hold** | micro_f1=93.3% | [inspection](docs/experiments/exect/exect_s1_medication_pre_vocab_slice_gpt_inspection_20260520.md) |

## exect_s1_optimizer_gpt_cap25_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_optimizer_bootstrap_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | optimizer_compiled_single_pass | L1_llm_constrained | during | cap25 | **reject** | micro_f1=90.7% | [inspection](docs/experiments/exect/exect_s1_optimizer_gpt_cap25_v1_inspection_20260521.md) |
| `exect_s1_optimizer_baseline_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **hold** | micro_f1=95.8% | [inspection](docs/experiments/exect/exect_s1_optimizer_gpt_cap25_v1_inspection_20260521.md) |

## exect_s1_pipeline_stage_graph_gpt_cap25_v1

Rows: 5

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_stage_graph_g3_family_split_merge_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | section_aware | L1_llm_constrained | during | cap25 | **reject** | micro_f1=83.3% | [inspection](docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md) |
| `exect_s1_stage_graph_g2_raw_post_bridge_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | H1_post_deterministic | during, post | cap25 | **hold** | micro_f1=95.8% | [inspection](docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md) |
| `exect_s1_stage_graph_g1_l1_policy_bridges_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **hold** | micro_f1=95.8% | [inspection](docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md) |
| `exect_s1_stage_graph_g1_l1_policy_no_bridges_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **hold** | micro_f1=72.8% | [inspection](docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md) |
| `exect_s1_stage_graph_g2_extract_verify_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | verify_repair | L1_llm_constrained | during | cap25 | **reject** | micro_f1=72.8% | [inspection](docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md) |

## exect_s1_prompt_policy_gpt_validation_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_prompt_policy_v4_10_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **hold** | micro_f1=95.8% | [inspection](docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md) |
| `exect_s1_prompt_policy_v4_11_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **reject** | micro_f1=95.1% | [inspection](docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md) |

## exect_s1_qwen_diagnosis_stabilized_v1

Rows: 3

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_qwen_v4_12_diagnosis_stabilized_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | H1_post_deterministic | post | cap25 | **hold** | micro_f1=93.8% | [inspection](docs/experiments/exect/exect_s1_qwen_v4_12_diagnosis_stabilized_preregistration_20260521.md) |
| `exect_s1_qwen_v4_12_diagnosis_stabilized_cap25_ollama` | exect_v2 | exect_s1 | qwen35b | single_pass | H1_post_deterministic | post | cap25 | **reject** | micro_f1=83.8% | [inspection](docs/experiments/exect/exect_s1_qwen_v4_12_diagnosis_stabilized_cap25_inspection_20260521.md) |
| `exect_s1_qwen_v4_12_diagnosis_stabilized_full_ollama` | exect_v2 | exect_s1 | qwen35b | single_pass | H1_post_deterministic | post | full_validation | **blocked** | — | [inspection](docs/experiments/exect/exect_s1_qwen_v4_12_diagnosis_stabilized_cap25_inspection_20260521.md) |

## exect_s1_s4_clean_ladder_qwen_validation_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s2_clean_ladder_v1_full_ollama` | exect_v2 | exect_s2 | qwen35b | single_pass | H1_post_deterministic | post | full_validation | **freeze** | micro_f1=84.4% | [inspection](docs/experiments/exect/exect_s1_clean_ladder_qwen_validation_v1_inspection_20260525.md) |
| `exect_s3_clean_ladder_v1_full_ollama` | exect_v2 | exect_s3 | qwen35b | single_pass | H1_post_deterministic | post | full_validation | **freeze** | micro_f1=75.3% | [inspection](docs/experiments/exect/exect_s1_clean_ladder_qwen_validation_v1_inspection_20260525.md) |

## exect_s1_seizure_pre_vocab_slice_gpt_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_interleaving_h2_seizure_pre_vocab_slice` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | H2_pre_deterministic | pre, during | slice | **reject** | micro_f1=90.3% | [inspection](docs/experiments/exect/exect_s1_seizure_pre_vocab_slice_gpt_inspection_20260520.md) |
| `exect_s1_interleaving_l1_baseline_seizure_slice` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | slice | **hold** | micro_f1=93.5% | [inspection](docs/experiments/exect/exect_s1_seizure_pre_vocab_slice_gpt_inspection_20260520.md) |

## exect_s1_seizure_prompt_policy_qwen_v1

Rows: 3

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_seizure_prompt_policy_v4_11_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during, post | cap25 | **hold** | micro_f1=95.1% | [inspection](docs/experiments/exect/exect_s1_seizure_prompt_policy_qwen_v1_inspection_20260520.md) |
| `exect_s1_seizure_prompt_policy_v4_11_cap25_ollama` | exect_v2 | exect_s1 | qwen35b | single_pass | H1_post_deterministic | during, post | cap25 | **hold** | micro_f1=85.4% | [inspection](docs/experiments/exect/exect_s1_seizure_prompt_policy_qwen_v1_inspection_20260520.md) |
| `exect_s1_seizure_prompt_policy_v4_11_full_ollama` | exect_v2 | exect_s1 | qwen35b | single_pass | H1_post_deterministic | during, post | full_validation | **hold** | micro_f1=84.3% | [inspection](docs/experiments/exect/exect_s1_seizure_prompt_policy_qwen_v1_inspection_20260520.md) |

## exect_s1_stage_executor_gpt_cap25_v1

Rows: 5

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_stage_executor_e2_post_bridges_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | H1_post_deterministic | during, post | cap25 | **hold** | micro_f1=95.8% | [inspection](docs/experiments/exect/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md) |
| `exect_s1_stage_executor_e3_all_family_hints_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | H2_pre_deterministic | pre, during | cap25 | **reject** | micro_f1=90.9% | [inspection](docs/experiments/exect/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md) |
| `exect_s1_stage_executor_e4_seizure_hints_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | H2_pre_deterministic | pre, during | cap25 | **reject** | micro_f1=92.8% | [inspection](docs/experiments/exect/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md) |
| `exect_s1_stage_executor_e5_medication_hints_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | H2_pre_deterministic | pre, during | cap25 | **reject** | micro_f1=93.3% | [inspection](docs/experiments/exect/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md) |
| `exect_s1_stage_executor_e1_inline_bridges_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **hold** | micro_f1=95.8% | [inspection](docs/experiments/exect/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md) |

## exect_s1_verification_gpt_validation_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_verification_single_pass_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **hold** | micro_f1=95.8% | [inspection](docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md) |
| `exect_s1_verification_verify_repair_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | verify_repair | L1_llm_constrained | during | cap25 | **reject** | micro_f1=86.4% | [inspection](docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md) |

## exect_s2_s3_clean_ladder_gpt_validation_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s2_clean_ladder_v1_full` | exect_v2 | exect_s2 | gpt4_1_mini | single_pass | H1_post_deterministic | post | full_validation | **freeze** | micro_f1=82.7% | [inspection](docs/archive/experiments/exect/s0_s1_label_policy_trail/exect_s2_s3_clean_ladder_gpt_validation_v1_inspection_20260525.md) |
| `exect_s3_clean_ladder_v1_full` | exect_v2 | exect_s3 | gpt4_1_mini | single_pass | H1_post_deterministic | post | full_validation | **freeze** | micro_f1=74.4% | [inspection](docs/archive/experiments/exect/s0_s1_label_policy_trail/exect_s2_s3_clean_ladder_gpt_validation_v1_inspection_20260525.md) |

## exect_s3_epilepsy_cause_bridge_gpt_cap25_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s3_cause_k0_k1_cap25` | exect_v2 | exect_s3 | gpt4_1_mini | single_pass | H1_post_deterministic | post | cap25 | **hold** | epilepsy_cause_f1=20.0% | [inspection](docs/experiments/exect/exect_s3_epilepsy_cause_bridge_gpt_cap25_v1_inspection_20260521.md) |
| `exect_s3_cause_l1_baseline_cap25` | exect_v2 | exect_s3 | gpt4_1_mini | single_pass | H1_post_deterministic | post | cap25 | **hold** | epilepsy_cause_f1=0.0% | [inspection](docs/experiments/exect/exect_s3_epilepsy_cause_bridge_gpt_cap25_v1_inspection_20260521.md) |

## exect_s4_epilepsy_cause_bridge_gpt_full_validation_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s4_cause_k0_k1_full` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | H1_post_deterministic | post | full_validation | **hold** | epilepsy_cause_f1=21.1% | [inspection](docs/experiments/exect/exect_s4_epilepsy_cause_bridge_gpt_full_validation_v1_inspection_20260521.md) |
| `exect_s4_cause_l1_baseline_full` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | L1_llm_constrained | during | full_validation | **hold** | epilepsy_cause_f1=10.5% | [inspection](docs/experiments/exect/exect_s4_epilepsy_cause_bridge_gpt_full_validation_v1_inspection_20260521.md) |

## exect_s4_frequency_deterministic_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s4_frequency_h2_pre_vocab_cap25` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | H2_pre_deterministic | pre, during | cap25 | **reject** | micro_f1=71.5% | [inspection](docs/experiments/exect/exect_s4_frequency_deterministic_gpt_inspection_20260520.md) |
| `exect_s4_frequency_l1_baseline_cap25` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **hold** | micro_f1=69.2% | [inspection](docs/experiments/exect/exect_s4_frequency_deterministic_gpt_inspection_20260520.md) |

## exect_s4_frequency_structured_slots_gpt_cap25_v1

Rows: 1

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s4_frequency_slots_s2_structured_cap25` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | H2_pre_deterministic | pre, during, post | cap25 | **hold** | seizure_frequency_f1=51.0% | [inspection](docs/experiments/exect/exect_s4_frequency_structured_slots_gpt_cap25_v1_inspection_20260521.md) |

## exect_s4_frequency_surface_repair_gpt_cap25_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s4_frequency_surface_r1_post_merge_cap25` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | H1_post_deterministic | during, post | cap25 | **reject** | seizure_frequency_f1=48.1% | [inspection](docs/experiments/exect/exect_s4_frequency_surface_repair_gpt_cap25_v1_inspection_20260521.md) |
| `exect_s4_frequency_surface_r0_control_cap25` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | L1_llm_constrained | during, post | cap25 | **hold** | seizure_frequency_f1=51.0% | [inspection](docs/experiments/exect/exect_s4_frequency_surface_repair_gpt_cap25_v1_inspection_20260521.md) |

## exect_s4_temporality_deterministic_v1

Rows: 4

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s4_temporality_h1_post_classifier_cap25` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | H1_post_deterministic | during, post | cap25 | **hold** | field_precision.medication_temporality=61.3% | [inspection](docs/experiments/exect/exect_s4_temporality_deterministic_gpt_inspection_20260520.md) |
| `exect_s4_temporality_l1_baseline_cap25` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **hold** | field_precision.medication_temporality=46.8% | [inspection](docs/experiments/exect/exect_s4_temporality_deterministic_gpt_inspection_20260520.md) |
| `exect_s4_temporality_h1_post_classifier_full` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | H1_post_deterministic | during, post | full_validation | **reject** | field_precision.medication_temporality=56.5% | [inspection](docs/experiments/exect/exect_s4_temporality_deterministic_gpt_inspection_20260520.md) |
| `exect_s4_temporality_l1_baseline_full` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | L1_llm_constrained | during | full_validation | **hold** | field_precision.medication_temporality=46.4% | [inspection](docs/experiments/exect/exect_s4_temporality_deterministic_gpt_inspection_20260520.md) |

## exect_s5_frequency_verify_v2b_model_comparison

Rows: 3

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full` | exect_v2 | exect_s5 | gpt4_1_mini | verify_repair | H2_pre_deterministic, H1_post_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | full_validation | **freeze** | micro_f1=85.8% | [inspection](docs/experiments/exect/exect_s5_frequency_verifier_v2b_full_validation_promotion_review_20260524.md) |
| `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt5_5_openai` | exect_v2 | exect_s5 | gpt5_5 | verify_repair | H2_pre_deterministic, H1_post_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | full_validation | **hold** | micro_f1=82.6% | [inspection](docs/experiments/exect/exect_s5_best_closed_gpt5_5_anchor_inspection_20260526.md) |
| `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_ollama` | exect_v2 | exect_s5 | qwen35b | verify_repair | H2_pre_deterministic, H1_post_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | full_validation | **freeze** | micro_f1=85.4% | [inspection](docs/experiments/synthesis/l1_2_s5_local_vs_closed_comparison_20260525.md) |

## exect_schema_complexity_gpt_validation_v1

Rows: 4

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s0_s1_validation_full` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during, eval_only | full_validation | **freeze** | micro_f1=92.3% | [inspection](docs/experiments/exect/exect_s0_label_policy_v4_10_implementation.md) |
| `exect_s2_validation_full` | exect_v2 | exect_s2 | gpt4_1_mini | single_pass | L1_llm_constrained | during, eval_only | full_validation | **freeze** | micro_f1=80.9% | [inspection](docs/experiments/exect/exect_s2_validation_full_gpt4_1_mini_inspection_20260520.md) |
| `exect_s3_validation_full` | exect_v2 | exect_s3 | gpt4_1_mini | single_pass | L1_llm_constrained | during, eval_only | full_validation | **freeze** | micro_f1=72.1% | [inspection](docs/experiments/exect/exect_s3_validation_full_gpt4_1_mini_inspection_20260520.md) |
| `exect_s4_validation_full` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | L1_llm_constrained | during, eval_only | full_validation | **freeze** | micro_f1=65.5% | [inspection](docs/experiments/exect/exect_s4_validation_full_v1_2_gpt4_1_mini_inspection_20260520.md) |

## gan_s0_architecture_gpt_validation_v1

Rows: 3

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_synthesis_bootstrap_full_validation` | gan_2026 | gan_s0 | gpt4_1_mini | optimizer_compiled_single_pass | L1_llm_constrained | during, eval_only | full_validation | **superseded** | monthly_frequency_accuracy=62.9% | [inspection](docs/experiments/gan/gan_s0_gepa_vs_synthesis_decision_20260519.md) |
| `gan_s0_temporal_candidates_verify_repair_full_validation_guardrails` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | full_validation | **promote** | monthly_frequency_accuracy=65.1% | [inspection](docs/experiments/gan/gan_s0_gpt4_1_mini_temporal_candidates_full_validation_decision_20260520.md) |
| `gan_s0_verify_repair_full_validation` | gan_2026 | gan_s0 | gpt4_1_mini | verify_repair | H1_post_deterministic | during, post | full_validation | **superseded** | monthly_frequency_accuracy=65.4% | [inspection](docs/experiments/gan/gan_s0_verify_repair_full_validation_v2_20260519.md) |

## gan_s0_architecture_qwen_validation_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_direct_full_validation_guardrails` | gan_2026 | gan_s0 | qwen35b | direct_single_pass | L1_llm_constrained | during, eval_only | full_validation | **exploratory** | monthly_frequency_accuracy=55.9% | [inspection](docs/experiments/gan/gan_s0_qwen35b_direct_full_validation_guardrails_error_analysis.md) |
| `gan_s0_temporal_candidates_verify_repair_full_validation_guardrails` | gan_2026 | gan_s0 | qwen35b | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | full_validation | **promote** | monthly_frequency_accuracy=65.8% | [inspection](docs/experiments/gan/gan_s0_temporal_candidates_v1_1_full_validation_decision_20260519.md) |

## gan_s0_candidate_builder_gap_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_candidate_builder_gap_v1_full_validation` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | full_validation | **promote** | monthly_frequency_accuracy=80.6% | [inspection](docs/experiments/gan/gan_s0_r10_promotion_holdout_selection_review_20260526.md) |
| `gan_s0_candidate_builder_gap_v1_slice` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | slice | **promote** | monthly_frequency_accuracy=92.0% | [inspection](docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md) |

## gan_s0_candidate_builder_gap_v1_model_comparison

Rows: 1

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_candidate_builder_gap_v1_ollama_full_validation` | gan_2026 | gan_s0 | qwen35b | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | full_validation | **freeze** | monthly_frequency_accuracy=70.7% | [inspection](docs/experiments/gan/gan_s0_r10_promotion_holdout_selection_review_20260526.md) |

## gan_s0_evidence_policy_gpt_validation_v1

Rows: 3

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_evidence_model_quote_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | cap25 | **hold** | monthly_frequency_accuracy=44.0% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |
| `gan_s0_evidence_optional_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | cap25 | **reject** | monthly_frequency_accuracy=40.0% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |
| `gan_s0_evidence_span_check_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | cap25 | **reject** | monthly_frequency_accuracy=55.6% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |

## gan_s0_expanded_builders_prose_gpt_cap50_v1

Rows: 1

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_expanded_builders_prose_cap50` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | cap50 | **hold** | monthly_frequency_accuracy=68.0% | [inspection](docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_cap50_v1_inspection_20260521.md) |

## gan_s0_expanded_builders_prose_gpt_full_validation_v1

Rows: 1

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_expanded_builders_prose_full_validation` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | full_validation | **superseded** | monthly_frequency_accuracy=68.1% | [inspection](docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_full_validation_v1_inspection_20260521.md) |

## gan_s0_expanded_builders_prose_model_comparison_v1

Rows: 4

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_expanded_builders_prose_full_validation_gemini31_flash_lite` | gan_2026 | gan_s0 | gemini | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | full_validation | **hold** | monthly_frequency_accuracy=72.6% | [inspection](docs/experiments/gan/gan_s0_expanded_builders_prose_gemini_full_validation_v1_inspection_20260521.md) |
| `gan_s0_expanded_builders_prose_cap25_ollama` | gan_2026 | gan_s0 | qwen35b | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | cap25 | **hold** | monthly_frequency_accuracy=48.0% | [inspection](docs/experiments/gan/gan_s0_expanded_builders_prose_qwen_cap25_v1_inspection_20260522.md) |
| `gan_s0_expanded_builders_prose_full_validation_ollama` | gan_2026 | gan_s0 | qwen35b | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | full_validation | **pending** | — | [inspection](docs/experiments/gan/gan_s0_expanded_builders_prose_qwen_full_validation_v1_preregistration_20260521.md) |
| `gan_s0_expanded_builders_prose_smoke_ollama` | gan_2026 | gan_s0 | qwen35b | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | smoke | **hold** | schema_valid_prediction_rate=100.0% | [inspection](docs/experiments/gan/gan_s0_expanded_builders_prose_qwen_full_validation_v1_preregistration_20260521.md) |

## gan_s0_expanded_builders_vr_gpt_full_validation_v1

Rows: 1

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_expanded_builders_vr_full_validation` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | full_validation | **hold** | monthly_frequency_accuracy=65.8% | [inspection](docs/experiments/gan/gan_s0_expanded_builders_vr_gpt_full_validation_v1_inspection_20260521.md) |

## gan_s0_gpt4_1_mini_error_taxonomy_policy_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_constrained_verifier_slice` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_adjudicate_constrained_verifier | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | slice | **reject** | monthly_frequency_accuracy=36.0% | [inspection](docs/experiments/gan/gan_s0_candidate_constrained_verifier_gpt_slice_v1_inspection_20260522.md) |
| `gan_s0_error_taxonomy_policy_v1_4_slice` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | slice | **hold** | monthly_frequency_accuracy=36.0% | [inspection](docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md) |

## gan_s0_gpt4_1_mini_multiple_answer_selector_v1

Rows: 1

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_multiple_answer_det_selector_slice` | gan_2026 | gan_s0 | gpt4_1_mini | multiple_answer_det_selector | L1_llm_constrained, H4_deterministic_first_llm_adjudicates | pre, post | slice | **reject** | monthly_frequency_accuracy=0.0% | [inspection](docs/experiments/gan/gan_s0_multiple_answer_selector_gpt_slice_v1_inspection_20260522.md) |

## gan_s0_gpt4_1_mini_targeted_examples_v1

Rows: 1

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_targeted_examples_min7_slice` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | slice | **reject** | monthly_frequency_accuracy=36.0% | [inspection](docs/experiments/gan/gan_s0_targeted_examples_min7_gpt_slice_v1_inspection_20260523.md) |

## gan_s0_hard_slice_qwen_architecture_v1

Rows: 7

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_direct_regression_slice_guardrails` | gan_2026 | gan_s0 | qwen35b | direct_single_pass | L1_llm_constrained | during, eval_only | slice | **exploratory** | monthly_frequency_accuracy=71.4% | [inspection](docs/experiments/gan/gan_s0_qwen35b_regression_slice_inspection_20260519.md) |
| `gan_s0_labeled_fewshot_regression_slice_guardrails` | gan_2026 | gan_s0 | qwen35b | direct_single_pass | L1_llm_constrained | during, eval_only | slice | **exploratory** | — | [inspection](pending_backfill) |
| `gan_s0_react_temporal_tools_regression_slice_guardrails` | gan_2026 | gan_s0 | qwen35b | react_temporal_tools | H3_interleaved_tool_hybrid | tool_during, during | slice | **reject** | monthly_frequency_accuracy=42.9% | [inspection](docs/experiments/gan/gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails_inspection_20260520.md) |
| `gan_s0_temporal_candidates_verify_repair_regression_slice_guardrails` | gan_2026 | gan_s0 | qwen35b | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | slice | **exploratory** | monthly_frequency_accuracy=100.0% | [inspection](docs/experiments/gan/gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_b1_error_analysis.md) |
| `gan_s0_temporal_event_table_regression_slice_guardrails` | gan_2026 | gan_s0 | qwen35b | temporal_event_table_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | slice | **exploratory** | monthly_frequency_accuracy=100.0% | [inspection](docs/experiments/gan/gan_s0_qwen35b_temporal_event_table_regression_slice_b2_error_analysis.md) |
| `gan_s0_labeled_fewshot_verify_repair_regression_slice_guardrails` | gan_2026 | gan_s0 | qwen35b | verify_repair | H1_post_deterministic | during, post | slice | **exploratory** | — | [inspection](pending_backfill) |
| `gan_s0_verify_repair_regression_slice_guardrails` | gan_2026 | gan_s0 | qwen35b | verify_repair | H1_post_deterministic | during, post | slice | **exploratory** | monthly_frequency_accuracy=46.2% | [inspection](docs/experiments/gan/gan_s0_qwen35b_verify_repair_regression_slice_guardrails_error_analysis.md) |

## gan_s0_implementation_variant_gpt_cap25_v1

Rows: 4

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_impl_i0_cand_prose_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | slice | **reject** | monthly_frequency_accuracy=52.0% | [inspection](docs/experiments/gan/gan_s0_implementation_variant_gpt_cap25_v1_inspection_20260521.md) |
| `gan_s0_impl_i1_cand_table_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | slice | **hold** | monthly_frequency_accuracy=56.0% | [inspection](docs/experiments/gan/gan_s0_implementation_variant_gpt_cap25_v1_inspection_20260521.md) |
| `gan_s0_impl_i2_cand_json_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | slice | **hold** | monthly_frequency_accuracy=56.0% | [inspection](docs/experiments/gan/gan_s0_implementation_variant_gpt_cap25_v1_inspection_20260521.md) |
| `gan_s0_impl_i3_cand_bullets_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | slice | **hold** | monthly_frequency_accuracy=56.0% | [inspection](docs/experiments/gan/gan_s0_implementation_variant_gpt_cap25_v1_inspection_20260521.md) |

## gan_s0_implementation_variant_gpt_cap50_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_impl_i0_cand_prose_cap50` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | cap50 | **hold** | monthly_frequency_accuracy=62.0% | [inspection](docs/experiments/gan/gan_s0_implementation_variant_gpt_cap50_v1_inspection_20260521.md) |
| `gan_s0_impl_i1_cand_table_cap50` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | cap50 | **hold** | monthly_frequency_accuracy=62.0% | [inspection](docs/experiments/gan/gan_s0_implementation_variant_gpt_cap50_v1_inspection_20260521.md) |

## gan_s0_l2_exact_policy_model_comparison_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_l2_exact_policy_full` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | full_validation | **freeze** | monthly_frequency_accuracy=78.5% | [inspection](docs/experiments/gan/gan_s0_r10_promotion_holdout_selection_review_20260526.md) |
| `gan_s0_l2_qwen_exact_policy_full_ollama` | gan_2026 | gan_s0 | qwen35b | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | full_validation | **hold** | monthly_frequency_accuracy=69.1% | [inspection](docs/experiments/gan/gan_s0_r10_promotion_holdout_selection_review_20260526.md) |

## gan_s0_l2_qwen_hybrid_resolution_cap25_v1

Rows: 1

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_l2_qwen_hybrid_resolution_cap25_ollama` | gan_2026 | gan_s0 | qwen35b | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | cap25 | **superseded** | monthly_frequency_accuracy=60.0% | [inspection](docs/experiments/gan/gan_s0_r9_recovery_and_exact_policy_summary_20260526.md) |

## gan_s0_pipeline_stage_graph_gpt_cap25_v1

Rows: 5

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_stage_graph_g1_direct_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | direct_single_pass | L1_llm_constrained | during | slice | **reject** | monthly_frequency_accuracy=44.0% | [inspection](docs/experiments/gan/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md) |
| `gan_s0_stage_graph_g2_candidates_adjudicate_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | slice | **hold** | monthly_frequency_accuracy=52.0% | [inspection](docs/experiments/gan/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md) |
| `gan_s0_stage_graph_g3_candidates_extract_repair_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | slice | **reject** | monthly_frequency_accuracy=44.0% | [inspection](docs/experiments/gan/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md) |
| `gan_s0_stage_graph_g2_extract_repair_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | verify_repair | H1_post_deterministic | during, post | slice | **reject** | monthly_frequency_accuracy=44.0% | [inspection](docs/experiments/gan/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md) |
| `gan_s0_stage_graph_g3_extract_verify_repair_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | verify_repair | H1_post_deterministic | during, post | slice | **reject** | monthly_frequency_accuracy=44.0% | [inspection](docs/experiments/gan/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md) |

## gan_s0_prompt_policy_gpt_validation_v1

Rows: 3

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_prompt_policy_guardrails_port_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | cap25 | **hold** | monthly_frequency_accuracy=48.0% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |
| `gan_s0_prompt_policy_synthesis_port_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | cap25 | **reject** | monthly_frequency_accuracy=39.1% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |
| `gan_s0_prompt_policy_temporal_v1_1_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | cap25 | **hold** | monthly_frequency_accuracy=44.0% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |

## gan_s0_stage_executor_gpt_cap25_v1

Rows: 5

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_stage_executor_e3_hybrid_candidates_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | hybrid_temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | slice | **reject** | monthly_frequency_accuracy=41.7% | [inspection](docs/experiments/gan/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md) |
| `gan_s0_stage_executor_e2_llm_candidates_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | llm_temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | slice | **reject** | monthly_frequency_accuracy=29.2% | [inspection](docs/experiments/gan/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md) |
| `gan_s0_stage_executor_e5_llm_vr_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | llm_temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | slice | **reject** | monthly_frequency_accuracy=29.2% | [inspection](docs/experiments/gan/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md) |
| `gan_s0_stage_executor_e4_det_vr_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_adjudicate_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | slice | **hold** | monthly_frequency_accuracy=52.0% | [inspection](docs/experiments/gan/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md) |
| `gan_s0_stage_executor_e1_det_candidates_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | slice | **hold** | monthly_frequency_accuracy=52.0% | [inspection](docs/experiments/gan/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md) |

## gan_s0_validation_ladder_gpt_cap25_v1

Rows: 7

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_validation_ladder_v4_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_adjudicate_confirm_only | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | slice | **reject** | monthly_frequency_accuracy=58.3% | [inspection](docs/experiments/gan/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md) |
| `gan_s0_validation_ladder_v3_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_adjudicate_det_evidence | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, post | slice | **reject** | monthly_frequency_accuracy=58.3% | [inspection](docs/experiments/gan/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md) |
| `gan_s0_validation_ladder_v2_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_adjudicate_det_guards | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, post | slice | **hold** | monthly_frequency_accuracy=52.0% | [inspection](docs/experiments/gan/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md) |
| `gan_s0_validation_ladder_v6_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_adjudicate_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | slice | **hold** | monthly_frequency_accuracy=52.0% | [inspection](docs/experiments/gan/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md) |
| `gan_s0_validation_ladder_v5_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_adjudicate_verify_repair_no_guards | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | slice | **reject** | monthly_frequency_accuracy=58.3% | [inspection](docs/experiments/gan/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md) |
| `gan_s0_validation_ladder_v7_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_adjudicate_verify_repair_span_check | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | slice | **reject** | monthly_frequency_accuracy=50.0% | [inspection](docs/experiments/gan/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md) |
| `gan_s0_validation_ladder_v0_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | slice | **hold** | monthly_frequency_accuracy=52.0% | [inspection](docs/experiments/gan/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md) |

## gan_s0_verification_gpt_validation_v1

Rows: 3

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_verification_direct_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | direct_single_pass | L1_llm_constrained | during | cap25 | **hold** | monthly_frequency_accuracy=44.0% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |
| `gan_s0_verification_temporal_verify_repair_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | cap25 | **hold** | monthly_frequency_accuracy=44.0% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |
| `gan_s0_verification_verify_repair_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | verify_repair | L1_llm_constrained | during | cap25 | **hold** | monthly_frequency_accuracy=44.0% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |

## model_suite_frozen_architecture_v1

Rows: 6

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s0_s1_validation_full_claude_sonnet_4_6_anthropic` | exect_v2 | exect_s1 | claude_sonnet46 | single_pass | L1_llm_constrained | during, eval_only | full_validation | **hold** | micro_f1=81.8% | [inspection](docs/experiments/synthesis/model_suite_claude_sonnet_4_6_full_validation_v1_inspection_20260522.md) |
| `exect_s0_s1_validation_full_gemini3_flash` | exect_v2 | exect_s1 | gemini3flash | single_pass | L1_llm_constrained | during, eval_only | full_validation | **hold** | micro_f1=89.9% | [inspection](docs/experiments/synthesis/model_suite_gemini3_flash_full_validation_v1_inspection_20260522.md) |
| `exect_s4_validation_full_claude_sonnet_4_6_anthropic` | exect_v2 | exect_s4 | claude_sonnet46 | single_pass | H1_post_deterministic, L1_llm_constrained | during, post, eval_only | full_validation | **hold** | micro_f1=65.1% | [inspection](docs/experiments/synthesis/model_suite_claude_sonnet_4_6_full_validation_v1_inspection_20260522.md) |
| `exect_s4_validation_full_gemini3_flash` | exect_v2 | exect_s4 | gemini3flash | single_pass | H1_post_deterministic, L1_llm_constrained | during, post, eval_only | full_validation | **hold** | micro_f1=63.2% | [inspection](docs/experiments/synthesis/model_suite_gemini3_flash_full_validation_v1_inspection_20260522.md) |
| `gan_s0_expanded_builders_prose_full_validation_claude_sonnet_4_6_anthropic` | gan_2026 | gan_s0 | claude_sonnet46 | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | full_validation | **hold** | monthly_frequency_accuracy=73.0% | [inspection](docs/experiments/synthesis/model_suite_claude_sonnet_4_6_full_validation_v1_inspection_20260522.md) |
| `gan_s0_expanded_builders_prose_full_validation_gemini3_flash` | gan_2026 | gan_s0 | gemini3flash | temporal_candidates_single_pass | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during | full_validation | **hold** | monthly_frequency_accuracy=75.3% | [inspection](docs/experiments/synthesis/model_suite_gemini3_flash_full_validation_v1_inspection_20260522.md) |
