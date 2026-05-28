from __future__ import annotations

import pytest

from clinical_extraction.fixtures.primitive_cases import (
    DEFAULT_PRIMITIVE_CASES_PATH,
    REQUIRED_FAILURE_MODES,
    assert_primitive_fixture_case,
    invoke_primitive_fixture_case,
    load_primitive_cases,
    primitive_cases_by_id,
    primitive_cases_for_primitive,
)
from clinical_extraction.paths import PROJECT_ROOT
from clinical_extraction.primitives import primitive_registry_by_id


def test_primitive_cases_fixture_loads_from_project_root():
    payload = load_primitive_cases()
    cases = payload.cases

    assert payload.name == "primitive_cases_v1"
    assert len(cases) >= 12
    assert len({case.case_id for case in cases}) == len(cases)


def test_primitive_cases_fixture_path_is_windows_portable():
    path = DEFAULT_PRIMITIVE_CASES_PATH.resolve()
    assert path == (PROJECT_ROOT / "data" / "fixtures" / "primitive_cases.json").resolve()
    assert path.exists()
    assert path.read_text(encoding="utf-8").strip().startswith("{")


def test_primitive_cases_cover_required_failure_modes():
    payload = load_primitive_cases()
    failure_modes = {case.failure_mode for case in payload.cases}

    assert REQUIRED_FAILURE_MODES.issubset(failure_modes)


def test_primitive_cases_reference_registered_primitives():
    registry = primitive_registry_by_id()
    payload = load_primitive_cases()

    for case in payload.cases:
        assert case.primitive_id in registry, case.case_id


def test_primitive_cases_by_id_lookup_is_deterministic():
    first = primitive_cases_by_id()
    second = primitive_cases_by_id()

    assert first == second
    assert "shared.evidence.exact_substring.v1" in first


@pytest.mark.parametrize(
    "case_id",
    [
        "shared.evidence.exact_substring.v1",
        "shared.evidence.unsupported_quote.v1",
        "gan.frequency.evidence_guard.elided.v1",
        "gan.frequency.label_policy.unknown.v1",
        "exect.medication.rx_candidates.planned.v1",
        "exect.medication_temporality.previous.v1",
        "exect.frequency.benchmark_bridge.abstention.v1",
    ],
)
def test_parametrized_primitive_fixture_cases_pass(case_id: str):
    case = primitive_cases_by_id()[case_id]
    assert_primitive_fixture_case(case)


def test_primitive_cases_for_primitive_filters_by_id():
    cases = primitive_cases_for_primitive("shared.evidence.substring_support.v1")

    assert cases
    assert all(
        case.primitive_id == "shared.evidence.substring_support.v1" for case in cases
    )


def test_invoke_returns_evidence_result_for_shared_substring_case():
    case = primitive_cases_by_id()["shared.evidence.exact_substring.v1"]
    result = invoke_primitive_fixture_case(case)

    assert result.support_status == "exact_substring"
    assert result.raw_quote_supported


def test_primitive_fixture_registry_entry_is_implemented():
    registry = primitive_registry_by_id()
    fixture = registry["shared.fixtures.primitive_cases.v1"]

    assert fixture.status == "implemented"
    assert fixture.clinical_operation == "fixture_definition"
    assert "eval_only" in fixture.interleaving_positions
