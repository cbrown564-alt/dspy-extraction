# Script Entrypoint Inventory

Status: active guidance
Date: 2026-05-28
Kanban card: C25 - Script Hygiene And Report Exporter Split

## Purpose

C25 classifies the active `scripts/` surface so C26 can run `ruff` and
`vulture` without treating intentional CLI entrypoints as ordinary dead code.
This pass preserves scorer, loader, split, benchmark bridge, and current
component semantics.

## Current Validators

| Script | Classification | Notes |
| --- | --- | --- |
| `scripts/validate_primitives.py` | current validator | Primitive registry/catalog gate. |
| `scripts/validate_experiment_taxonomy.py` | current validator | Experiment registry/config taxonomy gate. |

## Active Experiment Runners And Utilities

| Script | Classification | Notes |
| --- | --- | --- |
| `scripts/run_experiment.py` | active experiment runner | Thin CLI over `clinical_extraction.experiments.runner`. |
| `scripts/smoke_gan_s0_adapter.py` | active provider smoke utility | Opt-in model/provider adapter smoke path. |
| `scripts/generate_gan_splits.py` | active data utility | Regenerates the documented Gan split file. |

## Current Report Exporters

| Script | Classification | Reusable logic home |
| --- | --- | --- |
| `scripts/evaluate_predictions.py` | current evaluator CLI | `clinical_extraction.evaluation.cli` |
| `scripts/analyze_gan_frequency_run.py` | current Gan report exporter | `clinical_extraction.evaluation.gan_run_analysis` plus script-local CLI assembly |
| `scripts/analyze_gan_policy_probe_g3.py` | current Gan policy-probe exporter | `clinical_extraction.evaluation.gan_policy_probe_g3` |
| `scripts/audit_gan_candidate_builder_gap.py` | current Gan no-model audit exporter | script-local until reused by a current tested report |
| `scripts/audit_gan_residual_candidate_coverage.py` | current Gan residual audit exporter | script-local until reused by a current tested report |
| `scripts/export_gan_candidate_inventory_report.py` | current Gan report exporter | `clinical_extraction.evaluation.gan_candidate_inventory` |
| `scripts/export_gan_exact_frequency_residual_slice.py` | current Gan report exporter | `clinical_extraction.evaluation.gan_residual_slice` |
| `scripts/export_gan_g2_model_arm_comparison_report.py` | current Gan report exporter | `clinical_extraction.evaluation.gan_g2_model_arm_comparison` |
| `scripts/export_gan_multi_event_flags.py` | current Gan report exporter | `clinical_extraction.evaluation.gan_multi_event_flags` |
| `scripts/export_gan_record_report.py` | current Gan report exporter | `clinical_extraction.evaluation.gan_run_analysis` |
| `scripts/export_gan_target_label_split_report.py` | current Gan report exporter | `clinical_extraction.evaluation.gan_target_label_split` |
| `scripts/generate_gan_baseline_report.py` | current Gan report exporter | `clinical_extraction.evaluation.gan_baseline` |
| `scripts/audit_exect_s1_raw_bridge_prompt_split.py` | current ExECT no-model audit exporter | `clinical_extraction.evaluation.exect_s1_split_audit` |
| `scripts/audit_exect_frequency_event_rate_payload.py` | current ExECT no-model audit exporter | `clinical_extraction.evaluation.exect_frequency_event_rate_payload` |
| `scripts/audit_exect_medication_current_rx_lifecycle_payload.py` | current ExECT no-model audit exporter | `clinical_extraction.evaluation.exect_medication_current_rx_lifecycle_payload` |
| `scripts/export_exect_medication_current_rx_ceiling_probe.py` | current ExECT component-ceiling report exporter | `clinical_extraction.evaluation.exect_medication_current_rx_ceiling_probe` |
| `scripts/audit_exect_family_span_payload.py` | current ExECT no-model audit exporter | `clinical_extraction.evaluation.exect_family_span_payload` |
| `scripts/export_experiment_registry_matrix.py` | current registry report exporter | `clinical_extraction.experiments.program_variant_registry` |
| `scripts/report_program_variant_registry.py` | current registry report exporter | `clinical_extraction.experiments.program_variant_registry` |
| `scripts/export_review_queue.py` | current review queue exporter | script-local small CLI |

## Archived One-Offs

These scripts had no active references outside archived docs and were moved to
`archive/scripts/` as provenance-only tooling:

| Archived script | Archived rationale |
| --- | --- |
| `archive/scripts/analyze_exect_qwen_s1_seizure_gap_error_read.py` | Historical Qwen S1 seizure-gap error read; artifact and docs live under `docs/archive/experiments/exect/model_comparison_diagnostics/`. |
| `archive/scripts/analyze_exect_s4_temporality_error_read.py` | Historical S4 medication temporality error read; artifact and docs live under `docs/archive/experiments/exect/frequency_pre_payload_attempts/`. |
| `archive/scripts/replay_exect_s2_comorbidity_residual_slice.py` | Historical residual-slice replay; current ExECT component work no longer depends on active replay. |
| `archive/scripts/replay_exect_s3_epilepsy_cause_residual_slice.py` | Historical residual-slice replay; current ExECT component work no longer depends on active replay. |
| `archive/scripts/replay_gan_canonical_format_residual_slice.py` | Historical Gan canonical-format residual replay; current Gan report exporters use active evaluation modules. |

## C26 Notes

- Treat the active script names above as intentional CLI entrypoints during
  static dead-code triage.
- Prefer moving reusable report logic into `clinical_extraction.evaluation.*`
  when a current report has tests or is reused by another CLI.
- Do not revive archive scripts during `ruff`/`vulture` cleanup unless a current
  card explicitly promotes the report or replay surface.
