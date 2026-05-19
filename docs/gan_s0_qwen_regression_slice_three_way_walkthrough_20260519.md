# Gan S0 Qwen Regression Slice: Three-Way Error Walkthrough

End-to-end record-by-record comparison of three approaches on the same 14-record validation slice (`data/fixtures/gan_s0_qwen_error_regression_slice.json`). Goal: show what each change actually does, where it wins, and why it fails.

**Runs compared**

| Approach | Run ID | Prompt / program |
| --- | --- | --- |
| Direct v2.2 | `runs/gan_s0_qwen35b_direct_regression_slice_guardrails_20260519T151933Z` | `gan_frequency_s0_direct_single_pass` + guardrails v2.2 signature |
| Verify-repair v2.3 | `runs/gan_s0_qwen35b_verify_repair_regression_slice_guardrails_20260519T155438Z` | Extract (guardrails v2.2) → verify/repair (v2.3 infrequent rules) |
| LabeledFewShot + v2.2 | `runs/gan_s0_qwen35b_labeled_fewshot_regression_slice_guardrails_20260519T160348Z` | Same guardrails v2.2 signature + 4 synthesis-labeled train demos |

**Scorer:** `gan_frequency_deterministic_v1` (unchanged across all three). Monthly / Purist / Pragmatic are benchmark-facing; normalized exact is diagnostic.

---

## What each approach changes

### Direct v2.2 (baseline)

Single `dspy.Predict` call. The guardrails v2.2 signature text is the only instruction layer. It explicitly tells the model:

- Output quantified rates even when infrequent (count + window → `N per M unit`, not `unknown`).
- Distinguish `unknown` vs `no seizure frequency reference`.
- Use YTD denominators, full cluster format, `multiple per week`, etc.

**What it does not do:** second-pass correction, worked examples from train.

### Verify-repair v2.3

Two model calls per record:

1. **Extractor** — same direct module / guardrails v2.2 signature as baseline.
2. **Verifier** — sees `note_text`, `initial_label`, `initial_evidence`; returns `confirm` / `repair` / `abstain` plus `final_label`.

v2.3 adds verifier repair rules targeting **infrequent over-`unknown`**: if the extractor said `unknown` but the note has count + window, repair to a canonical rate.

**Risk:** verifier can over-repair correct extractions (YTD, clusters) or mis-repair qualitative `unknown` cases into wrong canonical labels.

### LabeledFewShot + v2.2

Same single-pass architecture as direct v2.2, but before prediction the module is compiled with **4 labeled demonstrations** sampled from 50 development-train records (`synthesis_exact_with_evidence` metric). Demos show gold label + locatable evidence quotes from synthesis train.

**What it changes:** in-context examples, not post-hoc repair. Compile cost is paid once per run (~5 min on this hardware).

---

## Headline numbers

| Metric | Direct v2.2 | Verify-repair v2.3 | LabeledFewShot v2.2 |
| --- | ---: | ---: | ---: |
| Records predicted | 14 | 14 | 14 |
| Schema-valid | **14/14 (100%)** | 13/14 (92.9%) | 13/14 (92.9%) |
| Normalized exact (valid only) | **10/14 (71.4%)** | 6/13 (46.2%) | 9/13 (69.2%) |
| Monthly (valid only) | **10/14 (71.4%)** | 6/13 (46.2%) | 9/13 (69.2%) |
| Evidence quote support | 100% | 100% | 100% |
| Original 10 targets exact | **10/10** | 5/10 | 9/10 |
| Infrequent 4 targets exact | 0/4 | **1/4** | 0/4 |
| Infrequent 4 off `unknown` | 0/4 | **4/4** | 0/4 |

**How to read this:** Direct v2.2 is strongest on the slice’s *original* regression targets but never quantifies the four infrequent gold labels. Verify-repair forces quantification on all four infrequent cases but only one is gold-correct, and it breaks five of the ten original targets. LabeledFewShot nearly matches direct on original targets but does not unlock infrequent quantification; one record abstains.

