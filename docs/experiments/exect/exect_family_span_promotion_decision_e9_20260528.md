# ExECT Family-Span Promotion Decision E9

Date: 2026-05-28
Status: active guidance
Kanban card: E9 - Family-Span Promotion Or Rejection Decision
Decision scope: prompt-routing arm classification; no scorer, loader, split, bridge, prompt, repair, or model-output change

## Decision

The tested E8 family-span prompting arm is a **rejected arm** for S1-style full-note replacement.

The underlying `exect.sections.family_spans.v1` payload remains a **diagnostic document-geometry substrate** and may still support future preregistered mechanisms, but it is not promoted as an operational context-routing default.

This decision rejects the specific single-pass arm shape tested in E8: replacing the full-note S1 context with E4 family spans for diagnosis/problem, seizure, medication, and investigation-bearing lines. It does not reject typed document geometry, evidence coverage audits, one-family span probes, candidate adjudication surfaces, or pairwise interaction designs that use spans with a narrower hypothesis.

## Evidence

E4 established that the family-span payload has strong representability as a substrate:

| Evidence item | Result |
| --- | ---: |
| Full validation spans emitted | 816 |
| Diagnosis/problem evidence coverage | 56/56 |
| Seizure evidence coverage | 49/49 |
| Medication evidence coverage | 53/53 |
| Investigation evidence coverage | 33/33 |
| Frequency evidence coverage | 44/44 |
| History/background evidence coverage | 85/89 |
| Cap-25 selected-family gold coverage | 116/116 |
| Cap-25 family-span characters / full-note characters | 29,319 / 33,029 |
| Cap-25 character ratio | 88.8% |

E8 tested the promotion question directly on the first 25 ExECT validation documents with the same model, prompt, repair policy, schema level, scorer, and split. The only varied factor was context selection.

| Arm | Micro P | Micro R | Micro F1 | Diagnosis F1 | Seizure-type F1 | Medication F1 | Evidence support |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full note | 96.3% | 95.2% | 95.8% | 97.6% | 95.4% | 94.9% | 97.3% |
| Family span | 91.4% | 89.2% | 90.2% | 97.6% | 81.8% | 94.7% | 95.8% |

The span arm lost 5.5pp micro F1 and 13.6pp seizure-type F1 while only reducing prompt substrate characters by 11.2%. Because cap-slice gold evidence coverage was 116/116, the loss is not adequately explained by missing gold offsets. The better current interpretation is that the span rendering and false-family context changed seizure-type adjudication without delivering enough recall, precision, evidence, or cost benefit to justify promotion.

## Classification

| Surface | Classification | Rationale |
| --- | --- | --- |
| E8 S1 family-span prompt arm | rejected arm | Failed the preregistered promotion gate against the matched full-note control. |
| `exect.sections.family_spans.v1` payload | diagnostic substrate / mechanism open | Strong evidence coverage remains useful for audits, routing, and future narrower mechanisms. |
| Full-note S1 control | diagnostic baseline | Strong cap-slice baseline, not an isolated diagnosis or seizure-type ceiling. |
| ExECT Table 1 comparison | blocked benchmark claim | This E9 decision uses project S1 field-family scoring, not CUI-aware all-family published-benchmark scoring. |

## Guardrails

Future work may reopen family spans only with a preregistered, narrower mechanism that states:

- the target family or component;
- whether spans are used as context, candidates, evidence filters, or adjudication inputs;
- the full-note or current-stack comparator;
- the scorer mode and bridge policy;
- false-family span handling;
- support counts and stop rules;
- whether the result is diagnostic, an isolated component ceiling, or a rejected arm.

Do not rerun the same S1 full-note replacement shape as an optimization loop. A future span mechanism should make the mechanism smaller, not just prompt around the same broad context substitution.

## Caveats

- Dataset/split: ExECTv2 `exectv2_fixed_v1:validation`.
- E8 scope: first 25 validation documents, not full validation or holdout.
- Model/provider: GPT 4.1-mini / OpenAI.
- Schema level: `exect_s0_s1_field_family`.
- Scorer: `exect_field_family_deterministic_v1`.
- Medication scoring remains benchmark-facing annotated prescription matching; medication temporality is not scored.
- Investigation spans were included as context in E8 but investigation was not scored by the S1 comparison.
- Holdout was not used.
- No scorer, loader, split, bridge, prompt, repair, or artifact semantics changed.

## Implications

E9 closes the immediate family-span promotion decision. The next ExECT work should move to validation-only component probes from the current board: S1 diagnosis/seizure-type transfer, frequency payload robustness/adjudication, medication payload routing, or E12 investigation confirmation.

Family spans remain available as a diagnostic substrate for those probes when they have a specific mechanism role. They are not a default prompt-routing replacement for full notes.

## References

- `docs/experiments/exect/exect_family_span_payload_audit_20260528.md`
- `docs/experiments/exect/exect_family_span_payload_audit_20260528.json`
- `docs/experiments/exect/exect_family_span_prompt_comparison_e8_preregistration_20260528.md`
- `docs/experiments/exect/exect_family_span_prompt_comparison_e8_results_20260528.md`
- `docs/component_ceiling_registry.md`
- `docs/datasets/exect/exect_gold_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md`
