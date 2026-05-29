# Gan S0 G17 Unknown vs. No-Reference Policy Separation

Status: current synthesis / special-label policy
Date: 2026-05-29
Kanban card: G17 - Gan Unknown vs. No-Reference Policy Separation
Dataset/split: Gan 2026 synthetic (`gan_2026_fixed_v1:validation`)
Surface: `gan_s0_g6_standard50_v1`
Primary scorer: `gan2026_paper_reproduction` monthly-frequency match, with repair, range, and tolerance disabled
Diagnostic scorer: `gan_frequency_deterministic_v1` canonical monthly-frequency match
Model calls: none
Scorer, loader, split, bridge, prompt, model, candidate-builder, target-selection, and prediction-repair semantics: unchanged.

## Research Question

What should the next Gan special-label policy distinguish before another selector or repair mechanism is allowed to claim progress on `unknown` versus `no seizure frequency reference`?

G17 is deliberately a policy separation card, not a new selector. G19 showed that the relevant failure surface is broader than a string-level `unknown` versus `no seizure frequency reference` distinction. The active surface includes unclear-frequency rows, unknown-cluster rows, seizure-free/no-reference scorer discordance, and cases where unclear gold is overcalled as a concrete rate.

## Method

The policy slice comes from the G19 post-G16 standard50 attribution ledger. Rows were selected when G19 routed them to special-label policy rather than quantified-rate aggregation or ordinary closed-option target selection.

Source artifacts:

