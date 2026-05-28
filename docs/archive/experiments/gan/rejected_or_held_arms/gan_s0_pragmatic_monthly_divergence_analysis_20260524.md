# Gan S0 Pragmatic Monthly Divergence Analysis

Date: 2026-05-24
Kanban Card: C3 - Pragmatic monthly divergence analysis
Decision Scope: analysis (no gold semantics changed)
Status: Complete

---

## 1. Purpose

Decide whether the 16 `pragmatic_match_monthly_divergence` benchmark-severe misses in the operational default (`gan_s0_candidate_builder_gap_v1` on GPT-4.1-mini, 80.6% monthly accuracy on full validation) represent:

(a) Fixable extraction failures — the model selects the wrong window or count but could be corrected with prompt or verifier changes;
(b) Gold-policy limitations — the gold annotation reflects a pragmatic clinical choice that differs from any reasonable deterministic extraction path; or
(c) Acceptable benchmark residuals — the pragmatic category matches, meaning the coarsest clinically relevant bucket is correct even though the exact monthly value diverges.

This analysis does not alter Gan gold semantics. The scorer (`gan_frequency_deterministic_v1`) and gold source (`seizure_frequency_number[0]`) remain unchanged.

---

## 2. What Is Pragmatic Monthly Divergence?

The metric hierarchy is: `normalized_label ⊂ monthly_frequency ⊂ purist_category ⊂ pragmatic_category`.

`pragmatic_match_monthly_divergence` applies when:
- Pragmatic category matches (the model is in the correct infrequent/frequent/unknown/no-seizure-information bucket), AND
- Monthly frequency does NOT match (the exact seizures-per-month value differs from gold).

These are benchmark-severe because monthly accuracy (80.6%) is the primary paper-facing metric. A pragmatic-only win is clinically coarse; it masks whether the model found the right event rate.

---

## 3. Full-Validation Records

From the `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` error analysis (299 valid predictions):

| Record | Gold | Predicted | Gold monthly | Pred monthly | Divergence type |
| --- | --- | --- | ---: | ---: | --- |
| `gan_15997` | `10 per 3 month` | `6 per 3 month` | 3.33 | 2.00 | count underestimation |
| `gan_17287` | `1 per 1 to 2 day` | `1 per 2 day` | 20.0 | 15.0 | window underestimation |
| `gan_16041` | `9 per 3 month` | `2 per month` | 3.00 | 2.00 | count underestimation |
| `gan_1463` | `3 per month` | `2 per month` | 3.00 | 2.00 | count underestimation |
| `gan_9424` | `10 per 9 month` | `2 per month` | 1.11 | 2.00 | window selection |
| `gan_12218` | `1 per day` | `multiple per day` | 30.0 | 1000.0* | count overestimation |
| `gan_1486` | `3 per month` | `2 per month` | 3.00 | 2.00 | count underestimation |
| `gan_1070` | `3 to 4 per week` | `4 per week` | 16.3 | 17.3 | boundary collapse |
| `gan_12246` | `1 to 2 per day` | `multiple per day` | 45.0 | 1000.0* | range to vague |
| `gan_12562` | `1 per day` | `3 to 4 per week` | 30.0 | 16.3 | freq underestimation |

> *`multiple` maps to 1000.0 in the scorer normalization, which inflates the monthly value; the pragmatic match is because `multiple per day` and `1 per day` both land in `frequent`.

From the Qwen 35b error taxonomy (same class, 20 records, `gan_s0_expanded_builders_prose_full_validation_qwen35b_ollama_20260522T131822Z`):

| Pattern | Count | Description |
| --- | --- | --- |
| Count underestimation (infrequent bucket) | 8 | Model picks a plausible but lower count from the note |
| Window selection mismatch | 5 | Model picks a different denominator for the same events |
| Range-to-point or point-to-range collapse | 4 | Model collapses a range or expands a point to a range |
| Multi-type frequency selector (picks lower) | 3 | Model picks a less-frequent seizure type's rate |

Combining both runs: **pragmatic monthly divergence accounts for 16-20 benchmark-severe misses depending on model and prompt version**, making it the second-largest benchmark-severe class after `other_semantic_mismatch`.

---

## 4. Mechanistic Classification

### 4A. Fixable Extraction Failures

The following sub-patterns are extractable errors where the note contains enough signal to recover the correct label with prompt or pipeline changes:

#### 4A1. Count underestimation in a defined window

Records `gan_15997`, `gan_16041`, `gan_1463`, `gan_1486` (and ~8 Qwen records):
- The note gives a multi-event window (e.g., "9 seizures in the past 3 months").
- The model emits a lower count for the same denominator ("6 per 3 month", "2 per month").
- **Root cause:** The model selects an incomplete subset of events from the note, likely missing a count that spans across multiple sentences or paragraphs.
- **Fixability:** High. Candidate injection can help: if a deterministic candidate extracts the correct count (e.g., via `_first_and_subsequent_dated_events_window` or `_diary_cluster_and_single_events_window`), candidate-override discipline (as planned in C2) would force the model to justify any departure.
- **Risk:** These patterns often require reading dispersed event mentions, which deterministic builders do not always cover. A verifier checking candidate vs. prediction consistency could catch this.

