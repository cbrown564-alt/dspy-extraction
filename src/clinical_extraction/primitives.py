from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, model_validator

from clinical_extraction.experiments.taxonomy import (
    HybridBalanceClassValue,
    InterleavingPositionValue,
)
from clinical_extraction.schemas import FrozenModel, NormalizedValue

PrimitiveDatasetValue = Literal["gan_2026", "exect_v2", "shared"]
PrimitiveFieldFamilyValue = Literal[
    "frequency",
    "diagnosis",
    "seizure_type",
    "medication",
    "investigation",
    "comorbidity",
    "birth_development",
    "onset",
    "epilepsy_cause",
    "when_diagnosed",
    "family_history",
    "social_history",
    "driving",
    "pregnancy",
    "multi_family",
]
PrimitiveOperationValue = Literal[
    "candidate_generation",
    "controlled_vocabulary",
    "normalization",
    "benchmark_bridge",
    "evidence_support",
    "verification",
    "repair",
    "tool_interface",
    "fixture_definition",
    "inspection_reporting",
]
PrimitiveKnowledgeSourceValue = Literal[
    "regex_rules",
    "temporal_rules",
    "controlled_vocabulary",
    "benchmark_label_policy",
    "json_schema",
    "pydantic_validation",
    "manual_examples",
    "bootstrapped_examples",
    "optimizer_feedback",
    "cui_or_ontology",
    "gold_audit_policy",
    "temporal_tooling",
    "diagnostic_metric",
]
PrimitiveControlModeValue = Literal[
    "none",
    "soft_hint",
    "hard_constraint",
    "tool_affordance",
    "posthoc_correction",
    "diagnostic_only",
]
PrimitiveArmValue = Literal["L0", "L1", "H1", "H2", "H3", "H4", "D1"]
PrimitiveStatusValue = Literal["planned", "implemented", "validated", "deprecated"]
NormalizationScopeValue = Literal[
    "none",
    "model_only",
    "deterministic_mapping",
    "benchmark_bridge",
    "scorer_only",
]
EvidenceSupportStatusValue = Literal[
    "exact_substring",
    "normalized_interpretation",
    "unsupported_quote",
    "no_reference",
]


class PrimitiveMetadata(FrozenModel):
    """Research-facing metadata contract for reusable taxonomy primitives."""

    primitive_id: str = Field(pattern=r"^[a-z0-9]+(\.[a-z0-9_]+)+\.v[0-9]+$")
    name: str
    dataset: PrimitiveDatasetValue
    field_families: list[PrimitiveFieldFamilyValue] = Field(min_length=1)
    clinical_operation: PrimitiveOperationValue
    knowledge_sources: list[PrimitiveKnowledgeSourceValue] = Field(min_length=1)
    hybrid_balance_class: list[HybridBalanceClassValue] = Field(min_length=1)
    interleaving_positions: list[InterleavingPositionValue] = Field(min_length=1)
    control_modes: list[PrimitiveControlModeValue] = Field(min_length=1)
    input_contract: str
    output_contract: str
    compatible_experiment_arms: list[PrimitiveArmValue] = Field(min_length=1)
    status: PrimitiveStatusValue = "planned"
    normalization_scope: NormalizationScopeValue = "none"
    caveats: list[str] = Field(default_factory=list)
    intended_comparison_groups: list[str] = Field(default_factory=list)
    implementation_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def infer_default_normalization_scope(cls, data: Any) -> Any:
        if not isinstance(data, dict) or data.get("normalization_scope", "none") != "none":
            return data
        clinical_operation = data.get("clinical_operation")
        knowledge_sources = data.get("knowledge_sources", [])
        if clinical_operation == "benchmark_bridge":
            data["normalization_scope"] = "benchmark_bridge"
        elif (
            clinical_operation == "normalization"
            and "benchmark_label_policy" in knowledge_sources
        ):
            data["normalization_scope"] = "benchmark_bridge"
        elif clinical_operation == "normalization":
            data["normalization_scope"] = "deterministic_mapping"
        return data

    @model_validator(mode="after")
    def validate_primitive_contract(self) -> PrimitiveMetadata:
        text_fields = {
            "name": self.name,
            "input_contract": self.input_contract,
            "output_contract": self.output_contract,
        }
        for field_name, value in text_fields.items():
            if not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")

        if (
            "posthoc_correction" in self.control_modes
            and "post" not in self.interleaving_positions
        ):
            raise ValueError("posthoc_correction requires post interleaving.")
        if "tool_affordance" in self.control_modes and "tool_during" not in (
            self.interleaving_positions
        ):
            raise ValueError("tool_affordance requires tool_during interleaving.")
        if "diagnostic_only" in self.control_modes and "eval_only" not in (
            self.interleaving_positions
        ):
            raise ValueError("diagnostic_only requires eval_only interleaving.")
        return self

    @property
    def is_prediction_affecting(self) -> bool:
        return not (
            set(self.interleaving_positions) == {"eval_only"}
            or set(self.control_modes) == {"diagnostic_only"}
        )


