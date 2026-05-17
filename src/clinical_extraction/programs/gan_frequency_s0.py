from __future__ import annotations

from collections.abc import Callable, Iterable

from pydantic import BaseModel, ConfigDict, Field

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
                "This contract supports mocked execution only; provider adapters are a later card.",
            ],
            metadata={"prompt_config": self.prompt_config()},
        )


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
