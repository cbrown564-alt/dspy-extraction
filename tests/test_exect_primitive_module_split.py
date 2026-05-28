from __future__ import annotations

from clinical_extraction.exect import primitives as legacy_primitives
from clinical_extraction.exect.diagnosis_primitives import (
    exect_diagnosis_benchmark_bridge,
)
from clinical_extraction.exect.frequency_primitives import (
    build_exect_frequency_pre_vocab_labels,
)
from clinical_extraction.exect.medication_primitives import (
    build_exect_medication_candidate_payloads,
)
from clinical_extraction.exect.seizure_type_primitives import (
    exect_seizure_type_benchmark_bridge,
)


def test_legacy_exect_primitives_facade_reexports_family_modules():
    assert (
        legacy_primitives.build_exect_medication_candidate_payloads
        is build_exect_medication_candidate_payloads
    )
    assert (
        legacy_primitives.exect_diagnosis_benchmark_bridge
        is exect_diagnosis_benchmark_bridge
    )
    assert (
        legacy_primitives.exect_seizure_type_benchmark_bridge
        is exect_seizure_type_benchmark_bridge
    )
    assert (
        legacy_primitives.build_exect_frequency_pre_vocab_labels
        is build_exect_frequency_pre_vocab_labels
    )


def test_legacy_exect_primitives_preserves_existing_private_imports():
    assert legacy_primitives._BRAND_SURFACES["lamictal"] == "lamotrigine"
    assert legacy_primitives.canonical_medication_name("Lamictal") == "lamictal"
