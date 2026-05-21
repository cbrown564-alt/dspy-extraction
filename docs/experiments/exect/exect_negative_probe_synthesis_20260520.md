# ExECT Negative-Probe Synthesis

Date: 2026-05-20  
Status: Phase 1 consolidation note — **arm-repeat guardrail** (not global mechanism closure)  
Related: `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`, `docs/planning/kanban_plan.md`, `docs/planning/next_major_phases_20260520.md`, `docs/experiments/exect/exect_field_family_deterministic_support_map_20260520.md`, `docs/taxonomy/taxonomy_primitive_catalog.md`, `docs/experiments/synthesis/experiment_registry.json`

**Pivot note (2026-05-21):** Probes below are **reject (arm)** for named configs. They do **not** close Axis 2 mechanism classes (e.g. all `pre` placement, all verify-repair, all tool-during) without further grids per `hybrid-pipeline-exploration`.

## Research Question

Which completed ExECT deterministic probes should be treated as closed negative evidence, and what should that prevent the next experiment phase from repeating?

## Scope

This note covers local ExECT field-family diagnostics, not published ExECTv2 benchmark reproduction. All claims use the repository's current deterministic scorer semantics and validation/slice scopes described in the linked inspection documents.

Dataset: ExECTv2 local validation split or explicitly named validation slices.  
Models: GPT 4.1-mini for the probe-discovery track; Qwen3.6:35b Ollama for the S1 interleaving port check.  
Schema/families: S1 diagnosis/seizure/medication and S4 all-family diagnostic view with focused seizure-frequency or medication-temporality metrics.

## Closed Probe Summary

| Probe | Scope | Main artifacts | Decision | Why it closed |
| --- | --- | --- | --- | --- |
| S1 interleaving GPT v2 | full validation 40 | `docs/experiments/exect/exect_s1_interleaving_gpt_validation_v2_inspection_20260520.md`; runs `...190804Z`, `...190807Z` | Hold as diagnostic, not promotion | H1 post bridge matched frozen production L1 at 92.3% micro; bridge-free L1 only quantified a +23.7pp bridge contribution. |
| S1 interleaving Qwen v1 | full validation 40 | `docs/experiments/exect/exect_s1_interleaving_qwen_validation_v1_inspection_20260520.md`; runs `...210719Z`, `...210722Z` | Reject port narrative | H1 matched frozen Qwen production anchor at 79.0% micro and did not close the GPT gap; seizure F1 remained 55.7% vs GPT H1 90.5%. |
| S1 medication H2 pre-vocab | 14-record Rx-heavy slice | `docs/experiments/exect/exect_s1_medication_pre_vocab_slice_gpt_inspection_20260520.md`; runs `...191336Z`, `...191345Z` | Reject | Medication F1 regressed from 98.3% to 95.1% despite family isolation. |
| S1 seizure H2 pre-vocab | 15-record seizure-heavy slice | `docs/experiments/exect/exect_s1_seizure_pre_vocab_slice_gpt_inspection_20260520.md`; runs `...205806Z`, `...205814Z` | Reject | Seizure_type F1 regressed from 91.5% to 83.3%; static candidate lists worsened evidence alignment and surface choices. |
| S4 seizure-frequency H2 pre-candidates | cap-25 validation | `docs/experiments/exect/exect_s4_frequency_deterministic_gpt_inspection_20260520.md`; runs `...191914Z`, `...191951Z` | Reject | Primary seizure_frequency F1 regressed from 49.1% to 47.1%; pooled micro gains came from other families and do not promote the frequency mechanism. |
| S4 medication-temporality H1 post classifier | full validation 40 | `docs/experiments/exect/exect_s4_temporality_deterministic_gpt_inspection_20260520.md`; runs `...204207Z`, `...204216Z` | Reject | Precision improved by +10.1pp, but medication_temporality F1 fell by -6.6pp because recall collapsed from 95.7% to 55.3%. |

## Interpretation

The ExECT negative probes point to a consistent pattern: deterministic components can explain or diagnose benchmark-facing behavior, but their existence does not mean they should be promoted as interventions.

