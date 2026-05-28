"""ExECT medication taxonomy primitive and bridge helpers."""

from __future__ import annotations

import re

from clinical_extraction.datasets.exect import (
    canonical_clinical_phrase,
    canonical_medication_name,
    format_medication_temporality_label,
    infer_prescription_temporality,
)
from clinical_extraction.primitives import NormalizationResult, PrimitiveCandidate

EXECT_MEDICATION_RX_CANDIDATE_PRIMITIVE_ID = "exect.medication.rx_candidates.v1"
EXECT_MEDICATION_BENCHMARK_BRIDGE_PRIMITIVE_ID = (
    "exect.medication.benchmark_bridge.v1"
)
EXECT_MEDICATION_TEMPORALITY_PRIMITIVE_ID = (
    "exect.medication_temporality.post_classifier.v1"
)
EXECT_MEDICATION_TEMPORALITY_NON_ASM_GUARD_PRIMITIVE_ID = (
    "exect.medication_temporality.non_asm_guard.v1"
)
EXECT_MEDICATION_TEMPORALITY_NON_ASM_DOSE_CURRENT_GUARD_PRIMITIVE_ID = (
    "exect.medication_temporality.non_asm_dose_current_guard.v1"
)
EXECT_ANNOTATED_MEDICATION_NON_ASM_BRAND_ALIAS_GUARD_PRIMITIVE_ID = (
    "exect.medication.am_guard_non_asm_brand_alias.v1"
)
EXECT_ANNOTATED_MEDICATION_TEMPORAL_EVIDENCE_GUARD_PRIMITIVE_ID = (
    "exect.medication.am_guard_temporal_evidence.v1"
)
_ASM_CANONICAL_MEDICATIONS = frozenset(
    {
        "brivaracetam",
        "carbamazepine",
        "clobazam",
        "eslicarbazepine",
        "gabapentin",
        "lacosamide",
        "lamotrigine",
        "levetiracetam",
        "oxcarbazepine",
        "phenobarbital",
        "phenytoin",
        "pregabalin",
        "sodium valproate",
        "topiramate",
        "vigabatrin",
        "zonisamide",
    }
)

_SURFACE_REPAIRS = {
    "brivitiracetam": "brivaracetam",
    "eslicarbazine": "eslicarbazepine",
    "zonismaide": "zonisamide",
    "eplim": "epilim chrono",
    "eplim chrono": "epilim chrono",
}

_BRAND_SURFACES = {
    "epilim chrono": "sodium valproate",
    "epilim": "sodium valproate",
    "lamictal": "lamotrigine",
    "keppra": "levetiracetam",
}

_NON_ASM_MEDICATIONS = frozenset(
    {
        "amitriptyline",
        "citalopram",
        "diazepam",
        "fluoxetine",
        "sertraline",
    }
)

_MEDICATION_SURFACES = tuple(
    sorted(
        {
            *_ASM_CANONICAL_MEDICATIONS,
            *_SURFACE_REPAIRS,
            *_SURFACE_REPAIRS.values(),
            *_BRAND_SURFACES,
            *_NON_ASM_MEDICATIONS,
        },
        key=len,
        reverse=True,
    )
)

_CURRENT_MARKERS = (
    "current medication",
    "current medications",
    "current anti-epileptic medication",
    "current anti epileptic medication",
    "currently taking",
    "currently she is taking",
    "currently he is taking",
    "continue to take",
    "does continue to take",
    "continues to take",
    "now taking",
    "is now taking",
)

_PLANNED_MARKERS = (
    "to start",
    "please start",
    "plan to start",
    "will start",
    "recommend starting",
    "grateful if you could prescribe",
    "could prescribe",
    "to change to",
)

_PREVIOUS_MARKERS = (
    "previously",
    "prior ",
    "tried ",
    "had been on",
    "had been taking",
    "stopped completely",
    "decided to stop",
    "stopped ",
)

_TAPER_OR_STOP_MARKERS = (
    "reduce and stop",
    "reduce the",
    "weaned",
    "taper",
    "stop over",
    "every week until",
)

