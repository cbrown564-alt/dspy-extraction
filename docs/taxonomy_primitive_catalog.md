# Taxonomy Primitive Catalog

Date: 2026-05-20  
Status: Seed catalog  
Related: `docs/taxonomy_primitive_contract.md`, `docs/taxonomy_primitives_workstream_plan_20260520.md`, `docs/exect_field_family_deterministic_support_map_20260520.md`, `docs/gan_s0_temporal_candidate_pivot_20260519.md`

## Purpose

This catalog lists current and planned reusable primitives by clinical operation and taxonomy position. The typed contract lives in `src/clinical_extraction/primitives.py`; this document is the review surface for deciding which primitives should be implemented, tested, promoted, or deferred.

## Candidate Generation

| Primitive ID | Dataset | Family | Position | Control | Status | Intended experiments | Caveats |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `gan.frequency.temporal_candidates.v1` | Gan 2026 | frequency | pre | soft hint | implemented | Gan temporal candidates / H2-H4 frequency arms | Preserve Gan `seizure_frequency_number[0]` as gold; monthly normalization does not transfer directly to ExECT; shared candidate payload contract now exists for future adapter work. |
| `exect.frequency.rate_candidates.v1` | ExECTv2 | frequency | pre | soft hint | planned | S4 seizure-frequency deterministic probes | Use ExECT MarkupSeizureFrequency templates, not Gan monthly policy. |
| `exect.medication.rx_candidates.v1` | ExECTv2 | medication | pre | soft hint | implemented | Medication-only H2 slices or post-classifier fixtures | Broad S1 pre-vocabulary was rejected; keep candidate lists medication-scoped; planned/previous candidates are diagnostic, not S1 current prescription outputs. |
| `exect.sections.family_spans.v1` | ExECTv2 | multi_family | pre | soft hint | planned | Section-aware or family-filtered extraction arms | Section filtering is not automatically promotable; preserve full-note baselines. |

## Normalization And Benchmark Bridges

| Primitive ID | Dataset | Family | Position | Control | Status | Intended experiments | Caveats |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `exect.medication.benchmark_bridge.v1` | ExECTv2 | medication | post | posthoc correction | implemented | H1 post bridge, medication temporality follow-up | Benchmark prescription alignment is not the same as clinically rich medication status; brand surfaces are preserved when the note uses an audited brand form and non-ASM medications are rejected. |
| `exect.seizure_type.benchmark_bridge.v1` | ExECTv2 | seizure_type | post | posthoc correction | implemented | S1 raw vs bridge and Qwen seizure-gap probes | Coarsens granular focal surfaces, splits fused temporal-lobe and secondary-generalisation phrases, rejects jerk/absence descriptors, and can co-list the secondary token; avoid using seizure-frequency spans as seizure-type evidence unless the audit supports it. |
| `exect.diagnosis.benchmark_bridge.v1` | ExECTv2 | diagnosis | post | posthoc correction | implemented | S1 raw vs bridge and diagnosis recall checks | Strips uncertainty qualifiers, applies audited specificity collapse, restores symptomatic/on-awakening surfaces, and note-gates co-list augmentation; do not infer diagnosis from seizure type alone. |
| `gan.frequency.label_policy_bridge.v1` | Gan 2026 | frequency | post/eval_only | posthoc correction/diagnostic_only | implemented | Gan frequency repair diagnostics and scorer-only audits | Keep scorer semantics fixed; bridge output preserves raw, canonical, benchmark-facing, monthly, Purist, and Pragmatic values separately. |

## Evidence Support

| Primitive ID | Dataset | Family | Position | Control | Status | Intended experiments | Caveats |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `shared.evidence.substring_support.v1` | shared | multi_family | eval_only | diagnostic_only | implemented | Evidence diagnostics across Gan and ExECT | Exact quote support can validate a raw quote without validating the normalized interpretation. |
| `shared.evidence.verified_quote.v1` | shared | multi_family | post | posthoc correction | planned | H1 evidence guard and verifier-repair policies | Must distinguish unsupported quotes from no-reference cases. |
| `gan.frequency.evidence_guard.v1` | Gan 2026 | frequency | post/eval_only | posthoc correction/diagnostic_only | implemented | Gan frequency guardrails and repair comparisons | Evidence support remains diagnostic unless a decision doc says it affects prediction; elided Gan gold evidence is ordered multi-span support, not an exact quote. |

## Verification, Repair, And Tool Interfaces

| Primitive ID | Dataset | Family | Position | Control | Status | Intended experiments | Caveats |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `gan.frequency.verify_repair_policy.v1` | Gan 2026 | frequency | post | posthoc correction | implemented | Gan verify-repair variants | Hosted GPT benefited; local Qwen verifier damaged some correct temporal labels. |
| `gan.frequency.temporal_tool.v1` | Gan 2026 | frequency | tool_during | tool affordance | implemented | Gan ReAct / H3 negative-control comparisons | Do not make H3 default after the negative ReAct result. |
| `exect.medication_temporality.post_classifier.v1` | ExECTv2 | medication | post/eval_only | posthoc correction/diagnostic_only | implemented | S4 medication-temporality precision probe | Cue-based because MarkupPrescriptions has no temporality column; current prescription lines with taper instructions remain current unless the medication is only a separate stop/plan mention. |

## Fixtures And Inspection

| Primitive ID | Dataset | Family | Position | Control | Status | Intended experiments | Caveats |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `shared.fixtures.primitive_cases.v1` | shared | multi_family | eval_only | diagnostic_only | planned | Deterministic primitive tests | Fixtures should cover positive, negative, ambiguous, absent, historical, planned, and unsupported-evidence cases. |
| `shared.reporting.primitive_inspection.v1` | shared | multi_family | eval_only | diagnostic_only | planned | Inspection/decision templates | Reports must name primitive IDs, scorer mode, normalization semantics, evidence semantics, and caveats. |

## Deferred Or Blocked

| Primitive ID | Dataset | Family | Position | Control | Status | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| `exect.ontology.cui_alignment.v1` | ExECTv2 | multi_family | post/eval_only | posthoc correction/diagnostic_only | planned | Deferred until published ExECT benchmark reproduction work is explicitly in scope. |
| `gan.frequency.real_set_validation.v1` | Gan 2026 | frequency | eval_only | diagnostic_only | planned | Blocked on Real(300)/Real(150)-style data access. |

## Open Review Notes

- The catalog is intentionally broader than the initial typed seed registry. It should not be treated as proof that a primitive is useful.
- Promotion still requires valid comparison groups, fixed scorer semantics, and inspection documents.
- Shared candidate, normalization, and evidence payload models now exist as initial contracts. The next implementation cards should connect them to dataset-specific primitive packs, fixtures, and interleaving adapters.
