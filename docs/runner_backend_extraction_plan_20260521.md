# Runner Backend Extraction Plan

Date: 2026-05-21  
Status: **Complete** — library `run_experiment`, dataset backends, thin CLI, golden `prompts.json` fixtures, Phase 7 artifact-layout regression tests; script compatibility re-exports removed  
Related review: `docs/codebase_architecture_review_20260519.md`  
Related doctrine: `docs/hybrid_pipeline_research_pivot_20260521.md`

## Goal

Extract the experiment runner into importable library code with dataset-specific backends, while preserving every downstream research and artifact contract.

The intended end state is:

```text
scripts/run_experiment.py
  parse args
  load env file
  call clinical_extraction.experiments.runner.run_experiment(...)
  print/exit

src/clinical_extraction/experiments/
  runner.py          # generic run lifecycle
  backends.py        # protocol + backend registry
  gan_backend.py     # Gan S0 loading/build/compile/predict/evaluate/prompts/metadata
  exect_backend.py   # ExECT S1-S4 loading/build/compile/predict/evaluate/prompts/metadata
```

The desired behavior is intentionally boring: every existing config should still run from the same command, emit the same `runs/<run_id>/` files, keep the same JSON shapes, use the same split ordering, scorer semantics, prompt metadata, optimizer behavior, token/runtime reporting, and summary output. The refactor changes ownership boundaries, not experiment meaning.

## Current Problem

`scripts/run_experiment.py` currently mixes at least eight responsibilities:

- CLI and env loading
- split resolution and record filtering
- dataset loading
- DSPy LM setup
- module construction
- optimizer compilation
- prediction
- evaluation, artifact writing, prompt metadata, runtime reporting, and summary printing

The most important branch points are:

- `_build_module`
- `_run_metadata`
- `_prompts_data`
- `_predict_records`
- `_evaluate_predictions`

These are the places new datasets, schema levels, or program variants keep adding conditional logic. The May 19 architecture review identified this as the main scaling bottleneck. Since then, the research governance layer has improved, but the runner has grown more branch-heavy.

Before starting this extraction, fix the current local config-contract failure for the new Gan validation-ladder configs so the refactor begins from a clean baseline.

## Backend Contract

Create an `ExperimentBackend` protocol in `src/clinical_extraction/experiments/backends.py`.

Initial shape:

```python
class ExperimentBackend(Protocol):
    dataset: str

    def load_records_by_id(self) -> dict[str, Any]: ...
    def build_module(self, config: ExperimentConfig) -> dspy.Module: ...
    def compile_module(...): ...
    def run_metadata(...): ...
    def prompts_data(...): ...
    def predict_records(...): ...
    def evaluate_predictions(...): ...
    def summary_sections(...): ...
```

Do not over-abstract the first pass. The backend should absorb dataset/schema branching, while the generic runner owns universal lifecycle concerns:

- config loading
- split subset validation
- `record_ids` and `max_records`
- LM creation and DSPy configuration
- run ID creation
- artifact directory creation via `create_run_artifact_layout`
- writing `config.json`, `prompts.json`, `predictions.json`, `metrics.json`, and `errors.json`
- runtime timings
- token usage
- model residency
- final summary printing

This keeps "what is this experiment?" in the backend and "how is a run executed and recorded?" in the runner.

## Phase 1: Baseline Lock

Make current behavior measurable before moving code.

Tasks:

1. Fix the Gan validation-ladder config contract mismatch.
2. Run focused tests:

```powershell
uv run pytest tests/test_experiment_configs.py tests/test_experiment_registry_validation.py tests/test_run_experiment_runtime.py tests/test_gan_s0_program.py tests/test_exect_s0_s1_program.py -q
```

3. Add or confirm a dry-run smoke test for at least one Gan config and one ExECT config.
4. Add a deterministic/mock runner test that asserts artifact file names and top-level JSON keys.

Do not begin extraction until this baseline is green.

## Phase 2: Extract Generic Runner Utilities

Move low-risk generic helpers into `src/clinical_extraction/experiments/runner.py` without changing behavior:

- `_make_run_id`
- `_load_env_file`
- `_runtime_report`
- `_collect_lm_token_usage`
- `_capture_local_model_residency`
- `_parse_ollama_ps_output`
- split resolution/filtering logic
- `_print_prediction_progress`, if helpful

`tests/test_run_experiment_runtime.py` currently imports private helpers from `scripts/run_experiment.py`. Either update tests to import from the library module or temporarily re-export those helpers from the script.

Break risk: tests, notebooks, or ad hoc scripts import private script helpers.

Mitigation: keep compatibility re-exports during the transition, then remove them in a later cleanup.

## Phase 3: Add Backend Registry

Add a simple backend registry:

```python
BACKENDS = {
    "gan_2026": GanExperimentBackend(),
    "exect_v2": ExectExperimentBackend(),
}
```

The first lookup should be by `config.dataset`, not `program_variant`. Inside `ExectExperimentBackend`, schema/program branching can remain for S1-S4 at first. This keeps the migration small.

Break risk: invalid dataset errors change from current `SystemExit` messages.

Mitigation: preserve user-facing error messages where tests or scripts may rely on them.

## Phase 4: Move Gan Branches

Move these Gan-specific responsibilities into `GanExperimentBackend`:

- record loading from `load_gan_records`
- `build_gan_s0_module`
- compile paths: `compile_gan_s0_module`, `compile_gan_s0_module_gepa`
- Gan prompt metadata currently in `_prompts_data`
- `predict_gan_records`
- `evaluate_gan_predictions`
- Gan summary metric fields

