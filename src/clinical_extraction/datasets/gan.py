from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.gan.frequency import normalize_label
from clinical_extraction.paths import GAN_ROOT
from clinical_extraction.schemas import GanRecord

FREQUENCY_KEY = "check__Seizure Frequency Number"


def load_gan_records(path: Path | None = None) -> list[GanRecord]:
    source_path = path or GAN_ROOT / "synthetic_data_subset_1500.json"
    raw_records = json.loads(source_path.read_text(encoding="utf-8"))
    return [_parse_gan_record(raw) for raw in raw_records]


def _parse_gan_record(raw: dict[str, Any]) -> GanRecord:
    frequency = raw[FREQUENCY_KEY]
    gold = frequency["seizure_frequency_number"]
    reference = frequency.get("reference") or [None, None]

    source_row_index = int(raw["source_row_index"])
    gold_label = normalize_label(gold[0])
    reference_label = normalize_label(reference[0]) if reference[0] else None
    row_ok = bool(raw["row_ok"])

    flags = _flags(
        gold_label=gold_label,
        reference_label=reference_label,
        row_ok=row_ok,
        quote_issue_categories=str(raw.get("quote_issue_categories", "")),
    )

    return GanRecord(
        record_id=f"gan_{source_row_index}",
        source_row_index=source_row_index,
        note_text=raw["clinic_date"],
        gold_label=gold_label,
        gold_evidence=gold[1] if len(gold) > 1 else None,
        reference_label=reference_label,
        reference_evidence=reference[1] if len(reference) > 1 else None,
        row_ok=row_ok,
        labels_match_all_categories=bool(raw["labels_match_all_categories"]),
        quotes_ok_all_categories=bool(raw["quotes_ok_all_categories"]),
        flags=flags,
        raw=raw,
    )


def _flags(
    *,
    gold_label: str,
    reference_label: str | None,
    row_ok: bool,
    quote_issue_categories: str,
) -> list[str]:
    flags: list[str] = []
    if reference_label is not None and gold_label != reference_label:
        flags.extend(["label_reference_disagreement", "hard_case"])
    if gold_label == "unknown":
        flags.append("unknown")
    if gold_label == "no seizure frequency reference":
        flags.append("no_seizure_frequency_reference")
    if not row_ok:
        flags.append("row_not_ok")
    if not row_ok and gold_label == "no seizure frequency reference":
        flags.append("admin_or_nonclinical")
    if "Seizure Frequency Number" in quote_issue_categories:
        flags.append("frequency_quote_issue")
    return flags

