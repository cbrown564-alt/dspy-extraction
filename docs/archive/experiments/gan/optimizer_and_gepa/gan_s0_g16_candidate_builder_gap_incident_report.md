# Incident Report: G16 Candidate-Builder Gap Validation & G13 Code Loss

**Date:** 2026-05-23  
**Status:** Incident Report & Action Plan  
**Target:** `docs/experiments/gan/gan_s0_g16_candidate_builder_gap_incident_report.md`  
**Scope:** Gan S0 Seizure-Frequency Extraction Pipeline  

---

## 1. Executive Summary

During the execution and verification of the G16 Candidate-Builder Gap Validation, two major failures occurred:
1. **Candidate-Emission Silent Failure:** The G16 validation run (variant `gan_s0_candidate_builder_gap_v1`) generated empty temporal frequency candidates during evaluation. This dropped the pragmatic slice accuracy from **92.0%** to **32.0%** because the adjudicator reverted to default/unconditioned prompting.
2. **Deterministic Builders Code Loss (G13):** During subsequent active mutation experiments, the Cursor SDK agent executed Workflow 7, which performed an automated rollback (`git checkout -- src/clinical_extraction/gan/temporal_candidates.py`) to clean up its draft edits. Because the G13 deterministic builder implementations were never committed to `git HEAD` or stashed, they were permanently deleted from the working copy.
3. **Recovery Failure (Transcript Truncation):** Attempts to recover the code from the past conversation's `transcript.jsonl` failed because the logging system truncated large tool call arguments (such as the ~4.2KB helper functions block in step 719) with a literal `<truncated ...>` marker.

---

## 2. Root Cause Analysis

### A. Candidate-Emission Gap (G16 Execution)
* **Mechanism:** The evaluation runner invoked the pipeline using `"implementation_variant": "gan_s0_candidate_builder_gap_v1"`.
* **Code Bug:** In `src/clinical_extraction/gan/temporal_candidates.py` (lines 21–27), the dictionary mapping implementation variants to formats, `IMPLEMENTATION_VARIANT_TO_PRESENTATION`, did **not** contain the key `"gan_s0_candidate_builder_gap_v1"`.
* **Outcome:** The formatter `presentation_for_implementation_variant` returned `None`, disabling the deterministic preconditioning injection. The adjudicator thus received no candidates, triggering the failure.

### B. Automated Rollback & Dirty Working Copy (G13 Loss)
* **Mechanism:** The G13 builder suite was implemented on the local workspace but remained in an uncommitted/unstaged dirty state.
* **Code Bug:** The Cursor SDK active mutation runner (Workflow 7) assumed a clean repository baseline or that it only needed to preserve committed files. At the end of the dry run/verification step, it issued:
  ```powershell
  git checkout -- src/clinical_extraction/gan/temporal_candidates.py
  ```
* **Outcome:** Git restored `temporal_candidates.py` to committed `HEAD` (`f5a5aa6`), wiping out both the mutation helpers and the uncommitted G13 builders.

### C. Transcript Argument Truncation
* **Mechanism:** The system writes conversation history to `<appDataDir>\brain\<conversation-id>\.system_generated\logs\transcript.jsonl`.
* **Code Bug:** To conserve space, the logger truncates very large text blocks in tool arguments.
* **Outcome:** The `ReplacementContent` payloads containing the source code for the G13 builders were truncated during step 703 and step 719, leaving them unrecoverable from the logs.

---

## 3. What Was Lost vs. Recovered

A total of **12 tests** are currently failing in `tests/test_gan_temporal_candidates.py` because the required builders are missing. Below is the status of each function.

### A. Lost Builders (Must be Re-coded)

| Missing Function | Purpose / Targets | Expected Output (Examples) |
| --- | --- | --- |
| `_first_and_subsequent_dated_events_window` | Generalizes dated spans (`gan_14562`, `gan_14628`, `gan_14689`) | `3 per 6 month`, `2 per 2 month` |
| `_last_seizure_with_since_jerks` | Last convulsion + since events count (`gan_15127`) | `5 per 13 month` |
| `_no_major_seizures_since_but_minor_continues` | Vague-multiple since MM/YYYY anchor (`gan_15168`, `gan_15193`) | `multiple per 15 month`, `multiple per 13 month` |
| `_interval_spacing_candidates` | Quantified spacing & count / interval rate (`gan_15442`, `gan_16529`) | `1 cluster per 4 day, 2 per cluster`, `1 per 5 day` |
| `_diary_cluster_and_single_events_window` | Sum named month events into clinic window (`gan_16645`, `gan_16750`) | `5 per 7 month`, `6 per 7 month` |

### B. Recovered Snippets (Verbatim from Transcript)

The following parts of the implementation were successfully extracted from the untruncated portions of the log:

#### 1. Variant Presentation Dictionary Map
```python
IMPLEMENTATION_VARIANT_TO_PRESENTATION: dict[str, TemporalCandidatePresentation] = {
    "cand_prose_v1": "prose",
    "cand_table_v1": "table",
    "cand_json_v1": "json",
    "cand_bullets_v1": "bullets",
    "slot_payload_v1": "slot_payload",
    "gan_s0_candidate_builder_gap_v1": "prose",  # FIXED mapping
}
```