---

## Slice composition (why these 14 records)

| Group | Records | What we are testing |
| --- | --- | --- |
| Unknown vs no-reference | `gan_10509`, `gan_10751`, `gan_11221` | Clusters without counts, trigger-dependent infrequency, last-seizure date only |
| No clinical content | `gan_11733` | Admin letter → `no seizure frequency reference`, not null |
| Highest current rate | `gan_12130`, `gan_12823` | `multiple per week` vs undercount; YTD → monthly denominator |
| YTD denominator | `gan_12810` | “This year to date” → months since January, not `per year` |
| Cluster shape | `gan_10052`, `gan_10003`, `gan_10410` | Full cluster format; preserve `multiple per cluster` |
| Infrequent quantified | `gan_13123`, `gan_14485`, `gan_14881`, `gan_15306` | Gold is a rate; models tend to say `unknown` |

---

## Record-by-record walkthrough

Legend: ✓ exact normalized match · ✗ miss · — abstain/invalid

| Record | Gold | Direct v2.2 | VR v2.3 | LF v2.2 |
| --- | --- | --- | --- | --- |
| `gan_10509` | `unknown` | ✓ | ✓ confirm | ✓ |
| `gan_10751` | `unknown` | ✓ | ✗ repair→no-ref | — abstain |
| `gan_11221` | `unknown` | ✓ | ✗ repair→sz-free 4mo | ✓ |
| `gan_11733` | no-ref | ✓ | ✓ confirm | ✓ |
| `gan_12130` | multiple/week | ✓ | ✓ repair* | ✓ |
| `gan_12810` | 5 per 2 month | ✓ | ✓ confirm | ✓ |
| `gan_12823` | 9 per month | ✓ | ✗ repair→9/12mo | ✓ |
| `gan_10052` | 4 cluster/3mo, mult/cluster | ✓ | — invalid cluster | ✓ |
| `gan_10003` | 1 cluster/week, mult/cluster | ✓ | ✗ repair→1/week | ✓ |
| `gan_10410` | 1 cluster/week, 3-4/cluster | ✓ | ✓ confirm | ✓ |
| `gan_13123` | 1 per year | ✗ unknown | ✗ 1/3mo | ✗ unknown |
| `gan_14485` | 2 per 3 month | ✗ unknown | ✗ sz-free 1mo | ✗ unknown |
| `gan_14881` | 1 per month | ✗ unknown | ✗ no-ref | ✗ unknown |
| `gan_15306` | 2-3 per 15 month | ✗ unknown | ✓ repair | ✗ unknown |

\*Verifier marked `repair` but output stayed `multiple per week` (artifact bridge may have normalized).

---

### 1. `gan_10509` — unknown vs no-reference (clusters, no counts)

**Gold:** `unknown`  
**Failure mode:** Seizures discussed; cluster pattern without quantifiable count+window.

**Note (excerpt):** “…recent shift in her seizure pattern over the past three months, characterised by **clusters** arising after nights of curtailed sleep…”

| Approach | Prediction | Verdict |
| --- | --- | --- |
| Direct v2.2 | `unknown` | ✓ Correct. Model cites cluster language; no numeric rate. |
| Verify-repair | `unknown` (confirm) | ✓ Extractor and verifier agree: clusters without per-cluster or total count → not quantifiable. |
| LabeledFewShot | `unknown` | ✓ Same as direct; demos did not change this decision. |

**Takeaway:** All three handle qualitative cluster-without-counts correctly. This is the intended `unknown` case v2.2 guardrails describe.

---

### 2. `gan_10751` — unknown vs no-reference (trigger-dependent, “none in 4 months”)

**Gold:** `unknown`  
**Failure mode:** Infrequent at home, bursts around travel; no steady rate.

**Note (excerpt):** “Episodes remain **infrequent at home (none in the last 4 months)** but he describes **short bursts** occurring around long-distance travel…”

