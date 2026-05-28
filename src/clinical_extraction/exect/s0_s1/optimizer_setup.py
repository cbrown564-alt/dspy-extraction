"""Optimizer setup and run metadata contracts for ExECT S0/S1."""
from __future__ import annotations

import dspy

from clinical_extraction.exect.s0_s1.constants import (
    EXECT_DATASET,
    EXECT_S0_S1_PROMPT_VERSION,
    EXECT_S0_S1_SCHEMA_LEVEL,
    EXECT_S0_S1_SCORER,
    EXECT_S0_S1_STAGE_GRAPH_BY_VARIANT,
    EXECT_S0_S1_VARIANT,
)
from clinical_extraction.exect.s0_s1.metrics import EXECT_S0_S1_OPTIMIZER_METRICS
from clinical_extraction.exect.s0_s1.modules import (
    ExectS0S1FieldFamilyModule,
    build_exect_s0_s1_module,
)
from clinical_extraction.runs import RunMetadata
from clinical_extraction.schemas import ExectGoldDocument

def make_exect_s0_s1_dspy_examples(
    records: list[ExectGoldDocument],
) -> list[dspy.Example]:
    """Convert audited ExECT gold documents into DSPy examples."""
    return [
        dspy.Example(
            note_text=record.text,
            document_id=record.document_id,
            diagnosis=record.diagnoses,
            seizure_type=record.seizure_types,
            annotated_medication=record.current_medications,
        ).with_inputs("note_text")
        for record in records
    ]


def compile_exect_s0_s1_module(
    records: list[ExectGoldDocument],
    *,
    program_variant: str = EXECT_S0_S1_VARIANT,
    prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
    optimizer_name: str = "BootstrapFewShot",
    max_bootstrapped_demos: int = 4,
    max_labeled_demos: int = 0,
    max_rounds: int = 1,
    num_candidate_programs: int = 16,
    optimizer_metric: str = "exect_field_family_micro_f1",
) -> ExectS0S1FieldFamilyModule:
    """Compile an ExECT S0/S1 single-pass module with a few-shot DSPy optimizer."""
    if program_variant != EXECT_S0_S1_VARIANT:
        raise ValueError(
            f"ExECT S0/S1 optimizer compilation supports {EXECT_S0_S1_VARIANT!r} only; "
            f"got {program_variant!r}."
        )

    trainset = make_exect_s0_s1_dspy_examples(records)
    module = build_exect_s0_s1_module(program_variant, prompt_version=prompt_version)
    assert isinstance(module, ExectS0S1FieldFamilyModule)

    if optimizer_name == "LabeledFewShot":
        optimizer = dspy.LabeledFewShot(k=max_labeled_demos)
        return optimizer.compile(module, trainset=trainset)

    try:
        metric = EXECT_S0_S1_OPTIMIZER_METRICS[optimizer_metric]
    except KeyError as exc:
        allowed = ", ".join(sorted(EXECT_S0_S1_OPTIMIZER_METRICS))
        raise ValueError(
            f"Unknown optimizer_metric {optimizer_metric!r}; use {allowed}."
        ) from exc

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
            f"Unsupported ExECT S0/S1 optimizer {optimizer_name!r}; use "
            "LabeledFewShot, BootstrapFewShot, or BootstrapFewShotWithRandomSearch."
        )

    optimizer = dspy.BootstrapFewShot(
        metric=metric,
        max_bootstrapped_demos=max_bootstrapped_demos,
        max_labeled_demos=max_labeled_demos,
        max_rounds=max_rounds,
    )
    return optimizer.compile(module, trainset=trainset)


def stage_graph_id_for_program_variant(program_variant: str) -> str | None:
    return EXECT_S0_S1_STAGE_GRAPH_BY_VARIANT.get(program_variant)


def exect_s0_s1_run_metadata(
    run_id: str,
    split_name: str,
    model_provider: str,
    model_name: str,
    *,
    prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
    program_variant: str = EXECT_S0_S1_VARIANT,
    extra: dict | None = None,
) -> RunMetadata:
    """Build run metadata for an ExECT S0/S1 field-family run."""
    return RunMetadata(
        run_id=run_id,
        dataset=EXECT_DATASET,
        split_name=split_name,
        model_provider=model_provider,
        model_name=model_name,
        schema_level=EXECT_S0_S1_SCHEMA_LEVEL,
        program_variant=program_variant,
        scorer_mode=EXECT_S0_S1_SCORER,
        metric_caveats=[
            "These are partial ExECT S0/S1 diagnostics, not published ExECTv2 benchmark reproduction.",
            "Benchmark-facing fields are limited to diagnosis, seizure type, and annotated medications.",
            "Medication temporality is intentionally not benchmark-facing in this baseline.",
            "Evidence quote support is diagnostic and should be reported separately from label metrics.",
        ],
        metadata={
            "prompt_version": prompt_version,
            **(extra or {}),
        },
    )
