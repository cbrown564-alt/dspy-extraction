# Taxonomy Primitive Contract

Date: 2026-05-20  
Status: Initial contract  
Related: `docs/taxonomy/taxonomy_primitives_workstream_plan_20260520.md`, `docs/taxonomy/experiment_taxonomy_schema.md`, `src/clinical_extraction/primitives.py`

## Purpose

Taxonomy primitives are reusable deterministic or structured helpers that can be placed before, during, after, or outside model prediction. They make hybrid experiments comparable by naming the helper, the knowledge it uses, where it enters the pipeline, how strongly it controls prediction, and which experiment arms it can support.

The contract is deliberately metadata-first. A primitive can be planned before code exists, but it must still declare the input and output contract clearly enough for deterministic tests, fixtures, and experiment templates to use it later.

## Source Of Truth

Primitive metadata lives first as typed Python records using `PrimitiveMetadata` in `src/clinical_extraction/primitives.py`.

This is the current registry-location decision for Card 16:

- Python metadata is the source of truth because later experiment builders and validators need typed access without parsing Markdown.
- Markdown docs summarize and inspect the registry, but should not become a second independent metadata source.
- A generated JSON or Markdown export can be added later if the registry grows large enough for external review tooling.

## Required Fields

| Field | Meaning |
| --- | --- |
| `primitive_id` | Stable dotted identifier ending in a version, such as `gan.frequency.temporal_candidates.v1`. |
| `name` | Human-readable primitive name. |
| `dataset` | `gan_2026`, `exect_v2`, or `shared`. |
| `field_families` | One or more clinical families affected by the primitive. |
| `clinical_operation` | Candidate generation, normalization, benchmark bridge, evidence support, verification, repair, tool interface, fixture definition, or inspection/reporting. |
| `knowledge_sources` | Controlled sources such as temporal rules, controlled vocabulary, benchmark label policy, gold audit policy, or diagnostic metrics. |
| `hybrid_balance_class` | Experiment-taxonomy balance classes the primitive can instantiate. |
| `interleaving_positions` | Where the primitive enters the pipeline: `pre`, `during`, `tool_during`, `post`, or `eval_only`. |
| `control_modes` | Whether the primitive is a soft hint, hard constraint, tool affordance, posthoc correction, or diagnostic-only helper. |
| `input_contract` | Short statement of what the primitive consumes. |
| `output_contract` | Short statement of what the primitive returns or guarantees. |
| `compatible_experiment_arms` | L0/L1/H1/H2/H3/H4/D1 arms that can use this primitive. |
| `status` | `planned`, `implemented`, `validated`, or `deprecated`. |

Optional fields include `normalization_scope`, `caveats`, `intended_comparison_groups`, and `implementation_refs`.

## Validation Rules

- Text contract fields must be non-empty.
- `posthoc_correction` requires `post` interleaving.
- `tool_affordance` requires `tool_during` interleaving.
- `diagnostic_only` requires `eval_only` interleaving.
- Normalization primitives infer `normalization_scope` from their operation and knowledge sources unless it is set explicitly.
- Eval-only or diagnostic-only primitives are not prediction-affecting.

## Initial Example Records

The deterministic test suite validates representative records:

- `gan.frequency.temporal_candidates.v1`: Gan frequency candidate generation using temporal and regex rules, gold audit policy, and pre-model soft hints.
- `gan.frequency.label_policy_bridge.v1`: Gan label-policy normalization preserving raw, canonical, benchmark-facing, monthly, Purist, and Pragmatic values.
- `gan.frequency.evidence_guard.v1`: Gan-specific evidence support checks that preserve unknown/no-reference distinctions and treat `...` evidence as multi-span support.
- `exect.medication.benchmark_bridge.v1`: ExECT medication normalization and benchmark bridge as a posthoc correction.
- `exect.seizure_type.benchmark_bridge.v1`: ExECT seizure-type bridge for granular-surface coarsening, fused-phrase splits, secondary-token handling, and benchmark-facing seizure labels.
- `exect.diagnosis.benchmark_bridge.v1`: ExECT diagnosis bridge for uncertainty stripping, specificity collapse, note-gated co-listing, symptomatic/on-awakening surface repair, empty-list header recovery, and explicit certainty-policy diagnostics.
- `shared.evidence.substring_support.v1`: shared deterministic evidence support diagnostics for exact substring, unsupported quote, normalized-interpretation, and no-reference cases.

## Payload Models

The first shared payload contracts are implemented in `src/clinical_extraction/primitives.py`:

- `PrimitiveCandidate`: deterministic hint/candidate records for temporal candidates, medication candidates, frequency surfaces, section spans, and later controlled-vocabulary hints. It preserves raw text, normalized value, benchmark-facing value, source span text, optional offsets, rule name, confidence, caveats, and metadata separately.
- `NormalizationResult`: normalization and benchmark-bridge records that separate raw value, canonical value, benchmark-facing value, clinical caveat, transformation rule, prediction-affecting status, and scorer-only status.
- `EvidenceSupportResult`: deterministic support records for exact quote support, normalized-interpretation support, unsupported quote, and no-reference cases.
- `check_evidence_support`: a no-model helper for exact substring and interpretation-evidence checks. This helper is deliberately conservative: exact quote support does not imply that the normalized interpretation is valid.

The payload models are shared infrastructure. Dataset-specific primitive packs still need to decide whether and how these records affect prediction, post-processing, or diagnostic reporting. The initial Gan pack uses the shared records in scorer-only/diagnostic mode by default; callers must explicitly opt into prediction-affecting bridge behavior.

## Caveats

This contract now covers the initial metadata and payload layers, the first Gan frequency, ExECT medication, ExECT seizure-type, ExECT diagnosis, and ExECT S4 frequency primitive packs, the initial interleaving adapter layer in `src/clinical_extraction/interleaving_adapters.py`, experiment arm templates in `src/clinical_extraction/experiments/arm_templates.py`, inspection templates under `docs/templates/`, the primitive fixture library in `data/fixtures/primitive_cases.json` with loader helpers in `src/clinical_extraction/fixtures/primitive_cases.py`, planned ExECT family sketches in `src/clinical_extraction/exect/family_backlog.py`, and consolidated registry validation via `scripts/validate_primitives.py`.
