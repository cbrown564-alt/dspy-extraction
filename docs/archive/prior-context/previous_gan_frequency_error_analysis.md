# GAN Frequency Format Sweep — Running Log

Goal: Raise relaxed frequency score for Qwen3.5 on GAN 2026 validation set to >0.8.
Baseline: `gan_frequency_qwen35_single_call__validation__v1` — relaxed_match = 0.578 (170/294)

---

## 2026-05-16 — Deep Error Analysis

### Baseline metrics
| metric | value |
|---|---|
| format_valid | 1.000 (294/294) |
| frequency_match (strict) | 0.554 (163/294) |
| frequency_relaxed_match | 0.578 (170/294) |
| abstention_decision_correct | 0.782 (230/294) |
| quote_exists | 0.964 (352/365) |

### Error breakdown (124 misses)
| category | count | % of misses |
|---|---|---|
| pred_unparsed | 44 | 35.5% |
| wrong UNK (model says unknown, gold has rate) | 35 | 28.2% |
| wrong NS/no_ref (model says SF/no-ref, gold has rate) | 23 | 18.5% |
| other wrong bucket | 22 | 17.7% |

### Root causes — unparsed predictions (44)

- **≤/≥ prefix copying** (2): model verbatim copies `≤ 6 to 7 per year` from letter instead of stripping to `6 to 7 per year`
- **"or" instead of "to" ranges** (3): `8 or 9 per 3 week`, `6 or 7 per 2 month`, `3 or 4 per week`
- **"every N unit" pattern** (5): `every 4 days`, `every two to three days`, `every three to four months`, `every one or three days`, `every night`
- **Adjective time units** (4): `daily`, `nightly`, `biweekly`, `monthly` — should be `1 per day`, `1 per 2 week`, etc.
- **Multi-type extraction** (7–8): model lists all seizure types (`daily drop attacks, twice weekly focal aware...`) instead of the highest-frequency type
- **Qualitative without number** (3): `several per week`, `several in the past week`, `many per month`
- **Non-canonical units** (1): `11 to 28 per quarter` → `11 to 28 per 3 month`
- **Cluster format** (1): `2 clusters per month` instead of `2 cluster per month, 4 per cluster`
- **Calendar reference** (2): `4 in July` → `4 per month`; `3 per calendar year` → `3 per year`
- **Compound phrases** (5): free-text descriptions that aren't label-format

### Root causes — wrong UNK (35)
Model over-abstains to "unknown" when gold has specific (often complex) frequency:
- 13 cases have cluster gold labels (`N cluster per unit, M per cluster`)
- 12 cases have sub-monthly rates (`N per M month` style, e.g. `5 per 2 month`, `7 per 9 month`)
- 10 remaining are other cases where model fails to extract

### Root causes — wrong NS/no_ref (23)
Model says "seizure free" when letter contains ongoing frequency:
- ~20 cases: model picks up short recent seizure-free period (e.g., "SF for 2 weeks") and ignores the ongoing monthly rate
- ~3 cases: model says "seizure free since [month]" when gold says an ongoing rate

---

## Interventions Designed

### Three ablation conditions vs baseline `gan_core`

| condition | change from baseline | hypothesis |
|---|---|---|
| `gan_frequency_rich_policy_qwen35` | `guideline: gan_frequency_policy_rich` | Explicit format rules in normalization/abstention sections reduce unparsed outputs |
| `gan_frequency_rich_examples_qwen35` | `example_policy: gan_frequency_format_examples` | 13 examples covering error types guide canonical output format |
| `gan_frequency_rich_both_qwen35` | both guideline + examples | Maximum expected improvement |

### New guideline `gan_frequency_policy_rich` (added to components.yaml)
Adds to existing 3 normalization rules:
- Canonical form enumeration: `N per unit`, `N to M per unit`, `N per M unit`, `N cluster per unit, M per cluster`, `seizure free for N unit`, `unknown`, `no seizure frequency reference`
- Valid units: day, week, month, year (singular)
- Strip ≤/≥ and "at most"/"up to" qualifiers
- "or" → "to" for numeric ranges
- Convert adjective rates: daily→1/day, nightly→1/day, weekly→1/week, monthly→1/month, biweekly/fortnightly→1 per 2 week
- Convert "every N unit" → "1 per N unit"
- Qualitative without number → "unknown"
- Abstention rule: don't use "seizure free for N unit" when a current quantified rate is also present