_DOSE_LINE_RE = re.compile(
    r"\b(?:\d+(?:\.\d+)?\s*)?"
    r"(?:mg|mgs|milligram|milligrams|milligrammes|mcg|micrograms)\b"
    r"|"
    r"\b(?:bd|od|tds|qds|nocte|twice a day|once a day|daily|morning|evening)\b",
    re.IGNORECASE,
)

def build_exect_medication_candidate_payloads(note_text: str) -> list[PrimitiveCandidate]:
    """Return note-anchored medication candidates using the shared payload contract.

    These are soft hints for narrow medication experiments. Planned and previous
    medications are surfaced for inspection but are not S1 benchmark-facing
    current prescription outputs.
    """

    candidates: list[PrimitiveCandidate] = []
    seen: set[tuple[str, int]] = set()
    for surface in _MEDICATION_SURFACES:
        for match in re.finditer(rf"\b{re.escape(surface)}\b", note_text, re.IGNORECASE):
            raw_text = note_text[match.start() : match.end()]
            key = (raw_text.lower(), match.start())
            if key in seen:
                continue
            seen.add(key)

            context = _local_context(note_text, match.start(), match.end())
            bridge = exect_medication_benchmark_bridge(
                raw_text,
                note_text=note_text,
                evidence_text=context,
            )
            temporality = infer_exect_medication_temporality(context)
            caveats = _candidate_caveats(bridge=bridge, temporality=temporality)

            candidates.append(
                PrimitiveCandidate(
                    primitive_id=EXECT_MEDICATION_RX_CANDIDATE_PRIMITIVE_ID,
                    dataset="exect_v2",
                    field_family="medication",
                    raw_text=raw_text,
                    normalized_value=bridge.canonical_value,
                    benchmark_value=(
                        bridge.benchmark_value
                        if temporality.canonical_value == "current"
                        else None
                    ),
                    source_span_text=raw_text,
                    start=match.start(),
                    end=match.end(),
                    rule_name="exect_note_anchored_medication_surface",
                    confidence=1.0,
                    caveats=caveats,
                    metadata={
                        "temporality": temporality.canonical_value,
                        "benchmark_s1_included": (
                            temporality.canonical_value == "current"
                            and bridge.benchmark_value is not None
                        ),
                        "canonical_medication": bridge.canonical_value,
                        "benchmark_surface_policy": bridge.metadata.get(
                            "benchmark_surface_policy"
                        ),
                        "context": context,
                    },
                )
            )

    return sorted(candidates, key=lambda item: (item.start or 0, str(item.raw_text)))


def exect_medication_benchmark_bridge(
    raw_value: str,
    *,
    note_text: str = "",
    evidence_text: str | None = None,
    prediction_affecting: bool = True,
) -> NormalizationResult:
    """Normalize an ExECT medication surface while preserving benchmark policy."""

    repaired = _SURFACE_REPAIRS.get(raw_value.strip().lower())
    source_value = repaired or raw_value
    canonical = canonical_medication_name(source_value)
    canonical = _BRAND_SURFACES.get(canonical, canonical)
    benchmark_value = _brand_surface_from_text(
        canonical=canonical,
        note_text=note_text,
        evidence_text=evidence_text,
    )
    if benchmark_value is None and canonical in _ASM_CANONICAL_MEDICATIONS:
        benchmark_value = canonical

    metadata: dict[str, object] = {
        "is_asm": canonical in _ASM_CANONICAL_MEDICATIONS,
        "surface_repaired": repaired is not None,
        "benchmark_surface_policy": (
            "brand_surface_preserved"
            if benchmark_value is not None and benchmark_value != canonical
            else "canonical_generic"
        ),
    }
    caveat = None
    if canonical in _NON_ASM_MEDICATIONS or canonical not in _ASM_CANONICAL_MEDICATIONS:
        benchmark_value = None
        metadata["is_asm"] = False
        metadata["rejected_reason"] = "non_asm_medication"
        caveat = "Non-ASM medications are rejected from ExECT annotated medication output."
    elif repaired is not None:
        caveat = "Medication surface spelling was repaired before benchmark alignment."

    return NormalizationResult(
        primitive_id=EXECT_MEDICATION_BENCHMARK_BRIDGE_PRIMITIVE_ID,
        dataset="exect_v2",
        field_family="medication",
        raw_value=raw_value,
        canonical_value=canonical,
        benchmark_value=benchmark_value,
        clinical_caveat=caveat,
        transformation_rule="exect_medication_benchmark_surface_alignment",
        prediction_affecting=prediction_affecting,
        scorer_only=not prediction_affecting,
        metadata=metadata,
    )


