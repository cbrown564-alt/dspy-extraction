"""Inspection and decision document section contracts."""

from __future__ import annotations

from pathlib import Path

INSPECTION_REQUIRED_HEADINGS: tuple[str, ...] = (
    "## Taxonomy",
    "## Run scope and artifacts",
    "## Primitive use",
    "## Scorer mode",
    "## Normalization semantics",
    "## Evidence semantics",
    "## Headline metrics",
    "## Decisions",
    "## Caveats and interpretation",
)

DECISION_REQUIRED_HEADINGS: tuple[str, ...] = (
    "## Research question",
    "## Fixed controls (all arms)",
    "## Comparison group",
    "## Arms",
    "## Promotion gates",
    "## Normalization and evidence policy",
    "## Caveats",
)

INSPECTION_REQUIRED_KEYWORDS: tuple[str, ...] = (
    "comparison group",
    "scorer",
    "primitive",
    "normalization",
    "evidence",
    "caveat",
)

TEMPLATE_PATHS = {
    "inspection": Path("docs/templates/primitive_inspection_template.md"),
    "decision": Path("docs/templates/experiment_decision_template.md"),
}


def validate_template_file(path: Path, required_headings: tuple[str, ...]) -> list[str]:
    if not path.is_file():
        return [f"Missing template file: {path}"]
    text = path.read_text(encoding="utf-8")
    return [heading for heading in required_headings if heading not in text]


def validate_inspection_document(path: Path) -> list[str]:
    """Return missing headings/keywords for a primitive-aware inspection doc."""
    if not path.is_file():
        return [f"Missing inspection document: {path}"]
    text = path.read_text(encoding="utf-8").lower()
    issues: list[str] = []
    for heading in INSPECTION_REQUIRED_HEADINGS:
        if heading.lower() not in text:
            issues.append(f"Missing heading: {heading}")
    for keyword in INSPECTION_REQUIRED_KEYWORDS:
        if keyword not in text:
            issues.append(f"Missing keyword: {keyword}")
    return issues


def validate_decision_document(path: Path) -> list[str]:
    if not path.is_file():
        return [f"Missing decision document: {path}"]
    text = path.read_text(encoding="utf-8")
    return [heading for heading in DECISION_REQUIRED_HEADINGS if heading not in text]