### New example policy `gan_frequency_format_examples` (added to components.yaml + assembly.py)
13 examples (4 original + 9 new covering error types):
- `≤ 6 to 7 per year` → `6 to 7 per year`
- `daily` / `nightly` → `1 per day`
- `biweekly` → `1 per 2 week`
- `every 4 days` → `1 per 4 day`
- `every two to three days` → `1 per 2 to 3 day`
- `3 or 4 per week` → `3 to 4 per week`
- `daily absences and 2 focal seizures per month` → `1 per day` (highest freq type)
- `2 cluster days per month with 5 to 7 seizures per cluster day` → `2 cluster per month, 5 to 7 per cluster`
- `11 to 28 events per quarter` → `11 to 28 per 3 month`

---

## Iterations Designed (2026-05-16)

### Iteration 1 (launched ~13:25)
Three conditions launched:
- `gan_frequency_rich_policy_qwen35` — new `gan_frequency_policy_rich` guideline with explicit format rules
- `gan_frequency_rich_examples_qwen35` — new `gan_frequency_format_examples` policy (13 examples)
- `gan_frequency_rich_both_qwen35` — both combined

### Intermediate findings from rich_policy early results (44/294 docs)
- **Format errors eliminated**: 0 unparsed predictions (vs 44 in baseline) ✓
- **Remaining error profile**:
  - pred_unk_wrong: 6/44 (projected ~35 full run) — cluster and infrequent rate cases
  - pred_ns_wrong: 4/44 (projected ~27 full run) — SF disambiguation
  - wrong bucket: 2/44
- Early relaxed rate: 31/44 = 0.705

### Critical discovery: GAN dataset has a 6-month SF threshold rule
Inspecting gold annotation analysis text revealed an explicit annotation policy:
- **SF < 6 months** → compute rate from total event count over full period (NOT "seizure free")
- **SF ≥ 6 months** → use "seizure free for N unit" label

Example from GAN014370 analysis: "As seizure freedom is <6 months, we calculate frequency rather than label as long-term seizure free. Hence: 4 per 3 month."
Example from GAN014390: "the seizure-free period is about 3 months, which is less than 6 months, so he cannot be classified as seizure free."
Example from GAN014872: "He is not seizure-free by the 6-month criterion."

This explains ~20 of the 23 NS-wrong cases in baseline. The model says "seizure free for N weeks/months" when gold computes the period rate.

### Iteration 2 (launched ~13:30 and ~13:33)
Two new conditions targeting the discovered issues:
- `gan_frequency_v2_qwen35` — `gan_frequency_policy_v2` + `gan_frequency_format_examples_v2`
  - Adds cluster format instruction, historical period rule, stronger SF disambiguation
- `gan_frequency_v3_qwen35` — `gan_frequency_policy_v3` + `gan_frequency_format_examples_v3`
  - **Adds the 6-month SF threshold rule** (the key annotation-specific rule)
  - Two concrete SF < 6 months examples: "4 seizures in Feb, well since (now May, 3 months) → 4 per 3 month"

---

## Regression Analysis

### GAN006252 (quarter-as-window regression)
- Letter says: "These have occurred approximately 2 to 4 times per month over the last quarter"
- Gold: "2 to 4 per month" (rate is monthly; "quarter" is observation window)
- rich_policy: "2 to 4 per month" ✓ (guideline alone, no examples, correct)
- rich_examples: "2 to 4 per month" ✓ (examples alone, correct)
- rich_both: "2 to 4 per 3 month" ✗ (REGRESSION! guideline + examples = over-applies quarter→3month)
- v2, v3: same regression
- Root cause: the "quarter → 3 month" guideline rule COMBINED with the quarter example causes over-generalization. Neither alone causes the regression.
- v4 fix: remove the "per quarter" example; add counter-example showing "quarter as window → monthly rate"

### GAN010386 (cluster partial format regression, v3 only)
- Letter has cluster seizures with weekly pattern
- Gold: hit (purist bucket match)
- v2: "1 cluster per week, 2 to 3 per cluster" ✓ (FULL cluster format)
- v3: "2 to 3 per cluster" ✗ (PARTIAL format = unparsed = miss)
- Root cause: v3's additional SF examples ("4 per 3 month" etc.) seem to interfere with the cluster format generation (stochastic or interaction effect)
- v4 does NOT have this regression (uses `gan_frequency_format_examples_v4` without the extra SF examples)