| Approach | Prediction | Verdict |
| --- | --- | --- |
| Direct v2.2 | `unknown` | ✓ Seizures discussed, no canonical ongoing rate. |
| Verify-repair | `no seizure frequency reference` (repair) | ✗ **Over-repair.** Verifier treats “none in 4 months” as grounds to reject `unknown`, then picks no-reference even though seizures are clearly discussed. |
| LabeledFewShot | **null** (abstain) | ✗ **Abstention.** Evidence snippet “none in the last 4 months” without a label — model refused to commit. |

**Why verify-repair fails:** v2.3 infrequent rules push *away* from `unknown` when any count/window language appears. “None in 4 months” looks quantifiable to the verifier, but gold annotators still chose `unknown` because the overall pattern is trigger-dependent, not a stable rate.

**Why LabeledFewShot fails:** Demos did not teach this edge; the model hedges to null on ambiguous temporal phrasing.

---

### 3. `gan_11221` — unknown vs no-reference (last seizure date only)

**Gold:** `unknown`  
**Clinic date:** 01 October 2020. **Last seizure:** 30/5/2020 (~4 months ago).

**Note (excerpt):** “Last seizure on 30/5/2020.” (Letter also discusses focal aware episodes but no ongoing quantified rate.)

| Approach | Prediction | Verdict |
| --- | --- | --- |
| Direct v2.2 | `unknown` | ✓ Last-event date without ongoing rate window. |
| Verify-repair | `seizure free for 4 month` (repair) | ✗ **Over-repair + invalid canonical use.** Verifier computes ~4 months since last event but emits `seizure free for 4 month` — gold policy uses `seizure free for N unit` only when N ≥ 6 months; shorter periods should stay `unknown` or a computed rate if events exist. |
| LabeledFewShot | `unknown` | ✓ Matches direct. |

**Takeaway:** Verify-repair’s temporal arithmetic misfires on short seizure-free gaps. This is the same failure family seen on GPT verify-repair v1 (over-repair to `unknown` / wrong canonical).

---

### 4. `gan_11733` — no clinical content (admin letter)

**Gold:** `no seizure frequency reference`

| Approach | Prediction | Verdict |
| --- | --- | --- |
| Direct v2.2 | `no seizure frequency reference` | ✓ v2.2 regression fix (was null on v2.1). |
| Verify-repair | confirm → same | ✓ |
| LabeledFewShot | same (null evidence) | ✓ |

**Takeaway:** All paths preserve the v2.2 win on admin/no-content letters.

---

### 5. `gan_12130` — highest current quantified frequency

**Gold:** `multiple per week`  
**Note:** GTC “3 events per year” vs focal sensory “**several times each week**”.

| Approach | Prediction | Verdict |
| --- | --- | --- |
| Direct v2.2 | `multiple per week` | ✓ Picks higher current rate; preserves vague multiplicity. |
| Verify-repair | `multiple per week` (repair flagged) | ✓ Final label correct; verifier unnecessarily “repaired” an already-valid label. |
| LabeledFewShot | `multiple per week` | ✓ |

**Takeaway:** Verify-repair adds noise (repair decision) without benefit here.

---

### 6. `gan_12810` — year-to-date denominator

**Gold:** `5 per 2 month`  
**Clinic date:** 24 February 2016. **Note:** “five … seizures documented **this year to date**”.

| Approach | Prediction | Verdict |
| --- | --- | --- |
| Direct v2.2 | `5 per 2 month` | ✓ YTD → Jan+Feb = 2 months. |
| Verify-repair | confirm → `5 per 2 month` | ✓ |
| LabeledFewShot | `5 per 2 month` | ✓ |

**Takeaway:** YTD policy is learned on direct and preserved under verify-repair when extractor is already correct.

---

### 7. `gan_12823` — highest current rate + YTD (paired with `gan_12810`)

**Gold:** `9 per month`  
**Clinic date:** 22 January 2017. **Note:** “nine … seizures documented **this year to date**”.

