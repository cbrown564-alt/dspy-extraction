import json
from pathlib import Path

from clinical_extraction.evaluation.exect_s1_split_audit import (
    classify_s1_residual,
    field_f1_delta,
    summarize_s1_run,
)


def test_classify_s1_residual_prefers_specificity_collapse():
    mismatch = {
        "field_family": "diagnosis",
        "false_positives": ["epilepsy"],
        "false_negatives": ["juvenile myoclonic epilepsy"],
        "gold_quality_flags": ["specificity_collapsed"],
    }
    prediction_values = [
        {
            "field_name": "diagnosis",
            "normalized_value": "juvenile myoclonic epilepsy",
            "quality_flags": ["specificity_collapsed"],
        }
    ]

    assert classify_s1_residual(mismatch, prediction_values) == "specificity_collapse"


def test_classify_s1_residual_separates_bridge_policy_scope_and_extraction():
    assert (
        classify_s1_residual(
            {
                "field_family": "seizure_type",
                "false_positives": ["secondary generalisation"],
                "false_negatives": [],
                "gold_quality_flags": [],
            },
            [
                {
                    "field_name": "seizure_type",
                    "normalized_value": "secondary generalisation",
                    "quality_flags": ["benchmark_bridge:fused_seizure_type_split"],
                }
            ],
        )
        == "bridge"
    )
    assert (
        classify_s1_residual(
            {
                "field_family": "seizure_type",
                "false_positives": ["focal seizures with altered awareness"],
                "false_negatives": ["focal seizure"],
                "gold_quality_flags": [],
            },
            [],
        )
        == "policy"
    )
    assert (
        classify_s1_residual(
            {
                "field_family": "seizure_type",
                "false_positives": ["absence seizures"],
                "false_negatives": [],
                "gold_quality_flags": ["specificity_collapsed"],
            },
            [],
        )
        == "policy"
    )
    assert (
        classify_s1_residual(
            {
                "field_family": "diagnosis",
                "false_positives": ["epilepsy"],
                "false_negatives": [],
                "gold_quality_flags": [],
            },
            [],
            note_text="Family history: mother has epilepsy.",
        )
        == "scope"
    )
    assert (
        classify_s1_residual(
            {
                "field_family": "diagnosis",
                "false_positives": [],
                "false_negatives": ["focal epilepsy"],
                "gold_quality_flags": [],
            },
            [],
            note_text="Family history: mother has epilepsy.",
        )
        == "extraction"
    )
    assert (
        classify_s1_residual(
            {
                "field_family": "diagnosis",
                "false_positives": [],
                "false_negatives": ["focal epilepsy"],
                "gold_quality_flags": [],
            },
            [],
        )
        == "extraction"
    )


def test_field_f1_delta_limits_to_diagnosis_and_seizure_type():
    before = {"field_f1": {"diagnosis": 0.50, "seizure_type": 0.25, "annotated_medication": 0.9}}
    after = {"field_f1": {"diagnosis": 0.75, "seizure_type": 0.50, "annotated_medication": 0.8}}

    assert field_f1_delta(before, after) == {
        "diagnosis": 0.25,
        "seizure_type": 0.25,
    }


def test_summarize_s1_run_counts_bridge_flags_for_split_fields(tmp_path: Path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_json(
        run_dir / "config.json",
        {
            "split_name": "exectv2_fixed_v1:validation",
            "program_variant": "exect_s0_s1_field_family_single_pass",
            "prompt_version": "exect_s0_s1_field_family_v4_10_label_policy",
            "scorer_mode": "exect_field_family_deterministic_v1",
            "controls": {"repair_policy": "artifact_benchmark_bridge_only"},
        },
    )
    _write_json(
        run_dir / "metrics.json",
        {
            "benchmark_metrics": {
                "micro_f1": 0.75,
                "field_f1": {
                    "diagnosis": 0.8,
                    "seizure_type": 0.7,
                    "annotated_medication": 0.9,
                },
                "field_precision": {"diagnosis": 1.0, "seizure_type": 1.0},
                "field_recall": {"diagnosis": 0.67, "seizure_type": 0.54},
                "field_support": {"diagnosis": 2, "seizure_type": 2},
            },
            "counts": {"evaluated_records": 1},
        },
    )
    _write_json(
        run_dir / "errors.json",
        {
            "field_family_mismatches": [
                {
                    "document_id": "EA_TEST",
                    "field_family": "diagnosis",
                    "false_positives": ["epilepsy"],
                    "false_negatives": [],
                    "gold_quality_flags": [],
                }
            ],
            "evidence_support_errors": [],
        },
    )
    _write_json(
        run_dir / "predictions.json",
        {
            "dataset": "exect_v2",
            "schema_level": "exect_s0_s1_field_family",
            "metadata": {},
            "predictions": [
                {
                    "dataset": "exect_v2",
                    "document_id": "EA_TEST",
                    "schema_level": "exect_s0_s1_field_family",
                    "quality_flags": [],
                    "metadata": {"bridge_stage": "post"},
                    "values": [
                        {
                            "field_name": "diagnosis",
                            "raw_value": "epilepsy",
                            "normalized_value": "epilepsy",
                            "quality_flags": ["benchmark_bridge:diagnosis_parent_added"],
                        },
                        {
                            "field_name": "annotated_medication",
                            "raw_value": "lamotrigine",
                            "normalized_value": "lamotrigine",
                            "quality_flags": ["benchmark_bridge:current_prescription_medication_augmented"],
                        },
                    ],
                }
            ],
        },
    )

    summary = summarize_s1_run(run_dir)

    assert summary["run_id"] == "run"
    assert summary["micro_f1"] == 0.75
    assert summary["field_f1"] == {"diagnosis": 0.8, "seizure_type": 0.7}
    assert summary["bridge_flag_counts"] == {"diagnosis": 1, "seizure_type": 0}
    assert summary["residual_class_counts"] == {"bridge": 1}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