def infer_exect_medication_temporality(evidence_text: str | None) -> NormalizationResult:
    """Classify prescription temporality for benchmark-facing medication policy."""

    text = (evidence_text or "").lower()
    cues: list[str] = []
    if _has_current_prescription_marker(text):
        temporality = "current"
        benchmark_value = "current_prescription"
    elif any(marker in text for marker in _PLANNED_MARKERS):
        temporality = "planned"
        benchmark_value = None
    elif any(marker in text for marker in _PREVIOUS_MARKERS):
        temporality = "previous"
        benchmark_value = None
    else:
        temporality = "unknown"
        benchmark_value = None

    if any(marker in text for marker in _TAPER_OR_STOP_MARKERS):
        cue = (
            "taper_or_stop_inside_current_prescription_line"
            if temporality == "current"
            else "taper_or_stop"
        )
        cues.append(cue)
    if temporality != "unknown":
        cues.append(f"{temporality}_cue")

    caveat = None
    if temporality in {"planned", "previous"}:
        caveat = (
            "Medication is clinically relevant but not benchmark-facing S1 current "
            "prescription output."
        )
    elif temporality == "unknown":
        caveat = "Medication temporality is not explicit enough for S1 benchmark inclusion."

    return NormalizationResult(
        primitive_id=EXECT_MEDICATION_TEMPORALITY_PRIMITIVE_ID,
        dataset="exect_v2",
        field_family="medication",
        raw_value=evidence_text,
        canonical_value=temporality,
        benchmark_value=benchmark_value,
        clinical_caveat=caveat,
        transformation_rule="exect_medication_temporality_cue_policy",
        prediction_affecting=True,
        scorer_only=False,
        metadata={
            "benchmark_s1_included": temporality == "current",
            "cues": cues,
        },
    )


_VALID_RX_TEMPORALITIES = frozenset({"current", "planned", "previous"})


