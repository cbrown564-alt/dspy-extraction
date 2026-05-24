# Gan S0 Multi-Stage GEPA Workstream

Date: 2026-05-24
Status: Cap-25 G0-G2 completed; G1/G2 rejected as arms
Decision scope: open mechanism class; G1/G2 arm rejection only
Primary board: `docs/planning/kanban_plan.md`

## Goal

Test whether a GEPA variant can surpass the current Gan S0 operational default:
`gan_s0_candidate_builder_gap_v1` on GPT 4.1-mini, full validation monthly
accuracy 80.6%, Purist 86.0%, Pragmatic 88.6%, with 100.0% schema validity
and 100.0% evidence quote support.

This workstream is deliberately not a repeat of the historical direct GEPA run.
The previous few-shot and GEPA attempts mostly optimized a single direct prompt,
often by adding demonstrations or long policy text. The new hypothesis is that
GEPA may be useful when it can optimize instructions across a multi-stage Gan
pipeline, with feedback attached to the stage that failed.

## Hypothesis

GEPA with stage-attributed textual feedback can improve Gan S0 residual errors
over `gan_s0_candidate_builder_gap_v1` by shortening or sharpening the
adjudicator and verifier instructions, without adding few-shot prompt bloat or
changing deterministic candidate builders, gold labels, scorer semantics, or the
validation split.

## External Documentation Review

Primary sources checked on 2026-05-24:

- DSPy GEPA API docs:
  `https://github.com/stanfordnlp/dspy/blob/main/docs/docs/api/optimizers/GEPA/overview.md`
- DSPy optimizer overview:
  `https://github.com/stanfordnlp/dspy/blob/main/docs/docs/learn/optimization/optimizers.md`
- GEPA full-program evolution tutorial:
  `https://gepa-ai.github.io/gepa/tutorials/dspy_full_program_evolution/`
- Cursor CLI/agent docs:
  `https://docs.cursor.com/en/cli/overview`,
  `https://docs.cursor.com/en/cli/using`,
  `https://docs.cursor.com/en/cli/reference/parameters`

Takeaways applied here:

- DSPy optimizers are defined over a DSPy program, which may be a complex
  multi-module program, not only a single `Predict` call.
- Few-shot optimizers add demonstrations to prompts; this directly matches the
  prompt-length failure mode already observed in this repo.
- GEPA is appropriate when a metric can return rich textual feedback and when
  traces expose which module or stage failed.
- GEPA's useful artifacts include candidate instructions, stats, Pareto
  coverage, and best outputs when tracking is enabled. These should be mined as
  research artifacts, not just used to pick a compiled prompt.
- Full-program evolution exists in the separate GEPA ecosystem, but the first
  repo-safe step should use current `dspy.GEPA` over existing DSPy modules
  before introducing source-code mutation.
- Cursor SDK remains review-only in this repo. A live Cursor SDK inspection run
  was attempted for this workstream (`20260524T125735Z`) after `check` passed,
  but produced a zero-byte draft. It is recorded as a stub and was not used as
  source evidence.

## Codebase Review

Relevant current implementation:

- `src/clinical_extraction/programs/gan_frequency_s0.py` already supports GEPA
  through `compile_gan_s0_module_gepa`.
- `src/clinical_extraction/experiments/gan_backend.py` routes `optimizer.name ==
  "GEPA"` into the GEPA compile helper.
- `src/clinical_extraction/experiments/config.py` validates GEPA configs:
  feedback metric required, exactly one budget control required.
- Existing feedback metrics are
  `semantic_frequency_with_evidence_feedback` and
  `synthesis_exact_with_evidence_feedback`.
- `src/clinical_extraction/gan/temporal_candidates.py` maps
  `gan_s0_candidate_builder_gap_v1` to prose presentation and provides the
  current deterministic candidate surface.

Key gap:

`compile_gan_s0_module_gepa` builds the module with `build_gan_s0_module`, so it
can technically compile multi-stage program variants, but the return typing,
config tests, and artifact expectations were written around direct GEPA probes.
There is no specific multi-stage GEPA contract that names optimized predictors,
stage-attributed feedback, instruction-length limits, or DAG/mining outputs.

## Critique Of Previous Optimizer Implementations

Historical results to preserve:

