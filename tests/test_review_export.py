import json

from clinical_extraction.review.export import (
    build_review_queue_items,
    write_review_queue_jsonl,
)


def test_build_review_queue_items_flattens_error_analysis_examples():
    report = {
        "dataset": "gan_2026",
        "schema_level": "gan_frequency_s0",
        "scorer": "gan_frequency_deterministic_v1",
        "error_analysis": {
            "counts": {
                "normalization.monthly_frequency_mismatch": 2,
                "evidence.unsupported_quote": 1,
            },
            "examples": {
                "normalization.monthly_frequency_mismatch": [
                    {
                        "record_id": "gan-1",
                        "reason": "monthly frequency differs from gold",
                        "gold_monthly_frequency": 4.0,
                        "predicted_monthly_frequency": 1.0,
                    }
                ],
                "evidence.unsupported_quote": [
                    {
                        "record_id": "gan-1",
                        "reason": "predicted evidence quote is unsupported",
                    }
                ],
            },
        },
    }

    items = build_review_queue_items(report)

    assert items == [
        {
            "review_id": "gan_2026:gan-1:evidence.unsupported_quote:1",
            "dataset": "gan_2026",
            "schema_level": "gan_frequency_s0",
            "scorer": "gan_frequency_deterministic_v1",
            "record_id": "gan-1",
            "category": "evidence.unsupported_quote",
            "category_count": 1,
            "reason": "predicted evidence quote is unsupported",
            "priority": "high",
            "details": {},
        },
        {
            "review_id": "gan_2026:gan-1:normalization.monthly_frequency_mismatch:1",
            "dataset": "gan_2026",
            "schema_level": "gan_frequency_s0",
            "scorer": "gan_frequency_deterministic_v1",
            "record_id": "gan-1",
            "category": "normalization.monthly_frequency_mismatch",
            "category_count": 2,
            "reason": "monthly frequency differs from gold",
            "priority": "high",
            "details": {
                "gold_monthly_frequency": 4.0,
                "predicted_monthly_frequency": 1.0,
            },
        },
    ]


def test_write_review_queue_jsonl_is_deterministic(tmp_path):
    report = {
        "dataset": "gan_2026",
        "schema_level": "gan_frequency_s0",
        "error_analysis": {
            "counts": {"schema.missing_prediction": 3},
            "examples": {
                "schema.missing_prediction": [
                    {"record_id": "gan-2", "reason": "gold record has no prediction"}
                ]
            },
        },
    }
    output_path = tmp_path / "review_queue.jsonl"

    count = write_review_queue_jsonl(report, output_path)

    assert count == 1
    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["review_id"] == (
        "gan_2026:gan-2:schema.missing_prediction:1"
    )
