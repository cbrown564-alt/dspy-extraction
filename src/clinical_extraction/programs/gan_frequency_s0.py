"""Gan seizure-frequency S0 DSPy program."""
from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any, Optional

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
GAN_FREQUENCY_S0_DIRECT_VARIANT = "gan_frequency_s0_direct_single_pass"
GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT = "gan_frequency_s0_direct_verify_repair"
GAN_FREQUENCY_S0_VERIFY_REPAIR_PROMPT_VERSION = (
    "gan_frequency_s0_direct_verify_repair_v2"
)
GAN_FREQUENCY_S0_SCORER = "gan_frequency_deterministic_v1"
GAN_FREQUENCY_S0_SYNTHESIS_PROMPT_VERSION = "gan_frequency_s0_synthesis_v1"

GAN_FREQUENCY_SYNTHESIS_GUIDANCE = (
    "Synthesis-backed Gan frequency policy: output only canonical Gan labels; "
    "use singular units day/week/month/year; convert daily or nightly to 1 per day; "
    "convert every N unit to 1 per N unit; use 'to' for numeric ranges; "
    "choose the highest current quantified seizure-type frequency; use full cluster "
    "format 'N cluster per unit, M per cluster'; for year-to-date counts use months "
    "elapsed since January as the denominator; treat a quarter as an observation "
    "window when the note gives a per-month rate over the last quarter; use seizure "
    "free labels only for seizure freedom of 6 months or longer, otherwise compute "
    "the rate from total events over the described period; return an exact contiguous "
    "source quote for every present claim."
)


class GanFrequencyS0Signature(dspy.Signature):
    """Extract the Gan seizure-frequency label and supporting evidence from a clinical note.

    /no_think
    Do not use hidden reasoning. Emit only the requested output fields.

    The label must match the Gan annotation vocabulary exactly. Abstain (null) only when
    the note contains no usable seizure-frequency information.

    Synthesis-backed policy:
    - Output only canonical Gan labels: N per unit, N to M per unit, N per M unit,
      N cluster per unit, M per cluster, seizure free for N unit, unknown, or
      no seizure frequency reference.
    - Use singular units: day, week, month, year.
    - Convert daily/nightly to 1 per day, every N unit to 1 per N unit, and
      numeric "or" ranges to "to" ranges.
    - Choose the highest current quantified seizure-type frequency.
    - Use the full cluster format; do not drop either the cluster period or
      the per-cluster count.
    - Use seizure free for N unit only when seizure freedom is at least 6 months.
      If seizure freedom is shorter than 6 months, compute the rate from the
      total events over the described period.
    - For year-to-date counts, use months elapsed since January as the denominator.
    - Treat "over the last quarter" as an observation window when the note gives
      a per-month rate; do not automatically convert it to per 3 month.
    - evidence_text must be an exact contiguous quote from the note.
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
        desc=(
            "Shortest exact contiguous quote from the note supporting the label. "
            "Do not include prompt instructions or wrapper text. Null if abstaining."
        )
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


class GanFrequencyS0DirectModule(dspy.Module):
    """Gan S0 module that predicts the structured fields without a reasoning output."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.Predict(GanFrequencyS0Signature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(note_text=note_text)


