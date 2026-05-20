from __future__ import annotations

from pathlib import Path

from clinical_extraction.experiments.primitive_registry_validation import (
    extract_catalog_primitive_ids,
    validate_primitive_registry,
    validation_failed,
)
from clinical_extraction.primitives import PRIMITIVE_REGISTRY, primitive_registry_by_id


def test_primitive_registry_has_unique_ids():
    ids = [primitive.primitive_id for primitive in PRIMITIVE_REGISTRY]
    assert len(ids) == len(set(ids))


def test_planned_exect_family_backlog_is_registered():
    registry = primitive_registry_by_id()
    assert registry["exect.investigation.surface_bridge.v1"].status == "planned"
    assert registry["exect.onset.cui_phrase_bridge.v1"].field_families == ["onset"]


def test_validate_primitive_registry_passes_for_repo():
    issues = validate_primitive_registry(Path.cwd())
    assert not validation_failed(issues), issues


def test_extract_catalog_primitive_ids_finds_backtick_ids():
    text = "| `exect.medication.benchmark_bridge.v1` | ExECTv2 |"
    assert extract_catalog_primitive_ids(text) == {"exect.medication.benchmark_bridge.v1"}
