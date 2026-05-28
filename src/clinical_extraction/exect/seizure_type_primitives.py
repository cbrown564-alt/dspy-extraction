"""ExECT seizure-type taxonomy primitive and bridge helpers."""

from __future__ import annotations

import re

from clinical_extraction.datasets.exect import canonical_clinical_phrase
from clinical_extraction.primitives import NormalizationResult

EXECT_SEIZURE_TYPE_BENCHMARK_BRIDGE_PRIMITIVE_ID = (
    "exect.seizure_type.benchmark_bridge.v1"
)

_REJECTED_GRANULAR_SEIZURE_TYPES = frozenset(
    {
        "absences",
        "jerks",
        "occasional absences",
    }
)

_GRANULAR_SEIZURE_TYPE_COARSENING = {
    "focal aware seizure": "focal seizure",
    "focal aware seizures": "focal seizures",
    "focal impaired awareness seizure": "focal seizure",
    "focal impaired awareness seizures": "focal seizures",
    "focal seizures with impaired awareness": "focal seizures with altered awareness",
    "myoclonic jerks": "myoclonic seizures",
    "absence events": "generalized tonic clonic seizures",
}

_SEIZURE_SURFACE_REPAIRS = {
    "focal onset convulsive seizure": "focal to bilateral convulsive seizure",
    "focal onset convulsive seizures": "focal to bilateral convulsive seizures",
    "focal to bilateral seizure": "focal to bilateral convulsive seizure",
    "focal to bilateral seizures": "focal to bilateral convulsive seizures",
    "generalized tonic clonic seizures from sleep": "generalized tonic clonic seizures",
}

_FUSED_SEIZURE_TYPE_SPLITS = {
    "temporal lobe onset focal seizures": (
        "temporal lobe seizure",
        "focal seizures",
    ),
    "temporal lobe focal seizures": (
        "temporal lobe seizure",
        "focal seizures",
    ),
    "temporal onset focal seizures": (
        "temporal lobe seizure",
        "focal seizures",
    ),
    "temporal lobe seizures": (
        "temporal lobe seizure",
        "focal seizures",
    ),
    "focal seizures with secondary generalisation": (
        "focal seizures",
        "secondary generalisation",
        "generalized tonic clonic seizure",
    ),
    "focal seizures with secondary generalization": (
        "focal seizures",
        "secondary generalisation",
        "generalized tonic clonic seizure",
    ),
}

_SECONDARY_GENERALISED_SEIZURE_LABELS = frozenset(
    {
        "secondary generalised seizure",
        "secondary generalised seizures",
        "secondary generalized seizure",
        "secondary generalized seizures",
    }
)
_SECONDARY_COLLAPSED_SEIZURE_TOKEN = "secondary"
_SECONDARY_GENERALISED_SEIZURE_NOTE_RE = re.compile(
    r"\bsecondary generali[sz]ed seiz"
)

