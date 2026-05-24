# Paper Frozen Arm-Reject Table

Date: 2026-05-24  
Status: Frozen negative-result table for manuscript supplementary evidence  
Decision scope: Paper table freeze; documents **arm-level** rejections only (`decision_scope: arm`)

## Purpose

This table consolidates rejected experimental arms that inform the paper's hybrid-pipeline argument. Each row names a single varied factor against a frozen comparison baseline, cites a primary run artifact, and records why the arm failed its preregistered or diagnostic gate.

**Legend**

- `decision_scope: arm` — this configuration is rejected as tested; the underlying mechanism class may remain open.
- Cap-25 rows are search/diagnostic gates unless a full-validation run is explicitly noted.
- Do not treat arm rejection as mechanism closure unless a separate inspection doc says so.

**Companion docs:** [paper_frozen_operational_defaults_20260524.md](paper_frozen_operational_defaults_20260524.md) (D1), [paper_frozen_results_narrative_20260524.md](paper_frozen_results_narrative_20260524.md) (D3)

---

## Tier 1 — 2026-05-24 Pathway Closures (Highest Paper Priority)

Recent arms from Pathways A and C with fresh inspection docs and explicit gates.

| Arm | Dataset | Comparison group | Varied factor | Baseline / control | Headline metric | Result | Reject reason | Run ID | decision_scope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ExECT S5 temporal medication guard (A4) | ExECTv2 | `exect_s5_axis1_axis2_decomposition_gpt_cap25_v1` | `implementation_variant` (post guard) | AM guard + freq verifier cap-25 | annotated_medication recall | 79.3% (−20.7pp) | Precision hit 100% but recall collapsed beyond 3.0pp gate; planned/previous leakage repair too aggressive for benchmark-facing gold | `exect_s5_frequency_pre_vocab_am_guard_temporal_frequency_verify_cap25_gpt4_1_mini_20260524T203942Z` | arm |
| ExECT S5 high-precision frequency candidates | ExECTv2 | `exect_s5_frequency_candidate_precision_vs_recall_v1` | `candidate_density` | High-recall pre-vocab cap-25 | seizure_frequency F1 | 56.3% (−4.2pp vs high-recall) | Narrowing candidates dropped qualitative gold recall (−12.0pp) without precision gain | `exect_s5_frequency_pre_vocab_high_precision_cap25_gpt4_1_mini_20260524T141503Z` | arm |
| Gan unknown-overuse guard v1.5 (C2) | Gan 2026 | Pathway C residual repair | `prompt_policy` | builder-gap v1 operational default | monthly accuracy (cap-25) | 16.0% | Rule 1 over-extraction + Rule 4 inert on no-candidate records | `gan_s0_unknown_overuse_guard_cap25_gpt4_1_mini_20260524T201746Z` | arm |
| Gan GEPA G1 adjudicator | Gan 2026 | `gan_s0_multistage_gepa_gpt_validation_v1` | `optimizer` | G0 cap-25 control | monthly accuracy | 60.0% (−16.0pp vs G0) | Long optimized instructions regressed monthly and category accuracy | `gan_s0_multistage_gepa_g1_adjudicator_cap25_gpt4_1_mini_20260524T131719Z` | arm |
| Gan GEPA G2 verify-repair | Gan 2026 | `gan_s0_multistage_gepa_gpt_validation_v1` | `optimizer` | G0 cap-25 control | monthly accuracy | 48.0% (−28.0pp vs G0) | Verify-repair GEPA variant regressed further; high token cost | `gan_s0_multistage_gepa_g2_verify_repair_cap25_gpt4_1_mini_20260524T131744Z` | arm |

Primary sources: [exect_s5_medication_temporal_guard_walkthrough_20260524.md](../exect/exect_s5_medication_temporal_guard_walkthrough_20260524.md), [exect_s5_frequency_pre_vocab_high_precision_cap25_gpt4_1_mini_inspection_20260524.md](../exect/exect_s5_frequency_pre_vocab_high_precision_cap25_gpt4_1_mini_inspection_20260524.md), [gan_s0_pathway_c_completion_walkthrough_20260524.md](../gan/gan_s0_pathway_c_completion_walkthrough_20260524.md), [gan_s0_multistage_gepa_gpt_cap25_v1_inspection_20260524.md](../gan/gan_s0_multistage_gepa_gpt_cap25_v1_inspection_20260524.md).