class PrimitiveCandidate(FrozenModel):
    """Shared deterministic hint/candidate payload for taxonomy primitives."""

    primitive_id: str = Field(pattern=r"^[a-z0-9]+(\.[a-z0-9_]+)+\.v[0-9]+$")
    dataset: PrimitiveDatasetValue
    field_family: PrimitiveFieldFamilyValue
    raw_text: str
    normalized_value: NormalizedValue = None
    benchmark_value: NormalizedValue = None
    source_span_text: str
    start: int | None = None
    end: int | None = None
    rule_name: str
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    caveats: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_candidate_contract(self) -> PrimitiveCandidate:
        text_fields = {
            "raw_text": self.raw_text,
            "source_span_text": self.source_span_text,
            "rule_name": self.rule_name,
        }
        for field_name, value in text_fields.items():
            if not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")
        if (self.start is None) != (self.end is None):
            raise ValueError("source offsets must provide both start and end, or neither.")
        if self.start is not None and self.end is not None:
            if self.start < 0 or self.end < 0:
                raise ValueError("source offsets must be non-negative.")
            if self.end < self.start:
                raise ValueError("source end offset must be greater than or equal to start.")
        return self

    @property
    def is_benchmark_aligned(self) -> bool:
        return self.benchmark_value is not None and (
            self.benchmark_value == self.normalized_value
            or self.benchmark_value == self.raw_text
        )


class NormalizationResult(FrozenModel):
    """Shared output contract for normalization and benchmark bridge primitives."""

    primitive_id: str = Field(pattern=r"^[a-z0-9]+(\.[a-z0-9_]+)+\.v[0-9]+$")
    dataset: PrimitiveDatasetValue
    field_family: PrimitiveFieldFamilyValue
    raw_value: NormalizedValue
    canonical_value: NormalizedValue
    benchmark_value: NormalizedValue = None
    clinical_caveat: str | None = None
    transformation_rule: str
    prediction_affecting: bool
    scorer_only: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_normalization_contract(self) -> NormalizationResult:
        if not self.transformation_rule.strip():
            raise ValueError("transformation_rule must be a non-empty string.")
        if self.scorer_only and self.prediction_affecting:
            raise ValueError("scorer_only normalization cannot be prediction-affecting.")
        return self

    @property
    def has_changed_value(self) -> bool:
        return self.raw_value != self.canonical_value

    @property
    def is_benchmark_bridge(self) -> bool:
        return self.benchmark_value is not None and (
            self.benchmark_value != self.raw_value
            or self.benchmark_value != self.canonical_value
        )


