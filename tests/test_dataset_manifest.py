import json

import pytest

from clinical_extraction.datasets.manifest import (
    DEFAULT_MANIFEST_PATH,
    ManifestIssue,
    require_valid_dataset_manifest,
    validate_dataset_manifest,
)


def test_dataset_manifest_validates_raw_files_splits_and_counts():
    assert validate_dataset_manifest() == []


def test_dataset_manifest_validation_reports_count_mismatch(tmp_path):
    manifest = json.loads(DEFAULT_MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["datasets"]["gan_2026"]["record_count"] = 1499
    manifest_path = tmp_path / "dataset_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    issues = validate_dataset_manifest(manifest_path)

    assert ManifestIssue(
        "gan_2026",
        "record_count=1499 does not match loaded count 1500",
    ) in issues


def test_dataset_manifest_requirement_raises_for_invalid_manifest(tmp_path):
    manifest = json.loads(DEFAULT_MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["datasets"]["exectv2"]["derived_split_file"] = "data/splits/missing.json"
    manifest_path = tmp_path / "dataset_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="Dataset manifest validation failed"):
        require_valid_dataset_manifest(manifest_path)
