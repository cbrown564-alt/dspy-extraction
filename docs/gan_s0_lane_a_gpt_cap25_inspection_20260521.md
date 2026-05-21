# Gan S0 Lane A — Clean GPT Cap-25 Inspection (2026-05-21)

Preregistrations: verification `docs/gan_s0_verification_gpt_validation_v1_preregistration_20260521.md`, evidence `docs/gan_s0_evidence_policy_gpt_validation_v1_preregistration_20260521.md`, prompt policy `docs/gan_s0_prompt_policy_gpt_validation_v1_preregistration_20260521.md`.

All arms: GPT 4.1-mini, `gan_2026_fixed_v1:validation`, cap-25 (same record order ending `gan_16825`), scorer `gan_frequency_deterministic_v1`.

## Summary verdicts

| Comparison group | Cap-25 outcome | Recommendation |
| --- | --- | --- |
| `gan_s0_verification_gpt_validation_v1` | **Null on monthly** (44% all arms) | **Hold** — do not spend full-validation budget on this trio |
| `gan_s0_evidence_policy_gpt_validation_v1` | Span-check confounded; optional regresses | **Reject** span-check & optional; **hold** model-quote reference only |
| `gan_s0_prompt_policy_gpt_validation_v1` | Guardrails port +4pp | **Hold** guardrails port for error-read; **reject** synthesis port |

Frozen default unchanged: temporal-candidates verify-repair v1.1 (`…130933Z` full validation).

---

## 1. Verification strategy

| Arm | Run ID | Monthly | Purist | Pragmatic | Schema | Evidence | Valid |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct | `gan_s0_verification_direct_cap25_gpt4_1_mini_20260520T233555Z` | 44.0% | 64.0% | 72.0% | 100% | 100% | 25 |
| Verify-repair | `gan_s0_verification_verify_repair_cap25_gpt4_1_mini_20260520T233559Z` | 44.0% | 56.0% | 68.0% | 100% | 100% | 25 |
| Temporal + VR | `gan_s0_verification_temporal_verify_repair_cap25_gpt4_1_mini_20260520T233701Z` | 44.0% | 64.0% | 72.0% | 100% | 100% | 25 |

### Prediction overlap

- **Direct ≡ temporal + VR** on all 25 `raw_value` labels (byte-identical outputs).
- **Verify-repair** differs on **8** records (`gan_14485`, `gan_15306`, `gan_7894`, `gan_14881`, `gan_9566`, …) but **monthly accuracy is unchanged** — repairs move canonical labels without changing the benchmark-facing monthly scalar on this slice.

### Gate (prereg)

| Criterion | Result |
| --- | --- |
| Monthly ≥ historical direct cap-25 (~34.8% at `…081439Z`) | **Pass** (44%) |
| Schema ≥ 95% | **Pass** |
| Evidence ≥ 85% | **Pass** |
| Meaningful factor separation (≥ 3pp) | **Fail** — null |

### Interpretation

Clean factor-isolation shows **no verification-strategy lift on monthly frequency** at cap-25, despite passing individual proceed thresholds. Temporal preconditioning did not change labels versus direct on this draw; verify-repair perturbed labels but not monthly matches. Prior full-validation architecture ordering (temporal + VR promoted) is **not contradicted**, but this slice does not add new evidence for spending three full runs.

**Decision: hold** — skip full-validation reruns for the verification trio; keep `gan_s0_architecture_gpt_validation_v1` promoted anchor.

---

## 2. Evidence strategy

Architecture fixed: temporal-candidates verify-repair.

| Arm | Run ID | Monthly (reported) | Schema | Evidence | Valid / Invalid |
| --- | --- | ---: | ---: | ---: | --- |
| Model quote (baseline) | `gan_s0_evidence_model_quote_cap25_gpt4_1_mini_20260520T233707Z` | 44.0% | 100% | 100% | 25 / 0 |
| Optional quote | `gan_s0_evidence_optional_cap25_gpt4_1_mini_20260520T233713Z` | 40.0% | 100% | 100% | 25 / 0 |
| Span-check | `gan_s0_evidence_span_check_cap25_gpt4_1_mini_20260520T233837Z` | **55.6%** | **72%** | 100% | **18 / 7** |

