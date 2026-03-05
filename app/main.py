# ----- app/main.py -----
# Entry point — creates the FastAPI application.
# This file wires everything together:
#   - Creates the app
#   - Registers middleware (rate limiting, logging)
#   - Includes routes
#   - Creates DB tables on startup

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import engine, Base
from app.routes import router, limiter

# ── Logging Setup ────────────────────────────────────────
# Logs go to console with timestamps, level, and module name.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup/shutdown) ──────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on app startup and shutdown.
    - Startup: Create all database tables if they don't exist.
    - Shutdown: Cleanup (logging only for now).
    """
    # ── STARTUP ──
    logger.info("🚀 Starting URL Shortener...")
    logger.info(f"   Base URL : {settings.BASE_URL}")
    logger.info(f"   Database : {settings.DATABASE_URL[:30]}...")
    logger.info(f"   Redis    : {settings.REDIS_URL}")

    # Create tables (safe to call multiple times — skips existing tables)
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created/verified")

    yield  # App is running and handling requests here

    # ── SHUTDOWN ──
    logger.info("👋 Shutting down URL Shortener...")


# ── Create FastAPI App ───────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "A production-ready URL shortener API with:\n"
        "- Base62 short code generation\n"
        "- Click tracking & analytics\n"
        "- Redis caching for fast redirects\n"
        "- Rate limiting to prevent abuse\n"
        "- Expiry support\n"
        "- Custom alias support\n\n"
        "Built with FastAPI + PostgreSQL + Redis + Docker."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",       # Swagger UI at http://localhost:8000/docs
    redoc_url="/redoc",     # ReDoc at http://localhost:8000/redoc
)


# ── Rate Limiter Middleware ──────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── Global Exception Handler ────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions and return a clean 500 response."""
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )


# ── Request Logging Middleware ───────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every incoming request and its response status."""
    logger.info(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"← {request.method} {request.url.path} → {response.status_code}")
    return response


# ── Health Check ─────────────────────────────────────────
@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Returns OK if the service is running.",
)
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": settings.APP_NAME}


# ── Include Routes ───────────────────────────────────────
# All URL shortener endpoints are defined in routes.py
app.include_router(router, tags=["URL Shortener"])
