"""
Central configuration for VBCUA.

Loads settings from environment variables (via a local .env file if present)
so secrets never need to be hard-coded into source files.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env if present (no-op if it doesn't exist)
load_dotenv()

# --- Paths -------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
REPORTS_DIR = BASE_DIR / "reports"
ASSETS_DIR = BASE_DIR / "assets"

for _dir in (UPLOAD_DIR, REPORTS_DIR, ASSETS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# --- Models --------------------------------------------------------------
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
SBERT_MODEL_NAME = os.getenv("SBERT_MODEL_NAME", "all-MiniLM-L6-v2")

# --- Gemini ----------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")

# --- Database ---------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'vbcua.db'}")

# --- Scoring weights ----------------------------------------------------
SEMANTIC_WEIGHT = float(os.getenv("SEMANTIC_WEIGHT", 0.6))
FLUENCY_WEIGHT = float(os.getenv("FLUENCY_WEIGHT", 0.4))

# Filler words tracked during fluency analysis
FILLER_WORDS = [
    "um", "uh", "uhh", "umm", "erm", "hmm",
    "like", "you know", "sort of", "kind of", "basically", "actually",
    "i mean", "so yeah", "right",
]

# Pause detection thresholds (seconds)
MIN_PAUSE_DURATION = 0.4     # pauses shorter than this are ignored
LONG_PAUSE_DURATION = 1.5    # pauses longer than this are flagged as "long"

# Ideal speaking rate range (words per minute) used for fluency scoring
IDEAL_WPM_MIN = 110
IDEAL_WPM_MAX = 160
