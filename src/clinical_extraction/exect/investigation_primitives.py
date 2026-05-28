"""ExECT investigation bridge helpers."""

from __future__ import annotations

from clinical_extraction.datasets.exect import normalize_investigation_phrase

_INVESTIGATION_MODALITIES = ("eeg", "mri", "ct")
_PLANNED_INVESTIGATION_MARKERS = (
    "will arrange",
    "will request",
    "requesting",
    "due to have",
    "plan to",
    "arrange an",
    "arrange a",
    "which i will request",
)


def recover_exect_s4_investigation_benchmark_values(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Recover S4 investigation labels while blocking planned-scan unknowns."""

    flags: list[str] = []
    recovered: list[str] = []
    seen: set[str] = set()

    for raw in raw_values:
        if not raw.strip():
            continue
        canonical = normalize_investigation_phrase(raw)
        if not canonical.endswith(" unknown"):
            if canonical in seen:
                continue
            seen.add(canonical)
            recovered.append(canonical)
            continue

        modality = canonical.split()[0]
        if modality not in _INVESTIGATION_MODALITIES:
            flags.append("s4_bridge:investigation_unknown_removed")
            continue
        if note_supports_exect_s4_investigation_unknown(modality, note_text):
            if canonical in seen:
                continue
            seen.add(canonical)
            recovered.append(canonical)
            continue
        if note_has_planned_exect_s4_investigation(modality, note_text):
            flags.append("s4_bridge:investigation_unknown_removed")
            continue
        flags.append("s4_bridge:investigation_unknown_removed")

    return recovered, flags


def note_supports_exect_s4_investigation_unknown(
    modality: str,
    note_text: str,
) -> bool:
    note = note_text.lower()
    if f"{modality} unknown" in note or f"{modality} result unknown" in note:
        return True
    if "unknown" in note and modality in note:
        return True
    if modality == "eeg" and any(
        marker in note
        for marker in (
            "do not have the results of",
            "don't have the results of",
            "results of his recent eeg",
            "results of her recent eeg",
            "results of the recent eeg",
            "results of recent eeg",
        )
    ):
        return True
    if modality == "mri" and any(
        marker in note
        for marker in (
            "do not have the results of",
            "don't have the results of",
            "results of his recent mri",
            "results of her recent mri",
            "results of the recent mri",
            "results of recent mri",
        )
    ):
        return True
    return False


def note_has_planned_exect_s4_investigation(modality: str, note_text: str) -> bool:
    note = note_text.lower()
    if modality not in note:
        return False
    return any(marker in note for marker in _PLANNED_INVESTIGATION_MARKERS)


__all__ = [
    "note_has_planned_exect_s4_investigation",
    "note_supports_exect_s4_investigation_unknown",
    "recover_exect_s4_investigation_benchmark_values",
]
