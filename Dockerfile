# ── Stage 1: Python base image ──
FROM python:3.11-slim

# ── Set working directory ──
WORKDIR /app

# ── Install OS-level dependencies (for psycopg2) ──
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ── Copy requirements first (Docker layer caching) ──
# This layer is cached if requirements.txt hasn't changed,
# so "pip install" doesn't re-run on every code change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application code ──
COPY . .

# ── Expose port ──
EXPOSE 8000

# ── Run the app ──
# uvicorn serves the FastAPI app
# --host 0.0.0.0 makes it accessible outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
