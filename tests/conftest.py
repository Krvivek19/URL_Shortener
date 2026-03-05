# ----- tests/conftest.py -----
# Shared test fixtures.
# Sets up an in-memory SQLite database for testing (no PostgreSQL needed).

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# ── Test Database (SQLite in-memory) ────────────────────
# We use SQLite for tests so you don't need PostgreSQL running.
SQLALCHEMY_TEST_URL = "sqlite://"

test_engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Yields a test DB session instead of the real one."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the DB dependency so all routes use the test DB
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """
    Before each test: create all tables.
    After each test: drop all tables (clean slate).
    """
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """FastAPI test client — makes HTTP requests to the app without a server."""
    return TestClient(app)
