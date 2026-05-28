# C21 Fresh-Start Deadweight Pruning Review

Status: active pruning plan
Date: 2026-05-28
Kanban card: C21 - Fresh-Start Deadweight Pruning Review
Skills used: `thermo-nuclear-code-quality-review`, `research-synthesis`

## Scope

C21 reopens the C20 accepted-residual list under one new assumption: historical
experiment reruns are no longer a product requirement. Git history, archive
files, generated registry snapshots, and decision docs are enough provenance
unless a current card explicitly depends on executable replay.

This review does not change code behavior. It classifies live surfaces into:

- delete now;
- keep only as archived provenance;
- keep as active infrastructure;
- split into a follow-up implementation card.

The guardrail is unchanged: do not silently change scorer, loader, split,
benchmark bridge, component, or current run semantics.

## Method

Source docs read:

- `docs/README.md`
- `docs/current_research_program.md`
- `docs/component_ceiling_registry.md`
- `docs/planning/kanban_plan.md`
- `docs/planning/program_surface_inventory_deletion_map_20260528.md`
- `docs/planning/thermo_nuclear_codebase_architecture_audit_20260528.md`
- `docs/planning/active_experiment_status_review_20260528.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md`
- `docs/workstreams/cursor_sdk/cursor_sdk_final_value_report_20260525.md`

Static scans used:

- `git status --short`
- line-count scan over `src`, `scripts`, and `tests`
- text scans for `compat`, `legacy`, `archive`, `replay`, `monkeypatch`,
  `facade`, and `resolve_*`
- import graph scan for candidate modules and facades
- script-reference scan for active `scripts/*`
- program-variant registry and config inventory count via
  `clinical_extraction.experiments.program_variant_registry`

Tooling caveat: the original C21 scan did not run whole-repo dead-code tooling.
`ruff` and `vulture` were later installed as dev dependencies for the follow-up
C26 static sweep. The original unused-code findings are file/script-level
findings backed by `rg` and AST import inspection, not function-level proof.

## Current Inventory Snapshot

The current authority split is clean enough for research work, but the runtime
still carries old replay guarantees:

| Surface | Current count / evidence | Interpretation |
| --- | ---: | --- |
| Active experiment configs | 35 files under `configs/experiments` | current-authority config surface |
| Archived experiment configs | 307 files under `archive/configs` | provenance store, not current queue |
| Archived configs matched by registry inventory | 211 | still treated as loadable replay by generated inventory |
| Archived configs unmatched by registry inventory | 96 | already docs/files-only in practice |
| Program-variant registry rows | 77 | 9 current authority, 68 loadable replay |
| Active scripts | 35 files under `scripts` | mixture of active CLIs, report exporters, one-off mutators, stale launchers |
| Largest live compatibility tests | `tests/test_experiment_configs.py` 3187 lines, `tests/test_exect_s0_s1_program.py` 2237 lines, `tests/test_gan_s0_program.py` 2087 lines | useful parity nets, but still preserve old facade/import contracts |

## Delete Now

These surfaces can be removed from active code in the next implementation pass.
The retained provenance is already in docs, archive artifacts, or git history.

