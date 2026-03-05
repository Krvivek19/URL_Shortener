# ----- app/database.py -----
# Database engine & session factory.
# Every request gets its own DB session via the `get_db` dependency.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# ── Engine ───────────────────────────────────────────────
# pool_pre_ping=True keeps connections healthy.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# ── Session Factory ──────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Base class for ORM models ────────────────────────────
Base = declarative_base()


# ── Dependency: yields a DB session per request ──────────
def get_db():
    """
    FastAPI dependency.
    Usage in routes:  db: Session = Depends(get_db)
    Automatically closes the session when the request ends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
