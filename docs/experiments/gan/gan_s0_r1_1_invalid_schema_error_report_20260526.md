# Gan S0 R1.1 Invalid Schema Error Report

Date: 2026-05-26

## Run

- Run ID: `gan_s0_l2_qwen_exact_policy_full_qwen35b_ollama_20260526T054752Z`
- Artifact directory: `runs/gan_s0_l2_qwen_exact_policy_full_qwen35b_ollama_20260526T054752Z`
- Dataset and split: `gan_2026`, `gan_2026_fixed_v1:validation`
- Model/provider: `qwen3.6:35b` via Ollama
- Schema level: `gan_frequency_s0`
- Program variant: `gan_frequency_s0_temporal_candidates_single_pass`
- Prompt version: `gan_frequency_s0_temporal_candidates_single_pass_v1_8_qwen_schema_validity`
- Structured output strategy: `provider_json_schema_with_pydantic_validation`
- Scorer mode: `gan_frequency_deterministic_v1`
- Context policy: full note plus deterministic temporal candidates
- Verifier policy: none
- Repair policy: artifact bridge surface normalization only

Artifacts inspected:

- `config.json`
- `metadata.json`
- `prompts.json`
- `metrics.json`
- `errors.json`
- `predictions.json`

## Bottom Line

The 30 invalid schema cases were not mostly JSON/Pydantic failures. They were post-parse Gan label-policy failures: the run produced a `seizure_frequency_number` value, but the deterministic Gan scorer could not convert the label because it fell outside the audited six-form Gan label taxonomy.

Invalid cases split into:

| Failure type | Count | Share of invalids | Interpretation |
|---|---:|---:|---|
| `unknown, <rate>` quantified hybrid | 12 | 40.0% | Model mixed uncertainty with a quantified rate; Gan only allows bare `unknown` or `unknown, <n> per cluster`. |
| Explicit abstention/null value | 7 | 23.3% | Model abstained on no-reference/admin records instead of emitting `no seizure frequency reference`. |
| Multiple frequency labels concatenated | 5 | 16.7% | Model listed more than one candidate rate in the final label field. |
| Inequality operator | 4 | 13.3% | Model copied `<=`/`≤` evidence into the canonical label. |
| Extra prose appended to label | 1 | 3.3% | Model included seizure-type/context prose after a valid rate. |
| Malformed cluster/unknown slot | 1 | 3.3% | Model tried to combine cluster syntax with an invalid `unknown, multiple` slot. |

Only 7/30 were null label values. The other 23 were populated strings rejected by the deterministic label parser.

## Invalid Record Table

| Record | Gold label | Predicted label | Cause class | Notes |
|---|---|---|---|---|
| `gan_10447` | `unknown` | `unknown, multiple per week` | `unknown, <rate>` hybrid | Quantified cluster timing was emitted with an unknown prefix. |
| `gan_11411` | `no seizure frequency reference` | null | abstention/null | Abstained; row is `row_ok=False`. |
| `gan_115` | `7 to 8 per month` | `≤ 7 to 8 per month` | inequality operator | Otherwise close to gold surface. |
| `gan_11733` | `no seizure frequency reference` | null | abstention/null | Abstained; row is `row_ok=False`. |
| `gan_11734` | `no seizure frequency reference` | null | abstention/null | Abstained; row is `row_ok=False`. |
| `gan_11748` | `no seizure frequency reference` | null | abstention/null | Abstained; row is `row_ok=False`. |
| `gan_11763` | `no seizure frequency reference` | null | abstention/null | Abstained; row is `row_ok=False`. |
| `gan_11804` | `no seizure frequency reference` | null | abstention/null | Abstained; row is `row_ok=False`. |
| `gan_11874` | `no seizure frequency reference` | null | abstention/null | Abstained; row is `row_ok=False`. |
| `gan_12218` | `1 per day` | `unknown, multiple per day` | `unknown, <rate>` hybrid | Daily spasms were treated as unknown-plus-rate. |
| `gan_12314` | `3 per week` | `3 per week, drop attacks in batches, tonic seizures during day and night` | prose appended | Valid leading rate plus non-canonical context. |
| `gan_12319` | `2 to 3 per week` | `2 to 3 cluster per week, unknown, multiple per cluster` | malformed cluster/unknown slot | Cluster syntax invented despite rate gold. |
| `gan_12362` | `2 to 3 per day` | `2 to 3 per day, 2 per month` | multiple labels | First label matches gold, second label appended. |
| `gan_12438` | `1 per day` | `unknown, 2 to 3 per year` | `unknown, <rate>` hybrid | Selected lower-frequency tonic events and prefixed unknown. |
| `gan_12465` | `1 per day` | `unknown, 2 per year` | `unknown, <rate>` hybrid | Ignored nightly convulsions in favor of lower-frequency tonic events. |
| `gan_13019` | `9 per 3 month` | `unknown, 9 per 2022` | `unknown, <rate>` hybrid | Year-to-date denominator not canonicalized. |
| `gan_15639` | `2 per week` | `2 per week, 1 per 2 week` | multiple labels | First label matches gold, secondary rate appended. |
| `gan_15847` | `6 per week` | `6 per week, 1 per 2 week` | multiple labels | First label matches gold, secondary rate appended. |
| `gan_15876` | `6 per week` | `6 per week, 3 to 4 per week, 1 to 2 per week` | multiple labels | Model exposed component rates instead of final summed/highest label. |
| `gan_17` | `2 per day` | `≤ 2 per day` | inequality operator | Otherwise close to gold surface. |
| `gan_22` | `3 per day` | `≤ 3 per day` | inequality operator | Otherwise close to gold surface. |
| `gan_31` | `4 per day` | `≤ 4 per day` | inequality operator | Otherwise close to gold surface. |
| `gan_3747` | `3 per day` | `unknown, 3 per day` | `unknown, <rate>` hybrid | Correct rate with invalid unknown prefix. |
| `gan_4591` | `1 per 5 month` | `unknown, 2 per 18 month` | `unknown, <rate>` hybrid | Quantitative interpretation differs from gold. |
| `gan_6153` | `9 per month` | `unknown, 3 to 9 per 4 week` | `unknown, <rate>` hybrid | Hard case; reference label is `unknown`. |
| `gan_6509` | `1 per week` | `unknown, 2 per 2 week` | `unknown, <rate>` hybrid | Hard case; stripped rate would monthly-match gold. |
| `gan_7341` | `unknown` | `unknown, 2 per month` | `unknown, <rate>` hybrid | Gold/reference both unknown; model over-quantified. |
| `gan_7420` | `1 to 2 per 2 week` | `unknown, 1 to 2 per 2 week` | `unknown, <rate>` hybrid | Hard case; stripped rate would match gold. |
| `gan_744` | `multiple per week` | `multiple per day, 1 per 8 week` | multiple labels | Hard case; selected/combined incompatible rates. |
| `gan_750` | `multiple per week` | `unknown, 2 per 2 week` | `unknown, <rate>` hybrid | Hard case; reference label is `1 per day`. |