def exect_seizure_type_benchmark_bridge(
    raw_value: str,
    *,
    note_text: str = "",
    prediction_affecting: bool = True,
) -> list[NormalizationResult]:
    """Map seizure-type surfaces to audited ExECT benchmark labels.

    This is a bridge primitive, not a gold loader. It intentionally does not
    use MarkupSeizureFrequency spans as seizure-type evidence.
    """

    canonical = _canonical_seizure_type_surface(raw_value)
    if not canonical or canonical in _REJECTED_GRANULAR_SEIZURE_TYPES:
        return []

    repaired = _SEIZURE_SURFACE_REPAIRS.get(canonical)
    split_values = _FUSED_SEIZURE_TYPE_SPLITS.get(repaired or canonical)
    if split_values is not None:
        return [
            _seizure_type_normalization_result(
                raw_value=raw_value,
                canonical_value=canonical,
                benchmark_value=split_value,
                rule="exect_seizure_type_fused_phrase_split",
                prediction_affecting=prediction_affecting,
                metadata={
                    "bridge_flags": ["benchmark_bridge:fused_seizure_type_split"],
                    "split_index": index,
                    "source_policy": "diagnosis_json_seizure_type_surface",
                },
            )
            for index, split_value in enumerate(split_values)
        ]

    coarsened = _GRANULAR_SEIZURE_TYPE_COARSENING.get(repaired or canonical)
    if coarsened is not None:
        return [
            _seizure_type_normalization_result(
                raw_value=raw_value,
                canonical_value=canonical,
                benchmark_value=coarsened,
                rule="exect_seizure_type_granularity_coarsening",
                prediction_affecting=prediction_affecting,
                metadata={
                    "bridge_flags": [
                        "benchmark_bridge:granular_seizure_surface_coarsened"
                    ],
                    "source_policy": "diagnosis_json_seizure_type_surface",
                },
            )
        ]

    if repaired is not None:
        return [
            _seizure_type_normalization_result(
                raw_value=raw_value,
                canonical_value=canonical,
                benchmark_value=repaired,
                rule="exect_seizure_type_surface_repair",
                prediction_affecting=prediction_affecting,
                metadata={
                    "bridge_flags": [_seizure_repair_flag(canonical)],
                    "source_policy": "diagnosis_json_seizure_type_surface",
                },
            )
        ]

    results = [
        _seizure_type_normalization_result(
            raw_value=raw_value,
            canonical_value=canonical,
            benchmark_value=canonical,
            rule="exect_seizure_type_identity_surface",
            prediction_affecting=prediction_affecting,
            metadata={
                "bridge_flags": [],
                "source_policy": "diagnosis_json_seizure_type_surface",
            },
        )
    ]
    if _should_co_list_secondary_token(canonical, note_text):
        results.append(
            _seizure_type_normalization_result(
                raw_value=raw_value,
                canonical_value=canonical,
                benchmark_value=_SECONDARY_COLLAPSED_SEIZURE_TOKEN,
                rule="exect_seizure_type_secondary_token_co_list",
                prediction_affecting=prediction_affecting,
                metadata={
                    "bridge_flags": ["benchmark_bridge:secondary_token_co_listed"],
                    "source_policy": "diagnosis_json_seizure_type_surface",
                },
            )
        )
    return results

def _seizure_type_normalization_result(
    *,
    raw_value: str,
    canonical_value: str,
    benchmark_value: str,
    rule: str,
    prediction_affecting: bool,
    metadata: dict[str, object],
) -> NormalizationResult:
    caveat = None
    if canonical_value != benchmark_value:
        caveat = (
            "ExECT seizure-type bridge maps clinically richer or fused wording to "
            "the audited benchmark-facing surface."
        )
    return NormalizationResult(
        primitive_id=EXECT_SEIZURE_TYPE_BENCHMARK_BRIDGE_PRIMITIVE_ID,
        dataset="exect_v2",
        field_family="seizure_type",
        raw_value=raw_value,
        canonical_value=canonical_value,
        benchmark_value=benchmark_value,
        clinical_caveat=caveat,
        transformation_rule=rule,
        prediction_affecting=prediction_affecting,
        scorer_only=not prediction_affecting,
        metadata=metadata,
    )


def _canonical_seizure_type_surface(raw_value: str) -> str:
    return canonical_clinical_phrase(raw_value)


def _seizure_repair_flag(canonical: str) -> str:
    if canonical.startswith("focal onset convulsive"):
        return "benchmark_bridge:focal_onset_to_bilateral_surface"
    if canonical.startswith("focal to bilateral"):
        return "benchmark_bridge:seizure_type_convulsive_modifier"
    if canonical == "generalized tonic clonic seizures from sleep":
        return "benchmark_bridge:seizure_temporal_modifier_stripped"
    return "benchmark_bridge:seizure_type_surface_repaired"


def _should_co_list_secondary_token(canonical: str, note_text: str) -> bool:
    if canonical == _SECONDARY_COLLAPSED_SEIZURE_TOKEN:
        return False
    if canonical not in _SECONDARY_GENERALISED_SEIZURE_LABELS:
        return False
    return bool(_SECONDARY_GENERALISED_SEIZURE_NOTE_RE.search(note_text.lower()))

__all__ = [
    "EXECT_SEIZURE_TYPE_BENCHMARK_BRIDGE_PRIMITIVE_ID",
    "exect_seizure_type_benchmark_bridge",
]
