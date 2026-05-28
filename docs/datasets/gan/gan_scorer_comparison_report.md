# Gan Seizure Frequency Task: Paper-Reproduction Scorer Comparison and Evaluation Impact Report

**Date**: May 28, 2026  
**File Reference**: [gan_scorer_comparison_report.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/datasets/gan/gan_scorer_comparison_report.md)  
**Target File**: `docs/datasets/gan/gan_scorer_comparison_report.md`

---

## 1. Executive Summary

This report documents the structural, mathematical, and semantic differences between the author-provided Gan 2026 paper evaluation code (`data/Gan (2026)/previous_paper_scorer/`) and the current codebase scorer (`src/clinical_extraction/gan/`).

The provenance matters: this scorer directory was supplied by Yujian Gan, lead author of `data/Gan (2026)/Synthetic Clinical Letters for Seizure Frequency.pdf`, as code demonstrating how the paper evaluated results. It should therefore be treated as a paper-reproduction evaluator, not as an arbitrary legacy script.

Because of differences in **null-reference mapping**, **unit-dependent constants**, the **`multiple` keyword resolution**, **range arithmetic**, **prediction repair**, and **optional tolerance behavior**, direct comparisons between metrics from the author-provided evaluator and the current repo scorer are currently **apples-to-oranges**.

The correct remedy is not to silently replace current scorer semantics. The repo should support two explicit scorer modes:

- `gan2026_paper_reproduction`: reproduces the author-provided evaluation behavior for comparison to Gan 2026 results.
- `gan_canonical_clinical`: preserves the current repo's audited semantic distinction between `unknown` and `no seizure frequency reference`.

Going forward, Gan result reports that make benchmark-comparison claims should lead with
`gan2026_paper_reproduction`. Canonical clinical metrics can still be reported, but they should be
clearly labeled as diagnostics or sensitivity analysis rather than like-for-like paper comparison.

---

## 2. Provenance and Policy Context

The Gan paper describes evaluation through Purist and Pragmatic categories after converting predictions into a common categorical frequency representation. The paper text also states that, for comparability with previous approaches, letters with unclear seizure frequency and letters with no seizure-related information were merged into an `Unknown` class, while a separate `No seizure` class captured explicit seizure-free or absence-of-seizure presentations.

That policy aligns with the author-provided evaluator's behavior where `no seizure frequency reference` is routed to the unknown numeric code (`1000`) during paper-style evaluation.

This differs from the current repo audit and scorer, which treat:

- `unknown` as seizures mentioned but frequency unclear (`1000`)
- `no seizure frequency reference` as no seizure-frequency information (`0`)
- seizure-free labels as no current seizures (`0`)

That current behavior is clinically interpretable and useful for model diagnostics, but it is not a faithful reproduction of the author-provided paper evaluator. The audit should be updated or caveated so it distinguishes paper-reproduction scorer semantics from canonical clinical semantics.

---

## 3. Technical Comparison Matrix

| Dimension | Author-Provided Gan 2026 Evaluator | Current Codebase |
| :--- | :--- | :--- |
| **Primary intended use** | Paper reproduction / comparison to Gan 2026 reported results | Current project diagnostics and experiments |
| **`no seizure frequency reference`** | Evaluated as **`1000`** (`seizure_freq_unknown`) | Evaluated as **`0.0`** (`no_seizure_information`) |
| **`unknown`** | Evaluated as **`1000`** (`seizure_freq_unknown`) | Evaluated as **`1000.0`** (`unknown`) |
| **Seizure-free labels** | Evaluated as **`0`** (`currently_no_seizure`) | Evaluated as **`0.0`** (`no_seizure_information`) |
| **`multiple` keyword** | Dynamic mapping: **2** for day/week/cluster slots, **8** for month, **18** for year | Static mapping: **3.0** in all slots |
| **Range midpoint math** | Midpoint of final rate bounds: `(max_rate + min_rate) / 2` | Rate of midpoint quantities: `mid(num) / mid(den) * unit_factor` |
| **Time constants** | 365-day year basis (`day=365/year`, `week=365/7/year`, `month=365/30/year`) | Direct monthly factors (`day=30.0`, `week=4.33`, `month=1.0`, `year=1/12`) |
| **Cluster handling** | Converts clusters to simple rate in parts of the pipeline; `multiple per cluster` maps to 2 | Preserves cluster multiplication; `multiple` maps to 3 per slot |
| **Prediction repair** | Sequential regex pipeline (`repair_predict_label`) can coerce noncanonical predictions | Strict canonical label parsing with narrow surface repair only |
| **Tolerances** | Optional `--allow_prediction_range` and `--allow_error_tolerance` (`1.5x`) | Strict monthly equality/category matching unless caller sets numeric tolerance |
| **Purist category names** | e.g. `seizure_freq_1_per_yr`, `seizure_freq_more1mon_less1week` | e.g. `lt_1_per_6_months`, `gt_1_per_month_lt_1_per_week` |
| **Pragmatic category names** | e.g. `seizure_infrequent`, `seizure_frequent` | e.g. `infrequent`, `frequent` |

---

## 4. Impact on Scoring Comparisons and Evaluations

### 4.1 Null-Reference Policy Shift

In the synthetic letters corpus, a portion of records, including administrative/non-clinical letters, are labeled `no seizure frequency reference`.

- Under the author-provided Gan 2026 evaluator, these map to `1000` (`seizure_freq_unknown`).
- Under the current codebase, these map to `0.0` (`no_seizure_information`).

