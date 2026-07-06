from src.audio_analysis import (
    PauseInfo,
    compute_fluency_score,
    compute_words_per_minute,
    detect_filler_words,
)


def test_detect_filler_words_counts_occurrences():
    transcript = "So, um, photosynthesis is, like, um, the process plants use."
    fillers = detect_filler_words(transcript)
    assert fillers.count("um") == 2
    assert fillers.count("like") == 1


def test_detect_filler_words_no_fillers():
    transcript = "Photosynthesis converts light energy into chemical energy."
    assert detect_filler_words(transcript) == []


def test_compute_words_per_minute():
    assert compute_words_per_minute(150, 60) == 150.0
    assert compute_words_per_minute(0, 60) == 0.0
    assert compute_words_per_minute(100, 0) == 0.0


def test_fluency_score_ideal_conditions_is_high():
    pauses = PauseInfo(count=1, long_pause_count=0, total_pause_duration=0.5, pause_starts=[2.0])
    score = compute_fluency_score(pauses, filler_count=0, wpm=130, word_count=100)
    assert score > 90


def test_fluency_score_penalizes_long_pauses_and_fillers():
    pauses = PauseInfo(count=6, long_pause_count=4, total_pause_duration=8.0, pause_starts=[])
    score = compute_fluency_score(pauses, filler_count=15, wpm=250, word_count=100)
    assert score < 50
