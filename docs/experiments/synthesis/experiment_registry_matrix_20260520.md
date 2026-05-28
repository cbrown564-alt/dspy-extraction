# Experiment Registry Matrix (Paper-Ready Export)

Status: superseded generated export
Replacement: `README.md` for synthesis status and
`../../component_ceiling_registry.md` for current component status.

This export was generated from an older registry snapshot and predates the May
28 decomposition pivot. It is preserved as historical evidence only.

**Generated:** 2026-05-21  
**Source:** `docs/experiments/synthesis/experiment_registry.json` (registry_rows=130)  
**Filter mode:** `curated`  
**Exported rows:** 72

Grouped by `comparison_group`, then dataset, schema, model, and run scope. Compare rows only within the same comparison group and respect `metric_caveats` on each registry row.

## Caveats

- Individual run directories remain attached in artifact_paths; canonical_run_id is the latest local metric-bearing run for each experiment_id unless later curated.
- Retrospective taxonomy fields are inferred from config/run metadata and should be reviewed before paper-facing analysis.
- Step 3 curated the first canonical anchor rows; non-anchor retrospective rows may still contain generated tags pending later backfill.
- Step 4 added comparison_groups arrays for curated rows that legitimately participate in more than one analysis; comparison_group remains the primary group for simple consumers.
- This is the Step 1 registry seed; controlled vocabularies and validation are planned in later steps.
- This table is for methods/results drafting; it is not published ExECTv2 Table 1 or Gan Real-set reproduction.
- Regenerate after registry updates: `uv run python scripts/export_experiment_registry_matrix.py`.

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

## exect_s1_evidence_policy_gpt_validation_v1

Rows: 3

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_evidence_soft_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **reject** | micro_f1=95.1% | [inspection](docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md) |
| `exect_s1_evidence_standard_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **hold** | micro_f1=95.8% | [inspection](docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md) |
| `exect_s1_evidence_strict_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **hold** | micro_f1=96.3% | [inspection](docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md) |

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

## exect_s1_prompt_policy_gpt_validation_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_prompt_policy_v4_10_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **hold** | micro_f1=95.8% | [inspection](docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md) |
| `exect_s1_prompt_policy_v4_11_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **reject** | micro_f1=95.1% | [inspection](docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md) |

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

## exect_s1_verification_gpt_validation_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s1_verification_single_pass_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **hold** | micro_f1=95.8% | [inspection](docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md) |
| `exect_s1_verification_verify_repair_cap25` | exect_v2 | exect_s1 | gpt4_1_mini | verify_repair | L1_llm_constrained | during | cap25 | **reject** | micro_f1=86.4% | [inspection](docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md) |

## exect_s4_frequency_deterministic_v1

Rows: 2

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s4_frequency_h2_pre_vocab_cap25` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | H2_pre_deterministic | pre, during | cap25 | **reject** | micro_f1=71.5% | [inspection](docs/experiments/exect/exect_s4_frequency_deterministic_gpt_inspection_20260520.md) |
| `exect_s4_frequency_l1_baseline_cap25` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **hold** | micro_f1=69.2% | [inspection](docs/experiments/exect/exect_s4_frequency_deterministic_gpt_inspection_20260520.md) |

## exect_s4_temporality_deterministic_v1

Rows: 4

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect_s4_temporality_h1_post_classifier_cap25` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | H1_post_deterministic | during, post | cap25 | **hold** | field_precision.medication_temporality=61.3% | [inspection](docs/experiments/exect/exect_s4_temporality_deterministic_gpt_inspection_20260520.md) |
| `exect_s4_temporality_l1_baseline_cap25` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | L1_llm_constrained | during | cap25 | **hold** | field_precision.medication_temporality=46.8% | [inspection](docs/experiments/exect/exect_s4_temporality_deterministic_gpt_inspection_20260520.md) |
| `exect_s4_temporality_h1_post_classifier_full` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | H1_post_deterministic | during, post | full_validation | **reject** | field_precision.medication_temporality=56.5% | [inspection](docs/experiments/exect/exect_s4_temporality_deterministic_gpt_inspection_20260520.md) |
| `exect_s4_temporality_l1_baseline_full` | exect_v2 | exect_s4 | gpt4_1_mini | single_pass | L1_llm_constrained | during | full_validation | **hold** | field_precision.medication_temporality=46.4% | [inspection](docs/experiments/exect/exect_s4_temporality_deterministic_gpt_inspection_20260520.md) |

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

## gan_s0_evidence_policy_gpt_validation_v1

Rows: 3

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_evidence_model_quote_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | cap25 | **hold** | monthly_frequency_accuracy=44.0% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |
| `gan_s0_evidence_optional_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | cap25 | **reject** | monthly_frequency_accuracy=40.0% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |
| `gan_s0_evidence_span_check_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | cap25 | **reject** | monthly_frequency_accuracy=55.6% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |

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

## gan_s0_prompt_policy_gpt_validation_v1

Rows: 3

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_prompt_policy_guardrails_port_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | cap25 | **hold** | monthly_frequency_accuracy=48.0% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |
| `gan_s0_prompt_policy_synthesis_port_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | cap25 | **reject** | monthly_frequency_accuracy=39.1% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |
| `gan_s0_prompt_policy_temporal_v1_1_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | cap25 | **hold** | monthly_frequency_accuracy=44.0% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |

## gan_s0_verification_gpt_validation_v1

Rows: 3

| Experiment | Dataset | Schema | Model | Architecture | Hybrid | Interleave | Scope | Outcome | Headline metric | Decision doc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan_s0_verification_direct_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | direct_single_pass | L1_llm_constrained | during | cap25 | **hold** | monthly_frequency_accuracy=44.0% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |
| `gan_s0_verification_temporal_verify_repair_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | temporal_candidates_verify_repair | H2_pre_deterministic, H4_deterministic_first_llm_adjudicates | pre, during, post | cap25 | **hold** | monthly_frequency_accuracy=44.0% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |
| `gan_s0_verification_verify_repair_cap25` | gan_2026 | gan_s0 | gpt4_1_mini | verify_repair | L1_llm_constrained | during | cap25 | **hold** | monthly_frequency_accuracy=44.0% | [inspection](docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md) |