### Span-check confound (critical)

The span-check guard **abstained on 7 records** (`gan_14485`, `gan_12679`, `gan_15997`, `gan_16251`, `gan_16772`, `gan_16825`, `gan_6532`) — same IDs as `schema.missing_value` / `predicted_abstention` in `errors.json`. Reported **55.6% monthly is on 18 valid predictions only**, not comparable to 25/25 arms.

Evidence support stays **100%** on evaluated valid rows; the policy trades **coverage for abstention**, not better quotes.

### Gate (prereg)

| Arm | Promote? | Reason |
| --- | --- | --- |
| Model quote | **Hold** | Reproduces 44% cap-25 band (matches verification temporal arm) |
| Optional | **Reject** | −4pp monthly vs model quote; no evidence diagnostic gain |
| Span-check | **Reject** | Schema 72% < 90% reject rule; monthly headline not apples-to-apples |

**Decision:** do not change evidence policy; keep required model quotes on promoted path. Revisit span-check only with a softer guard (repair-to-initial vs abstain) if evidence diagnostics remain a research question.

---

## 3. Prompt policy

Architecture fixed: temporal-candidates verify-repair; evidence: model quote.

| Arm | Run ID | Monthly | Purist | Pragmatic | Schema | Valid / Invalid |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Temporal v1.1 (baseline) | `gan_s0_prompt_policy_temporal_v1_1_cap25_gpt4_1_mini_20260520T233934Z` | 44.0% | 64.0% | 72.0% | 100% | 25 / 0 |
| Synthesis port | `gan_s0_prompt_policy_synthesis_port_cap25_gpt4_1_mini_20260520T233941Z` | 39.1% | 56.5% | 78.3% | 92% | 23 / 2 |
| Guardrails port | `gan_s0_prompt_policy_guardrails_port_cap25_gpt4_1_mini_20260520T234051Z` | **48.0%** | 64.0% | 72.0% | 100% | 25 / 0 |

### Prediction overlap

- **v1.1 ≡ model-quote ≡ direct** (identical labels).
- **Guardrails port** differs on **6** records; **+4pp** monthly vs v1.1.
- **Synthesis port** differs on several records; **−4.9pp** monthly, 2 invalid.

### Gate (prereg)

| Arm | Proceed to full? | Reason |
| --- | --- | --- |
| v1.1 | **Hold** (reference) | Matches 44% cap-25 anchor |
| Synthesis port | **Reject** | > 2pp below v1.1; schema 92% |
| Guardrails port | **Hold** (candidate) | 48% ≥ v1.1 − 2pp; schema 100%; +4pp monthly |

**Decision:** **reject** synthesis port. **Hold** guardrails port — run a short error-read against v1.1 on the 6 changed IDs before any full-validation prompt-policy run; do not promote over v1.1 without full-split confirmation.

---

## Next steps (recommended)

1. **Registry + atlas:** add nine rows under the three `gan_s0_*_gpt_validation_v1` comparison groups; regenerate matrix/atlas.
2. **Optional:** cap-25 error-read for guardrails port vs `…233934Z` on differing record IDs.
3. **Do not run:** verification full-validation trio; evidence span-check/optional follow-ups; synthesis port full validation.
4. **Lane A ExECT:** continue GPT cap-25 groups (prompt / verification / evidence) — Gan slice is now closed at cap-25.

## Taxonomy

| Group | `varied_factor` | `intended_decision` (cap-25) |
| --- | --- | --- |
| `gan_s0_verification_gpt_validation_v1` | `verification_strategy` | hold (null) |
| `gan_s0_evidence_policy_gpt_validation_v1` | `evidence_strategy` | reject optional & span-check |
| `gan_s0_prompt_policy_gpt_validation_v1` | `prompt_policy` | hold guardrails port; reject synthesis |
