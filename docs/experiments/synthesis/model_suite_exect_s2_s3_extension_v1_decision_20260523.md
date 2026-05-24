# Model Suite ExECT S2/S3 Extension v1 Decision

Date: 2026-05-23  
Status: Do not run  
Decision scope: arm planning decision  
Related: `docs/experiments/synthesis/model_suite_pattern_interpretation_20260522.md`, `docs/experiments/synthesis/model_suite_qwen27b_full_validation_v1_inspection_20260523.md`, `docs/experiments/synthesis/model_suite_frozen_architecture_v1_preregistration_20260522.md`

## Decision

Do not launch `model_suite_exect_s2_s3_extension_v1` now.

The completed frozen suite already covers the three planned surfaces: ExECT S1, ExECT S4, and Gan S0 F0. Those surfaces are enough for the current model-profile claim because they span narrow benchmark-policy alignment, broad multi-family extraction, and Gan temporal candidate adjudication.

## Rationale

The paper need is not strong enough to justify more S2/S3 model runs:

- The model-suite synthesis is explicitly framed as model-profile evidence, not an operational leaderboard.
- S1 and S4 already bracket the ExECT schema-width question more cleanly than adding middle ladder rows.
- The preregistration excluded S2/S3 unless the paper needed hosted validation of a mid-ladder Qwen-vs-GPT claim.
- Current paper-facing caution is that pooled micro across schema levels can mislead without per-family reporting; adding S2/S3 rows risks making that harder to explain rather than clearer.
- The higher-value active work is Gan builder-gap validation and follow-through.

## If Reopened

Reopen only if a manuscript section makes a specific middle-ladder claim that cannot be supported by existing GPT S2/S3 frozen runs plus S1/S4 model-suite profiles. A reopened extension should preregister:

- exact S2/S3 model tracks;
- whether hosted-only or hosted-plus-local;
- per-family reporting requirements;
- cost/latency ceiling;
- how the result will change a paper claim.

Until then, the model suite remains frozen at S1/S4/Gan F0.
