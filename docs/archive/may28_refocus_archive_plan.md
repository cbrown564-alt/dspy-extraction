# May 28 Documentation Refocus Archive Plan

Status: completed archive plan
Created: 2026-05-28
Completed: 2026-05-28

This plan translates the May 28 decomposition pivot into a physical docs cleanup.
The goal is not to erase provenance. The goal is to make active guidance small
enough that a future agent cannot accidentally steer from stale experiment
history.

## Target Active Surface

After cleanup, the active docs surface should be roughly:

- top-level docs: 5-8 active files;
- Gan experiment folder: 8-12 active routing/current evidence docs;
- ExECT experiment folder: 8-12 active routing/current evidence docs;
- synthesis folder: 5-8 active paper/holdout/registry docs;
- policies/datasets/taxonomy: retained as stable guidance, with stale policy
  conflicts fixed in place;
- everything else: archived by decision boundary.

## Wave 1 - Authority Reset

Status: completed

Completed in the first pass:

- created `../current_research_program.md`;
- created `../component_ceiling_registry.md`;
- rewrote `../README.md`;
- added domain maps for `../experiments/gan/`, `../experiments/exect/`, and
  `../experiments/synthesis/`;
- marked stale memory, matrix, and mechanism-status surfaces as superseded, and
  removed the obsolete generated atlas surface.

## Wave 2 - Stale Generated Navigation

Status: completed

Remove obsolete generated atlas files and de-authorize stale matrix exports:

- deleted `research_atlas/evidence_matrix.md`
- deleted `research_atlas/decision_map.mmd`
- deleted `research_atlas/journey.mmd`
- preserved `../experiments/synthesis/experiment_registry_matrix_20260520.md`
  as a post-pivot X3 methods/provenance matrix with explicit authority caveats.

Reason: generated before the May 28 pivot and newer R11-R15 decisions. These are
not active navigation.

Replacement:

- `../component_ceiling_registry.md`
- refreshed registry matrix with explicit pointers to the C4/X1 authority
  surfaces and May 28 component-pivot caveats.

## Wave 3 - Pre-Pivot Synthesis

Status: completed

Archive as `archive/synthesis/pre_component_pivot/`:

- `experiments_methods_results_20260520.md`
- `experiments_narrative_report_20260520.md`
- `best_pipeline_benchmark_context_assessment_20260521.md`
- `core_research_questions_pipeline_review_20260524.md`
- `paper_synthesis_update_20260524.md`
- `paper_frozen_results_narrative_20260524.md`
- `paper_frozen_operational_defaults_20260524.md`
- older `paper_*_20260524.md` drafts unless the synthesis README keeps them as
  explicit paper evidence

Reason: useful provenance, but the active frame is now component ceilings before
stacking.

Replacement:

- `../experiments/synthesis/README.md`
- `../experiments/synthesis/paper_result_table_pack_20260525.md`
- `../experiments/synthesis/paper_claims_caveats_20260525.md`
- `../experiments/synthesis/test_holdout_evaluation_report_20260527.md`

## Wave 4 - Gan Experiment Evidence

Status: completed

Keep active in `experiments/gan/`:

- `README.md`
- `gan_s0_pipeline_decomposition_deep_dive_20260528.md`
- R11/R12/R13/R14/R15 decision docs
- builder-gap promotion and current baseline docs
- scorer/paper-reproduction decision docs until moved to policies

Archive older notes into decision-boundary buckets:

- `archive/experiments/gan/pre_d1_temporal_candidates/`
- `archive/experiments/gan/prompt_policy_and_examples/`
- `archive/experiments/gan/verify_repair_and_evidence/`
- `archive/experiments/gan/optimizer_and_gepa/`
- `archive/experiments/gan/model_comparison_diagnostics/`
- `archive/experiments/gan/rejected_or_held_arms/`

Reason: Gan now uses the decomposition stages in `component_ceiling_registry.md`.
Older notes are evidence for why a path is held or rejected, not current
planning surfaces.

## Wave 5 - ExECT Experiment Evidence

Status: completed

Keep active in `experiments/exect/`:

- `README.md`
- `exect_task_deep_review_20260528.md`
- current S5 v2b promotion/local-transfer evidence;
- S1 clean-ladder evidence needed for the raw/bridge/prompt causal split;
- S4/S5 frequency gold-template audit until E1 supersedes it;
- medication precision/temporality docs only where they inform the lifecycle
  payload.

Archive older notes into decision-boundary buckets:

- `archive/experiments/exect/s0_s1_label_policy_trail/`
- `archive/experiments/exect/schema_ladder_baselines/`
- `archive/experiments/exect/section_and_family_split_rejected_arms/`
- `archive/experiments/exect/frequency_pre_payload_attempts/`
- `archive/experiments/exect/medication_temporality_rejected_arms/`
- `archive/experiments/exect/model_comparison_diagnostics/`

Reason: the ladder is now a baseline and warning system, not the organizing
decomposition.

## Wave 6 - Memory Layer

Status: completed

Either refresh or archive:

- `memory/session_brief.md`
- `memory/workflow_index.md`
- `memory/dreams/*`

Rule: memory must never contain current baselines unless it is generated from
the active docs in the same pass. Stale memory is more dangerous than no memory.

## Move Rules

Before any physical move:

1. create the target archive README;
2. list old path, new path, status, reason, and replacement active doc;
3. update `docs/README.md` or the domain README only if the moved doc was linked
   from an active surface;
4. run link checks over docs;
5. do not move dataset audits, scorer policies, run artifacts, or current deep
   dives without a replacement.
