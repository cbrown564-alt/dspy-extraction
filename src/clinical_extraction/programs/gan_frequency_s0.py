"""Gan seizure-frequency S0 DSPy program."""
from __future__ import annotations

from typing import Optional

import dspy

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


class GanFrequencyS0Signature(dspy.Signature):
    """Extract the Gan seizure-frequency label and supporting evidence from a clinical note.

    The label must match the Gan annotation vocabulary exactly. Abstain (null) only when
    the note contains no usable seizure-frequency information.
    """

    note_text: str = dspy.InputField(desc="Clinical neurology note text")
    seizure_frequency_number: Optional[str] = dspy.OutputField(
        desc=(
            "Seizure frequency in Gan label format. One of: "
            "'{count} per {unit}' e.g. '2 per week', '1 per 3 month'; "
            "'{count} cluster per {unit}, {n} per cluster'; "
            "'unknown'; 'no seizure frequency reference'; "
            "or null to abstain. Unit must be singular: day/week/month/year."
        )
    )
    evidence_text: Optional[str] = dspy.OutputField(
        desc="Direct verbatim quote from the note supporting the label. Null if abstaining."
    )


class GanFrequencyS0Module(dspy.Module):
    """Narrow Gan seizure-frequency S0 DSPy module.

    Uses ChainOfThought so the model reasons before committing to a label.
    Compile with BootstrapFewShot or MIPROv2 + ``gan_frequency_s0_metric``
    before running on the evaluation split.
    """

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(GanFrequencyS0Signature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(note_text=note_text)


# ---------------------------------------------------------------------------
# DSPy metric for optimizer training
# ---------------------------------------------------------------------------

def gan_frequency_s0_metric(
    example: dspy.Example,
    pred: dspy.Prediction,
    trace=None,
) -> float:
    """DSPy metric for Gan S0 optimizer training.

    Uses pragmatic category match (infrequent / frequent / unknown) as the
    optimization target — it is the coarsest benchmark-facing signal and
    therefore most stable across minor label format variation.

    Returns 1.0 on pragmatic category match, 0.0 on mismatch or invalid label.
    """
    from clinical_extraction.gan.scoring import score_gan_frequency_prediction

    predicted = getattr(pred, GAN_FREQUENCY_S0_FIELD, None)
    gold = getattr(example, GAN_FREQUENCY_S0_FIELD, None)

    if not predicted or not gold:
        return 0.0

    try:
        score = score_gan_frequency_prediction(
            gold_label=gold, predicted_label=predicted
        )
        return float(score.pragmatic_category_match)
    except ValueError:
        return 0.0


# ---------------------------------------------------------------------------
# DSPy Example helpers
# ---------------------------------------------------------------------------

def make_gan_dspy_examples(records: list[GanRecord]) -> list[dspy.Example]:
    """Convert Gan records into DSPy Examples for training or evaluation.

    Each example exposes ``note_text`` as input and ``seizure_frequency_number``
    (the gold label) as the expected output for the metric.
    """
    return [
        dspy.Example(
            note_text=record.note_text,
            seizure_frequency_number=record.gold_label,
        ).with_inputs("note_text")
        for record in records
    ]


# ---------------------------------------------------------------------------
# BootstrapFewShot compilation helper
# ---------------------------------------------------------------------------

def compile_gan_s0_module(
    records: list[GanRecord],
    *,
    max_bootstrapped_demos: int = 4,
    max_labeled_demos: int = 0,
    max_rounds: int = 1,
) -> GanFrequencyS0Module:
    """Compile GanFrequencyS0Module with BootstrapFewShot on labeled training records.

    Runs the teacher module on each record and keeps traces that pass
    ``gan_frequency_s0_metric`` (pragmatic category match) as few-shot
    demonstrations. Returns the compiled module with demos baked in.
    """
    trainset = make_gan_dspy_examples(records)
    optimizer = dspy.BootstrapFewShot(
        metric=gan_frequency_s0_metric,
        max_bootstrapped_demos=max_bootstrapped_demos,
        max_labeled_demos=max_labeled_demos,
        max_rounds=max_rounds,
    )
    module = GanFrequencyS0Module()
    return optimizer.compile(module, trainset=trainset)


# ---------------------------------------------------------------------------
# Bridge: DSPy Prediction → PredictionSet artifact
# ---------------------------------------------------------------------------

def predict_gan_records(
    module: GanFrequencyS0Module,
    records: list[GanRecord],
    *,
    model_provider: str,
    model_name: str,
    prompt_version: str = "gan_frequency_s0_v1",
) -> PredictionSet:
    """Run ``module`` on each Gan record and return a ``PredictionSet`` artifact."""
    predictions = [_predict_record(module, record) for record in records]
    return PredictionSet(
        dataset="gan_2026",
        schema_level=GAN_FREQUENCY_S0_SCHEMA_LEVEL,
        predictions=predictions,
        metadata={
            "program_variant": GAN_FREQUENCY_S0_VARIANT,
            "model_provider": model_provider,
            "model_name": model_name,
            "prompt_version": prompt_version,
            "scorer_mode": GAN_FREQUENCY_S0_SCORER,
        },
    )


_ABSTAIN_STRINGS = frozenset({"none", "null", ""})


def _predict_record(
    module: GanFrequencyS0Module, record: GanRecord
) -> DocumentPrediction:
    pred = module(note_text=record.note_text)
    label: str | None = pred.seizure_frequency_number
    evidence_text: str | None = pred.evidence_text

    # Normalize sentinel strings to Python None (DummyLM and some adapters
    # return the string "None" / "null" instead of Python None for null fields).
    if isinstance(label, str) and label.strip().lower() in _ABSTAIN_STRINGS:
        label = None
    if isinstance(evidence_text, str) and evidence_text.strip().lower() in _ABSTAIN_STRINGS:
        evidence_text = None

    value = ExtractedValue(
        field_name=GAN_FREQUENCY_S0_FIELD,
        raw_value=label,
        normalized_value=label,
        evidence=_evidence_spans(record, evidence_text),
        temporality="unknown",
        negation="unknown",
        confidence=None,
        quality_flags=["abstained"] if label is None else [],
    )
    return DocumentPrediction(
        document_id=record.record_id,
        dataset="gan_2026",
        schema_level=GAN_FREQUENCY_S0_SCHEMA_LEVEL,
        values=[value],
        metadata={"program_variant": GAN_FREQUENCY_S0_VARIANT},
    )


def _evidence_spans(
    record: GanRecord, evidence_text: str | None
) -> list[EvidenceSpan]:
    if not evidence_text:
        return []
    start = record.note_text.find(evidence_text)
    if start == -1:
        return [EvidenceSpan(text=evidence_text, document_id=record.record_id)]
    return [
        EvidenceSpan(
            text=evidence_text,
            start=start,
            end=start + len(evidence_text),
            document_id=record.record_id,
        )
    ]


# ---------------------------------------------------------------------------
# Run metadata helper
# ---------------------------------------------------------------------------

def gan_frequency_s0_run_metadata(
    run_id: str,
    split_name: str,
    model_provider: str,
    model_name: str,
    *,
    prompt_version: str = "gan_frequency_s0_v1",
    extra: dict | None = None,
) -> RunMetadata:
    """Build a ``RunMetadata`` for a Gan S0 run."""
    return RunMetadata(
        run_id=run_id,
        dataset="gan_2026",
        split_name=split_name,
        model_provider=model_provider,
        model_name=model_name,
        schema_level=GAN_FREQUENCY_S0_SCHEMA_LEVEL,
        program_variant=GAN_FREQUENCY_S0_VARIANT,
        scorer_mode=GAN_FREQUENCY_S0_SCORER,
        metric_caveats=[
            "Monthly-frequency, Purist category, and Pragmatic category metrics are benchmark-facing.",
            "Raw exact, normalized-label exact, schema validity, abstention, and evidence support are diagnostic.",
            "Provider adapters target this narrow Gan S0 contract before broader DSPy modules.",
        ],
        metadata={
            "prompt_version": prompt_version,
            **(extra or {}),
        },
    )
