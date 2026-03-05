# ----- app/config.py -----
# Central configuration using pydantic-settings.
# Reads from environment variables (or .env file).

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Docker Compose sets these; for local dev you can use a .env file.
    """

    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "URL Shortener"
    BASE_URL: str = "http://localhost:8000"

    # ── PostgreSQL ───────────────────────────────────────
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/urlshortener"

    # ── Redis ────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600  # seconds (1 hour)

    # ── Rate Limiting ────────────────────────────────────
    RATE_LIMIT: str = "10/minute"  # max 10 shorten requests per minute per IP

    # ── Short Code ───────────────────────────────────────
    SHORT_CODE_LENGTH: int = 6  # characters in generated short code

    class Config:
        env_file = ".env"


# Singleton instance – import this everywhere
settings = Settings()
