# Taxonomy Primitive Catalog

Date: 2026-05-20  
Status: Catalog aligned with primitive coverage audit  
Related: `docs/taxonomy/taxonomy_primitive_contract.md`, `docs/taxonomy/taxonomy_primitives_workstream_plan_20260520.md`, `docs/taxonomy/taxonomy_primitive_coverage_audit_20260520.md`, `docs/experiments/exect/exect_field_family_deterministic_support_map_20260520.md`, `docs/experiments/gan/gan_s0_temporal_candidate_pivot_20260519.md`

## Purpose

This catalog lists current and planned reusable primitives by clinical operation and taxonomy position. The typed contract lives in `src/clinical_extraction/primitives.py`; this document is the review surface for deciding which primitives should be implemented, tested, promoted, or deferred.

`Registry status` describes implementation state in the typed primitive registry. `Evidence status` describes the current research role from `docs/taxonomy/taxonomy_primitive_coverage_audit_20260520.md`. A primitive being implemented or validated does not imply that it is promoted for model-backed use.

## Candidate Generation

| Primitive ID | Dataset | Family | Position | Control | Registry status | Evidence status | Intended experiments | Caveats |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan.frequency.temporal_candidates.v1` | Gan 2026 | frequency | pre | soft hint | implemented | promoted | Gan temporal candidates / H2-H4 frequency arms | Promoted only for Gan S0 synthetic validation under fixed scorer semantics, paired with LLM adjudication/verify-repair. Preserve Gan `seizure_frequency_number[0]` as gold; monthly normalization does not transfer directly to ExECT. |
| `exect.frequency.rate_candidates.v1` | ExECTv2 | frequency | pre | soft hint | implemented | rejected_for_current_arm | Redesigned S4 seizure-frequency mechanisms only | Use ExECT MarkupSeizureFrequency templates, not Gan monthly policy; cap-25 H2 pre-candidates regressed seizure_frequency F1, so do not rerun the same pre-vocab arm. |
| `exect.frequency.benchmark_bridge.v1` | ExECTv2 | frequency | post | posthoc correction | implemented | diagnostic_only | S4 raw vs bridge diagnostics and redesigned post-template follow-ups | Existing bridge policy is infrastructure around ExECT frequency surfaces, not a promoted new arm; abstention is empty-list, not Gan no-reference. |
| `exect.medication.rx_candidates.v1` | ExECTv2 | medication | pre | soft hint | implemented | current_synthesis | Medication current-Rx/lifecycle payload audits and redesigned narrow arms | E3 shows annotation-derived current-Rx reproduces 47/47 validation medication labels; note-surface lifecycle candidates remain diagnostic and should stay off default S1 current-prescription paths unless a preregistered mechanism changes presentation or repair behavior. |
| `exect.sections.family_spans.v1` | ExECTv2 | multi_family | pre | soft hint | implemented | current_synthesis | Section-aware or family-filtered extraction arms | E4 implements typed document-geometry spans with validation evidence coverage reported by family; section filtering is not promoted and must be compared against full-note baselines. |

## Broad ExECT Family Backlog (Card 11)

Sparse S2–S4 families sketched for catalog review. Implementation waits until S1/S4 high-signal probes settle.

| Primitive ID | Dataset | Family | Position | Control | Registry status | Evidence status | Intended experiments | Caveats |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect.investigation.surface_bridge.v1` | ExECTv2 | investigation | post | posthoc correction | planned | planned | S4 investigation normalization follow-ups | Planned metadata only; modality+result canonical strings remain separate from planned-scan guard. |
| `exect.investigation.planned_scan_guard.v1` | ExECTv2 | investigation | post | posthoc correction | planned | planned | S4 unavailable/planned scan repair | Planned metadata only; do not score future-tense plans as completed results. |
| `exect.comorbidity.overlap_policy.v1` | ExECTv2 | comorbidity | post | posthoc correction | planned | planned | S3 overlap resolver slices | Planned metadata only; cause and comorbidity gold are independent, and scorer does not deduplicate. |
| `exect.birth_development.cui_phrase_bridge.v1` | ExECTv2 | birth_development | post | posthoc correction | planned | planned | S3 sparse-family bridge probes | CUI/phrase work is deferred until benchmark-reproduction scope is reopened; sparse validation support makes this diagnostic design only. |
| `exect.onset.cui_phrase_bridge.v1` | ExECTv2 | onset | post | posthoc correction | planned | planned | S3 onset canonicalization | CUI/phrase work is deferred until benchmark-reproduction scope is reopened; age/year attributes are not benchmark labels. |
| `exect.epilepsy_cause.cui_phrase_bridge.v1` | ExECTv2 | epilepsy_cause | post | posthoc correction | planned | planned | S3 cause versus comorbidity slices | CUI/phrase work is deferred until benchmark-reproduction scope is reopened; same phrase may score in both cause and comorbidity. |
| `exect.when_diagnosed.cui_phrase_bridge.v1` | ExECTv2 | when_diagnosed | post | posthoc correction | planned | planned | S3 timing-surface repair | CUI/phrase work is deferred until benchmark-reproduction scope is reopened; duplicate predictions across diagnosis and when_diagnosed are expected noise. |
| `exect.family_history.cui_phrase_bridge.v1` | ExECTv2 | family_history | post | posthoc correction | planned | planned | Future patient-history arms | Planned sparse-family metadata only; defer until higher-signal S1/S4 probes settle. |
| `exect.social_history.cui_phrase_bridge.v1` | ExECTv2 | social_history | post | posthoc correction | planned | planned | Patient-history normalization | Planned sparse-family metadata only; published Table 1 uses Patient History naming. |
| `exect.driving.cui_phrase_bridge.v1` | ExECTv2 | driving | post | posthoc correction | planned | planned | Sparse-family design only | Planned sparse-family metadata only; not an active interleaving target. |
| `exect.pregnancy.cui_phrase_bridge.v1` | ExECTv2 | pregnancy | post | posthoc correction | planned | planned | Sparse-family design only | Planned sparse-family metadata only; not an active interleaving target. |

