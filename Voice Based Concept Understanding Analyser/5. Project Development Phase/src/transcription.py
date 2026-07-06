"""
Speech-to-text transcription using OpenAI Whisper.

The Whisper model is loaded once and cached (module-level) since loading it
is the most expensive step and Streamlit re-runs scripts on every interaction.
"""
from dataclasses import dataclass
from functools import lru_cache
from typing import List

import config


@dataclass
class Segment:
    """A single timed segment of transcribed speech."""
    start: float
    end: float
    text: str


@dataclass
class TranscriptionResult:
    text: str
    segments: List[Segment]
    language: str


@lru_cache(maxsize=1)
def _load_model(model_size: str = None):
    """Load (and cache) the Whisper model. Imported lazily so the rest of the
    app can be explored/tested without requiring torch/whisper installed."""
    import whisper  # local import: heavy dependency

    size = model_size or config.WHISPER_MODEL_SIZE
    return whisper.load_model(size)


def transcribe_audio(audio_path: str, model_size: str = None) -> TranscriptionResult:
    """
    Transcribe an audio file to text.

    Args:
        audio_path: path to a .wav/.mp3/.m4a file on disk.
        model_size: optional override for the Whisper model size.

    Returns:
        TranscriptionResult with full text, timed segments, and detected language.
    """
    model = _load_model(model_size)
    result = model.transcribe(audio_path, verbose=False)

    segments = [
        Segment(start=seg["start"], end=seg["end"], text=seg["text"].strip())
        for seg in result.get("segments", [])
    ]

    return TranscriptionResult(
        text=result.get("text", "").strip(),
        segments=segments,
        language=result.get("language", "unknown"),
    )
