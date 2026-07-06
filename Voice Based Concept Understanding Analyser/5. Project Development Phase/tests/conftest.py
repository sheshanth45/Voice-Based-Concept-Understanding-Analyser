import sys
from pathlib import Path

import pytest

# Ensure the project root is importable when running `pytest` from anywhere.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture()
def in_memory_db(monkeypatch):
    """Point the database module at a throwaway in-memory SQLite DB."""
    from src import database

    database._engine = None
    database._SessionLocal = None
    database.init_db("sqlite:///:memory:")
    yield database
    database._engine = None
    database._SessionLocal = None
