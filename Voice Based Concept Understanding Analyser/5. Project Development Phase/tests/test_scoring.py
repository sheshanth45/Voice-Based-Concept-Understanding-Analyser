from src.scoring import compute_overall_score


def test_overall_score_weighted_average():
    result = compute_overall_score(semantic_score=80, fluency_score=60, semantic_weight=0.6, fluency_weight=0.4)
    assert result.overall_score == 72.0
    assert result.semantic_score == 80
    assert result.fluency_score == 60


def test_overall_score_defaults_to_config_weights():
    result = compute_overall_score(semantic_score=100, fluency_score=0)
    # With default weights (0.6 / 0.4), overall should equal 60.
    assert result.overall_score == 60.0


def test_grade_bands():
    assert compute_overall_score(90, 90).grade == "Excellent"
    assert compute_overall_score(75, 75).grade == "Good"
    assert compute_overall_score(55, 55).grade == "Fair"
    assert compute_overall_score(20, 20).grade == "Needs Improvement"


def test_zero_weights_falls_back_to_defaults():
    result = compute_overall_score(50, 50, semantic_weight=0, fluency_weight=0)
    assert result.overall_score == 50.0
