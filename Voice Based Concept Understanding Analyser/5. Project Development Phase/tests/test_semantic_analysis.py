import numpy as np

from src.semantic_analysis import compute_semantic_score, cosine_similarity


def test_cosine_similarity_identical_vectors():
    v = np.array([1.0, 2.0, 3.0])
    assert cosine_similarity(v, v) == 1.0


def test_cosine_similarity_orthogonal_vectors():
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 1.0])
    assert cosine_similarity(a, b) == 0.0


def test_cosine_similarity_zero_vector_is_safe():
    a = np.array([0.0, 0.0])
    b = np.array([1.0, 1.0])
    assert cosine_similarity(a, b) == 0.0


def test_compute_semantic_score_empty_text_returns_zero():
    result = compute_semantic_score("", "some reference text")
    assert result == {"similarity": 0.0, "score": 0.0}


def test_compute_semantic_score_uses_model(monkeypatch):
    """Mock the heavy SentenceTransformer model so this test runs fast and
    without needing the model weights downloaded."""
    import src.semantic_analysis as sa

    class FakeModel:
        def encode(self, texts):
            # Return identical embeddings -> similarity should be 1.0
            return np.array([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]])

    sa._load_model.cache_clear()
    monkeypatch.setattr(sa, "_load_model", lambda model_name=None: FakeModel())

    result = compute_semantic_score("water cycle explanation", "water cycle explanation")
    assert result["score"] == 100.0
