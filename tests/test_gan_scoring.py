from clinical_extraction.gan.scoring import score_gan_frequency_prediction


def test_gan_scoring_separates_raw_exact_from_normalized_and_category_matches():
    score = score_gan_frequency_prediction(
        gold_label="seizure free for 6 month",
        predicted_label="seizure free for 6 months",
    )

    assert score.gold_label != score.predicted_label
    assert score.exact_normalized_match
    assert score.monthly_frequency_match
    assert score.purist_category_match
    assert score.pragmatic_category_match


def test_gan_scoring_allows_different_surface_forms_with_same_monthly_frequency():
    score = score_gan_frequency_prediction(
        gold_label="12 per 1 year",
        predicted_label="1 per 1 month",
    )

    assert not score.exact_normalized_match
    assert score.monthly_frequency_match
    assert score.purist_category_match
    assert score.pragmatic_category_match
