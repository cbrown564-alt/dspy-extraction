# Evidence Matrix

Status: superseded generated index
Replacement: `../component_ceiling_registry.md`

This generated matrix predates the May 28 decomposition pivot and newer R11-R15
decisions. It is retained as provenance only. Do not use it as current
navigation until regenerated from a refreshed registry.

Generated: 2026-05-21

Each cell shows the strongest registered row for that schema and study type. Use this as a navigation surface, not as a claim that unlike cells are directly comparable.

| Schema | Architecture | Interleaving | Prompt policy | Optimization | Model | Schema ladder | Scale | Verification | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gan_s0 | `gan_s0_temporal_candidates_verify_repair_full_validation_guardrails`<br>promote<br>monthly_frequency_accuracy=65.1% | `gan_s0_react_temporal_tools_regression_slice_guardrails`<br>reject<br>monthly_frequency_accuracy=42.9% | `gan_s0_prompt_policy_guardrails_port_cap25`<br>hold<br>monthly_frequency_accuracy=48.0% | `gan_s0_synthesis_bootstrap_full_validation`<br>superseded<br>monthly_frequency_accuracy=62.9% | - | - | - | `gan_s0_verification_direct_cap25`<br>hold<br>monthly_frequency_accuracy=44.0% | `gan_s0_evidence_model_quote_cap25`<br>hold<br>monthly_frequency_accuracy=44.0% |
| exect_s1 | `exect_s1_interleaving_l1_baseline_medication_slice`<br>hold<br>micro_f1=93.3% | `exect_s1_interleaving_h1_post_bridge`<br>hold<br>micro_f1=92.3% | `exect_s1_seizure_prompt_policy_v4_11_full_ollama`<br>hold<br>micro_f1=84.3% | `exect_s1_optimizer_baseline_cap25`<br>hold<br>micro_f1=95.8% | `exect_s0_s1_validation_full_ollama`<br>hold<br>micro_f1=79.0% | `exect_s0_s1_validation_full`<br>freeze<br>micro_f1=92.3% | `exect_s0_s1_validation_test`<br>hold<br>micro_f1=77.8% | `exect_s1_verification_single_pass_cap25`<br>hold<br>micro_f1=95.8% | `exect_s1_evidence_standard_cap25`<br>hold<br>micro_f1=95.8% |
| exect_s2 | - | - | - | - | `exect_s2_validation_full_ollama`<br>hold<br>micro_f1=82.6% | `exect_s2_validation_full`<br>freeze<br>micro_f1=80.9% | - | - | - |
| exect_s3 | - | - | - | - | `exect_s3_validation_full_ollama`<br>hold<br>micro_f1=72.2% | `exect_s3_validation_full`<br>freeze<br>micro_f1=72.1% | - | - | - |
| exect_s4 | `exect_s4_temporality_l1_baseline_full`<br>hold<br>field_precision.medication_temporality=46.4% | `exect_s4_frequency_l1_baseline_cap25`<br>hold<br>micro_f1=69.2% | - | - | `exect_s4_validation_full_ollama`<br>hold<br>micro_f1=67.5% | `exect_s4_validation_full`<br>freeze<br>micro_f1=65.5% | - | - | - |

## Reading Notes

- Rows summarize registered local diagnostics, not published benchmark reproduction.
- Prefer within-cell decision docs and comparison groups before making metric claims.
- Empty cells are useful: they mark open or intentionally deferred paths.
