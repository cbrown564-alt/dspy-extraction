"""ExECT seizure-frequency payloads and benchmark bridge helpers."""

from __future__ import annotations

import re

from clinical_extraction.datasets.exect import canonical_clinical_phrase
from clinical_extraction.primitives import NormalizationResult, PrimitiveCandidate

EXECT_FREQUENCY_RATE_CANDIDATE_PRIMITIVE_ID = "exect.frequency.rate_candidates.v1"
EXECT_FREQUENCY_BENCHMARK_BRIDGE_PRIMITIVE_ID = (
    "exect.frequency.benchmark_bridge.v1"
)

_FREQUENCY_MARKERS = (
    " per ",
    "seizure free",
    "frequency increased",
    "frequency decreased",
    "infrequent",
    "frequency same",
)
_NEAR_MISS_QUANTIFIED_FREQUENCY = re.compile(
    r"^(?P<count>\d+) per (?P<period>week|month|day|year)$"
)
_FREQUENCY_CHANGE_SYNONYMS = {
    "increased frequency": "frequency increased",
    "frequency has increased": "frequency increased",
    "decreased frequency": "frequency decreased",
    "frequency has decreased": "frequency decreased",
}
_SEIZURE_TYPE_FREQUENCY_CONFUSION = (
    "seizure",
    "seizures",
    "tonic clonic",
    "convulsive",
    "absence",
    "myoclonic",
    "focal aware",
    "impaired awareness",
    "altered awareness",
    "temporal lobe",
    "occipital lobe",
)
_QUANTIFIED_FREQUENCY_RE = re.compile(
    r"^(?:\d+|several) per (?:\d+ )?(?:week|month|day|year)$"
)
_NON_AUDITED_FREQUENCY_RES = (
    re.compile(r" per 30 day$"),
    re.compile(r"previous appointment"),
    re.compile(r"^several per"),
    re.compile(r" per \d+ \d+ week$"),
)
_FREQUENCY_CO_LABEL_CUES = {
    "frequency increased": (
        "frequency increased",
        "frequency has increased",
        "increased frequency",
        "seizures have returned",
        "seizures returned",
        "seizures have worsened",
        "seizures worsened",
        "returned seizures",
        "having more",
        "getting more",
        "more seizures",
        "another seizure",
        "had another seizure",
        "seizures returning",
        "increasing seizures",
        "seizures increasing",
        "seizures have increased",
        "seizures have been worse",
        "seizures worse",
        "more frequent",
        "worse in the last year",
    ),
    "frequency decreased": (
        "frequency decreased",
        "frequency has decreased",
        "decreased frequency",
        "seizures have improved",
        "seizures improved",
        "epilepsy has improved",
        "epilepsy improved",
        "seizures have reduced",
        "seizures reduced",
        "improved seizures",
    ),
    "infrequent": (
        "infrequent",
        "occasional",
        "occasionally",
        "rare",
        "rarely",
        "well controlled",
        "controlled",
        "reasonably controlled",
    ),
    "frequency same": (
        "frequency same",
        "remains the same",
        "remain the same",
        "no change",
        "remain well controlled",
        "remains well controlled",
        "remain controlled",
        "remains controlled",
        "continue to get",
        "continues to get",
        "continue to have",
        "continues to have",
        "not really helped",
        "hasn't really helped",
        "haven't really helped",
        "stable",
        "remain stable",
        "remains stable",
        "stable frequency",
        "seizures remain",
        "well controlled",
        "controlled",
    ),
}
_COUNT_WORDS = {
    "once": "1",
    "twice": "2",
    "thrice": "3",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "several": "3",
}
_PERIOD_UNIT = r"weeks?|months?|days?|years?"
_QUANTIFIED_FREQUENCY_EX_RE = re.compile(
    rf"\b(?P<count>once|twice|thrice|one|two|three|four|five|six|seven|eight|nine|ten|several|\d+)\s+"
    rf"(?:(?:[a-zA-Z-]+)\s+){{0,3}}?(?:seizures?|convulsions|episodes|events)?\s*(?:times?\s+)?(?:every|per|a|over|in|during|within|for)(?:\s+the\s+(?:last|past))?\s+"
    rf"(?P<period_count>one|two|three|four|five|six|seven|eight|nine|ten|several|\d+)?\s*(?P<period>{_PERIOD_UNIT})\b",
    flags=re.IGNORECASE,
)
_IMPLICIT_QUANTIFIED_FREQUENCY_RE = re.compile(
    rf"\b(?:every|per|a|over|in|during|within|for)(?:\s+the\s+(?:last|past))?\s+(?P<period_count>one|two|three|four|five|six|seven|eight|nine|ten|several|\d+)?\s*"
    rf"(?P<period>{_PERIOD_UNIT})\b",
    flags=re.IGNORECASE,
)
_ADVERB_FREQUENCY_RE = re.compile(
    rf"\b(?P<count>once|twice|thrice|one|two|three|four|five|six|seven|eight|nine|ten|several|\d+)?\s*"
    rf"(?:times?\s+)?(?P<adverb>daily|weekly|monthly|yearly|annually)\b",
    flags=re.IGNORECASE,
)
_ZERO_RATE_WINDOW_RE = re.compile(
    rf"\b(?:no|zero|0|not had|not happen|not happened)\s+(?:[a-zA-Z-]+\s+){{0,5}}?(?:seizures?|convulsions|episodes|events)?\s*"
    rf"(?:now\s+)?(?:for|in|over|since|per|every|a)\s+(?:the\s+last|the\s+past|at\s+least|more\s+than|over)?\s*"
    rf"(?P<period_count>one|two|three|four|five|six|seven|eight|nine|ten|several|\d+)?\s*(?P<period>{_PERIOD_UNIT})\b",
    flags=re.IGNORECASE,
)
_ZERO_RATE_FREE_RE = re.compile(
    rf"\bseizure[- ]free\s+(?:for|in|over)\s+(?:the\s+last|the\s+past|at\s+least|more\s+than|over)?\s*"
    rf"(?P<period_count>one|two|three|four|five|six|seven|eight|nine|ten|several|\d+)?\s*(?P<period>{_PERIOD_UNIT})\b",
    flags=re.IGNORECASE,
)
_SEIZURE_FREE_CURRENT_RE = re.compile(
    rf"\b(?:no|zero|0|not had|not happen|not happened)\s+(?:[a-zA-Z-]+\s+){{0,3}}?(?:seizures?|convulsions|episodes|events)\b",
    flags=re.IGNORECASE,
)
_AGO_ZERO_RATE_RE = re.compile(
    rf"\b(?:(?:last|most recent)\s*(?:one|seizure|event|episode|convulsion|seizures|convulsions|episodes|events)?|(?:her|his|the)?\s*(?:seizure|event|episode|convulsion|seizures|convulsions|episodes|events))\s*(?:of\s+these\s+)?(?:was|happened|occurred|occur|ocured|occurd|happend)?\s*(?:around|about|at\s+least|more\s+than|greater\s+than|over)?\s*"
    rf"(?P<period_count>one|two|three|four|five|six|seven|eight|nine|ten|several|\d+)\s+(?P<period>{_PERIOD_UNIT})\s+ago\b",
    flags=re.IGNORECASE,
)
_SEIZURE_FREE_SINCE_YEAR_RE = re.compile(
    rf"\b(?:seizure[- ]free|free of seizures)\s+since\s+"
    rf"(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sept|oct|nov|dec)?\s*"
    rf"(?P<year>\d{{4}})\b",
    flags=re.IGNORECASE,
)
_LAST_EVENT_YEAR_RE = re.compile(
    rf"\blast\s+(?:seizure|event|episode|convulsion)\s+(?:was\s+)?(?:in\s+)?"
    rf"(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sept|oct|nov|dec)?\s*"
    rf"(?P<year>\d{{4}})\b",
    flags=re.IGNORECASE,
)
_LAST_SEIZURE_DATE_RE = re.compile(
    rf"\blast\s+(?:seizure|event|episode|convulsion|seizures|convulsions|episodes|events)\s+(?:was\s+)?(?:on\s+the\s+|on\s+|in\s+)?(?:\d{{1,2}}(?:st|nd|rd|th)?\s+)?(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sept|oct|nov|dec)\b",
    flags=re.IGNORECASE,
)
_BREAKTHROUGH_AFTER_PERIOD_RE = re.compile(
    rf"\b(?P<period_count>one|two|three|four|five|six|seven|eight|nine|ten|several|\d+)?\s*(?P<period>{_PERIOD_UNIT})\s+(?:without\s+having|without|free of|no)\s+seizures?\s+(?:[a-zA-Z-]+\s+){{0,10}}?(?P<event>cluster|seizure|episode|event|convulsion|convulsions)\b",
    flags=re.IGNORECASE,
)
_AUDITED_QUALITATIVE_FREQUENCY_LABELS = frozenset(
    {
        "frequency increased",
        "frequency decreased",
        "infrequent",
        "seizure free",
        "frequency same",
    }
)
_ADVERB_TO_PERIOD = {
    "daily": "day",
    "weekly": "week",
    "monthly": "month",
    "yearly": "year",
    "annually": "year",
}