This changes the gold category distribution and affects micro, macro, weighted F1, and category accuracy. A model that distinguishes no-reference from unknown may be rewarded under the current scorer but receive no such distinction under paper-reproduction scoring.

### 4.2 Quantitative Rate Discrepancies

The time constants and range arithmetic create numeric shifts. For example, for `"1 per 2 to 3 month"`:

- **Author-provided evaluator**: computes min/max yearly rates using 30-day months, then averages the final bounds. This yields approximately **0.422 seizures/month**.
- **Current codebase**: computes the midpoint denominator first (`2.5 month`) and then converts to monthly rate, yielding **0.400 seizures/month**.

These differences are usually small for ordinary numeric ranges, but they can affect boundary cases near Purist thresholds.

### 4.3 `multiple` Keyword Divergence

The author-provided evaluator uses context-dependent replacements:

- `multiple per week` -> `2 per week`
- `multiple per month` -> `8 per month`
- `multiple per year` -> `18 per year`
- `multiple per cluster` -> `2 per cluster`

The current codebase follows the audited label scheme's `multiple -> 3` rule in each slot. This is a large semantic difference. For example, `multiple per year` is infrequent under the current scorer (`3/year = 0.25/month`) but frequent under the author-provided evaluator (`18/year = 1.5/month`).

### 4.4 Prediction Repair and Tolerance Effects

The author-provided evaluator includes a broad `repair_predict_label` pipeline that can convert noncanonical output such as `"3x a week"` into a parseable label such as `"3 per week"`. It also has optional range and 1.5x numeric tolerance modes.

This means paper-reproduction scoring can be substantially more permissive than the current repo's canonical parser. That permissiveness should be reproduced when the research question is "how do our results compare to Gan 2026?", but it should not be silently mixed into project diagnostics or ablation metrics.

---

## 5. Recommended Scorer Modes

### Mode 1: `gan2026_paper_reproduction`

Purpose: reproduce the author-provided Gan 2026 evaluator for comparison with reported paper results.
This is the primary benchmark-facing evaluation mode.

Required behavior:

- Use the author-provided null-reference policy: `no seizure frequency reference -> 1000`.
- Use the dynamic `multiple` replacements from `e_evaluation_synthetic_results.py`.
- Use the 365-day year and 30-day month conversion logic from `z_step3_csv2json_and_get_freq.py`.
- Use rate-bound midpoint arithmetic for ranges.
- Support legacy category names or emit a mapping table to current category names.
- Optionally support `repair_predict_label`, `allow_prediction_range`, and `allow_error_tolerance`.
- Report the exact options used in evaluation artifacts.

### Mode 2: `gan_canonical_clinical`

Purpose: preserve current repo semantics for diagnostic research and clinically interpretable error analysis.

Required behavior:

- Preserve `unknown` and `no seizure frequency reference` as distinct label-policy classes.
- Preserve `no seizure frequency reference -> 0.0`.
- Preserve `multiple -> 3.0`.
- Preserve strict canonical parsing except for narrow, explicitly documented surface normalization.
- Keep evidence diagnostics separate from primary frequency scoring.

---

## 6. Implementation Plan

### Action 1: Add a Paper-Reproduction Scorer Mode

Extend `src/clinical_extraction/gan/scoring.py` and/or add a separate module such as `src/clinical_extraction/gan/paper_reproduction_scoring.py`.

Avoid a vague flag such as `legacy_mode=True`. Prefer explicit naming:

- `scorer_mode="gan2026_paper_reproduction"`
- `scorer_mode="gan_canonical_clinical"`

### Action 2: Port the Author-Provided Conversion Behavior with Tests

Write focused regression tests comparing the two modes on:

- `no seizure frequency reference`
- `unknown`
- `seizure free for 6 month`
- `multiple per week`
- `multiple per month`
- `multiple per year`
- `1 per 2 to 3 month`
- `2 cluster per month, 6 per cluster`
- `1 cluster per week, multiple per cluster`

The tests should make differences explicit rather than hiding them behind shared helpers.

### Action 3: Add Optional Paper-Repair and Tolerance Controls

Port `repair_predict_label` only as a paper-reproduction option, for example:

- `apply_paper_prediction_repair=True`
- `allow_prediction_range=True`
- `allow_error_tolerance=True`

Generated reports must print these options so paper-reproduction numbers are traceable.

### Action 4: Update Documentation and Existing Audit Caveats

Update `docs/datasets/gan/gan_2026_label_audit.md` to distinguish:

- author-provided paper-reproduction evaluation behavior
- current clinical/canonical diagnostic scorer behavior

Do not erase the current distinction between `unknown` and `no seizure frequency reference`; instead, document that the distinction is intentionally collapsed only in the paper-reproduction mode.

---

## 7. Implementation Reference

Author-provided evaluator files:

- **Parser and unit mapping**: `data/Gan (2026)/previous_paper_scorer/z_step3_csv2json_and_get_freq.py`
- **Prediction repair, dynamic `multiple`, tolerance flags, and categories**: `data/Gan (2026)/previous_paper_scorer/e_evaluation_synthetic_results.py`

Current repo scorer files:

- **Canonical frequency conversion**: `src/clinical_extraction/gan/frequency.py`
- **Current score object**: `src/clinical_extraction/gan/scoring.py`
- **Scorer-only label-policy bridge**: `src/clinical_extraction/gan/primitives.py`

The implementation should keep both modes available and make scorer mode part of every Gan evaluation artifact.
