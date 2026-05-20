from __future__ import annotations

import json

import pytest

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.interleaving_adapters import (
    EvalOnlySurface,
    InterleavingAdapter,
    PostProcessorSurface,
    PreInjectionSurface,
    ToolDuringSurface,
    fingerprint_payload,
    get_interleaving_adapter,
    list_interleaving_adapters,
)
from clinical_extraction.primitives import primitive_registry_by_id


def _gan_record(record_id: str):
    return next(record for record in load_gan_records() if record.record_id == record_id)


GAN_NOTE = _gan_record("gan_10052").note_text
EXECT_MED_NOTE = "Current medication: Lamictal 100mg BD."


def test_list_interleaving_adapters_covers_implemented_registry_entries():
    adapters = list_interleaving_adapters()
    registry = primitive_registry_by_id()

    assert adapters
    for adapter in adapters:
        assert adapter.primitive_id in registry
        assert registry[adapter.primitive_id].status in {"implemented", "validated"}


def test_gan_temporal_candidates_pre_and_tool_during_share_core_payload():
    adapter = get_interleaving_adapter("gan.frequency.temporal_candidates.v1")

    pre = adapter.render("pre", note_text=GAN_NOTE)
    tool = adapter.render("tool_during", note_text=GAN_NOTE)

    assert isinstance(pre, PreInjectionSurface)
    assert isinstance(tool, ToolDuringSurface)
    assert pre.core_fingerprint == tool.core_fingerprint
    assert pre.position == "pre"
    assert tool.position == "tool_during"
    assert GAN_NOTE in pre.injected_note_text
    assert "Precomputed" in pre.injected_context
    assert tool.tool_name == "list_gan_frequency_temporal_candidates_v1"
    assert tool.execution_result
    parsed = json.loads(tool.execution_result)
    assert isinstance(parsed, list)
    assert parsed


def test_gan_temporal_candidates_during_surface_exposes_prompt_rules_without_changing_payload():
    adapter = get_interleaving_adapter("gan.frequency.temporal_candidates.v1")

    during = adapter.render("during", note_text=GAN_NOTE)
    pre = adapter.render("pre", note_text=GAN_NOTE)

    assert during.core_fingerprint == pre.core_fingerprint
    assert during.prompt_rules
    assert any("temporal" in rule.lower() for rule in during.prompt_rules)
    assert fingerprint_payload(during.reference_payload) == fingerprint_payload(
        pre.reference_payload
    )


def test_exect_medication_bridge_post_and_eval_only_share_core_payload():
    adapter = get_interleaving_adapter("exect.medication.benchmark_bridge.v1")

    post = adapter.render(
        "post",
        raw_value="lamotrigine",
        note_text=EXECT_MED_NOTE,
        evidence_text=EXECT_MED_NOTE,
    )
    eval_only = adapter.render(
        "eval_only",
        raw_value="lamotrigine",
        note_text=EXECT_MED_NOTE,
        evidence_text=EXECT_MED_NOTE,
    )

    assert isinstance(post, PostProcessorSurface)
    assert isinstance(eval_only, EvalOnlySurface)
    assert post.core_fingerprint == eval_only.core_fingerprint
    assert post.prediction_affecting
    assert not eval_only.prediction_affecting
    assert post.output_value == "lamictal"
    assert eval_only.diagnostic_payload.canonical_value == "lamotrigine"
    assert eval_only.diagnostic_payload.benchmark_value == "lamictal"


def test_gan_evidence_guard_post_and_eval_only_share_core_payload():
    note = "She had two seizures in January. She then had one seizure in March."
    adapter = get_interleaving_adapter("gan.frequency.evidence_guard.v1")

    post = adapter.render(
        "post",
        note_text=note,
        evidence_text="two seizures in January ... one seizure in March",
        label="3 per 3 month",
    )
    eval_only = adapter.render(
        "eval_only",
        note_text=note,
        evidence_text="two seizures in January ... one seizure in March",
        label="3 per 3 month",
    )

    assert post.core_fingerprint == eval_only.core_fingerprint
    assert post.support_status == eval_only.diagnostic_payload.support_status
    assert post.support_status == "normalized_interpretation"


def test_gan_label_policy_bridge_post_is_prediction_affecting_eval_only_is_not():
    adapter = get_interleaving_adapter("gan.frequency.label_policy_bridge.v1")

    post = adapter.render("post", label="Seizure free for 6 months")
    eval_only = adapter.render("eval_only", label="Seizure free for 6 months")

    assert post.core_fingerprint == eval_only.core_fingerprint
    assert post.prediction_affecting
    assert not eval_only.prediction_affecting
    assert post.output_value == "seizure free for 6 month"


def test_adapter_rejects_unsupported_interleaving_position():
    adapter = get_interleaving_adapter("exect.medication.benchmark_bridge.v1")

    with pytest.raises(ValueError, match="does not support interleaving position 'pre'"):
        adapter.render("pre", raw_value="lamotrigine", note_text=EXECT_MED_NOTE)


def test_adapter_rejects_primitive_without_binding():
    with pytest.raises(KeyError, match="no interleaving binding"):
        get_interleaving_adapter("shared.evidence.substring_support.v1")


def test_supported_positions_include_native_registry_positions():
    adapter = get_interleaving_adapter("gan.frequency.evidence_guard.v1")

    assert set(adapter.native_positions).issubset(set(adapter.supported_positions()))


def test_candidate_adapter_exposes_extra_interleaving_surfaces_for_experiments():
    adapter = get_interleaving_adapter("gan.frequency.temporal_candidates.v1")

    assert adapter.native_positions == ["pre"]
    assert set(adapter.supported_positions()) == {"pre", "during", "tool_during"}


def test_exect_medication_candidates_pre_injection_scopes_field_family():
    note = (
        "Current medication: Lamictal 100mg BD. "
        "To start levetiracetam 250mg nocte if seizures recur."
    )
    adapter = get_interleaving_adapter("exect.medication.rx_candidates.v1")
    surface = adapter.render("pre", note_text=note)

    assert "annotated_medication:" in surface.injected_context
    assert "lamictal" in surface.injected_context.lower()
    assert "diagnosis:" not in surface.injected_context.lower()


def test_interleaving_adapter_exposes_metadata():
    adapter = get_interleaving_adapter("gan.frequency.temporal_candidates.v1")

    assert isinstance(adapter, InterleavingAdapter)
    assert adapter.metadata.primitive_id == "gan.frequency.temporal_candidates.v1"
    assert adapter.metadata.field_families == ["frequency"]
