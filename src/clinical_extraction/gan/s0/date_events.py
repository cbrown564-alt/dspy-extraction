"""Gan S0 deterministic date/event payload helpers."""
from __future__ import annotations

import re

from pydantic import Field

from clinical_extraction.schemas import FrozenModel


class GanDateEventPayload(FrozenModel):
    clinic_date: str | None = None
    temporal_anchors: list[str] = Field(default_factory=list)
    seizure_events: list[str] = Field(default_factory=list)
    seizure_free_intervals: list[str] = Field(default_factory=list)
    cluster_events: list[str] = Field(default_factory=list)
    current_window_cues: list[str] = Field(default_factory=list)
    candidate_labels: list[str] = Field(default_factory=list)
    evidence_text: str | None = None
    stage_confidence: float | None = None
    calculated_arithmetic: str | None = None


def run_arithmetic_calculator(note_text: str) -> tuple[str, str] | None:
    month_map = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    number_words_map = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }
    
    # 1. Segmented monthly series (e.g. In Nov he had 3 ... In Jan he had 5)
    month_pattern = r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b"
    month_mentions = []
    for m in re.finditer(month_pattern, note_text, re.IGNORECASE):
        m_name = m.group(1).lower()
        month_mentions.append((month_map[m_name], m.start(), m.end()))
        
    if len(month_mentions) >= 2:
        segments = []
        for i in range(len(month_mentions)):
            start_pos = month_mentions[i][2]
            end_pos = month_mentions[i+1][1] if i + 1 < len(month_mentions) else len(note_text)
            seg_text = note_text[start_pos:end_pos]
            period_idx = seg_text.find('.')
            if period_idx != -1:
                seg_text = seg_text[:period_idx]
            segments.append((month_mentions[i][0], seg_text))
            
        parsed_series = []
        number_pattern = r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b"
        for m_num, seg_text in segments:
            counts = []
            for num_match in re.finditer(number_pattern, seg_text, re.IGNORECASE):
                val_str = num_match.group(1)
                if val_str.isdigit():
                    val = int(val_str)
                    if 2020 <= val <= 2030:
                        continue
                else:
                    val = number_words_map.get(val_str.lower(), 0)
                counts.append(val)
            if counts:
                parsed_series.append((m_num, sum(counts)))
                
        if len(parsed_series) >= 2:
            total = sum(x[1] for x in parsed_series)
            years = [0]
            for i in range(1, len(parsed_series)):
                prev_m = parsed_series[i-1][0]
                curr_m = parsed_series[i][0]
                if curr_m < prev_m:
                    years.append(years[-1] + 1)
                else:
                    years.append(years[-1])
            start_idx = 0
            end_idx = len(parsed_series) - 1
            month_span = (years[end_idx] - years[start_idx]) * 12 + parsed_series[end_idx][0] - parsed_series[start_idx][0] + 1
            if month_span > 0:
                lbl = f"{total} per {month_span} month" if month_span > 1 else f"{total} per month"
                deriv = f"Summed monthly series ({' + '.join(str(x[1]) for x in parsed_series)} = {total}) over {month_span} months"
                return lbl, deriv

    # 2. Co-occurring event tally (e.g. two drop attacks and five tonic-clonic in past three months)
    window_match = re.search(
        r"(?:in|over|during)\s+(?:the\s+)?(?:past|last)\s+(\d+|one|two|three|four|five|six|seven|eight|nine|ten)?\s*(month|week|year)s?",
        note_text, re.IGNORECASE
    )
    if window_match:
        window_start = window_match.start()
        window_str = window_match.group(1)
        unit = window_match.group(2).lower()
        
        pre_text = note_text[max(0, window_start - 150):window_start]
        number_pattern = r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b"
        matches = list(re.finditer(number_pattern, pre_text, re.IGNORECASE))
        if len(matches) >= 2:
            total = 0
            for m in matches:
                val_str = m.group(1)
                if val_str.isdigit():
                    total += int(val_str)
                else:
                    total += number_words_map.get(val_str.lower(), 0)
            
            w = int(window_str) if (window_str and window_str.isdigit()) else number_words_map.get((window_str or "").lower(), 1)
            if total > 0:
                lbl = f"{total} per {w} {unit}" if w > 1 else f"{total} per {unit}"
                deriv = f"Summed co-occurring event types ({' + '.join(m.group(1) for m in matches)} = {total}) over {w} {unit}"
                return lbl, deriv

    return None


def validate_and_fallback_label(label: str | None) -> str | None:
    if label is None:
        return None
    from clinical_extraction.gan.frequency import gan_label_policy_failure_class
    fail_class = gan_label_policy_failure_class(label)
    if fail_class in {"unknown_quantified_hybrid", "malformed_cluster_unknown_slot"}:
        return "unknown"
    return label


def build_deterministic_date_event_payload(note_text: str) -> GanDateEventPayload:
    from clinical_extraction.gan.temporal_candidates import (
        build_temporal_frequency_candidates_from_note,
        _clinic_date,
    )
    candidates = list(build_temporal_frequency_candidates_from_note(note_text))
    
    # Arithmetic calculator: run for diagnostic reporting only (v1.3: not injected as candidates
    # because the month-series parser fires on non-seizure month mentions, adding spurious candidates).
    arith_res = run_arithmetic_calculator(note_text)
    calculated_arithmetic = None
    if arith_res:
        lbl, deriv = arith_res
        calculated_arithmetic = f"{lbl} (derived via: {deriv})"
        # NOTE: calculator result is stored in calculated_arithmetic for prompt context
        # but NOT appended to candidates to avoid spurious candidate injection.
    
    clinic_d = _clinic_date(note_text)
    clinic_date_str = clinic_d.isoformat() if clinic_d else None
    
    temporal_anchors = []
    seizure_events = []
    seizure_free_intervals = []
    cluster_events = []
    current_window_cues = []
    candidate_labels = []
    evidence_pieces = []
    
    for c in candidates:
        candidate_labels.append(c.canonical_label)
        if c.evidence_text:
            evidence_pieces.append(c.evidence_text)
        
        label_lower = c.canonical_label.lower()
        if "seizure free" in label_lower or "seizure-free" in label_lower:
            seizure_free_intervals.append(f"{c.canonical_label} (based on: {c.evidence_text!r})")
        elif "cluster" in label_lower:
            cluster_events.append(f"{c.canonical_label} (based on: {c.evidence_text!r})")
        else:
            seizure_events.append(f"{c.canonical_label} (based on: {c.evidence_text!r})")
            
        if c.derivation:
            current_window_cues.append(c.derivation)
            
    if clinic_date_str:
        temporal_anchors.append(f"clinic_date={clinic_date_str}")
        
    unique_evidence = list(dict.fromkeys(evidence_pieces))
    evidence_text = " | ".join(unique_evidence) if unique_evidence else None
    
    return GanDateEventPayload(
        clinic_date=clinic_date_str,
        temporal_anchors=list(dict.fromkeys(temporal_anchors)),
        seizure_events=list(dict.fromkeys(seizure_events)),
        seizure_free_intervals=list(dict.fromkeys(seizure_free_intervals)),
        cluster_events=list(dict.fromkeys(cluster_events)),
        current_window_cues=list(dict.fromkeys(current_window_cues)),
        candidate_labels=list(dict.fromkeys(candidate_labels)),
        evidence_text=evidence_text,
        stage_confidence=1.0,
        calculated_arithmetic=calculated_arithmetic,
    )