## Cause Analysis

### 1. Unknown-prefix quantified hybrids are the largest invalid class

The deterministic Gan parser accepts:

- `unknown`
- `unknown, <v|multiple> per cluster`

It does not accept `unknown, <rate>` such as `unknown, 2 per month` or `unknown, multiple per day`. These 12 cases show the model using `unknown` as a confidence hedge while still extracting a rate.

This is not safe to repair globally by stripping `unknown,`. Some stripped labels would match gold (`gan_3747`, `gan_6509`, `gan_7420`), while others would remain semantically wrong (`gan_12438`, `gan_12465`, `gan_4591`, `gan_7341`, `gan_750`). Treat this as a verifier/prompt-policy failure, not a deterministic scorer repair.

### 2. Abstentions are concentrated in no-reference/admin records

All 7 null-label invalids have gold `no seizure frequency reference`, reference `no seizure frequency reference`, and `row_ok=False`. The run config allowed explicit abstention via `allow_explicit_abstain_flag_with_error_taxonomy_policy_patch`; the model chose abstention where the Gan benchmark requires the canonical label `no seizure frequency reference`.

These are operational schema failures rather than clinical interpretation failures. The prompt or output adapter should make `no seizure frequency reference` the required label for no-reference/admin letters and reserve abstention for true extraction failure outside the benchmark contract.

### 3. The model sometimes exposed candidate lists instead of adjudicating

Five invalid labels concatenate multiple rates. In four of these (`gan_12362`, `gan_15639`, `gan_15847`, `gan_15876`), the first emitted rate is already the gold label or the intended final rate. The model appears to understand relevant rates but fails the final-label contract by appending secondary candidates.

This points toward a final-slot formatting/adjudication weakness in the single-pass temporal-candidate program. It is probably better addressed by a constrained verifier or deterministic final-slot guard than by silently taking the first comma-separated rate.

### 4. Inequality operators are near-surface failures

Four records preserve `≤` from the source evidence in the label. The gold labels drop the inequality symbol and use the canonical numeric form. These are the cleanest potential deterministic repair candidates, but they still need regression tests because `≤ N` can mean an upper bound rather than an exact/current rate. Repair should be allowed only if project policy decides this is a one-to-one canonical surface repair for Gan S0.

### 5. Prose and malformed cluster cases are isolated but diagnostic

`gan_12314` has a valid leading rate followed by seizure-type prose. `gan_12319` invents a cluster form with an invalid `unknown, multiple` slot. Both suggest the prompt's "output only canonical Gan labels" constraint is insufficient for Qwen without a stricter final output guard.

## Repairability

Deterministic repair candidates:

- Possible, with tests: strip a leading inequality operator from labels like `≤ 2 per day` if the policy accepts this as canonical surface normalization.
- Possible, with stricter guard rather than scorer semantics: reject or reprompt labels with multiple comma-separated rates, and require a single canonical final label.

Not safe as deterministic repair:

- `unknown, <rate>` hybrids. Stripping `unknown,` is sometimes right and sometimes wrong.
- Null abstentions. These should be prevented by benchmark-aware prompt/output policy, not scored as valid.
- Malformed cluster labels with unknown slots.
- Labels with appended prose.

## Implications For R1.1

Schema validity of 90.0% understates JSON validity and mostly measures Gan label-taxonomy compliance. The main issue is that Qwen can satisfy the outer structured-output shape while violating the inner canonical label language.

The invalid cases probably depress benchmark-facing accuracy, but not all invalids are equally severe:

- 7 are operational no-reference abstentions that should be straightforward to prevent.
- 4 inequality labels and several multiple-label cases contain enough information to recover the gold label under a stricter final-slot policy.
- The 12 `unknown, <rate>` hybrids are the real semantic/policy problem because they blend uncertainty, candidate evidence, and final label.

## Recommended Follow-Ups

1. Add a small invalid-schema regression fixture covering all six cause classes above.
2. Add or test a final-label guard that rejects labels outside the six Gan forms before accepting the prediction.
3. Change no-reference policy so admin/no-reference records emit `no seizure frequency reference`, not abstention.
4. Consider a targeted, tested repair for leading inequality operators only after deciding whether `≤ N per unit` is canonicalizable under Gan policy.
5. For `unknown, <rate>` hybrids, prefer verifier/repair DSPy work or prompt examples that contrast `unknown`, quantified rates, and `unknown, <n> per cluster`.

Scorer semantics were preserved for this report. No invalid label was counted as valid by post-hoc repair.
