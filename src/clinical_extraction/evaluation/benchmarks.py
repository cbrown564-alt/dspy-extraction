from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import ConfigDict

from clinical_extraction.schemas import FrozenModel


class AlignmentLabel(StrEnum):
    ALIGNED = "aligned"
    PARTIAL = "partial"
    NOT_COMPARABLE = "not_comparable"


class BenchmarkReference(FrozenModel):
    benchmark_id: str
    dataset: Literal["exect_v2", "gan_2026"]
    metric_name: str
    value: float | int
    source: str
    evaluation_set: str
    metric_definition: str
    caveats: tuple[str, ...] = ()


class AlignmentContext(FrozenModel):
    dataset: str
    evaluation_set: str
    scorer_mode: str
    metric_name: str
    schema_level: str


class BenchmarkAlignment(FrozenModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    label: AlignmentLabel
    reference: BenchmarkReference | None
    caveats: tuple[str, ...]


EXECT_TABLE1_REFERENCES: dict[str, BenchmarkReference] = {
    "birth_history.gold_annotations": BenchmarkReference(
        benchmark_id="exectv2.table1.birth_history.gold_annotations",
        dataset="exect_v2",
        metric_name="gold_annotations",
        value=47,
        source="ExECTv2 paper Table 1",
        evaluation_set="synthetic_200",
        metric_definition="Consensus gold annotation count for the annotation family.",
    ),
    "birth_history.per_item_f1": BenchmarkReference(
        benchmark_id="exectv2.table1.birth_history.per_item_f1",
        dataset="exect_v2",
        metric_name="per_item_f1",
        value=0.97,
        source="ExECTv2 paper Table 1",
        evaluation_set="synthetic_200",
        metric_definition="Entity-level F1 for the ExECTv2 pipeline against consensus gold.",
    ),
    "birth_history.per_letter_f1": BenchmarkReference(
        benchmark_id="exectv2.table1.birth_history.per_letter_f1",
        dataset="exect_v2",
        metric_name="per_letter_f1",
        value=0.98,
        source="ExECTv2 paper Table 1",
        evaluation_set="synthetic_200",
        metric_definition="Letter-level F1 for at least one correct entity extraction with features.",
    ),
    "diagnosis.gold_annotations": BenchmarkReference(
        benchmark_id="exectv2.table1.diagnosis.gold_annotations",
        dataset="exect_v2",
        metric_name="gold_annotations",
        value=572,
        source="ExECTv2 paper Table 1",
        evaluation_set="synthetic_200",
        metric_definition="Consensus gold annotation count for the annotation family.",
    ),
    "diagnosis.per_item_f1": BenchmarkReference(
        benchmark_id="exectv2.table1.diagnosis.per_item_f1",
        dataset="exect_v2",
        metric_name="per_item_f1",
        value=0.85,
        source="ExECTv2 paper Table 1",
        evaluation_set="synthetic_200",
        metric_definition="Entity-level F1 for diagnosis annotations using CUI and feature matching.",
    ),
    "diagnosis.per_letter_f1": BenchmarkReference(
        benchmark_id="exectv2.table1.diagnosis.per_letter_f1",
        dataset="exect_v2",
        metric_name="per_letter_f1",
        value=0.94,
        source="ExECTv2 paper Table 1",
        evaluation_set="synthetic_200",
        metric_definition="Letter-level F1 for diagnosis annotations using CUI and feature matching.",
    ),
    "prescription.per_item_f1": BenchmarkReference(
        benchmark_id="exectv2.table1.prescription.per_item_f1",
        dataset="exect_v2",
        metric_name="per_item_f1",
        value=0.87,
        source="ExECTv2 paper Table 1",
        evaluation_set="synthetic_200",
        metric_definition="Entity-level F1 for prescription annotations.",
    ),
    "seizure_frequency.per_item_f1": BenchmarkReference(
        benchmark_id="exectv2.table1.seizure_frequency.per_item_f1",
        dataset="exect_v2",
        metric_name="per_item_f1",
        value=0.66,
        source="ExECTv2 paper Table 1",
        evaluation_set="synthetic_200",
        metric_definition="Entity-level F1 for ExECTv2 seizure-frequency annotations.",
    ),
    "all.gold_annotations": BenchmarkReference(
        benchmark_id="exectv2.table1.all.gold_annotations",
        dataset="exect_v2",
        metric_name="gold_annotations",
        value=2047,
        source="ExECTv2 paper Table 1",
        evaluation_set="synthetic_200",
        metric_definition="Consensus gold annotation count across all Table 1 annotation families.",
    ),
    "all.per_item_f1": BenchmarkReference(
        benchmark_id="exectv2.table1.all.per_item_f1",
        dataset="exect_v2",
        metric_name="per_item_f1",
        value=0.87,
        source="ExECTv2 paper Table 1",
        evaluation_set="synthetic_200",
        metric_definition="Entity-level F1 across all Table 1 annotation families.",
        caveats=(
            "Requires CUI/feature-aware scoring across all ExECTv2 annotation families.",
        ),
    ),
    "all.per_letter_f1": BenchmarkReference(
        benchmark_id="exectv2.table1.all.per_letter_f1",
        dataset="exect_v2",
        metric_name="per_letter_f1",
        value=0.90,
        source="ExECTv2 paper Table 1",
        evaluation_set="synthetic_200",
        metric_definition="Letter-level F1 across all Table 1 annotation families.",
        caveats=(
            "Requires CUI/feature-aware scoring across all ExECTv2 annotation families.",
        ),
    ),
}

GAN_REFERENCES: dict[str, BenchmarkReference] = {
    "abstract.real300.purist_micro_f1": BenchmarkReference(
        benchmark_id="gan2026.abstract.real300.purist_micro_f1",
        dataset="gan_2026",
        metric_name="purist_micro_f1",
        value=0.788,
        source="Gan 2026 abstract",
        evaluation_set="Real(300)",
        metric_definition="Micro-F1 under the fine-grained Purist category scheme.",
    ),
    "abstract.real300.pragmatic_micro_f1": BenchmarkReference(
        benchmark_id="gan2026.abstract.real300.pragmatic_micro_f1",
        dataset="gan_2026",
        metric_name="pragmatic_micro_f1",
        value=0.847,
        source="Gan 2026 abstract",
        evaluation_set="Real(300)",
        metric_definition="Micro-F1 under the Pragmatic category scheme.",
    ),
    "table6.qwen25_14b.real300.purist_micro_f1": BenchmarkReference(
        benchmark_id="gan2026.table6.qwen25_14b.our_cot.real300.purist_micro_f1",
        dataset="gan_2026",
        metric_name="purist_micro_f1",
        value=0.776,
        source="Gan 2026 Table 6",
        evaluation_set="Real(300)",
        metric_definition="Micro-F1 under the Purist scheme after synthetic-only training.",
    ),
    "table6.qwen25_14b.real300.pragmatic_micro_f1": BenchmarkReference(
        benchmark_id="gan2026.table6.qwen25_14b.our_cot.real300.pragmatic_micro_f1",
        dataset="gan_2026",
        metric_name="pragmatic_micro_f1",
        value=0.832,
        source="Gan 2026 Table 6",
        evaluation_set="Real(300)",
        metric_definition="Micro-F1 under the Pragmatic scheme after synthetic-only training.",
    ),
    "table8.cot15000.real300.purist_micro_f1": BenchmarkReference(
        benchmark_id="gan2026.table8.qwen25_14b.cot15000.real300.purist_micro_f1",
        dataset="gan_2026",
        metric_name="purist_micro_f1",
        value=0.788,
        source="Gan 2026 Table 8",
        evaluation_set="Real(300)",
        metric_definition="Micro-F1 under the Purist scheme for synthetic CoT scaling.",
    ),
    "table8.cot15000.real300.pragmatic_micro_f1": BenchmarkReference(
        benchmark_id="gan2026.table8.qwen25_14b.cot15000.real300.pragmatic_micro_f1",
        dataset="gan_2026",
        metric_name="pragmatic_micro_f1",
        value=0.847,
        source="Gan 2026 Table 8",
        evaluation_set="Real(300)",
        metric_definition="Micro-F1 under the Pragmatic scheme for synthetic CoT scaling.",
    ),
}


def benchmark_alignment(context: AlignmentContext) -> BenchmarkAlignment:
    if context.dataset == "exect_v2":
        return _exect_alignment(context)
    if context.dataset == "gan_2026":
        return _gan_alignment(context)
    return BenchmarkAlignment(
        label=AlignmentLabel.NOT_COMPARABLE,
        reference=None,
        caveats=(f"No published benchmark reference is registered for {context.dataset!r}.",),
    )


def _exect_alignment(context: AlignmentContext) -> BenchmarkAlignment:
    reference = EXECT_TABLE1_REFERENCES["all.per_item_f1"]
    if context.scorer_mode == "exect_field_family_deterministic_v1":
        return BenchmarkAlignment(
            label=AlignmentLabel.PARTIAL,
            reference=reference,
            caveats=(
                "Current ExECT scoring is a narrower audited field-family view: diagnosis, seizure type, and annotated medication.",
                "Published ExECTv2 Table 1 values require CUI/feature-aware scoring across all annotation families.",
                "Planned/current medication status is excluded from benchmark-facing repo metrics until reliable temporality gold exists.",
            ),
        )
    if context.scorer_mode == "exect_s2_field_family_deterministic_v1":
        return BenchmarkAlignment(
            label=AlignmentLabel.PARTIAL,
            reference=reference,
            caveats=(
                "Current ExECT S2 scoring extends S1 with investigation and comorbidity families only.",
                "Published ExECTv2 Table 1 values require CUI/feature-aware scoring across all annotation families.",
                "Investigation labels use modality+result strings; comorbidities exclude seizure-history PatientHistory phrases.",
            ),
        )
    if context.scorer_mode == "exect_s3_field_family_deterministic_v1":
        return BenchmarkAlignment(
            label=AlignmentLabel.PARTIAL,
            reference=reference,
            caveats=(
                "Current ExECT S3 scoring extends frozen S2 with birth history, onset, epilepsy cause, and when diagnosed.",
                "Published ExECTv2 Table 1 values require CUI/feature-aware scoring across all annotation families.",
                "Overlapping CUIPhrases across families are scored per entity type; see docs/experiments/exect/exect_s3_phase1_overlap_policy.md.",
            ),
        )
    if context.scorer_mode == "exect_s4_field_family_deterministic_v1":
        return BenchmarkAlignment(
            label=AlignmentLabel.PARTIAL,
            reference=reference,
            caveats=(
                "Current ExECT S4 scoring extends frozen S3 with seizure frequency and medication temporality.",
                "Published ExECTv2 Table 1 values require CUI/feature-aware scoring across all annotation families.",
                "Medication temporality is inferred from prescription span text; see docs/experiments/exect/exect_s4_gold_policy.md.",
            ),
        )
    return BenchmarkAlignment(
        label=AlignmentLabel.NOT_COMPARABLE,
        reference=reference,
        caveats=(
            "The ExECT scorer mode is not registered as benchmark-aligned.",
            "Do not compare against Table 1 without documented CUI/feature-aware metric compatibility.",
        ),
    )


def _gan_alignment(context: AlignmentContext) -> BenchmarkAlignment:
    reference = _gan_reference_for_metric(context.metric_name)
    if reference is None:
        return BenchmarkAlignment(
            label=AlignmentLabel.NOT_COMPARABLE,
            reference=None,
            caveats=(
                f"No Gan published benchmark reference is registered for {context.metric_name!r}.",
                "Raw exact, normalized-label exact, evidence, and abstention metrics are diagnostic.",
            ),
        )
    if context.scorer_mode != "gan2026_paper_reproduction":
        return BenchmarkAlignment(
            label=AlignmentLabel.NOT_COMPARABLE,
            reference=reference,
            caveats=(
                "Gan paper-number comparisons require scorer_mode='gan2026_paper_reproduction'.",
                "Canonical Gan project metrics preserve no-reference semantics and must stay separate from author-evaluator compatibility metrics.",
            ),
        )
    if _normalize_evaluation_set(context.evaluation_set) == "real(300)" and context.metric_name in {
        "purist_micro_f1",
        "pragmatic_micro_f1",
    }:
        return BenchmarkAlignment(
            label=AlignmentLabel.ALIGNED,
            reference=reference,
            caveats=(
                "Alignment assumes every evaluated record has exactly one valid category prediction.",
                "Evidence diagnostics remain separate from the published frequency classification metric.",
            ),
        )
    return BenchmarkAlignment(
        label=AlignmentLabel.PARTIAL,
        reference=reference,
        caveats=(
            "Gan label normalization and category boundaries match the published scoring direction.",
            "Current repo data is not the Gan Real(300) or Real(150) evaluation set used for the published benchmark.",
            "Category accuracy can coincide with micro-F1 only for single-label multiclass reports with one valid prediction per record.",
        ),
    )


def _gan_reference_for_metric(metric_name: str) -> BenchmarkReference | None:
    if metric_name.startswith("purist_"):
        return GAN_REFERENCES["table8.cot15000.real300.purist_micro_f1"]
    if metric_name.startswith("pragmatic_"):
        return GAN_REFERENCES["table8.cot15000.real300.pragmatic_micro_f1"]
    return None


def _normalize_evaluation_set(evaluation_set: str) -> str:
    return evaluation_set.strip().lower().replace(" ", "")
