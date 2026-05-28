"""Gan S0 optimizer metrics and feedback surfaces."""
from __future__ import annotations

import dspy

from clinical_extraction.gan.s0.prediction_bridge import (
    _evidence_policy_feedback,
    _evidence_policy_ok,
    _forbidden_unit,
    _has_temporal_window_mismatch,
    _is_short_seizure_free_label,
    _looks_like_cluster_failure,
    _requires_evidence_support,
)
from clinical_extraction.gan.s0.variant_routing import GAN_FREQUENCY_S0_FIELD
from clinical_extraction.gan.scoring import score_gan_frequency_prediction


def gan_frequency_s0_metric(
    example: dspy.Example,
    pred: dspy.Prediction,
    trace=None,
) -> float:
    """DSPy metric for Gan S0 optimizer training.

    Uses pragmatic category match (infrequent / frequent / unknown) as the
    optimization target; benchmark reporting remains controlled by the
    configured scorer mode outside this optimizer-facing metric.
    """
    predicted = getattr(pred, GAN_FREQUENCY_S0_FIELD, None)
    gold = getattr(example, GAN_FREQUENCY_S0_FIELD, None)

    if not predicted or not gold:
        return 0.0

    try:
        score = score_gan_frequency_prediction(
            gold_label=gold, predicted_label=predicted
        )
        return float(score.pragmatic_category_match)
    except ValueError:
        return 0.0


def gan_frequency_s0_synthesis_metric(
    example: dspy.Example,
    pred: dspy.Prediction,
    trace=None,
) -> float:
    """Stricter optimizer metric for synthesis-backed Gan S0 compilation."""
    predicted = getattr(pred, GAN_FREQUENCY_S0_FIELD, None)
    gold = getattr(example, GAN_FREQUENCY_S0_FIELD, None)

    if not predicted or not gold:
        return 0.0

    try:
        score = score_gan_frequency_prediction(
            gold_label=gold, predicted_label=predicted
        )
    except ValueError:
        return 0.0

    if not score.exact_normalized_match:
        return 0.0

    predicted_evidence = getattr(pred, "evidence_text", None)
    if gold == "no seizure frequency reference":
        return float(predicted_evidence is None or not str(predicted_evidence).strip())

    if not _requires_evidence_support(gold):
        return 1.0

    if not isinstance(predicted_evidence, str) or not predicted_evidence.strip():
        return 0.0
    return float(predicted_evidence.strip() in example.note_text)


