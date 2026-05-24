# Gan S0 Multi-Stage GEPA GPT Cap-25 v1 Inspection

Date: 2026-05-24
Status: Completed; G1/G2 rejected as cap-25 arms
Preregistration/workstream: `docs/workstreams/optimizer/gan_s0_multistage_gepa_workstream_20260524.md`
Comparison group: `gan_s0_multistage_gepa_gpt_validation_v1`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Split | `gan_2026_fixed_v1:validation`, cap-25 |
| Schema complexity | `gan_frequency_s0` |
| Clinical task family | frequency |
| Model/provider | GPT 4.1-mini |
| Scorer mode | `gan_frequency_deterministic_v1` |
| Research axis | Axis 3 implementation / optimizer strategy over fixed stage graphs |
| Comparison group | `gan_s0_multistage_gepa_gpt_validation_v1` |
| decision_scope | `arm` |

Gan gold remains `seizure_frequency_number[0]`; `reference` remains diagnostic only. The GEPA metric `gan_s0_stage_attributed_frequency_feedback` is optimizer-facing only and does not replace benchmark-facing deterministic scoring.

## Runs

| Arm | Config | Run ID | Monthly | Purist | Pragmatic | Normalized label | Schema | Evidence | Decision |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| G0 | `gan_s0_multistage_gepa_g0_control_cap25_gpt4_1_mini.json` | `gan_s0_multistage_gepa_g0_control_cap25_gpt4_1_mini_20260524T131431Z` | 76.0% | 84.0% | 96.0% | 64.0% | 100.0% | 100.0% | hold as matched cap control |
| G1 | `gan_s0_multistage_gepa_g1_adjudicator_cap25_gpt4_1_mini.json` | `gan_s0_multistage_gepa_g1_adjudicator_cap25_gpt4_1_mini_20260524T131719Z` | 60.0% | 80.0% | 88.0% | 48.0% | 100.0% | 100.0% | reject arm |
| G2 | `gan_s0_multistage_gepa_g2_verify_repair_cap25_gpt4_1_mini.json` | `gan_s0_multistage_gepa_g2_verify_repair_cap25_gpt4_1_mini_20260524T131744Z` | 48.0% | 68.0% | 76.0% | 40.0% | 100.0% | 100.0% | reject arm |

An earlier G1 run, `gan_s0_multistage_gepa_g1_adjudicator_cap25_gpt4_1_mini_20260524T131442Z`, exposed a feedback-metric contract bug (`GanTemporalFrequencyCandidate.label` instead of `canonical_label`) and should be treated as a bug-finding artifact, not a decision artifact. The clean G1 run above was produced after the fix and regression test.

## Gate Check

The preregistered cap gate required a GEPA arm to beat the matched cap/control arm by at least 4 percentage points in monthly accuracy or reduce severe residual errors without increasing invalid/evidence errors.

| Arm | Monthly vs G0 | Schema/evidence | Prompt-length caveat | Gate outcome |
| --- | ---: | --- | --- | --- |
| G1 | -16.0pp | 100% / 100% | selected adjudicator instruction 4,829 chars / 766 words | fail |
| G2 | -28.0pp | 100% / 100% | selected extractor instruction 4,742 chars / 768 words plus verifier 1,286 chars / 182 words | fail |

Both GEPA arms preserve schema validity and evidence quote support, but both regress benchmark-facing monthly frequency and category accuracy. G2 also consumed substantially more prompt tokens during the run (`340,106` total tokens recorded) and was slower per prediction than G0/G1.

## Artifact Review

Expected artifacts are present for the clean GEPA runs:

- `runs/gan_s0_multistage_gepa_g1_adjudicator_cap25_gpt4_1_mini_20260524T131719Z/artifacts/compiled_state.json`
- `runs/gan_s0_multistage_gepa_g1_adjudicator_cap25_gpt4_1_mini_20260524T131719Z/artifacts/optimizer/summary.json`
- `runs/gan_s0_multistage_gepa_g1_adjudicator_cap25_gpt4_1_mini_20260524T131719Z/artifacts/optimizer/logs/gepa_state.bin`
- `runs/gan_s0_multistage_gepa_g2_verify_repair_cap25_gpt4_1_mini_20260524T131744Z/artifacts/compiled_state.json`
- `runs/gan_s0_multistage_gepa_g2_verify_repair_cap25_gpt4_1_mini_20260524T131744Z/artifacts/optimizer/summary.json`
- `runs/gan_s0_multistage_gepa_g2_verify_repair_cap25_gpt4_1_mini_20260524T131744Z/artifacts/optimizer/logs/gepa_state.bin`

The optimizer summaries preserve the GEPA budget contract: `max_metric_calls=64`, `trainset_size=50`, `reflection_minibatch_size=2`, `candidate_selection_strategy=pareto`, `track_stats=true`, and `track_best_outputs=true`.

## Failure Pattern

G1 increases monthly mismatches from 6/25 in G0 to 10/25. The clean G1 residuals include `unknown` overuse for high-frequency labels (`gan_4702`, `gan_4709`) and wrong denominator/count choices such as `gan_12679`, `gan_15997`, `gan_16772`, and `gan_16825`.

G2 increases monthly mismatches to 13/25 and adds more severe category flips, including cluster/unknown confusion (`gan_10618`), infrequent labels pushed to unknown/frequent (`gan_14881`, `gan_15306`), and repeated high-frequency-to-unknown failures (`gan_4702`, `gan_4709`).

## Decision

Reject G1 and G2 as cap-25 arms. Do not promote either to full validation, and do not treat this as mechanism closure for all possible GEPA use. The result only rejects these two stage-attributed GEPA configurations under this budget, train/dev setup, and selected prompt artifacts.

G0 remains the matched cap control for this comparison group. The operational Gan S0 default remains `gan_s0_candidate_builder_gap_v1` on GPT 4.1-mini from the full-validation inspection, not this cap-25 control.

## Follow-Up

- Preserve the feedback-metric fix because it hardens future GEPA/feedback runs without changing benchmark scorer semantics.
- Do not run G3/G4 until there is a new preregistered reason, likely a smaller valset or targeted submodule-freezing design that avoids long policy-wall instructions.
- If optimizer work continues, inspect whether GEPA can be constrained to compact instruction deltas; otherwise prioritize residual error forensics or non-optimizer implementation variants.
