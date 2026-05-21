# Gan S0 Evidence Policy — Clean GPT Ablation Pre-Registration

Date: 2026-05-21  
Status: **Cap-25 complete — reject optional & span-check** — `docs/gan_s0_lane_a_gpt_cap25_inspection_20260521.md`  
Comparison group: `gan_s0_evidence_policy_gpt_validation_v1`  
Kanban: `docs/kanban_plan.md` (Lane A, Phase 2)

## Research question

On Gan S0 with **GPT 4.1-mini**, does **evidence strategy** (optional quote vs required model quote vs stricter span-checked quote) change monthly-frequency accuracy or only evidence diagnostics, when architecture, prompt, split, model, and scorer are fixed?

## Hypothesis

Stricter evidence requirements improve evidence support diagnostics and may reduce unsupported-quote repairs without materially changing benchmark-facing monthly accuracy on the promoted temporal-candidates verify-repair path.

## Fixed controls (all arms)

| Control | Value |
| --- | --- |
| Dataset | `gan_2026` |
| Split | `gan_2026_fixed_v1:validation` |
| Model | GPT 4.1-mini |
| Scorer | `gan_frequency_deterministic_v1` (unchanged) |
| Architecture | `gan_frequency_s0_temporal_candidates_verify_repair` |
| Prompt | `gan_frequency_s0_temporal_candidates_verify_repair_v1_1` |
| Verification | `verify_repair` with candidate-gated guards |
| `context_policy` | `full_note_plus_deterministic_temporal_candidates` |
| Few-shot | `none` |

## Varied factor

`evidence_strategy`

## Arms

| Arm | `evidence_strategy` | Description | Config (planned) |
| --- | --- | --- | --- |
| **Optional quote** | `absent` | Prompt/signature allows null evidence; scorer evidence support remains diagnostic | `gan_s0_evidence_optional_cap25_gpt4_1_mini.json` |
| **Model quote required** | `model_quote` | Current promoted default — exact contiguous quote required in signature and verifier | `gan_s0_evidence_model_quote_cap25_gpt4_1_mini.json` |
| **Span-checked quote** | `model_quote_with_diagnostic_span_check` | Required quote plus deterministic post-check / verifier guard on unsupported spans | `gan_s0_evidence_span_check_cap25_gpt4_1_mini.json` |

### Implementation prerequisites

1. **Optional quote arm:** relax extractor/verifier prompt language to permit abstention on evidence while keeping label policy identical; confirm JSON schema still validates.
2. **Span-check arm:** reuse `_evidence_policy_feedback` / artifact-bridge span discipline without changing `gan_frequency_deterministic_v1` label scoring.
3. Confirm evidence changes do **not** silently alter monthly-frequency label normalization (evidence is diagnostic unless a decision doc says otherwise).

## Frozen baseline reference

Promoted temporal + VR full run `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z` — 65.1% monthly, **100%** evidence support. The **model quote required** arm should reproduce this band on cap-25 before interpreting other arms.

## Run order

1. Implement prompt/control variants per arm (minimal diffs in `gan_frequency_s0.py` or config-only if sufficient).
2. Dry-run cap-25 configs.
3. Cap-25 all three arms on matched records.
4. Full validation only if an arm beats baseline monthly within 1pp **and** improves evidence support ≥ 3pp vs optional-quote arm.
5. Inspection `docs/gan_s0_evidence_policy_gpt_validation_v1_inspection_<date>.md`.
6. Registry rows.

## Primary metrics

- **Monthly-frequency accuracy** (benchmark-facing — must not regress > 2pp vs model-quote arm on cap-25)
- **Evidence quote support rate** (headline for this group)

## Diagnostic metrics

- Purist / Pragmatic category accuracy
- Schema-valid rate
- Unsupported-quote count from verifier metadata
- Repair rate attributable to evidence failures

## Cap-25 gate

| Outcome | Rule |
| --- | --- |
| **Promote evidence policy** | Evidence support ≥ +5pp vs optional-quote **and** monthly within −1pp of model-quote arm |
| **Hold** | Evidence gain with monthly −1pp to −2pp |
| **Reject** | Monthly regression > 2pp vs model-quote **or** no evidence diagnostic improvement |

## Interpretation guardrails

- Do not treat evidence support alone as a benchmark-facing metric unless this inspection explicitly promotes an evidence policy.
- Do not compare to published Gan benchmark claims; fixed synthetic validation only.

## Artifacts checklist

- [x] Three cap-25 configs with taxonomy `varied_factor: evidence_strategy`
- [x] Optional program/prompt diffs in `gan_frequency_s0.py` (optional + span-check prompt versions)
- [ ] Inspection doc
- [ ] Registry rows under `gan_s0_evidence_policy_gpt_validation_v1`