- `docs/experiments/gan/gan_s0_few_shot_ladder_cap25_inspection_20260519.md`:
  labeled few-shot beat bootstrap/BootstrapRS on the direct path, while
  bootstrap variants added cost and did not solve label semantics.
- `docs/experiments/gan/gan_s0_gepa_vs_synthesis_decision_20260519.md`:
  direct GEPA was rejected as an arm because it increased prompt length,
  regressed label metrics, and was slow or non-canonical on Qwen.
- `docs/workstreams/optimizer/dspy_optimizer_investigation_20260521.md`:
  optimizers were mainly tried on single-pass extractors, while the winning
  Gan path became a hybrid candidate/adjudication architecture.

Failure modes to avoid:

- Do not stack GEPA on top of hand-tuned long prompts and then blame GEPA for
  bloat.
- Do not compare a cap-5 compile against a full-validation operational default.
- Do not let optimizer feedback redefine the benchmark scorer.
- Do not run GEPA on Qwen as the development path. Use hosted GPT first, then
  distill or port only if a compact instruction wins.
- Do not treat one new GEPA arm as mechanism closure, whether it wins or loses.

## Experiment Design

### Comparison group

`gan_s0_multistage_gepa_gpt_validation_v1`

### Fixed controls

| Control | Value |
| --- | --- |
| Dataset | `gan_2026` |
| Split | `gan_2026_fixed_v1:validation` for cap/full eval; train/development only for compile |
| Model | GPT 4.1-mini first |
| Schema | `gan_frequency_s0` |
| Scorer | `gan_frequency_deterministic_v1` |
| Gold label | `seizure_frequency_number[0]`; `reference` diagnostic only |
| Candidate builders | `gan_s0_candidate_builder_gap_v1` fixed |
| Evidence policy | Diagnostic quote support; do not change benchmark scorer |
| Test split | Not used in this workstream unless a later preregistered confirmation run is written |

### Primary arms

| Arm | Program variant | Varied factor | Purpose |
| --- | --- | --- | --- |
| G0 | `gan_frequency_s0_temporal_candidates_single_pass` | none | Reproduce current operational default prompt/run contract on cap before compile |
| G1 | same as G0 + GEPA | optimizer_strategy | Optimize only candidate-adjudicator instruction |
| G2 | `gan_frequency_s0_temporal_candidates_verify_repair` + GEPA | optimizer_strategy | Optimize extractor/adjudicator and verifier instructions in a multi-stage path |
| G3 | same as G2, verifier-only compile if supported | optimized_stage | Test whether targeted verifier feedback helps without perturbing adjudication |
| G4 | best G1/G2 instruction distilled into non-compiled config | implementation_variant | Check whether GEPA found a compact human-promotable rule set |

G3 is blocked until the implementation can target a submodule or explicitly
freeze other predictors. If targeting is not supported cleanly, leave G3 as a
design note rather than simulating it through ad hoc prompt edits.

### Feedback design

The GEPA metric should emit stage-attributed feedback:

- `candidate_surface`: no deterministic candidate, candidate label missing gold,
  candidate contains misleading highest-rate option.
- `adjudicator`: chose unknown over quantified rate, collapsed ranges, chose
  wrong current seizure type, misread YTD/window denominator, selected
  no-reference when seizures were clinically discussed.
- `verifier`: over-repaired a supported label, confirmed an unsupported unknown,
  stripped cluster format, repaired to a label not in the candidate set.
- `evidence`: missing quote, unsupported quote, no-reference with evidence.
- `format`: non-canonical unit, malformed cluster, plural/unit drift.

Optimizer score remains optimizer-facing only. Benchmark-facing reporting must
still use `metrics.json` from the deterministic Gan evaluator.

### Gates

Cap gate:

- cap-25 monthly accuracy must beat the current cap/control arm by at least
  4 percentage points or reduce severe residual errors without increasing
  invalid/evidence errors.
- schema validity must stay at 100% or have a documented repairable cause.
- evidence quote support must stay at or near the operational default.
- selected instruction must be inspected for prompt bloat. Record chars/words
  per predictor and reject any arm that wins only by recreating a long policy
  wall unless the metric lift is large enough to justify a separate tradeoff.

Full-validation promotion gate:

- Full validation must beat 80.6% monthly and not regress Purist/Pragmatic
  beyond confidence-interval noise.
