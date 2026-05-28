"""Gan seizure-frequency S0 DSPy program compatibility facade."""
from __future__ import annotations

from clinical_extraction.gan.s0.date_events import *  # noqa: F401,F403
from clinical_extraction.gan.s0.metrics import *  # noqa: F401,F403
from clinical_extraction.gan.s0.modules import *  # noqa: F401,F403
from clinical_extraction.gan.s0.optimizer_setup import *  # noqa: F401,F403
from clinical_extraction.gan.s0.prediction_bridge import *  # noqa: F401,F403
from clinical_extraction.gan.s0.signatures import *  # noqa: F401,F403
from clinical_extraction.gan.s0.variant_routing import *  # noqa: F401,F403

from clinical_extraction.gan.s0.modules import (  # noqa: F401
    _apply_det_evidence_grounding,
    _build_gan_frequency_s0_llm_candidate_generator_signature,
    _llm_temporal_candidates_from_prediction,
    _multiple_answer_label_class,
    _multiple_answer_option_to_dict,
    _multiple_answer_selector_score,
    _parse_multiple_answer_options_json,
    _parse_multiple_answer_options_json_with_rejections,
    _prediction_from_temporal_adjudicate_validation,
    _prompt_note_text_for_context_policy,
    _raw_multiple_answer_option_to_dict,
    _synthetic_confirm_from_adjudicate,
    _temporal_adjudication_prediction,
    _temporal_candidates_to_multiple_answer_options,
)
from clinical_extraction.gan.s0.optimizer_setup import (  # noqa: F401
    _gan_s0_optimizer_trainset,
    _locatable_gold_evidence,
    _synthesis_example_priority,
)
from clinical_extraction.gan.s0.prediction_bridge import (  # noqa: F401
    _apply_constrained_verifier_guard,
    _apply_evidence_span_check_guard,
    _apply_temporal_verifier_guards,
    _evidence_policy_feedback,
    _evidence_policy_ok,
    _evidence_spans,
    _forbidden_unit,
    _guard_evidence_text,
    _has_temporal_window_mismatch,
    _is_short_seizure_free_label,
    _looks_like_cluster_failure,
    _looks_like_no_reference_note,
    _normalize_predicted_label,
    _predict_record,
    _requires_evidence_support,
)
