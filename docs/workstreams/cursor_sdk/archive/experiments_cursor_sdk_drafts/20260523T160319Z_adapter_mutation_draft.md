# Adapter and Prompt Mutation Draft

**Status:** Review-only artifact. No source edits. Not benchmark evidence unless tied to primary run artifacts.

**Decision scope:** `operational` / `arm` synthesis and `open` mechanism follow-ups. Does not close mechanism, change scorer semantics, or promote arms without primary run comparison.

---

## Sources Read

| Path | Role |
| --- | --- |
| `docs/experiments/gan/gan_s0_qwen35b_20260522_error_taxonomy.md` | Qwen 35B full-validation error taxonomy (A–H), instruction gaps, pipeline flaws |
| `docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md` | GPT slice arm outcomes; H6 candidate-recall bottleneck; next-pull priorities |
| `src/clinical_extraction/gan/temporal_candidates.py` | Current deterministic builder surface (`build_temporal_frequency_candidates_from_note`, ~30 helpers) |
| `docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md` | Post-G13 no-model coverage audit (23/25 on enriched slice) |
| `docs/experiments/gan/gan_s0_candidate_builder_gap_preregistration_20260523.md` | G12 inclusion/exclusion rules for builder families |
| `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md` | G15 GPT slice adjudication lift after builder expansion |
| `configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice.json` | Held-fixed v1.4 prompt + `gan_s0_candidate_builder_gap_v1` implementation variant |
| `src/clinical_extraction/programs/gan_frequency_s0.py` | v1.4 error-taxonomy policy addendum text (`GAN_FREQUENCY_S0_ERROR_TAXONOMY_POLICY_ADDENDUM`) |
| `tests/test_gan_temporal_candidates.py` | Regression and slice-coverage tests for builders |

**Missing context flagged:** Exact note text for `gan_13574` / `gan_13598` was not read in this pass (only audit metadata in `docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.json`). Regex templates below are pattern hypotheses pending note inspection.

---

## Identified Bottlenecks

### Facts (from primary artifacts)

