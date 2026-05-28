# Thermo-Nuclear Codebase Architecture Audit

Status: active guidance
Date: 2026-05-28
Kanban card: C1 - Thermo-Nuclear Codebase Architecture Audit

## Scope And Guardrails

This audit follows the May 28 component-decomposition pivot. It reviewed active
program, primitive, scorer-adjacent, experiment-config, registry, and analysis
surfaces for bloat and semantic bundling that blocks the Gan S0 and ExECT
component-ceiling work.

Skills and policies used as guardrails:

- `thermo-nuclear-code-quality-review`
- `dataset-audit-first`
- `gold-scorer-integrity`
- `dspy-experiment-design`
- `taxonomy-primitive-design`
- `docs/datasets/exect/exect_gold_label_audit.md`
- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md`

No code behavior was changed by this audit.

## Findings

### P1 - Gan S0 Is A Single Program Monolith, Not A Decomposition Surface

`src/clinical_extraction/programs/gan_frequency_s0.py` is over 5k physical
lines and holds prompt version history, DSPy signatures, date/event payloads,
candidate generators, adjudicators, multiple-answer selectors, ReAct tooling,
metrics, optimizer compilation, prediction artifact bridging, evidence guards,
and label surface repair.

Concrete evidence:

- Variant and prompt constants span the top-level namespace:
  `src/clinical_extraction/programs/gan_frequency_s0.py:39`.
- Stage graph mapping is a dictionary beside prompt constants, not a typed
  variant contract: `src/clinical_extraction/programs/gan_frequency_s0.py:196`.
- Prompt-version dispatch is a long string branch:
  `src/clinical_extraction/programs/gan_frequency_s0.py:1102`.
- Module construction is another long string branch:
  `src/clinical_extraction/programs/gan_frequency_s0.py:4512`.
- Prediction bridging mixes abstention repair, final-label rejection, canonical
  surface repair, evidence fallback, and metadata assembly:
  `src/clinical_extraction/programs/gan_frequency_s0.py:4973`.

Why this matters: the active Gan cards require candidate inventory, temporal
anchoring, target selection, label construction, unknown/no-reference policy,
and evidence/schema diagnostics to be measured independently. The current file
stores those stages as program-variant branches inside one orchestration module,
so G1/G2 cannot cleanly report which component helped or failed.

Recommended simplification: create a Gan S0 package with behavior-preserving
wrappers:

- `gan/s0/variant_registry.py` for typed variant specs, status, prompt default,
  stage graph, scorer mode, and active/rejected status.
- `gan/s0/candidate_inventory.py` for deterministic/LLM/hybrid candidate
  payload interfaces.
- `gan/s0/target_selection.py` for selected-candidate and reason-code outputs.
- `gan/s0/label_construction.py` for canonical label construction and surface
  repair, keeping raw model labels preserved.
- `gan/s0/prediction_bridge.py` for artifact conversion and evidence guards.

Validation before and after each extraction:

- `uv run pytest tests/test_gan_s0_program.py tests/test_gan_temporal_candidates.py tests/test_gan_slot_payload.py -q`
- `uv run pytest tests/test_gan_scoring.py tests/test_gan_paper_reproduction_scoring.py -q`
- At least one fixture-level prediction parity check for builder-gap v1 and D1
  v1.2b on the same record IDs.

Preservation risk: do not collapse `unknown` and `no seizure frequency reference`
outside `gan2026_paper_reproduction`, and do not compare newly separated
component metrics to older canonical reports unless the scorer mode is explicit.

### P1 - ExECT S0/S1 Entangles Raw Extraction, Bridge Policy, Prompt Policy, And Artifact Repair

`src/clinical_extraction/programs/exect_s0_s1.py` is over 3k lines and is the
wrong shape for E2's raw/bridge/prompt causal split.

Concrete evidence:

- Variant, repair-policy, scorer, and prompt-version constants are all top-level:
  `src/clinical_extraction/programs/exect_s0_s1.py:30`.
- Module construction is string-dispatched over historical arms:
  `src/clinical_extraction/programs/exect_s0_s1.py:1884`.
- `_predict_record` performs raw model invocation, repair-policy routing,
  benchmark-bridge application, candidate metadata, and output artifact
  assembly in one function:
  `src/clinical_extraction/programs/exect_s0_s1.py:2197`.
- Diagnosis header and specificity helpers are duplicated with the primitive
  implementation: program copy at
  `src/clinical_extraction/programs/exect_s0_s1.py:2521`; primitive copy at
  `src/clinical_extraction/exect/primitives.py:1243`.
- Current-prescription augmentation is a benchmark-sensitive note parser inside
  the program file: `src/clinical_extraction/programs/exect_s0_s1.py:2600`.

Why this matters: E2 needs to say whether S1 errors come from extraction, bridge
policy, prompt policy, specificity collapse, or scope. Right now those effects
are interleaved during prediction artifact creation, so a strong S1 metric can
hide deterministic bridge compensation.

Recommended simplification:

- Move S1 bridge logic into family-specific primitive/bridge modules and expose
  a typed `S1BridgePolicy`.
- Preserve raw extraction values, bridge-normalized values, bridge flags, and
  final benchmark-facing values as separate artifact fields or metadata.
- Keep the existing public `build_exect_s0_s1_module` and `predict_exect_records`
  wrappers until configs and tests are migrated.

Validation:

- `uv run pytest tests/test_exect_s0_s1_program.py tests/test_exect_diagnosis_primitives.py tests/test_exect_medication_primitives.py -q`
- `uv run pytest tests/test_exect_scoring.py tests/test_exect_loader.py -q`
- A small raw/bridge parity fixture set covering diagnosis specificity collapse,
  seizure-type co-listing, brand medication normalization, and current Rx lines.

Preservation risk: ExECT JSON diagnosis/seizure-type source policy, certainty
threshold, medication CUIPhrase preference, and specificity collapse must remain
unchanged unless the scorer policy document and tests change in the same PR.

### P1 - ExECT Frequency Candidate Logic Is A Hidden Payload, Not A First-Class E1 Substrate

The active E1 card asks for a no-model frequency event/rate payload audit. The
current implementation has useful rules, but they are buried inside
`src/clinical_extraction/exect/primitives.py`.

Concrete evidence:

- Frequency candidate payloads begin inside the broad primitive module:
  `src/clinical_extraction/exect/primitives.py:1668`.
- The ExECT frequency label-set builder imports Gan temporal candidates inside
  the function body: `src/clinical_extraction/exect/primitives.py:1946`.
- The broad builder mixes qualitative cue matching, seizure-free guards, rate
  parsing, and Gan-candidate filtering:
  `src/clinical_extraction/exect/primitives.py:1954`.
- The high-precision builder duplicates most parsing mechanics:
  `src/clinical_extraction/exect/primitives.py:2143`.

Why this matters: E1 needs coverage, precision, and full-label coverage by
label type. The current surface returns labels, not a typed event/rate/cue
inventory with enough provenance to explain misses and false positives.

Recommended simplification:

- Extract `exect/frequency_payload.py` with typed rate/event/cue records:
  quantitative rate, qualitative change, seizure-free, zero-rate,
  type-associated, temporal scope, and multi-label support.
- Keep `exect.frequency.rate_candidates.v1` as a compatibility primitive, but
  make it render from the typed payload instead of owning the parser.
- Make Gan-candidate reuse an explicit adapter field rather than an in-function
  import hidden in the ExECT parser.

Validation:

- `uv run pytest tests/test_exect_frequency_primitives.py tests/test_exect_frequency_slot_payload.py -q`
- A new E1 coverage report that separates document coverage, label coverage,
  precision samples, and label-type strata.

Preservation risk: do not infer seizure type from frequency rows; do not convert
Gan monthly labels into ExECT benchmark truth; keep MarkupSeizureFrequency
templates as the benchmark-facing surface until an explicit policy changes it.

### P1 - ExECT S4 And S5 Operational Stack Variants Are Bundled With Component Probes

`src/clinical_extraction/programs/exect_s4.py` now carries both S4 family work
and S5 operational stack variants.

Concrete evidence:

- S4 and S5 variant constants share the same namespace:
  `src/clinical_extraction/programs/exect_s4.py:64`.
- Module factory routing dispatches S4 frequency pre-vocab, S5 medication guard,
  S5 frequency verifier, and S5 parallel core variants together:
  `src/clinical_extraction/programs/exect_s4.py:1091`.
- `_predict_s4_record` special-cases S5, imports S1 medication helpers inside
  the function, filters and rebuilds annotated-medication values, and assembles
  component metadata:
  `src/clinical_extraction/programs/exect_s4.py:1345`.
- Frequency verifier guards are implemented in the same file as the broad S4/S5
  prediction path:
  `src/clinical_extraction/programs/exect_s4.py:1711`.

Why this matters: the current research program says S5 v2b is an operational
stacked baseline, not a component ceiling. Keeping S5 stack repair and S4
component probes in one module invites new prompt/guard changes that look like
component progress but actually modify the stacked system.

Recommended simplification:

- Split `programs/exect_s5_core.py` from S4, with a stable wrapper for existing
  configs.
- Move medication guard and frequency verifier logic into family bridge/verifier
  modules that can be called by isolated component probes and the stack.
- Make stack composition explicit: S1/S2/S3/S4 family values in, S5 stack values
  out, with interference metadata.

Validation:

- `uv run pytest tests/test_exect_s4_program.py tests/test_exect_s5_scoring.py tests/test_exect_s5_frequency_verifier.py -q`
- Parity on the current S5 v2b full-validation artifact shape before any new
  component run.

Preservation risk: do not treat S5 stack improvements as isolated family
ceilings; keep medication temporality diagnostic unless the gold policy changes.

### P2 - Experiment Config Validation Makes Obsolete Arms Sticky

`src/clinical_extraction/experiments/config.py` imports every program variant
constant from every program module, then keeps a central literal list and
contract table.

Concrete evidence:

- Variant imports span program modules:
  `src/clinical_extraction/experiments/config.py:9`.
- The `program_variant` literal contains old and new Gan/ExECT arms:
  `src/clinical_extraction/experiments/config.py:276`.
- Dataset/schema/program/scorer compatibility is a hand-maintained central map:
  `src/clinical_extraction/experiments/config.py:342`.

Why this matters: C2 cannot safely delete, archive, or demote stale program
surfaces while the validator itself is a dependency on those surfaces. The
current shape also makes new component variants feel like another string in a
long enum rather than a typed research contract.

Recommended simplification:

- Introduce a program registry whose rows include dataset, schema level, program
  variant, scorer mode(s), prompt default, stage graph, current status, and
  deprecation/replacement target.
- Let program modules register specs while preserving importable constants for
  backward compatibility during the migration.
- Generate config validation and C2 inventory from the same registry.

Validation:

- `uv run pytest tests/test_experiment_configs.py tests/test_experiment_registry_validation.py -q`
- `uv run python scripts/validate_experiment_taxonomy.py --errors-only`

Preservation risk: old configs and run artifacts must remain loadable or have a
documented archive/replay path before variant constants are removed.

### P2 - Registry Backfill And Analysis Scripts Contain Hard-Coded Historical Knowledge

Some scripts are still doing one-off registry/report work with hard-coded rows
and implicit scorer assumptions.

Concrete evidence:

- `scripts/backfill_hybrid_cap25_registry.py` starts with hundreds of lines of
  static row dictionaries before executable logic:
  `scripts/backfill_hybrid_cap25_registry.py:20`; helper functions begin around
  `scripts/backfill_hybrid_cap25_registry.py:831`.
- `docs/experiments/synthesis/experiment_registry.json` is a 17k-line monolith.
- `scripts/analyze_gan_frequency_run.py` calls `score_gan_frequency_prediction`
  without exposing scorer mode, so it defaults to canonical Gan scoring:
  `scripts/analyze_gan_frequency_run.py:130`; the scorer default is
  `gan_frequency_deterministic_v1` at
  `src/clinical_extraction/gan/scoring.py:44`.

Why this matters: the May 28 pivot requires active versus historical evidence
to be obvious. A C2 deletion map will be fragile if the only encoded knowledge
about old grids lives in a hard-coded script or a giant registry JSON.

Recommended simplification:

- Move static backfill rows into archived provenance or a declarative manifest.
- Generate active registry views from the program registry and component-ceiling
  registry rather than editing the giant registry directly for every decision.
- Add explicit scorer-mode flags to retained analysis scripts, defaulting direct
  Gan paper-comparison analyses to `gan2026_paper_reproduction` and labeling
  canonical mode as diagnostic.

Validation:

- `uv run pytest tests/test_export_registry_matrix.py -q`
- `uv run pytest tests/test_analyze_gan_frequency_run.py tests/test_gan_paper_reproduction_scoring.py -q`

Preservation risk: archive run IDs, decision documents, and scorer caveats
before deleting or regenerating registry rows.

### P2 - Test Coverage Is Strong But Too Coupled To Monolithic Files

The repo has meaningful regression coverage, but several test files mirror the
current monoliths and will resist behavior-preserving extraction.

Concrete evidence:

- `tests/test_experiment_configs.py` is about 3.2k lines and contains 136 tests.
- `tests/test_gan_s0_program.py` is about 2.3k lines and contains 103 tests.
- `tests/test_exect_s0_s1_program.py` is about 2.1k lines and contains 84 tests.

Why this matters: large private-helper tests are useful for protecting current
behavior, but they make it hard to split modules around real domain concepts.
If the tests stay monolithic, refactoring will either become too risky or will
require broad, noisy import churn.

Recommended simplification:

- Add stage-level characterization tests before moving code: candidate inventory,
  target selection, label construction, bridge policy, evidence guard, and
  artifact assembly.
- Split tests by domain stage after each extracted module exists.
- Keep existing giant tests temporarily as parity nets; delete private-helper
  assertions only after public stage tests cover the same semantics.

Validation: run the existing focused domain files after each extraction, then
only broaden to the full test suite when shared contracts move.

## Ranked Cleanup Sequence

1. **C2 inventory first.** Build an active/obsolete surface inventory for
   programs, configs, scripts, and helpers. Each row should include current
   status, replacement, retained provenance, and tests required before removal.
2. **Introduce typed program variant specs.** Do this before deleting arms, so
   config validation, artifact metadata, C2 inventory, and registry exports all
   read from one source.
3. **Extract Gan S0 prediction bridge and variant registry.** This is a
   behavior-preserving split that reduces the largest file without changing
   candidate logic or scorer behavior.
4. **Extract ExECT S1 benchmark bridge policy.** This directly unlocks E2 by
   separating raw extraction from deterministic bridge effects.
5. **Extract ExECT frequency payload.** Use the current frequency rules as the
   seed, but output typed payload records and an E1 coverage report before any
   model grid.
6. **Split ExECT S5 stack from S4 family program logic.** Keep the current S5
   v2b baseline reproducible, but stop adding component probes to the stacked
   program file.
7. **Retire or archive hard-coded registry backfill scripts.** Only after C2
   maps each script/config to replacement code and provenance.
8. **Split monolithic tests last.** Use them as parity coverage while modules
   move; retire private-helper assertions once public stage tests exist.

## Stop Rules

- Stop any cleanup PR that changes loader, split, scorer, or benchmark bridge
  semantics without a focused test and policy-note update.
- Stop any deletion that loses the ability to trace an active metric to run ID,
  config, model/provider, split, scorer mode, and caveat.
- Stop any ExECT S5 edit that reports a stacked-system delta as a component
  ceiling.
- Stop any Gan report that mixes `gan2026_paper_reproduction` and
  `gan_frequency_deterministic_v1` without labeling benchmark versus diagnostic
  views.

## Validation Run For This Audit

No code tests were run because this card produced a review artifact only. The
inspection used repository structure, line-count scans, targeted file reads, and
the active dataset/scorer policy docs listed above.