class GanFrequencyS0VerifierSignature(dspy.Signature):
    """Verify and optionally repair a Gan seizure-frequency prediction.

    /no_think
    Do not use hidden reasoning. Emit only the requested output fields.

    Review the initial prediction against the source note. Prefer confirm or
    repair toward a better canonical label. Abstain only as a last resort.

    Canonical Gan vocabulary (singular units: day, week, month, year):
    - N per unit, N to M per unit, N per M unit
    - N cluster per unit, M per cluster
    - seizure free for N unit — VALID and canonical when N is at least 6 months
      (e.g. seizure free for 7 month, seizure free for 35 year)
    - unknown — note discusses seizures but frequency cannot be quantified
    - no seizure frequency reference — note lacks usable frequency information

    Decision policy:
    - confirm: initial label is already canonical, note-supported, and evidence is
      an exact contiguous note substring. Do not add quotes or wrapper punctuation.
    - repair: fix a specific error to a strictly better canonical label supported
      by the note. Do not repair imprecise-but-valid labels to unknown.
    - abstain: last resort only — set final_label to null when no confident
      canonical label is supported.

    Confirm rules (do not over-repair):
    - Keep correct seizure-free labels such as seizure free for 7 month.
    - seizure free for N unit is canonical when seizure freedom is >= 6 months;
      never reject it as non-canonical or replace it with no seizure frequency
      reference.
    - If the initial label and evidence already match the note, confirm unchanged.

    Repair rules:
    - Incomplete cluster labels: add the per-cluster count when the note states it.
    - Short seizure-free periods (< 6 months): compute a rate from total events over
      the described period; do not emit unknown unless the note is truly ambiguous.
    - Imprecise but valid labels (e.g. multiple per week): sharpen toward the
      nearest supported canonical form or confirm; do not collapse to unknown.
    - Unknown vs no-reference: use unknown when seizures are discussed but not
      quantifiable; use no-reference only when the note lacks frequency information.

    Evidence rules:
    - final_evidence must be the shortest exact contiguous substring of note_text.
    - On confirm, preserve initial_evidence when it already supports the label.
    - On repair, update evidence only when needed to support the repaired label.
    - Never replace a note-contained quote with an unsupported or invented quote.

    Arithmetic and temporal guardrails:
    - Do not invent monthly rates without explicit support (e.g. one seizure in
      three weeks → 1 per 3 week, not 3 per month).
    - Apply the 6-month seizure-free threshold before labeling seizure free.
    - For year-to-date counts, use months elapsed since January as denominator.

    Target failure modes:
    - Incomplete cluster labels (missing per-cluster count)
    - Temporal-window or denominator errors (year-to-date, quarter misinterpretation)
    - Short seizure-free periods labeled as seizure free
    - Misrejecting valid seizure free for N unit labels
    - Over-repairing to unknown or no seizure frequency reference
    - Unknown vs no seizure frequency reference confusion
    - Non-canonical or unsupported evidence quotes
    """

    note_text: str = dspy.InputField(desc="Clinical neurology note text")
    initial_label: Optional[str] = dspy.InputField(
        desc="Initial predicted seizure-frequency label"
    )
    initial_evidence: Optional[str] = dspy.InputField(
        desc="Initial predicted evidence quote"
    )
    final_label: Optional[str] = dspy.OutputField(
        desc=(
            "Confirmed or repaired canonical Gan label without wrapper quotes. "
            "Formats: N per unit, N to M per unit, N per M unit, "
            "N cluster per unit, M per cluster, seizure free for N unit (>= 6 months), "
            "unknown, no seizure frequency reference, or null to abstain."
        )
    )
    final_evidence: Optional[str] = dspy.OutputField(
        desc=(
            "Shortest exact contiguous quote from note_text supporting final_label. "
            "Preserve initial_evidence on confirm when it already matches the note. "
            "Null only when abstaining or final_label is no seizure frequency reference."
        )
    )
    decision: str = dspy.OutputField(
        desc=(
            "confirm when the initial prediction is already correct; "
            "repair only for a strictly better supported canonical label; "
            "abstain only as a last resort"
        )
    )
    reason: str = dspy.OutputField(
        desc="Brief explanation citing the note span and why confirm/repair/abstain"
    )


class GanFrequencyS0VerifierModule(dspy.Module):
    """Standalone verifier for Gan S0 predictions."""

    def __init__(self) -> None:
        super().__init__()
        self.verify = dspy.Predict(GanFrequencyS0VerifierSignature)

    def forward(
        self,
        note_text: str,
        initial_label: str | None,
        initial_evidence: str | None,
    ) -> dspy.Prediction:
        return self.verify(
            note_text=note_text,
            initial_label=initial_label,
            initial_evidence=initial_evidence,
        )