def recover_exect_medication_temporality_with_post_classifier(
    raw_values: list[str],
    evidence_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Recover S4 medication-temporality labels with evidence-aligned post classification."""

    flags: list[str] = []
    recovered: list[str] = []
    seen: set[str] = set()

    for index, raw in enumerate(raw_values):
        if not raw.strip():
            continue
        evidence = (
            evidence_values[index].strip()
            if index < len(evidence_values) and evidence_values[index]
            else ""
        )
        model_status: str | None = None
        if "|" in raw:
            medication_part, status_part = raw.split("|", 1)
            medication_name = canonical_medication_name(medication_part)
            model_status = canonical_clinical_phrase(status_part)
            context = evidence or note_text
        else:
            medication_name = canonical_medication_name(raw)
            context = evidence or note_text

        if not medication_name:
            flags.append("s4_bridge:medication_temporality_unrecognized")
            continue
        if (
            medication_name in _NON_ASM_MEDICATIONS
            or medication_name not in _ASM_CANONICAL_MEDICATIONS
        ):
            flags.append("s4_bridge:medication_temporality_non_asm_removed")
            continue

        classification = infer_exect_medication_temporality(context)
        status = classification.canonical_value
        if status not in _VALID_RX_TEMPORALITIES:
            if status == "unknown":
                flags.append("s4_bridge:medication_temporality_unknown_removed")
            else:
                flags.append("s4_bridge:medication_temporality_invalid_status_removed")
            continue
        if (
            model_status in _VALID_RX_TEMPORALITIES
            and model_status != status
        ):
            flags.append("s4_bridge:medication_temporality_status_reclassified")

        label = format_medication_temporality_label(medication_name, status)
        if label in seen:
            continue
        seen.add(label)
        recovered.append(label)

    return recovered, flags


def recover_exect_medication_temporality_non_asm_guard(
    raw_values: list[str],
    evidence_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Drop non-ASM medication-temporality labels; keep model-assigned ASM status."""

    del evidence_values  # G0 does not reclassify from evidence (unlike H1 post-classifier).

    flags: list[str] = []
    recovered: list[str] = []
    seen: set[str] = set()

    for raw in raw_values:
        if not raw.strip():
            continue
        if "|" in raw:
            medication_part, status_part = raw.split("|", 1)
            medication_name = canonical_medication_name(medication_part)
            status = canonical_clinical_phrase(status_part)
            if not medication_name:
                flags.append("s4_bridge:medication_temporality_unrecognized")
                continue
            if (
                medication_name in _NON_ASM_MEDICATIONS
                or medication_name not in _ASM_CANONICAL_MEDICATIONS
            ):
                flags.append("s4_bridge:medication_temporality_non_asm_removed")
                continue
            if status not in _VALID_RX_TEMPORALITIES:
                flags.append("s4_bridge:medication_temporality_invalid_status_removed")
                continue
            label = format_medication_temporality_label(medication_name, status)
        else:
            medication_name = canonical_medication_name(raw)
            if not medication_name:
                flags.append("s4_bridge:medication_temporality_unrecognized")
                continue
            if (
                medication_name in _NON_ASM_MEDICATIONS
                or medication_name not in _ASM_CANONICAL_MEDICATIONS
            ):
                flags.append("s4_bridge:medication_temporality_non_asm_removed")
                continue
            status = infer_prescription_temporality(note_text)
            label = format_medication_temporality_label(medication_name, status)
            flags.append("s4_bridge:medication_temporality_status_inferred")

        if label in seen:
            continue
        seen.add(label)
        recovered.append(label)

    return recovered, flags


def recover_exect_medication_temporality_non_asm_dose_current_guard(
    raw_values: list[str],
    evidence_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Prune unsupported MT labels while preserving dose-only current ASM rows.

    This is narrower than the rejected broad post-classifier: it removes non-ASM
    labels, keeps explicit planned/previous evidence, and preserves model current
    status when the aligned evidence is a prescription-style dose line.
    """

    flags: list[str] = []
    recovered: list[str] = []
    seen: set[str] = set()

    for index, raw in enumerate(raw_values):
        if not raw.strip():
            continue
        if "|" not in raw:
            flags.append("s4_bridge:medication_temporality_invalid_pipe")
            continue

        medication_part, status_part = raw.split("|", 1)
        medication_name = canonical_medication_name(medication_part)
        model_status = canonical_clinical_phrase(status_part)
        if not medication_name:
            flags.append("s4_bridge:medication_temporality_unrecognized")
            continue
        if (
            medication_name in _NON_ASM_MEDICATIONS
            or medication_name not in _ASM_CANONICAL_MEDICATIONS
        ):
            flags.append("s4_bridge:medication_temporality_non_asm_removed")
            continue
        if model_status not in _VALID_RX_TEMPORALITIES:
            flags.append("s4_bridge:medication_temporality_invalid_status_removed")
            continue

        evidence = (
            evidence_values[index].strip()
            if index < len(evidence_values) and evidence_values[index]
            else ""
        )
        context = evidence or note_text
        inferred_status = infer_exect_medication_temporality(context).canonical_value

        status = model_status
        if inferred_status in _VALID_RX_TEMPORALITIES:
            if model_status in {"planned", "previous"} and inferred_status != model_status:
                flags.append(
                    "s4_bridge:medication_temporality_unsupported_planned_previous_removed"
                )
                continue
            if model_status == "current" and inferred_status != "current":
                flags.append("s4_bridge:medication_temporality_status_reclassified")
                status = inferred_status
        elif model_status == "current" and _is_prescription_dose_line(context):
            flags.append("s4_bridge:medication_temporality_dose_current_preserved")
        elif model_status in {"planned", "previous"}:
            flags.append(
                "s4_bridge:medication_temporality_unsupported_planned_previous_removed"
            )
            continue

        label = format_medication_temporality_label(medication_name, status)
        if label in seen:
            continue
        seen.add(label)
        recovered.append(label)

    return recovered, flags


def recover_exect_annotated_medication_non_asm_brand_alias_guard(
    raw_values: list[str],
    evidence_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Prune non-ASM medications, repair brand aliases, and deduplicate same-canonical.

    This is for ExECT S5 annotated_medication to address the precision deficit.
    """
    flags: list[str] = []
    recovered: list[str] = []

    # Track the best surface for each canonical medication to deduplicate
    canonical_to_surface: dict[str, str] = {}

    # First pass: analyze and select best surface for each unique canonical medication
    for index, raw in enumerate(raw_values):
        if not raw.strip():
            continue

        evidence = (
            evidence_values[index].strip()
            if index < len(evidence_values) and evidence_values[index]
            else ""
        )

        # 1. Clean the raw value
        cleaned_raw = raw.strip().lower()

        # 2. Repair "eplim" / "eplim chrono" spelling errors.
        eplim_spelling_repaired = cleaned_raw in {"eplim", "eplim chrono"}
        if eplim_spelling_repaired:
            cleaned_raw = "epilim chrono"
            flags.append("benchmark_bridge:medication_surface_repaired")

        # 3. Get canonical medication name and resolve brand surface to generic canonical
        raw_canonical = canonical_medication_name(cleaned_raw)
        canonical = _BRAND_SURFACES.get(raw_canonical, raw_canonical)

        # 4. Check if it's ASM
        if canonical in _NON_ASM_MEDICATIONS or canonical not in _ASM_CANONICAL_MEDICATIONS:
            flags.append("benchmark_bridge:non_asm_medication_rejected")
            continue

        # 5. Resolve brand/benchmark surface
        # Repair eplim spelling in note/evidence text so _brand_surface_from_text can match epilim chrono
        repaired_note = re.sub(r"eplim", "epilim", note_text, flags=re.IGNORECASE)
        repaired_evidence = re.sub(r"eplim", "epilim", evidence, flags=re.IGNORECASE)

        if raw_canonical == canonical and cleaned_raw in {canonical, "epilim"}:
            benchmark_val = (
                _brand_surface_from_text(
                    canonical=canonical,
                    note_text=repaired_note,
                    evidence_text=repaired_evidence,
                )
                if canonical == "lamotrigine"
                else canonical
            )
        else:
            benchmark_val = _brand_surface_from_text(
                canonical=canonical,
                note_text=repaired_note,
                evidence_text=repaired_evidence,
            )
            if eplim_spelling_repaired and benchmark_val == "epilim":
                benchmark_val = "epilim chrono"

        if benchmark_val is None:
            # If the prediction was already a brand name like "epilim chrono" or "lamictal",
            # preserve it if it maps to this canonical ASM.
            if cleaned_raw in {"epilim chrono", "lamictal"}:
                benchmark_val = cleaned_raw
            else:
                benchmark_val = canonical
        else:
            flags.append("benchmark_bridge:medication_brand_surface_preserved")

        # 6. Deduplicate same-canonical medications.
        # Prefer an explicit generic prediction when present; use the repaired
        # brand surface only when it is the only available same-canonical label.
        if canonical in canonical_to_surface:
            existing = canonical_to_surface[canonical]
            if existing in {"epilim chrono", "lamictal"} and benchmark_val == canonical:
                canonical_to_surface[canonical] = benchmark_val
            flags.append("benchmark_bridge:medication_deduplicated")
        else:
            canonical_to_surface[canonical] = benchmark_val

    # Second pass: preserve insertion order of unique canonicals
    seen_canonicals = set()
    for raw in raw_values:
        cleaned_raw = raw.strip().lower()
        if cleaned_raw in {"eplim", "eplim chrono", "epilim", "epilim chrono"}:
            cleaned_raw = "epilim chrono"
        canonical = canonical_medication_name(cleaned_raw)
        canonical = _BRAND_SURFACES.get(canonical, canonical)
        if canonical in canonical_to_surface and canonical not in seen_canonicals:
            seen_canonicals.add(canonical)
            recovered.append(canonical_to_surface[canonical])

    return recovered, sorted(list(set(flags)))


def recover_exect_annotated_medication_temporal_evidence_guard(
    raw_values: list[str],
    evidence_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Prune non-ASM medications, repair brand aliases, prune non-current status labels,
    and deduplicate same-canonical.

    This is for ExECT S5 annotated_medication (A4 card) to address the temporal precision deficit.
    """
    flags: list[str] = []
    recovered: list[str] = []

    # Get all candidate payloads to check for note-wide current prescription evidence
    candidates = build_exect_medication_candidate_payloads(note_text)

    # Track the best surface for each canonical medication to deduplicate
    canonical_to_surface: dict[str, str] = {}

    # First pass: analyze, verify temporality, and select best surface for each unique canonical medication
    for index, raw in enumerate(raw_values):
        if not raw.strip():
            continue

        evidence = (
            evidence_values[index].strip()
            if index < len(evidence_values) and evidence_values[index]
            else ""
        )

        # 1. Clean the raw value
        cleaned_raw = raw.strip().lower()

        # 2. Repair "eplim" / "eplim chrono" spelling errors.
        eplim_spelling_repaired = cleaned_raw in {"eplim", "eplim chrono"}
        if eplim_spelling_repaired:
            cleaned_raw = "epilim chrono"
            flags.append("benchmark_bridge:medication_surface_repaired")

        # 3. Get canonical medication name and resolve brand surface to generic canonical
        raw_canonical = canonical_medication_name(cleaned_raw)
        canonical = _BRAND_SURFACES.get(raw_canonical, raw_canonical)

        # 4. Check if it's ASM
        if canonical in _NON_ASM_MEDICATIONS or canonical not in _ASM_CANONICAL_MEDICATIONS:
            flags.append("benchmark_bridge:non_asm_medication_rejected")
            continue

        # 5. Check medication temporality (A4 temporal evidence guard)
        context = evidence or note_text
        inferred_status = infer_exect_medication_temporality(context).canonical_value
        if inferred_status not in _VALID_RX_TEMPORALITIES:
            inferred_status = "unknown"

        if inferred_status != "current":
            # Check if there is any candidate for the same canonical medication in the note that is current
            has_current_candidate = any(
                c.normalized_value == canonical and c.metadata.get("temporality") == "current"
                for c in candidates
            )
            if not has_current_candidate:
                flags.append("benchmark_bridge:medication_temporality_pruned")
                continue

        # 6. Resolve brand/benchmark surface
        # Repair eplim spelling in note/evidence text so _brand_surface_from_text can match epilim chrono
        repaired_note = re.sub(r"eplim", "epilim", note_text, flags=re.IGNORECASE)
        repaired_evidence = re.sub(r"eplim", "epilim", evidence, flags=re.IGNORECASE)

        if raw_canonical == canonical and cleaned_raw in {canonical, "epilim"}:
            benchmark_val = (
                _brand_surface_from_text(
                    canonical=canonical,
                    note_text=repaired_note,
                    evidence_text=repaired_evidence,
                )
                if canonical == "lamotrigine"
                else canonical
            )
        else:
            benchmark_val = _brand_surface_from_text(
                canonical=canonical,
                note_text=repaired_note,
                evidence_text=repaired_evidence,
            )
            if eplim_spelling_repaired and benchmark_val == "epilim":
                benchmark_val = "epilim chrono"

        if benchmark_val is None:
            # If the prediction was already a brand name like "epilim chrono" or "lamictal",
            # preserve it if it maps to this canonical ASM.
            if cleaned_raw in {"epilim chrono", "lamictal"}:
                benchmark_val = cleaned_raw
            else:
                benchmark_val = canonical
        else:
            flags.append("benchmark_bridge:medication_brand_surface_preserved")

        # 7. Deduplicate same-canonical medications.
        # Prefer an explicit generic prediction when present; use the repaired
        # brand surface only when it is the only available same-canonical label.
        if canonical in canonical_to_surface:
            existing = canonical_to_surface[canonical]
            if existing in {"epilim chrono", "lamictal"} and benchmark_val == canonical:
                canonical_to_surface[canonical] = benchmark_val
            flags.append("benchmark_bridge:medication_deduplicated")
        else:
            canonical_to_surface[canonical] = benchmark_val

    # Second pass: preserve insertion order of unique canonicals
    seen_canonicals = set()
    for raw in raw_values:
        cleaned_raw = raw.strip().lower()
        if cleaned_raw in {"eplim", "eplim chrono", "epilim", "epilim chrono"}:
            cleaned_raw = "epilim chrono"
        canonical = canonical_medication_name(cleaned_raw)
        canonical = _BRAND_SURFACES.get(canonical, canonical)
        if canonical in canonical_to_surface and canonical not in seen_canonicals:
            seen_canonicals.add(canonical)
            recovered.append(canonical_to_surface[canonical])

    return recovered, sorted(list(set(flags)))

def _candidate_caveats(
    *,
    bridge: NormalizationResult,
    temporality: NormalizationResult,
) -> list[str]:
    caveats = [
        "ExECT medication candidates are soft hints, not gold-label replacements."
    ]
    if bridge.clinical_caveat:
        caveats.append(bridge.clinical_caveat)
    if temporality.canonical_value == "planned":
        caveats.append(
            "Planned medications are not benchmark-facing S1 current prescriptions."
        )
    elif temporality.canonical_value == "previous":
        caveats.append(
            "Previous medications are not benchmark-facing S1 current prescriptions."
        )
    elif temporality.canonical_value == "unknown":
        caveats.append(
            "Unknown medication temporality is diagnostic until a task policy includes it."
        )
    return caveats

def _brand_surface_from_text(
    *,
    canonical: str,
    note_text: str,
    evidence_text: str | None,
) -> str | None:
    search_text = " ".join(
        part.lower() for part in (note_text, evidence_text or "") if part
    )
    for brand_surface, brand_canonical in _BRAND_SURFACES.items():
        if brand_canonical == canonical and brand_surface in search_text:
            return brand_surface
    return None


def _local_context(note_text: str, start: int, end: int) -> str:
    line_start = note_text.rfind("\n", 0, start) + 1
    line_end = note_text.find("\n", end)
    if line_end == -1:
        line_end = len(note_text)
    previous_sentence = note_text.rfind(". ", 0, start)
    sentence_start = max(
        line_start,
        previous_sentence + 2 if previous_sentence != -1 else line_start,
    )
    sentence_end = note_text.find(". ", end)
    if sentence_end == -1:
        sentence_end = line_end
    else:
        sentence_end = min(sentence_end + 1, line_end)
    return note_text[sentence_start:sentence_end].strip()


def _has_current_prescription_marker(text: str) -> bool:
    return any(marker in text for marker in _CURRENT_MARKERS) or bool(
        re.search(r"^medications?\s*[:\s-]", text)
    )


def _is_prescription_dose_line(text: str) -> bool:
    return bool(_DOSE_LINE_RE.search(text or ""))

__all__ = [
    "EXECT_ANNOTATED_MEDICATION_NON_ASM_BRAND_ALIAS_GUARD_PRIMITIVE_ID",
    "EXECT_ANNOTATED_MEDICATION_TEMPORAL_EVIDENCE_GUARD_PRIMITIVE_ID",
    "EXECT_MEDICATION_BENCHMARK_BRIDGE_PRIMITIVE_ID",
    "EXECT_MEDICATION_RX_CANDIDATE_PRIMITIVE_ID",
    "EXECT_MEDICATION_TEMPORALITY_NON_ASM_DOSE_CURRENT_GUARD_PRIMITIVE_ID",
    "EXECT_MEDICATION_TEMPORALITY_NON_ASM_GUARD_PRIMITIVE_ID",
    "EXECT_MEDICATION_TEMPORALITY_PRIMITIVE_ID",
    "build_exect_medication_candidate_payloads",
    "exect_medication_benchmark_bridge",
    "infer_exect_medication_temporality",
    "recover_exect_annotated_medication_non_asm_brand_alias_guard",
    "recover_exect_annotated_medication_temporal_evidence_guard",
    "recover_exect_medication_temporality_non_asm_dose_current_guard",
    "recover_exect_medication_temporality_non_asm_guard",
    "recover_exect_medication_temporality_with_post_classifier",
]