| Surface | Why it is deadweight | Dropped guarantee | Minimum validation |
| --- | --- | --- | --- |
| `cursor-sdk` core dependency in `pyproject.toml`, `uv.lock`, and generated package metadata | The final Cursor SDK report says active SDK usage is retired and not valuable enough to keep as an active dependency. The dependency remains in the core runtime dependency list. | The repo no longer launches Cursor SDK workflows from the shared environment. | `uv lock`; `uv run pytest -q`; `rg -n "cursor_sdk|cursor-sdk" pyproject.toml src scripts tests` should only find archived docs if any. |
| `scripts/cursor_sdk_workflows.py` and `tests/test_cursor_sdk_workflows.py` | The script is a retired research-ops wrapper with a Windows bridge monkeypatch and mutating-workflow guard. It is not part of clinical extraction, scoring, datasets, experiments, or component ceilings. | The local Windows Cursor bridge workaround and SDK prompt generator are no longer executable active tooling. | Remove script/test together; keep `docs/workstreams/cursor_sdk/` as historical traceability; full suite after dependency removal. |
| `tests/test_run_self_consistency.py` | This active test imports `archive/scripts/run_self_consistency.py` by file path and mocks its internals. R13 rejected self-consistency, and C21 explicitly drops old rerun as a requirement. | Archived self-consistency script behavior is not regression-tested. | Delete the test; confirm no active docs instruct running the archived script; run `uv run pytest tests/test_gan_s0_program.py tests/test_experiment_configs.py -q`. |
| `scripts/run_gan_gpt_d1_full_validation.ps1` | Hard-coded local path and points at `configs/experiments/gan_s0_date_stage_d1_det_events_full_validation_gpt4_1_mini.json`, which no longer exists in the active config tree. The run artifact and archived config remain traceable. | One bespoke launcher for an old D1 full-validation run is gone. | `Test-Path` for the active config stays false; no active docs reference the launcher. |
| `scripts/_registry_analysis_pass.py` | One-off registry printout with zero outside references in active code/docs. | The exact ad hoc console summary is not rerunnable from active scripts. | None beyond `rg -n "_registry_analysis_pass"`. |
| `scripts/backfill_registry_headline_metrics.py` | One-off mutator for old registry headline rows with zero active outside references. The registry JSON and decision docs are the retained source. | Old headline backfill cannot be rerun as an active mutating script. | `uv run pytest tests/test_export_registry_matrix.py -q`; inspect generated registry diff only if registry is regenerated. |
| `scripts/retag_registry_decision_scope.py` | One-off mutator for old registry notes with zero active outside references. | Old decision-scope retag pass cannot be rerun as active tooling. | `uv run python scripts/validate_experiment_taxonomy.py --errors-only`. |

## Keep Only As Archived Provenance

These should not remain active script/test/runtime contracts, but their
historical content can stay under `archive/` or current docs.

| Surface | Classification | Follow-up action |
| --- | --- | --- |
| `scripts/backfill_hybrid_cap25_registry.py` | Keep as archived provenance only. C10 already moved static row data to `docs/archive/experiments/synthesis/pre_component_pivot/hybrid_cap25_registry_backfill_manifest_20260528.json`; the active script now exists mainly so a test can assert that manifest shape. | Move to `archive/scripts/` or delete after rewriting `tests/test_export_registry_matrix.py` to read the manifest directly. |
| `archive/configs/**` | Keep as provenance files. Do not treat archive count as active experiment inventory. | Leave files in archive, but stop active config loading from falling back to them by default. |
| `archive/runs/**` | Keep as provenance and residual-analysis source only where a current report cites a run ID. | Remove automatic active-run fallback unless an explicit analysis command opts in. |
| `archive/scripts/**` | Keep as historical traceability. | Do not test archived scripts in the active test suite unless a current card explicitly promotes one back to active tooling. |
| `docs/workstreams/cursor_sdk/**` | Keep as historical review lead map and safety lesson. | Preserve docs, but remove active code and dependency. |

## Keep As Active Infrastructure

These surfaces are still doing current work and should not be deleted in a
deadweight pass.

| Surface | Why it stays active |
| --- | --- |
| `configs/experiments/**` | 35 current-authority configs backing promoted, mechanism, diagnostic, and operational baselines. |
| `scripts/run_experiment.py` | Main execution entrypoint for model-backed experiments. |
| `scripts/validate_primitives.py` and `scripts/validate_experiment_taxonomy.py` | Current validation gates for primitive and taxonomy/registry contracts. |
| `scripts/report_program_variant_registry.py` | Current generator for `docs/experiments/synthesis/program_variant_registry.md`. |
| Current no-model audit/export scripts for Gan G1/G2 and ExECT E1/E3/E4 | They back the component-decomposition reports and are cheap, deterministic reproducibility tools. Archive only after their reports no longer need regeneration. |
| `scripts/analyze_gan_frequency_run.py` | Still useful because C10 added explicit canonical versus paper-reproduction scorer modes. It is a reporting tool, not merely replay baggage. |
| Dataset loaders and scorer modules | Governed by dataset/scorer policy; no deletion without `dataset-audit-first` and `gold-scorer-integrity` gates. |

