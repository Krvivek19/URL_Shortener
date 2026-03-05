# ----- app/routes.py -----
# API endpoints (thin layer — delegates to service.py).
# Each route validates input via Pydantic schemas,
# calls the service layer, and returns a response.

import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.schemas import URLCreateRequest, URLResponse, URLStatsResponse
from app.service import create_short_url, get_long_url, get_url_stats
from app.config import settings

logger = logging.getLogger(__name__)

# ── Rate Limiter ─────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ── Router ───────────────────────────────────────────────
router = APIRouter()


# ═════════════════════════════════════════════════════════
#  POST /shorten  —  Create a new short URL
# ═════════════════════════════════════════════════════════
@router.post(
    "/shorten",
    response_model=URLResponse,
    status_code=201,
    summary="Shorten a URL",
    description="Takes a long URL and returns a shortened version. "
                "Optionally accepts a custom alias and expiry date.",
    responses={
        201: {"description": "Short URL created successfully"},
        400: {"description": "Invalid URL format"},
        409: {"description": "Custom alias already taken"},
    },
)
@limiter.limit(settings.RATE_LIMIT)
def shorten_url(
    request: Request,           # needed by slowapi for rate limiting
    body: URLCreateRequest,     # validated request body
    db: Session = Depends(get_db),
):
    """
    **Create a short URL.**

    - If the `long_url` was already shortened before → returns the existing short URL (dedup).
    - If `custom_alias` is provided and taken → returns 409 Conflict.
    - Short code is generated using Base62 encoding of the DB record ID.
    """
    url_record = create_short_url(body, db)

    logger.info(f"POST /shorten → {url_record.short_code}")

    return URLResponse(
        short_url=f"{settings.BASE_URL}/{url_record.short_code}",
        short_code=url_record.short_code,
        long_url=url_record.long_url,
        created_at=url_record.created_at,
        expiry_date=url_record.expiry_date,
    )


# ═════════════════════════════════════════════════════════
#  GET /{short_code}  —  Redirect to original URL
# ═════════════════════════════════════════════════════════
@router.get(
    "/{short_code}",
    summary="Redirect to original URL",
    description="Looks up the short code and performs a 302 redirect "
                "to the original long URL. Increments click count.",
    responses={
        302: {"description": "Redirect to original URL"},
        404: {"description": "Short code not found"},
        410: {"description": "Short URL has expired"},
    },
)
def redirect_to_url(
    short_code: str,
    db: Session = Depends(get_db),
):
    """
    **Redirect to the original URL.**

    - Checks Redis cache first (fast path).
    - Falls back to PostgreSQL if cache miss.
    - Returns 404 if not found, 410 if expired.
    - Increments click_count on every successful redirect.
    """
    long_url = get_long_url(short_code, db)

    logger.info(f"GET /{short_code} → 302 Redirect")

    # HTTP 302 Found → browser follows the Location header
    return RedirectResponse(url=long_url, status_code=302)


# ═════════════════════════════════════════════════════════
#  GET /stats/{short_code}  —  Get click stats
# ═════════════════════════════════════════════════════════
@router.get(
    "/stats/{short_code}",
    response_model=URLStatsResponse,
    summary="Get URL statistics",
    description="Returns click count and metadata for a given short code.",
    responses={
        200: {"description": "Stats returned successfully"},
        404: {"description": "Short code not found"},
    },
)
def url_stats(
    short_code: str,
    db: Session = Depends(get_db),
):
    """
    **Get statistics for a short URL.**

    Returns:
    - `click_count`: Total number of redirects
    - `long_url`: The original URL
    - `created_at`: When it was created
    - `expiry_date`: When it expires (if set)
    """
    url_record = get_url_stats(short_code, db)

    logger.info(f"GET /stats/{short_code} → {url_record.click_count} clicks")

    return URLStatsResponse(
        short_code=url_record.short_code,
        long_url=url_record.long_url,
        click_count=url_record.click_count,
        created_at=url_record.created_at,
        expiry_date=url_record.expiry_date,
    )
