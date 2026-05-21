# ExECT S0/S1 Full Validation Inspection

Date: 2026-05-19

Run artifact:

- `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T200017Z`
- Log: `runs/exect_s0_s1_validation_full_run.log`

Config:

- `configs/experiments/exect_s0_s1_validation_full_gpt4_1_mini.json`

Comparison anchor (cap-25 monolithic, same scorer and prompt):

- `docs/experiments/exect/exect_s0_s1_validation_cap25_inspection.md` (prior run `runs/exect_s0_s1_validation_cap25_gpt4_1_mini_20260518T172431Z`)

## Scope

Full fixed ExECTv2 validation split (`exectv2_fixed_v1:validation`, 40 records):

- dataset: `exect_v2`
- model: `gpt-4.1-mini` via OpenAI
- program variant: `exect_s0_s1_field_family_single_pass`
- prompt version: `exect_s0_s1_field_family_v3_seizure_evidence_policy`
- scorer: `exect_field_family_deterministic_v1`

Not published ExECTv2 benchmark reproduction.

## Validation

```powershell
uv run --extra dev pytest tests/test_experiment_configs.py::test_exect_s0_s1_validation_full_config_removes_precheck_cap tests/test_exect_s0_s1_program.py tests/test_exect_scoring.py -q
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_validation_full_gpt4_1_mini.json --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_validation_full_gpt4_1_mini.json --env-file .env
```

Runtime: ~79s prediction, 40 model calls, ~1.96s/record.

## Metrics

| Metric | Full (40) | Cap-25 anchor (25) | Delta |
| --- | ---: | ---: | ---: |
| Micro precision | 65.3% | 68.8% | −3.5pp |
| Micro recall | 70.6% | 79.5% | −8.9pp |
| Micro F1 | **67.8%** | **73.7%** | −5.9pp |
| Diagnosis F1 | 50.6% | 60.5% | −9.9pp |
| Seizure-type F1 | 61.4% | 65.8% | −4.4pp |
| Annotated-medication F1 | 87.4% | 92.1% | −4.7pp |
| Evidence quote support | 87.6% | 92.1% | −4.5pp |
| Evidence (exact only) | 87.5% | 92.0% | −4.5pp |
| Ellipsis repair rate | 0.7% | 1.1% | low both |

Gold-quality flags on evaluated records: 22.5% (vs 28.0% on cap-25).

## Error Read

Field-family mismatches span **35 documents** on the full split (vs 19 on cap-25). Dominant failure modes match the cap-25 read and intensify on the extra 15 records:

1. **Seizure-type surface drift** — e.g. `focal to bilateral seizures` vs `focal to bilateral convulsive seizures` (EA0061); `focal onset convulsive seizure` vs `focal to bilateral convulsive seizure` (EA0098); `absence events` (EA0124).
2. **Diagnosis specificity / uncertainty** — e.g. `probable juvenile myoclonic epilepsy` vs `juvenile myoclonic epilepsy` (EA0047); `symptomatic structural epilepsy` vs `symptomatic structural focal epilepsy` (EA0059, EA0150); `epilepsy with … from sleep` vs `… on awakening` (EA0116).
3. **Fused rich surfaces not split** — e.g. `focal seizures with secondary generalisation` as one label vs three gold seizure types (EA0090); combined diagnosis phrases in seizure slot (EA0188).
4. **Cross-family leakage** — diagnosis slot carries seizure or non-epilepsy content (EA0068 hydrocephalus, EA0109 focal seizures as diagnosis).
5. **Medication scope** — false positives on non-prescription or missing-gold records (EA0078, EA0109, EA0143); brand vs canonical (`lamictal` vs `lamotrigine`, EA0142).

Evidence-support errors: **25** rows (vs 14 on cap-25). Still mostly missing or header-style quotes on seizure types and medications; not the primary label-policy blocker but worth tracking on the harder tail records (EA0135, EA0142, EA0174).

Records only in the full split that add material error mass include EA0131, EA0135–EA0137, EA0142–EA0143, EA0148, EA0150, EA0153, EA0170, EA0173–EA0174, EA0179, EA0185, EA0188.

## Interpretation

- The monolithic v3 baseline is **stable enough to score at full validation scale** (40/40 predictions, artifact bundle complete).
- Full-split F1 is **lower than cap-25**, so cap-25 was an optimistic slice; do not treat 73.7% micro F1 as the validation estimate.
- Section-aware architecture remains **deprioritized** (cap-25 underperformed monolithic).
- The active improvement lever is still **benchmark label-policy alignment** (seizure-type splitting, diagnosis surface, cross-family leakage), not scorer changes or architecture reopen without a new hypothesis.

## Recommended Next Pull

1. **Do not** promote section-aware or field-group splits without a new hypothesis.
2. Target prompt/policy fixes for the highest-frequency full-split failure clusters (seizure-type convulsive modifier, fused secondary-generalisation splits, diagnosis uncertainty stripping).
3. Optional: capped replay on a **full-split error slice** fixture (mirroring Gan regression slice) before another full run.
4. Defer ExECT verify-repair until label-policy gains plateau; evidence support at 87.6% is secondary to label F1 gaps.

## Audit Guidance

Grounded in `docs/datasets/exect/exect_gold_label_audit.md`: benchmark-facing diagnosis/seizure/medication only; specificity collapse and `missing_gold` surfaced as flags, not scorer changes.
