# ----- app/cache.py -----
# Redis cache layer for fast short-code → long-url lookups.
#
# FLOW:
#   1. On REDIRECT → check Redis first (fast, ~1ms)
#   2. If cache MISS → query PostgreSQL → store result in Redis
#   3. On URL CREATION → optionally pre-warm the cache
#
# WHY?
#   A popular link may get thousands of clicks/min.
#   Hitting the DB every time is slow & expensive.
#   Redis serves from memory in <1ms.

import json
import logging
from typing import Optional

import redis

from app.config import settings

logger = logging.getLogger(__name__)

# ── Redis Client ─────────────────────────────────────────
# decode_responses=True → returns strings instead of bytes
try:
    redis_client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,
    )
    # Quick check: can we connect?
    redis_client.ping()
    REDIS_AVAILABLE = True
    logger.info("✅ Redis connected successfully")
except Exception as e:
    redis_client = None
    REDIS_AVAILABLE = False
    logger.warning(f"⚠️ Redis not available, running without cache: {e}")


def cache_set(short_code: str, long_url: str, ttl: int = None) -> None:
    """
    Store a short_code → long_url mapping in Redis.

    Parameters
    ----------
    short_code : The short code key (e.g. "abc123")
    long_url   : The original URL value
    ttl        : Time-to-live in seconds (default from settings)
    """
    if not REDIS_AVAILABLE:
        return

    try:
        ttl = ttl or settings.CACHE_TTL
        redis_client.setex(
            name=f"url:{short_code}",
            time=ttl,
            value=long_url,
        )
        logger.debug(f"Cache SET: {short_code} → {long_url[:50]}...")
    except Exception as e:
        logger.error(f"Cache SET failed: {e}")


def cache_get(short_code: str) -> Optional[str]:
    """
    Retrieve the long_url for a short_code from Redis.

    Returns
    -------
    str or None : The original URL if cached, else None (cache miss).
    """
    if not REDIS_AVAILABLE:
        return None

    try:
        result = redis_client.get(f"url:{short_code}")
        if result:
            logger.debug(f"Cache HIT: {short_code}")
        else:
            logger.debug(f"Cache MISS: {short_code}")
        return result
    except Exception as e:
        logger.error(f"Cache GET failed: {e}")
        return None


def cache_delete(short_code: str) -> None:
    """Remove a short_code from the cache (e.g. when URL expires)."""
    if not REDIS_AVAILABLE:
        return

    try:
        redis_client.delete(f"url:{short_code}")
        logger.debug(f"Cache DELETE: {short_code}")
    except Exception as e:
        logger.error(f"Cache DELETE failed: {e}")
