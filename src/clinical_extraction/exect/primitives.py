"""Backward-compatible ExECT primitive imports.

Family-owned implementations live in the diagnosis, seizure-type, medication,
and frequency primitive modules. Keep this module as the legacy import surface
for experiment configs and replay artifacts.
"""

from __future__ import annotations

from clinical_extraction.datasets.exect import (
    canonical_clinical_phrase,
    canonical_medication_name,
    collapse_diagnoses_to_most_specific,
    format_medication_temporality_label,
    infer_prescription_temporality,
)
from clinical_extraction.exect.diagnosis_primitives import (
    EXECT_DIAGNOSIS_BENCHMARK_BRIDGE_PRIMITIVE_ID,
    exect_diagnosis_annotation_policy,
    exect_diagnosis_benchmark_bridge,
)
from clinical_extraction.exect.frequency_primitives import (
    EXECT_FREQUENCY_BENCHMARK_BRIDGE_PRIMITIVE_ID,
    EXECT_FREQUENCY_RATE_CANDIDATE_PRIMITIVE_ID,
    build_exect_frequency_candidate_payloads,
    build_exect_frequency_pre_vocab_labels,
    build_exect_frequency_pre_vocab_labels_high_precision,
    exect_frequency_benchmark_bridge,
    filter_gan_temporal_candidate_for_exect,
    format_exect_frequency_pre_vocab_note,
    format_exect_frequency_pre_vocab_note_high_precision,
    note_has_exect_frequency_support,
    recover_exect_frequency_benchmark_values,
    recover_exect_frequency_benchmark_values_with_multi_label_retention,
    recover_exect_frequency_benchmark_values_with_post_merge,
    repair_exect_frequency_surface,
)
from clinical_extraction.exect.medication_primitives import (
    EXECT_ANNOTATED_MEDICATION_NON_ASM_BRAND_ALIAS_GUARD_PRIMITIVE_ID,
    EXECT_ANNOTATED_MEDICATION_TEMPORAL_EVIDENCE_GUARD_PRIMITIVE_ID,
    EXECT_MEDICATION_BENCHMARK_BRIDGE_PRIMITIVE_ID,
    EXECT_MEDICATION_RX_CANDIDATE_PRIMITIVE_ID,
    EXECT_MEDICATION_TEMPORALITY_NON_ASM_DOSE_CURRENT_GUARD_PRIMITIVE_ID,
    EXECT_MEDICATION_TEMPORALITY_NON_ASM_GUARD_PRIMITIVE_ID,
    EXECT_MEDICATION_TEMPORALITY_PRIMITIVE_ID,
    _BRAND_SURFACES,
    build_exect_medication_candidate_payloads,
    exect_medication_benchmark_bridge,
    infer_exect_medication_temporality,
    recover_exect_annotated_medication_non_asm_brand_alias_guard,
    recover_exect_annotated_medication_temporal_evidence_guard,
    recover_exect_medication_temporality_non_asm_dose_current_guard,
    recover_exect_medication_temporality_non_asm_guard,
    recover_exect_medication_temporality_with_post_classifier,
)
from clinical_extraction.exect.seizure_type_primitives import (
    EXECT_SEIZURE_TYPE_BENCHMARK_BRIDGE_PRIMITIVE_ID,
    exect_seizure_type_benchmark_bridge,
)
from clinical_extraction.primitives import NormalizationResult, PrimitiveCandidate

__all__ = [
    "EXECT_ANNOTATED_MEDICATION_NON_ASM_BRAND_ALIAS_GUARD_PRIMITIVE_ID",
    "EXECT_ANNOTATED_MEDICATION_TEMPORAL_EVIDENCE_GUARD_PRIMITIVE_ID",
    "EXECT_DIAGNOSIS_BENCHMARK_BRIDGE_PRIMITIVE_ID",
    "EXECT_FREQUENCY_BENCHMARK_BRIDGE_PRIMITIVE_ID",
    "EXECT_FREQUENCY_RATE_CANDIDATE_PRIMITIVE_ID",
    "EXECT_MEDICATION_BENCHMARK_BRIDGE_PRIMITIVE_ID",
    "EXECT_MEDICATION_RX_CANDIDATE_PRIMITIVE_ID",
    "EXECT_MEDICATION_TEMPORALITY_NON_ASM_DOSE_CURRENT_GUARD_PRIMITIVE_ID",
    "EXECT_MEDICATION_TEMPORALITY_NON_ASM_GUARD_PRIMITIVE_ID",
    "EXECT_MEDICATION_TEMPORALITY_PRIMITIVE_ID",
    "EXECT_SEIZURE_TYPE_BENCHMARK_BRIDGE_PRIMITIVE_ID",
    "NormalizationResult",
    "PrimitiveCandidate",
    "_BRAND_SURFACES",
    "build_exect_frequency_candidate_payloads",
    "build_exect_frequency_pre_vocab_labels",
    "build_exect_frequency_pre_vocab_labels_high_precision",
    "build_exect_medication_candidate_payloads",
    "canonical_clinical_phrase",
    "canonical_medication_name",
    "collapse_diagnoses_to_most_specific",
    "exect_diagnosis_annotation_policy",
    "exect_diagnosis_benchmark_bridge",
    "exect_frequency_benchmark_bridge",
    "exect_medication_benchmark_bridge",
    "exect_seizure_type_benchmark_bridge",
    "filter_gan_temporal_candidate_for_exect",
    "format_exect_frequency_pre_vocab_note",
    "format_exect_frequency_pre_vocab_note_high_precision",
    "format_medication_temporality_label",
    "infer_exect_medication_temporality",
    "infer_prescription_temporality",
    "note_has_exect_frequency_support",
    "recover_exect_annotated_medication_non_asm_brand_alias_guard",
    "recover_exect_annotated_medication_temporal_evidence_guard",
    "recover_exect_frequency_benchmark_values",
    "recover_exect_frequency_benchmark_values_with_multi_label_retention",
    "recover_exect_frequency_benchmark_values_with_post_merge",
    "recover_exect_medication_temporality_non_asm_dose_current_guard",
    "recover_exect_medication_temporality_non_asm_guard",
    "recover_exect_medication_temporality_with_post_classifier",
    "repair_exect_frequency_surface",
]