- `docs/experiments/gan/gan_s0_g19_post_g16_error_attribution_audit_20260529.json`
- `docs/experiments/gan/gan_s0_g19_post_g16_error_attribution_audit_20260529.md`
- `docs/experiments/gan/gan_s0_g16_aggregation_policy_20260529.md`
- `docs/experiments/gan/gan_s0_g13_frequency_content_gate_report_20260529.md`
- `docs/experiments/gan/gan_s0_g5_scorer_mode_forensics_for_g4_20260528.md`
- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md`

Gold remains `seizure_frequency_number[0]`. `reference[0]` remains a secondary cross-check and difficulty signal, not gold.

## Policy Slice

The G17 slice has 9 standard50 rows.

| Policy bucket | Rows | Record IDs |
| --- | ---: | --- |
| Unknown cluster misrouted as concrete | 1 | `gan_6532` |
| Unknown misrouted as concrete quantified evidence | 3 | `gan_9566`, `gan_6607`, `gan_11380` |
| Unknown misrouted as seizure-free evidence | 2 | `gan_5974`, `gan_14002` |
| Unknown overcalled as a concrete rate despite a correct G13 gate | 1 | `gan_6387` |
| Seizure-free/no-reference scorer-mode discordance | 2 | `gan_7894`, `gan_8264` |

Companion artifact:

- `docs/experiments/gan/gan_s0_g17_unknown_no_reference_policy_20260529.json`

## Row-Level Ledger

| Record | Gold | Reference | Policy bucket | Missed by | G13/G14/G16 links |
| --- | --- | --- | --- | --- | --- |
| `gan_6532` | `unknown, multiple per cluster` | `unknown` | unknown cluster misrouted as concrete | G8, G10 | G13 `unknown_unclear_frequency -> quantified_frequency_presence`; G14 exact temporal candidate present; G16 closed option already available |
| `gan_9566` | `unknown` | `unknown` | unknown misrouted as concrete quantified evidence | G8, G10, G15 | G13 `unknown_unclear_frequency -> quantified_frequency_presence`; G14 upstream G13 caveat; G16 outside rate/duration policy |
| `gan_5974` | `unknown` | `unknown` | unknown misrouted as seizure-free evidence | G8, G10, G15 | G13 `unknown_unclear_frequency -> seizure_free`; G14 upstream G13 caveat; G16 outside rate/duration policy |
| `gan_6607` | `unknown` | `unknown` | unknown misrouted as concrete quantified evidence | G10, G15 | G13 `unknown_unclear_frequency -> quantified_frequency_presence`; G14 upstream G13 caveat; G16 outside rate/duration policy |
| `gan_6387` | `unknown` | `unknown` | unknown overcalled as a concrete rate despite a correct G13 gate | D1 | G13 `unknown_unclear_frequency -> unknown_unclear_frequency`; G14 exact temporal candidate present; G16 closed option already available |
| `gan_14002` | `unknown` | `unknown` | unknown misrouted as seizure-free evidence | G10, G15 | G13 `unknown_unclear_frequency -> seizure_free`; G14 upstream G13 caveat; G16 outside rate/duration policy |
| `gan_11380` | `unknown` | `unknown` | unknown misrouted as concrete quantified evidence | G8, G10, G15 | G13 `unknown_unclear_frequency -> quantified_frequency_presence`; G14 upstream G13 caveat; G16 outside rate/duration policy |
| `gan_7894` | `seizure free for multiple year` | `seizure free for multiple month` | seizure-free/no-reference scorer-mode discordance | Builder-gap GPT, D1 | G13 `seizure_free -> seizure_free`; G14 exact temporal candidate present; G16 closed option already available |
| `gan_8264` | `seizure free for 4 month` | `unknown` | seizure-free/no-reference scorer-mode discordance | D1 | G13 `seizure_free -> seizure_free`; G14 exact temporal candidate present; G16 closed option already available |

## Policy

### 1. Do not collapse G17 into a binary string problem

The active policy surface is not just whether a model writes `unknown` or `no seizure frequency reference`. Future reports must keep at least these strata separate:

- `unknown`: seizures are referenced but frequency is uninterpretable.
- `no seizure frequency reference`: no seizure-frequency information is present.
- `unknown, <n> per cluster`: cluster size is known but cluster spacing is unknown.
- `seizure free for <duration>`: seizure freedom duration, not no-reference.
- unclear-frequency evidence misrouted as concrete quantified evidence.
- unclear-frequency evidence misrouted as seizure-free evidence.

### 2. Keep scorer modes separate

`gan2026_paper_reproduction` is the benchmark-facing comparison mode. The canonical clinical scorer preserves the distinction between `unknown` and `no seizure frequency reference`. G17 does not change either scorer. A future selector may report both, but it must state which discrepancies are scorer-mode artifacts rather than semantic corrections.

### 3. Route unknown-cluster rows outside simple abstention policy

`unknown, multiple per cluster` is not plain `unknown`; it has partial cluster information and missing spacing. It should be stratified with cluster policy and unclear-frequency handling rather than repaired into a bare abstention label.

### 4. Treat seizure-free/no-reference discordance as benchmark semantics

Rows like `gan_7894` and `gan_8264` should not be repaired after prediction solely because the paper scorer treats special classes differently from the canonical clinical scorer. They are benchmark target-semantics rows, not deterministic repair candidates.

### 5. Do not use G17 to authorize another G8/G10/G15 prompt shape

G8, G10, and G15 already regressed on the motivating special-label overlays. A new selector card must name the G19 failure class it targets, preserve a row-level before/after ledger, and keep scorer, loader, split, benchmark bridge, candidate-builder, and prediction-repair semantics fixed.

## Decision

- Classification: **special_label_policy_defined**.
- Deterministic repair candidates: **0**.
- Selector authorization: **blocked until a new mechanism card**.
- G17 is complete as a no-model policy separation. It does not implement target selection, scorer changes, candidate changes, or prediction repair.

## Next Work

1. Pull G21 if the next step is engineering: implement the G20 deterministic quantified-rate aggregation constructor fixtures only.
2. Open a new special-label selector mechanism only if it explicitly targets one or more G17 buckets and carries a before/after ledger for the nine G17 rows.
3. Keep duration aggregation, unknown-cluster flattening, and no-reference/unknown scorer-mode collapse outside G21 unless a separate policy card authorizes them.
