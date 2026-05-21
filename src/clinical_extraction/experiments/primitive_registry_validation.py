"""Validate typed primitive registry, catalog, fixtures, and adapter bindings."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from clinical_extraction.fixtures.primitive_cases import load_primitive_cases
from clinical_extraction.interleaving_adapters import PRIMITIVE_BINDINGS
from clinical_extraction.primitives import PRIMITIVE_REGISTRY, primitive_registry_by_id

IssueLevel = Literal["error", "warning"]

CATALOG_PATH = Path("docs/taxonomy/taxonomy_primitive_catalog.md")
PRIMITIVE_ID_PATTERN = re.compile(r"`([a-z0-9]+(?:\.[a-z0-9_]+)+\.v[0-9]+)`")


@dataclass(frozen=True)
class ValidationIssue:
    level: IssueLevel
    message: str


def extract_catalog_primitive_ids(catalog_text: str) -> set[str]:
    return set(PRIMITIVE_ID_PATTERN.findall(catalog_text))


def validate_registry_uniqueness() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    ids = [primitive.primitive_id for primitive in PRIMITIVE_REGISTRY]
    duplicates = {item for item in ids if ids.count(item) > 1}
    for duplicate in sorted(duplicates):
        issues.append(
            ValidationIssue(
                level="error",
                message=f"Duplicate primitive_id in registry: {duplicate}",
            )
        )
    return issues


def validate_catalog_registry_alignment(
    repo_root: Path,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    catalog_path = repo_root / CATALOG_PATH
    if not catalog_path.exists():
        issues.append(
            ValidationIssue(
                level="error",
                message=f"Missing primitive catalog: {catalog_path}",
            )
        )
        return issues

    catalog_ids = extract_catalog_primitive_ids(catalog_path.read_text(encoding="utf-8"))
    registry_ids = set(primitive_registry_by_id())
    missing_from_registry = sorted(catalog_ids - registry_ids)
    for primitive_id in missing_from_registry:
        issues.append(
            ValidationIssue(
                level="error",
                message=(
                    f"Catalog primitive {primitive_id} is missing from typed registry."
                ),
            )
        )

    undocumented = sorted(
        primitive_id
        for primitive_id in registry_ids
        if primitive_id not in catalog_ids
        and not primitive_id.startswith("shared.")
    )
    for primitive_id in undocumented:
        issues.append(
            ValidationIssue(
                level="warning",
                message=(
                    f"Registry primitive {primitive_id} is not listed in the catalog."
                ),
            )
        )
    return issues


def validate_fixture_primitive_references(repo_root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    fixture_path = repo_root / "data" / "fixtures" / "primitive_cases.json"
    if not fixture_path.exists():
        issues.append(
            ValidationIssue(
                level="error",
                message=f"Missing primitive fixture library: {fixture_path}",
            )
        )
        return issues

    registry = primitive_registry_by_id()
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    for case in payload.get("cases", []):
        primitive_id = case.get("primitive_id")
        if primitive_id not in registry:
            issues.append(
                ValidationIssue(
                    level="error",
                    message=(
                        f"Fixture case {case.get('case_id')} references unknown "
                        f"primitive_id {primitive_id!r}."
                    ),
                )
            )

    try:
        load_primitive_cases(fixture_path)
    except Exception as exc:  # pragma: no cover - surfaced as validation issue
        issues.append(
            ValidationIssue(
                level="error",
                message=f"Primitive fixture library failed to load: {exc}",
            )
        )
    return issues


def validate_interleaving_bindings() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    registry = primitive_registry_by_id()
    for primitive_id, binding in PRIMITIVE_BINDINGS.items():
        metadata = registry.get(primitive_id)
        if metadata is None:
            issues.append(
                ValidationIssue(
                    level="error",
                    message=(
                        f"Interleaving binding exists for unknown primitive {primitive_id}."
                    ),
                )
            )
            continue
        if metadata.status != "implemented":
            issues.append(
                ValidationIssue(
                    level="warning",
                    message=(
                        f"Interleaving binding for {primitive_id} has status "
                        f"{metadata.status!r}."
                    ),
                )
            )
        extended = set(binding.renderers) - set(metadata.interleaving_positions)
        if extended:
            issues.append(
                ValidationIssue(
                    level="warning",
                    message=(
                        f"Interleaving binding for {primitive_id} exposes adapter-extended "
                        f"positions {sorted(extended)} beyond registry metadata "
                        f"{metadata.interleaving_positions}."
                    ),
                )
            )
    return issues


def validate_implementation_refs(repo_root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for primitive in PRIMITIVE_REGISTRY:
        if primitive.status != "implemented":
            continue
        if not primitive.implementation_refs:
            issues.append(
                ValidationIssue(
                    level="warning",
                    message=(
                        f"Implemented primitive {primitive.primitive_id} has no "
                        "implementation_refs."
                    ),
                )
            )
            continue
        for ref in primitive.implementation_refs:
            if ref.startswith("docs/"):
                path = repo_root / ref
            else:
                path = repo_root / ref
            if not path.exists():
                issues.append(
                    ValidationIssue(
                        level="warning",
                        message=(
                            f"Primitive {primitive.primitive_id} implementation_ref "
                            f"does not exist: {ref}"
                        ),
                    )
                )
    return issues


def validate_primitive_registry(repo_root: Path | None = None) -> list[ValidationIssue]:
    root = repo_root or Path.cwd()
    issues: list[ValidationIssue] = []
    issues.extend(validate_registry_uniqueness())
    issues.extend(validate_catalog_registry_alignment(root))
    issues.extend(validate_fixture_primitive_references(root))
    issues.extend(validate_interleaving_bindings())
    issues.extend(validate_implementation_refs(root))
    return issues


def validation_failed(issues: list[ValidationIssue]) -> bool:
    return any(issue.level == "error" for issue in issues)


def format_validation_report(issues: list[ValidationIssue]) -> str:
    lines = ["Primitive registry validation issues:"]
    for issue in issues:
        lines.append(f"[{issue.level}] {issue.message}")
    return "\n".join(lines)