def gan_frequency_s0_synthesis_feedback_metric(
    example: dspy.Example,
    pred: dspy.Prediction,
    trace=None,
    pred_name=None,
    pred_trace=None,
):
    """GEPA-compatible Gan S0 feedback metric."""
    from dspy.teleprompt.gepa.gepa_utils import ScoreWithFeedback

    predicted = getattr(pred, GAN_FREQUENCY_S0_FIELD, None)
    gold = getattr(example, GAN_FREQUENCY_S0_FIELD, None)
    note_text = getattr(example, "note_text", "") or ""

    if not predicted:
        return ScoreWithFeedback(
            score=0.0,
            feedback=(
                "[abstention] The prediction did not provide seizure_frequency_number. "
                "Return a canonical Gan label or no seizure frequency reference, and "
                "abstain only when the note truly lacks usable seizure-frequency information."
            ),
        )
    if not gold:
        return ScoreWithFeedback(
            score=0.0,
            feedback="The training example is missing the gold Gan frequency label.",
        )

    try:
        score = score_gan_frequency_prediction(
            gold_label=gold, predicted_label=predicted
        )
    except ValueError as exc:
        feedback = [
            (
                "[invalid-format] "
                f"The predicted label {predicted!r} is not a valid canonical Gan "
                f"frequency label: {exc}."
            )
        ]
        if _looks_like_cluster_failure(str(predicted)):
            feedback.append(
                "[cluster-format] Cluster labels must use the full format "
                "'N cluster per unit, M per cluster' and must not drop the "
                "per-cluster count."
            )
        forbidden_unit = _forbidden_unit(str(predicted))
        if forbidden_unit is not None:
            feedback.append(
                f"[forbidden-unit] Replace {forbidden_unit!r} with canonical Gan "
                "units day, week, month, or year."
            )
        return ScoreWithFeedback(
            score=0.0,
            feedback=" ".join(feedback),
        )

    predicted_evidence = getattr(pred, "evidence_text", None)
    feedback: list[str] = []
    metric_score = 0.8 if score.exact_normalized_match else 0.0

    if not score.exact_normalized_match:
        feedback.append(
            "[exact-label] "
            f"Expected normalized Gan label {gold!r}, but the prediction was "
            f"{predicted!r}. Preserve the benchmark-facing label semantics."
        )
        if score.pragmatic_category_match:
            metric_score = 0.3
        else:
            feedback.append(
                "[pragmatic-category] The prediction crossed the benchmark-facing "
                f"Pragmatic bucket from {score.gold_pragmatic_category!r} to "
                f"{score.predicted_pragmatic_category!r}."
            )
        if (
            _looks_like_cluster_failure(score.predicted_label)
            or "cluster" in score.normalized_gold_label
        ):
            feedback.append(
                "[cluster-format] Preserve the cluster structure exactly. Do not "
                "drop the cluster period or the per-cluster count, and do not back "
                "off to unknown when the note gives both values."
            )
        if _is_short_seizure_free_label(score.normalized_predicted_label):
            feedback.append(
                "[seizure-free-threshold] Use seizure-free labels only for 6 months "
                "or longer. Shorter seizure-free periods should be converted into "
                "the appropriate quantified rate."
            )
        if _has_temporal_window_mismatch(
            note_text,
            gold_label=score.normalized_gold_label,
            predicted_label=score.normalized_predicted_label,
        ):
            feedback.append(
                "[temporal-window] The note looks like a year-to-date or bounded-window "
                "case. Use the described observation window as the denominator; for "
                "year-to-date counts, use months elapsed since January."
            )

    evidence_ok = True
    if gold == "no seizure frequency reference":
        if isinstance(predicted_evidence, str) and predicted_evidence.strip():
            evidence_ok = False
            feedback.append(
                "[evidence-support] No-reference labels should not include supporting "
                "frequency evidence."
            )
    elif _requires_evidence_support(gold):
        if not isinstance(predicted_evidence, str) or not predicted_evidence.strip():
            evidence_ok = False
            feedback.append(
                "[evidence-support] The prediction must include an exact contiguous "
                "source quote as evidence."
            )
        elif predicted_evidence.strip() not in example.note_text:
            evidence_ok = False
            feedback.append(
                "[evidence-support][unsupported-quote] The evidence_text is not an "
                "exact contiguous quote from the note."
            )

    if evidence_ok:
        metric_score += 0.2

    if not feedback:
        feedback.append(
            "The prediction matched the normalized Gan label and evidence policy."
        )
    return ScoreWithFeedback(score=metric_score, feedback=" ".join(feedback))


def gan_frequency_s0_semantic_evidence_metric(
    example: dspy.Example,
    pred: dspy.Prediction,
    trace=None,
) -> float:
    """Graded optimizer metric for Gan frequency extraction."""
    predicted = getattr(pred, GAN_FREQUENCY_S0_FIELD, None)
    gold = getattr(example, GAN_FREQUENCY_S0_FIELD, None)

    if not predicted or not gold:
        return 0.0

    try:
        score = score_gan_frequency_prediction(
            gold_label=gold, predicted_label=predicted
        )
    except ValueError:
        return 0.0

    predicted_evidence = getattr(pred, "evidence_text", None)
    if not _evidence_policy_ok(
        gold_label=gold,
        predicted_evidence=predicted_evidence,
        note_text=getattr(example, "note_text", "") or "",
    ):
        return 0.0

    return _semantic_frequency_reward(score)