Post-hoc benchmark bridges are essential for interpreting current S1 scores. They recover large portions of the scored GPT and Qwen gap between raw surfaces and audited labels, especially diagnosis and seizure_type. However, the S1 H1 arms are not new interventions because they reproduce the existing production bridge path. They are diagnostic controls that quantify bridge contribution.

Pre-vocabulary and pre-candidate H2 arms did not promote across medication, seizure_type, or seizure_frequency. The likely failure mode is not a lack of deterministic surfaces alone; candidate lists can anchor the LLM to coarse or unsupported forms without improving the audited label policy. This is especially visible in seizure_type evidence failures and S4 frequency's mismatch between Gan-style temporal hints and ExECT MarkupSeizureFrequency surfaces.

The S4 medication-temporality H1 post classifier showed that post-position deterministic filtering can improve precision, but the full-validation run rejected the broad abstention policy. The follow-up error read (`docs/experiments/exect/exect_s4_temporality_planned_taper_error_read_20260520.md`) found that the recall collapse was driven mostly by unknown-abstention on dose-only ASM evidence, not by the planned/taper boundary initially suspected.

The Qwen S1 port clarifies that local-model weakness is not solved by simply applying the same bridge comparison group. Qwen raw micro F1 was close to GPT raw F1, but Qwen received much less benefit from bridges and retained a large seizure_type gap. The next Qwen S1 work should begin as seizure-gap error analysis or prompt/model-policy diagnosis, not another S1 post-bridge or H2 pre-vocab rerun.

## Decisions For Next-Phase Planning

Do not start another ExECT model-backed run until a preregistration names a new varied factor, frozen baseline, primitive IDs, scorer mode, scope, and reject/hold/promote gate.

Closed shapes that should not be rerun by default:

- S1 post-bridge H1 as an intervention; it is a diagnostic bridge-contribution control.
- Broad or static H2 pre-vocabulary injection for S1 medication or seizure_type.
- S4 seizure-frequency H2 pre-candidate injection in the tested presentation shape.
- Broad S4 medication-temporality H1 post-classifier abstention policy.
- Qwen S1 interleaving port without a new model-side or prompt-policy hypothesis.

Still plausible, but only with preregistration:

- Qwen S1 seizure-gap diagnosis, starting with error analysis rather than deterministic bridge additions.
- S4 seizure-frequency redesign if the varied factor changes candidate presentation, prompt policy, or post-template repair rather than repeating H2 pre-candidates.
- S4 medication-temporality fallback if the mechanism is narrowed to dose-only ASM current-status preservation, not a broad post-classifier retune.
- A no-run synthesis pause if none of the above can be framed as a clean single-factor comparison.

## Primitive Status Implications

Implemented primitives should be separated into reusable infrastructure versus rejected experimental arms:

- `exect.medication.benchmark_bridge.v1`, `exect.seizure_type.benchmark_bridge.v1`, and `exect.diagnosis.benchmark_bridge.v1` remain S1 benchmark-policy infrastructure and diagnostic controls.
- `exect.medication.rx_candidates.v1`, seizure pre-vocabulary surfaces, and `exect.frequency.rate_candidates.v1` should be marked rejected for the tested H2 arm shape, not removed from the catalog.
- `exect.medication_temporality.post_classifier.v1` remains a tested diagnostic/repair primitive, but the full-validation abstention policy is rejected.
- New primitive reuse should cite the comparison group and mechanism it supports; catalog existence alone is not promotion evidence.

## Caveats

The medication and seizure H2 results are slice diagnostics, not full-validation estimates. They are still enough to block promotion because the primary family metrics regressed on intentionally enriched slices.

S4 frequency H2 was cap-25 only. It failed its primary gate, so full validation was not run.

All ExECT metrics here are local field-family diagnostics. Published benchmark reproduction remains blocked on CUI-aware all-family scoring and ontology-aligned primitives.

## Next Steps

1. Use this note as the Phase 1 negative-probe synthesis artifact in `docs/planning/kanban_plan.md`.
2. Complete the primitive coverage audit so catalog statuses distinguish `promoted`, `diagnostic_only`, `rejected_for_current_arm`, `planned`, and `blocked`.
3. Choose one Phase 2 path only after preregistration: Qwen seizure-gap diagnosis, S4 frequency redesign, medication-temporality fallback, or synthesis pause.
