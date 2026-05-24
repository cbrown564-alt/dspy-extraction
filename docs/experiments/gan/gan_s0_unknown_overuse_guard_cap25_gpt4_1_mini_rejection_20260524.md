# Gan S0 C2 Unknown-Overuse Guard — Cap-25 Arm Rejection Report

Date: 2026-05-24  
Arm: `gan_s0_unknown_overuse_guard_cap25_gpt4_1_mini`  
Run: `runs/gan_s0_unknown_overuse_guard_cap25_gpt4_1_mini_20260524T201746Z`  
Gate: cap-25 monthly accuracy ≥ 84%  
Outcome: **REJECTED** — gate not met

---

## 1. Results

| Metric | C2 (v1.5 guard) | Baseline v1.4 | Delta |
| --- | ---: | ---: | ---: |
| Monthly accuracy | **16.0%** | ~80.6%† | −64.6 pp |
| Purist category | 40.0% | ~88% | −48 pp |
| Pragmatic category | 40.0% | ~90% | −50 pp |
| Normalized label | 16.0% | — | — |

†Baseline is from full-validation run `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z`; not directly comparable on this enriched slice.

Gate threshold (84% monthly on cap-25 slice) **not met**. Arm is rejected. No full-validation run will proceed.

---

## 2. Failure Analysis

The v1.5 unknown-overuse guard addendum caused a **systematic regression** rather than targeted repair.

### Pattern A: Correct `unknown` gold labels over-corrected to specific rates (5/25 records)

The addendum's "quantified-window preservation" rule (Rule 1) triggered even for records where `unknown` was the correct gold label:

| Record | Gold | Predicted | Class |
| --- | --- | --- | --- |
| `gan_14081` | `unknown` | `2 to 3 per month` | unknown_as_quantified_rate → now over-corrected opposite direction |
| `gan_14146` | `unknown` | `3 per 2 month` | unknown_as_high_rate → now over-corrected |
| `gan_6077` | `unknown` | `1 per 8 month` | unknown_as_quantified_rate → persists |
| `gan_11216` | `unknown` | `seizure free for 4 month` | unknown_vs_seizure_free → persists |

These are cases where the model had been correctly emitting `unknown` in the baseline, but the new addendum text ("preserve the rate label even if…") is over-activating on ambiguous note spans.

### Pattern B: Records where gold=specific rate still incorrectly emitting `unknown` (7/25 records)

The addendum failed to fix the core problem — `other_semantic_mismatch` records where gold is a concrete rate but baseline emits `unknown`:

| Record | Gold | Predicted | Prior failure class |
| --- | --- | --- | --- |
| `gan_3623` | `7 per week` | `unknown` | other_semantic_mismatch |
| `gan_3630` | `7 per week` | `unknown` | other_semantic_mismatch |
| `gan_4602` | `1 per 7 to 10 day` | `unknown` | other_semantic_mismatch |
| `gan_4709` | `multiple per day` | `unknown` | other_semantic_mismatch |
| `gan_6094` | `3 per month` | `unknown` | other_semantic_mismatch |
| `gan_16041` | `9 per 3 month` | `unknown` | other_semantic_mismatch |
| `gan_16780` | `3 per 7 month` | `unknown` | other_semantic_mismatch |

Pattern B persists for the majority of the target failures. The addendum's candidate-override discipline (Rule 4) did not resolve them because these records have **no deterministic candidates** — the builder already fails to produce candidates for them.

### Root cause diagnosis

The v1.5 prompt has **two competing design flaws**:

1. **Rule 1 (quantified-window preservation) is too aggressive**: The rule is instructing the model to always extract a rate when any window-count pattern is visible, but some of those window-count patterns are genuinely ambiguous (e.g. historical seizure windows, ictal patterns without clear recurrence). The rule causes the model to hallucinate specific rates where `unknown` is correct.

2. **Rules 3 and 4 (no-reference vs unknown boundary; candidate-override discipline) fail for the `other_semantic_mismatch` class** because these records have no deterministic candidates. The addendum explicitly says "If a deterministic temporal candidate is present…" — when no candidate is present, these records fall through unchanged.

---

## 3. Decision

**C2 arm is rejected.** The v1.5 unknown-overuse guard prompt produces a net regression of ~65 pp on monthly accuracy and is not promotable.

No further prompt variants of this design should be run without resolving the two root causes above.

---

## 4. Follow-on Recommendations

Two root causes must be addressed separately before retrying:

### RC1: Rule 1 over-extraction (quantified-window preservation)

**Problem**: Injecting a strong quantified-window rule causes the model to hallucinate specific rates for ambiguous notes.

**Options**:
1. Remove Rule 1 entirely and rely on the existing v1.4 error taxonomy. 
2. Soften Rule 1 to require "explicit calendar-window phrasing" (e.g. "N seizures between [DATE] and [DATE]") rather than any count+window pattern.
3. Add a hedging clause: "Only preserve the rate if the note's phrasing is specific and unambiguous; when in doubt, use `unknown`."

Recommendation: **Option 2 or 3** — add an explicit precision guard that prevents the rule from triggering on ambiguous note text.

### RC2: `other_semantic_mismatch` records still failing (no deterministic candidates)

**Problem**: For records where the builder produces no candidates, Rule 4 is inert. These records require the extractor to derive the rate from raw note text without candidate scaffolding.

**Options**:
1. Fix the deterministic builder to produce candidates for these records (builder extension — highest upside).
2. Add specific few-shot examples for common `other_semantic_mismatch` patterns.
3. Target them separately with a dedicated no-candidate-path fallback in the prompt.

Recommendation: **Option 1** is the highest-value fix; it benefits the entire pipeline, not just these 7 records. Option 2 is a quicker interim patch.

---

## 5. Kanban Update

- C2 card: → **DONE (rejected, no gate passage)**
- Recommended next pull: Either revisit C2 with a corrected Rule 1 (RC1 fix), or proceed to the builder extension (RC2 fix) which would benefit both this arm and the general pipeline.
- No new prompts should run on the enriched cap-25 slice until RC1 is resolved.
