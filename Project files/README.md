# VBCUA — Voice-Based Concept Understanding Analyser

An AI-powered web app that evaluates **spoken conceptual explanations**: it transcribes speech,
measures how semantically close the explanation is to a reference concept, analyses speaking
fluency, generates AI feedback, scores the attempt, and produces a downloadable PDF report.

Built to match the PRD: Streamlit UI, Whisper for STT, Sentence-BERT for semantic similarity,
Librosa for audio/fluency analysis, Gemini for feedback, ReportLab for PDF reports, and
SQLite/PostgreSQL for storage.

---

## 1. Project Structure

```
vbcua/
├── app.py                     # Streamlit UI (entry point)
├── config.py                  # Central config (env vars, model names, paths)
├── requirements.txt
├── .env.example                # Copy to .env and fill in secrets
├── src/
│   ├── transcription.py       # Whisper speech-to-text
│   ├── semantic_analysis.py   # Sentence-BERT similarity scoring
│   ├── audio_analysis.py      # Librosa fluency/pause/filler analysis
│   ├── scoring.py             # Combines sub-scores into final score
│   ├── feedback.py            # Gemini API feedback generation
│   ├── pdf_report.py          # ReportLab PDF report generator
│   └── database.py            # SQLite/PostgreSQL persistence layer
├── data/
│   ├── topics.py              # Sample topics + reference explanations
│   └── uploads/                # Uploaded audio files land here
├── reports/                    # Generated PDF reports land here
├── assets/                     # Generated waveform images, logos, etc.
└── tests/
    ├── conftest.py
    ├── test_semantic_analysis.py
    ├── test_audio_analysis.py
    ├── test_scoring.py
    └── test_database.py
```

## 2. Setup (in VS Code)

1. Open the `vbcua` folder in VS Code (`File → Open Folder…`).
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # on Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   > Whisper and Sentence-BERT (torch-based) are large downloads. First run will also
   > download model weights — make sure you have a stable connection and a few GB free.

4. Configure secrets:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your `GEMINI_API_KEY` (from https://aistudio.google.com/apikey).

5. Run the app:
   ```bash
   streamlit run app.py
   ```

6. Run tests:
   ```bash
   pytest -v
   ```

## 3. How it works (pipeline)

```
User → Streamlit UI → Audio Upload → Whisper (transcript)
     → Sentence-BERT (semantic score) + Librosa (fluency score)
     → Scoring Engine (weighted overall score)
     → Gemini (natural-language feedback)
     → PDF Generator (report) → Database (persisted record) → Dashboard
```

## 4. Configuration knobs (`config.py` / `.env`)

| Variable | Purpose | Default |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key | *(required for AI feedback)* |
| `WHISPER_MODEL_SIZE` | `tiny`/`base`/`small`/`medium`/`large` | `base` |
| `SBERT_MODEL_NAME` | Sentence-BERT model | `all-MiniLM-L6-v2` |
| `DATABASE_URL` | SQLite path or Postgres URL | `sqlite:///vbcua.db` |
| `SEMANTIC_WEIGHT` | Weight of semantic score in final score | `0.6` |
| `FLUENCY_WEIGHT` | Weight of fluency score in final score | `0.4` |

## 5. Notes / Known limitations

- If `GEMINI_API_KEY` is not set, the app falls back to a rule-based feedback generator so the
  rest of the pipeline still works end-to-end.
- Whisper runs on CPU by default; larger model sizes will be slow without a GPU.
- PostgreSQL is supported via `DATABASE_URL`, but SQLite is used out of the box — no server setup
  needed to try the app.

## 6. Future enhancements (from PRD)

Real-time microphone input, multilingual support, emotion detection, user authentication, a
richer analytics dashboard, LMS integration, and cloud deployment.
