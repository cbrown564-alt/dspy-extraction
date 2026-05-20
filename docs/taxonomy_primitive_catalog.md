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
| `exect.frequency.rate_candidates.v1` | ExECTv2 | frequency | pre | soft hint | implemented | S4 seizure-frequency deterministic probes | Use ExECT MarkupSeizureFrequency templates, not Gan monthly policy; cap-25 H2 pre-vocab was rejected so keep off default paths. |
| `exect.frequency.benchmark_bridge.v1` | ExECTv2 | frequency | post | posthoc correction | implemented | S4 raw vs bridge and post-classifier follow-ups | Repairs near-miss quantified rates, strips seizure-type confusion, blocks non-audited periods, and note-anchors qualitative co-labels; abstention is empty-list, not Gan no-reference. |
| `exect.medication.rx_candidates.v1` | ExECTv2 | medication | pre | soft hint | implemented | Medication-only H2 slices or post-classifier fixtures | Broad S1 pre-vocabulary was rejected; keep candidate lists medication-scoped; planned/previous candidates are diagnostic, not S1 current prescription outputs. |
| `exect.sections.family_spans.v1` | ExECTv2 | multi_family | pre | soft hint | planned | Section-aware or family-filtered extraction arms | Section filtering is not automatically promotable; preserve full-note baselines. |

## Broad ExECT Family Backlog (Card 11)

Sparse S2–S4 families sketched for catalog review. Implementation waits until S1/S4 high-signal probes settle.

| Primitive ID | Dataset | Family | Position | Control | Status | Intended experiments | Caveats |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `exect.investigation.surface_bridge.v1` | ExECTv2 | investigation | post | posthoc correction | planned | S4 investigation normalization follow-ups | Modality+result canonical strings; separate from planned-scan guard. |
| `exect.investigation.planned_scan_guard.v1` | ExECTv2 | investigation | post | posthoc correction | planned | S4 unavailable/planned scan repair | Do not score future-tense plans as completed results. |
| `exect.comorbidity.overlap_policy.v1` | ExECTv2 | comorbidity | post | posthoc correction | planned | S3 overlap resolver slices | Cause and comorbidity gold are independent; scorer does not deduplicate. |
| `exect.birth_development.cui_phrase_bridge.v1` | ExECTv2 | birth_development | post | posthoc correction | planned | S3 sparse-family bridge probes | Very sparse validation support; paraphrase mismatch common. |
| `exect.onset.cui_phrase_bridge.v1` | ExECTv2 | onset | post | posthoc correction | planned | S3 onset canonicalization | CUIPhrase surfaces; age/year attributes are not benchmark labels. |
| `exect.epilepsy_cause.cui_phrase_bridge.v1` | ExECTv2 | epilepsy_cause | post | posthoc correction | planned | S3 cause versus comorbidity slices | Same phrase may score in both cause and comorbidity. |
| `exect.when_diagnosed.cui_phrase_bridge.v1` | ExECTv2 | when_diagnosed | post | posthoc correction | planned | S3 timing-surface repair | Duplicate predictions across diagnosis and when_diagnosed are expected noise. |
| `exect.family_history.cui_phrase_bridge.v1` | ExECTv2 | family_history | post | posthoc correction | planned | Future patient-history arms | Defer until higher-signal S1/S4 probes settle. |
| `exect.social_history.cui_phrase_bridge.v1` | ExECTv2 | social_history | post | posthoc correction | planned | Patient-history normalization | Published Table 1 uses Patient History naming. |
| `exect.driving.cui_phrase_bridge.v1` | ExECTv2 | driving | post | posthoc correction | planned | Sparse-family design only | Low priority until S4 frequency/temporality probed. |
| `exect.pregnancy.cui_phrase_bridge.v1` | ExECTv2 | pregnancy | post | posthoc correction | planned | Sparse-family design only | Design only; not an active interleaving target. |

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
| `shared.fixtures.primitive_cases.v1` | shared | multi_family | eval_only | diagnostic_only | implemented | Deterministic primitive tests | Fixture library in `data/fixtures/primitive_cases.json`; loader and invoker in `src/clinical_extraction/fixtures/primitive_cases.py`. |
| `shared.reporting.primitive_inspection.v1` | shared | multi_family | eval_only | diagnostic_only | implemented | Inspection/decision templates | Templates in `docs/templates/`; section contracts in `src/clinical_extraction/experiments/inspection_templates.py`. |

## Deferred Or Blocked

| Primitive ID | Dataset | Family | Position | Control | Status | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| `exect.ontology.cui_alignment.v1` | ExECTv2 | multi_family | post/eval_only | posthoc correction/diagnostic_only | planned | Deferred until published ExECT benchmark reproduction work is explicitly in scope. |
| `gan.frequency.real_set_validation.v1` | Gan 2026 | frequency | eval_only | diagnostic_only | planned | Blocked on Real(300)/Real(150)-style data access. |

## Open Review Notes

- The catalog is intentionally broader than the initial typed seed registry. It should not be treated as proof that a primitive is useful.
- Promotion still requires valid comparison groups, fixed scorer semantics, and inspection documents.
- Shared candidate, normalization, and evidence payload models now exist as initial contracts. The primitive fixture library now exercises implemented Gan and ExECT packs without model calls.
- Card 11 broad ExECT family sketches are registered as planned metadata in `src/clinical_extraction/exect/family_backlog.py`; implementation waits until S1/S4 high-signal probes settle.
- Cards 17 and 18 decisions are recorded in `docs/taxonomy_tool_interface_decision_20260520.md` and `docs/taxonomy_ontology_cui_scope_decision_20260520.md`.
- No-model validation: `uv run python scripts/validate_primitives.py --errors-only`.
- Interleaving adapters in `src/clinical_extraction/interleaving_adapters.py` can render the same primitive core logic at pre, during, tool_during, post, or eval_only surfaces for controlled interleaving experiments.
- Experiment arm builders in `src/clinical_extraction/experiments/arm_templates.py` prefill L1/H1/H2/H3/H4/D1 taxonomy metadata and validate primitive compatibility before emitting configs.
