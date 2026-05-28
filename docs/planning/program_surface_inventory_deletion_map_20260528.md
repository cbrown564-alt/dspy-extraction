# Program Surface Inventory And Deletion Map

Status: active guidance / C19 archive pass applied
Date: 2026-05-28
Kanban card: C2 - Program Surface Inventory And Deletion Map
Depends on: `docs/planning/thermo_nuclear_codebase_architecture_audit_20260528.md`

## Scope

This inventory maps active versus obsolete Gan/ExECT programs, configs, scripts,
and helper modules after the May 28 component-decomposition pivot. It does not
delete code. It identifies what can be consolidated or archived once behavior,
scorer semantics, and run provenance are protected.

Inputs inspected:

- `docs/current_research_program.md`
- `docs/component_ceiling_registry.md`
- `docs/planning/kanban_plan.md`
- `docs/experiments/gan/README.md`
- `docs/experiments/exect/README.md`
- `docs/experiments/synthesis/README.md`
- active experiment configs under `configs/experiments/`
- archived replay configs under `archive/configs/`
- active program modules under `src/clinical_extraction/programs/`
- scripts under `scripts/` and `archive/scripts/`

Observed surface counts:

- 35 live experiment config JSON files under `configs/experiments/`
- 307 archived experiment config JSON files under `archive/configs/`
- 49 archived run launcher or utility scripts under `archive/scripts/`
- 5 active program modules under `src/clinical_extraction/programs/`
- 35 live Python/PowerShell scripts under `scripts/`

## Active Surfaces To Preserve