- Runtime and token usage must be recorded.
- GEPA artifacts must include logs, selected instructions, detailed stats when
  available, and a short mining note identifying reusable rules.

### Artifact expectations

Each live run should preserve:

- `config.json`, `metadata.json`, `metrics.json`, `predictions.json`,
  `errors.json`, `prompts.json`
- `artifacts/compiled_state.json`
- `artifacts/optimizer/summary.json`
- `artifacts/optimizer/logs/`
- extracted instruction text per predictor
- candidate lineage or detailed GEPA stats when `track_stats=True`
- best-output samples when `track_best_outputs=True`

## Implementation Cards

### Card 1: Preregister configs and tests

Outcome: Config stubs for G0-G2 with taxonomy, budget, controls, and tests that
assert the multi-stage GEPA contract.

Status: Complete. Added:

- `configs/experiments/gan_s0_multistage_gepa_g0_control_cap25_gpt4_1_mini.json`
- `configs/experiments/gan_s0_multistage_gepa_g1_adjudicator_cap25_gpt4_1_mini.json`
- `configs/experiments/gan_s0_multistage_gepa_g2_verify_repair_cap25_gpt4_1_mini.json`
- Config coverage in `tests/test_experiment_configs.py`

Validation:

```powershell
uv run pytest tests/test_experiment_configs.py tests/test_experiment_runner.py
uv run python scripts/validate_experiment_taxonomy.py --errors-only
```

### Card 2: Add stage-attributed GEPA feedback metric

Outcome: New feedback metric, likely
`gan_s0_stage_attributed_frequency_feedback`, that wraps existing Gan scoring
plus residual taxonomy tags.

Status: Complete. `gan_s0_stage_attributed_frequency_feedback` is registered as
an optimizer-facing GEPA metric and emits `stage:candidate_surface`,
`stage:adjudicator`, `stage:verifier`, `stage:evidence`, and `stage:format`
feedback without changing benchmark-facing `gan_frequency_deterministic_v1`
scoring.

Validation:

```powershell
uv run pytest tests/test_gan_scoring.py tests/test_gan_s0_program.py
```

### Card 3: Harden multi-stage GEPA compile artifacts

Outcome: `compile_gan_s0_module_gepa` and run artifacts explicitly support
multi-stage Gan modules and preserve per-predictor compiled instruction state.

Status: Complete for the G0-G2 cap-25 run. A feedback-metric contract bug was
found during the first G1 run (`GanTemporalFrequencyCandidate.label` instead of
`canonical_label`), fixed with regression coverage, and the clean G1/G2 runs
preserved compiled state plus optimizer summaries/logs.

Validation:

```powershell
uv run pytest tests/test_experiment_runner.py tests/test_gan_s0_program.py
```

### Card 4: Cap-25 GEPA search

Outcome: G0-G2 cap-25 runs under `gan_s0_multistage_gepa_gpt_validation_v1`
with inspection note and artifact mining note.

Status: Complete. G0 matched control held at 76.0% monthly / 84.0% Purist /
96.0% Pragmatic, while G1 regressed to 60.0% monthly and G2 regressed to
48.0% monthly despite 100% schema validity and evidence quote support. G1/G2
are rejected as cap-25 arms; no full-validation promotion.

Validation: live run artifacts plus inspection doc with `decision_scope: arm`:
`docs/experiments/gan/gan_s0_multistage_gepa_gpt_cap25_v1_inspection_20260524.md`.

### Card 5: Full-validation candidate

Outcome: At most one GEPA winner or distilled non-compiled instruction runs on
full validation.

Validation: full-validation metrics compared to
`gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z`.

## Risks And Guardrails

- Prompt bloat can recur. Track prompt length as a gate, not an afterthought.
- GEPA may optimize the wrong stage if feedback is too aggregate. Require
  stage names in feedback.
- Candidate builders are already strong. Do not mutate them in this workstream.
- Validation split has been heavily studied. Treat full-validation wins as
  development evidence unless a later test-holdout protocol is explicitly
  approved.
- The Cursor SDK draft for this design was a zero-byte stub; do not cite it.

## Recommended First Pull

Start with Cards 1 and 2 only. They create the reproducible GEPA surface and
feedback contract without spending model budget. Then run a dry-run and one
cap-25 G0 control before compiling G1/G2.
