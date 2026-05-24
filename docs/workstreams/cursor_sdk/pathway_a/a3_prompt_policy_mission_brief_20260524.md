# A3 Prompt Policy Mission Brief

Date: 2026-05-24
Status: Ready as a held competing arm after A2 decision
Decision scope: Pathway A card A3 design brief

## Card

A3. Frequency prompt/policy refinement

## Hypothesis

Tightening prompt guidance for qualitative frequency labels can reduce unsupported `infrequent`, `frequency same`, `frequency increased`, and `frequency decreased` false positives while preserving high-recall candidate density and existing scorer semantics.

This arm changes prompt policy only. It should not be mixed with the A2 verifier in the same implementation pilot.

## Fixed Controls

| Dimension | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Split | `exectv2_fixed_v1:validation`; cap-25 before full validation |
| Surface | S5 core families |
| Baseline config | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_cap25_gpt4_1_mini.json` |
| Model/provider | `gpt-4.1-mini`, OpenAI |
| Scorer mode | `exect_s5_core_field_family_deterministic_v1` |
| Candidate policy | High-recall candidates unchanged |
| Verifier/repair | None |
| Medication guard | Existing annotated-medication guard unchanged |

## Varied Factor

Only vary qualitative frequency label evidence guidance:

- Qualitative labels require independent note support.
- Candidate hints alone are not evidence.
- Evidence quotes must come from the clinical note body, not the injected candidate block.
- Medication-control language, rescue-medication use, and seizure-type descriptions do not justify qualitative frequency labels unless frequency change is explicit.
- Supported quantified rates and explicitly supported qualitative changes may still co-exist.

Temporal/current-scope policy, multi-type/range normalization, and gold-empty clinical-frequency examples remain out of scope for this isolated arm.

## Suggested Variant

Suggested prompt version:

`exect_s4_field_family_v1_3_qualitative_evidence_gate`

Suggested cap-25 config:

`configs/experiments/exect_s5_frequency_qual_evidence_gate_am_guard_cap25_gpt4_1_mini.json`

## Allowed Write Surfaces

- `src/clinical_extraction/programs/exect_s4.py`
- `src/clinical_extraction/exect/primitives.py`, only for candidate-header wording if needed and without changing builder output
- `src/clinical_extraction/experiments/exect_prompts.py`, only if prompt version resolution requires it
- `configs/experiments/exect_s5_frequency_qual_evidence_gate_am_guard_cap25_gpt4_1_mini.json`
- Prompt-policy tests such as `tests/test_exect_s4_prompt_policy.py`

## Forbidden Changes

- Scorer, loader, split, bridge normalization, or candidate-builder logic
- Any change that reduces or reorders the high-recall candidate set
- Gold-empty examples encoded as "should extract" benchmark truth
- A2 verifier code in the same patch
- Registry, Kanban, paper, or operational-default updates before run artifacts exist

## Validation Gate

Run focused tests:

```powershell
uv run --extra dev pytest tests/test_exect_s4_prompt_policy.py tests/test_experiment_configs.py -q
uv run python scripts/validate_experiment_taxonomy.py --errors-only
```

Run cap-25 only after tests pass:

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s5_frequency_qual_evidence_gate_am_guard_cap25_gpt4_1_mini.json --env-file .env
```

Provisional pass thresholds:

- `seizure_frequency` F1 at least matches control, or precision improves by at least 3.0 points with recall drop no worse than 3.0 points.
- Diagnosis, seizure_type, annotated_medication, and investigation F1 each stay within 2.0 points of control.
- Full validation is blocked unless cap-25 clears all gates.

## A1 Fixture Focus

| Purpose | Example docs |
| --- | --- |
| Suppress unsupported qualitative FP | EA0008, EA0053, EA0131, EA0170, EA0174, EA0029 |
| Preserve true qualitative/zero-rate recall | EA0059, EA0173 |
| Confirm candidate output unchanged | Any fixed sample note before/after prompt edit |
| Avoid quantified regression | EA0047, EA0150 |

## Stop Rules

Stop and report if:

- Candidate contents or count change for the same note.
- Prompt changes touch temporal/multi-type policy or A2 verifier behavior.
- Cap-25 recall drops more than 3.0 points.
- Guard families regress beyond threshold.
- The prompt text treats clinical plausibility as a benchmark gold correction.

## Sequencing Recommendation

Prefer A2I first because it tests the precision repair mechanism without changing extraction prompt policy. Keep A3I as the lower-code competing arm or follow-up if A2 fails cap-25 or proves too costly.