---

## Tier 2 — ExECT S5 Frequency and Medication Arms

| Arm | Dataset | Comparison group | Varied factor | Baseline / control | Headline metric | Result | Reject reason | Run ID | decision_scope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ExECT S5 frequency verifier (initial A2, buggy) | ExECTv2 | `exect_s5_axis1_axis2_decomposition_gpt_cap25_v1` | `verification_strategy` | AM guard cap-25 | seizure_frequency recall | 72.0% (−20.0pp) | Verifier too aggressive; case-sensitivity and medication-control bugs (repaired in A2R) | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini_20260524T193119Z` | arm |
| ExECT S5 frequency verifier (repaired A2R, cap-25) | ExECTv2 | same | `verification_strategy` | AM guard cap-25 | seizure_frequency recall | 76.0% (−16.0pp) | F1 improved (+11.2pp) but recall gate (>3.0pp loss) not cleared; led to A3 prompt policy | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini_20260524T194925Z` | arm |
| ExECT S4 medication-temporality H1 post-classifier | ExECTv2 | S4 temporality probe | `post_classifier` | S4 baseline full validation | medication_temporality F1 | 55.9% (−6.6pp) | Precision +10.1pp but recall collapsed to 55.3% | `exect_s4_temporality_h1_post_classifier_full_gpt4_1_mini_20260520T204216Z` | arm |
| ExECT S1 verify-repair second stage | ExECTv2 | S1 decomposition grid | `stage_graph` | S1 cap-25 baseline | micro F1 | −9.4pp | Second-pass verify-repair regressed vs single-pass + bridges | `exect_s1_verification_verify_repair_cap25` (registry) | arm |

Primary sources: [exect_s5_frequency_verifier_cap25_inspection_20260524.md](../exect/exect_s5_frequency_verifier_a2r_regression_review_20260524.md), [exect_s4_temporality_deterministic_gpt_inspection_20260520.md](../exect/exect_s4_temporality_deterministic_gpt_inspection_20260520.md), [exect_negative_probe_synthesis_20260520.md](../exect/exect_negative_probe_synthesis_20260520.md).

---

## Tier 3 — Gan S0 Mechanism Search Arms

Arms that tested alternate Gan S0 surfaces before or alongside builder-gap v1 promotion. All remain `decision_scope: arm`.

| Arm | Dataset | Comparison group | Varied factor | Baseline / control | Headline metric | Result | Reject reason | Run ID | decision_scope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Gan candidate-constrained verifier (G7) | Gan 2026 | enriched slice | `verification_strategy` | v1.4 slice control | monthly accuracy | 36.0% (tied) | Second LLM pass added cost without lift | registry: `gan_s0_candidate_constrained_verifier_gpt_slice_v1` | arm |
| Gan targeted examples min7 | Gan 2026 | enriched slice | `prompt_examples` | v1.4 slice control | monthly accuracy | 36.0% (tied) | Mixed rescues/regressions; no net promotion signal | registry: `gan_s0_targeted_examples_min7_gpt_slice_v1` | arm |
| Gan seeded answer options (G6b) | Gan 2026 | enriched slice | `answer_options` | v1.4 slice control | monthly accuracy | 16.0% | 14/25 fallback `unknown`; LLM option selection errors | registry: `gan_s0_seeded_answer_options_gpt_slice_v1` | arm |
| Gan evidence span-check (V7) | Gan 2026 | validation ladder cap-25 | `evidence_policy` | g2 adjudicate skeleton | monthly accuracy | cap-25 fail | 9/25 abstentions; recall collapse | `docs/experiments/gan/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md` | arm |
| Gan Qwen ReAct temporal tools | Gan 2026 | hard slice | `tool_during` | baseline slice | monthly accuracy | 42.9% (14-record slice) | Tool-during interface underperformed on hard slice | `gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails_20260520T173943Z` | arm |
| Gan historical direct GEPA | Gan 2026 | historical | `optimizer` | pre-GEPA baseline | monthly accuracy | below operational surfaces | Superseded by multistage GEPA workstream; class arm-rejected historically | hybrid mechanism status | arm |

