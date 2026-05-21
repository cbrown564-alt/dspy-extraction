from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from typing import Any, Iterable

from clinical_extraction.gan.frequency import pragmatic_category, purist_category
from clinical_extraction.schemas import GanRecord

DEFAULT_GAN_SPLIT_SALT = "gan-2026-fixed-splits-v1"
GAN_SPLIT_RATIOS = {
    "train": 0.6,
    "validation": 0.2,
    "test": 0.2,
}


def make_gan_splits(
    records: Iterable[GanRecord],
    *,
    salt: str = DEFAULT_GAN_SPLIT_SALT,
) -> dict[str, Any]:
    records = list(records)
    strata: dict[str, list[GanRecord]] = defaultdict(list)
    for record in records:
        strata[_gan_stratum(record)].append(record)

    split_ids = {"train": [], "validation": [], "test": []}
    stratum_counts: dict[str, dict[str, int]] = {}

    for stratum, stratum_records in sorted(strata.items()):
        ordered = sorted(
            stratum_records,
            key=lambda record: _stable_key(record.record_id, salt),
        )
        n = len(ordered)
        dev_n = round(n * 0.6)
        val_n = round(n * 0.2)
        buckets = {
            "train": ordered[:dev_n],
            "validation": ordered[dev_n : dev_n + val_n],
            "test": ordered[dev_n + val_n :],
        }
        stratum_counts[stratum] = {}
        for split, bucket in buckets.items():
            split_ids[split].extend(record.record_id for record in bucket)
            stratum_counts[stratum][split] = len(bucket)

    for split in split_ids:
        split_ids[split].sort(key=lambda record_id: _stable_key(record_id, salt))

    return {
        "name": "gan_2026_fixed_v1",
        "method": "sha256(record_id, salt) deterministic stratified 60/20/20 split",
        "salt": salt,
        "split_ratios": GAN_SPLIT_RATIOS,
        "allocation_policy": (
            "Within each stratum, records are sorted by sha256(record_id:salt); "
            "train and validation counts are round(n * ratio), and the "
            "remaining records are assigned to test."
        ),
        "split_policy": (
            "train: optimizer compile only (no benchmark eval configs). "
            "validation: routine eval. test: holdout with report_on_test_split."
        ),
        "counts": {split: len(ids) for split, ids in split_ids.items()},
        "stratification": {
            "fields": [
                "pragmatic_category",
                "purist_category",
                "row_ok",
                "label_reference_disagreement",
            ],
            "hard_case_definition": (
                "Records whose primary gold label differs from the secondary "
                "reference label; these are kept as a stratification field."
            ),
            "hard_case_counts": _flag_counts_by_split(records, split_ids, "hard_case"),
            "stratum_counts": stratum_counts,
            "label_counts": dict(Counter(record.gold_label for record in records)),
        },
        **split_ids,
    }


def _gan_stratum(record: GanRecord) -> str:
    disagreement = "label_reference_disagreement" in record.flags
    return "|".join(
        [
            pragmatic_category(record.gold_label),
            purist_category(record.gold_label),
            f"row_ok={record.row_ok}",
            f"disagreement={disagreement}",
        ]
    )


def _stable_key(record_id: str, salt: str) -> str:
    return hashlib.sha256(f"{record_id}:{salt}".encode("utf-8")).hexdigest()


def _flag_counts_by_split(
    records: list[GanRecord],
    split_ids: dict[str, list[str]],
    flag: str,
) -> dict[str, int]:
    records_by_id = {record.record_id: record for record in records}
    return {
        split: sum(flag in records_by_id[record_id].flags for record_id in ids)
        for split, ids in split_ids.items()
    }