#### 4A2. Window selection mismatch

Records `gan_9424`, `gan_17287` (and ~5 Qwen records):
- The note gives rates with multiple possible denominators (e.g., "1 per day" from a last-event-on-date calculation vs. a longer window).
- The model selects a different but plausible window.
- **Root cause:** Underspecified window-selection policy. The current policy says "use the highest current quantified frequency" but does not specify how to choose between overlapping windows (e.g., "1 seizure in the past 2 days" vs. "10 seizures in the past 9 months").
- **Fixability:** Moderate. Adding a priority rule — prefer the observation window that matches the current clinic visit's reporting period, then fall back to the full-note time span — would help. Deterministic candidates could disambiguate by providing both windows.
- **Risk:** Window selection may depend on clinical context that is not consistently surfaced in the note.

#### 4A3. Multi-type selector (picks lower frequency)

Records `gan_12562` (and ~3 Qwen records):
- Multiple seizure types are present; the model selects a less-frequent type's rate.
- **Root cause:** Prompt says "highest current quantified frequency" but the model applies it inconsistently when seizure types differ in severity or salience.
- **Fixability:** High. Adding examples where a less-severe but more frequent seizure type determines the gold label would directly address this.
- **Risk:** Low; the policy itself is unambiguous once examples are present.

---

### 4B. Gold-Policy Limitations

The following sub-patterns reflect genuine annotation-policy divergence that cannot be resolved by extraction improvement alone:

#### 4B1. Range-to-point and point-to-range collapse

Records `gan_1070` (`3 to 4 per week` → predicted `4 per week`), and range cases in Qwen:
- Gold is a range label (e.g., `3 to 4 per week`), model emits a point label (`4 per week`).
- Both are clinically equivalent for most purposes; the pragmatic bucket matches.
- **Assessment:** This is primarily a **label surface fidelity** issue, not a frequency understanding failure. The monthly conversion differs (`(3+4)/2 * 4.33 = 15.2` for range vs. `4 * 4.33 = 17.3` for point), which triggers the monthly divergence flag.
- **Paper status:** Monthly divergence is real by the scorer's definition, but the clinical information is near-identical. For paper discussion, this class should be noted as a **surface-form policy gap** rather than an extraction failure.
- **Fixability:** Low impact. Adding range-preservation examples would reduce these specific cases, but they represent a scorer boundary artifact, not a clinical misunderstanding.

#### 4B2. vague-multiple vs. specific count

Records `gan_12218` (`1 per day` → `multiple per day`), `gan_12246` (`1 to 2 per day` → `multiple per day`):
- Gold is a specific count label; model emits a vague `multiple per day`.
- Both map to the `frequent` pragmatic bucket, so pragmatic matches.
- **Assessment:** The note likely contains both a vague descriptor ("multiple seizures") and a specific count. The gold annotation chose the specific count; the model chose the vague phrase.
- **Gold-policy note:** Gan annotation policy is not fully documented for these cases. The `reference` label (diagnostic only) may differ from the primary gold in some of these records.
- **Fixability:** Moderate. Adding a preference rule for specific-count labels over vague descriptors when both are present in the note would help. However, if the note's specific count is less clinically prominent than the vague descriptor, this is a genuine annotation ambiguity.

---

### 4C. Acceptable Benchmark Residuals (Pragmatic-Correct Class)

The 16 records in this class are benchmark-severe only because **monthly frequency is the primary paper metric**. The pragmatic bucket — `frequent`, `infrequent`, `unknown`, or `no_seizure_information` — is always correct in this class.

This means:
- The model correctly identifies whether a patient has frequent seizures, infrequent seizures, unknown frequency, or no seizure information.
- The failure is in the precise mathematical conversion (seizures per month), not the clinical category.

**Paper-facing caveat:** Monthly accuracy is the right primary metric for reproducibility and benchmark comparison. However, pragmatic category accuracy (88.6% on builder-gap v1) should be included in paper tables as a supporting metric to show that the clinical classification is largely correct even when exact monthly values diverge.

---

## 5. Prioritized Summary

| Sub-pattern | Count (GPT) | Count (Qwen est.) | Fixability | Recommended action |
| --- | --- | --- | --- | --- |
| Count underestimation in defined window | ~6 | ~8 | High | C2 candidate-override discipline; candidate builder coverage for diary/dispersed counts |
| Window selection mismatch | ~3 | ~5 | Moderate | Add window-priority policy; provide denominator-preference examples |
| Multi-type selector (picks lower) | ~2 | ~3 | High | Add highest-frequency example with multi-type notes |
| Range-to-point collapse | ~2 | ~4 | Low impact | Range-preservation examples; accept as scorer surface artifact in paper |
| Vague-multiple vs. specific count | ~3 | ~0 | Moderate | Add specific-count preference rule |