class EvidenceSupportResult(FrozenModel):
    """Deterministic support status for quotes and normalized interpretations."""

    primitive_id: str = Field(
        default="shared.evidence.substring_support.v1",
        pattern=r"^[a-z0-9]+(\.[a-z0-9_]+)+\.v[0-9]+$",
    )
    document_text: str
    quote: str | None = None
    normalized_value: NormalizedValue = None
    interpretation_evidence_text: str | None = None
    support_status: EvidenceSupportStatusValue
    raw_quote_supported: bool = False
    normalized_interpretation_supported: bool = False
    start: int | None = None
    end: int | None = None
    caveats: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_evidence_support_contract(self) -> EvidenceSupportResult:
        if self.support_status == "exact_substring" and not self.raw_quote_supported:
            raise ValueError("exact_substring requires raw quote support.")
        if (
            self.support_status == "normalized_interpretation"
            and not self.normalized_interpretation_supported
        ):
            raise ValueError(
                "normalized_interpretation requires interpretation support."
            )
        if self.support_status == "no_reference" and self.quote:
            raise ValueError("no_reference requires an empty quote.")
        if (self.start is None) != (self.end is None):
            raise ValueError("support offsets must provide both start and end, or neither.")
        if self.start is not None and self.end is not None:
            if self.start < 0 or self.end < 0:
                raise ValueError("support offsets must be non-negative.")
            if self.end < self.start:
                raise ValueError("support end offset must be greater than or equal to start.")
            if self.document_text[self.start : self.end] not in {
                self.quote,
                self.interpretation_evidence_text,
            }:
                raise ValueError("support offsets must match the supported text.")
        return self


def check_evidence_support(
    *,
    document_text: str,
    quote: str | None,
    normalized_value: NormalizedValue = None,
    interpretation_evidence_text: str | None = None,
    primitive_id: str = "shared.evidence.substring_support.v1",
) -> EvidenceSupportResult:
    """Classify deterministic source support for a quote or interpretation text."""

    if quote is None or not quote.strip():
        return EvidenceSupportResult(
            primitive_id=primitive_id,
            document_text=document_text,
            quote=quote,
            normalized_value=normalized_value,
            interpretation_evidence_text=interpretation_evidence_text,
            support_status="no_reference",
        )

    quote_range = _find_text_range(document_text, quote)
    if quote_range is not None:
        start, end = quote_range
        return EvidenceSupportResult(
            primitive_id=primitive_id,
            document_text=document_text,
            quote=quote,
            normalized_value=normalized_value,
            interpretation_evidence_text=interpretation_evidence_text,
            support_status="exact_substring",
            raw_quote_supported=True,
            start=start,
            end=end,
        )

    interpretation_range = _find_text_range(document_text, interpretation_evidence_text)
    if interpretation_range is not None:
        start, end = interpretation_range
        return EvidenceSupportResult(
            primitive_id=primitive_id,
            document_text=document_text,
            quote=quote,
            normalized_value=normalized_value,
            interpretation_evidence_text=interpretation_evidence_text,
            support_status="normalized_interpretation",
            normalized_interpretation_supported=True,
            start=start,
            end=end,
            caveats=[
                "Evidence supports the source phrase, not necessarily the normalized value."
            ],
        )

    return EvidenceSupportResult(
        primitive_id=primitive_id,
        document_text=document_text,
        quote=quote,
        normalized_value=normalized_value,
        interpretation_evidence_text=interpretation_evidence_text,
        support_status="unsupported_quote",
    )


def _find_text_range(document_text: str, text: str | None) -> tuple[int, int] | None:
    if text is None or not text:
        return None
    start = document_text.find(text)
    if start == -1:
        return None
    return start, start + len(text)