| Approach | Prediction | Verdict |
| --- | --- | --- |
| Direct v2.2 | `9 per month` | ✓ Correct YTD interpretation (9 events over 1 month elapsed in January). |
| Verify-repair | `9 per 12 month` (repair) | ✗ **Verifier YTD regression.** Verifier treats “year to date” as full 12-month window, undoing a correct extraction. Reason text: “nine… this year to date (a 12-month window)”. |
| LabeledFewShot | `9 per month` | ✓ Matches direct. |

**Takeaway:** This single repair explains a large slice score drop. The verifier’s temporal policy conflicts with the extractor’s (and gold’s) January YTD reading. **Do not promote verify-repair until YTD confirm rules protect correct extractor output.**

---

### 8. `gan_10052` — incomplete cluster label

**Gold:** `4 cluster per 3 month, multiple per cluster`  
**Note:** “confirm **4 clusters this quarter**”.

| Approach | Prediction | Verdict |
| --- | --- | --- |
| Direct v2.2 | full cluster label | ✓ |
| Verify-repair | `4 cluster per 3 month` only (repair) | ✗ **Invalid label** — stripped `, multiple per cluster`. Scorer rejects incomplete cluster. **Schema invalid on this record.** |
| LabeledFewShot | full cluster label | ✓ |

**Why verify-repair fails:** Verifier reason claims “multiple per cluster is not a standard Gan frequency unit” — wrong relative to project schema, which requires that second clause when per-cluster count is undocumented.

---

### 9. `gan_10003` — cluster multiplier preservation

**Gold:** `1 cluster per week, multiple per cluster`  
**Note:** “Weekly morning clusters reported; **number per cluster not documented**.”

| Approach | Prediction | Verdict |
| --- | --- | --- |
| Direct v2.2 | full cluster label | ✓ |
| Verify-repair | `1 per week` (repair) | ✗ **Cluster collapsed to rate.** Monthly/Purist miss; pragmatic still matches. Verifier explicitly rejects `multiple per cluster`. |
| LabeledFewShot | full cluster label | ✓ |

**Takeaway:** Verify-repair v2.3 anti-cluster-stripping rules from GPT v2 are not holding on local Qwen — same failure mode as Gemini verify-repair cap-25.

---

### 10. `gan_10410` — short seizure-free threshold + cluster

**Gold:** `1 cluster per week, 3 to 4 per cluster`  
**Note:** “now weekly, **3 or 4 per cluster**”.

| Approach | Prediction | Verdict |
| --- | --- | --- |
| All three | `1 cluster per week, 3 to 4 per cluster` | ✓ |

**Takeaway:** Complete cluster with documented per-cluster count — all paths succeed.

---

### 11. `gan_13123` — infrequent quantified (`1 per year`)

**Gold:** `1 per year`  
**Note:** “**no seizures for nearly a year** … then … **a tonic seizure three Saturdays ago**.”

| Approach | Prediction | Evidence focus | Verdict |
| --- | --- | --- | --- |
| Direct v2.2 | `unknown` | Long span + one recent event | ✗ Over-abstains to `unknown` despite quantifiable long-run rate. |
| Verify-repair | `1 per 3 month` (repair) | “three Saturdays ago” only | ✗ Off `unknown` but **wrong window** — anchors on recent event, ignores “nearly a year” + one breakthrough framing. Pragmatic-only win (infrequent bucket). |
| LabeledFewShot | `unknown` | Same as direct | ✗ |

**Gold reasoning (audit):** Annotators derived ~1 event per ~12 months from seizure-free year + single breakthrough — requires integrating two time spans, not just the latest event.

**Why text-only v2.2 fails:** Model sees conflicting narratives (long stability + single recent seizure) and defaults to `unknown` despite guardrails text saying infrequent rates should be quantified.

**Why verify-repair fails:** v2.3 rule “repair unknown when count+window present” fires on “one seizure three Saturdays ago” and picks an arbitrary 3-month denominator (likely confounding “three Saturdays” with “3 month”).

---

### 12. `gan_14485` — infrequent quantified (`2 per 3 month`)