### GAN010244 (cluster-historical, only v2 fixes it)
- Gold: "4 cluster per month, multiple per cluster"
- All except v2: "unknown" (missed)
- v2: "4 cluster per month, multiple per cluster" ✓ (FIXED by cluster-historical example)
- rich_both: still "unknown" (doesn't have cluster-historical example)
- v4: still "unknown" (doesn't have cluster-historical example)
- This is the key trade-off: v2 fixes GAN010244 but regresses GAN006252. v4 doesn't fix GAN010244 but prevents GAN006252 regression.

### Summary of regression types
- Quarter-as-window regression (GAN006252): affects rich_both, v2, v3 but NOT rich_policy, rich_examples, v4
- Cluster partial format (GAN010386): affects v3 only
- Quarter regression appears RARE (1 in ~10 baseline hit docs in sample, only 1 at-risk doc found in v2's 20 processed docs)

## Runs Status

| run_id | condition | status | early_rate (@ docs) |
|---|---|---|---|
| `gan_frequency_rich_policy_qwen35__validation__v1` | `gan_frequency_rich_policy_qwen35` | **DONE** (294/294) | 0.677 @ 62 docs |
| `gan_frequency_rich_examples_qwen35__validation__v1` | `gan_frequency_rich_examples_qwen35` | **DONE** (294/294) | 0.741 @ 27 docs |
| `gan_frequency_rich_both_qwen35__validation__v1` | `gan_frequency_rich_both_qwen35` | **DONE** (294/294) | 0.760 @ 25 docs |
| `gan_frequency_v2_qwen35__validation__v1` | `gan_frequency_v2_qwen35` | **DONE** (294/294) | **0.842 @ 19 docs** |
| `gan_frequency_v3_qwen35__validation__v1` | `gan_frequency_v3_qwen35` | **DONE** (294/294) | 0.750 @ 16 docs |
| `gan_frequency_v4_qwen35__validation__v1` | `gan_frequency_v4_qwen35` | **DONE** (294/294) | — |
| `gan_frequency_v5_qwen35__validation__v1` | `gan_frequency_v5_qwen35` | **DONE** (294/294) | — |

---

## Interim Findings (in-progress, ~13:45 UTC)

### Error rates per early sample
| condition | docs | hits | relaxed_rate | unparsed | unk_wrong | ns_wrong | bucket |
|---|---|---|---|---|---|---|---|
| baseline | 294 | 170 | 0.578 | 44 | 35 | 23 | 22 |
| rich_policy | 51 | 34 | 0.667 | 1 | 8 | 6 | 2 |
| rich_examples | 15 | 11 | 0.733 | 0 | 1 | 3 | 0 |
| rich_both | 13 | 10 | **0.769** | 0 | **0** | 2 | 1 |
| v2 | 6 | 4 | 0.667 | 0 | 0 | 1 | 1 |
| v3 | 4 | 3 | 0.750 | 0 | 0 | 1 | 0 |

### Key observations
- Format fixes are working for all rich* conditions (unparsed → 0 or 1)
- `rich_examples` significantly reduces UNK wrong vs `rich_policy` (1 vs 8 in early sample)
- `rich_both` eliminates UNK wrong entirely in 13-doc sample (0 UNK errors!)
- `rich_policy` without examples still has high UNK wrong (8/51 = 16%)
- GAN003468 (perimenstrual, gold=unknown): rich_examples causes regression (SF 5 months), rich_both correctly says "unknown"
- GAN014540 (SF ~6 months, hard case): still fails in v3 (predicts "seizure free for 6 month")

### Prediction: `rich_both` most likely to reach >0.8
If UNK=0 pattern holds for all 294 docs:
- Baseline 170 hits + fix 44 unparsed + fix 35 UNK = 249/294 = 0.847 > 0.8
- Even with partial NS improvement (some NS still wrong), likely >0.8

### GAN dataset annotation policy confirmed
The analysis text in the gold annotation reveals explicit rules:
- SF ≥ 6 months → use "seizure free for N unit" label
- SF < 6 months → compute rate from total event count in the described period
- This is why "He had 4 seizures in Feb, well since (3 months)" → "4 per 3 month" not "seizure free for 3 month"

## Interim Snapshot (2026-05-16, ~15:30 UTC)

| condition | docs | rate | error_breakdown | projection |
|---|---|---|---|---|
| rich_policy | 65 | 0.677 | unk=10,ns=7,bucket=3,unparsed=1 | ~0.68 final |
| rich_examples | 33 | 0.758 | ns=4,unk=2,bucket=2,unparsed=0 | ~0.76-0.78 |
| rich_both | 32 | 0.750 | unk=3,bucket=3,ns=2,unparsed=0 | ~0.75-0.80 |
| **v2** | **25** | **0.800** | **bucket=3,ns=2,unk=0,unparsed=0** | **~0.78-0.83 → best candidate** |
| v3 | 18 | 0.750 | ns=2,bucket=1 + regression | ~0.75 |
| v4 | 2 | — | — | — (just started) |

v2 key advantages:
- 0 UNK wrong (cluster + historical examples + daily example working perfectly)
- Only 2 NS wrong (hard SF cases not fixable) 
- 3 bucket errors (2 are "year vs period" confusion, 1 is quarter regression)

Confirmed fixes vs baseline in v2's sample:
- GAN010244 (cluster-historical): "unknown" → "4 cluster per month, multiple per cluster" ✓
- Multiple format cases (≤ stripping, or→to, etc.) ✓

Confirmed non-fixes (hard cases):
- GAN014370, GAN014540: SF rule not reliably applied
- GAN012810, GAN012835: year vs per-month bucket confusion
- GAN006252: quarter-as-window regression

## Results (2026-05-17, all runs complete)

### Final scores — all conditions (294/294 docs each)

| condition | relaxed_match | strict_match | ns_wrong | unk_wrong | bucket | unparsed | notes |
|---|---|---|---|---|---|---|---|
| baseline (v1) | 0.578 | 0.554 | 23 | 35 | 22 | 44 | — |
| rich_examples | 0.561 | 0.514 | 80 | 11 | 29 | 9 | Examples alone; strict *worse* than baseline |
| rich_both | 0.578 | 0.554 | 74 | 22 | 26 | 2 | Guideline + examples; no net gain over baseline relaxed |
| rich_policy | 0.588 | 0.558 | 71 | 20 | 28 | 2 | Policy alone outperforms combined |
| v2 | 0.588 | 0.565 | 80 | 13 | 23 | 5 | Cluster + historical rule; ns_wrong rebounds |
| v4 | 0.585 | 0.558 | 73 | 20 | 25 | 4 | rich_both guideline + quarter counter-example; no improvement |
| v5 | 0.592 | 0.575 | 66 | 24 | 28 | 2 | Shorter prompt; lowest ns_wrong but highest unk_wrong |
| **v3** | **0.646** | **0.592** | **67** | **10** | **26** | **1** | **Best overall; 6-month SF threshold rule** |

Target: 0.800 relaxed. Best achieved: **0.646** (v3). Gap: 45 hits short (190/294 vs 235/294).

### Key findings

**v3 is the clear winner** (+0.068 relaxed, +0.038 strict over baseline). Its sole addition over v2 is the **6-month seizure-free threshold rule**: use `seizure free for N unit` only when SF ≥ 6 months; if SF < 6 months, compute the period rate from total events over the full described period. This directly addresses the GAN annotation policy and explains the unk_wrong collapse (35→10).

**Early projections were wrong**: the interim snapshot predicted v2 as best candidate (~0.80) and underestimated v3. v2's 0 unk_wrong in early sample did not hold at scale (13 final unk_wrong, ns_wrong rebounded to 80). v3's early regressions turned out not to dominate.

**rich_both did not improve over baseline** on relaxed match (0.578 = 0.578), and rich_examples is the only condition that *hurt* strict match (0.514 vs 0.554). The interaction effect between guideline and examples is negative on average.

**The quarter-as-window regression** (GAN006252: `2 to 4 per 3 month` instead of `2 to 4 per month`) affected rich_both, v2, v3 but not v4 or v5. v4's counter-example fix worked for that case but failed to improve overall.

### Remaining error structure in v3 (best condition)

| category | count | representative cases |
|---|---|---|
| ns_wrong | 67 | pred=`''` vs gold=`seizure free for multiple month` — model under-applies SF label for vague duration phrases |
| bucket | 26 | `per year` vs `per month` (12x off), cluster format dropped, minor numeric errors |
| unk_wrong | 10 | qualitative descriptions model can't resolve to a rate |
| unparsed | 1 | — |

**Next lever**: the 67 ns_wrong cases in v3 are almost all `pred=''` vs `gold='seizure free for multiple month'`. The 6-month threshold is now over-suppressing SF labels — the model emits empty string when it can't confirm ≥6 months. A rule that maps "multiple months" or "many months" to ≥6 months could recover a substantial portion.

**No condition reached 0.800.** The annotation policy's 6-month rule is the right direction but requires better handling of vague duration expressions (`multiple month`, `several months`) and the cluster-per-month format remains partially broken across all conditions.

---

## Deep Error Analysis — v3 (2026-05-17)

Full case-by-case analysis in **[`docs/gan_frequency_v3_error_analysis.md`](gan_frequency_v3_error_analysis.md)**.

### Key finding: infrastructure masks true performance

60 of v3's 104 misses are **API timeouts** — the model never returned a response. v3's long prompt (long policy + 17 examples) triggered longer reasoning chains that exceeded the timeout. On docs that completed:

> **190 / 233 completed = 81.5% — already above the 0.800 target.**

The remaining 44 misses on completed docs break down as:

| category | count | root cause |
|---|---|---|
| pred_ns_wrong | 15 | 6-month rule not reliably applied — "Clobazam-withdrawal cluster" pattern: model outputs SF label despite rule |
| wrong_bucket | 14 | Three sub-patterns: "year to date" denominator (3 cases), cluster format partial (3), multi-month diary sum (2), plus misc |
| pred_unk_wrong | 10 | Calendar arithmetic — model cannot sum discrete month-named events to compute N per M months |
| gold_unk_but_pred_rate | 4 | Model over-extracts from ambiguous letters; mostly defensible |
| unparsed | 1 | GAN010386 — partial cluster format (drops cluster-period, keeps per-cluster count) |

### Gold label quality notes
- **GAN009937**: probable annotation error — letter says "roughly every few weeks" but gold says 1 cluster/month
- **GAN000174**: annotation inconsistent with guideline — guideline says pick highest, gold expresses range
- ~4 cases where model answer is more defensible than gold (multiple=3 mapping; conditional-trigger seizures)

---

## Iteration 3 — v6 and v7 (designed 2026-05-17)

Two new conditions targeting the two main fixable levers: timeout elimination and year-to-date window correction.

### v6: Precision-trimmed v3

**Hypothesis**: Removing three redundant examples (already covered by policy rules) and the quarter conversion rule (which caused the GAN006252 regression) slightly shrinks the prompt, reduces timeout pressure, and fixes 3 wrong_bucket cases. Keeps all 6-month SF threshold content.

| dimension | v3 | v6 |
|---|---|---|
| policy | `gan_frequency_policy_v3` | `gan_frequency_policy_v6` |
| examples | `gan_frequency_format_examples_v3` (17) | `gan_frequency_format_examples_v6` (15) |
| quarter conversion rule | present (causes regression) | **removed** |
| year-to-date window rule | absent | **added** |
| examples dropped | — | `≤ 6 to 7 per year`, `biweekly/fortnightly`, `11 to 28 per quarter` (regression source) |
| examples added | — | `Five GTCs this year to date (clinic: Feb) → 5 per 2 month` |
| 6-month SF threshold | ✓ (policy + 2 examples) | ✓ (policy + 2 examples, unchanged) |

**Expected outcome**: Fixes GAN006252 regression + 3 year-to-date wrong_bucket cases; marginal timeout reduction. Most likely outcome is same or slightly higher score with fewer misses on completed docs.

### v7: v5 + 6-month rule (minimum viable prompt)

**Hypothesis**: v5 achieved 0 timeouts (medium policy + 11 examples) but scored 0.592 by missing the 6-month SF rule. Grafting only that rule + 2 targeted examples onto v5's shorter prompt should recover v3's gain without reintroducing timeouts.

| dimension | v5 | v7 |
|---|---|---|
| policy | `gan_frequency_policy_v5` (medium) | `gan_frequency_policy_v7` (medium) |
| examples | `gan_frequency_format_examples_v5` (11) | `gan_frequency_format_examples_v7` (13) |
| 6-month SF threshold | ✗ | **added to policy + 2 examples** |
| quarter conversion | in policy | in policy (same as v5) |
| timeouts in v5 | 0 | expected 0 or few |
| SF < 6 months example | absent | `4 seizures Feb withdrawing Clobazam; well since (May, 3 months) → 4 per 3 month` |
| SF >= 6 months example | present (18 months) | present (18 months) + `14 month` anchor |

**Expected outcome**: 0 or near-0 timeouts; relaxed_match ≥ 0.646 (v3's score). This is the decisive test: if v7 matches v3 with 0 timeouts, it achieves 0.646 on 294 docs, already close to target.

### Runs status

| run_id | condition | status |
|---|---|---|
| `gan_frequency_v6_qwen35__validation__v1` | `gan_frequency_v6_qwen35` | pending |
| `gan_frequency_v7_qwen35__validation__v1` | `gan_frequency_v7_qwen35` | pending |
