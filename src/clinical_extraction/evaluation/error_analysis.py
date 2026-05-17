from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


class ErrorTaxonomy:
    """Collect bounded examples for evaluation failure categories."""

    def __init__(self, *, max_examples: int = 20) -> None:
        self.max_examples = max_examples
        self._counts: Counter[str] = Counter()
        self._examples: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def add(
        self,
        category: str,
        *,
        record_id: str,
        reason: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self._counts[category] += 1
        examples = self._examples[category]
        if len(examples) >= self.max_examples:
            return
        example = {
            "record_id": record_id,
            "reason": reason,
        }
        if details:
            example.update(details)
        examples.append(example)

    def to_report(self) -> dict[str, Any]:
        categories = sorted(self._counts)
        return {
            "counts": {category: self._counts[category] for category in categories},
            "examples": {
                category: self._examples.get(category, []) for category in categories
            },
        }