## Split Into Follow-Up Cards

These are not safe one-shot deletes. Each needs a focused implementation card
because current runtime imports or tests still depend on the compatibility
surface.

### C22 - Archive Loadability Retirement

Current evidence:

- `src/clinical_extraction/paths.py` resolves configs and runs from active
  locations or archive fallback.
- `tests/test_paths.py` explicitly locks archive config/run fallback.
- `program_variant_registry.py` still has `LOADABLE_REPLAY_STATUSES`, an
  `archive`/`all` config inventory source, and archived inventory rendering.
- `tests/test_program_variant_registry.py` asserts `loadable_replay` archive
  behavior.

Proposed change:

- make active config/run resolution active-only by default;
- remove archive fallback from ordinary `load_experiment_config`;
- convert archived config inventory into a docs-only generated snapshot or an
  explicit `--include-archive` report mode;
- stop validating `historical_arm`, `replay_provenance`, and `rejected_arm`
  rows as runnable contracts.

Dropped guarantee:

- archived configs and archived runs are not guaranteed rerunnable by basename.

Retained traceability:

- archived files, run IDs in reports, `program_variant_registry.md` snapshots,
  `component_ceiling_registry.md`, and git history.

Minimum gate:

- `uv run pytest tests/test_paths.py tests/test_program_variant_registry.py tests/test_experiment_configs.py tests/test_experiment_registry_validation.py tests/test_export_registry_matrix.py -q`
- `uv run python scripts/validate_experiment_taxonomy.py --errors-only`

### C23 - Legacy Program Facade Import Inversion

Current evidence:

- `programs/gan_frequency_s0.py` is a wildcard compatibility facade and
  re-exports private helpers.
- `programs/exect_s0_s1.py` dynamically imports modules and fills `globals()`.
- active backends, config validation, prompt metadata, and tests still import
  through those legacy facades.

Proposed change:

- update active runtime imports to domain-owned modules:
  `clinical_extraction.gan.s0.*` and `clinical_extraction.exect.s0_s1.*`;
- delete tests that exist only to prove legacy facade compatibility;
- keep a tiny deprecation shim only if packaging/import compatibility still
  matters for external users. This repo currently has no evidence of that.

Dropped guarantee:

- private helper imports from old program module paths no longer work.

Minimum gate:

- `uv run pytest tests/test_gan_s0_package_decomposition.py tests/test_gan_s0_program.py tests/test_gan_s0_stage_surfaces.py tests/test_exect_s0_s1_program.py tests/test_exect_s1_boundary_surfaces.py tests/test_experiment_configs.py -q`

### C24 - ExECT S4/S5 Routing Separation

Current evidence:

- `ExectExperimentBackend` classifies S5 variants inside
  `_EXECT_S4_PROGRAM_VARIANTS` and routes them through `build_exect_s4_module`.
- C16 split S5 modules, but S4/S5 runtime dispatch still shares one branch.

Proposed change:

- add an explicit S5 variant set and route S5 module building, prediction, and
  scoring through S5-named helpers;
- keep S5 v2b as an operational stacked baseline, not a component ceiling.

Dropped guarantee:

- old S5 variants can no longer masquerade as S4 compatibility variants.

Minimum gate:

- `uv run pytest tests/test_exect_s4_program.py tests/test_exect_s5_scoring.py tests/test_exect_s5_frequency_verifier.py tests/test_experiment_configs.py -q`

### C25 - Script Hygiene And Report Exporter Split

Current evidence:

- multiple active scripts have zero active references outside themselves, but
  several are legitimate deterministic report builders invoked manually by
  current cards.
- G3 policy-probe code is script-local and tested, but not promoted as a
  stable module.

Proposed change:

- split script inventory into `current report exporters`, `current validators`,
  `active experiment runners`, and `archived one-offs`;
- move reusable logic from scripts into `clinical_extraction.evaluation.*` only
  when a current report needs tests;
- archive or delete one-off scripts after their artifact and decision doc are
  promoted.

Dropped guarantee:

- every past ad hoc analysis remains runnable from `scripts/`.

Minimum gate:

- targeted tests for each retained report builder plus `rg` checks for deleted
  filenames.

