# ExECT Label-Policy v4.12 Implementation

Date: 2026-05-21  
Prompt version: `exect_s0_s1_field_family_v4_12_label_policy`  
Comparison group: `exect_s1_qwen_diagnosis_stabilized_v1`  
Preregistration: `docs/experiments/exect/exect_s1_qwen_v4_12_diagnosis_stabilized_preregistration_20260521.md`

## Target

Repair the Qwen v4.11 S1 promotion blocker: v4.11 raised seizure_type F1 strongly but diagnosis fell from 95.1% to 90.0% on full validation. v4.12 is a prompt-only stabilization pass that keeps v4.11 seizure guidance and adds diagnosis boundary counterexamples.

## Changes

- Added `EXECT_S0_S1_V4_12_PROMPT_VERSION`.
- Added `EXECT_S0_S1_V4_12_LABEL_POLICY_ADDENDUM` for diagnosis stability.
- Added three v4.12 examples:
  - generic epilepsy must not become focal epilepsy from seizure-type wording;
  - structural imaging context alone must not become symptomatic structural focal epilepsy;
  - focal onset epilepsy diagnosis recall must be preserved.
- Added v4.12 signature boundary examples.
- Added GPT cap-25, Qwen cap-25, and Qwen full-validation configs under `exect_s1_qwen_diagnosis_stabilized_v1`.

## Unchanged

- Scorer: `exect_field_family_deterministic_v1`
- Program variant: `exect_s0_s1_field_family_single_pass`
- Bridges: existing `artifact_benchmark_bridge_only` path for Qwen
- Default production prompt: v4.10 remains frozen until a successful promotion decision

## Validation

Planned before model execution:

```powershell
uv run pytest tests/test_exect_s0_s1_program.py -q
uv run python scripts/validate_experiment_taxonomy.py --errors-only
```