def gan_frequency_s0_semantic_evidence_feedback_metric(
    example: dspy.Example,
    pred: dspy.Prediction,
    trace=None,
    pred_name=None,
    pred_trace=None,
):
    """GEPA-compatible graded Gan S0 feedback metric."""
    from dspy.teleprompt.gepa.gepa_utils import ScoreWithFeedback

    predicted = getattr(pred, GAN_FREQUENCY_S0_FIELD, None)
    gold = getattr(example, GAN_FREQUENCY_S0_FIELD, None)
    note_text = getattr(example, "note_text", "") or ""

    if not predicted:
        return ScoreWithFeedback(
            score=0.0,
            feedback=(
                "[abstention] The prediction did not provide seizure_frequency_number. "
                "Return a canonical Gan label or no seizure frequency reference."
            ),
        )
    if not gold:
        return ScoreWithFeedback(
            score=0.0,
            feedback="The training example is missing the gold Gan frequency label.",
        )

    try:
        score = score_gan_frequency_prediction(
            gold_label=gold, predicted_label=predicted
        )
    except ValueError as exc:
        return ScoreWithFeedback(
            score=0.0,
            feedback=(
                "[invalid-format] "
                f"The predicted label {predicted!r} is not a valid canonical Gan "
                f"frequency label: {exc}."
            ),
        )

    predicted_evidence = getattr(pred, "evidence_text", None)
    evidence_feedback = _evidence_policy_feedback(
        gold_label=gold,
        predicted_evidence=predicted_evidence,
        note_text=note_text,
    )
    if evidence_feedback is not None:
        return ScoreWithFeedback(score=0.0, feedback=evidence_feedback)

    metric_score = _semantic_frequency_reward(score)
    feedback = _semantic_frequency_feedback(score)
    return ScoreWithFeedback(score=metric_score, feedback=feedback)


def gan_frequency_s0_stage_attributed_feedback_metric(
    example: dspy.Example,
    pred: dspy.Prediction,
    trace=None,
    pred_name=None,
    pred_trace=None,
):
    """GEPA feedback metric that names the Gan S0 pipeline stage at fault."""
    from dspy.teleprompt.gepa.gepa_utils import ScoreWithFeedback
    from clinical_extraction.gan.temporal_candidates import (
        build_temporal_frequency_candidates_from_note,
    )

    base = gan_frequency_s0_semantic_evidence_feedback_metric(
        example,
        pred,
        trace=trace,
        pred_name=pred_name,
        pred_trace=pred_trace,
    )
    predicted = getattr(pred, GAN_FREQUENCY_S0_FIELD, None)
    gold = getattr(example, GAN_FREQUENCY_S0_FIELD, None)
    note_text = getattr(example, "note_text", "") or ""

    stage_feedback: list[str] = []
    if not predicted:
        stage_feedback.append(
            "[stage:adjudicator] The LLM did not select a canonical Gan label."
        )
        return ScoreWithFeedback(
            score=base.score,
            feedback=" ".join(stage_feedback + [base.feedback]),
        )

    try:
        score = score_gan_frequency_prediction(
            gold_label=gold,
            predicted_label=predicted,
        )
    except ValueError:
        stage_feedback.append(
            "[stage:format] The emitted label is malformed before benchmark "
            "scoring can compare frequency semantics."
        )
        return ScoreWithFeedback(
            score=base.score,
            feedback=" ".join(stage_feedback + [base.feedback]),
        )

    candidate_labels = {
        candidate.canonical_label
        for candidate in build_temporal_frequency_candidates_from_note(note_text)
    }
    normalized_candidate_labels = {
        score_gan_frequency_prediction(gold_label=label, predicted_label=label)
        .normalized_gold_label
        for label in candidate_labels
    }
    gold_candidate_missing = (
        gold not in {"unknown", "no seizure frequency reference"}
        and score.normalized_gold_label not in normalized_candidate_labels
    )
    if gold_candidate_missing:
        stage_feedback.append(
            "[stage:candidate_surface] The deterministic temporal-candidate "
            "surface did not include the normalized gold label; do not treat this "
            "as an adjudicator-only failure."
        )

    evidence_feedback = _evidence_policy_feedback(
        gold_label=gold,
        predicted_evidence=getattr(pred, "evidence_text", None),
        note_text=note_text,
    )
    if evidence_feedback is not None:
        stage_feedback.append(
            "[stage:evidence] The label/evidence pair failed the source-quote "
            "support contract."
        )

    if not score.exact_normalized_match:
        if getattr(pred, "verifier_decision", None) or getattr(pred, "verifier_reason", None):
            stage_feedback.append(
                "[stage:verifier] The verify/repair stage returned a residual "
                "frequency error after seeing the initial label."
            )
        elif not gold_candidate_missing:
            stage_feedback.append(
                "[stage:adjudicator] The gold-compatible candidate surface was "
                "available or not disproven, but the selected label missed the "
                "Gan frequency semantics."
            )
        if (
            _looks_like_cluster_failure(score.predicted_label)
            or "cluster" in score.normalized_gold_label
        ):
            stage_feedback.append(
                "[stage:format] Preserve canonical cluster structure and "
                "per-cluster counts."
            )

    if not stage_feedback:
        stage_feedback.append(
            "[stage:all] Candidate surface, adjudication, evidence, and format "
            "matched the optimizer-facing contract."
        )

    return ScoreWithFeedback(
        score=base.score,
        feedback=" ".join(stage_feedback + [base.feedback]),
    )


