from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.datasets.exect import load_exect_gold_documents
from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.paths import PROJECT_ROOT


DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "data" / "manifests" / "dataset_manifest.json"


@dataclass(frozen=True)
class ManifestIssue:
    dataset: str
    message: str


def load_dataset_manifest(path: Path = DEFAULT_MANIFEST_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_dataset_manifest(path: Path = DEFAULT_MANIFEST_PATH) -> list[ManifestIssue]:
    manifest = load_dataset_manifest(path)
    issues: list[ManifestIssue] = []

    datasets = manifest.get("datasets", {})
    _validate_exect_manifest(datasets.get("exectv2", {}), issues)
    _validate_gan_manifest(datasets.get("gan_2026", {}), issues)
    return issues


def require_valid_dataset_manifest(path: Path = DEFAULT_MANIFEST_PATH) -> None:
    issues = validate_dataset_manifest(path)
    if issues:
        detail = "; ".join(f"{issue.dataset}: {issue.message}" for issue in issues)
        raise ValueError(f"Dataset manifest validation failed: {detail}")


def _validate_exect_manifest(entry: dict[str, Any], issues: list[ManifestIssue]) -> None:
    dataset = "exectv2"
    root = _project_path(entry.get("root", ""))
    letters_dir = _project_path(entry.get("letters_dir", ""))
    json_dir = _project_path(entry.get("json_annotations_dir", ""))
    split_file = _project_path(entry.get("derived_split_file", ""))

    _require_path(dataset, root, "root", issues)
    _require_path(dataset, letters_dir, "letters_dir", issues)
    _require_path(dataset, json_dir, "json_annotations_dir", issues)
    _require_path(dataset, split_file, "derived_split_file", issues)

    documents = entry.get("documents", [])
    expected_count = entry.get("document_count")
    loaded_documents = load_exect_gold_documents(exect_root=root)
    loaded_ids = [document.document_id for document in loaded_documents]

    if expected_count != len(loaded_documents):
        issues.append(
            ManifestIssue(
                dataset,
                f"document_count={expected_count} does not match loaded count {len(loaded_documents)}",
            )
        )
    if documents != loaded_ids:
        issues.append(ManifestIssue(dataset, "documents list does not match loaded ExECT JSON ids"))

    if split_file.exists():
        _validate_split_file(dataset, split_file, set(loaded_ids), issues)


def _validate_gan_manifest(entry: dict[str, Any], issues: list[ManifestIssue]) -> None:
    dataset = "gan_2026"
    root = _project_path(entry.get("root", ""))
    primary_file = _project_path(entry.get("primary_file", ""))
    split_file = _project_path(entry.get("derived_split_file", ""))

    _require_path(dataset, root, "root", issues)
    _require_path(dataset, primary_file, "primary_file", issues)
    _require_path(dataset, split_file, "derived_split_file", issues)

    records = load_gan_records(primary_file if primary_file.exists() else None)
    record_ids = [record.record_id for record in records]
    expected_count = entry.get("record_count")

    if expected_count != len(records):
        issues.append(
            ManifestIssue(
                dataset,
                f"record_count={expected_count} does not match loaded count {len(records)}",
            )
        )

    if split_file.exists():
        _validate_split_file(dataset, split_file, set(record_ids), issues)


def _validate_split_file(
    dataset: str,
    path: Path,
    expected_ids: set[str],
    issues: list[ManifestIssue],
) -> None:
    split = json.loads(path.read_text(encoding="utf-8"))
    train_ids = split.get("train") or split.get("development", [])
    assigned_ids = train_ids + split.get("validation", []) + split.get("test", [])
    assigned_set = set(assigned_ids)

    if len(assigned_ids) != len(assigned_set):
        issues.append(ManifestIssue(dataset, f"{path} contains duplicate split assignments"))
    if assigned_set != expected_ids:
        missing = len(expected_ids - assigned_set)
        extra = len(assigned_set - expected_ids)
        issues.append(
            ManifestIssue(
                dataset,
                f"{path} split ids differ from loaded ids: missing={missing}, extra={extra}",
            )
        )

    expected_counts = {
        "train": len(train_ids),
        "validation": len(split.get("validation", [])),
        "test": len(split.get("test", [])),
    }
    if split.get("counts") != expected_counts:
        issues.append(ManifestIssue(dataset, f"{path} counts do not match split lengths"))


def _require_path(dataset: str, path: Path, field: str, issues: list[ManifestIssue]) -> None:
    if not path.exists():
        issues.append(ManifestIssue(dataset, f"{field} does not exist: {path}"))


def _project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path
