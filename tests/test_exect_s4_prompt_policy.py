from clinical_extraction.exect.frequency_payload import (
    build_exect_frequency_pre_vocab_labels,
    format_exect_frequency_pre_vocab_note,
)
from clinical_extraction.programs.exect_s4 import (
    EXECT_S4_FREQUENCY_QUALITATIVE_EVIDENCE_GATE_GUIDANCE,
    EXECT_S4_PROMPT_VERSION,
    EXECT_S4_PROMPT_VERSION_V1_3,
    EXECT_S4_V1_3_POLICY_EXAMPLES,
    ExectS4FrequencyPreVocabV13FieldFamilyModule,
    resolve_exect_s4_frequency_label_policy,
)


def test_resolve_exect_s4_frequency_label_policy_v1_2_unchanged():
    guidance, examples = resolve_exect_s4_frequency_label_policy(EXECT_S4_PROMPT_VERSION)

    assert "Qualitative labels" not in " ".join(guidance)
    assert not any(
        example.get("case") == "s4_qual_no_infrequent_without_wording" for example in examples
    )


def test_resolve_exect_s4_frequency_label_policy_v1_3_adds_qualitative_gate():
    guidance, examples = resolve_exect_s4_frequency_label_policy(
        EXECT_S4_PROMPT_VERSION_V1_3
    )

    assert EXECT_S4_FREQUENCY_QUALITATIVE_EVIDENCE_GATE_GUIDANCE[0] in guidance
    assert any(
        example.get("case") == "s4_qual_no_infrequent_without_wording" for example in examples
    )
    assert EXECT_S4_V1_3_POLICY_EXAMPLES[0] in examples


def test_v1_3_prompt_policy_does_not_change_candidate_builder_output():
    note_text = (
        "He has about one focal seizure every three weeks and the frequency has increased."
    )

    baseline = build_exect_frequency_pre_vocab_labels(note_text)
    formatted = format_exect_frequency_pre_vocab_note(note_text)

    assert build_exect_frequency_pre_vocab_labels(note_text) == baseline
    assert "soft hints; emit only when note-supported" in formatted
    assert isinstance(ExectS4FrequencyPreVocabV13FieldFamilyModule(), ExectS4FrequencyPreVocabV13FieldFamilyModule)
