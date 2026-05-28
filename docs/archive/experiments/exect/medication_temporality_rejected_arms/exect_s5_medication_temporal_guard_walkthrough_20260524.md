# ExECT S5 Medication Temporal Guard (A4) — Walkthrough

Date: 2026-05-24  
Decision scope: **arm**  
Status: **Rejected (cap-25 gate)**  
Preregistration: [exect_s5_medication_temporal_guard_preregistration_20260524.md](exect_s5_medication_temporal_guard_preregistration_20260524.md)

## Research Question

Does a post-prediction temporal evidence guard improve S5 `annotated_medication` precision versus the promoted AM-guard + frequency-verifier baseline without causing a recall drop of >3.0pp?

## Implementation

| Component | Value |
| --- | --- |
| Primitive | `exect.medication.am_guard_temporal_evidence.v1` |
| Function | `recover_exect_annotated_medication_temporal_evidence_guard` |
| Program variant | `exect_s5_frequency_pre_vocab_am_guard_temporal_frequency_verify_v1` |
| Config (cap-25) | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_temporal_frequency_verify_cap25_gpt4_1_mini.json` |
| Config (full) | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_temporal_frequency_verify_full_gpt4_1_mini.json` |

The guard extends the promoted non-ASM brand-alias guard by inferring temporality from model-aligned evidence, pruning planned/previous/future ASM predictions when no note-wide current candidate exists for the same canonical medication.

## Cap-25 Run

| Field | Value |
| --- | --- |
| Run ID | `exect_s5_frequency_pre_vocab_am_guard_temporal_frequency_verify_cap25_gpt4_1_mini_20260524T203942Z` |
| Dataset / split | ExECTv2, `exectv2_fixed_v1:validation`, 25 records |
| Model | GPT 4.1-mini (`configs/models/gan_s0_gpt4_1_mini.json`) |
| Scorer | `exect_s5_core_field_family_deterministic_v1` |
| Baseline run | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini_20260524T195709Z` |

## Cap-25 Results

| Metric | Baseline (AM guard + freq verify) | A4 temporal guard | Delta | Gate |
| --- | ---: | ---: | ---: | --- |
| annotated_medication precision | 78.4% | **100.0%** | +21.6pp | Pass (primary) |
| annotated_medication recall | 100.0% | **79.3%** | **−20.7pp** | **Fail** (≤3.0pp allowed) |
| annotated_medication F1 | 87.9% | 88.5% | +0.6pp | Pass |
| seizure_frequency F1 | 73.7% | 73.7% | 0.0pp | Pass |
| diagnosis F1 | 93.0% | 93.0% | 0.0pp | Pass |
| seizure_type F1 | 92.5% | 92.5% | 0.0pp | Pass |
| investigation F1 | 93.8% | 93.8% | 0.0pp | Pass |
| micro F1 | 87.5% | 87.6% | +0.1pp | Pass |

## Gate Decision

**Reject (arm).** Precision improves to 100% on cap-25, but recall collapses from 100% to 79.3% (−20.7pp), far exceeding the preregistered 3.0pp recall guard. Full validation was not run.

## Residual Analysis

Cap-25 annotated-medication false negatives introduced by temporal pruning:

| Document | Missed gold | Likely cause |
| --- | --- | --- |
| EA0026 | topiramate | Evidence temporality inferred as non-current; no current candidate match |
| EA0029 | levetiracetam | Planned-context evidence pruned despite current prescription elsewhere |
| EA0059 | lamotrigine | Non-current evidence cue; note candidate check insufficient |
| EA0069 | lamotrigine | Same pattern as EA0059 |
| EA0116 | levetiracetam | Temporal evidence mismatch |
| EA0124 | zonisamide | Temporal evidence mismatch |

These are annotation-policy-sensitive cases: the guard correctly targets planned/previous leakage (the original A4 motivation) but also removes true current prescriptions when model evidence quotes planned/historical phrasing or when candidate matching fails to find a current note span.

## Interpretation

The temporal guard is doing the intended precision work (zero false positives on cap-25) but is too aggressive for benchmark-facing recall under ExECT S5 annotated-medication gold, which encodes current prescriptions without native temporality columns. This mirrors the earlier S4 medication-temporality H1 recall-collapse diagnosis.

The arm should remain **rejected** as an operational default. The promoted baseline stays `exect.medication.am_guard_non_asm_brand_alias.v1` with the A3 frequency verifier stack.

## A5 Note

S2/S3 middle-ladder reruns are **not needed** for current paper anchors (frozen in `docs/experiments/synthesis/paper_frozen_operational_defaults_20260524.md`).

## Taxonomy

| Field | Value |
| --- | --- |
| dataset | `exect_v2` |
| schema_complexity | `exect_s5` |
| clinical_task_family | `frequency`, `medication` |
| program_architecture | `verify_repair` |
| hybrid_balance_class | `H2_pre_deterministic`, `H1_post_deterministic`, `H4_deterministic_first_llm_adjudicates` |
| interleaving_positions | `pre`, `during`, `post` |
| varied_factor | `implementation_variant` |
| comparison_group | `exect_s5_axis1_axis2_decomposition_gpt_cap25_v1` |
| outcome | **reject** |
| decision_scope | **arm** |

## Validation Performed

- Unit tests: `tests/test_exect_medication_primitives.py` (8/8 passed)
- Primitive registry: `uv run python scripts/validate_primitives.py --errors-only` (no errors; catalog entry added)
- Config dry run: passed
- Cap-25 model run: completed and gated

## Files Touched

- `src/clinical_extraction/exect/primitives.py` — temporal guard implementation
- `src/clinical_extraction/primitives.py` — registry entry
- `src/clinical_extraction/programs/exect_s4.py` — program variant wiring
- `src/clinical_extraction/experiments/config.py`, `exect_backend.py`, `exect_prompts.py` — experiment registration
- `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_temporal_frequency_verify_*_gpt4_1_mini.json`
- `tests/test_exect_medication_primitives.py`
- `docs/taxonomy/taxonomy_primitive_catalog.md`
- `docs/experiments/exect/exect_s5_medication_temporal_guard_preregistration_20260524.md`
