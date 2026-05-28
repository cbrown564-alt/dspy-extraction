"""ExECT S0/S1 optimizer metrics."""
from __future__ import annotations

import dspy

from clinical_extraction.evaluation.exect import score_exect_document
from clinical_extraction.exect.s0_s1.constants import (
    EXECT_DATASET,
    EXECT_S0_S1_PROMPT_VERSION,
    EXECT_S0_S1_SCHEMA_LEVEL,
    EXECT_S0_S1_VARIANT,
)
from clinical_extraction.exect.s0_s1.prediction_artifacts import (
    _as_list,
    _build_s1_field_family_values,
)
from clinical_extraction.exect.s1_boundary import build_s1_boundary_surfaces_metadata
from clinical_extraction.schemas import DocumentPrediction, ExectGoldDocument


def _gold_document_from_optimizer_example(example: dspy.Example) -> ExectGoldDocument:
    document_id = getattr(example, "document_id", None) or "optimizer_example"
    return ExectGoldDocument(
        document_id=document_id,
        text=example.note_text,
        diagnoses=_as_list(getattr(example, "diagnosis", [])),
        seizure_types=_as_list(getattr(example, "seizure_type", [])),
        current_medications=_as_list(getattr(example, "annotated_medication", [])),
    )


def _document_prediction_from_field_family_pred(
    record: ExectGoldDocument,
    pred: dspy.Prediction,
    *,
    apply_benchmark_bridges: bool = True,
) -> DocumentPrediction:
    """Map an optimizer prediction to the scored S1 field-family document shape."""
    values = _build_s1_field_family_values(
        record,
        pred,
        apply_benchmark_bridges=apply_benchmark_bridges,
    )
    bridge_stage = "inline" if apply_benchmark_bridges else "none"
    return DocumentPrediction(
        document_id=record.document_id,
        dataset=EXECT_DATASET,
        schema_level=EXECT_S0_S1_SCHEMA_LEVEL,
        values=values,
        quality_flags=record.quality_flags,
        metadata={
            "program_variant": EXECT_S0_S1_VARIANT,
            "apply_benchmark_bridges": apply_benchmark_bridges,
            "bridge_stage": bridge_stage,
            "repair_policy": "none",
            "s1_boundary_surfaces": build_s1_boundary_surfaces_metadata(
                pred=pred,
                values=values,
                prompt_version=EXECT_S0_S1_PROMPT_VERSION,
                program_variant=EXECT_S0_S1_VARIANT,
                repair_policy="none",
                apply_benchmark_bridges=apply_benchmark_bridges,
                bridge_stage=bridge_stage,
            ),
        },
    )


def exect_s0_s1_field_family_micro_f1_metric(
    example: dspy.Example,
    pred: dspy.Prediction,
    trace=None,
    *,
    apply_benchmark_bridges: bool = True,
) -> float:
    """DSPy metric for ExECT S0/S1 optimizer training.

    Uses pooled document micro F1 on the three S1 field families. When
    ``apply_benchmark_bridges`` is true, the metric uses the same inline bridge
    path as production ``repair_policy=none`` scoring. When false, it scores raw
    model surfaces only.
    """
    gold = _gold_document_from_optimizer_example(example)
    prediction = _document_prediction_from_field_family_pred(
        gold,
        pred,
        apply_benchmark_bridges=apply_benchmark_bridges,
    )
    document_score = score_exect_document(gold=gold, prediction=prediction)
    if document_score.document_micro_f1 is None:
        return 0.0
    return float(document_score.document_micro_f1)


def exect_s0_s1_field_family_micro_f1_raw_metric(
    example: dspy.Example,
    pred: dspy.Prediction,
    trace=None,
) -> float:
    """Optimizer metric without inline benchmark bridges."""
    return exect_s0_s1_field_family_micro_f1_metric(
        example,
        pred,
        trace,
        apply_benchmark_bridges=False,
    )

EXECT_S0_S1_OPTIMIZER_METRICS = {
    "exect_field_family_micro_f1": exect_s0_s1_field_family_micro_f1_metric,
    "exect_field_family_micro_f1_raw": exect_s0_s1_field_family_micro_f1_raw_metric,
}


__all__ = [
    "EXECT_S0_S1_OPTIMIZER_METRICS",
    "exect_s0_s1_field_family_micro_f1_metric",
    "exect_s0_s1_field_family_micro_f1_raw_metric",
]
