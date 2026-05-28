"""ExECT residual-slice replay helpers (deterministic bridge re-score on fixed doc queues)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.datasets.exect import load_exect_gold_document
from clinical_extraction.evaluation.exect import (
    S2_FIELD_FAMILIES,
    _gold_values_by_family,
    _score_field_family,
)
from clinical_extraction.datasets.exect import canonical_epilepsy_cause_label
from clinical_extraction.programs.exect_s2 import (
    EXECT_S2_COMORBIDITY_C0_C1_VARIANT,
    EXECT_S2_COMORBIDITY_C0_VARIANT,
    EXECT_S2_VARIANT,
    _augment_s2_comorbidity_from_note,
    _recover_s2_comorbidity_raw_values,
    _s2_bridge_tiers,
    _s2_values_for_family,
    canonical_comorbidity_label,
)
from clinical_extraction.programs.exect_s3 import (
    EXECT_S3_CAUSE_BRIDGE_K0_K1_VARIANT,
    EXECT_S3_VARIANT,
    _recover_s3_epilepsy_cause_raw_values,
    _s3_bridge_tiers,
)
from clinical_extraction.paths import resolve_run_directory
from clinical_extraction.schemas import DocumentPrediction, PredictionSet

DEFAULT_COMORBIDITY_SLICE_FIXTURE = Path(
    "data/fixtures/exect_s2_comorbidity_residual_slice.json"
)
DEFAULT_CAUSE_SLICE_FIXTURE = Path(
    "data/fixtures/exect_s3_epilepsy_cause_residual_slice.json"
)

COMORBIDITY_SLICE_ARMS: tuple[tuple[str, str], ...] = (
    ("L1", EXECT_S2_VARIANT),
    ("C0", EXECT_S2_COMORBIDITY_C0_VARIANT),
    ("C0+C1", EXECT_S2_COMORBIDITY_C0_C1_VARIANT),
)

CAUSE_SLICE_ARMS: tuple[tuple[str, str], ...] = (
    ("L1", EXECT_S3_VARIANT),
    ("K0+K1", EXECT_S3_CAUSE_BRIDGE_K0_K1_VARIANT),
)


def load_residual_slice_record_ids(fixture_path: Path) -> list[str]:
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    return [row["record_id"] for row in payload["records"]]


def load_prediction_set(run_dir: Path) -> PredictionSet:
    resolved_run_dir = resolve_run_directory(
        run_dir,
        allow_prefix_match=True,
        include_archive=True,
    )
    predictions_path = resolved_run_dir / "predictions.json"
    if not predictions_path.is_file():
        raise FileNotFoundError(f"Missing predictions.json under {run_dir}")
    return PredictionSet.model_validate_json(predictions_path.read_text(encoding="utf-8"))


def _comorbidity_raw_from_prediction(prediction: DocumentPrediction) -> tuple[list[str], list[str]]:
    raw_values: list[str] = []
    evidence_values: list[str] = []
    for value in prediction.values:
        if value.field_name != "comorbidity":
            continue
        raw_values.append(value.raw_value)
        if value.evidence:
            evidence_values.append(value.evidence[0].text)
        else:
            evidence_values.append("")
    return raw_values, evidence_values


def _comorbidity_prediction_for_arm(
    *,
    record_id: str,
    raw_values: list[str],
    evidence_values: list[str],
    program_variant: str,
) -> DocumentPrediction:
    record = load_exect_gold_document(record_id)
    tiers = _s2_bridge_tiers(program_variant)
    recovered, _ = _recover_s2_comorbidity_raw_values(
        raw_values,
        record.text,
        bridge_tiers=tiers,
    )
    recovered, _ = _augment_s2_comorbidity_from_note(recovered, record.text)
    values = _s2_values_for_family(
        record=record,
        field_name="comorbidity",
        raw_values=recovered,
        evidence_values=evidence_values,
        normalize=canonical_comorbidity_label,
    )
    return DocumentPrediction(
        document_id=record_id,
        dataset="exect_v2",
        schema_level="exect_s2_field_family",
        values=values,
        quality_flags=[],
        metadata={"program_variant": program_variant, "residual_slice_replay": True},
    )


def _aggregate_comorbidity_f1(
    *,
    record_ids: list[str],
    predictions_by_id: dict[str, DocumentPrediction],
) -> dict[str, Any]:
    per_doc: list[dict[str, Any]] = []
    tp = fp = fn = 0

    for record_id in record_ids:
        gold = load_exect_gold_document(record_id)
        gold_values = _gold_values_by_family(gold, field_families=S2_FIELD_FAMILIES)[
            "comorbidity"
        ]
        pred = predictions_by_id[record_id]
        predicted_values = [
            value.normalized_value
            for value in pred.values
            if value.field_name == "comorbidity" and value.normalized_value
        ]
        score = _score_field_family(
            field_family="comorbidity",
            gold_values=gold_values,
            predicted_values=predicted_values,
        )
        tp += len(score.true_positives)
        fp += len(score.false_positives)
        fn += len(score.false_negatives)
        per_doc.append(
            {
                "record_id": record_id,
                "gold": gold_values,
                "predicted": predicted_values,
                "true_positives": score.true_positives,
                "false_positives": score.false_positives,
                "false_negatives": score.false_negatives,
                "f1": score.f1,
            }
        )

    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {
        "comorbidity_f1": f1,
        "comorbidity_precision": precision,
        "comorbidity_recall": recall,
        "per_document": per_doc,
    }


def replay_comorbidity_bridge_slice(
    *,
    reference_run_dir: Path,
    record_ids: list[str],
) -> dict[str, Any]:
    """Re-score comorbidity on a fixed doc queue with L1/C0/C0+C1 bridge tiers.

    Uses raw comorbidity labels from ``reference_run_dir`` predictions (typically
    full-validation S2) and applies deterministic post-module bridges only.
    """
    reference = load_prediction_set(reference_run_dir)
    predictions_by_id = {pred.document_id: pred for pred in reference.predictions}

    arm_results: dict[str, Any] = {}
    for arm_id, program_variant in COMORBIDITY_SLICE_ARMS:
        replayed: dict[str, DocumentPrediction] = {}
        for record_id in record_ids:
            base = predictions_by_id[record_id]
            raw_values, evidence_values = _comorbidity_raw_from_prediction(base)
            replayed[record_id] = _comorbidity_prediction_for_arm(
                record_id=record_id,
                raw_values=raw_values,
                evidence_values=evidence_values,
                program_variant=program_variant,
            )
        arm_results[arm_id] = {
            "program_variant": program_variant,
            "bridge_tiers": sorted(_s2_bridge_tiers(program_variant)),
            **_aggregate_comorbidity_f1(
                record_ids=record_ids,
                predictions_by_id=replayed,
            ),
        }

    l1_docs = {row["record_id"]: row for row in arm_results["L1"]["per_document"]}
    label_fixes = 0
    label_regressions = 0
    for arm_id in ("C0", "C0+C1"):
        for row in arm_results[arm_id]["per_document"]:
            l1_row = l1_docs[row["record_id"]]
            if row["predicted"] != l1_row["predicted"]:
                if row["f1"] > l1_row["f1"]:
                    label_fixes += 1
                elif row["f1"] < l1_row["f1"]:
                    label_regressions += 1

    return {
        "reference_run_id": reference_run_dir.name,
        "record_ids": record_ids,
        "arms": arm_results,
        "headline": {
            "l1_comorbidity_f1": arm_results["L1"]["comorbidity_f1"],
            "c0_comorbidity_f1": arm_results["C0"]["comorbidity_f1"],
            "c0_c1_comorbidity_f1": arm_results["C0+C1"]["comorbidity_f1"],
            "c0_vs_l1_f1_delta": arm_results["C0"]["comorbidity_f1"]
            - arm_results["L1"]["comorbidity_f1"],
            "c0_c1_vs_l1_f1_delta": arm_results["C0+C1"]["comorbidity_f1"]
            - arm_results["L1"]["comorbidity_f1"],
            "label_fixes_vs_l1": label_fixes,
            "label_regressions_vs_l1": label_regressions,
        },
    }


def _epilepsy_cause_raw_from_prediction(
    prediction: DocumentPrediction,
) -> tuple[list[str], list[str]]:
    raw_values: list[str] = []
    evidence_values: list[str] = []
    for value in prediction.values:
        if value.field_name != "epilepsy_cause":
            continue
        raw_values.append(value.raw_value)
        if value.evidence:
            evidence_values.append(value.evidence[0].text)
        else:
            evidence_values.append("")
    return raw_values, evidence_values


def _epilepsy_cause_prediction_for_arm(
    *,
    record_id: str,
    raw_values: list[str],
    evidence_values: list[str],
    program_variant: str,
) -> DocumentPrediction:
    record = load_exect_gold_document(record_id)
    tiers = _s3_bridge_tiers(program_variant)
    recovered, _ = _recover_s3_epilepsy_cause_raw_values(
        raw_values,
        record.text,
        bridge_tiers=tiers,
    )
    values = _s2_values_for_family(
        record=record,
        field_name="epilepsy_cause",
        raw_values=recovered,
        evidence_values=evidence_values,
        normalize=canonical_epilepsy_cause_label,
    )
    return DocumentPrediction(
        document_id=record_id,
        dataset="exect_v2",
        schema_level="exect_s3_field_family",
        values=values,
        quality_flags=[],
        metadata={"program_variant": program_variant, "residual_slice_replay": True},
    )


def _aggregate_epilepsy_cause_f1(
    *,
    record_ids: list[str],
    predictions_by_id: dict[str, DocumentPrediction],
) -> dict[str, Any]:
    per_doc: list[dict[str, Any]] = []
    tp = fp = fn = 0

    for record_id in record_ids:
        gold = load_exect_gold_document(record_id)
        gold_values = gold.epilepsy_causes
        pred = predictions_by_id[record_id]
        predicted_values = [
            value.normalized_value
            for value in pred.values
            if value.field_name == "epilepsy_cause" and value.normalized_value
        ]
        score = _score_field_family(
            field_family="epilepsy_cause",
            gold_values=gold_values,
            predicted_values=predicted_values,
        )
        tp += len(score.true_positives)
        fp += len(score.false_positives)
        fn += len(score.false_negatives)
        per_doc.append(
            {
                "record_id": record_id,
                "gold": gold_values,
                "predicted": predicted_values,
                "true_positives": score.true_positives,
                "false_positives": score.false_positives,
                "false_negatives": score.false_negatives,
                "f1": score.f1,
            }
        )

    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {
        "epilepsy_cause_f1": f1,
        "epilepsy_cause_precision": precision,
        "epilepsy_cause_recall": recall,
        "per_document": per_doc,
    }


def replay_epilepsy_cause_bridge_slice(
    *,
    reference_run_dir: Path,
    record_ids: list[str],
) -> dict[str, Any]:
    """Re-score epilepsy_cause on a fixed doc queue with L1 vs K0+K1 bridge tiers.

    Uses raw epilepsy_cause labels from ``reference_run_dir`` predictions (typically
    full-validation S3) and applies deterministic post-module bridges only.
    """
    reference = load_prediction_set(reference_run_dir)
    predictions_by_id = {pred.document_id: pred for pred in reference.predictions}

    arm_results: dict[str, Any] = {}
    for arm_id, program_variant in CAUSE_SLICE_ARMS:
        replayed: dict[str, DocumentPrediction] = {}
        for record_id in record_ids:
            base = predictions_by_id[record_id]
            raw_values, evidence_values = _epilepsy_cause_raw_from_prediction(base)
            replayed[record_id] = _epilepsy_cause_prediction_for_arm(
                record_id=record_id,
                raw_values=raw_values,
                evidence_values=evidence_values,
                program_variant=program_variant,
            )
        arm_results[arm_id] = {
            "program_variant": program_variant,
            "bridge_tiers": sorted(_s3_bridge_tiers(program_variant)),
            **_aggregate_epilepsy_cause_f1(
                record_ids=record_ids,
                predictions_by_id=replayed,
            ),
        }

    l1_docs = {row["record_id"]: row for row in arm_results["L1"]["per_document"]}
    label_fixes = 0
    label_regressions = 0
    k01_row = arm_results["K0+K1"]
    for row in k01_row["per_document"]:
        l1_row = l1_docs[row["record_id"]]
        if row["predicted"] != l1_row["predicted"]:
            if row["f1"] > l1_row["f1"]:
                label_fixes += 1
            elif row["f1"] < l1_row["f1"]:
                label_regressions += 1

    return {
        "reference_run_id": reference_run_dir.name,
        "record_ids": record_ids,
        "arms": arm_results,
        "headline": {
            "l1_epilepsy_cause_f1": arm_results["L1"]["epilepsy_cause_f1"],
            "k0_k1_epilepsy_cause_f1": arm_results["K0+K1"]["epilepsy_cause_f1"],
            "k0_k1_vs_l1_f1_delta": arm_results["K0+K1"]["epilepsy_cause_f1"]
            - arm_results["L1"]["epilepsy_cause_f1"],
            "label_fixes_vs_l1": label_fixes,
            "label_regressions_vs_l1": label_regressions,
        },
    }