def build_exect_frequency_candidate_payloads(note_text: str) -> list[PrimitiveCandidate]:
    """Return note-anchored ExECT seizure-frequency candidates as shared payloads."""

    payloads: list[PrimitiveCandidate] = []
    for label in sorted(_build_exect_frequency_label_set(note_text)):
        span = _frequency_label_span(note_text, label)
        payloads.append(
            PrimitiveCandidate(
                primitive_id=EXECT_FREQUENCY_RATE_CANDIDATE_PRIMITIVE_ID,
                dataset="exect_v2",
                field_family="frequency",
                raw_text=span or label,
                normalized_value=label,
                benchmark_value=label,
                source_span_text=span or label,
                start=note_text.find(span) if span and span in note_text else None,
                end=(
                    note_text.find(span) + len(span)
                    if span and span in note_text
                    else None
                ),
                rule_name=_frequency_candidate_rule_name(label, note_text),
                confidence=1.0,
                caveats=[
                    "ExECT seizure-frequency candidates are soft hints for narrow S4 probes.",
                    "Gan monthly normalization and label-policy classes do not transfer to ExECT.",
                    "MarkupSeizureFrequency templates remain the benchmark-facing gold surface.",
                ],
                metadata={
                    "candidate_source": _frequency_candidate_source(label, note_text),
                    "gan_temporal_filtered": _frequency_candidate_source(
                        label, note_text
                    )
                    == "gan_temporal_filtered",
                },
            )
        )
    return payloads