Primary sources: [hybrid_pipeline_mechanism_status_20260521.md](../../workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md), [paper_result_table_pack_20260524.md](paper_result_table_pack_20260524.md) Table 5.

---

## Tier 4 — ExECT S1/S4 Negative Probes (Historical)

Consolidated from the ExECT negative-probe synthesis. These arms should not be rerun without new preregistration.

| Arm | Dataset | Comparison group | Varied factor | Scope | Headline metric | Result | Reject reason | decision_scope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1 section/family split | ExECTv2 | S1 decomposition | `stage_graph` | cap-25 | micro F1 | 65.6% | Family splitting regressed vs monolithic + bridges | arm |
| S1 BootstrapFewShot optimizer | ExECTv2 | S1 optimizer ladder | `optimizer` | cap-25 | micro F1 | 90.7% vs 95.8% baseline | Optimizer did not beat frozen manual policy | arm |
| S1 medication H2 pre-vocab | ExECTv2 | S1 interleaving | `pre_vocabulary` | 14-record Rx slice | medication F1 | 95.1% (−3.2pp) | Static candidate list regressed on enriched slice | arm |
| S1 seizure H2 pre-vocab | ExECTv2 | S1 interleaving | `pre_vocabulary` | 15-record seizure slice | seizure_type F1 | 83.3% (−8.2pp) | Static lists worsened evidence alignment | arm |
| S4 seizure-frequency H2 pre-candidates | ExECTv2 | S4 frequency probe | `pre_candidates` | cap-25 | seizure_frequency F1 | 47.1% (−2.0pp) | Primary family regressed; pooled micro gains not promotable | arm |
| S1 interleaving Qwen port | ExECTv2 | S1 interleaving | `model_transfer` | full validation | micro F1 | 79.0% (seizure 55.7%) | Same bridge path did not close GPT seizure-type gap | arm |
| S1 prompt v4_11 | ExECTv2 | S1 prompt sweep | `prompt_policy` | cap-25 | seizure_type F1 | −1.5pp | Minor regression on cap-25 | arm |
| S1 evidence soft policy | ExECTv2 | S1 evidence sweep | `evidence_policy` | cap-25 | micro F1 | fail gate | Soft evidence policy regressed cap-25 | arm |

Primary source: [exect_negative_probe_synthesis_20260520.md](../exect/exect_negative_probe_synthesis_20260520.md).

---

## Holds and Non-Reject Outcomes (Not Arm-Reject Rows)

These outcomes inform the narrative but are **not** arm rejects:

| Item | Outcome | Notes |
| --- | --- | --- |
| ExECT S5 paper-frozen stack (verifier + A3) | **Promoted to D1** | 72.3% seizure_frequency F1, 85.5% micro F1 — run `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_full_gpt4_1_mini_20260524T195813Z`; see promotion review |
| ExECT S5 AM guard (non-ASM brand alias) | **Component of D1 stack** | 88.7% medication F1 retained in promoted run |
| ExECT S4 MT guard G0G2 dose-current | **Pass arm gates; mechanism open** | Best tested MT precision arm; not full S4 solution |
| Gan G0 multistage GEPA control | **Hold** | Matched cap-25 control only; not operational default |

---

## Manuscript Usage Rules

1. Cite **Tier 1** rows when arguing recent methodological control (Pathways A/C closures).
2. Use **Tier 2–4** rows as supplementary negative evidence; group by mechanism axis (decomposition, deterministic placement, implementation variant) rather than chronology.
3. Always pair reject claims with `decision_scope: arm` and the comparison baseline named in the row.
4. Do not claim mechanism closure from this table alone; see [hybrid_pipeline_mechanism_status_20260521.md](../../workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md) for open classes.
5. Cap-25 rejections require explicit scope wording in manuscript text.

## Verification Notes

Headline metrics for Tier 1 and Tier 2 ExECT rows were checked against local `runs/<run_id>/metrics.json` where present (2026-05-24). Gan C2 and GEPA rows checked against cap-25 inspection docs and run artifacts. Tier 3 registry rows verified against `docs/experiments/synthesis/experiment_registry.json` notes fields.