## Normalization And Benchmark Bridges

| Primitive ID | Dataset | Family | Position | Control | Registry status | Evidence status | Intended experiments | Caveats |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `exect.medication.benchmark_bridge.v1` | ExECTv2 | medication | post | posthoc correction | implemented | diagnostic_only | Frozen S1 benchmark-policy bridge path and bridge-contribution diagnostics | Benchmark prescription alignment is scorer-policy infrastructure, not a promoted H1 intervention; it is not equivalent to clinically rich medication status. |
| `exect.seizure_type.benchmark_bridge.v1` | ExECTv2 | seizure_type | post | posthoc correction | implemented | diagnostic_only | S1 raw vs bridge diagnostics and Qwen seizure-gap error analysis | Quantifies bridge contribution, but Qwen seizure gap persists after bridging; next work should diagnose model/prompt policy rather than rerun post-bridge arms. |
| `exect.diagnosis.benchmark_bridge.v1` | ExECTv2 | diagnosis | post | posthoc correction | implemented | diagnostic_only | S1 raw vs bridge diagnostics and diagnosis recall checks | Bridge remains scorer-policy infrastructure; do not infer diagnosis from seizure type alone. |
| `gan.frequency.label_policy_bridge.v1` | Gan 2026 | frequency | post/eval_only | posthoc correction/diagnostic_only | implemented | diagnostic_only | Gan frequency repair diagnostics and scorer-only audits | Keep scorer semantics fixed; bridge output preserves raw, canonical, benchmark-facing, monthly, Purist, and Pragmatic values separately. |
| `gan.frequency.aggregation_constructor.v1` | Gan 2026 | frequency | post/eval_only | posthoc correction/diagnostic_only | implemented | mechanism_open | G21 quantified-rate answer-option construction fixtures | Creates separate constructed answer options only for G16-eligible quantified-rate aggregation rows; excludes duration, special labels, cluster flattening, inventory gaps, and final target selection. |

## Evidence Support

| Primitive ID | Dataset | Family | Position | Control | Registry status | Evidence status | Intended experiments | Caveats |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `shared.evidence.substring_support.v1` | shared | multi_family | eval_only | diagnostic_only | implemented | diagnostic_only | Evidence diagnostics across Gan and ExECT | Exact quote support can validate a raw quote without validating the normalized interpretation. |
| `shared.evidence.verified_quote.v1` | shared | multi_family | post | posthoc correction | planned | planned | H1 evidence guard and verifier-repair policies | Needs a comparison group before prediction-affecting use; must distinguish unsupported quotes from no-reference cases. |
| `gan.frequency.evidence_guard.v1` | Gan 2026 | frequency | post/eval_only | posthoc correction/diagnostic_only | implemented | diagnostic_only | Gan frequency guardrails and repair comparisons | Evidence support is required for interpretation but remains diagnostic unless a decision doc makes it prediction-affecting; elided Gan gold evidence is ordered multi-span support, not an exact quote. |

## Verification, Repair, And Tool Interfaces