class GanFrequencyS0VerifyRepairModule(dspy.Module):
    """Gan S0 module that extracts then verifies/repairs the prediction."""

    def __init__(self, extractor_variant: str = GAN_FREQUENCY_S0_DIRECT_VARIANT) -> None:
        super().__init__()
        self.extractor = build_gan_s0_module(extractor_variant)
        self.verifier = GanFrequencyS0VerifierModule()

    def forward(self, note_text: str) -> dspy.Prediction:
        initial = self.extractor(note_text=note_text)
        verified = self.verifier(
            note_text=note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
        )
        return dspy.Prediction(
            seizure_frequency_number=verified.final_label,
            evidence_text=verified.final_evidence,
            verifier_decision=verified.decision,
            verifier_reason=verified.reason,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
        )


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


def gan_frequency_s0_synthesis_metric(
    example: dspy.Example,
    pred: dspy.Prediction,
    trace=None,
) -> float:
    """Stricter optimizer metric for synthesis-backed Gan S0 compilation.

    This metric is intentionally optimizer-facing. It does not change the
    benchmark evaluator. A trace passes only when the predicted label matches
    the normalized gold label and, unless the gold label is no-reference, the
    prediction supplies an exact contiguous quote from the note.
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
    except ValueError:
        return 0.0

    if not score.exact_normalized_match:
        return 0.0

    predicted_evidence = getattr(pred, "evidence_text", None)
    if gold == "no seizure frequency reference":
        return float(predicted_evidence is None or not str(predicted_evidence).strip())

    if not _requires_evidence_support(gold):
        return 1.0

    if not isinstance(predicted_evidence, str) or not predicted_evidence.strip():
        return 0.0
    return float(predicted_evidence.strip() in example.note_text)


def gan_frequency_s0_synthesis_feedback_metric(
    example: dspy.Example,
    pred: dspy.Prediction,
    trace=None,
    pred_name=None,
    pred_trace=None,
):
    """GEPA-compatible Gan S0 feedback metric.

    This metric is optimizer-facing only. It preserves the benchmark scorer
    contract while surfacing richer textual feedback for common Gan failure
    modes such as canonical-label drift, temporal-window errors, cluster-format
    failures, abstentions, and unsupported evidence quotes.
    """
    from dspy.teleprompt.gepa.gepa_utils import ScoreWithFeedback

    from clinical_extraction.gan.scoring import score_gan_frequency_prediction

    predicted = getattr(pred, GAN_FREQUENCY_S0_FIELD, None)
    gold = getattr(example, GAN_FREQUENCY_S0_FIELD, None)
    note_text = getattr(example, "note_text", "") or ""

    if not predicted:
        return ScoreWithFeedback(
            score=0.0,
            feedback=(
                "[abstention] The prediction did not provide seizure_frequency_number. "
                "Return a canonical Gan label or no seizure frequency reference, and "
                "abstain only when the note truly lacks usable seizure-frequency information."
            ),
        )
    if not gold:
        return ScoreWithFeedback(
            score=0.0,
            feedback="The training example is missing the gold Gan frequency label.",
        )

    try:
        score = score_gan_frequency_prediction(
            gold_label=gold, predicted_label=predicted
        )
    except ValueError as exc:
        feedback = [
            (
                "[invalid-format] "
                f"The predicted label {predicted!r} is not a valid canonical Gan "
                f"frequency label: {exc}."
            )
        ]
        if _looks_like_cluster_failure(str(predicted)):
            feedback.append(
                "[cluster-format] Cluster labels must use the full format "
                "'N cluster per unit, M per cluster' and must not drop the "
                "per-cluster count."
            )
        forbidden_unit = _forbidden_unit(str(predicted))
        if forbidden_unit is not None:
            feedback.append(
                f"[forbidden-unit] Replace {forbidden_unit!r} with canonical Gan "
                "units day, week, month, or year."
            )
        return ScoreWithFeedback(
            score=0.0,
            feedback=" ".join(feedback),
        )

    predicted_evidence = getattr(pred, "evidence_text", None)
    feedback: list[str] = []
    metric_score = 0.8 if score.exact_normalized_match else 0.0

    if not score.exact_normalized_match:
        feedback.append(
            "[exact-label] "
            f"Expected normalized Gan label {gold!r}, but the prediction was "
            f"{predicted!r}. Preserve the benchmark-facing label semantics."
        )
        if score.pragmatic_category_match:
            metric_score = 0.3
        else:
            feedback.append(
                "[pragmatic-category] The prediction crossed the benchmark-facing "
                f"Pragmatic bucket from {score.gold_pragmatic_category!r} to "
                f"{score.predicted_pragmatic_category!r}."
            )
        if (
            _looks_like_cluster_failure(score.predicted_label)
            or "cluster" in score.normalized_gold_label
        ):
            feedback.append(
                "[cluster-format] Preserve the cluster structure exactly. Do not "
                "drop the cluster period or the per-cluster count, and do not back "
                "off to unknown when the note gives both values."
            )
        if _is_short_seizure_free_label(score.normalized_predicted_label):
            feedback.append(
                "[seizure-free-threshold] Use seizure-free labels only for 6 months "
                "or longer. Shorter seizure-free periods should be converted into "
                "the appropriate quantified rate."
            )
        if _has_temporal_window_mismatch(
            note_text,
            gold_label=score.normalized_gold_label,
            predicted_label=score.normalized_predicted_label,
        ):
            feedback.append(
                "[temporal-window] The note looks like a year-to-date or bounded-window "
                "case. Use the described observation window as the denominator; for "
                "year-to-date counts, use months elapsed since January."
            )

    evidence_ok = True
    if gold == "no seizure frequency reference":
        if isinstance(predicted_evidence, str) and predicted_evidence.strip():
            evidence_ok = False
            feedback.append(
                "[evidence-support] No-reference labels should not include supporting "
                "frequency evidence."
            )
    elif _requires_evidence_support(gold):
        if not isinstance(predicted_evidence, str) or not predicted_evidence.strip():
            evidence_ok = False
            feedback.append(
                "[evidence-support] The prediction must include an exact contiguous "
                "source quote as evidence."
            )
        elif predicted_evidence.strip() not in example.note_text:
            evidence_ok = False
            feedback.append(
                "[evidence-support][unsupported-quote] The evidence_text is not an "
                "exact contiguous quote from the note."
            )

    if evidence_ok:
        metric_score += 0.2

    if not feedback:
        feedback.append(
            "The prediction matched the normalized Gan label and evidence policy."
        )
    return ScoreWithFeedback(score=metric_score, feedback=" ".join(feedback))


def _requires_evidence_support(gold_label: str) -> bool:
    return gold_label != "no seizure frequency reference"


def _looks_like_cluster_failure(label: str) -> bool:
    normalized = label.strip().lower()
    return "cluster" in normalized and " per cluster" not in normalized


def _forbidden_unit(label: str) -> str | None:
    match = _FORBIDDEN_UNIT_RE.search(label)
    if match is None:
        return None
    return match.group(1).lower()


def _is_short_seizure_free_label(label: str) -> bool:
    match = _SEIZURE_FREE_RE.match(label)
    if match is None:
        return False
    count = float(match.group("count"))
    months = count * 12 if match.group("unit") == "year" else count
    return months < 6


def _has_temporal_window_mismatch(
    note_text: str,
    *,
    gold_label: str,
    predicted_label: str,
) -> bool:
    if not _YTD_NOTE_RE.search(note_text):
        return False
    if gold_label == predicted_label:
        return False
    return " per " in gold_label and " per " in predicted_label


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


def make_gan_synthesis_dspy_examples(records: list[GanRecord]) -> list[dspy.Example]:
    """Convert Gan records into synthesis-backed examples.

    Evidence outputs are included only when the annotation text is a contiguous
    source quote. Paraphrased or elided Gan evidence is not used as a quote demo.
    """
    return [
        dspy.Example(
            note_text=record.note_text,
            seizure_frequency_number=record.gold_label,
            evidence_text=_locatable_gold_evidence(record),
        ).with_inputs("note_text")
        for record in sorted(records, key=_synthesis_example_priority)
    ]


def _locatable_gold_evidence(record: GanRecord) -> str | None:
    if not record.gold_evidence or "..." in record.gold_evidence:
        return None
    if record.gold_evidence not in record.note_text:
        return None
    return record.gold_evidence


def _synthesis_example_priority(record: GanRecord) -> tuple[int, int, str]:
    if _locatable_gold_evidence(record):
        evidence_rank = 0
    elif record.gold_label == "no seizure frequency reference":
        evidence_rank = 2
    else:
        evidence_rank = 1

    label = record.gold_label
    if "cluster" in label:
        label_rank = 0
    elif label.startswith("seizure free"):
        label_rank = 1
    elif " per " in label:
        label_rank = 2
    elif label == "unknown":
        label_rank = 3
    else:
        label_rank = 4
    return (evidence_rank, label_rank, record.record_id)


# ---------------------------------------------------------------------------
# BootstrapFewShot compilation helper
# ---------------------------------------------------------------------------

GAN_FREQUENCY_S0_OPTIMIZER_METRICS = {
    "pragmatic_category": gan_frequency_s0_metric,
    "synthesis_exact_with_evidence": gan_frequency_s0_synthesis_metric,
    "synthesis_exact_with_evidence_feedback": gan_frequency_s0_synthesis_feedback_metric,
}


def _gan_s0_optimizer_trainset(
    records: list[GanRecord],
    *,
    optimizer_metric: str,
) -> list[dspy.Example]:
    if optimizer_metric == "synthesis_exact_with_evidence":
        return make_gan_synthesis_dspy_examples(records)
    return make_gan_dspy_examples(records)


def compile_gan_s0_module(
    records: list[GanRecord],
    *,
    program_variant: str = GAN_FREQUENCY_S0_VARIANT,
    optimizer_name: str = "BootstrapFewShot",
    max_bootstrapped_demos: int = 4,
    max_labeled_demos: int = 0,
    max_rounds: int = 1,
    num_candidate_programs: int = 16,
    optimizer_metric: str = "pragmatic_category",
) -> GanFrequencyS0Module | GanFrequencyS0DirectModule:
    """Compile a Gan S0 module with a few-shot DSPy optimizer.

    Supports ``LabeledFewShot``, ``BootstrapFewShot``, and
    ``BootstrapFewShotWithRandomSearch`` (``BootstrapRS``). LabeledFewShot
    samples labeled demonstrations from the trainset without bootstrapping.
    BootstrapFewShot keeps teacher traces that pass the optimizer metric.
    BootstrapFewShotWithRandomSearch searches over candidate demo sets.
    """
    trainset = _gan_s0_optimizer_trainset(records, optimizer_metric=optimizer_metric)
    module = build_gan_s0_module(program_variant)

    if optimizer_name == "LabeledFewShot":
        optimizer = dspy.LabeledFewShot(k=max_labeled_demos)
        return optimizer.compile(module, trainset=trainset)

    try:
        metric = GAN_FREQUENCY_S0_OPTIMIZER_METRICS[optimizer_metric]
    except KeyError as exc:
        allowed = ", ".join(sorted(GAN_FREQUENCY_S0_OPTIMIZER_METRICS))
        raise ValueError(f"Unknown optimizer_metric {optimizer_metric!r}; use {allowed}.") from exc

    if optimizer_name == "BootstrapFewShotWithRandomSearch":
        optimizer = dspy.BootstrapFewShotWithRandomSearch(
            metric=metric,
            max_bootstrapped_demos=max_bootstrapped_demos,
            max_labeled_demos=max_labeled_demos,
            max_rounds=max_rounds,
            num_candidate_programs=num_candidate_programs,
        )
        return optimizer.compile(module, trainset=trainset)

    if optimizer_name != "BootstrapFewShot":
        raise ValueError(
            f"Unsupported few-shot optimizer {optimizer_name!r}; use "
            "LabeledFewShot, BootstrapFewShot, or BootstrapFewShotWithRandomSearch."
        )

    optimizer = dspy.BootstrapFewShot(
        metric=metric,
        max_bootstrapped_demos=max_bootstrapped_demos,
        max_labeled_demos=max_labeled_demos,
        max_rounds=max_rounds,
    )
    return optimizer.compile(module, trainset=trainset)


def compile_gan_s0_module_gepa(
    records: list[GanRecord],
    *,
    program_variant: str = GAN_FREQUENCY_S0_DIRECT_VARIANT,
    optimizer_metric: str = "synthesis_exact_with_evidence_feedback",
    auto: str | None = None,
    max_full_evals: int | None = None,
    max_metric_calls: int | None = None,
    reflection_minibatch_size: int = 3,
    candidate_selection_strategy: str = "pareto",
    skip_perfect_score: bool = True,
    add_format_failure_as_feedback: bool = False,
    track_stats: bool = False,
    track_best_outputs: bool = False,
    use_cloudpickle: bool = False,
    num_threads: int | None = None,
    seed: int | None = 0,
    log_dir: Path | None = None,
    reflection_lm: dspy.LM | None = None,
) -> GanFrequencyS0Module | GanFrequencyS0DirectModule:
    """Compile a Gan S0 module with GEPA and a feedback metric."""
    try:
        metric = GAN_FREQUENCY_S0_OPTIMIZER_METRICS[optimizer_metric]
    except KeyError as exc:
        allowed = ", ".join(sorted(GAN_FREQUENCY_S0_OPTIMIZER_METRICS))
        raise ValueError(f"Unknown optimizer_metric {optimizer_metric!r}; use {allowed}.") from exc

    trainset = make_gan_synthesis_dspy_examples(records)
    optimizer = dspy.GEPA(
        metric=metric,
        auto=auto,
        max_full_evals=max_full_evals,
        max_metric_calls=max_metric_calls,
        reflection_minibatch_size=reflection_minibatch_size,
        candidate_selection_strategy=candidate_selection_strategy,
        reflection_lm=reflection_lm or dspy.settings.lm,
        skip_perfect_score=skip_perfect_score,
        add_format_failure_as_feedback=add_format_failure_as_feedback,
        track_stats=track_stats,
        track_best_outputs=track_best_outputs,
        num_threads=num_threads,
        seed=seed,
        log_dir=str(log_dir) if log_dir is not None else None,
        gepa_kwargs={"use_cloudpickle": use_cloudpickle},
    )
    module = build_gan_s0_module(program_variant)
    return optimizer.compile(module, trainset=trainset)


def build_gan_s0_module(
    program_variant: str,
) -> GanFrequencyS0Module | GanFrequencyS0DirectModule | GanFrequencyS0VerifyRepairModule:
    if program_variant == GAN_FREQUENCY_S0_VARIANT:
        return GanFrequencyS0Module()
    if program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT:
        return GanFrequencyS0DirectModule()
    if program_variant == GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT:
        return GanFrequencyS0VerifyRepairModule()
    raise ValueError(f"Unsupported Gan S0 program variant: {program_variant!r}")


# ---------------------------------------------------------------------------
# Bridge: DSPy Prediction → PredictionSet artifact
# ---------------------------------------------------------------------------

def predict_gan_records(
    module: GanFrequencyS0Module | GanFrequencyS0DirectModule,
    records: list[GanRecord],
    *,
    model_provider: str,
    model_name: str,
    prompt_version: str = "gan_frequency_s0_v1",
    program_variant: str = GAN_FREQUENCY_S0_VARIANT,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> PredictionSet:
    """Run ``module`` on each Gan record and return a ``PredictionSet`` artifact."""
    predictions = []
    total = len(records)
    for index, record in enumerate(records, start=1):
        predictions.append(_predict_record(module, record, program_variant=program_variant))
        if progress_callback is not None:
            progress_callback(index, total, record.record_id)
    return PredictionSet(
        dataset="gan_2026",
        schema_level=GAN_FREQUENCY_S0_SCHEMA_LEVEL,
        predictions=predictions,
        metadata={
            "program_variant": program_variant,
            "model_provider": model_provider,
            "model_name": model_name,
            "prompt_version": prompt_version,
            "scorer_mode": GAN_FREQUENCY_S0_SCORER,
        },
    )


_ABSTAIN_STRINGS = frozenset({"none", "null", ""})


def _predict_record(
    module: GanFrequencyS0Module | GanFrequencyS0DirectModule | GanFrequencyS0VerifyRepairModule,
    record: GanRecord,
    *,
    program_variant: str,
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

    normalized_label = _normalize_predicted_label(label)
    quality_flags = ["abstained"] if label is None else []
    if label != normalized_label:
        quality_flags.append("normalized_label_repaired")

    evidence_text, evidence_flags = _guard_evidence_text(record.note_text, evidence_text)
    quality_flags.extend(evidence_flags)

    metadata: dict[str, Any] = {"program_variant": program_variant}
    if hasattr(pred, "verifier_decision"):
        metadata["verifier_decision"] = pred.verifier_decision
    if hasattr(pred, "verifier_reason"):
        metadata["verifier_reason"] = pred.verifier_reason
    if hasattr(pred, "initial_label"):
        metadata["initial_label"] = pred.initial_label
    if hasattr(pred, "initial_evidence"):
        metadata["initial_evidence"] = pred.initial_evidence

    value = ExtractedValue(
        field_name=GAN_FREQUENCY_S0_FIELD,
        raw_value=label,
        normalized_value=normalized_label,
        evidence=_evidence_spans(record, evidence_text),
        temporality="unknown",
        negation="unknown",
        confidence=None,
        quality_flags=quality_flags,
    )
    return DocumentPrediction(
        document_id=record.record_id,
        dataset="gan_2026",
        schema_level=GAN_FREQUENCY_S0_SCHEMA_LEVEL,
        values=[value],
        metadata=metadata,
    )


_EVERY_DAY_RANGE_RE = re.compile(r"^1 per day to 1 per (?P<end>\d+) day$")
_DAILY_COUNT_RE = re.compile(r"^(?P<count>\d+(?:\.\d+)?) per day$")
_QUOTED_SPECIAL_LABEL_RE = re.compile(
    r"^[\"'](?P<label>unknown|no seizure frequency reference)[\"']$",
    re.IGNORECASE,
)
_MATCHING_RATE_RANGE_RE = re.compile(
    r"^(?P<count>\d+(?:\.\d+)?) per (?P<first>\d+(?:\.\d+)?) "
    r"(?P<first_unit>day|week|month|year) to (?P=count) per "
    r"(?P<second>\d+(?:\.\d+)?) (?P<second_unit>day|week|month|year)$"
)
_SEIZURE_FREE_RE = re.compile(
    r"^seizure free for (?P<count>\d+(?:\.\d+)?) (?P<unit>month|year)$"
)
_YTD_NOTE_RE = re.compile(r"\b(year to date|ytd|since january)\b", re.IGNORECASE)
_FORBIDDEN_UNIT_RE = re.compile(
    r"\b(quarter|quarters|fortnight|fortnights|night|nights|hour|hours)\b",
    re.IGNORECASE,
)
_ADJECTIVE_RATE_LABELS = {
    "daily": "1 per day",
    "nightly": "1 per day",
    "weekly": "1 per week",
    "monthly": "1 per month",
    "biweekly": "1 per 2 week",
    "fortnightly": "1 per 2 week",
}
_EVIDENCE_PROMPT_FOOTER_MARKERS = (
    "Respond with the corresponding output fields",
    "[[ ## ",
    "In adhering to this structure",
)


def _normalize_predicted_label(label: str | None) -> str | None:
    if label is None:
        return None

    stripped = label.strip()
    # Strip outer quotes from any fully-quoted label (model sometimes wraps
    # output in single or double quotes). This is surface normalization only.
    if len(stripped) >= 2 and stripped[0] in '"\'' and stripped[-1] == stripped[0]:
        stripped = stripped[1:-1].strip()

    quoted_special = _QUOTED_SPECIAL_LABEL_RE.match(stripped)
    if quoted_special:
        return quoted_special.group("label").lower()

    normalized = _apply_canonical_surface_repairs(stripped)

    every_day_range = _EVERY_DAY_RANGE_RE.match(normalized)
    if every_day_range:
        return f"1 per 1 to {every_day_range.group('end')} day"

    matching_rate_range = _MATCHING_RATE_RANGE_RE.match(normalized)
    if (
        matching_rate_range
        and matching_rate_range.group("first_unit") == matching_rate_range.group("second_unit")
    ):
        first = matching_rate_range.group("first")
        second = matching_rate_range.group("second")
        low, high = sorted((float(first), float(second)))
        return (
            f"{matching_rate_range.group('count')} per "
            f"{_format_number(low)} to {_format_number(high)} "
            f"{matching_rate_range.group('first_unit')}"
        )

    daily_count = _DAILY_COUNT_RE.match(normalized)
    if daily_count and float(daily_count.group("count")) > 33:
        return "multiple per day"

    return normalized


def _apply_canonical_surface_repairs(label: str) -> str:
    normalized = re.sub(r"\s+", " ", label.strip().lower())
    normalized = re.sub(
        r"^(?:<=|>=|<|>|at most|at least|up to)\s*",
        "",
        normalized,
    )
    if normalized in _ADJECTIVE_RATE_LABELS:
        return _ADJECTIVE_RATE_LABELS[normalized]

    normalized = re.sub(r"\b(few|several)\b", "multiple", normalized)
    normalized = re.sub(
        r"(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)",
        r"\1 to \2",
        normalized,
    )
    normalized = re.sub(
        r"(\d+(?:\.\d+)?)\s+or\s+(\d+(?:\.\d+)?)",
        r"\1 to \2",
        normalized,
    )
    normalized = re.sub(r"\bper\s+fortnight\b", "per 2 week", normalized)
    normalized = re.sub(r"\bper\s+fortnights\b", "per 2 week", normalized)
    normalized = re.sub(r"\bper\s+quarter\b", "per 3 month", normalized)
    normalized = re.sub(r"\bper\s+quarters\b", "per 3 month", normalized)
    return normalized


def _guard_evidence_text(
    note_text: str,
    evidence_text: str | None,
) -> tuple[str | None, list[str]]:
    if not evidence_text:
        return None, []

    flags: list[str] = []
    cleaned = evidence_text.strip()

    for marker in _EVIDENCE_PROMPT_FOOTER_MARKERS:
        marker_index = cleaned.find(marker)
        if marker_index != -1:
            cleaned = cleaned[:marker_index].rstrip()
            if "evidence_repaired:prompt_footer_stripped" not in flags:
                flags.append("evidence_repaired:prompt_footer_stripped")

    if cleaned in note_text:
        return cleaned, flags

    prefix = cleaned
    while prefix and prefix not in note_text:
        prefix = prefix[:-1].rstrip()
    if prefix and prefix != cleaned:
        flags.append("evidence_repaired:truncated_to_note_span")
        return prefix, flags

    return cleaned, flags


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return str(value)


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
    program_variant: str = GAN_FREQUENCY_S0_VARIANT,
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
        program_variant=program_variant,
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
