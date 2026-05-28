# Gan S0 D1 Guardrail Ablation Decision — 2026-05-28

## Summary

Completed a three-way guardrail ablation on the D1 (deterministic date/events candidates) pipeline to
diagnose the −10.4pp regression introduced by D1 v1.2 (schema guard + relative anchor guardrail +
arithmetic calculator candidate injection, 69.1% monthly).

**Decision: promote D1 v1.2b (schema guard only, 79.9% monthly) as the new D1 operational baseline.**

---

## Runs

| Run | Prompt version | Monthly | Purist | Pragmatic | Schema Valid | vs D1 v1.1 |
|---|---|:---:|:---:|:---:|:---:|:---:|
| D1 v1.1 (prior baseline) | `v1` | 79.5% | 84.9% | 87.6% | 99.7% | — |
| D1 v1.2 (all 3 enhancements) | `v1_2_guardrails` | 69.1% | 76.8% | 84.2% | 99.7% | −10.4pp |
| D1 v1.3 (schema guard + anchor, no calc) | `v1_2_guardrails` | 75.3% | 80.9% | 83.9% | 100.0% | −4.2pp |
| **D1 v1.2b (schema guard only, no anchor, no calc)** | `v1_2b_schema_guard_only` | **79.9%** | **84.9%** | **87.6%** | 99.7% | **+0.4pp** |

---

## Decomposition

| Enhancement | Marginal cost | Verdict |
|---|:---:|---|
| Schema guard (`X per unknown` → `unknown`) | **+0.4pp net positive** | KEEP |
| Relative anchor guardrail ("since starting…" → `unknown`) | **−4.6pp** | DISCARD |
| Arithmetic calculator candidate injection | **−6.2pp** | DISCARD |

### Schema guard
Enforcing that outputs never contain hybrid `X per unknown` labels slightly *improves* accuracy
(+0.4pp) while bringing schema validity to 99.7% (D1 v1.1 also had 99.7% but with 1 invalid;
v1.2b also has 1 invalid on a different record). Net positive; retained unconditionally.

### Arithmetic calculator candidate injection
The `run_arithmetic_calculator` function fires on any note containing two or more month names,
including medication date mentions, appointment schedules, and titration logs — not just seizure-event
series. This floods the adjudicator with spurious arithmetic candidates that push outputs toward
incorrect aggregated rates. Disabled as a candidate injector; retained in diagnostic-only mode
(stored in `calculated_arithmetic` field but not added to the `candidates` list).

### Relative anchor guardrail
The instruction blocking `"since starting [medication]"` / `"since discharge"` denominator inference
costs 4.6pp on the full validation set. Post-hoc analysis: the guardrail over-fires because many
notes that use relative anchoring phrases *also contain explicit month/year landmarks nearby* that
would allow correct calendar-window calculation. The guardrail blocks these along with truly
unanchored cases, causing net harm. Discarded for now; narrowing to *exclusively unanchored* cases
(no month/year in the surrounding ±200-character window) is a candidate for a future arm.

---

## What Changed in Code

- **`src/clinical_extraction/programs/gan_frequency_s0.py`**:
  - `build_deterministic_date_event_payload`: arithmetic calculator result stored in
    `calculated_arithmetic` field but no longer injected as a `GanTemporalFrequencyCandidate`.
  - Added `GAN_FREQUENCY_S0_DATE_EVENTS_ADJUDICATE_EXTRACTOR_SCHEMA_GUARD_ONLY_ADDENDUM`
    constant (v1.2b): identical to v1.2 addendum but with the relative anchor guardrail line removed.
  - Added prompt version constant
    `GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_V1_2B_SCHEMA_GUARD_ONLY_PROMPT_VERSION`
    (`gan_frequency_s0_date_events_candidates_v1_2b_schema_guard_only`).
  - Registered new prompt version in `build_gan_frequency_s0_extractor_signature` with its own
    `GanFrequencyS0DateEventsAdjudicateSchemaGuardOnlySignature` class.

- **New experiment configs**:
  - `configs/experiments/gan_s0_date_stage_d1_v1_2_guardrails_cap25_gpt4_1_mini.json` (isolation cap-25)
  - `configs/experiments/gan_s0_date_stage_d1_v1_2_guardrails_full_validation_gpt4_1_mini.json` (D1 v1.3 full)
  - `configs/experiments/gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini.json` (D1 v1.2b full)

---

## New D1 Operational Default

| Surface | Program | Prompt version | GPT 4.1-mini | Schema valid | Run |
|---|---|---|:---:|:---:|---|
| Gan S0 D1 pipeline | `gan_frequency_s0_date_events_candidates_single_pass` | `gan_frequency_s0_date_events_candidates_v1_2b_schema_guard_only` | **79.9% monthly** | 99.7% | `gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini_20260528T074900Z` |

The D1 v1.2b baseline still trails builder-gap v1 GPT (80.6% monthly), so **builder-gap v1 remains
the Gan S0 operational default for paper reporting**. D1 v1.2b is the best pipeline variant explored
under the temporal/date-stage ablation grid (R11) and is the reference point for any further D1
improvements.

---

## Open Questions

1. **Narrow anchor guardrail**: A scoped version (block only when no month/year appears within ±200
   chars of the relative-anchor phrase) may recover some of the 4.6pp at lower abstention cost.
   Requires a preregistered cap-gate before full validation.
2. **Arithmetic calculator with better parser**: The month-series regex fires too broadly. A
   seizure-event-specific parser (only aggregate counts that follow seizure-frequency noun phrases)
   might make the calculator genuinely useful. Currently too risky.
3. **Builder-gap vs D1 gap**: D1 v1.2b (79.9%) is now within 0.7pp of builder-gap v1 (80.6%).
   Whether this gap closes further with improved guardrails or better candidates is the key
   outstanding D1 question.

---

## Caveats

- All results are on the synthetic Gan 2026 validation split (`gan_2026_fixed_v1:validation`, 299 records).
- Builder-gap v1 GPT remains operational default at 80.6% monthly for paper reporting.
- The +0.4pp schema-guard gain is within 1-sigma noise for a 299-record set; treat as approximately neutral.
- The −4.6pp anchor-guardrail cost is consistent across full-validation runs and is reliable.