### C26 - Ruff/Vulture Static Dead-Code Sweep

Current evidence:

- C21 used `rg`, import-graph inspection, and manual script-reference scans,
  but did not run function-level dead-code tooling. `ruff` and `vulture` are now
  installed as dev dependencies for a follow-up pass.
- Manual scans are good at finding obvious stale files. They are not enough for
  unused imports, unused local variables, unreachable helper functions,
  stale compatibility exports, or private helpers kept alive only by old tests.
- C25 should first classify script entrypoints and move reusable report logic
  into modules where needed, so static tools do not confuse intentional CLI
  entrypoints with dead library code.

Proposed change:

- run `uv run ruff check src scripts tests` and triage all findings;
- run `uv run vulture src scripts tests --min-confidence 80` after C25 has
  settled the active script inventory;
- create a small explicit whitelist only for justified dynamic entrypoints,
  Pydantic/DSPy reflection surfaces, CLI-only functions, or generated
  compatibility exports that are intentionally retained;
- delete or simplify unused imports, dead helpers, stale constants, unreachable
  branches, and compatibility exports that no current card needs.

Dropped guarantee:

- unreferenced helper functions and constants are not retained merely because
  old experiments or private tests might have imported them.

Minimum gate:

- `uv run ruff check src scripts tests`
- `uv run vulture src scripts tests --min-confidence 80`
- focused scorer/loader/component tests for every touched area
- full suite after deletion batches

Stop rule:

- do not use `ruff --fix` broadly across scorer, loader, split, benchmark
  bridge, or current component code. Apply fixes in reviewed batches with
  targeted tests.

### C27 - Compatibility Test Shrink

Current evidence:

- large tests still protect config replay and facade compatibility even where
  public stage/domain tests exist.

Proposed change:

- after C22/C23/C26, delete tests that assert old replay/facade compatibility;
- keep behavior tests that protect current loaders, scorers, bridges, and
  component surfaces.

Dropped guarantee:

- legacy import/replay behavior is not a test contract.

Minimum gate:

- full current suite after each deletion wave, with explicit scorer/loader
  suites retained.

## Minimal First Implementation Pass

The safest first pull after C21 is a high-confidence deletion card:

1. Remove Cursor SDK from runtime dependencies and delete the active SDK script
   and test.
2. Delete active tests for archived self-consistency replay.
3. Delete or archive stale one-off launch/mutation scripts listed under
   `Delete Now`.
4. Move or delete `scripts/backfill_hybrid_cap25_registry.py` after rewriting
   the manifest assertion to read the archive manifest directly.

This pass intentionally avoids scorer, loader, split, benchmark bridge, and
component-runtime edits.

Suggested test matrix:

```powershell
uv run pytest tests/test_export_registry_matrix.py tests/test_experiment_configs.py tests/test_experiment_registry_validation.py -q
uv run pytest tests/test_gan_s0_program.py tests/test_gan_scoring.py tests/test_gan_paper_reproduction_scoring.py -q
uv run pytest tests/test_exect_s0_s1_program.py tests/test_exect_s4_program.py tests/test_exect_s5_frequency_verifier.py tests/test_exect_scoring.py -q
uv run python scripts/validate_experiment_taxonomy.py --errors-only
uv run python scripts/validate_primitives.py --errors-only
uv run pytest -q
```

## Stop Rules

- Stop if any deletion changes dataset loading, split membership, scorer
  denominator, scorer normalization, benchmark bridge behavior, evidence
  support semantics, or current config validation.
- Stop if a current report can no longer trace run ID, config, model/provider,
  split, scorer mode, and caveat.
- Stop if Gan paper-comparison reporting loses the
  `gan2026_paper_reproduction` versus canonical diagnostic split.
- Stop if ExECT project scorers are described as published Table 1 reproduction.

## Conclusion

C21 finds no new P1 architecture blocker. The deadweight is now mostly
operational: live dependencies, tests, config loaders, and facades still defend
the idea that old experiments are rerunnable from active code. The next value is
not another broad refactor. It is a controlled deletion pass that drops those
guarantees explicitly while preserving research memory in docs, archive files,
registry snapshots, and git history.