PRIMITIVE_REGISTRY: tuple[PrimitiveMetadata, ...] = (
    PrimitiveMetadata(
        primitive_id="gan.frequency.temporal_candidates.v1",
        name="Gan temporal frequency candidates",
        dataset="gan_2026",
        field_families=["frequency"],
        clinical_operation="candidate_generation",
        knowledge_sources=["temporal_rules", "regex_rules", "gold_audit_policy"],
        hybrid_balance_class=[
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        interleaving_positions=["pre"],
        control_modes=["soft_hint"],
        input_contract="Gan note text plus optional document metadata.",
        output_contract=(
            "Temporal seizure-frequency candidates with raw spans and benchmark caveats."
        ),
        compatible_experiment_arms=["H2", "H4"],
        status="implemented",
        caveats=[
            "Gan seizure_frequency_number[0] remains the benchmark-facing gold label.",
            "Monthly normalization is separate from ExECT frequency policy.",
        ],
        implementation_refs=[
            "src/clinical_extraction/gan/temporal_candidates.py",
            "src/clinical_extraction/programs/gan_frequency_s0.py",
        ],
    ),
    PrimitiveMetadata(
        primitive_id="exect.medication.rx_candidates.v1",
        name="ExECT medication prescription candidates",
        dataset="exect_v2",
        field_families=["medication"],
        clinical_operation="candidate_generation",
        knowledge_sources=["regex_rules", "controlled_vocabulary", "gold_audit_policy"],
        hybrid_balance_class=[
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        interleaving_positions=["pre"],
        control_modes=["soft_hint"],
        input_contract="ExECT note text with prescription-style medication surfaces.",
        output_contract=(
            "Note-anchored medication candidates with raw surface, canonical ASM, "
            "benchmark-facing value when current, temporality, and caveats."
        ),
        compatible_experiment_arms=["H2", "H4"],
        status="implemented",
        caveats=[
            "Broad S1 pre-vocabulary prompting was rejected; this primitive is medication-scoped.",
            "Planned and previous medications are surfaced diagnostically, not as S1 current prescriptions.",
        ],
        implementation_refs=["src/clinical_extraction/exect/primitives.py"],
    ),
    PrimitiveMetadata(
        primitive_id="exect.medication.benchmark_bridge.v1",
        name="ExECT medication benchmark bridge",
        dataset="exect_v2",
        field_families=["medication"],
        clinical_operation="normalization",
        knowledge_sources=["controlled_vocabulary", "benchmark_label_policy"],
        hybrid_balance_class=["H1_post_deterministic"],
        interleaving_positions=["post"],
        control_modes=["posthoc_correction"],
        input_contract="Raw medication predictions with evidence quotes.",
        output_contract=(
            "Raw, canonical, benchmark-facing, and caveated medication values."
        ),
        compatible_experiment_arms=["H1"],
        status="implemented",
        caveats=[
            "Do not reintroduce broad pre-vocabulary prompting as the default S1 medication path.",
            "Brand surfaces are preserved when the note uses an audited brand form.",
            "Non-ASM medications are rejected from benchmark-facing annotated medication output.",
        ],
        implementation_refs=["src/clinical_extraction/exect/primitives.py"],
    ),
    PrimitiveMetadata(
        primitive_id="exect.medication_temporality.post_classifier.v1",
        name="ExECT medication temporality post-classifier",
        dataset="exect_v2",
        field_families=["medication"],
        clinical_operation="benchmark_bridge",
        knowledge_sources=["temporal_rules", "benchmark_label_policy", "gold_audit_policy"],
        hybrid_balance_class=["H1_post_deterministic", "D1_deterministic_only"],
        interleaving_positions=["post", "eval_only"],
        control_modes=["posthoc_correction", "diagnostic_only"],
        input_contract="Medication evidence text or prescription-line context.",
        output_contract=(
            "Current, planned, previous, or unknown medication temporality with S1 "
            "benchmark-inclusion semantics and cue metadata."
        ),
        compatible_experiment_arms=["H1", "D1"],
        status="implemented",
        caveats=[
            "MarkupPrescriptions has no temporality column; this is cue-based support, not raw gold.",
            "Current prescription lines with taper instructions remain current for S1 unless the medication is only a separate stop/plan mention.",
        ],
        implementation_refs=["src/clinical_extraction/exect/primitives.py"],
    ),
    PrimitiveMetadata(
        primitive_id="exect.medication_temporality.non_asm_guard.v1",
        name="ExECT medication temporality non-ASM guard",
        dataset="exect_v2",
        field_families=["medication"],
        clinical_operation="benchmark_bridge",
        knowledge_sources=["benchmark_label_policy", "gold_audit_policy"],
        hybrid_balance_class=["H1_post_deterministic"],
        interleaving_positions=["post", "eval_only"],
        control_modes=["posthoc_correction", "diagnostic_only"],
        input_contract="Raw medication|status labels from S4 LLM extraction.",
        output_contract=(
            "ASM medication temporality labels with model-assigned status preserved; "
            "non-ASM and unlisted medications removed."
        ),
        compatible_experiment_arms=["H1", "D1"],
        status="implemented",
        caveats=[
            "Does not reclassify planned/previous/current from evidence (unlike post_classifier.v1).",
            "Does not drop dose-only current ASM rows when model status is current.",
        ],
        implementation_refs=["src/clinical_extraction/exect/primitives.py"],
    ),
    PrimitiveMetadata(
        primitive_id="exect.medication_temporality.non_asm_dose_current_guard.v1",
        name="ExECT medication temporality non-ASM dose-current guard",
        dataset="exect_v2",
        field_families=["medication"],
        clinical_operation="benchmark_bridge",
        knowledge_sources=[
            "temporal_rules",
            "regex_rules",
            "benchmark_label_policy",
            "gold_audit_policy",
        ],
        hybrid_balance_class=["H1_post_deterministic"],
        interleaving_positions=["post", "eval_only"],
        control_modes=["posthoc_correction", "diagnostic_only"],
        input_contract=(
            "Raw medication|status labels from S4 extraction plus aligned evidence quotes."
        ),
        output_contract=(
            "ASM medication temporality labels with non-ASM labels removed, explicit "
            "planned/previous evidence required, and dose-line current ASM labels preserved."
        ),
        compatible_experiment_arms=["H1", "D1"],
        status="implemented",
        caveats=[
            "Medication temporality gold is span-inferred because ExECT prescription JSON has no temporality column.",
            "This is a narrow follow-up to the rejected broad post-classifier; it should not be treated as default behavior without a model-backed gate.",
            "Dose-line current fallback applies only to ASM labels already emitted as current by the model.",
        ],
        implementation_refs=["src/clinical_extraction/exect/primitives.py"],
    ),
    PrimitiveMetadata(
        primitive_id="exect.medication.am_guard_non_asm_brand_alias.v1",
        name="ExECT annotated medication non-ASM and brand alias guard",
        dataset="exect_v2",
        field_families=["medication"],
        clinical_operation="benchmark_bridge",
        knowledge_sources=["controlled_vocabulary", "benchmark_label_policy", "gold_audit_policy"],
        hybrid_balance_class=["H1_post_deterministic"],
        interleaving_positions=["post", "eval_only"],
        control_modes=["posthoc_correction", "diagnostic_only"],
        input_contract="Raw medication labels from LLM extraction plus aligned evidence quotes.",
        output_contract=(
            "ASM medication labels with non-ASM medications removed, eplim/eplim chrono repaired, "
            "and duplicate same-canonical medications deduplicated."
        ),
        compatible_experiment_arms=["H1", "D1"],
        status="implemented",
        normalization_scope="benchmark_bridge",
        caveats=[
            "Prunes non-ASM medications from ExECT annotated medication output.",
            "Repairs spelling variations eplim/eplim chrono and preserves benchmark-facing brand policy.",
            "Deduplicates same-canonical medications while preserving explicit generic predictions."
        ],
        implementation_refs=["src/clinical_extraction/exect/primitives.py"],
    ),
    PrimitiveMetadata(
        primitive_id="exect.seizure_type.benchmark_bridge.v1",
        name="ExECT seizure-type benchmark bridge",
        dataset="exect_v2",
        field_families=["seizure_type"],
        clinical_operation="benchmark_bridge",
        knowledge_sources=["controlled_vocabulary", "benchmark_label_policy", "gold_audit_policy"],
        hybrid_balance_class=["H1_post_deterministic"],
        interleaving_positions=["post"],
        control_modes=["posthoc_correction"],
        input_contract="Raw seizure-type prediction surface plus optional note text.",
        output_contract=(
            "Raw, canonical, benchmark-facing, and caveated seizure-type values, "
            "including fused-phrase splits and secondary-token co-list decisions."
        ),
        compatible_experiment_arms=["H1"],
        status="implemented",
        caveats=[
            "Do not use MarkupSeizureFrequency spans as seizure-type evidence.",
            "Benchmark-facing labels may be coarser than clinically rich ILAE surfaces.",
            "Full-note pre-vocabulary prompting remains rejected for S1 seizure type.",
        ],
        implementation_refs=["src/clinical_extraction/exect/primitives.py"],
    ),
    PrimitiveMetadata(
        primitive_id="exect.diagnosis.benchmark_bridge.v1",
        name="ExECT diagnosis benchmark bridge",
        dataset="exect_v2",
        field_families=["diagnosis"],
        clinical_operation="benchmark_bridge",
        knowledge_sources=["controlled_vocabulary", "benchmark_label_policy", "gold_audit_policy"],
        hybrid_balance_class=["H1_post_deterministic"],
        interleaving_positions=["post"],
        control_modes=["posthoc_correction"],
        input_contract="Raw diagnosis prediction surfaces plus optional note text.",
        output_contract=(
            "Raw, canonical, benchmark-facing, and caveated diagnosis values, "
            "including uncertainty stripping, specificity collapse, and note-gated co-list decisions."
        ),
        compatible_experiment_arms=["H1"],
        status="implemented",
        caveats=[
            "Do not infer epilepsy subtype from seizure-type evidence alone.",
            "Single-event seizure diagnosis headers must not become established epilepsy diagnoses.",
            "Certainty and specificity rules follow the audited ExECT JSON diagnosis policy.",
        ],
        implementation_refs=["src/clinical_extraction/exect/primitives.py"],
    ),
    PrimitiveMetadata(
        primitive_id="exect.frequency.rate_candidates.v1",
        name="ExECT seizure-frequency rate candidates",
        dataset="exect_v2",
        field_families=["frequency"],
        clinical_operation="candidate_generation",
        knowledge_sources=["regex_rules", "temporal_rules", "benchmark_label_policy"],
        hybrid_balance_class=[
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        interleaving_positions=["pre"],
        control_modes=["soft_hint"],
        input_contract="ExECT note text with quantified rates, qualitative change cues, or filtered Gan temporal hints.",
        output_contract=(
            "Note-anchored seizure-frequency candidates with benchmark-facing "
            "templates, source spans, and Gan-filter caveats."
        ),
        compatible_experiment_arms=["H2", "H4"],
        status="implemented",
        caveats=[
            "Do not reuse Gan monthly normalization or unknown/no-reference label policy.",
            "Cap-25 H2 pre-vocab probe was rejected; keep this primitive off default S4 paths.",
            "Gan temporal hints are accepted only when they map to audited ExECT templates.",
        ],
        implementation_refs=["src/clinical_extraction/exect/primitives.py"],
    ),
    PrimitiveMetadata(
        primitive_id="exect.frequency.benchmark_bridge.v1",
        name="ExECT seizure-frequency benchmark bridge",
        dataset="exect_v2",
        field_families=["frequency"],
        clinical_operation="benchmark_bridge",
        knowledge_sources=["benchmark_label_policy", "gold_audit_policy"],
        hybrid_balance_class=["H1_post_deterministic"],
        interleaving_positions=["post"],
        control_modes=["posthoc_correction"],
        input_contract="Raw seizure-frequency prediction surfaces plus note text for co-label augmentation.",
        output_contract=(
            "Benchmark-facing frequency templates with near-miss repair, "
            "seizure-type stripping, non-audited period blocking, and multi-label co-label flags."
        ),
        compatible_experiment_arms=["H1"],
        status="implemented",
        caveats=[
            "ExECT abstention uses empty lists, not Gan no seizure frequency reference.",
            "Seizure-free prose may collapse to seizure free while gold may use zero-rate templates.",
            "Co-label augmentation requires explicit note cues; it does not invent qualitative changes.",
        ],
        implementation_refs=[
            "src/clinical_extraction/exect/primitives.py",
            "src/clinical_extraction/programs/exect_s4.py",
        ],
    ),
    PrimitiveMetadata(
        primitive_id="gan.frequency.label_policy_bridge.v1",
        name="Gan frequency label-policy bridge",
        dataset="gan_2026",
        field_families=["frequency"],
        clinical_operation="benchmark_bridge",
        knowledge_sources=["benchmark_label_policy", "gold_audit_policy"],
        hybrid_balance_class=["H1_post_deterministic", "D1_deterministic_only"],
        interleaving_positions=["post", "eval_only"],
        control_modes=["posthoc_correction", "diagnostic_only"],
        input_contract="Raw Gan frequency label string from gold or prediction.",
        output_contract=(
            "Raw, canonical, benchmark-facing, monthly-frequency, Purist, and "
            "Pragmatic label-policy values."
        ),
        compatible_experiment_arms=["H1", "D1"],
        status="implemented",
        caveats=[
            "Gan seizure_frequency_number[0] remains the benchmark-facing gold label.",
            "Unknown and no seizure frequency reference are separate label-policy classes.",
            "Default helper use is scorer-only unless a caller explicitly makes it prediction-affecting.",
        ],
        implementation_refs=[
            "src/clinical_extraction/gan/primitives.py",
            "src/clinical_extraction/gan/frequency.py",
        ],
    ),
    PrimitiveMetadata(
        primitive_id="shared.evidence.substring_support.v1",
        name="Deterministic substring evidence support",
        dataset="shared",
        field_families=["multi_family"],
        clinical_operation="evidence_support",
        knowledge_sources=["regex_rules", "diagnostic_metric"],
        hybrid_balance_class=["D1_deterministic_only"],
        interleaving_positions=["eval_only"],
        control_modes=["diagnostic_only"],
        input_contract="Note text plus model quote or deterministic evidence candidate.",
        output_contract=(
            "Supported, unsupported, no-reference, or normalized-interpretation support result."
        ),
        compatible_experiment_arms=["D1"],
        status="implemented",
        implementation_refs=["src/clinical_extraction/primitives.py"],
    ),
    PrimitiveMetadata(
        primitive_id="shared.fixtures.primitive_cases.v1",
        name="Primitive fixture case library",
        dataset="shared",
        field_families=["multi_family"],
        clinical_operation="fixture_definition",
        knowledge_sources=["manual_examples", "gold_audit_policy"],
        hybrid_balance_class=["D1_deterministic_only"],
        interleaving_positions=["eval_only"],
        control_modes=["diagnostic_only"],
        input_contract="Fixture case inputs keyed by primitive_id and failure mode.",
        output_contract=(
            "Deterministic primitive outputs validated against expected fields "
            "without model calls."
        ),
        compatible_experiment_arms=["D1"],
        status="implemented",
        caveats=[
            "Fixture cases are curated examples, not a substitute for dataset-wide audits.",
            "Cases should cover positive, negative, ambiguous, absent, historical, planned, and unsupported-evidence modes.",
        ],
        implementation_refs=[
            "data/fixtures/primitive_cases.json",
            "src/clinical_extraction/fixtures/primitive_cases.py",
        ],
    ),
    PrimitiveMetadata(
        primitive_id="gan.frequency.evidence_guard.v1",
        name="Gan frequency evidence guard",
        dataset="gan_2026",
        field_families=["frequency"],
        clinical_operation="evidence_support",
        knowledge_sources=["regex_rules", "gold_audit_policy", "diagnostic_metric"],
        hybrid_balance_class=["H1_post_deterministic", "D1_deterministic_only"],
        interleaving_positions=["post", "eval_only"],
        control_modes=["posthoc_correction", "diagnostic_only"],
        input_contract="Gan note text, frequency label, and model or gold evidence text.",
        output_contract=(
            "Exact, elided multi-span, unsupported, or no-reference evidence support "
            "with Gan label-policy caveats."
        ),
        compatible_experiment_arms=["H1", "D1"],
        status="implemented",
        caveats=[
            "Elided Gan gold evidence can be supported by ordered fragments without being one exact quote.",
            "Evidence support remains diagnostic unless a decision document makes it prediction-affecting.",
            "Unknown still implies frequency context; no-reference means no seizure frequency reference.",
        ],
        implementation_refs=[
            "src/clinical_extraction/gan/primitives.py",
            "src/clinical_extraction/gan/react_tools.py",
        ],
    ),
)


def _load_planned_exect_family_primitives() -> tuple[PrimitiveMetadata, ...]:
    from clinical_extraction.deferred_primitives import DEFERRED_CATALOG_PRIMITIVES
    from clinical_extraction.exect.family_backlog import PLANNED_EXECT_FAMILY_PRIMITIVES

    return (*PLANNED_EXECT_FAMILY_PRIMITIVES, *DEFERRED_CATALOG_PRIMITIVES)


PRIMITIVE_REGISTRY = (
    PRIMITIVE_REGISTRY + _load_planned_exect_family_primitives()
)


def primitive_registry_by_id() -> dict[str, PrimitiveMetadata]:
    return {primitive.primitive_id: primitive for primitive in PRIMITIVE_REGISTRY}
