"""
Audio feature extraction and fluency analysis using Librosa.

Covers: pause detection (via silence intervals), filler word detection
(via the transcript + timed segments), speaking rate, and waveform
visualization for the PDF report / dashboard.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import config


@dataclass
class PauseInfo:
    count: int
    long_pause_count: int
    total_pause_duration: float
    pause_starts: List[float] = field(default_factory=list)


@dataclass
class FluencyResult:
    duration_seconds: float
    word_count: int
    words_per_minute: float
    filler_count: int
    filler_words_found: List[str]
    pauses: PauseInfo
    fluency_score: float  # 0-100


def load_audio(audio_path: str):
    import librosa

    y, sr = librosa.load(audio_path, sr=None, mono=True)
    return y, sr


def detect_pauses(y, sr, min_pause_duration: float = None, long_pause_duration: float = None) -> PauseInfo:
    """
    Detect silent intervals (pauses) in the audio using librosa's
    energy-based non-silent-interval splitter.
    """
    import librosa

    min_pause_duration = min_pause_duration or config.MIN_PAUSE_DURATION
    long_pause_duration = long_pause_duration or config.LONG_PAUSE_DURATION

    # Non-silent intervals (in samples); gaps between them are pauses.
    non_silent = librosa.effects.split(y, top_db=30)

    pause_count = 0
    long_pause_count = 0
    total_pause_duration = 0.0
    pause_starts = []

    for i in range(1, len(non_silent)):
        prev_end = non_silent[i - 1][1]
        cur_start = non_silent[i][0]
        gap_duration = (cur_start - prev_end) / sr

        if gap_duration >= min_pause_duration:
            pause_count += 1
            total_pause_duration += gap_duration
            pause_starts.append(round(prev_end / sr, 2))
            if gap_duration >= long_pause_duration:
                long_pause_count += 1

    return PauseInfo(
        count=pause_count,
        long_pause_count=long_pause_count,
        total_pause_duration=round(total_pause_duration, 2),
        pause_starts=pause_starts,
    )


def detect_filler_words(transcript: str) -> List[str]:
    """Return the list of filler-word occurrences found in the transcript.

    Uses regex word boundaries so punctuation (commas, periods, etc.) doesn't
    prevent a match, while still avoiding partial-word false positives
    (e.g. "like" inside "unlike").
    """
    import re

    text = transcript.lower()
    found = []
    for filler in config.FILLER_WORDS:
        pattern = r"\b" + re.escape(filler) + r"\b"
        matches = re.findall(pattern, text)
        found.extend(matches)
    return found


def compute_words_per_minute(word_count: int, duration_seconds: float) -> float:
    if duration_seconds <= 0:
        return 0.0
    return round(word_count / (duration_seconds / 60.0), 1)


def _rate_score(wpm: float) -> float:
    """Score speaking rate: 100 if within the ideal band, decaying outside it."""
    lo, hi = config.IDEAL_WPM_MIN, config.IDEAL_WPM_MAX
    if lo <= wpm <= hi:
        return 100.0
    distance = (lo - wpm) if wpm < lo else (wpm - hi)
    # Lose 2 points per wpm outside the ideal band, floor at 0.
    return max(0.0, 100.0 - distance * 2)


def compute_fluency_score(pauses: PauseInfo, filler_count: int, wpm: float, word_count: int) -> float:
    """
    Combine pause, filler, and speaking-rate signals into a single 0-100
    fluency score. Weights are heuristic and easy to retune.
    """
    rate_score = _rate_score(wpm)

    # Penalize long pauses more than short ones.
    pause_penalty = min(40.0, pauses.long_pause_count * 8 + max(0, pauses.count - pauses.long_pause_count) * 3)
    pause_score = max(0.0, 100.0 - pause_penalty)

    # Penalize fillers relative to how much was said (per 100 words).
    filler_rate = (filler_count / word_count * 100) if word_count else 0
    filler_score = max(0.0, 100.0 - filler_rate * 10)

    fluency_score = 0.4 * rate_score + 0.3 * pause_score + 0.3 * filler_score
    return round(fluency_score, 2)


def analyze_fluency(audio_path: str, transcript: str) -> FluencyResult:
    """Run the full fluency analysis pipeline for one recording."""
    import librosa

    y, sr = load_audio(audio_path)
    duration = librosa.get_duration(y=y, sr=sr)

    words = transcript.split()
    word_count = len(words)
    wpm = compute_words_per_minute(word_count, duration)

    pauses = detect_pauses(y, sr)
    fillers = detect_filler_words(transcript)

    fluency_score = compute_fluency_score(pauses, len(fillers), wpm, word_count)

    return FluencyResult(
        duration_seconds=round(duration, 2),
        word_count=word_count,
        words_per_minute=wpm,
        filler_count=len(fillers),
        filler_words_found=fillers,
        pauses=pauses,
        fluency_score=fluency_score,
    )


def generate_waveform_image(audio_path: str, output_path: Optional[str] = None) -> str:
    """
    Render a waveform plot for the given audio file and save it as a PNG.
    Returns the path to the saved image.
    """
    import librosa
    import librosa.display
    import matplotlib

    matplotlib.use("Agg")  # headless backend, safe for Streamlit/server use
    import matplotlib.pyplot as plt

    y, sr = load_audio(audio_path)

    if output_path is None:
        stem = Path(audio_path).stem
        output_path = str(config.ASSETS_DIR / f"{stem}_waveform.png")

    fig, ax = plt.subplots(figsize=(8, 2.2))
    librosa.display.waveshow(y, sr=sr, ax=ax, color="#4C6EF5")
    ax.set_title("Waveform")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path
