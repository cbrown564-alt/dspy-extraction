from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EvidenceSpan(BaseModel):
    text: str
    start: int | None = None
    end: int | None = None


class ExectGoldDocument(BaseModel):
    model_config = ConfigDict(frozen=True)

    document_id: str
    text: str
    raw_annotations: list[dict[str, Any]] = Field(default_factory=list)
    raw_diagnoses: list[str] = Field(default_factory=list)
    diagnoses: list[str] = Field(default_factory=list)
    seizure_types: list[str] = Field(default_factory=list)
    current_medications: list[str] = Field(default_factory=list)
    quality_flags: list[str] = Field(default_factory=list)


class GanRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

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

