# ExECT S1 Interleaving GPT Validation v1 — Inspection

Date: 2026-05-20  
Comparison group: `exect_s1_interleaving_gpt_validation_v1`  
Pre-registration: `docs/experiments/exect/exect_s1_interleaving_experiment_preregistration_20260520.md`

## Run artifacts

| Arm | Scope | Run ID | Config |
| --- | --- | --- | --- |
| **L1 baseline** *(frozen)* | full (40) | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` | `exect_s0_s1_validation_full_gpt4_1_mini.json` |
| **H1 post bridge** | cap-25 | `exect_s1_interleaving_h1_post_bridge_cap25_gpt4_1_mini_20260520T185424Z` | `exect_s1_interleaving_h1_post_bridge_cap25_gpt4_1_mini.json` |
| **H1 post bridge** | full (40) | `exect_s1_interleaving_h1_post_bridge_gpt4_1_mini_20260520T185747Z` | `exect_s1_interleaving_h1_post_bridge_gpt4_1_mini.json` |
| **H2 pre vocabulary** | cap-25 | `exect_s1_interleaving_h2_pre_vocab_cap25_gpt4_1_mini_20260520T185434Z` | `exect_s1_interleaving_h2_pre_vocab_cap25_gpt4_1_mini.json` |
| **H2 pre vocabulary** | full (40) | `exect_s1_interleaving_h2_pre_vocab_gpt4_1_mini_20260520T185755Z` | `exect_s1_interleaving_h2_pre_vocab_gpt4_1_mini.json` |

Fixed controls: ExECTv2 validation split (40), `exect_s0_s1_field_family`, `exect_field_family_deterministic_v1`, GPT 4.1-mini, prompt `exect_s0_s1_field_family_v4_10_label_policy`.

## Headline metrics

| Arm | Scope | Micro F1 | Diagnosis | Seizure | Medication | Evidence support |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| L1 baseline | full | **92.3%** | 93.8% | 90.5% | 92.8% | ~96% |
| H1 post bridge | cap-25 | 95.8% | 97.6% | 95.4% | 94.9% | 97.3% |
| H1 post bridge | full | **92.3%** | 93.8% | 90.5% | 92.8% | 95.8% |
| H2 pre vocabulary | cap-25 | 90.9% | 95.2% | 87.9% | 91.2% | 93.2% |
| H2 pre vocabulary | full | **87.5%** | 92.7% | 79.2% | 91.5% | 89.5% |

Cap-25 deltas vs frozen L1 cap-25 anchor (`exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T221936Z`, 95.8% micro): H1 **0.0pp**, H2 **−4.9pp**.

Full deltas vs L1: H1 **0.0pp**, H2 **−4.8pp**.

## Decisions (pre-registered criteria)

| Arm | Outcome | Rationale |
| --- | --- | --- |
| **H1** | **Hold (null)** | Full micro F1 identical to L1 on all 40 records (normalized label diff count = 0). No interleaving delta to port to Qwen. |
| **H2** | **Reject** | Full micro −4.8pp vs L1; seizure F1 −11.3pp (79.2% vs 90.5%). Mismatch records 20/40 vs L1 12/40. Evidence support −6.3pp. |
| **H3 tools** | **Defer** | No meaningful positive signal from H1/H2; Gan ReAct negative control remains sufficient unless a revised H1 arm is implemented. |

L1 remains the frozen ExECT S1 GPT default (`outcome: freeze` unchanged).

## H1 — null comparison finding

H1 was intended to test **post-hoc artifact-only benchmark bridges** (`repair_policy=artifact_benchmark_bridge_only`, `bridge_stage=post`) against L1 prompt policy alone.

Record-level replay shows **zero normalized-label differences** between H1 full and the frozen L1 full anchor. Both arms call `_build_s1_field_family_values`, which always applies the audited S1 benchmark bridges after single-pass extraction. The `repair_policy` flag currently changes metadata only (`bridge_stage: post` vs `inline`), not bridge application or scored labels.

**Implication:** this matrix did not isolate interleaving position for deterministic bridges. A valid H1 retry needs an L1 arm that scores **raw model outputs without bridge normalization**, or an H1 path that defers `_build_s1_field_family_values` bridges to a true post-artifact stage.

## H2 — pre-vocabulary regression

Pre-injected candidate lists (`full_note_plus_precomputed_family_candidates`, `exect_s0_s1_field_family_pre_vocab_single_pass`) passed cap-25 schema/evidence gates but **hurt full validation**, especially seizure type.

| Metric | H2 full | L1 full | Delta |
| --- | ---: | ---: | ---: |
| Mismatch records | 20 / 40 | 12 / 40 | +8 |
| Seizure mismatch records | 11 | 6 | +5 |
| Evidence support | 89.5% | ~96% | −6.5pp |

Likely failure mode: injected vocabulary surfaces steer the model toward **over-specific or alternate benchmark phrasing** (ILAE modernization, extra seizure surfaces, candidate-list anchoring) without improving recall on audited gold surfaces. Seizure type is the primary regression family; medication and diagnosis are closer to L1 but still net-negative on micro F1.

Do **not** iterate H2 prompt length or candidate formatting without a narrower family-specific probe (e.g., medication-only pre-vocab slice).

## Cap-25 gate notes

Both arms cleared operational gates (schema-valid predictions, evidence support ≥ 90%):

- H1 cap-25: 97.3% evidence, 100% schema-valid
- H2 cap-25: 93.2% evidence, 100% schema-valid

Cap-25 is systematically optimistic for H1 (matches L1 cap-25 at 95.8%) and masked H2 full-split seizure regression (−8.3pp seizure F1 cap-25 → full).

## Recommended next work

1. **Fix H1 null arm** before any Qwen port: add a bridge-free L1 scorer path or split bridge application so post-only is measurable.
2. **Build ExECT field-family deterministic support map** (kanban §2) using these results plus frozen S1–S4 ladder anchors.
3. **Skip H3** unless a revised interleaving arm shows ≥ 2pp full-validation gain.
4. **Do not** promote H2 or rerun pre-vocab variants on full validation.