def build_exect_frequency_pre_vocab_labels(note_text: str) -> list[str]:
    """Build sorted benchmark-facing seizure-frequency labels for H2 pre-vocab probes."""

    return sorted(_build_exect_frequency_label_set(note_text))


def format_exect_frequency_pre_vocab_note(note_text: str) -> str:
    """Inject seizure-frequency-only audited candidates before the clinical note."""

    frequency_candidates = build_exect_frequency_pre_vocab_labels(note_text)
    lines = [
        "Precomputed benchmark-facing candidates (soft hints; emit only when note-supported):",
        f"seizure_frequency: {', '.join(frequency_candidates)}",
        "",
        "---",
        "",
        note_text,
    ]
    return "\n".join(lines)


def build_exect_frequency_pre_vocab_labels_high_precision(note_text: str) -> list[str]:
    """Build sorted high-precision benchmark-facing seizure-frequency labels."""

    return sorted(_build_exect_frequency_label_set_high_precision(note_text))


def format_exect_frequency_pre_vocab_note_high_precision(note_text: str) -> str:
    """Inject high-precision seizure-frequency candidates before the note."""

    frequency_candidates = build_exect_frequency_pre_vocab_labels_high_precision(
        note_text
    )
    lines = [
        "Precomputed benchmark-facing candidates (soft hints; emit only when note-supported):",
        f"seizure_frequency: {', '.join(frequency_candidates)}",
        "",
        "---",
        "",
        note_text,
    ]
    return "\n".join(lines)


def repair_exect_frequency_surface(canonical: str) -> tuple[str, list[str]]:
    """Repair near-miss quantified rates and qualitative frequency-change synonyms."""

    flags: list[str] = []
    repaired = canonical

    synonym = _FREQUENCY_CHANGE_SYNONYMS.get(canonical)
    if synonym:
        return synonym, ["s4_bridge:frequency_change_synonym"]

    near_miss = _NEAR_MISS_QUANTIFIED_FREQUENCY.match(canonical)
    if near_miss:
        repaired = f"{near_miss.group('count')} per 1 {near_miss.group('period')}"
        flags.append("s4_bridge:frequency_missing_time_period_inserted")

    if canonical.startswith("seizure free") and canonical != "seizure free":
        if re.match(r"seizure free since \d{4}$", canonical):
            return canonical, flags
        return "seizure free", [*flags, "s4_bridge:seizure_free_prose_collapsed"]

    return repaired, flags


def note_has_exect_frequency_support(note_text: str) -> bool:
    """Return True when note text supports at least one audited frequency template."""

    return bool(_build_exect_frequency_label_set(note_text))


