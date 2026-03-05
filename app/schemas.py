# ----- app/schemas.py -----
# Pydantic models for request validation & response serialization.
# FastAPI uses these to auto-validate input and generate Swagger docs.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


# ── REQUEST SCHEMAS ──────────────────────────────────────

class URLCreateRequest(BaseModel):
    """
    Body of POST /shorten.

    Fields
    ------
    long_url     : The full URL to shorten (must be a valid HTTP/HTTPS URL).
    custom_alias : (Optional) User-chosen short code like "my-link".
    expiry_date  : (Optional) ISO datetime after which the link expires.

    Example JSON:
    {
      "long_url": "https://www.google.com/search?q=python",
      "custom_alias": "goog",
      "expiry_date": "2026-12-31T23:59:59"
    }
    """
    long_url: HttpUrl = Field(
        ...,
        description="The original URL to shorten. Must be valid HTTP/HTTPS.",
        examples=["https://www.google.com/search?q=python"],
    )
    custom_alias: Optional[str] = Field(
        None,
        min_length=3,
        max_length=10,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Optional custom short code (3-10 alphanumeric chars, hyphens, underscores).",
        examples=["my-link"],
    )
    expiry_date: Optional[datetime] = Field(
        None,
        description="Optional expiry datetime in ISO format. After this, link returns 410 Gone.",
        examples=["2026-12-31T23:59:59"],
    )


# ── RESPONSE SCHEMAS ────────────────────────────────────

class URLResponse(BaseModel):
    """
    Response from POST /shorten.

    Example:
    {
      "short_url": "http://localhost:8000/abc123",
      "short_code": "abc123",
      "long_url": "https://www.google.com/search?q=python",
      "created_at": "2026-03-05T12:00:00",
      "expiry_date": null
    }
    """
    short_url: str
    short_code: str
    long_url: str
    created_at: datetime
    expiry_date: Optional[datetime] = None

    class Config:
        from_attributes = True  # allows building from SQLAlchemy model


class URLStatsResponse(BaseModel):
    """
    Response from GET /stats/{short_code}.

    Example:
    {
      "short_code": "abc123",
      "long_url": "https://www.google.com/search?q=python",
      "click_count": 25,
      "created_at": "2026-03-05T12:00:00",
      "expiry_date": null
    }
    """
    short_code: str
    long_url: str
    click_count: int
    created_at: datetime
    expiry_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Standard error response body."""
    detail: str