| Bottleneck | Evidence | Scope |
| --- | --- | --- |
| **Unknown overuse dominates Pragmatic misses** | 47/63 Qwen Pragmatic misses are gold frequent/infrequent/no-seizure-information predicted as `unknown` (`docs/experiments/gan/gan_s0_qwen35b_20260522_error_taxonomy.md`, §3) | `mechanism` — Qwen full validation |
| **Low full-validation candidate coverage (pre-G13)** | Only 42/298 valid Qwen predictions had any deterministic candidate (`docs/experiments/gan/gan_s0_qwen35b_20260522_error_taxonomy.md`, §Pipeline Flaws #1) | `operational` baseline |
| **Candidate override without constraint** | 9 Qwen Pragmatic misses had gold in candidate list but model still wrong (`docs/experiments/gan/gan_s0_qwen35b_20260522_error_taxonomy.md`, §Pipeline Flaws #2) | `open` adjudication |
| **Pre-G13 slice recall was 5/25** | Synthesis table: gold in candidates by failure family (`docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md`, §Error Analysis) | `arm` — superseded baseline |
| **Post-G13 slice recall is 23/25** | Audit summary (`docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md`) | `operational` — current builder state |
| **Remaining slice gap: seizure-free multi-year** | `gan_13574`, `gan_13598`: gold `seizure free for multiple year`, no candidate (`docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md`) | `blocked` pending policy boundary |
| **Builder lift translated to adjudication on slice** | v1.4 control 36% monthly / 56% pragmatic → builder-gap v1 92% / 96% on same 25 records (`docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md`) | `arm` — mechanism signal, not full-validation claim |
| **Residual adjudication with candidates present** | `gan_15168` → `unknown` despite `multiple per 15 month` candidate; `gan_15193` → `1 per 13 month` vs gold `multiple per 13 month` (`docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md`, §Residual Errors) | `open` — vague-multiple policy |
| **v1.4 prompt-only arms did not beat themselves** | G7 verifier, G9 examples, G6b selector all rejected for promotion (`docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md`, §Arm Outcomes) | `arm` — tested, not promoted |

### Interpretation (uncertainty explicit)

1. **Long-window quantified counts, cluster spacing + per-cluster count, and simple frequent rates** were the binding pre-G13 bottleneck on the enriched slice. Many corresponding builders now exist in `temporal_candidates.py` (e.g. `_breakthrough_after_months_seizure_free`, `_cluster_free_days_then_cluster`, `_simple_cluster_interval_as_rate`, `_vague_since_month_year`) and are covered by tests such as `test_temporal_candidates_represent_breakthrough_after_explicit_month_window` and `test_temporal_candidates_represent_explicit_cluster_spacing_and_count` (`tests/test_gan_temporal_candidates.py`).

2. **Seizure-free duration surface** (`seizure free for multiple year/month`) remains the main *deterministic* gap on the slice and a broader full-validation gap (many seizure-free records with no candidate in `docs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_error_analysis.md`). Preregistration explicitly excluded emitting these until policy boundary is resolved (`docs/experiments/gan/gan_s0_candidate_builder_gap_preregistration_20260523.md`, §Excluded Patterns).

3. **Counted window + stability phrase** (failure mode B in taxonomy) is partially addressed by existing builders (`_two_dated_events_window`, `_following_week_events_monthly_rate`, `_diary_named_month_event_counts_to_clinic`) and v1.4 prompt text (`src/clinical_extraction/programs/gan_frequency_s0.py`, lines 743–746). Residual risk: adjudicator still free to ignore candidates (Qwen override cases; GPT residual `gan_15168`).

4. **Cluster/rate confusion** (failure mode F) and **highest-current-frequency selection** (failure mode G) are primarily prompt/adjudication problems once candidates exist; builders alone cannot fix `gan_16938`-class errors without concurrent-type builders or stricter selection policy.

5. **Unanchored denominator → unknown** (failure mode D) has partial builder support via `_unanchored_count_with_latest_date_unknown`; extending “since treatment start” / “inter-seizure interval” families may improve full-validation recall but needs note-grounded patterns, not clinical plausibility (preregistration exclusion).

---

## Draft Python Code Templates

**Convention:** Proposed additions to `src/clinical_extraction/gan/temporal_candidates.py`. Register in `build_temporal_frequency_candidates_from_note`. Templates are illustrative; do not treat as implemented unless covered by tests.

**Already implemented (do not re-add):** Long-window breakthrough (`gan_13058` → `2 per 7 month` via `_seizure_free_months_then_breakthrough_count`), cluster spacing + count (`gan_15442` via `_cluster_free_days_then_cluster`), simple rate not cluster (`gan_16529` via `_simple_cluster_interval_as_rate`), vague multiple with anchor (`gan_15168`/`gan_15193` via `_vague_since_month_year` / `_last_convulsive_with_occasional_clusters`). Source: `tests/test_gan_temporal_candidates.py` and `docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md`.

---

### 1. Seizure-free multi-year / multi-month (policy-boundary family)

**Targets:** `gan_13574`, `gan_13598` (slice); broader full-validation seizure-free rows in error analysis.

**Prerequisite (`blocked`):** Confirm Gan annotation policy maps “multiple year(s)” remission to exact surface `seizure free for multiple year`, not `seizure free for N year` with inferred N. Preregistration requires this before code (`docs/experiments/gan/gan_s0_candidate_builder_gap_preregistration_20260523.md`).

```python
def _seizure_free_for_multiple_year(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    """Emit canonical multi-year seizure-free label when duration is explicitly vague-multi-year.

    Policy boundary: only match phrases that map to gold surface
    'seizure free for multiple year' — do NOT infer numeric year count.
    """
    match = re.search(
        r"(?P<evidence>[^.]*\b(?:has been |remains |is )?"
        r"seizure[- ]free(?: for)?(?: the past)? "
        r"(?:for )?(?:multiple|several|a number of) years?[^.]*)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label="seizure free for multiple year",
            event_count="0",
            window_count="multiple",
            window_unit="year",
            evidence_text=evidence,
            derivation=(
                "explicit multi-year seizure freedom; emit policy canonical "
                "'seizure free for multiple year' without inferring N"
            ),
        )
    ]


def _seizure_free_for_multiple_month(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    """Mirror builder for 'seizure free for multiple month' full-validation residuals."""
    match = re.search(
        r"(?P<evidence>[^.]*\bseizure[- ]free(?: for)? "
        r"(?:multiple|several) months?[^.]*)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label="seizure free for multiple month",
            event_count="0",
            window_count="multiple",
            window_unit="month",
            evidence_text=evidence,
            derivation="explicit multi-month seizure freedom with policy surface form",
        )
    ]
```

---

### 2. Vague “from time to time” with explicit since-anchor (residual slice adjudication)

**Targets:** `gan_15168` (`multiple per 15 month`), `gan_15193` (`multiple per 13 month`). Candidate may already exist via `_vague_since_month_year`; builder-gap v1 still mispredicted (`docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md`). Proposed builder tightens evidence span to the vague-frequency clause + since-anchor (may dedupe with existing helper).

```python
def _vague_from_time_to_time_since_generalised_seizure(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    """Vague ongoing events ('from time to time') anchored by 'since MM-YYYY' month window."""
    match = re.search(
        r"(?P<evidence>[^.]*no generalised seizures since "
        r"(?P<month>\d{1,2})\s*-\s*(?P<year>\d{4}), though continues to experience "
        r"(?P<qualifier>brief (?:jumps|absence)) from time to time[^.]*)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    clinic_date = _clinic_date(note_text)
    if clinic_date is None:
        return []

    window_months = _months_between_month_year(
        clinic_date, int(match.group("month")), int(match.group("year"))
    )
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=f"multiple per {window_months} month",
            event_count="multiple",
            window_count=str(window_months),
            window_unit="month",
            evidence_text=evidence,
            derivation=(
                "vague 'from time to time' count with elapsed-month denominator "
                "since last generalised seizure anchor"
            ),
        )
    ]
```

---

### 3. Long-window quantified counts — generic elapsed-month span (full-validation extension)

**Targets:** Taxonomy failure mode E (`gan_12871`, `gan_16772`, etc.) and synthesis examples `5 per 13 month`, `6 per 7 month` where note gives count + first/last event dates or “since review” span.

```python
def _counted_events_over_elapsed_month_span(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    """N events between explicit start anchor and clinic/review date."""
    match = re.search(
        rf"(?P<evidence>[^.]*(?P<count>one|two|three|four|five|six|seven|eight|nine|ten|\d+(?:\s+to\s+\d+)?|\d+\s*-\s*\d+)"
        rf"\s+(?:seizures|events)[^.]*since "
        rf"(?:(?P<month>\d{{1,2}})[/-](?P<year>\d{{4}})|last review)[^.]*\.)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    clinic_date = _clinic_date(note_text)
    if clinic_date is None:
        return []

    if match.group("month"):
        window_months = _months_between_month_year(
            clinic_date, int(match.group("month")), int(match.group("year"))
        )
    else:
        # Missing context: define 'last review' anchor rule from label audit before shipping
        return []

    event_count = _count_range_text_to_label(match.group("count"))
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=_simple_rate_label(event_count, window_months, "month"),
            event_count=event_count,
            window_count=str(window_months),
            window_unit="month",
            evidence_text=evidence,
            derivation="explicit event count over elapsed months since textual anchor",
        )
    ]
```

---

### 4. Cluster spacing unknown, per-cluster count known (taxonomy D/F)

**Partially implemented:** `_vague_grouped_spells_unknown`. Extend for “grouped on days when they occur” without weekly spacing.

```python
def _unknown_cluster_spacing_with_per_cluster_range(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    """When per-cluster count is stated but cluster cadence is not (gold: unknown, N per cluster)."""
    match = re.search(
        r"(?P<evidence>[^.]*(?P<low>four to six|4 to 6|\d+\s+to\s+\d+|\d+)"
        r"[^.]*grouped together on days when they occur[^.]*)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []
    per_cluster = _count_range_text_to_label(match.group("low"))
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=f"unknown, {per_cluster} per cluster",
            event_count=per_cluster,
            window_count="",
            window_unit="",
            evidence_text=evidence,
            derivation="per-cluster count without benchmark-derivable cluster spacing",
        )
    ]
```

---

### 5. Inter-seizure interval → simple rate (taxonomy next experiment #3)

```python
def _inter_seizure_interval_as_simple_rate(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    """'Seizures every N days/weeks' without per-cluster multiplier → simple rate, not cluster label."""
    match = re.search(
        r"(?P<evidence>[^.]*(?:seizures|events) (?:occur|happening|reported) "
        r"(?:every|approximately every) (?P<n>\d+) (?P<unit>days?|weeks?)[^.]*\.)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []
    n = match.group("n")
    unit = match.group("unit").rstrip("s")  # normalize day/week
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=f"1 per {n} {unit}",
            event_count="1",
            window_count=n,
            window_unit=unit,
            evidence_text=evidence,
            derivation="inter-event interval treated as simple benchmark rate (not cluster form)",
        )
    ]
```

---

### 6. Concurrent seizure-type frequency selection hint (taxonomy G)

```python
def _concurrent_daily_type_frequency_candidates(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    """Surface explicit daily rates for non-GTC types when note also mentions lower GTC frequency."""
    patterns = (
        r"(?P<evidence>[^.]*\bdaily absences[^.]*\.)",
        r"(?P<evidence>[^.]*\bdaily myoclonic (?:jerks|events)[^.]*\.)",
        r"(?P<evidence>[^.]*\bdaily drop attacks[^.]*\.)",
    )
    candidates: list[GanTemporalFrequencyCandidate] = []
    for pattern in patterns:
        match = re.search(pattern, note_text, flags=re.IGNORECASE)
        if match is None:
            continue
        evidence = match.group("evidence").strip()
        candidates.append(
            GanTemporalFrequencyCandidate(
                canonical_label="1 per day",
                event_count="1",
                window_count="1",
                window_unit="day",
                evidence_text=evidence,
                derivation=(
                    "explicit daily concurrent seizure-type rate; adjudicator should "
                    "prefer over lower-frequency GTC mention when both current"
                ),
            )
        )
    return candidates
```

**Note:** `_daily_seizure_type_frequency` already covers one pattern (`tests/test_gan_temporal_candidates.py`, `test_temporal_candidates_represent_daily_seizure_type_for_concurrent_priority`). Template above is an extension sketch only.

---

## Draft Prompt Mutations

Base config shape: `configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice.json` — hold model, scorer, slice, and `prompt_version` fixed unless registering a new prompt arm.

Proposed new prompt version (hypothetical): `gan_frequency_s0_temporal_candidates_single_pass_v1_7_candidate_selection_discipline` as addendum atop v1.4 (`GAN_FREQUENCY_S0_ERROR_TAXONOMY_POLICY_ADDENDUM` in `src/clinical_extraction/programs/gan_frequency_s0.py`).

### A. Candidate selection discipline (addresses taxonomy A, pipeline flaw #2)

**Problem:** Gold-equivalent candidate present but model outputs `unknown` (`gan_14792`–`gan_14973` under v1.4 control; Qwen 9 override cases in taxonomy).

**Proposed addendum text:**

```
Candidate selection discipline (v1.7):
- When temporal_candidates includes one or more labels with explicit event_count
  and window_count/window_unit (or full cluster spacing + per-cluster count),
  you MUST either:
  (a) select the best-matching candidate canonical_label, OR
  (b) output unknown / seizure-free / no-reference ONLY with evidence_text
      quoting text that satisfies Gan policy for that override category.
- A later phrase alone ("no further events", "stable", "well since") is NOT
  sufficient to override a counted-window candidate unless the note states
  seizure freedom >= 6 months with explicit duration.
- Override reasons (choose one if not selecting a candidate):
  higher_current_frequency | qualifying_seizure_free | unanchored_denominator |
  trigger_conditioned_unknown | no_clinical_frequency_content
```

**Config mutation (illustrative):**

```json
{
  "controls": {
    "abstention_policy": "require_override_reason_when_candidates_present",
    "context_policy": "full_note_plus_deterministic_temporal_candidates"
  },
  "prompt_version": "gan_frequency_s0_temporal_candidates_single_pass_v1_7_candidate_selection_discipline"
}
```

**Scope:** `open` arm — requires preregistered A/B vs v1.4 + builder-gap v1; G7 showed verifier-only discipline tied v1.4 without better candidates (`docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md`).

---

### B. Vague-multiple adjudication (residual `gan_15168`, `gan_15193`)

**Problem:** Candidate `multiple per N month` present; model abstains or collapses to `1 per N month` (`docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md`).

**Proposed addendum:**

```
Vague-multiple policy:
- Phrases like "from time to time", "occasional", "brief jumps/absences"
  WITH a since-anchor or elapsed review window → output "multiple per N month"
  (not unknown, not "1 per N month") when that is the listed candidate.
- Do NOT treat vague frequency as zero events or as a single countable event
  unless the note gives an explicit count of 1.
```

**Optional targeted example (single-family, not mixed pack — aligns with synthesis open cell):**

```
note: "...no generalised seizures since 03-2023, though continues to experience
brief jumps from time to time."
output: "multiple per 15 month"
evidence_text: "continues to experience brief jumps from time to time"
```

---

### C. Seizure-free “multiple year/month” surface (taxonomy C; slice `gan_13574`, `gan_13598`)

**Problem:** Qwen predicted `unknown` on seizure-free gold; GPT slice gets category right but wrong normalized surface (`seizure free for year` vs `seizure free for multiple year`).

**Proposed addendum:**

```
Seizure-free surface forms:
- When remission duration is stated as "multiple years" / "several years" /
  "a number of years", output exactly: "seizure free for multiple year".
- When remission is "multiple months" without a numeric count, output:
  "seizure free for multiple month".
- Do NOT collapse to "seizure free for 1 year" or numeric N unless N is
  explicitly stated in the note.
```

**Coupling:** Prompt-only fix may suffice for surface fidelity; deterministic candidate (#1 above) reinforces when builders are unblocked.

---

### D. Stability-after-count guard (taxonomy B)

v1.4 already states this (`src/clinical_extraction/programs/gan_frequency_s0.py`, lines 743–746). **Mutation:** elevate to hard rule + negative example:

```
Counterexample (do NOT output unknown):
"He had two seizures in April and July; no further events reported."
→ "2 per 3 month" (counted window preserved; stability phrase does not erase denominator)
```

---

### E. Cluster vs rate guard (taxonomy F; `gan_16529` regression under v1.4)

**Proposed addendum:**

```
Do not append ", multiple per cluster" or cluster spacing to a simple rate
when the note describes a fixed inter-event interval (e.g. "every 5 days")
without grouped cluster language. Prefer "1 per 5 day" over cluster syntax.
```

Aligns with invalid prediction `gan_5866` grammar error in taxonomy §2.

---

### F. Config-only experiment arms (no prompt text change)

| Variant | Change | Hypothesis | Decision scope |
| --- | --- | --- | --- |
| `gan_s0_candidate_builder_gap_v1` + v1.4 | Already preregistered (`configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice.json`) | Recall-limited | `arm` — slice passed (`docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md`) |
| + `constrained_verifier` | `gan_s0_candidate_builder_gap_v1_constrained_verifier_gpt4_1_mini_full_validation.json` | Safe confirmation, low lift when candidates incomplete | `arm` — `stale_check` vs full-validation error analysis |
| v1.7 selection discipline | New prompt + same builders | Fix residual override/abstention | `open` — not yet tested |

---

## Verification Checklist

### No-model gates (required before any prompt arm)

| Step | Command / artifact | Pass criterion | Source |
| --- | --- | --- | --- |
| Unit tests | `uv run pytest tests/test_gan_temporal_candidates.py` | All pass | `docs/experiments/gan/gan_s0_candidate_builder_gap_preregistration_20260523.md` |
| Primitive validation | `uv run python scripts/validate_primitives.py --errors-only` | No errors | Same |
| Gap audit | `uv run python scripts/audit_gan_candidate_builder_gap.py` | Coverage report updated | `scripts/audit_gan_candidate_builder_gap.py` |
| Enriched slice coverage | `test_enriched_gap_slice_gold_label_coverage_improves` | `covered >= 23` (raise to 25 if seizure-free builders unblocked) | `tests/test_gan_temporal_candidates.py` |
| Residual slice regression | `test_residual_slice_gold_label_coverage_improves` | `covered >= 24` | Same |
| Regression anchors | Tests for `gan_13123`, `gan_14250`, `gan_14485`, `gan_14881`, `gan_15302` | Gold labels remain in candidate set | Preregistration §Regression Cases |

### Per new builder family (add before merge)

| Family | Test record(s) | Assert |
| --- | --- | --- |
| Seizure-free multi-year | `gan_13574`, `gan_13598` | `"seizure free for multiple year" in labels` **after policy sign-off** |
| Seizure-free multi-month | Sample from full-validation error analysis | `"seizure free for multiple month" in labels` |
| Vague-multiple since-anchor | `gan_15168`, `gan_15193` | `"multiple per 15 month"`, `"multiple per 13 month"` |
| Long-window since-review | `gan_15127`, `gan_16750` | Already covered; must not regress |
| Cluster spacing + count | `gan_15442` | `"1 cluster per 4 day, 2 per cluster"` |
| Simple rate not cluster | `gan_16529` | `"1 per 5 day"` present; no erroneous cluster label |
| Unanchored → unknown | `gan_10618` (fixture) | Candidate starts with `unknown,` | `test_temporal_candidates_emit_unknown_for_vague_grouped_spells_without_spacing` |
| Concurrent daily priority | `gan_12562`, `gan_12667` | `"1 per day"` in labels | Existing test |

### Model gates (only after no-model pass)

| Step | Config | Compare | Metrics | Scope |
| --- | --- | --- | --- | --- |
| GPT enriched slice | `configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice.json` vs v1.4 control | Same 25 `record_ids` | Monthly, Purist, Pragmatic, normalized-label | Done — primary: `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md` |
| GPT full validation | `configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation.json` | F0 operational default | Same + candidate coverage audit | `open` — check `docs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_error_analysis.md` |
| Prompt v1.7 arm | New config mirroring slice JSON | v1.4 + builder-gap v1 | Residuals: `gan_15168`, `gan_15193`; override rate when gold in candidates | `open` |
| Qwen transfer | Blocked | — | — | `blocked` per synthesis until GPT full validation confirms (`docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md`, §Next Pull) |

### Non-regression guards

- Do **not** change `src/clinical_extraction/gan/frequency.py` or `scoring.py` (preregistration exclusion).
- Do **not** treat slice lift as full-validation performance (caveats in taxonomy and slice inspection).
- Evidence support remains diagnostic; do not use 100% quote support as semantic correctness (`docs/experiments/gan/gan_s0_qwen35b_20260522_error_taxonomy.md`, §H).
- Separately track **normalized-label** vs **Pragmatic category** for seizure-free surface mismatches (`gan_13574`, `gan_13598` are category-correct but surface-wrong in slice inspection).

---

## Summary Table: Failure Mode → Proposed Lever

| Failure mode | Primary lever | Status |
| --- | --- | --- |
| Long-window quantified counts | Deterministic builders + elapsed-month helpers | **Largely implemented** (G13); extend for full-validation patterns |
| Cluster spacing + per-cluster count | `_cluster_free_days_then_cluster` etc. | **Implemented** for slice targets |
| Seizure-free multi-year/month | Policy boundary + builder #1 + prompt §C | **Blocked** on slice (0/2 coverage) |
| Counted window + no further events | Existing builders + v1.4 prompt §B/D | **Partial** — Qwen override remains |
| Unknown overuse with candidate present | Prompt §A selection discipline | **Open** — not tested as dedicated arm |
| Vague multiple | Builder #2 + prompt §B | Candidate exists; **adjudication residual** on slice |
| Cluster/rate confusion | Prompt §E + `_simple_cluster_interval_as_rate` | Builder helps; prompt prevents re-clustering |
| Highest concurrent frequency | `_daily_seizure_type_frequency` + prompt §G examples | **Partial** |
| Unanchored denominator | `_unanchored_count_with_latest_date_unknown` | **Partial** — extend since-treatment patterns |
| Invalid cluster suffix on plain rate | Prompt §E + artifact grammar repair (taxonomy §2) | Lower priority for category metrics |

---

**Uncertainty / next inspection:** Before implementing seizure-free builders, read note text for `gan_13574` and `gan_13598` from Gan dataset loader or run artifacts and confirm phrase-level match to `seizure free for multiple year`. Before generic `_counted_events_over_elapsed_month_span`, define “last review” anchor rule against `docs/datasets/gan/gan_2026_label_audit.md` (not read in this pass).