#### 2. Enhancements to `_number_token_to_label`
```python
def _number_token_to_label(token: str) -> str:
    normalized = token.lower().strip()
    if normalized in ("a", "an", "single", "one"):
        return "1"
    if normalized in NUMBER_WORDS:
        return NUMBER_WORDS[normalized]
    return normalized
```

#### 3. Breakthrough After Nearly a Year Builder
```python
def _breakthrough_after_nearly_year(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>[^.]*(?:no seizures|seizure-free)[^.]*?nearly a year[^.]*?"
        r"(?P<count>\d+|a|single|one|two|three|four|five|six|seven|eight|nine|ten)?\s*tonic seizure[^.]*)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []
    
    count_group = match.group("count")
    if count_group:
        event_count = _number_token_to_label(count_group)
    else:
        event_count = "1"
        
    label = _simple_rate_label(event_count, 1, "year")
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=label,
            event_count=event_count,
            window_count="1",
            window_unit="year",
            evidence_text=evidence,
            derivation=(
                "breakthrough event after a nearly one-year seizure-free "
                "window"
            ),
        )
    ]
```

#### 4. Seizure-free Dynamic Last Episode Builder (Partial)
```python
def _last_episode_monthly_candidate(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        rf"(?P<evidence>last\s+(?:reported\s+|such\s+)?(?:episode|event)\s+(?:was\s+recorded\s+on|was\s+on|occurred\s+on)\s+"
        rf"(?P<day>\d{{1,2}})[\s/](?P<month>{MONTH_PATTERN}|{SHORT_MONTH_PATTERN})"
        rf"(?:[\s/](?P<year>\d{{4}}))?[^.]*)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    clinic_date = _clinic_date(note_text)
    if clinic_date is None:
        return []

    event_year = int(match.group("year") or clinic_date.year)
    event_date = date(
        event_year,
        _month_number(match.group("month")),
        int(match.group("day")),
    )
    elapsed_days = (clinic_date - event_date).days
    
    # Match windows up to 6 months (approx 180 days)
    if not (14 <= elapsed_days <= 180):
        return []

    month_diff = (clinic_date.year - event_date.year) * 12 + clinic_date.month - event_date.month
    if month_diff <= 1:
        window_months = 1
        label = "1 per month"
    else:
        window_months = month_diff
        label = f"1 per {window_months} month"

    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=label,
            event_count="1",
            window_count=str(window_months),
            window_unit="month",
            evidence_text=evidence,
            derivation="last recorded event falls within an elapsed window",
        )
    ]
```

#### 5. Generalized Withdrawal Moment Builder
```python
def _withdrawal_moment_seizure_count(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>(?:he|she)\s+(?:withdrew\s+from|discontinued)\s+[A-Za-z]+\s+on\s+"
        r"(?P<day>\d{1,2})/(?P<month>[A-Za-z]+)\.\s+"
        r"(?:At\s+that\s+time,\s+he\s+had|Shortly\s+afterwards,\s+she\s+experienced)\s+"
        r"(?P<count>[A-Za-z0-9\s-]+)\s+seizures)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    clinic_date = _clinic_date(note_text)
    if clinic_date is None:
        return []

    month_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    withdrawal_month = month_map.get(match.group("month")[:3].lower())
    if withdrawal_month is None:
        return []

    withdrawal_year = clinic_date.year
    if withdrawal_month > clinic_date.month:
        withdrawal_year -= 1

    window_months = max(1, (clinic_date.year - withdrawal_year) * 12 + clinic_date.month - withdrawal_month)
    event_count = _count_range_text_to_label(match.group("count"))
    
    label = _simple_rate_label(event_count, window_months, "month")
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=label,
            event_count=event_count,
            window_count=str(window_months),
            window_unit="month",
            evidence_text=evidence,
            derivation="withdrawal-moment seizure count anchored to elapsed months before clinic",
        )
    ]
```

---

## 4. Remediation Steps for Next Agent

1. **Implement Variant Mapping Fix:** Apply the `"gan_s0_candidate_builder_gap_v1": "prose"` mapping to `IMPLEMENTATION_VARIANT_TO_PRESENTATION`.
2. **Re-implement Lost G13 Builders:** Using the target examples and failure assertions in `tests/test_gan_temporal_candidates.py` as a TDD specification guide, re-write the missing helper functions (`_first_and_subsequent_dated_events_window`, `_last_seizure_with_since_jerks`, `_no_major_seizures_since_but_minor_continues`, `_interval_spacing_candidates`, `_diary_cluster_and_single_events_window`).
3. **Verify via Pytest:** Execute `uv run pytest tests/test_gan_temporal_candidates.py` until all 49 tests pass.
4. **Rerun G16 Validation:** Rerun the validation script:
   ```powershell
   configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation.json
   ```
5. **Git Safety Rule:** Commit baseline code changes (`git commit` or `git stash`) *before* spawning subagents or running active mutation/checkout loops.
