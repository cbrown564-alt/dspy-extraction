# Gan S0 Candidate Builder Gap V1 GPT Full-Validation Reconciliation

Date: 2026-05-23  
Status: Reconciled / rerun required  
Related: `docs/planning/kanban_plan.md`, `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md`, `docs/experiments/gan/gan_s0_g16_candidate_builder_gap_incident_report.md`

## Decision

The G16 artifact `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z` should **not** be promoted as the full-validation result for `gan_s0_candidate_builder_gap_v1`.

It is also not a clean mechanism rejection. The run has favorable aggregate metrics versus the operational F0 anchor, but primary artifacts show that the enriched-slice candidate-builder surface did not replay inside the full-validation run. The correct next action is a rerun after verifying deterministic builder parity on the accepted code state.

| Scope | Decision |
| --- | --- |
| Operational default | Blocked; keep Gan S0 F0 expanded builders + prose as default |
| Arm | Open; G16 artifact is stale-check evidence, not a valid promotion artifact |
| Mechanism | Open; candidate-builder gap remains plausible but needs a trustworthy full-validation replay |
| Qwen transfer | Blocked until a verified GPT full-validation run clears the gate |
| Registry / paper evidence | Do not register as a promoted full-validation result or cite for paper claims |

## Run Facts

| Field | Value |
| --- | --- |
| Dataset / split | Gan 2026 synthetic, `gan_2026_fixed_v1:validation` |
| Records | 299/299 validation records scored |
| Model / provider | GPT 4.1-mini / OpenAI |
| Program | `gan_frequency_s0_temporal_candidates_single_pass` |
| Prompt | `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy` |
| Implementation variant | `gan_s0_candidate_builder_gap_v1` |
| Scorer | `gan_frequency_deterministic_v1` |
| Structured output | provider JSON schema with Pydantic validation |

Primary metrics from `metrics.json`:

| Metric | Result |
| --- | ---: |
| Monthly-frequency accuracy | 75.9% (227/299) |
| Purist category accuracy | 81.3% (243/299) |
| Pragmatic category accuracy | 85.6% (256/299) |
| Normalized-label exact accuracy | 67.2% (201/299) |
| Schema-valid prediction rate | 100.0% |
| Evidence quote support rate | 100.0% |

Runtime: 323.3 seconds total, 299 estimated model calls, 1,080,725 prompt tokens and 12,820 completion tokens.

## Reconciliation Findings

The aggregate monthly result beats the documented F0 GPT full-validation anchor (75.9% vs 68.1%), but that comparison is confounded because F0 used a different prompt/presentation surface. The G16 run cannot isolate the builder-gap implementation effect.

The enriched 25-record slice that justified G16 did not replay:

| Check | G15 slice run | Same 25 IDs inside G16 full run |
| --- | ---: | ---: |
| Monthly accuracy | 92.0% (23/25) | 32.0% (8/25) |
| Purist accuracy | 92.0% (23/25) | 44.0% (11/25) |
| Pragmatic accuracy | 96.0% (24/25) | 48.0% (12/25) |
| Normalized-label exact | 84.0% (21/25) | 32.0% (8/25) |
| Gold label in emitted candidates | 23/25 no-model expectation | 5/25 in G16 predictions |
| Empty candidate lists | not observed as the mechanism signal | 19/25 |

Full-split candidate emission also looks inconsistent with the intended candidate-builder expansion:

| Diagnostic | Count |
| --- | ---: |
| Records with at least one emitted temporal candidate | 42/299 |
| Records with empty temporal candidates | 257/299 |
| Records where gold label appeared in emitted candidates | 39/299 |

This is consistent with the incident report hypothesis that the implementation-variant presentation mapping was missing or stale at G16 runtime. The current workspace has since recovered the mapping and builders, but the run metadata does not record a git SHA, so current code health cannot retroactively validate the G16 artifact.

## Error Profile

Among the 72 monthly-frequency mismatches in the full run, the leading classes were:

| Failure class | Count |
| --- | ---: |
| `other_semantic_mismatch` | 26 |
| `pragmatic_match_monthly_divergence` | 16 |
| `purist_bin_boundary_within_pragmatic` | 11 |
| `frequent_undercalled` | 6 |
| `cluster_collapsed_to_rate` | 3 |
| `unknown_as_high_rate` | 3 |
| `frequent_overcalled` | 3 |

Gold pragmatic strata among monthly mismatches: frequent 45, infrequent 20, unknown 6, no-seizure-information 1. Four predictions had no evidence span (`gan_11874`, `gan_11411`, `gan_11804`, `gan_11734`); evidence support remained 100% for predictions with spans.

## Current No-Model Validation

Validation run after reconciliation:

```powershell
uv run pytest tests/test_gan_temporal_candidates.py
uv run python scripts/audit_gan_candidate_builder_gap.py
uv run python scripts/validate_primitives.py --errors-only
```

Results:

- `tests/test_gan_temporal_candidates.py`: 49 passed.
- Candidate-builder gap audit: 23/25 gold-in-candidates on the enriched slice.
- Primitive validation: warning-only output; no blocking errors.

These checks show that current code is ready for a verified rerun, not that the stale G16 artifact is promotion-ready.

## Next Action

Before spending on another model run:

1. Preserve the recovered candidate-builder code state so a rerun can be tied to an explicit commit or stash.
2. Run the no-model audit and Gan temporal-candidate tests immediately before launch.
3. Rerun `configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation.json`.
4. In the rerun inspection, require non-empty candidate emission on the enriched 25 IDs and report gold-in-candidates coverage for both the enriched slice and full split.
5. Only after a verified rerun should the project consider registry promotion, paper-facing claims, or Qwen transfer.

Scorer semantics are unchanged: primary gold remains `seizure_frequency_number[0]`; `reference[0]` remains a secondary difficulty signal; normalized-label exact remains diagnostic.
