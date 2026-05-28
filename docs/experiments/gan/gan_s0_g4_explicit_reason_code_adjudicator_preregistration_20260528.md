# Gan S0 G4 Explicit Reason-Code Adjudicator Preregistration

Status: mechanism open / preregistered diagnostic slice
Date: 2026-05-28
Related card: G4 - Gan Explicit Reason-Code Adjudicator

## Research Question

Can a Gan S0 adjudicator expose target-selection reason codes, selected-candidate
references, and label-construction inputs while preserving the same-slice lift
seen in G2 candidate-constrained and seeded answer-options arms?

## Hypothesis

An explicit reason-code adjudicator over indexed deterministic temporal
candidates will match or improve the G2 seeded answer-options surrogate on the
25-record enriched validation slice, while making target-selection,
label-construction, policy, and evidence failures separable in artifacts.

## Method

- Dataset: Gan 2026 synthetic.
- Split: `gan_2026_fixed_v1:validation`.
- Slice: the same 25 enriched validation records used by G2.
- Gold source: `check__Seizure Frequency Number.seizure_frequency_number[0]`.
- Reference policy: `reference[0]` is a difficulty signal only, not gold.
- Model/provider: GPT-4.1-mini / OpenAI via `configs/models/gan_s0_gpt4_1_mini.json`.
- Config: `configs/experiments/gan_s0_g4_explicit_reason_code_adjudicator_gpt4_1_mini_slice.json`.
- Program variant: `gan_frequency_s0_explicit_reason_code_adjudicator`.
- Prompt version: `gan_frequency_s0_explicit_reason_code_adjudicator_v1_0`.
- Scorer views to report: `gan2026_paper_reproduction` and
  `gan_frequency_deterministic_v1`.
- Prediction construction: the LLM emits `adjudication_json`; deterministic code
  constructs the final label from the selected indexed candidate when possible.

## Fixed Controls

- The record slice, model, dataset split, and scorer semantics stay fixed against
  the G2 model-arm comparison.
- Deterministic temporal candidates remain the candidate substrate.
- No verifier or semantic repair pass is enabled.
- The final benchmark-facing label is distinct from the adjudication metadata.
- `unknown` and `no seizure frequency reference` remain distinct except inside
  the named paper-reproduction scorer view.

## Comparison Arms

The G4 run must be compared on this same slice against:

- `free_adjudication`: `gan_s0_g2_free_adjudication_gpt4_1_mini_slice_20260528T155000Z`.
- `candidate_constrained`: `gan_s0_g2_candidate_constrained_gpt4_1_mini_slice_20260528T155000Z`.
- `reason_code_selector`: `gan_s0_g2_reason_code_selector_gpt4_1_mini_slice_20260528T155000Z`.

## Required Diagnostics

- Reason-code distribution.
- Selected-candidate index, label, evidence, construction status, and failure reason.
- Label-construction inputs separate from the final label.
- Unsupported or invalid selected-candidate cases.
- Error class distribution: target-selection, label-construction, policy,
  evidence, or none.
- Differential records against the three G2 baselines.

## Decision Rule

Do not promote or full-validate this adjudicator unless it beats or clearly
explains the same-slice G2 candidate-constrained and seeded-selector baselines
under both scorer views. If metrics tie but metadata improves error attribution,
classify it as diagnostic mechanism evidence, not a promoted selector.

## Taxonomy

- Dataset: `gan_2026`
- Schema complexity: `gan_s0`
- Clinical task family: `frequency`
- Program architecture: `explicit_reason_code_adjudicator`
- Hybrid balance class: `H2_pre_deterministic`, `L1_llm_constrained`,
  `H4_deterministic_first_llm_adjudicates`, `H1_post_deterministic`
- Interleaving positions: `pre`, `during`, `post`
- Varied factor: `implementation_variant`
- Comparison group: `gan_s0_g4_reason_code_adjudicator_gpt4_slice_v1`
- Decision scope: `arm`

## Caveats

This is a diagnostic synthetic-validation slice, not Gan paper reproduction and
not Real(300) reporting. Direct benchmark-comparison claims remain blocked until
G5 paper-scorer rescoring and the dataset caveats in
`docs/policies/published_benchmark_metrics.md` are satisfied.
