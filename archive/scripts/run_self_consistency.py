"""Run Gan S0 repeated-sampling self-consistency experiment and aggregate results."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

import dspy

from clinical_extraction.experiments.backends import get_backend
from clinical_extraction.experiments.config import load_experiment_config
from clinical_extraction.llms import LLMProviderConfig, build_dspy_lm
from clinical_extraction.programs.gan_frequency_s0 import (
    _predict_record,
    build_gan_s0_module,
)
from clinical_extraction.gan.frequency import (
    label_to_monthly_frequency,
    normalize_label,
)
from clinical_extraction.gan.scoring import score_gan_frequency_prediction
from clinical_extraction.schemas import (
    DocumentPrediction,
    ExtractedValue,
    PredictionSet,
)
from clinical_extraction.runs import create_run_artifact_layout

def compute_entropy(labels: list[str]) -> float:
    if not labels:
        return 0.0
    counts = Counter(labels)
    total = len(labels)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run Gan S0 self-consistency repeated sampling.",
    )
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--env-file", type=Path, help="Load API keys from .env file.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.env_file is not None:
        from clinical_extraction.experiments.runner import load_env_file
        load_env_file(args.env_file)

    config = load_experiment_config(args.config)
    backend = get_backend(config.dataset)

    print(f"Self-Consistency Experiment: {config.experiment_id}")
    print(f"Dataset:                      {config.dataset}")
    print(f"Split:                        {config.split_name}")
    print(f"Model config:                 {config.model_config_path}")

    model_config = LLMProviderConfig.model_validate_json(
        config.model_config_path.read_text(encoding="utf-8")
    )

    all_records = backend.load_records_by_id()
    from clinical_extraction.experiments.runner import load_split_records
    records, missing = load_split_records(config, all_records)
    print(f"Records loaded: {len(records)}")

    if args.dry_run:
        print("Dry run complete.")
        return 0

    lm = build_dspy_lm(model_config)
    lm.cache = False
    dspy.configure(lm=lm)

    # Initialize layout and parent directory
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    parent_run_id = f"{config.experiment_id}_{timestamp}"
    run_dir = Path("runs") / parent_run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Parent Run Directory: {run_dir}")

    # Build Module
    module = backend.build_module(config, prompt_version=config.prompt_version)

    # Predict 5 samples per record
    record_samples: dict[str, list[DocumentPrediction]] = {}
    record_latencies: dict[str, list[float]] = {}

    total_records = len(records)
    print(f"Starting repeated sampling (5x) on {total_records} records...")

    for i, record in enumerate(records, start=1):
        print(f"  Processing record {i}/{total_records}: {record.record_id}")
        record_samples[record.record_id] = []
        record_latencies[record.record_id] = []
        for s_idx in range(1, 6):
            t0 = perf_counter()
            pred_doc = _predict_record(
                module,
                record,
                program_variant=config.program_variant,
                repair_policy=config.controls.repair_policy,
            )
            lat = perf_counter() - t0
            record_samples[record.record_id].append(pred_doc)
            record_latencies[record.record_id].append(lat)

    # Write all raw samples to disk
    samples_serialized = {
        rid: [doc.model_dump(mode="json") for doc in docs]
        for rid, docs in record_samples.items()
    }
    (run_dir / "all_samples.json").write_text(
        json.dumps(samples_serialized, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    # Aggregate arms
    arm_predictions: dict[str, list[DocumentPrediction]] = {
        "S0": [],  # stochastic single-pass
        "S1": [],  # majority vote
        "S2": [],  # confidence weighted (falls back to S1)
        "S3": [],  # majority + tie breakers
        "S4": [],  # abstain-on-instability
    }

    # Variance stats per record
    variance_stats = {}

    for record in records:
        rid = record.record_id
        samples = record_samples[rid]
        lats = record_latencies[rid]

        # Extract values
        valid_normalized_labels: list[str] = []
        raw_labels: list[str] = []
        evidences: list[str] = []
        for doc in samples:
            val = doc.values[0] if doc.values else None
            if val and "abstained" not in val.quality_flags:
                valid_normalized_labels.append(val.normalized_value or "unknown")
                raw_labels.append(val.raw_value or "unknown")
                if val.evidence:
                    evidences.append(val.evidence[0].text)
            else:
                valid_normalized_labels.append("unknown")
                raw_labels.append("unknown")

        # S0: First sample
        arm_predictions["S0"].append(samples[0])

        # Compute monthly frequencies
        monthly_freqs = [label_to_monthly_frequency(lbl) for lbl in valid_normalized_labels]

        # Basic Stats
        unique_lbl_count = len(set(valid_normalized_labels))
        vote_ent = compute_entropy(valid_normalized_labels)
        counts = Counter(valid_normalized_labels)
        most_common = counts.most_common(2)
        if len(most_common) >= 2:
            top_margin = (most_common[0][1] - most_common[1][1]) / 5.0
        else:
            top_margin = most_common[0][1] / 5.0 if most_common else 0.0

        monthly_range = max(monthly_freqs) - min(monthly_freqs) if monthly_freqs else 0.0
        valid_sample_rate = len([v for v in samples if v.values and "abstained" not in v.values[0].quality_flags]) / 5.0
        evidence_support_rate = len(evidences) / 5.0

        variance_stats[rid] = {
            "unique_label_count": unique_lbl_count,
            "vote_entropy": vote_ent,
            "top_vote_margin": top_margin,
            "monthly_value_range": monthly_range,
            "valid_sample_rate": valid_sample_rate,
            "evidence_support_rate": evidence_support_rate,
            "samples": valid_normalized_labels,
        }

        # Helper to construct aggregated DocumentPrediction
        def make_agg_doc(label_val: str, evidence_val: str | None, flags: list[str], meta: dict[str, Any]) -> DocumentPrediction:
            from clinical_extraction.programs.gan_frequency_s0 import _normalize_predicted_label, _evidence_spans
            norm_lbl = _normalize_predicted_label(label_val)
            ev_spans = _evidence_spans(record, evidence_val) if evidence_val else []
            val = ExtractedValue(
                field_name="seizure_frequency_number",
                raw_value=label_val,
                normalized_value=norm_lbl,
                evidence=ev_spans,
                quality_flags=flags,
            )
            return DocumentPrediction(
                document_id=rid,
                dataset="gan_2026",
                schema_level="gan_frequency_s0",
                values=[val],
                metadata=meta,
            )

        # S1: Majority Vote
        s1_winner = counts.most_common(1)[0][0] if counts else "unknown"
        # evidence: find first sample with this label and use its evidence
        s1_evidence = None
        for doc in samples:
            val = doc.values[0] if doc.values else None
            if val and val.normalized_value == s1_winner and val.evidence:
                s1_evidence = val.evidence[0].text
                break
        arm_predictions["S1"].append(make_agg_doc(s1_winner, s1_evidence, [], {"policy": "majority_vote"}))

        # S2: Confidence-weighted (equal weight fallback)
        arm_predictions["S2"].append(make_agg_doc(s1_winner, s1_evidence, [], {"policy": "confidence_weighted_fallback"}))

        # S3: Majority + Tie Break
        # Rank unique labels by:
        # 1. -vote_count
        # 2. -evidence_support_count
        # 3. monthly_value
        # 4. first_idx
        label_rankings = []
        for lbl in counts:
            lbl_samples = [s for s in samples if s.values and s.values[0].normalized_value == lbl]
            vote_cnt = len(lbl_samples)
            ev_sup_cnt = sum(1 for s in lbl_samples if s.values[0].evidence)
            m_val = label_to_monthly_frequency(lbl)
            first_idx = next(i for i, s in enumerate(samples) if s.values and s.values[0].normalized_value == lbl)
            label_rankings.append((lbl, vote_cnt, ev_sup_cnt, m_val, first_idx))

        label_rankings.sort(key=lambda x: (-x[1], -x[2], x[3], x[4]))
        s3_winner = label_rankings[0][0] if label_rankings else "unknown"
        s3_evidence = None
        for doc in samples:
            val = doc.values[0] if doc.values else None
            if val and val.normalized_value == s3_winner and val.evidence:
                s3_evidence = val.evidence[0].text
                break
        arm_predictions["S3"].append(make_agg_doc(s3_winner, s3_evidence, [], {"policy": "majority_plus_tiebreak"}))

        # S4: Abstain on instability (margin < 0.2)
        if top_margin < 0.2:
            if "unknown" in valid_normalized_labels:
                s4_winner = "unknown"
                s4_evidence = None
            else:
                s4_winner = s3_winner
                s4_evidence = s3_evidence
        else:
            s4_winner = s3_winner
            s4_evidence = s3_evidence
        arm_predictions["S4"].append(make_agg_doc(s4_winner, s4_evidence, [], {"policy": "abstain_on_instability"}))

    # Evaluate each arm and save outputs
    all_arm_results = {}
    for arm, preds in arm_predictions.items():
        pred_set = PredictionSet(
            dataset="gan_2026",
            schema_level="gan_frequency_s0",
            predictions=preds,
            metadata={
                "experiment_id": f"gan_s0_self_consistency_{arm.lower()}_cap25_gpt4_1_mini",
                "program_variant": config.program_variant,
                "prompt_version": config.prompt_version,
                "scorer_mode": config.scorer_mode,
            },
        )
        report = backend.evaluate_predictions(pred_set)
        
        # Save files mimicking runner structure
        arm_dir = run_dir / arm.lower()
        arm_dir.mkdir(parents=True, exist_ok=True)
        (arm_dir / "predictions.json").write_text(
            json.dumps(pred_set.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (arm_dir / "metrics.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        
        all_arm_results[arm] = report

    # Calculate error prediction diagnostics
    s0_results = all_arm_results["S0"]
    # Check which S0 predictions are incorrect
    # S0 exact normalized match rate
    # Let's compute correctness of S0 vs variance
    # S0 predictions are in arm_predictions["S0"]
    s0_preds = arm_predictions["S0"]
    s0_correct_map = {}
    for pred in s0_preds:
        rid = pred.document_id
        gold = all_records[rid].gold_label
        pred_val = pred.values[0].normalized_value if pred.values else None
        s0_correct_map[rid] = (normalize_label(gold) == pred_val)

    # 2x2 error vs disagreement table
    # Disagreement: unique_label_count > 1
    tp, fp, fn, tn = 0, 0, 0, 0
    for rid, stats in variance_stats.items():
        disagreed = stats["unique_label_count"] > 1
        s0_wrong = not s0_correct_map[rid]
        stats["s0_wrong"] = s0_wrong
        if disagreed and s0_wrong:
            tp += 1
        elif disagreed and not s0_wrong:
            fp += 1
        elif not disagreed and s0_wrong:
            fn += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    error_analysis = {
        "confusion_matrix": {"TP": tp, "FP": fp, "FN": fn, "TN": tn},
        "precision": precision,
        "recall": recall,
    }

    # Save final aggregate report
    final_report = {
        "experiment_id": config.experiment_id,
        "parent_run_id": parent_run_id,
        "timestamp": timestamp,
        "arm_metrics": {
            arm: {
                "monthly_accuracy": rep.get("benchmark_metrics", {}).get("monthly_frequency_accuracy"),
                "purist_accuracy": rep.get("benchmark_metrics", {}).get("purist_category_accuracy"),
                "pragmatic_accuracy": rep.get("benchmark_metrics", {}).get("pragmatic_category_accuracy"),
                "schema_validity": rep.get("diagnostic_metrics", {}).get("schema_valid_prediction_rate"),
                "evidence_support": rep.get("diagnostic_metrics", {}).get("evidence_quote_support_rate"),
            }
            for arm, rep in all_arm_results.items()
        },
        "error_analysis": error_analysis,
        "record_variance_diagnostics": variance_stats,
    }

    (run_dir / "self_consistency_report.json").write_text(
        json.dumps(final_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("\n--- Self-Consistency Run Complete ---")
    for arm, metrics in final_report["arm_metrics"].items():
        acc_val = metrics['monthly_accuracy']
        val_val = metrics['schema_validity']
        acc_str = f"{acc_val:.1%}" if acc_val is not None else "N/A"
        val_str = f"{val_val:.1%}" if val_val is not None else "N/A"
        print(f"Arm {arm}: Monthly Accuracy = {acc_str}, Valid = {val_str}")

    print(f"\nDisagreement (variance > 1) vs S0 correctness:")
    print(f"  True Positives (Disagreed & S0 Wrong): {tp}")
    print(f"  False Positives (Disagreed & S0 Right): {fp}")
    print(f"  False Negatives (Stable & S0 Wrong): {fn}")
    print(f"  True Negatives (Stable & S0 Right): {tn}")
    print(f"  Precision: {precision:.1%}, Recall: {recall:.1%}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
