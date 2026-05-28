# G3 - Gan Unknown Versus No-Reference Policy Probe Report

Input Run Directory: `runs\gan_s0_g2_reason_code_selector_gpt4_1_mini_slice_20260528T155000Z`
Total Records Evaluated: 25

## Policy Configuration
- Unknown vs No-Reference Boundary Rule: **Enabled**
- Weak Rate to Unknown Rule: **Enabled**
- Seizure-Free Conflict Resolution Rule: **Enabled**

## Metrics Comparison

| Scorer / Metric | Original | Probed | Delta |
| --- | ---: | ---: | ---: |
| gan2026_paper_reproduction_exact | 92.0% | 92.0% | +0.0pp |
| gan2026_paper_reproduction_monthly | 92.0% | 92.0% | +0.0pp |
| gan2026_paper_reproduction_pragmatic | 100.0% | 96.0% | -4.0pp |
| gan2026_paper_reproduction_purist | 92.0% | 92.0% | +0.0pp |
| gan_frequency_deterministic_v1_exact | 92.0% | 92.0% | +0.0pp |
| gan_frequency_deterministic_v1_monthly | 92.0% | 92.0% | +0.0pp |
| gan_frequency_deterministic_v1_pragmatic | 100.0% | 96.0% | -4.0pp |
| gan_frequency_deterministic_v1_purist | 92.0% | 92.0% | +0.0pp |

## Changed Predictions Details

| Record ID | Gold Label | Original Prediction | Probed Prediction |
| --- | --- | --- | --- |
| `gan_13123` | `1 per year` | `1 per multiple months` | `unknown` |