| Surface | Files / examples | Current status | Keep because | Validation before movement |
| --- | --- | --- | --- | --- |
| Gan builder-gap v1 | `configs/experiments/gan_s0_candidate_builder_gap_v1_*`; `gan_frequency_s0_temporal_candidates_single_pass` | promoted baseline / synthetic operational default | Current synthetic default until paper-rescored or superseded. | `tests/test_gan_s0_program.py`, `tests/test_gan_scoring.py`, `tests/test_gan_paper_reproduction_scoring.py` |
| Gan D1 v1.2b date/events | `configs/experiments/gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini.json`; `gan_frequency_s0_date_events_candidates_single_pass` | mechanism baseline | Current decomposed Gan mechanism baseline. | `tests/test_gan_s0_program.py`, `tests/test_gan_temporal_events.py`, `tests/test_gan_temporal_candidates.py` |
| Gan scorer modes | `src/clinical_extraction/gan/scoring.py`; `src/clinical_extraction/gan/paper_reproduction_scoring.py` | active benchmark/diagnostic split | Paper comparison now requires `gan2026_paper_reproduction`; canonical mode remains diagnostic. | `tests/test_gan_frequency.py`, `tests/test_gan_scoring.py`, `tests/test_gan_paper_reproduction_scoring.py` |
| Gan candidate audit scripts | `scripts/audit_gan_candidate_builder_gap.py`; `scripts/audit_gan_residual_candidate_coverage.py` | active for G1 | Needed for candidate inventory coverage report. | Run as part of G1 with fixed split and scorer caveats. |
| ExECT clean S1-S4 ladder | `exect_s1_clean_ladder_*`, `exect_s2_clean_ladder_*`, `exect_s3_clean_ladder_*`, `exect_s4_validation_*` configs | diagnostic baseline | Complexity stress-test provenance; not component ceilings. | `tests/test_experiment_configs.py`, family scorer tests |
| ExECT S5 v2b stack | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_*` | promoted operational baseline | Current stacked baseline, useful for later stacking-loss comparison. | `tests/test_exect_s4_program.py`, `tests/test_exect_s5_scoring.py`, `tests/test_exect_s5_frequency_verifier.py` |
| ExECT dataset and scorers | `src/clinical_extraction/datasets/exect.py`; `src/clinical_extraction/evaluation/exect.py` | active policy surface | Encodes audited JSON source, certainty, specificity collapse, and field-family metrics. | `tests/test_exect_loader.py`, `tests/test_exect_scoring.py`, `tests/test_exect_s*_scoring.py` |
| ExECT family primitive logic | `src/clinical_extraction/exect/primitives.py` | active but over-bundled | Contains current medication, diagnosis, seizure-type, and frequency bridge behavior. | Family primitive tests plus `scripts/validate_primitives.py --errors-only` |
| Experiment runner and config validation | `src/clinical_extraction/experiments/runner.py`; `src/clinical_extraction/experiments/config.py` | active orchestration | Required to replay existing configs and generate new controlled runs. | `tests/test_experiment_runner.py`, `tests/test_experiment_configs.py`, `scripts/validate_experiment_taxonomy.py --errors-only` |

## Consolidate, Do Not Delete Yet

| Candidate | Current risk | Replacement target | Retained provenance | Focused validation |
| --- | --- | --- | --- | --- |
| `src/clinical_extraction/programs/gan_frequency_s0.py` | Monolithic Gan S0 program bundles variants, prompts, candidate stages, label repair, metrics, and artifact bridging. | `clinical_extraction/gan/s0/` package with typed variant registry, candidate inventory, target selection, label construction, and prediction bridge modules. | Existing configs, run artifacts, R11-R15 docs, component ceiling registry. | Gan S0 program/scorer/candidate tests; fixture prediction parity for builder-gap v1 and D1 v1.2b. |
| `src/clinical_extraction/programs/exect_s0_s1.py` | Raw extraction, benchmark bridge, prompt policy, and repair policy are entangled; duplicated diagnosis bridge helpers exist in `exect/primitives.py`. | S1 family bridge modules plus typed raw/bridge/final artifact contract. | S1/S2/S3/S4 ladder docs, holdout report, ExECT audit. | S0/S1 program tests, diagnosis/medication primitive tests, ExECT scorer tests. |
| `src/clinical_extraction/programs/exect_s4.py` | S4 component probes and S5 operational stack variants share one module and prediction path. | Split `programs/exect_s5_core.py`, `exect/frequency_verifier.py`, and medication guard module wrappers. | S5 v2b full-validation configs and holdout configs. | S4/S5 program/scorer/verifier tests; S5 artifact-shape parity. |
| `src/clinical_extraction/exect/primitives.py` | Medication, diagnosis, seizure type, and frequency primitives are in one 2k+ line file; frequency payload is not first-class. | Family-specific primitive modules, especially `exect/frequency_payload.py`. | Primitive registry IDs and catalog rows remain stable. | Family primitive tests; primitive registry validation. |
| `src/clinical_extraction/experiments/config.py` | Imports every program variant and keeps a central literal contract table, making obsolete arms sticky. | Program variant registry consumed by config validation and C2 inventory. | Existing config files stay loadable during migration. | Experiment config tests; taxonomy validation. |
| Large monolithic tests | Refactors will produce noisy private-helper import churn. | Stage-level characterization tests, then split by Gan/ExECT component. | Existing tests stay as parity nets until public stage tests replace them. | Existing focused tests plus new stage tests. |

## Archive Or Deletion Candidates

Archive means move out of the live steering/config/script surface only after a
replacement pointer and validation gate are present. It does not mean losing run
provenance.

| Candidate | Current status | Replacement / retained source | Required gate before archive/delete |
| --- | --- | --- | --- |
| Gan entity-first configs: `gan_s0_entity_first_c0_*`, `gan_s0_entity_first_c1_*` | R12 rejected arm; C1 severely regressed. | `docs/experiments/gan/gan_s0_r12_clines_entity_first_pipeline_gate_decision_20260528.md`; run IDs in that decision doc. | Config inventory row links each file to R12 and confirms no active Kanban card depends on rerunning it. |
| Gan self-consistency configs and `archive/scripts/run_self_consistency.py` | R13 rejected for current compute allocation; archived in C19. | `docs/experiments/gan/gan_s0_r13_self_consistency_variance_probe_decision_20260528.md`. | Preserve script/configs in archive unless a new instability hypothesis reopens mechanism. |
| Gan D2/D3 LLM/hybrid date-event configs | Diagnostic/rejected relative to D1 mechanism baseline; archived in C19. | R11/R15 date-stage decisions; D1 v1.2b config remains active. | Keep archive rows loadable and labeled replay/provenance; do not rerun without a new preregistered mechanism hypothesis. |
| Gan v1.2 broad guardrail configs | R15 showed broad relative-anchor/arithmetic guardrails regress; archived in C19. | `gan_s0_r15_d1_guardrail_ablation_decision_20260528.md`; keep D1 v1.2b schema-guard-only. | Ensure reports label arithmetic/broad guardrails as diagnostic or rejected arms. |
| ExECT S4/S5 non-v2b stack variants with no live config | Rejected, diagnostic, or stale implementation branches inside `exect_s4.py`. | ExECT deep review plus S5 v2b config set. | Split S5 core first; then remove unreachable branches with S4/S5 tests green. |
| `scripts/backfill_hybrid_cap25_registry.py` | Hard-coded historical registry backfill, 1k+ lines. | Current registry JSON plus decision docs; future generated views from typed program registry. | Registry validation/export tests pass; each hard-coded row has provenance in archive or registry. |
| `archive/scripts/register_gan_lane_a_cap25_registry.py` | One-off old registry registration; archived in C19. | Same registry-generation replacement as above. | Keep only as provenance; no active docs should instruct use of this script. |
| Registry-derived matrix outputs predating May 28 | Superseded navigation. | `docs/experiments/synthesis/README.md` says registry exports must wait for May 28 statuses. | X1 component registry backfill complete before X3 matrix regeneration. Obsolete research atlas has been permanently removed. |
| `archive/scripts/generate_qwen_configs.py` | One-off config generator; archived in C19. | Model/config compatibility docs if still needed. | Keep only as provenance unless a current model-config workflow explicitly reopens it. |
| Cursor SDK workflow scripts/docs in active tree | Useful provenance but outside current decomposition priority. | `docs/workstreams/cursor_sdk/` index/archive. | Do not delete; file under workstream/archive unless active docs still cite it. |

## Live Config Summary

After C19, the live config tree contains 35 current-authority experiment
configs. Rejected, historical, and replay/provenance configs moved to
`archive/configs/` and remain loadable through `resolve_config_path` by
basename.

| Count | Surface |
| ---: | --- |
| 9 | ExECT S4 cause-bridge K0/K1 with S4 deterministic scorer |
| 6 | ExECT S5 v2b with S5 deterministic scorer |
| 6 | Gan builder-gap v1 promoted baseline with canonical scorer |
| 5 | ExECT S3 clean ladder with S3 deterministic scorer |
| 4 | ExECT S2 clean ladder with S2 deterministic scorer |
| 3 | ExECT S1 clean ladder v2 diagnosis-stable with S1 deterministic scorer |
| 1 | Gan D1 v1.2b schema-guard-only mechanism baseline |
| 1 | Gan G2 candidate-constrained diagnostic model slice |

Immediate implication: `configs/experiments/` is now a current-authority
surface, not a broad historical inventory. The generated
`docs/experiments/synthesis/program_variant_registry.md` is the active map for
both live and archived config rows; archive rows are replay/provenance even when
they match a current-authority variant family.

## C19 Completion Notes

C19 applied this map without changing scorer, loader, split, benchmark bridge,
or metric semantics:

- Archived rejected/historical/replay configs from `configs/experiments/` into
  `archive/configs/`.
- Archived one-off or historical scripts into `archive/scripts/`.
- Kept archived configs loadable through the shared `resolve_config_path`
  helper.
- Regenerated the program variant report with separate active and archived
  config inventory sections.
- Deleted the obsolete generated research atlas surfaces and exporter.

## Cleanup Gates

Before any deletion or archive move:

1. The candidate must have a replacement row in the typed program registry or a
   current decision doc that explains why it is historical.
2. Any run IDs, config paths, scorer modes, model/provider names, and split names
   used in current docs must remain traceable.
3. The relevant focused tests must pass.
4. Scorer semantics must remain unchanged unless an explicit scorer-policy PR
   updates docs and tests.
5. Gan benchmark-facing reports must use `gan2026_paper_reproduction`; canonical
   Gan metrics must be labeled diagnostic or sensitivity views.
6. ExECT Table 1 reproduction must remain blocked until a CUI-aware scorer path
   exists.

## Recommended Next Cleanup Pull

The behavior-preserving program variant registry and first archive/delete pass
are complete. The next cleanup pull is C20:

1. Re-run the strict architecture/modularity review against the C12-C19 end
   state.
2. Update the architecture audit status with closed risks, intentionally
   retained replay-provenance surfaces, and any residual P1/P2 findings.
3. Keep any further archive movement tied to a decision doc, registry row, and
   replay validation.

## Validation Run For This Inventory

The original C2 inventory parsed live experiment configs with PowerShell
`ConvertFrom-Json`, counted script/config surfaces, and cross-checked statuses
against the active May 28 steering docs.

C19 then validated the archive move with:

- `uv run pytest tests/test_program_variant_registry.py tests/test_experiment_configs.py tests/test_experiment_registry_validation.py tests/test_export_registry_matrix.py tests/test_run_self_consistency.py -q` passed, 236 tests.
- `uv run pytest tests/test_experiment_runner.py tests/test_run_experiment_runtime.py -q` passed, 28 tests.
- `uv run python scripts/validate_experiment_taxonomy.py --errors-only` exited
  0 with the documented `canonical_run_missing_documented` warning and optional
  provider preload warnings.
- `uv run pytest -q` passed, 1002 tests.

The taxonomy validator should remain part of future archive moves because it
catches missing provenance and stale decision links.
