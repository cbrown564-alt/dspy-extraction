"""ExECT benchmark-facing seizure-frequency slot payloads for S4 Axis-3 probes."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from clinical_extraction.exect.primitives import build_exect_frequency_pre_vocab_labels

ExectFrequencySlotType = str

SLOT_TYPE_QUANTIFIED = "quantified_rate"
SLOT_TYPE_ZERO_RATE = "zero_rate"
SLOT_TYPE_QUALITATIVE = "qualitative_change"
SLOT_TYPE_SEIZURE_FREE = "seizure_free"

_QUANTIFIED_SLOT_RE = re.compile(
    r"^(?P<count>\d+) per (?P<period_count>\d+) (?P<period>week|month|day|year)$"
)
_ZERO_RATE_SLOT_RE = re.compile(
    r"^0 per (?P<period_count>\d+) (?P<period>week|month|day|year)$"
)
_SEIZURE_FREE_SINCE_RE = re.compile(r"^seizure free since (?P<year>\d{4})$")


@dataclass(frozen=True)
class ExectFrequencySlotPayload:
    """Structured ExECT frequency slot — not Gan monthly normalization."""

    slot_type: ExectFrequencySlotType
    benchmark_label: str
    count: str | None
    period_count: str | None
    period_unit: str | None
    multi_label_group: str
    retention_policy: str


def classify_exect_frequency_slot_type(benchmark_label: str) -> ExectFrequencySlotType:
    if benchmark_label in {
        "frequency increased",
        "frequency decreased",
        "infrequent",
    }:
        return SLOT_TYPE_QUALITATIVE
    if benchmark_label == "seizure free" or _SEIZURE_FREE_SINCE_RE.match(benchmark_label):
        return SLOT_TYPE_SEIZURE_FREE
    if _ZERO_RATE_SLOT_RE.match(benchmark_label):
        return SLOT_TYPE_ZERO_RATE
    if _QUANTIFIED_SLOT_RE.match(benchmark_label):
        return SLOT_TYPE_QUANTIFIED
    return SLOT_TYPE_QUALITATIVE


def enrich_exect_frequency_label_to_slot(benchmark_label: str) -> ExectFrequencySlotPayload:
    slot_type = classify_exect_frequency_slot_type(benchmark_label)
    count: str | None = None
    period_count: str | None = None
    period_unit: str | None = None

    if slot_type == SLOT_TYPE_QUANTIFIED:
        match = _QUANTIFIED_SLOT_RE.match(benchmark_label)
        assert match is not None
        count = match.group("count")
        period_count = match.group("period_count")
        period_unit = match.group("period")
    elif slot_type == SLOT_TYPE_ZERO_RATE:
        match = _ZERO_RATE_SLOT_RE.match(benchmark_label)
        assert match is not None
        count = "0"
        period_count = match.group("period_count")
        period_unit = match.group("period")

    multi_label_group = (
        "rate_block"
        if slot_type in {SLOT_TYPE_QUANTIFIED, SLOT_TYPE_ZERO_RATE, SLOT_TYPE_QUALITATIVE}
        else "seizure_free_block"
    )
    return ExectFrequencySlotPayload(
        slot_type=slot_type,
        benchmark_label=benchmark_label,
        count=count,
        period_count=period_count,
        period_unit=period_unit,
        multi_label_group=multi_label_group,
        retention_policy="emit_all_supported_slots_in_group",
    )


def build_exect_frequency_slot_payloads(note_text: str) -> list[ExectFrequencySlotPayload]:
    labels = build_exect_frequency_pre_vocab_labels(note_text)
    return [enrich_exect_frequency_label_to_slot(label) for label in labels]


def slot_payload_to_dict(payload: ExectFrequencySlotPayload) -> dict[str, str | None]:
    return {
        "slot_type": payload.slot_type,
        "benchmark_label": payload.benchmark_label,
        "count": payload.count,
        "period_count": payload.period_count,
        "period_unit": payload.period_unit,
        "multi_label_group": payload.multi_label_group,
        "retention_policy": payload.retention_policy,
    }


def format_exect_frequency_slot_payload_for_prompt(note_text: str) -> str:
    """Inject ExECT structured frequency slots before the clinical note."""

    payloads = build_exect_frequency_slot_payloads(note_text)
    if not payloads:
        return note_text

    header = (
        "ExECT seizure-frequency structured slots (soft hints — emit every supported "
        "benchmark label; retain multi-label blocks; do not collapse rate + change):"
    )
    rows = [
        "| # | slot_type | benchmark_label | count | period_count | period_unit | "
        "multi_label_group | retention_policy |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for index, payload in enumerate(payloads, start=1):
        rows.append(
            "| "
            f"{index} | {payload.slot_type} | {payload.benchmark_label!r} | "
            f"{payload.count or ''} | {payload.period_count or ''} | "
            f"{payload.period_unit or ''} | {payload.multi_label_group} | "
            f"{payload.retention_policy} |"
        )

    json_block = json.dumps(
        {"frequency_slots": [slot_payload_to_dict(payload) for payload in payloads]},
        indent=2,
    )
    return "\n".join(
        [
            header,
            *rows,
            "",
            "Frequency slot JSON:",
            json_block,
            "",
            "---",
            "",
            note_text,
        ]
    )
