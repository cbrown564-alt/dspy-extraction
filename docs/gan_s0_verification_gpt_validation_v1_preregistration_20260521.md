# Gan S0 Verification Strategy — Clean GPT Ablation Pre-Registration

Date: 2026-05-21  
Status: **Cap-25 complete — hold (null factor)** — `docs/gan_s0_lane_a_gpt_cap25_inspection_20260521.md`  
Comparison group: `gan_s0_verification_gpt_validation_v1`  
Kanban: `docs/kanban_plan.md` (Lane A, Phase 2)

## Research question

On Gan S0 with **GPT 4.1-mini**, how much of the promoted monthly-frequency performance comes from **verification strategy** (none vs verify-repair vs temporal-candidates preconditioning), holding prompt policy, evidence policy, split, model, and scorer fixed?

This is a **new clean comparison group**. Historical bundled rows (architecture matrix `gan_s0_architecture_gpt_validation_v1`) motivate priors but are **not** the paper-safe evidence base for this factor.

## Hypothesis

Verify-repair and temporal-candidate preconditioning each contribute independently to monthly-frequency accuracy beyond direct single-pass extraction. Temporal-candidates **without** repair may isolate pre-deterministic value if a program variant can be added without changing scorer semantics.

## Fixed controls (all arms)

| Control | Value |
| --- | --- |
| Dataset | `gan_2026` |
| Split | `gan_2026_fixed_v1:validation` |
| Model | GPT 4.1-mini (`configs/models/gan_s0_gpt4_1_mini.json`) |
| Scorer | `gan_frequency_deterministic_v1` |
| Evidence strategy | `model_quote` (signature requires quote; scorer evidence support is diagnostic) |
| Few-shot | `none` |
| Structured output | `provider_json_schema_with_pydantic_validation` |
| `repair_policy` | `artifact_bridge_surface_normalization_only` |
| Prompt (matched per arm) | Guardrails v2.2 on direct arms; temporal v1.1 on temporal arms |

## Varied factor

`verification_strategy`

## Arms

| Arm | `verification_strategy` | `program_variant` | `prompt_version` | Config (planned) |
| --- | --- | --- | --- | --- |
| **Direct** | `none` | `gan_frequency_s0_direct_single_pass` | `gan_frequency_s0_direct_guardrails_v2_2` | `gan_s0_verification_direct_cap25_gpt4_1_mini.json` |
| **Verify-repair** | `verify_repair` | `gan_frequency_s0_direct_verify_repair` | `gan_frequency_s0_direct_verify_repair_v2_4` | `gan_s0_verification_verify_repair_cap25_gpt4_1_mini.json` |
| **Temporal + verify-repair** | `verify_repair` (+ pre candidates) | `gan_frequency_s0_temporal_candidates_verify_repair` | `gan_frequency_s0_temporal_candidates_verify_repair_v1_1` | `gan_s0_verification_temporal_verify_repair_cap25_gpt4_1_mini.json` |
| **Temporal, no repair** | `none` (+ pre candidates) | *(deferred — no registered variant)* | — | — |

### Deferred arm: temporal-candidates without repair — **reopened**

**Status (2026-05-21):** Reassigned to Axis 1 comparison group `gan_s0_pipeline_stage_graph_gpt_cap25_v1` as arm **A3** (`g2_candidates_adjudicate`). See `docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_preregistration_20260521.md`. LLM candidate ID remains deferred to Phase 3 (`gan_s0_stage_executor_gpt_cap25_v1`).

Implementation prerequisites (unchanged):

1. Add `gan_frequency_s0_temporal_candidates_single_pass` variant that injects pre-candidates without a verifier pass.
2. Confirm scorer semantics and artifact-bridge behavior stay unchanged.
3. If not feasible without scorer or bridge changes, **drop A3** and document four-arm comparison only.

## Historical priors (do not treat as clean single-factor evidence)

| Arm | Reference run | Monthly (full/slice) | Notes |
| --- | --- | ---: | --- |
| Direct cap-25 | `…081439Z` | exploratory | Bundled with prompt evolution |
| Verify-repair full | `…084732Z` | 65.4% | Superseded hosted anchor |
| Temporal + VR full | `…130933Z` | 65.1% | **Promoted** default; bundled architecture row |

## Run order

1. Implement cap-25 configs with taxonomy (`varied_factor: verification_strategy`).
2. Dry-run all configs (`--dry-run`).
3. Cap-25 on matched validation records (25).
4. Full validation (299) only for arms passing cap-25 gate.
5. Inspection `docs/gan_s0_verification_gpt_validation_v1_inspection_<date>.md`.
6. Registry rows under `gan_s0_verification_gpt_validation_v1`.

## Primary metric

**Monthly-frequency accuracy** (benchmark-facing).

## Diagnostic metrics

- Purist and Pragmatic category accuracy
- Schema-valid prediction rate
- Evidence quote support rate
- Normalized-label exact match
- Verifier decision counts (confirm / repair / abstain) on verify-repair arms
- Latency per record (verify-repair doubles calls)

## Cap-25 gate

| Outcome | Rule |
| --- | --- |
| **Proceed to full** | Arm monthly ≥ best historical direct cap-25 reference **and** schema ≥ 95% **and** evidence support ≥ 85% |
| **Hold** | Meaningful monthly delta (≥ 3pp vs direct) but fails schema/evidence gate |
| **Reject arm** | Monthly ≤ direct cap-25 **or** schema < 90% |

Full-validation promotion compares within this group only; do not auto-promote over frozen temporal + VR default without beating `…130933Z` on monthly within 1pp **and** evidence ≥ 95%.

## Expected outcomes

- **Direct < verify-repair < temporal + verify-repair** on monthly (prior from bundled history).
- Temporal-no-repair, if implemented, expected between direct and temporal + VR.

## Artifacts checklist

- [x] Cap-25 configs (3 arms; temporal-no-repair deferred)
- [ ] Full-validation configs for passing arms
- [ ] Inspection doc with per-arm metrics and error clusters
- [ ] Registry rows with `comparison_group: gan_s0_verification_gpt_validation_v1`
- [ ] Regenerate `docs/experiment_registry_matrix_20260520.md` and `docs/research_atlas/evidence_matrix.md`
