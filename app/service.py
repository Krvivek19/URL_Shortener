# ----- app/service.py -----
# Business logic layer — ALL the core operations live here.
# Routes call service functions; service talks to DB and cache.
# This separation keeps routes thin and logic testable.

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models import URL
from app.schemas import URLCreateRequest
from app.utils import encode_base62, generate_random_code
from app.cache import cache_get, cache_set, cache_delete
from app.config import settings

logger = logging.getLogger(__name__)

# =====================================================================
#  1. CREATE SHORT URL
# =====================================================================

def create_short_url(request: URLCreateRequest, db: Session) -> URL:
    """
    Main function to shorten a URL.

    Steps:
    ------
    1. Check if this long_url already exists → return existing (dedup).
    2. If custom_alias provided → check it's not taken.
    3. Create DB record with a temporary short_code.
    4. Generate Base62 code from the new record's ID.
    5. Update the record with the final short_code.
    6. Cache the mapping in Redis.
    7. Return the URL object.
    """
    long_url_str = str(request.long_url)

    # ── Step 1: Duplicate check ──────────────────────────
    # If this exact long_url was already shortened, return that.
    # This avoids creating multiple short codes for the same URL.
    existing = db.query(URL).filter(URL.long_url == long_url_str).first()
    if existing:
        logger.info(f"Duplicate URL found: {existing.short_code}")
        return existing

    # ── Step 2: Custom alias handling ────────────────────
    if request.custom_alias:
        # Check if the alias is already taken
        alias_exists = db.query(URL).filter(URL.short_code == request.custom_alias).first()
        if alias_exists:
            raise HTTPException(
                status_code=409,
                detail=f"Custom alias '{request.custom_alias}' is already taken."
            )
        short_code = request.custom_alias
    else:
        # Temporary placeholder — will be replaced by Base62(id) after insert
        short_code = generate_random_code(settings.SHORT_CODE_LENGTH)

    # ── Step 3: Create DB record ─────────────────────────
    url_record = URL(
        long_url=long_url_str,
        short_code=short_code,
        expiry_date=request.expiry_date,
    )
    db.add(url_record)

    try:
        db.commit()
        db.refresh(url_record)
    except IntegrityError:
        # short_code collision (very rare with random codes)
        db.rollback()
        logger.warning(f"Collision on short_code '{short_code}', retrying...")
        return _retry_create(request, db)

    # ── Step 4 & 5: Generate Base62 from ID (if not custom) ──
    if not request.custom_alias:
        base62_code = encode_base62(url_record.id)
        # Pad to minimum length if too short
        while len(base62_code) < settings.SHORT_CODE_LENGTH:
            base62_code = "0" + base62_code

        url_record.short_code = base62_code
        try:
            db.commit()
            db.refresh(url_record)
        except IntegrityError:
            db.rollback()
            logger.warning(f"Collision on Base62 code '{base62_code}', retrying...")
            return _retry_create(request, db)

    # ── Step 6: Cache in Redis ───────────────────────────
    cache_set(url_record.short_code, url_record.long_url)

    logger.info(f"Created short URL: {url_record.short_code} → {long_url_str[:80]}")
    return url_record


def _retry_create(request: URLCreateRequest, db: Session, max_retries: int = 5) -> URL:
    """
    Retry creating a short URL with a new random code.
    This handles the extremely rare case of a collision.
    """
    for attempt in range(max_retries):
        new_code = generate_random_code(settings.SHORT_CODE_LENGTH)
        url_record = URL(
            long_url=str(request.long_url),
            short_code=new_code,
            expiry_date=request.expiry_date,
        )
        db.add(url_record)
        try:
            db.commit()
            db.refresh(url_record)
            cache_set(url_record.short_code, url_record.long_url)
            logger.info(f"Retry succeeded on attempt {attempt + 1}: {new_code}")
            return url_record
        except IntegrityError:
            db.rollback()
            logger.warning(f"Retry collision attempt {attempt + 1}")
            continue

    raise HTTPException(
        status_code=500,
        detail="Failed to generate a unique short code after multiple attempts."
    )


# =====================================================================
#  2. REDIRECT — Lookup short_code and return the original URL
# =====================================================================

def get_long_url(short_code: str, db: Session) -> str:
    """
    Lookup a short_code and return the original long_url.

    Steps:
    ------
    1. Check Redis cache first (fast path).
    2. If cache miss → query PostgreSQL.
    3. If found → check expiry.
    4. Increment click_count.
    5. Return long_url.

    Raises:
    -------
    404 if short_code not found.
    410 if short_code has expired.
    """
    # ── Step 1: Check cache ──────────────────────────────
    cached_url = cache_get(short_code)
    if cached_url:
        # Still need to increment click_count in DB
        _increment_clicks(short_code, db)
        return cached_url

    # ── Step 2: Query database ───────────────────────────
    url_record = db.query(URL).filter(URL.short_code == short_code).first()
    if not url_record:
        raise HTTPException(status_code=404, detail="Short URL not found.")

    # ── Step 3: Check expiry ─────────────────────────────
    if url_record.expiry_date:
        now = datetime.now(timezone.utc)
        expiry = url_record.expiry_date
        # Make expiry timezone-aware if it isn't
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if now > expiry:
            cache_delete(short_code)
            raise HTTPException(status_code=410, detail="This short URL has expired.")

    # ── Step 4: Increment clicks ─────────────────────────
    url_record.click_count += 1
    db.commit()

    # ── Step 5: Cache for next time and return ───────────
    cache_set(short_code, url_record.long_url)
    logger.info(f"Redirect: {short_code} → {url_record.long_url[:80]} (clicks: {url_record.click_count})")
    return url_record.long_url


def _increment_clicks(short_code: str, db: Session) -> None:
    """Increment click_count in the database (called when serving from cache)."""
    url_record = db.query(URL).filter(URL.short_code == short_code).first()
    if url_record:
        url_record.click_count += 1
        db.commit()


# =====================================================================
#  3. STATS — Return analytics for a short_code
# =====================================================================

def get_url_stats(short_code: str, db: Session) -> URL:
    """
    Return statistics for a given short_code.

    Returns the full URL record including click_count, created_at, etc.

    Raises:
    -------
    404 if short_code not found.
    """
    url_record = db.query(URL).filter(URL.short_code == short_code).first()
    if not url_record:
        raise HTTPException(status_code=404, detail="Short URL not found.")

    logger.info(f"Stats requested: {short_code} (clicks: {url_record.click_count})")
    return url_record