**Gold:** `2 per 3 month`  
**Clinic date:** 14 August 2019.  
**Note:** Events in **April 2019** (Germany) and **July 2019** (Italy); “no further events since July 2019.”

| Approach | Prediction | Evidence cited | Verdict |
| --- | --- | --- | --- |
| Direct v2.2 | `unknown` | “no further events since returning to UK” | ✗ Misses historical pair of dated events. |
| Verify-repair | `seizure free for 1 month` | “no further events since July 2019” | ✗ Anchors on recent freedom (~1 month), ignores April+July pair that defines gold rate. |
| LabeledFewShot | `unknown` | Same as direct | ✗ |

**Gold reasoning:** Two events ~3 months apart in a defined observation window → `2 per 3 month`. Requires reading **past** event dates, not current “no further events” sentence alone.

**Why direct fails:** Extractor treats the most recent “no further events” clause as dominant and abstains to `unknown`.

**Why verify-repair fails:** Infrequent repair rule sees a short seizure-free interval and jumps to `seizure free for 1 month` (< 6 months, non-canonical in practice) instead of aggregating the April/July pair.

---

### 13. `gan_14881` — infrequent quantified (`1 per month`)

**Gold:** `1 per month`  
**Clinic date:** 21 March 2014. **Last episode:** 26 February 2014 (~3–4 weeks).

| Approach | Prediction | Verdict |
| --- | --- | --- |
| Direct v2.2 | `unknown` | ✗ Last-event date + “remained well since” → gold still wants a monthly rate from broader history. |
| Verify-repair | `no seizure frequency reference` (repair) | ✗ **Worst outcome** — worse than `unknown`. Verifier argues 3 weeks seizure-free < 6 months ⇒ no canonical rate ⇒ no-reference, ignoring earlier February episodes mentioned in note header. |
| LabeledFewShot | `unknown` | ✗ Same as direct. |

**Note context:** Header mentions “two episodes of dizziness” and absence episodes in February; gold `1 per month` is an annotator normalization not obvious from the single quoted span alone — a hard case.

---

### 14. `gan_15306` — infrequent quantified (`2 to 3 per 15 month`) — verify-repair success

**Gold:** `2 to 3 per 15 month`  
**Clinic date:** 11 March 2022. **Note:** “No further tonic-clonic seizures since **12/2020**, although **two to three single jerks remain**…”

| Approach | Prediction | Verdict |
| --- | --- | --- |
| Direct v2.2 | `unknown` | ✗ Model cites jerk count but will not attach 15-month window. |
| Verify-repair | `2 to 3 per 15 month` (repair) | ✓ **Only infrequent gold hit across all paths.** Verifier integrates Dec 2020 → Mar 2022 (~15 months) with “two to three” count. |
| LabeledFewShot | `unknown` | ✗ |

**Why this one works:** Count and window appear in **one contiguous sentence** — the easiest infrequent shape for both v2.3 repair rules and temporal arithmetic.

**Why direct still fails:** Even with explicit count+window in text, guardrails v2.2 alone did not force quantification on Qwen — model labels jerks as residual/qualitative and outputs `unknown`.

---

## Cross-cutting themes

### 1. Two different “infrequent” problems

| Subtype | Example | Direct v2.2 | Verify-repair v2.3 | LabeledFewShot |
| --- | --- | --- | --- | --- |
| **Easy:** count + window in one span | `gan_15306` | ✗ `unknown` | ✓ quantified | ✗ `unknown` |
| **Hard:** multi-span temporal inference | `gan_13123`, `gan_14485`, `gan_14881` | ✗ `unknown` | ✗ wrong repair | ✗ `unknown` |

Text-only guardrails and few-shot demos did not solve hard temporal inference. Verify-repair solves the easy case but hallucinates denominators on hard cases.

### 2. Verify-repair trade-off is asymmetric on this slice

```
Original 10 targets:  direct 10/10  →  verify-repair 5/10  (−5)
Infrequent 4 targets: direct 0/4   →  verify-repair 1/4 exact, 4/4 off-unknown
```