| Primitive ID | Dataset | Family | Position | Control | Registry status | Evidence status | Intended experiments | Caveats |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gan.frequency.verify_repair_policy.v1` | Gan 2026 | frequency | post | posthoc correction | implemented | promoted | Gan verify-repair variants | Promoted as part of the Gan temporal-candidates default, not as a standalone verifier-only claim; local Qwen verifier-only variants remain caveated by slice regressions. |
| `gan.frequency.temporal_tool.v1` | Gan 2026 | frequency | tool_during | tool affordance | implemented | rejected_for_current_arm | Gan ReAct / H3 negative-control comparisons | Tool-during ReAct did not replace preconditioning; keep as negative control, not default path. |
| `exect.medication_temporality.post_classifier.v1` | ExECTv2 | medication | post/eval_only | posthoc correction/diagnostic_only | implemented | rejected_for_current_arm | Redesigned S4 medication-temporality fallback only | Full-validation H1 rejected because broad abstention over-pruned dose-only current ASM evidence; a dose-only fallback would be a new preregistered mechanism. |
| `exect.medication_temporality.non_asm_guard.v1` | ExECTv2 | medication | post/eval_only | posthoc correction/diagnostic_only | implemented | open | G0 tier: non-ASM removal only; preserves model ASM status | Cap-25 grid `exect_s4_medication_precision_guard_gpt_cap25_v1`; see `docs/experiments/exect/exect_s4_medication_precision_guard_design_20260521.md`. |
| `exect.medication_temporality.non_asm_dose_current_guard.v1` | ExECTv2 | medication | post/eval_only | posthoc correction/diagnostic_only | implemented | open | G0G2 tier: non-ASM removal plus dose-current preservation and unsupported planned/previous pruning | Cap-25 config `exect_s4_mt_guard_g0g2_dose_current_cap25_gpt4_1_mini.json`; narrow follow-up to the H1 recall-collapse diagnosis, not a default until model-backed gates pass. |
| `exect.medication.am_guard_non_asm_brand_alias.v1` | ExECTv2 | medication | post/eval_only | posthoc correction/diagnostic_only | implemented | promoted_for_s5_guard_arm | ExECT S5 annotated medication precision validation | Drops non-ASMs, repairs spelling surfaces (eplim/eplim chrono), preserves benchmark-facing Epilim/Lamictal surfaces, and dedupes same-canonical medications. |
| `exect.medication.am_guard_temporal_evidence.v1` | ExECTv2 | medication | post/eval_only | posthoc correction/diagnostic_only | implemented | open | ExECT S5 A4 annotated-medication temporal guard | Extends AM guard with planned/previous/future ASM pruning when evidence lacks current prescription cues and note candidates do not support current status; separately preregistered from brand-alias guard. |


## Fixtures And Inspection

| Primitive ID | Dataset | Family | Position | Control | Registry status | Evidence status | Intended experiments | Caveats |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `shared.fixtures.primitive_cases.v1` | shared | multi_family | eval_only | diagnostic_only | implemented | diagnostic_only | Deterministic primitive tests | Fixture library supports validation, not model-backed claims. |
| `shared.reporting.primitive_inspection.v1` | shared | multi_family | eval_only | diagnostic_only | implemented | diagnostic_only | Inspection/decision templates | Reporting infrastructure for traceability. |

## Deferred Or Blocked

| Primitive ID | Dataset | Family | Position | Control | Registry status | Evidence status | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `exect.ontology.cui_alignment.v1` | ExECTv2 | multi_family | post/eval_only | posthoc correction/diagnostic_only | planned | blocked | Deferred until published ExECT benchmark reproduction work is explicitly in scope. |
| `gan.frequency.real_set_validation.v1` | Gan 2026 | frequency | eval_only | diagnostic_only | planned | blocked | Blocked on Real(300)/Real(150)-style data access. |

## Open Review Notes

- The catalog is intentionally broader than the initial typed seed registry. It should not be treated as proof that a primitive is useful.
- Promotion still requires valid comparison groups, fixed scorer semantics, and inspection documents.
- Current promoted primitives are limited to Gan S0 temporal candidates plus verify-repair under synthetic validation. ExECT implemented primitives are diagnostic infrastructure, planned metadata, or rejected for the current H1/H2 arm shapes.
- ExECT medication, seizure-type, diagnosis, and frequency benchmark bridges remain useful scorer-policy infrastructure, but they do not justify another post-bridge rerun by themselves.
- ExECT medication, medication-temporality, and frequency candidate/classifier primitives require a new mechanism before any model-backed reuse.
- Shared candidate, normalization, and evidence payload models now exist as initial contracts. The primitive fixture library now exercises implemented Gan and ExECT packs without model calls.
- Card 11 broad ExECT family sketches are registered as planned metadata in `src/clinical_extraction/exect/family_backlog.py`; implementation waits until S1/S4 high-signal probes settle.
- Cards 17 and 18 decisions are recorded in `docs/taxonomy/taxonomy_tool_interface_decision_20260520.md` and `docs/taxonomy/taxonomy_ontology_cui_scope_decision_20260520.md`.
- No-model validation: `uv run python scripts/validate_primitives.py --errors-only`.
- Interleaving adapters in `src/clinical_extraction/interleaving_adapters.py` can render the same primitive core logic at pre, during, tool_during, post, or eval_only surfaces for controlled interleaving experiments.
- Experiment arm builders in `src/clinical_extraction/experiments/arm_templates.py` prefill L1/H1/H2/H3/H4/D1 taxonomy metadata and validate primitive compatibility before emitting configs.
