"""
Scoring engine: combines the semantic similarity score and the fluency score
into a single overall score, plus a human-readable grade band.
"""
from dataclasses import dataclass

import config


@dataclass
class OverallScore:
    semantic_score: float
    fluency_score: float
    overall_score: float
    grade: str


def _grade_for(score: float) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 50:
        return "Fair"
    return "Needs Improvement"


def compute_overall_score(
    semantic_score: float,
    fluency_score: float,
    semantic_weight: float = None,
    fluency_weight: float = None,
) -> OverallScore:
    """
    Weighted combination of semantic understanding and speaking fluency.
    Weights default to config values and are normalized to sum to 1.0.
    """
    w_sem = semantic_weight if semantic_weight is not None else config.SEMANTIC_WEIGHT
    w_flu = fluency_weight if fluency_weight is not None else config.FLUENCY_WEIGHT

    total_weight = w_sem + w_flu
    if total_weight <= 0:
        w_sem, w_flu = 0.6, 0.4
    else:
        w_sem, w_flu = w_sem / total_weight, w_flu / total_weight

    overall = round(semantic_score * w_sem + fluency_score * w_flu, 2)

    return OverallScore(
        semantic_score=semantic_score,
        fluency_score=fluency_score,
        overall_score=overall,
        grade=_grade_for(overall),
    )
