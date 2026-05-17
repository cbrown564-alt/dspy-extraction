from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HIGH_PRIORITY_PREFIXES = (
    "normalization.",
    "classification.",
    "evidence.",
)


def build_review_queue_items(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten bounded evaluation examples into deterministic review items."""

    error_analysis = report.get("error_analysis", {})
    counts = error_analysis.get("counts", {})
    examples_by_category = error_analysis.get("examples", {})
    dataset = report.get("dataset")
    schema_level = report.get("schema_level")
    scorer = report.get("scorer")

    items: list[dict[str, Any]] = []
    for category in sorted(examples_by_category):
        examples = examples_by_category[category]
        for index, example in enumerate(examples, start=1):
            record_id = example["record_id"]
            reason = example.get("reason", "")
            details = {
                key: value
                for key, value in example.items()
                if key not in {"record_id", "reason"}
            }
            items.append(
                {
                    "review_id": f"{dataset}:{record_id}:{category}:{index}",
                    "dataset": dataset,
                    "schema_level": schema_level,
                    "scorer": scorer,
                    "record_id": record_id,
                    "category": category,
                    "category_count": counts.get(category, len(examples)),
                    "reason": reason,
                    "priority": _priority_for_category(category),
                    "details": details,
                }
            )
    return items


def write_review_queue_jsonl(report: dict[str, Any], output_path: Path) -> int:
    items = build_review_queue_items(report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "".join(json.dumps(item, sort_keys=True) + "\n" for item in items),
        encoding="utf-8",
    )
    return len(items)


def _priority_for_category(category: str) -> str:
    if category.startswith(HIGH_PRIORITY_PREFIXES):
        return "high"
    if category.startswith(("schema.", "abstention.", "repair.")):
        return "medium"
    return "low"