def recover_exect_frequency_benchmark_values(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Recover benchmark-facing seizure-frequency labels from model outputs."""

    flags: list[str] = []
    recovered: list[str] = []
    seen: set[str] = set()

    for raw in raw_values:
        if not raw.strip():
            continue
        canonical = canonical_clinical_phrase(raw)
        if not canonical:
            continue
        if _looks_like_seizure_type_not_frequency(raw):
            flags.append("s4_bridge:seizure_type_removed_from_frequency")
            continue
        repaired, repair_flags = repair_exect_frequency_surface(canonical)
        flags.extend(repair_flags)
        canonical = repaired
        if _is_non_audited_frequency_surface(canonical):
            flags.append("s4_bridge:non_audited_frequency_removed")
            continue
        if not _is_audited_exect_frequency_template(canonical):
            flags.append("s4_bridge:unsupported_frequency_removed")
            continue
        if canonical in seen:
            continue
        seen.add(canonical)
        recovered.append(canonical)

    recovered, co_label_flags = _augment_exect_frequency_co_labels(
        recovered, note_text
    )
    flags.extend(co_label_flags)
    return recovered, flags


def recover_exect_frequency_benchmark_values_with_post_merge(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Recover frequency labels with v1.2 bridge plus post-merge note anchoring."""

    recovered, flags = recover_exect_frequency_benchmark_values(raw_values, note_text)
    note_anchored = _build_exect_frequency_label_set(note_text)

    seen = set(recovered)
    for label in sorted(note_anchored):
        if label in seen:
            continue
        recovered.append(label)
        seen.add(label)
        flags.append("s4_bridge:note_anchored_frequency_merged")

    note_lower = note_text.lower()
    filtered: list[str] = []
    for label in recovered:
        if label == "seizure free" and "seizure free" not in note_lower:
            flags.append("s4_bridge:spurious_seizure_free_removed")
            continue
        if label.startswith(
            "seizure free since "
        ) and not _SEIZURE_FREE_SINCE_YEAR_RE.search(note_text):
            flags.append("s4_bridge:spurious_seizure_free_removed")
            continue
        filtered.append(label)

    return filtered, flags


def recover_exect_frequency_benchmark_values_with_multi_label_retention(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Recover frequency labels with widened co-labels and partial slot fill."""

    recovered, flags = recover_exect_frequency_benchmark_values(raw_values, note_text)
    recovered, co_flags = _augment_exect_frequency_co_labels_multi_label(
        recovered,
        note_text,
    )
    flags.extend(co_flags)

    if recovered:
        note_anchored = _build_exect_frequency_label_set(note_text)
        seen = set(recovered)
        for label in sorted(note_anchored):
            if label in seen:
                continue
            recovered.append(label)
            seen.add(label)
            flags.append("s4_bridge:multi_label_slot_filled")

    note_lower = note_text.lower()
    filtered: list[str] = []
    for label in recovered:
        if label == "seizure free" and "seizure free" not in note_lower:
            flags.append("s4_bridge:spurious_seizure_free_removed")
            continue
        if label.startswith(
            "seizure free since "
        ) and not _SEIZURE_FREE_SINCE_YEAR_RE.search(note_text):
            flags.append("s4_bridge:spurious_seizure_free_removed")
            continue
        filtered.append(label)

    return filtered, flags


def exect_frequency_benchmark_bridge(
    raw_values: list[str],
    *,
    note_text: str = "",
    prediction_affecting: bool = True,
) -> list[NormalizationResult]:
    """Map seizure-frequency predictions to audited ExECT benchmark templates."""

    recovered, flags = recover_exect_frequency_benchmark_values(raw_values, note_text)
    if not recovered:
        return [
            NormalizationResult(
                primitive_id=EXECT_FREQUENCY_BENCHMARK_BRIDGE_PRIMITIVE_ID,
                dataset="exect_v2",
                field_family="frequency",
                raw_value=None,
                canonical_value=None,
                benchmark_value=None,
                clinical_caveat=(
                    "ExECT seizure frequency abstains when no audited benchmark "
                    "template survives bridge policy."
                ),
                transformation_rule="exect_frequency_abstention",
                prediction_affecting=prediction_affecting,
                scorer_only=not prediction_affecting,
                metadata={
                    "bridge_flags": flags,
                    "abstention": True,
                    "no_reference_policy": "empty_list_not_gan_no_reference",
                },
            )
        ]

    return [
        _exect_frequency_normalization_result(
            raw_value=label,
            benchmark_value=label,
            bridge_flags=flags,
            prediction_affecting=prediction_affecting,
        )
        for label in recovered
    ]


def filter_gan_temporal_candidate_for_exect(canonical_label: str) -> str | None:
    """Accept Gan temporal hints only when they map to audited ExECT templates."""

    return _accept_exect_frequency_candidate_label(canonical_label)


def _build_exect_frequency_label_set(note_text: str) -> set[str]:
    from clinical_extraction.gan.temporal_candidates import (
        build_temporal_frequency_candidates_from_note,
    )

    candidates: set[str] = set()
    note_lower = note_text.lower()

    for label, cues in _FREQUENCY_CO_LABEL_CUES.items():
        if any(cue in note_lower for cue in cues):
            accepted = _accept_exect_frequency_candidate_label(label)
            if accepted:
                candidates.add(accepted)

    for match in _SEIZURE_FREE_SINCE_YEAR_RE.finditer(note_text):
        accepted = _accept_exect_frequency_candidate_label(
            f"seizure free since {match.group('year')}"
        )
        if accepted:
            candidates.add(accepted)

    for match in _LAST_EVENT_YEAR_RE.finditer(note_text):
        accepted = _accept_exect_frequency_candidate_label(
            f"seizure free since {match.group('year')}"
        )
        if accepted:
            candidates.add(accepted)

    seizures_returned = (
        "seizures have returned" in note_lower
        or "seizures returned" in note_lower
        or "returned seizures" in note_lower
        or "seizures recurred" in note_lower
        or "seizures recur" in note_lower
        or "seizures have worsened" in note_lower
        or "seizures worsened" in note_lower
        or "seizures are worse" in note_lower
        or "seizures have been worse" in note_lower
        or "worse in the last" in note_lower
        or "worse recently" in note_lower
    )

    if not seizures_returned:
        if re.search(r"\bseizure[- ]free\b", note_lower):
            accepted = _accept_exect_frequency_candidate_label("seizure free")
            if accepted:
                candidates.add(accepted)
        elif _SEIZURE_FREE_CURRENT_RE.search(note_text):
            accepted = _accept_exect_frequency_candidate_label("seizure free")
            if accepted:
                candidates.add(accepted)

    def get_period_count_options(raw_count_str: str | None) -> list[str]:
        if not raw_count_str:
            return ["1"]
        clean = raw_count_str.strip().lower()
        if not clean:
            return ["1"]
        clean_first = clean.split()[0]
        if clean_first == "several":
            return ["2", "3"]
        return [_COUNT_WORDS.get(clean_first, clean_first)]

    def get_count_options(raw_count_str: str | None) -> list[str]:
        if not raw_count_str:
            return ["1"]
        clean = raw_count_str.strip().lower()
        if clean == "several":
            return ["2", "3"]
        return [_COUNT_WORDS.get(clean, clean)]

    for match in _QUANTIFIED_FREQUENCY_EX_RE.finditer(note_text):
        counts = get_count_options(match.group("count"))
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for count in counts:
            for period_count in period_counts:
                accepted = _accept_exect_frequency_candidate_label(
                    f"{count} per {period_count} {period}"
                )
                if accepted:
                    candidates.add(accepted)

    for match in _IMPLICIT_QUANTIFIED_FREQUENCY_RE.finditer(note_text):
        start_idx = match.start()
        preceding_text = note_text[max(0, start_idx - 15) : start_idx].strip().lower()
        preceding_words = preceding_text.split()
        if preceding_words:
            last_word = preceding_words[-1].strip("-,.(): ")
            if last_word in _COUNT_WORDS or last_word.isdigit():
                continue

        counts = ["1"]
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for count in counts:
            for period_count in period_counts:
                accepted = _accept_exect_frequency_candidate_label(
                    f"{count} per {period_count} {period}"
                )
                if accepted:
                    candidates.add(accepted)

    for match in _ADVERB_FREQUENCY_RE.finditer(note_text):
        counts = get_count_options(match.group("count"))
        adverb = match.group("adverb").lower()
        period = _ADVERB_TO_PERIOD.get(adverb, "week")
        for count in counts:
            accepted = _accept_exect_frequency_candidate_label(
                f"{count} per 1 {period}"
            )
            if accepted:
                candidates.add(accepted)

    for match in _ZERO_RATE_WINDOW_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            accepted = _accept_exect_frequency_candidate_label(
                f"0 per {period_count} {period}"
            )
            if accepted:
                candidates.add(accepted)
            if not seizures_returned:
                accepted_sf = _accept_exect_frequency_candidate_label("seizure free")
                if accepted_sf:
                    candidates.add(accepted_sf)

    for match in _ZERO_RATE_FREE_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            accepted = _accept_exect_frequency_candidate_label(
                f"0 per {period_count} {period}"
            )
            if accepted:
                candidates.add(accepted)
            if not seizures_returned:
                accepted_sf = _accept_exect_frequency_candidate_label("seizure free")
                if accepted_sf:
                    candidates.add(accepted_sf)

    for match in _AGO_ZERO_RATE_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            accepted = _accept_exect_frequency_candidate_label(
                f"0 per {period_count} {period}"
            )
            if accepted:
                candidates.add(accepted)
            if not seizures_returned:
                accepted_sf = _accept_exect_frequency_candidate_label("seizure free")
                if accepted_sf:
                    candidates.add(accepted_sf)

    if not seizures_returned:
        for _match in _LAST_SEIZURE_DATE_RE.finditer(note_text):
            accepted = _accept_exect_frequency_candidate_label("seizure free")
            if accepted:
                candidates.add(accepted)

    for match in _BREAKTHROUGH_AFTER_PERIOD_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            accepted = _accept_exect_frequency_candidate_label(
                f"1 per {period_count} {period}"
            )
            if accepted:
                candidates.add(accepted)

    for temporal_candidate in build_temporal_frequency_candidates_from_note(note_text):
        accepted = _accept_exect_frequency_candidate_label(
            temporal_candidate.canonical_label
        )
        if accepted:
            candidates.add(accepted)

    return candidates


def _build_exect_frequency_label_set_high_precision(note_text: str) -> set[str]:
    candidates: set[str] = set()

    for match in _SEIZURE_FREE_SINCE_YEAR_RE.finditer(note_text):
        accepted = _accept_exect_frequency_candidate_label(
            f"seizure free since {match.group('year')}"
        )
        if accepted:
            candidates.add(accepted)

    for match in _LAST_EVENT_YEAR_RE.finditer(note_text):
        accepted = _accept_exect_frequency_candidate_label(
            f"seizure free since {match.group('year')}"
        )
        if accepted:
            candidates.add(accepted)

    def get_period_count_options(raw_count_str: str | None) -> list[str]:
        if not raw_count_str:
            return ["1"]
        clean = raw_count_str.strip().lower()
        if not clean:
            return ["1"]
        clean_first = clean.split()[0]
        if clean_first == "several":
            return ["2", "3"]
        return [_COUNT_WORDS.get(clean_first, clean_first)]

    def get_count_options(raw_count_str: str | None) -> list[str]:
        if not raw_count_str:
            return ["1"]
        clean = raw_count_str.strip().lower()
        if clean == "several":
            return ["2", "3"]
        return [_COUNT_WORDS.get(clean, clean)]

    for match in _QUANTIFIED_FREQUENCY_EX_RE.finditer(note_text):
        counts = get_count_options(match.group("count"))
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for count in counts:
            for period_count in period_counts:
                accepted = _accept_exect_frequency_candidate_label(
                    f"{count} per {period_count} {period}"
                )
                if accepted:
                    candidates.add(accepted)

    for match in _IMPLICIT_QUANTIFIED_FREQUENCY_RE.finditer(note_text):
        start_idx = match.start()
        preceding_text = note_text[max(0, start_idx - 15) : start_idx].strip().lower()
        preceding_words = preceding_text.split()
        if preceding_words:
            last_word = preceding_words[-1].strip("-,.(): ")
            if last_word in _COUNT_WORDS or last_word.isdigit():
                continue

        counts = ["1"]
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for count in counts:
            for period_count in period_counts:
                accepted = _accept_exect_frequency_candidate_label(
                    f"{count} per {period_count} {period}"
                )
                if accepted:
                    candidates.add(accepted)

    for match in _ADVERB_FREQUENCY_RE.finditer(note_text):
        counts = get_count_options(match.group("count"))
        adverb = match.group("adverb").lower()
        period = _ADVERB_TO_PERIOD.get(adverb, "week")
        for count in counts:
            accepted = _accept_exect_frequency_candidate_label(
                f"{count} per 1 {period}"
            )
            if accepted:
                candidates.add(accepted)

    for match in _ZERO_RATE_WINDOW_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            accepted = _accept_exect_frequency_candidate_label(
                f"0 per {period_count} {period}"
            )
            if accepted:
                candidates.add(accepted)

    for match in _ZERO_RATE_FREE_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            accepted = _accept_exect_frequency_candidate_label(
                f"0 per {period_count} {period}"
            )
            if accepted:
                candidates.add(accepted)

    for match in _AGO_ZERO_RATE_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            accepted = _accept_exect_frequency_candidate_label(
                f"0 per {period_count} {period}"
            )
            if accepted:
                candidates.add(accepted)

    for match in _BREAKTHROUGH_AFTER_PERIOD_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            accepted = _accept_exect_frequency_candidate_label(
                f"1 per {period_count} {period}"
            )
            if accepted:
                candidates.add(accepted)

    return candidates


def _accept_exect_frequency_candidate_label(label: str) -> str | None:
    canonical = canonical_clinical_phrase(label)
    if not canonical or _looks_like_seizure_type_not_frequency(canonical):
        return None
    repaired, _ = repair_exect_frequency_surface(canonical)
    if _is_non_audited_frequency_surface(repaired):
        return None
    if not _is_audited_exect_frequency_template(repaired):
        return None
    return repaired


def _is_audited_exect_frequency_template(canonical: str) -> bool:
    if canonical in _AUDITED_QUALITATIVE_FREQUENCY_LABELS:
        return True
    if re.match(r"seizure free since \d{4}$", canonical):
        return True
    return bool(_QUANTIFIED_FREQUENCY_RE.match(canonical))


def _is_non_audited_frequency_surface(canonical: str) -> bool:
    return any(pattern.search(canonical) for pattern in _NON_AUDITED_FREQUENCY_RES)


def _is_quantified_frequency_label(canonical: str) -> bool:
    return bool(_QUANTIFIED_FREQUENCY_RE.match(canonical))


def _augment_exect_frequency_co_labels(
    recovered: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    if not any(_is_quantified_frequency_label(label) for label in recovered):
        return recovered, []

    note = note_text.lower()
    flags: list[str] = []
    augmented = list(recovered)
    seen = set(recovered)

    for label, cues in _FREQUENCY_CO_LABEL_CUES.items():
        if label in seen:
            continue
        if any(cue in note for cue in cues):
            augmented.append(label)
            seen.add(label)
            flags.append("s4_bridge:frequency_co_label_augmented")

    return augmented, flags


def _augment_exect_frequency_co_labels_multi_label(
    recovered: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Augment qualitative co-labels when note cues exist and model engaged frequency."""

    if not recovered:
        return recovered, []

    note = note_text.lower()
    note_anchored = _build_exect_frequency_label_set(note_text)
    note_has_rate_block = any(
        _is_quantified_frequency_label(label) or label.startswith("0 per")
        for label in note_anchored
    )
    model_has_rate = any(
        _is_quantified_frequency_label(label) or label.startswith("0 per")
        for label in recovered
    )
    if not (note_has_rate_block or model_has_rate):
        return _augment_exect_frequency_co_labels(recovered, note_text)

    flags: list[str] = []
    augmented = list(recovered)
    seen = set(recovered)

    for label, cues in _FREQUENCY_CO_LABEL_CUES.items():
        if label in seen:
            continue
        if any(cue in note for cue in cues):
            augmented.append(label)
            seen.add(label)
            flags.append("s4_bridge:frequency_co_label_multi_label_retained")

    return augmented, flags


def _looks_like_seizure_frequency_label(value: str) -> bool:
    canonical = canonical_clinical_phrase(value)
    if not canonical:
        return False
    return any(marker in canonical for marker in _FREQUENCY_MARKERS)


def _looks_like_seizure_type_not_frequency(value: str) -> bool:
    canonical = canonical_clinical_phrase(value)
    if not canonical:
        return False
    if _looks_like_seizure_frequency_label(canonical):
        return False
    return any(marker in canonical for marker in _SEIZURE_TYPE_FREQUENCY_CONFUSION)


def _normalize_period_unit(period: str) -> str:
    return period.lower().rstrip("s")


def _frequency_label_span(note_text: str, label: str) -> str | None:
    if label in _FREQUENCY_CO_LABEL_CUES:
        for cue in _FREQUENCY_CO_LABEL_CUES[label]:
            index = note_text.lower().find(cue)
            if index >= 0:
                return note_text[index : index + len(cue)]

    for match in _SEIZURE_FREE_SINCE_YEAR_RE.finditer(note_text):
        if f"seizure free since {match.group('year')}" == label:
            return match.group(0)

    for match in _LAST_EVENT_YEAR_RE.finditer(note_text):
        if f"seizure free since {match.group('year')}" == label:
            return match.group(0)

    if label == "seizure free":
        match = re.search(r"\bseizure[- ]free\b", note_text, re.IGNORECASE)
        if match:
            return match.group(0)
        match = _SEIZURE_FREE_CURRENT_RE.search(note_text)
        if match:
            return match.group(0)

    def get_period_count_options(raw_count_str: str | None) -> list[str]:
        if not raw_count_str:
            return ["1"]
        clean = raw_count_str.strip().lower()
        if not clean:
            return ["1"]
        clean_first = clean.split()[0]
        if clean_first == "several":
            return ["2", "3"]
        return [_COUNT_WORDS.get(clean_first, clean_first)]

    def get_count_options(raw_count_str: str | None) -> list[str]:
        if not raw_count_str:
            return ["1"]
        clean = raw_count_str.strip().lower()
        if clean == "several":
            return ["2", "3"]
        return [_COUNT_WORDS.get(clean, clean)]

    for match in _QUANTIFIED_FREQUENCY_EX_RE.finditer(note_text):
        counts = get_count_options(match.group("count"))
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for count in counts:
            for period_count in period_counts:
                if f"{count} per {period_count} {period}" == label:
                    return match.group(0)

    for match in _IMPLICIT_QUANTIFIED_FREQUENCY_RE.finditer(note_text):
        count = "1"
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            if f"{count} per {period_count} {period}" == label:
                return match.group(0)

    for match in _ADVERB_FREQUENCY_RE.finditer(note_text):
        counts = get_count_options(match.group("count"))
        adverb = match.group("adverb").lower()
        period = _ADVERB_TO_PERIOD.get(adverb, "week")
        for count in counts:
            if f"{count} per 1 {period}" == label:
                return match.group(0)

    for match in _ZERO_RATE_WINDOW_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            if f"0 per {period_count} {period}" == label:
                return match.group(0)

    for match in _ZERO_RATE_FREE_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            if f"0 per {period_count} {period}" == label:
                return match.group(0)

    for match in _AGO_ZERO_RATE_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            if f"0 per {period_count} {period}" == label:
                return match.group(0)

    return None


def _frequency_candidate_rule_name(label: str, note_text: str) -> str:
    source = _frequency_candidate_source(label, note_text)
    if source == "gan_temporal_filtered":
        return "gan_temporal_to_exect_template"
    if source == "qualitative_change_cue":
        return "qualitative_frequency_change_cue"
    if label.startswith("seizure free"):
        return "seizure_free_surface"
    if label.startswith("0 per "):
        return "zero_rate_surface"
    return "quantified_rate_surface"


def _frequency_candidate_source(label: str, note_text: str) -> str:
    from clinical_extraction.gan.temporal_candidates import (
        build_temporal_frequency_candidates_from_note,
    )

    note_lower = note_text.lower()
    if label in _FREQUENCY_CO_LABEL_CUES and any(
        cue in note_lower for cue in _FREQUENCY_CO_LABEL_CUES[label]
    ):
        return "qualitative_change_cue"
    if label.startswith("seizure free") and "seizure free" in note_lower:
        return "seizure_free_surface"
    for temporal_candidate in build_temporal_frequency_candidates_from_note(note_text):
        accepted = _accept_exect_frequency_candidate_label(
            temporal_candidate.canonical_label
        )
        if accepted == label:
            return "gan_temporal_filtered"
    return "note_regex_quantified"


def _exect_frequency_normalization_result(
    *,
    raw_value: str,
    benchmark_value: str,
    bridge_flags: list[str],
    prediction_affecting: bool,
) -> NormalizationResult:
    caveat = None
    if "s4_bridge:seizure_free_prose_collapsed" in bridge_flags:
        caveat = (
            "Clinical prose may state seizure-free duration; benchmark gold may use "
            "quantified zero-rate templates instead."
        )
    elif "s4_bridge:frequency_co_label_augmented" in bridge_flags:
        caveat = (
            "Qualitative change labels are added only when note text contains explicit "
            "frequency-change cues alongside a quantified rate."
        )
    return NormalizationResult(
        primitive_id=EXECT_FREQUENCY_BENCHMARK_BRIDGE_PRIMITIVE_ID,
        dataset="exect_v2",
        field_family="frequency",
        raw_value=raw_value,
        canonical_value=benchmark_value,
        benchmark_value=benchmark_value,
        clinical_caveat=caveat,
        transformation_rule="exect_frequency_benchmark_recovery",
        prediction_affecting=prediction_affecting,
        scorer_only=not prediction_affecting,
        metadata={
            "bridge_flags": bridge_flags,
            "source_policy": "markup_seizure_frequency_templates",
            "gan_monthly_policy_excluded": True,
        },
    )


__all__ = [
    "EXECT_FREQUENCY_BENCHMARK_BRIDGE_PRIMITIVE_ID",
    "EXECT_FREQUENCY_RATE_CANDIDATE_PRIMITIVE_ID",
    "build_exect_frequency_candidate_payloads",
    "build_exect_frequency_pre_vocab_labels",
    "build_exect_frequency_pre_vocab_labels_high_precision",
    "exect_frequency_benchmark_bridge",
    "filter_gan_temporal_candidate_for_exect",
    "format_exect_frequency_pre_vocab_note",
    "format_exect_frequency_pre_vocab_note_high_precision",
    "note_has_exect_frequency_support",
    "recover_exect_frequency_benchmark_values",
    "recover_exect_frequency_benchmark_values_with_multi_label_retention",
    "recover_exect_frequency_benchmark_values_with_post_merge",
    "repair_exect_frequency_surface",
]
