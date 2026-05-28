# Manuscript Claims And Caveats

Date: 2026-05-25  
Status: draft paper-facing claims/caveats section  
Decision scope: narrative synthesis; no scorer, loader, registry, or model-output changes

## Supported Claims

1. The current Gan S0 operational surface is GPT 4.1-mini candidate-builder gap v1 on synthetic validation: `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` reached 80.6% monthly accuracy with 100.0% schema validity and evidence quote support.
2. Qwen3.6:35b transfers the Gan builder-gap surface but does not close the hosted-model gap: `gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z` reached 70.7% monthly accuracy, with GPT ahead by 9.9pp.
3. Gan L2 forensics indicate the Qwen gap is concentrated in calibration and canonical-label selection under sparse deterministic candidate coverage, not in a scorer or loader defect.
4. The Qwen exact-policy cap-25 gate is promising but not yet a full-validation replacement: `gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama_20260525T162702Z` reached 69.6% monthly accuracy on cap-25, beating its 40.0% baseline parent and a 52.0% GPT E1 reference.
5. The ExECT Qwen clean ladder is now coherent after the S1 clean v2 correction: S1 85.9%, S2 84.4%, S3 75.3%, S4 67.5% micro F1 on fixed validation.
6. ExECT S5 v2b supports accepted local transfer on synthetic validation: Qwen true-v2b reached 85.4% micro F1 against GPT 4.1-mini at 85.8%, while trailing GPT on seizure-frequency F1 (71.4% vs 73.9%).
7. A2's GPT 5.5 S5 v2b anchor does not improve the overall S5 headline: `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt5_5_openai_20260526T130247Z` reached 82.6% micro F1, below GPT 4.1-mini and Qwen, despite slightly higher seizure-frequency F1 at 74.5%.
8. Several tempting mechanism arms are rejected as tested, including ExECT S5 per-family parallel decomposition, stacked strict frequency verification, high-precision frequency-candidate pruning, medication temporal guarding inside the S5 core surface, Gan unknown-overuse prompting, and Gan GEPA G1/G2.

## Plausible But Not Yet Headline Claims

1. Local Qwen may be good enough for selected synthetic ExECT surfaces when the schema and deterministic guards are carefully matched to the task. This is plausible from S2-S5 local results, but the claim needs careful per-family framing because S1 seizure-type and S5 frequency recall remain weaker than GPT.
2. Gan exact-frequency policy prompting may close part of the Qwen builder-gap deficit. The cap-25 result supports promotion, but the manuscript should wait for the 299-record full validation before treating it as an operational improvement.
3. Deterministic structure is most helpful when it supplies stable candidate recall or benchmark-policy normalization, not when it aggressively prunes ambiguous clinical facts. This is consistent with high-recall frequency candidates and rejected high-precision/temporal-pruning arms, but it remains a cross-experiment interpretation rather than a single controlled theorem.

## Risky Or Unsupported Claims To Avoid

| Claim | Why it is risky | Safer wording |
| --- | --- | --- |
| The system beats published ExECTv2 or Gan benchmarks. | Current evidence is fixed synthetic validation with project scorers; ExECT Table 1 reproduction and Gan Real reporting are blocked. | "The system improves internal synthetic-validation surfaces under fixed project scorers." |
| Qwen is better than GPT overall. | Qwen matches or exceeds some pooled metrics but trails on Gan monthly accuracy and several family-specific recalls. | "Qwen reaches near-parity on ExECT S5 v2b and remains weaker on Gan S0 monthly accuracy." |
| A stronger closed model automatically raises the S5 ceiling. | GPT 5.5 trailed both GPT 4.1-mini and Qwen on S5 v2b pooled micro F1 under fixed controls. | "GPT 5.5 did not improve the fixed S5 v2b overall headline, although it slightly improved seizure-frequency F1." |
| Rejected arms prove decomposition, GEPA, or verification do not work. | Rejections are arm-level decisions under specific gates and configs. | "These arms did not improve the current surfaces as tested." |
| Evidence support proves clinical correctness. | Evidence metrics are deterministic quote/source diagnostics, not clinician adjudication. | "Evidence quote grounding was high under deterministic checks." |
| The clean ladder proves schema complexity alone drives performance. | Field-family scope, guard availability, and family support vary by rung. | "The ladder is consistent with schema-breadth pressure, with family-composition caveats." |

## Suggested Manuscript Caveats

The experiments are best framed as controlled synthetic-validation studies of hybrid extraction design, not clinical deployment validation. Both datasets are clinically motivated, but the reported rows use fixed project validation splits and deterministic project scorers. Published benchmark reproduction remains gated: ExECTv2 requires a CUI-aware scorer path, and Gan Real(300)/Real(150) reporting requires access and protocol approval.

The local-model story should be stated as conditional transfer. Qwen3.6:35b can approach GPT 4.1-mini on the promoted ExECT S5 v2b surface and can form a coherent S1-S4 ladder after policy correction, but its Gan S0 monthly accuracy still trails GPT under the current full-validation default. The strongest local-model claim is therefore not "local wins"; it is that local performance can be competitive on some structured extraction surfaces while exposing task-specific calibration failures that need targeted policies.

Negative results should strengthen the methods narrative without overclosing mechanisms. The rejected arms show that more stages, stricter filters, and optimizer-generated prompts can regress fixed-scorer performance when they disturb benchmark-label recall or canonical-label selection. They do not prove those mechanism classes are useless; they define what should not be reused without a new preregistered decision question.

## Traceability

| Evidence area | Primary artifacts |
| --- | --- |
| Current table pack | `docs/experiments/synthesis/paper_result_table_pack_20260525.md` |
| Gan operational defaults | `docs/archive/experiments/synthesis/pre_component_pivot/paper_frozen_operational_defaults_20260524.md`; `docs/experiments/gan/gan_s0_operational_default_promotion_review_20260523.md` |
| Gan L2 forensics | `docs/experiments/gan/gan_s0_qwen35b_builder_gap_l2_error_forensics_20260525.md` |
| Gan exact-policy cap-25 | `docs/experiments/gan/gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama_inspection_20260525.md` |
| ExECT clean ladder | `docs/experiments/exect/exect_s1_clean_ladder_qwen_validation_v1_inspection_20260525.md`; `docs/experiments/exect/exect_s2_s3_clean_ladder_gpt_validation_v1_inspection_20260525.md` |
| ExECT S5 local transfer | `docs/experiments/synthesis/l1_2_s5_local_vs_closed_comparison_20260525.md` |
| ExECT S5 GPT 5.5 A2 anchor | `docs/experiments/exect/exect_s5_best_closed_gpt5_5_anchor_inspection_20260526.md` |
| Rejected arms | `docs/archive/experiments/synthesis/pre_component_pivot/paper_frozen_arm_reject_table_20260524.md` |

## Next Revision Loop

1. Run the Gan exact-policy full validation before replacing the Qwen Gan operational row.
2. Use the completed A2 S5 GPT 5.5 anchor as negative evidence against a stronger-closed-overall S5 claim; do not tune from this validation result.
3. Keep the manuscript table captions explicit about split, scorer, model/provider, schema level, and whether a row is full validation or cap-25.