Repairs that move off `unknown` are not necessarily improvements — three infrequent repairs are benchmark-severe wrong labels.

### 3. Verifier failure modes (local Qwen)

| Failure | Records | Mechanism |
| --- | --- | --- |
| YTD denominator regression | `gan_12823` | Misread “year to date” as 12-month window |
| Cluster stripping | `gan_10052`, `gan_10003` | Drops `, multiple per cluster` or collapses to `1 per week` |
| unknown → no-reference | `gan_10751`, `gan_14881` | Mis-applies “no usable frequency” |
| Short seizure-free over-repair | `gan_11221`, `gan_14485` | Emits sub-6-month `seizure free for N unit` or wrong freedom label |
| Infrequent wrong window | `gan_13123` | Anchors on partial span (“three Saturdays”) |

Several verifier `reason` fields show **truncation at max_tokens=256** (visible in run logs) — reasoning cuts off mid-policy, which may contribute to inconsistent repairs.

### 4. LabeledFewShot is a stability tweak, not an infrequent unlock

- **9/10** on original targets vs direct **10/10** — one abstention on `gan_10751`.
- **0/4** infrequent — demos did not transfer temporal aggregation patterns.
- Compile adds ~5 min; prediction latency similar to direct.

Demos prioritize exact label + evidence from train; infrequent quantified-over-unknown cases are underrepresented or not analogous in the 4 sampled examples.

### 5. Evidence is not the bottleneck

All three runs: **100% evidence quote support** on valid predictions. Failures are **semantic / temporal**, not unsupported quotes.

---

## What each path is actually doing (summary)

| Question | Direct v2.2 | Verify-repair v2.3 | LabeledFewShot v2.2 |
| --- | --- | --- | --- |
| Fixes admin no-content null? | Yes (`gan_11733`) | Yes | Yes |
| Fixes YTD / cluster / multiple-week? | Yes (10/10 original) | **No** — breaks 5/10 | Mostly yes (9/10) |
| Fixes infrequent over-unknown? | No (0/4) | Partially (1/4 exact; 4/4 quantified) | No (0/4) |
| Risk profile | Under-quantifies hard temporal cases | Over-repairs; invalid clusters | Abstention on ambiguity |
| Cost | 1× model call | 2× model call | 1× call + compile |

---

## Recommended reading order for debugging

1. **Verify-repair regressions first:** `gan_12823`, `gan_10052`, `gan_10003`, `gan_10751`, `gan_11221` — these explain most of the 5/10 original-target drop.
2. **Infrequent successes/failures:** `gan_15306` (success template) vs `gan_13123` / `gan_14485` (multi-span inference).
3. **Stable core:** `gan_10509`, `gan_11733`, `gan_12810`, `gan_12130`, `gan_10410` — unchanged wins across paths.

---

## Implications for next work

1. **Do not run cap-25** on current verify-repair v2.3 — slice monthly 46.2% vs direct 71.4%.
2. **Verify-repair needs confirm-first guardrails:** if extractor label scores valid and note-supported, confirm without repair (especially YTD and full cluster labels).
3. **Infrequent repair needs span discipline:** require count **and** explicit/shared window in evidence before repairing off `unknown`; penalize repairs that ignore earlier note spans.
4. **LabeledFewShot alone** will not fix infrequent cases without demos that show multi-span temporal aggregation — or a hybrid (few-shot extractor + constrained verifier).
5. **Consider raising verifier `max_tokens`** on local Qwen — truncation warnings appeared on 5/14 verify-repair records.

---

## Artifact links

- Direct analysis: `docs/gan_s0_qwen35b_regression_slice_inspection_20260519.md`
- Verify-repair analysis: `docs/gan_s0_qwen35b_verify_repair_regression_slice_guardrails_error_analysis.md`
- LabeledFewShot analysis: `docs/gan_s0_qwen35b_labeled_fewshot_regression_slice_guardrails_error_analysis.md`
- Kanban status: `docs/kanban_plan.md`
