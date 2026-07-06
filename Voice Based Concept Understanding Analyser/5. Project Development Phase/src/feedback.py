"""
AI feedback generation using Google's Gemini API.

If no API key is configured, falls back to a deterministic rule-based
feedback generator so the rest of the pipeline keeps working end-to-end
(useful for local development, demos, and tests without network access).
"""
import config


def _fallback_feedback(topic: str, transcript: str, semantic_score: float, fluency_score: float) -> str:
    """Rule-based feedback used when Gemini is unavailable."""
    lines = [f"Feedback for your explanation of '{topic}':"]

    if semantic_score >= 85:
        lines.append("Your explanation closely matches the key concepts expected for this topic.")
    elif semantic_score >= 60:
        lines.append("Your explanation covers several key ideas, but some important concepts "
                      "appear to be missing or under-explained.")
    else:
        lines.append("Your explanation seems to diverge significantly from the core concepts "
                      "of this topic. Consider reviewing the topic material and trying again.")

    if fluency_score >= 85:
        lines.append("Your delivery was fluent, well-paced, and free of excessive filler words.")
    elif fluency_score >= 60:
        lines.append("Your delivery was reasonably fluent, though there is room to reduce pauses "
                      "or filler words and steady your speaking pace.")
    else:
        lines.append("Your delivery had noticeable pauses, filler words, or pacing issues. "
                      "Practising the explanation aloud a few times should help.")

    lines.append("Tip: try structuring your answer as definition → mechanism → example for "
                  "maximum clarity.")
    return "\n".join(lines)


def _gemini_feedback(topic: str, transcript: str, reference: str, semantic_score: float, fluency_score: float) -> str:
    import google.generativeai as genai

    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel(config.GEMINI_MODEL_NAME)

    prompt = f"""You are an expert tutor evaluating a student's SPOKEN explanation of a concept.

Topic: {topic}

Reference explanation (what a strong answer should cover):
\"\"\"{reference}\"\"\"

Student's transcribed spoken explanation:
\"\"\"{transcript}\"\"\"

Computed scores:
- Semantic similarity to reference: {semantic_score}/100
- Speaking fluency score: {fluency_score}/100

Write concise, encouraging, actionable feedback (4-6 sentences) covering:
1. Conceptual accuracy/completeness vs. the reference.
2. Clarity and fluency of spoken delivery.
3. One specific, concrete suggestion for improvement.
Do not repeat the raw numeric scores back verbatim; refer to them qualitatively.
"""

    response = model.generate_content(prompt)
    return (response.text or "").strip()


def generate_feedback(topic: str, transcript: str, reference: str, semantic_score: float, fluency_score: float) -> str:
    """
    Generate feedback text for a user's spoken explanation.

    Uses Gemini if GEMINI_API_KEY is configured; otherwise falls back to a
    rule-based generator so the app remains fully functional offline.
    """
    if not config.GEMINI_API_KEY:
        return _fallback_feedback(topic, transcript, semantic_score, fluency_score)

    try:
        return _gemini_feedback(topic, transcript, reference, semantic_score, fluency_score)
    except Exception as exc:  # network issues, bad key, quota, etc.
        fallback = _fallback_feedback(topic, transcript, semantic_score, fluency_score)
        return f"{fallback}\n\n(Note: AI feedback service unavailable — {exc})"
