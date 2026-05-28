"""Gan S0 DSPy optimizer setup and example builders."""
from __future__ import annotations

from pathlib import Path

import dspy

from clinical_extraction.gan.s0.metrics import GAN_FREQUENCY_S0_OPTIMIZER_METRICS
from clinical_extraction.gan.s0.modules import (
    GanFrequencyS0DirectModule,
    GanFrequencyS0Module,
    GanFrequencyS0TemporalCandidatesSinglePassModule,
    GanFrequencyS0TemporalCandidatesVerifyRepairModule,
    GanFrequencyS0VerifyRepairModule,
    build_gan_s0_module,
)
from clinical_extraction.gan.s0.variant_routing import (
    GAN_FREQUENCY_S0_DIRECT_VARIANT,
    GAN_FREQUENCY_S0_VARIANT,
)
from clinical_extraction.schemas import GanRecord


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


def _gan_s0_optimizer_trainset(
    records: list[GanRecord],
    *,
    optimizer_metric: str,
) -> list[dspy.Example]:
    if optimizer_metric in {
        "semantic_frequency_with_evidence",
        "semantic_frequency_with_evidence_feedback",
        "gan_s0_stage_attributed_frequency_feedback",
        "synthesis_exact_with_evidence",
        "synthesis_exact_with_evidence_feedback",
    }:
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
    optimizer_metric: str = "semantic_frequency_with_evidence",
) -> (
    GanFrequencyS0Module
    | GanFrequencyS0DirectModule
    | GanFrequencyS0VerifyRepairModule
    | GanFrequencyS0TemporalCandidatesVerifyRepairModule
    | GanFrequencyS0TemporalCandidatesSinglePassModule
):
    """Compile a Gan S0 module with a few-shot DSPy optimizer.

    Supports ``LabeledFewShot``, ``BootstrapFewShot``, and
    ``BootstrapFewShotWithRandomSearch`` (``BootstrapRS``). LabeledFewShot
    samples labeled demonstrations from the trainset without bootstrapping.
    BootstrapFewShot keeps teacher traces that pass the optimizer metric.
    BootstrapFewShotWithRandomSearch searches over candidate demo sets.

    For verify-repair variants, LabeledFewShot compiles only the extractor
    sub-module so trainset demos stay on the direct extraction signature.
    """
    trainset = _gan_s0_optimizer_trainset(records, optimizer_metric=optimizer_metric)
    module = build_gan_s0_module(program_variant)

    if optimizer_name == "LabeledFewShot":
        optimizer = dspy.LabeledFewShot(k=max_labeled_demos)
        if isinstance(
            module,
            (
                GanFrequencyS0VerifyRepairModule,
                GanFrequencyS0TemporalCandidatesVerifyRepairModule,
            ),
        ):
            module.extractor = optimizer.compile(module.extractor, trainset=trainset)
            return module
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
    optimizer_metric: str = "semantic_frequency_with_evidence_feedback",
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