Do not split `src/clinical_extraction/programs/gan_frequency_s0.py` in this pass.

Break risks:

- candidate presentation from taxonomy is lost
- GEPA reflection LM path changes
- optimizer log path changes
- `prompts.json` differs
- `repair_policy` is accidentally passed to Gan prediction
- summary percentage labels or order change

Mitigations:

- Unit test `GanExperimentBackend.prompts_data` against current expected module/predictor strings.
- Test candidate presentation mapping from `config.taxonomy.implementation_variant`.
- Golden-file compare top-level `prompts.json` for one Gan direct config and one temporal-candidates config.
- Keep optimizer artifact paths exactly as `RunArtifactPaths` defines them.

## Phase 5: Move ExECT Branches

Move these ExECT-specific responsibilities into `ExectExperimentBackend`:

- record loading from `load_exect_gold_documents`
- S0/S1/S2/S3/S4 module building
- ExECT S0/S1 compile path
- ExECT prompt metadata for S1-S4
- `predict_exect_records`, `predict_exect_s2_records`, `predict_exect_s3_records`, and `predict_exect_s4_records`
- ExECT scoring dispatch
- ExECT summary metric fields

Break risks:

- S2/S3/S4 schema-level scoring routes get crossed
- S0/S1 `repair_policy` stops being passed
- prompt version resolution changes
- label policy guidance/examples are omitted from `prompts.json`
- field-family lists differ
- S4 frequency/temporality variants accidentally use default module metadata

Mitigations:

- Backend tests for each ExECT schema level: S1, S2, S3, S4.
- Assert `prediction_set.schema_level` dispatch routes to the correct scorer.
- Golden prompt metadata checks for one S1 and one S4 config.
- Keep existing program module APIs unchanged.

## Phase 6: Create Library Runner API

Expose a stable importable function:

```python
def run_experiment(
    experiment_path: Path,
    *,
    run_id: str | None = None,
    env_file: Path | None = None,
    dry_run: bool = False,
    stdout: TextIO = sys.stdout,
) -> int:
    ...
```

The CLI should call this function. Tests and downstream automation can then use the library API without invoking a subprocess.

Break risks:

- console output changes enough to disrupt scripts or manual expectations
- dry run starts creating files
- `--run-id` behavior changes
- env-file precedence changes

Mitigations:

- Snapshot-style tests for dry-run essentials: experiment, dataset, split, model, record count, optimizer, and "Dry run".
- Assert dry run does not create `runs/<run_id>`.
- Preserve env behavior: `.env` fills only missing vars.

## Phase 7: Freeze Artifact Contract

The run directory contract must not move:

```text
metadata.json
config.json
prompts.json
predictions.json
metrics.json
errors.json
artifacts/compiled_state.json
artifacts/optimizer/summary.json
artifacts/optimizer/logs/
```

This is defined in `src/clinical_extraction/runs.py`. Do not rename these files, do not nest by backend, and do not add backend-specific top-level files during this refactor.

Break risk: research docs, registry scripts, atlas exports, and inspection scripts expect current paths.

Mitigation: artifact-layout regression tests using `create_run_artifact_layout`.

## Phase 8: Shrink CLI Last

Only after backend tests are green, reduce `scripts/run_experiment.py` to the CLI wrapper. Keep the command unchanged:

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/...json --env-file .env
```

Do not add console entry points in the same change. That can come after the library runner stabilizes.

## Downstream Breakage Checklist

Verify these explicitly before merging:

- Existing experiment configs still load.
- `report_on_test_split` guard still fires.
- `record_ids` outside split still fail.
- `max_records` preserves split order.
- Missing dataset IDs still warn, not crash.
- Gan and ExECT predictions still serialize as `PredictionSet`.
- `metadata.json` still includes the same dataset, split, model, schema, program, and scorer fields.
- `prompts.json` still includes prompt versions, module names, policy text, and field families.
- Optimizer runs still write compiled state and optimizer summary.
- GEPA still gets reflection LM and log directory.
- Token usage still aggregates primary and reflection LMs.
- Ollama residency still reports for `provider == "ollama"`.
- `metrics.json` still embeds `runtime`.
- `errors.json` still mirrors `report["errors"]`.
- Printed summary still distinguishes Gan and ExECT metrics.
- Registry validation scripts still find run artifacts.
- Research atlas/export scripts still read metrics/config paths.
- Windows paths remain `Path` objects; no shell-specific path assumptions.

## Do Not Change In This Refactor

- Do not split the program monoliths yet.
- Do not change scorer semantics.
- Do not normalize prompt metadata into a new schema.
- Do not add a third dataset.
- Do not introduce plugin-style dynamic discovery.
- Do not move run artifacts.
- Do not change config JSON shape.

The goal is one thing: move orchestration branching out of the script into typed, testable backend objects while keeping every experimental artifact and comparison contract stable.

## Recommended First PR Scope

Small but meaningful:

1. Fix the current Gan validation-ladder config contract failure.
2. Add `experiments/backends.py` with the protocol and registry.
3. Add `experiments/runner.py` with generic helpers and split resolution.
4. Move only `_load_records_by_id`, `_build_module`, `_run_metadata`, `_predict_records`, and `_evaluate_predictions` behind backends.
5. Leave `_prompts_data` in place until the second PR if needed.

This gives the architecture its turn without trying to lift the whole runner at once.