---

## 6. Decisions

### Decision 1: Are pragmatic monthly divergences fixable extraction failures?

**Answer: Partially yes.** Count underestimation and multi-type selector errors are fixable with prompt and candidate-override changes. Window selection mismatch is partially fixable. Range-to-point collapse and vague-multiple cases are annotation-policy boundary artifacts.

**Implication:** The C2 unknown-overuse arm's candidate-override discipline will incidentally address count underestimation cases where a deterministic candidate provides the correct count. Separate micro-arms for multi-type selection and window-priority policy are medium-priority and should be preregistered separately if C2 clears its gate.

### Decision 2: Are pragmatic monthly divergences gold-policy limitations?

**Answer: For a subset, yes.** Range-to-point collapse and vague-multiple cases reflect genuine label-scheme ambiguity. These should not be targeted with prompt changes that alter extraction semantics; they should be documented as scorer-surface artifacts in paper tables.

**Implication:** Do not alter gold labels, scorer normalization, or range-handling logic to absorb these cases. The gold label is `seizure_frequency_number[0]` and scorer semantics are fixed per `deterministic_scorer_semantics.md`.

### Decision 3: Are pragmatic monthly divergences acceptable benchmark residuals?

**Answer: For paper purposes, yes, with caveats.** The paper must report monthly accuracy as primary and pragmatic category accuracy as supporting. The gap between the two (80.6% monthly, 88.6% pragmatic) should be explicitly attributed to this class in the paper methods or supplementary material.

**Implication:** Add a methods note: "The 16-record pragmatic-monthly-divergence class (5.4% of validation records) is benchmark-severe by the monthly accuracy metric but clinically benign: the correct seizure-frequency category is identified in every case. Sub-patterns include count underestimation from dispersed event mentions, window selection ambiguity, and surface-form range-to-point collapse."

---

## 7. Residual-Map Update

The pragmatic monthly divergence class is now partially characterized. The residual map for Gan S0 after this analysis:

| Class | Count (GPT full-val) | Addressability | Next step |
| --- | --- | --- | --- |
| `other_semantic_mismatch` | 17 | Heterogeneous; needs per-record read | Separate micro-audit; not in C2/C3 scope |
| `pragmatic_match_monthly_divergence` | 16 | Partially fixable (see Section 5) | Window-priority + multi-type examples arm (post-C2) |
| `frequent_undercalled` | 7 | Fixable (highest-frequency selection) | Include in multi-type examples arm |
| `purist_bin_boundary_within_pragmatic` | 7 | Scorer boundary; low extraction fix value | Accept as residual; report in paper |
| `unknown_as_quantified_rate` | 3 | C2 arm targets this | C2 |
| `cluster_collapsed_to_rate` | 2 | Instruction + schema; separate cluster arm | Post-C2 if monthly still bottleneck |
| `unknown_as_high_rate` | 2 | C2 arm partially targets | C2 |
| `unknown_vs_seizure_free` | 2 | C2 arm targets | C2 |
| `frequent_overcalled` | 1 | Requires note-level read | Low priority |
| `unknown_vs_no_reference` | 1 | C2 arm targets | C2 |

---

## 8. Recommended Next Arms (Post-C2)

If C2 clears its cap-25 gate (≥ 84% monthly accuracy):

1. **Multi-type highest-frequency arm.** Preregister a prompt-only arm adding 3-5 explicit examples where a less-severe but more-frequent seizure type determines the gold label. Expected to address `frequent_undercalled` (7 records) and multi-type `pragmatic_match_monthly_divergence` (2-3 records).
2. **Window-priority policy arm.** Add a structured window-priority rule: prefer the clinic-visit reporting period, then fall back to the longest current-seizure window. Likely to address window-selection divergence (3-5 records).
3. **`other_semantic_mismatch` micro-audit.** Per-record read of all 17 `other_semantic_mismatch` cases to classify as: unknown-overuse, wrong-seizure-type, denominator error, or unclassifiable annotation gap. Only after C2, since C2 may absorb some of these.

These are not preregistered here. Each requires a separate hypothesis, slice, and cap-25 gate before full-validation spend.

---

## 9. Caveats

- All counts are from the synthetic validation split (`gan_2026_fixed_v1:validation`, 299 records). The Gan Real dataset (300 records) is inaccessible; transfer to real clinical notes is unverified.
- The Qwen 35b counts are estimated from a separate run with a different prompt version and are provided for triangulation only.
- `reference[0]` disagreements (difficulty signals) are not used here; all analysis uses `seizure_frequency_number[0]` as gold.
- Evidence support is diagnostic; the analysis above does not claim that deterministic candidates would correctly cover all count-underestimation cases.
- This analysis does not change scorer semantics, gold labels, or operational defaults.
