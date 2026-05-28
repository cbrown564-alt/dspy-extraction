# Gan S0 R1.1 Schema Guard Follow-Up

Date: 2026-05-26

## Scope

Follow-up to `gan_s0_r1_1_invalid_schema_error_report_20260526.md` for R5-R8.

- Dataset and split: `gan_2026`, validation-focused regression surface.
- Model/provider: no model execution in this change.
- Schema level: `gan_frequency_s0`.
- Program variant: Gan S0 prediction bridge and deterministic label-policy helpers.
- Scorer mode: `gan_frequency_deterministic_v1`; scorer semantics preserved.

## Decision

Leading inequality operators are accepted as a narrow surface repair only when
removing the leading operator leaves an otherwise canonical Gan label. Examples:
`<= 2 per day`, `≤ 7 to 8 per month`, and `at most 3 per week` canonicalize to
the corresponding rate label. This is prediction-affecting adapter cleanup, not
scorer leniency, and the raw model output remains visible in the artifact.

The following R1.1 invalid classes are not converted into scored labels:

- `unknown, <rate>` quantified hybrids.
- Multiple frequency labels concatenated into the final slot.
- Valid leading labels followed by prose.
- Malformed cluster/unknown slots.

Those labels are rejected before evaluation with `rejected_raw_label` and
`rejected_label_failure_class` metadata so they do not masquerade as canonical
Gan predictions.

Null abstentions on note-facing administrative/no-frequency records are repaired
to `no seizure frequency reference` by a note-text heuristic. This preserves the
Gan distinction from `unknown`: seizure/frequency context without a count remains
`unknown` or a model error, not no-reference.

## Regression Coverage

Added focused tests for the six R1.1 invalid-schema classes:

- `unknown, <rate>` hybrids.
- Null abstentions on no-reference/admin records.
- Concatenated labels.
- Leading inequality operators.
- Prose-appended labels.
- Malformed cluster/unknown slots.

Existing incomplete-cluster tests continue to preserve raw invalid surfaces for
evaluation, so this change does not broaden deterministic semantic repair.

## Caveats

The no-reference repair is intentionally heuristic and note-facing; it does not
consult gold labels. It should be inspected on the next capped run before any
full R1.1 replay. This change does not address the semantic causes of
unknown-prefix quantified hybrids.
