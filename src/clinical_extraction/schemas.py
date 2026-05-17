from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ScalarValue = str | int | float | bool
NormalizedValue = ScalarValue | list[ScalarValue] | dict[str, ScalarValue] | None
Temporality = Literal[
    "current",
    "historical",
    "planned",
    "future",
    "hypothetical",
    "not_applicable",
    "unknown",
]
NegationStatus = Literal[
    "affirmed",
    "negated",
    "possible",
    "not_applicable",
    "unknown",
]


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class EvidenceSpan(FrozenModel):
    """Source-text support for a predicted or gold value."""

    text: str
    start: int | None = None
    end: int | None = None
    document_id: str | None = None
    section: str | None = None

    @model_validator(mode="after")
    def validate_offsets(self) -> EvidenceSpan:
        if (self.start is None) != (self.end is None):
            raise ValueError("Evidence offsets must provide both start and end, or neither.")
        if self.start is not None and self.end is not None:
            if self.start < 0 or self.end < 0:
                raise ValueError("Evidence offsets must be non-negative.")
            if self.end < self.start:
                raise ValueError("Evidence end offset must be greater than or equal to start.")
        return self


class ExtractedValue(FrozenModel):
    """A single extracted clinical value with normalization and support metadata."""

    field_name: str
    raw_value: str | None = None
    normalized_value: NormalizedValue = None
    evidence: list[EvidenceSpan] = Field(default_factory=list)
    temporality: Temporality = "unknown"
    negation: NegationStatus = "unknown"
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    quality_flags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentPrediction(FrozenModel):
    """Structured predictions for one source document.

    `schema_level` is deliberately a free string so S0-S4, Gan-only, and future
    task-specific schemas can remain experiment parameters rather than package
    constants.
    """

    document_id: str
    dataset: str
    schema_level: str
    values: list[ExtractedValue] = Field(default_factory=list)
    quality_flags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PredictionSet(FrozenModel):
    dataset: str
    schema_level: str
    predictions: list[DocumentPrediction] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_prediction_context(self) -> PredictionSet:
        for prediction in self.predictions:
            if prediction.dataset != self.dataset:
                raise ValueError("Prediction dataset must match the prediction set dataset.")
            if prediction.schema_level != self.schema_level:
                raise ValueError(
                    "Prediction schema_level must match the prediction set schema_level."
                )
        return self


class ExectGoldDocument(FrozenModel):
    document_id: str
    text: str
    raw_annotations: list[dict[str, Any]] = Field(default_factory=list)
    raw_diagnoses: list[str] = Field(default_factory=list)
    diagnoses: list[str] = Field(default_factory=list)
    seizure_types: list[str] = Field(default_factory=list)
    current_medications: list[str] = Field(default_factory=list)
    quality_flags: list[str] = Field(default_factory=list)


class GanRecord(FrozenModel):
    record_id: str
    source_row_index: int
    note_text: str
    gold_label: str
    gold_evidence: str | None = None
    reference_label: str | None = None
    reference_evidence: str | None = None
    row_ok: bool
    labels_match_all_categories: bool
    quotes_ok_all_categories: bool
    flags: list[str] = Field(default_factory=list)
    raw: dict[str, Any]
