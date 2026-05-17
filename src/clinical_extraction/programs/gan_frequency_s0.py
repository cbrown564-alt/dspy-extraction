from __future__ import annotations

from collections.abc import Callable, Iterable

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.llms import ChatAdapter, ChatMessage
from clinical_extraction.runs import RunMetadata
from clinical_extraction.schemas import (
    DocumentPrediction,
    EvidenceSpan,
    ExtractedValue,
    GanRecord,
    PredictionSet,
)

GAN_FREQUENCY_S0_FIELD = "seizure_frequency_number"
GAN_FREQUENCY_S0_SCHEMA_LEVEL = "gan_frequency_s0"
GAN_FREQUENCY_S0_VARIANT = "gan_frequency_s0_single_pass"
GAN_FREQUENCY_S0_SCORER = "gan_frequency_deterministic_v1"


class GanFrequencyS0Input(BaseModel):
    model_config = ConfigDict(frozen=True)

    record_id: str
    note_text: str
    target_field: str = GAN_FREQUENCY_S0_FIELD


class GanFrequencyS0Output(BaseModel):
    model_config = ConfigDict(frozen=True)

    seizure_frequency_number: str | None
    evidence_text: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    abstained: bool = False
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class GanFrequencyS0Program:
    """Narrow mocked-execution contract for first Gan frequency extraction runs.

    Real DSPy modules and provider adapters can target the same input/output
    shape later. For now, tests inject an extractor callable so the artifact and
    schema contract can stabilize without model calls.
    """

    def __init__(
        self,
        *,
        extractor: Callable[[GanFrequencyS0Input], GanFrequencyS0Output],
        model_provider: str,
        model_name: str,
        prompt_version: str = "gan_frequency_s0_v1",
    ) -> None:
        self.extractor = extractor
        self.model_provider = model_provider
        self.model_name = model_name
        self.prompt_version = prompt_version

    def predict_records(self, records: Iterable[GanRecord]) -> PredictionSet:
        predictions = [self.predict_record(record) for record in records]
        return PredictionSet(
            dataset="gan_2026",
            schema_level=GAN_FREQUENCY_S0_SCHEMA_LEVEL,
            predictions=predictions,
            metadata={
                "program_variant": GAN_FREQUENCY_S0_VARIANT,
                "model_provider": self.model_provider,
                "model_name": self.model_name,
                "prompt_version": self.prompt_version,
                "scorer_mode": GAN_FREQUENCY_S0_SCORER,
            },
        )

    def predict_record(self, record: GanRecord) -> DocumentPrediction:
        input_record = GanFrequencyS0Input(
            record_id=record.record_id,
            note_text=record.note_text,
        )
        output = self.extractor(input_record)
        value = ExtractedValue(
            field_name=GAN_FREQUENCY_S0_FIELD,
            raw_value=output.seizure_frequency_number,
            normalized_value=output.seizure_frequency_number,
            evidence=_evidence_spans(record, output),
            temporality="unknown",
            negation="unknown",
            confidence=output.confidence,
            quality_flags=["abstained"] if output.abstained else [],
            metadata=output.metadata,
        )
        return DocumentPrediction(
            document_id=record.record_id,
            dataset="gan_2026",
            schema_level=GAN_FREQUENCY_S0_SCHEMA_LEVEL,
            values=[value],
            metadata={
                "program_variant": GAN_FREQUENCY_S0_VARIANT,
                "prompt_config": self.prompt_config(),
            },
        )

    def prompt_config(self) -> dict[str, str]:
        return {
            "signature": "GanFrequencyS0Signature",
            "module": "GanFrequencyS0Program",
            "prompt_version": self.prompt_version,
            "target_field": GAN_FREQUENCY_S0_FIELD,
            "instruction": (
                "Extract one Gan seizure-frequency label and supporting evidence "
                "from the clinical note."
            ),
            "few_shot_policy": "none",
            "context_policy": "full_note",
            "verifier_policy": "none",
            "repair_policy": "none",
            "abstention_policy": "allow_explicit_abstain_flag",
        }

    def run_metadata(self, *, run_id: str, split_name: str) -> RunMetadata:
        return RunMetadata(
            run_id=run_id,
            dataset="gan_2026",
            split_name=split_name,
            model_provider=self.model_provider,
            model_name=self.model_name,
            schema_level=GAN_FREQUENCY_S0_SCHEMA_LEVEL,
            program_variant=GAN_FREQUENCY_S0_VARIANT,
            scorer_mode=GAN_FREQUENCY_S0_SCORER,
            metric_caveats=[
                "Monthly-frequency, Purist category, and Pragmatic category metrics are benchmark-facing.",
                "Raw exact, normalized-label exact, schema validity, abstention, and evidence support are diagnostic.",
                "Provider adapters target this narrow Gan S0 contract before broader DSPy modules.",
            ],
            metadata={"prompt_config": self.prompt_config()},
        )


def build_gan_frequency_s0_extractor(
    adapter: ChatAdapter,
) -> Callable[[GanFrequencyS0Input], GanFrequencyS0Output]:
    def extract(input_record: GanFrequencyS0Input) -> GanFrequencyS0Output:
        content = adapter.complete_json(
            _gan_frequency_s0_messages(input_record),
            response_schema=GAN_FREQUENCY_S0_RESPONSE_SCHEMA,
        )
        payload = _parse_json_object(content)
        return GanFrequencyS0Output.model_validate(payload)

    return extract


GAN_FREQUENCY_S0_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "seizure_frequency_number": {
            "type": ["string", "null"],
            "description": "The Gan seizure_frequency_number label, or null when abstaining.",
        },
        "evidence_text": {
            "type": ["string", "null"],
            "description": "A direct quote from the note supporting the label.",
        },
        "confidence": {
            "type": ["number", "null"],
            "minimum": 0,
            "maximum": 1,
        },
        "abstained": {"type": "boolean"},
        "metadata": {
            "type": "object",
            "additionalProperties": {"type": ["string", "number", "boolean", "null"]},
        },
    },
    "required": [
        "seizure_frequency_number",
        "evidence_text",
        "confidence",
        "abstained",
        "metadata",
    ],
}


def _gan_frequency_s0_messages(input_record: GanFrequencyS0Input) -> list[ChatMessage]:
    return [
        ChatMessage(
            role="system",
            content=(
                "Return strict JSON for the Gan seizure-frequency S0 extraction task. "
                "Extract exactly one seizure_frequency_number label and evidence quote. "
                "Use null for the label and set abstained=true when the note does not "
                "support a frequency label. Do not infer beyond the note text."
            ),
        ),
        ChatMessage(
            role="user",
            content=(
                f"record_id: {input_record.record_id}\n"
                f"target_field: {input_record.target_field}\n\n"
                f"clinical_note:\n{input_record.note_text}"
            ),
        ),
    ]


def _parse_json_object(content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("Gan S0 adapter response was not valid JSON.") from exc
    if not isinstance(parsed, dict):
        raise ValueError("Gan S0 adapter response must be a JSON object.")
    return parsed


def _evidence_spans(
    record: GanRecord,
    output: GanFrequencyS0Output,
) -> list[EvidenceSpan]:
    if not output.evidence_text:
        return []
    start = record.note_text.find(output.evidence_text)
    if start == -1:
        return [
            EvidenceSpan(
                text=output.evidence_text,
                document_id=record.record_id,
            )
        ]
    return [
        EvidenceSpan(
            text=output.evidence_text,
            start=start,
            end=start + len(output.evidence_text),
            document_id=record.record_id,
        )
    ]
