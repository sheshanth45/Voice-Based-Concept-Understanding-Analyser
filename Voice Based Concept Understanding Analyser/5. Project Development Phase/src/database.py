"""
Persistence layer for VBCUA evaluation records.

Uses SQLAlchemy so the same code works against SQLite (default, zero-setup)
or PostgreSQL (by setting DATABASE_URL), matching the PRD's
"SQLite/PostgreSQL" requirement.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Column, DateTime, Float, Integer, String, Text, create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker

import config

Base = declarative_base()


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String(255), nullable=False)
    transcript = Column(Text, nullable=False)
    semantic_score = Column(Float, nullable=False)
    fluency_score = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)
    grade = Column(String(50), nullable=False)
    feedback = Column(Text, nullable=True)
    words_per_minute = Column(Float, nullable=True)
    filler_count = Column(Integer, nullable=True)
    pause_count = Column(Integer, nullable=True)
    report_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "topic": self.topic,
            "transcript": self.transcript,
            "semantic_score": self.semantic_score,
            "fluency_score": self.fluency_score,
            "overall_score": self.overall_score,
            "grade": self.grade,
            "feedback": self.feedback,
            "words_per_minute": self.words_per_minute,
            "filler_count": self.filler_count,
            "pause_count": self.pause_count,
            "report_path": self.report_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


_engine = None
_SessionLocal = None


def get_engine(database_url: str = None):
    global _engine
    if _engine is None:
        _engine = create_engine(database_url or config.DATABASE_URL, echo=False)
    return _engine


def init_db(database_url: str = None):
    """Create tables if they don't already exist. Safe to call repeatedly."""
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)
    global _SessionLocal
    _SessionLocal = sessionmaker(bind=engine)
    return engine


def get_session():
    global _SessionLocal
    if _SessionLocal is None:
        init_db()
    return _SessionLocal()


def save_evaluation(**kwargs) -> Evaluation:
    """Persist one evaluation record and return the saved ORM object."""
    session = get_session()
    try:
        record = Evaluation(**kwargs)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record
    finally:
        session.close()


def get_all_evaluations(limit: int = 100):
    """Return the most recent evaluations, newest first."""
    session = get_session()
    try:
        return (
            session.query(Evaluation)
            .order_by(Evaluation.created_at.desc())
            .limit(limit)
            .all()
        )
    finally:
        session.close()


def get_evaluations_by_topic(topic: str, limit: int = 100):
    session = get_session()
    try:
        return (
            session.query(Evaluation)
            .filter(Evaluation.topic == topic)
            .order_by(Evaluation.created_at.desc())
            .limit(limit)
            .all()
        )
    finally:
        session.close()
