"""Load and execute deterministic primitive fixture cases."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import Field

from clinical_extraction.exect.frequency_payload import (
    build_exect_frequency_candidate_payloads,
    exect_frequency_benchmark_bridge,
)
from clinical_extraction.exect.primitives import (
    build_exect_medication_candidate_payloads,
    exect_diagnosis_benchmark_bridge,
    exect_medication_benchmark_bridge,
    exect_seizure_type_benchmark_bridge,
    infer_exect_medication_temporality,
)
from clinical_extraction.gan.primitives import (
    build_gan_frequency_candidate_payloads,
    check_gan_frequency_evidence_guard,
    gan_frequency_label_policy_bridge,
)
from clinical_extraction.paths import PROJECT_ROOT
from clinical_extraction.primitives import (
    EvidenceSupportResult,
    NormalizationResult,
    PrimitiveCandidate,
    PrimitiveDatasetValue,
    PrimitiveFieldFamilyValue,
    check_evidence_support,
)
from clinical_extraction.schemas import FrozenModel

PrimitiveFailureModeValue = Literal[
    "positive",
    "negative",
    "ambiguous",
    "absent",
    "historical",
    "planned",
    "unsupported_evidence",
]

REQUIRED_FAILURE_MODES: frozenset[str] = frozenset(
    {
        "positive",
        "negative",
        "ambiguous",
        "absent",
        "historical",
        "planned",
        "unsupported_evidence",
    }
)

DEFAULT_PRIMITIVE_CASES_PATH = PROJECT_ROOT / "data" / "fixtures" / "primitive_cases.json"


class PrimitiveFixtureCase(FrozenModel):
    """One deterministic primitive example with inputs and expected assertions."""

    case_id: str = Field(pattern=r"^[a-z0-9]+(\.[a-z0-9_]+)+\.v[0-9]+$")
    primitive_id: str = Field(pattern=r"^[a-z0-9]+(\.[a-z0-9_]+)+\.v[0-9]+$")
    dataset: PrimitiveDatasetValue
    field_family: PrimitiveFieldFamilyValue
    failure_mode: PrimitiveFailureModeValue
    inputs: dict[str, Any]
    expected: dict[str, Any]


class PrimitiveFixtureLibrary(FrozenModel):
    """Fixture library payload for taxonomy primitive unit tests."""

    name: str
    description: str
    cases: list[PrimitiveFixtureCase] = Field(min_length=1)


def load_primitive_cases(
    path: Path = DEFAULT_PRIMITIVE_CASES_PATH,
) -> PrimitiveFixtureLibrary:
    """Load the primitive fixture library from disk using UTF-8 and repo-root paths."""

    resolved = path if path.is_absolute() else (PROJECT_ROOT / path).resolve()
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    library = PrimitiveFixtureLibrary.model_validate(payload)
    case_ids = [case.case_id for case in library.cases]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError(f"{resolved} contains duplicate case_id values.")
    return library


@lru_cache(maxsize=1)
def primitive_cases_by_id(
    path: Path = DEFAULT_PRIMITIVE_CASES_PATH,
) -> dict[str, PrimitiveFixtureCase]:
    library = load_primitive_cases(path)
    return {case.case_id: case for case in library.cases}


def primitive_cases_for_primitive(
    primitive_id: str,
    path: Path = DEFAULT_PRIMITIVE_CASES_PATH,
) -> list[PrimitiveFixtureCase]:
    return [
        case
        for case in load_primitive_cases(path).cases
        if case.primitive_id == primitive_id
    ]


def invoke_primitive_fixture_case(
    case: PrimitiveFixtureCase,
) -> (
    EvidenceSupportResult
    | NormalizationResult
    | list[NormalizationResult]
    | list[PrimitiveCandidate]
):
    """Invoke the primitive referenced by a fixture case."""

    inputs = case.inputs
    primitive_id = case.primitive_id

    if primitive_id == "shared.evidence.substring_support.v1":
        return check_evidence_support(
            document_text=inputs["document_text"],
            quote=inputs.get("quote"),
            normalized_value=inputs.get("normalized_value"),
            interpretation_evidence_text=inputs.get("interpretation_evidence_text"),
            primitive_id=primitive_id,
        )
    if primitive_id == "gan.frequency.evidence_guard.v1":
        return check_gan_frequency_evidence_guard(
            note_text=inputs["note_text"],
            evidence_text=inputs.get("evidence_text"),
            label=inputs["label"],
        )
    if primitive_id == "gan.frequency.label_policy_bridge.v1":
        return gan_frequency_label_policy_bridge(inputs["label"])
    if primitive_id == "gan.frequency.temporal_candidates.v1":
        return build_gan_frequency_candidate_payloads(inputs["note_text"])
    if primitive_id == "exect.medication.rx_candidates.v1":
        return build_exect_medication_candidate_payloads(inputs["note_text"])
    if primitive_id == "exect.medication_temporality.post_classifier.v1":
        return infer_exect_medication_temporality(inputs.get("evidence_text"))
    if primitive_id == "exect.medication.benchmark_bridge.v1":
        return exect_medication_benchmark_bridge(
            inputs["raw_value"],
            note_text=inputs.get("note_text", ""),
            evidence_text=inputs.get("evidence_text"),
        )
    if primitive_id == "exect.frequency.rate_candidates.v1":
        return build_exect_frequency_candidate_payloads(inputs["note_text"])
    if primitive_id == "exect.frequency.benchmark_bridge.v1":
        return exect_frequency_benchmark_bridge(
            inputs["raw_values"],
            note_text=inputs.get("note_text", ""),
        )
    if primitive_id == "exect.diagnosis.benchmark_bridge.v1":
        return exect_diagnosis_benchmark_bridge(inputs["raw_value"])
    if primitive_id == "exect.seizure_type.benchmark_bridge.v1":
        return exect_seizure_type_benchmark_bridge(inputs["raw_value"])

    raise ValueError(f"No fixture invoker registered for primitive_id={primitive_id!r}.")


def assert_primitive_fixture_case(case: PrimitiveFixtureCase) -> None:
    """Run a fixture case and assert its expected fields."""

    result = invoke_primitive_fixture_case(case)
    expected = case.expected

    if isinstance(result, EvidenceSupportResult):
        _assert_mapping(result.model_dump(), expected, label=case.case_id)
        return

    if isinstance(result, NormalizationResult):
        _assert_normalization_result(result, expected, case.case_id)
        return

    if isinstance(result, list) and result and isinstance(result[0], NormalizationResult):
        _assert_normalization_results(result, expected, case.case_id)
        return

    if isinstance(result, list) and (
        not result or isinstance(result[0], PrimitiveCandidate)
    ):
        _assert_candidate_results(result, expected, case.case_id)
        return

    raise AssertionError(
        f"{case.case_id}: unsupported fixture result type {type(result)!r}."
    )


def _assert_normalization_result(
    result: NormalizationResult,
    expected: dict[str, Any],
    case_id: str,
) -> None:
    if "benchmark_values" in expected:
        raise AssertionError(
            f"{case_id}: expected.benchmark_values requires a list result."
        )
    _assert_mapping(result.model_dump(), expected, label=case_id)


def _assert_normalization_results(
    results: list[NormalizationResult],
    expected: dict[str, Any],
    case_id: str,
) -> None:
    if "benchmark_values" in expected:
        actual = [result.benchmark_value for result in results]
        assert actual == expected["benchmark_values"], (
            f"{case_id}: benchmark_values mismatch: {actual!r} != "
            f"{expected['benchmark_values']!r}"
        )
    if "metadata_contains" in expected:
        metadata = results[0].metadata if results else {}
        _assert_metadata_contains(metadata, expected["metadata_contains"], case_id)
    if "metadata_flag_contains" in expected:
        flags = results[0].metadata.get("bridge_flags", []) if results else []
        assert expected["metadata_flag_contains"] in flags, (
            f"{case_id}: expected bridge flag missing from {flags!r}"
        )


def _assert_candidate_results(
    candidates: list[PrimitiveCandidate],
    expected: dict[str, Any],
    case_id: str,
) -> None:
    if "contains_benchmark_values" in expected:
        actual = {
            candidate.benchmark_value
            for candidate in candidates
            if candidate.benchmark_value is not None
        }
        required = set(expected["contains_benchmark_values"])
        assert required.issubset(actual), (
            f"{case_id}: missing benchmark values {required - actual!r} in {actual!r}"
        )
    if "contains_raw_texts" in expected:
        actual = {candidate.raw_text for candidate in candidates}
        required = set(expected["contains_raw_texts"])
        assert required.issubset(actual), (
            f"{case_id}: missing raw texts {required - actual!r} in {actual!r}"
        )
    if "metadata_contains" in expected:
        raw_text = expected.get("contains_raw_texts", [None])[0]
        candidate = next(
            (item for item in candidates if item.raw_text == raw_text),
            candidates[0] if candidates else None,
        )
        assert candidate is not None, f"{case_id}: no candidates to inspect."
        _assert_metadata_contains(
            candidate.metadata, expected["metadata_contains"], case_id
        )
    raw_text = expected.get("benchmark_value_is_null_for_raw_text")
    if raw_text is not None:
        candidate = next(item for item in candidates if item.raw_text == raw_text)
        assert candidate.benchmark_value is None, (
            f"{case_id}: expected null benchmark_value for raw_text={raw_text!r}."
        )


def _assert_metadata_contains(
    metadata: dict[str, Any],
    expected_metadata: dict[str, Any],
    case_id: str,
) -> None:
    for key, value in expected_metadata.items():
        assert metadata.get(key) == value, (
            f"{case_id}: metadata[{key!r}] == {metadata.get(key)!r}, expected {value!r}"
        )


def _assert_mapping(
    actual: dict[str, Any],
    expected: dict[str, Any],
    *,
    label: str,
) -> None:
    for key, value in expected.items():
        if key in {
            "metadata_contains",
            "metadata_flag_contains",
            "contains_benchmark_values",
            "contains_raw_texts",
            "benchmark_value_is_null_for_raw_text",
            "benchmark_values",
        }:
            continue
        assert actual.get(key) == value, (
            f"{label}: field {key!r} == {actual.get(key)!r}, expected {value!r}"
        )
    if "metadata_contains" in expected:
        _assert_metadata_contains(
            actual.get("metadata", {}),
            expected["metadata_contains"],
            label,
        )
