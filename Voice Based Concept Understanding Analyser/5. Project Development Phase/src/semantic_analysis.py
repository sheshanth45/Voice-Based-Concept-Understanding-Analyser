"""
Semantic similarity scoring using Sentence-BERT embeddings.

Compares a user's spoken explanation (transcript) against a reference
explanation for the selected topic, and returns a 0-100 similarity score.
"""
from functools import lru_cache

import config


@lru_cache(maxsize=1)
def _load_model(model_name: str = None):
    """Load (and cache) the Sentence-BERT model. Imported lazily so the rest
    of the app can be explored/tested without sentence-transformers installed."""
    from sentence_transformers import SentenceTransformer  # local import

    return SentenceTransformer(model_name or config.SBERT_MODEL_NAME)


def cosine_similarity(vec_a, vec_b) -> float:
    """Compute cosine similarity between two 1-D numpy vectors."""
    import numpy as np

    a, b = np.asarray(vec_a), np.asarray(vec_b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def compute_semantic_score(user_text: str, reference_text: str, model_name: str = None) -> dict:
    """
    Compare the user's explanation to the reference explanation.

    Returns:
        dict with:
            - similarity: raw cosine similarity (-1 to 1)
            - score: normalized 0-100 score
    """
    if not user_text.strip() or not reference_text.strip():
        return {"similarity": 0.0, "score": 0.0}

    model = _load_model(model_name)
    embeddings = model.encode([user_text, reference_text])
    similarity = cosine_similarity(embeddings[0], embeddings[1])

    # Cosine similarity for sentence embeddings is typically in [0, 1] for
    # related text; clip and rescale to a 0-100 score for readability.
    clipped = max(0.0, min(1.0, similarity))
    score = round(clipped * 100, 2)

    return {"similarity": round(similarity, 4), "score": score}
