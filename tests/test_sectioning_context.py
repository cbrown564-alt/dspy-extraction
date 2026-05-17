from clinical_extraction.pipeline.sectioning import section_note, select_context


def test_section_note_preserves_offsets_and_canonical_titles():
    note = (
        "Clinic letter\n"
        "Diagnosis: Focal epilepsy.\n"
        "Seizures: Two focal seizures in the last month.\n"
        "Medication\n"
        "Lamotrigine 100 mg twice daily.\n"
    )

    sections = section_note(note)

    assert [section.title for section in sections] == [
        "document",
        "diagnosis",
        "seizures",
        "medication",
    ]
    assert sections[0].text == "Clinic letter\n"
    assert sections[1].text == "Diagnosis: Focal epilepsy.\n"
    assert note[sections[2].start : sections[2].end] == sections[2].text
    assert sections[3].heading == "Medication"


def test_select_context_prefers_field_relevant_sections_with_offsets():
    note = (
        "Diagnosis: Focal epilepsy.\n"
        "Medication: Lamotrigine continued.\n"
        "Seizure frequency: He has had 2 seizures in the last month.\n"
        "Plan: Review in six months.\n"
    )

    contexts = select_context(note, target_field="seizure_frequency_number")

    assert len(contexts) == 1
    assert contexts[0].section == "seizure_frequency"
    assert contexts[0].text == "Seizure frequency: He has had 2 seizures in the last month.\n"
    assert note[contexts[0].start : contexts[0].end] == contexts[0].text


def test_select_context_falls_back_to_keyword_hits_in_unheaded_text():
    note = "The patient reports no seizures since 2024. Medication unchanged."

    contexts = select_context(note, target_field="seizure_frequency_number")

    assert len(contexts) == 1
    assert contexts[0].section == "document"
    assert contexts[0].text == note