def _semantic_frequency_reward(score) -> float:
    if score.exact_normalized_match:
        return 1.0
    if score.monthly_frequency_match:
        return 0.85
    if score.purist_category_match:
        return 0.65
    if score.pragmatic_category_match:
        return 0.4
    return 0.0


def _semantic_frequency_feedback(score) -> str:
    if score.exact_normalized_match:
        return (
            "[exact-label][evidence-support] The prediction matched the normalized "
            "Gan label and evidence policy."
        )
    if score.monthly_frequency_match:
        return (
            "[monthly-frequency] The prediction converts to the correct seizures "
            "per month, but the canonical Gan label surface differs from gold."
        )
    if score.purist_category_match:
        return (
            "[purist-category] The prediction preserves the fine-grained Purist "
            "frequency category but misses the exact monthly value or canonical label."
        )
    if score.pragmatic_category_match:
        return (
            "[pragmatic-category] The prediction preserves only the coarse "
            "infrequent/frequent/unknown/no-reference bucket. Improve the temporal "
            "window, cluster details, or numeric conversion."
        )
    return (
        "[frequency-semantics] The prediction crossed the benchmark-facing "
        f"Pragmatic bucket from {score.gold_pragmatic_category!r} to "
        f"{score.predicted_pragmatic_category!r}."
    )


GAN_FREQUENCY_S0_OPTIMIZER_METRICS = {
    "pragmatic_category": gan_frequency_s0_metric,
    "semantic_frequency_with_evidence": gan_frequency_s0_semantic_evidence_metric,
    "semantic_frequency_with_evidence_feedback": (
        gan_frequency_s0_semantic_evidence_feedback_metric
    ),
    "gan_s0_stage_attributed_frequency_feedback": (
        gan_frequency_s0_stage_attributed_feedback_metric
    ),
    "synthesis_exact_with_evidence": gan_frequency_s0_synthesis_metric,
    "synthesis_exact_with_evidence_feedback": gan_frequency_s0_synthesis_feedback_metric,
}


__all__ = [
    "GAN_FREQUENCY_S0_OPTIMIZER_METRICS",
    "gan_frequency_s0_metric",
    "gan_frequency_s0_semantic_evidence_feedback_metric",
    "gan_frequency_s0_semantic_evidence_metric",
    "gan_frequency_s0_stage_attributed_feedback_metric",
    "gan_frequency_s0_synthesis_feedback_metric",
    "gan_frequency_s0_synthesis_metric",
]
