# 🔗 URL Shortener — Full Project Documentation

> **Tech Stack**: Python 3.11 + FastAPI + PostgreSQL + Redis + Docker  
> **Author**: Vivek Dubey  
> **Purpose**: SDE Portfolio Project — Production-Ready URL Shortener

---

## 📁 Project Structure

```
url-shortener/
├── app/
│   ├── __init__.py        ← Makes 'app' a Python package
│   ├── main.py            ← FastAPI entry point (wires everything)
│   ├── config.py          ← Settings loaded from environment variables
│   ├── database.py        ← SQLAlchemy engine, session, Base
│   ├── models.py          ← ORM model (URL table definition)
│   ├── schemas.py         ← Pydantic models (request/response validation)
│   ├── routes.py          ← API endpoints (thin controllers)
│   ├── service.py         ← Business logic (core operations)
│   ├── utils.py           ← Base62 encoding + helpers
│   └── cache.py           ← Redis cache layer
├── tests/
│   ├── __init__.py
│   ├── conftest.py        ← Test fixtures (SQLite in-memory DB)
│   ├── test_shorten.py    ← Tests for POST /shorten
│   ├── test_redirect.py   ← Tests for GET /{short_code}
│   ├── test_stats.py      ← Tests for GET /stats/{short_code}
│   └── test_utils.py      ← Tests for Base62 encoding
├── Dockerfile             ← Container image definition
├── docker-compose.yml     ← Multi-service orchestration
├── requirements.txt       ← Python dependencies
├── .env                   ← Local env variables
├── .gitignore
└── DOCS.md                ← THIS FILE
```

---

## 🏗️ System Architecture

```
┌──────────┐    HTTP     ┌───────────────────────────────────────────────────┐
│  Client   │───────────▶│                  FastAPI App                      │
│ (Browser, │◀───────────│                                                   │
│  Postman, │            │  ┌─────────┐   ┌───────────┐   ┌──────────────┐  │
│  curl)    │            │  │ routes.py│──▶│ service.py│──▶│ database.py  │  │
│           │            │  │ (API)    │   │ (Logic)   │   │ (PostgreSQL) │  │
│           │            │  └─────────┘   └─────┬─────┘   └──────────────┘  │
│           │            │                      │                            │
│           │            │                      ▼                            │
│           │            │               ┌────────────┐                      │
│           │            │               │  cache.py   │                      │
│           │            │               │  (Redis)    │                      │
│           │            │               └────────────┘                      │
│           │            │                                                   │
│           │            │  Middleware: Rate Limiting, Logging, Error Handler │
│           │            └───────────────────────────────────────────────────┘
└──────────┘

INFRASTRUCTURE (Docker Compose):
┌─────────────────┐  ┌───────────────────┐  ┌─────────────────┐
│  API Container   │  │  PostgreSQL (DB)  │  │   Redis (Cache) │
│  Python + FastAPI│  │  Port 5432        │  │   Port 6379     │
│  Port 8000       │  │  Data persisted   │  │   In-memory     │
└─────────────────┘  └───────────────────┘  └─────────────────┘
```

---

## 🔄 Complete Request Flow

### Flow 1: Creating a Short URL (`POST /shorten`)

```
Client sends POST /shorten with JSON body:
  { "long_url": "https://www.google.com", "custom_alias": "goog" }

    │
    ▼
[1] routes.py → shorten_url()
    - Rate limiter checks: is this IP under 10 req/min? 
    - Pydantic validates the body (URLCreateRequest)
    - If invalid URL → 422 Unprocessable Entity
    │
    ▼
[2] service.py → create_short_url()
    │
    ├─[2a] Check DUPLICATE: Does this long_url already exist in DB?
    │       YES → Return existing record (no new entry created)
    │       NO  → Continue
    │
    ├─[2b] Check CUSTOM ALIAS: Was custom_alias provided?
    │       YES → Is alias already taken?
    │              YES → 409 Conflict
    │              NO  → Use it as short_code
    │       NO  → Generate temporary random code
    │
    ├─[2c] INSERT into PostgreSQL (urls table)
    │       - If IntegrityError (collision) → _retry_create() with new random code
    │
    ├─[2d] If NOT custom alias → Generate Base62(record.id) as final short_code
    │       - UPDATE the record with the Base62 code
    │       - Example: id=123456 → Base62 → "W7e" → padded → "000W7e"
    │
    ├─[2e] CACHE in Redis: key="url:000W7e" value="https://www.google.com"
    │
    └─[2f] Return URL record to routes.py
    │
    ▼
[3] routes.py → Build response:
    {
      "short_url": "http://localhost:8000/000W7e",
      "short_code": "000W7e",
      "long_url": "https://www.google.com",
      "created_at": "2026-03-05T12:00:00",
      "expiry_date": null
    }
    Return with HTTP 201 Created
```

### Flow 2: Redirecting (`GET /{short_code}`)

```
Client visits: http://localhost:8000/abc123

    │
    ▼
[1] routes.py → redirect_to_url("abc123")
    │
    ▼
[2] service.py → get_long_url("abc123")
    │
    ├─[2a] CHECK CACHE (Redis): key="url:abc123"
    │       HIT  → Got the long_url! Increment clicks in DB, return URL
    │       MISS → Continue to DB
    │
    ├─[2b] QUERY DATABASE: SELECT * FROM urls WHERE short_code = 'abc123'
    │       NOT FOUND → 404 Not Found
    │       FOUND → Continue
    │
    ├─[2c] CHECK EXPIRY: Is expiry_date set AND past now?
    │       YES → Delete from cache, return 410 Gone
    │       NO  → Continue
    │
    ├─[2d] INCREMENT click_count += 1 in DB
    │
    ├─[2e] CACHE the result in Redis for next time
    │
    └─[2f] Return long_url
    │
    ▼
[3] routes.py → RedirectResponse(url=long_url, status_code=302)
    Browser follows the redirect to the original URL.
```

### Flow 3: Getting Stats (`GET /stats/{short_code}`)

```
Client requests: GET /stats/abc123

    │
    ▼
[1] routes.py → url_stats("abc123")
    │
    ▼
[2] service.py → get_url_stats("abc123")
    - Query DB for the record
    - NOT FOUND → 404
    - FOUND → Return record
    │
    ▼
[3] routes.py → Return:
    {
      "short_code": "abc123",
      "long_url": "https://www.google.com",
      "click_count": 25,
      "created_at": "2026-03-05T12:00:00",
      "expiry_date": null
    }
```

---

## 📂 File-by-File Explanation

### `app/config.py` — Settings

**What**: Loads configuration from environment variables using Pydantic Settings.  
**Why**: Never hardcode secrets/URLs. Environment variables let you change config per environment (dev/staging/prod) without changing code.

**Key Settings**:
| Setting | Default | Purpose |
|---------|---------|---------|
| `BASE_URL` | `http://localhost:8000` | Prefix for short URLs |
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `CACHE_TTL` | `3600` (1 hour) | How long to cache in Redis |
| `RATE_LIMIT` | `10/minute` | Max API calls per IP |
| `SHORT_CODE_LENGTH` | `6` | Length of generated codes |

---

### `app/database.py` — Database Connection

**What**: Sets up SQLAlchemy engine, session factory, and a FastAPI dependency.  
**Key Concept — Dependency Injection**:
```python
def get_db():
    db = SessionLocal()
    try:
        yield db       # Route uses this DB session
    finally:
        db.close()     # Auto-closes when request ends
```
Routes declare `db: Session = Depends(get_db)` — FastAPI automatically creates and closes a DB session per request.

---

### `app/models.py` — Database Table

**What**: Defines the `urls` table using SQLAlchemy ORM.

```
┌──────────────────────────────────────────────┐
│                    urls                       │
├──────────────┬──────────────┬────────────────┤
│ Column       │ Type         │ Constraint     │
├──────────────┼──────────────┼────────────────┤
│ id           │ BIGINT       │ PRIMARY KEY    │
│ long_url     │ TEXT         │ NOT NULL, INDEX│
│ short_code   │ VARCHAR(10)  │ UNIQUE, INDEX  │
│ created_at   │ TIMESTAMP    │ DEFAULT now()  │
│ click_count  │ INTEGER      │ DEFAULT 0      │
│ expiry_date  │ TIMESTAMP    │ NULLABLE       │
└──────────────┴──────────────┴────────────────┘
```

**Why index `short_code`?** Every redirect does `WHERE short_code = ?`. Without an index, the DB scans every row. With an index, it's O(log n) — milliseconds even with millions of rows.

**Why index `long_url`?** Duplicate detection (`WHERE long_url = ?`) needs to be fast too.

---

### `app/schemas.py` — Request/Response Validation

**What**: Pydantic models that FastAPI uses to:
1. **Validate** incoming JSON (reject bad data automatically)
2. **Serialize** outgoing responses (consistent JSON format)
3. **Generate** Swagger documentation

**Example**: `URLCreateRequest` uses `HttpUrl` type — Pydantic automatically rejects `"not-a-url"` with a 422 error. No manual validation code needed!

---

### `app/utils.py` — Base62 Encoding

**What**: Converts database IDs (integers) to short URL-safe strings.

**How Base62 Works**:
```
Character set: 0-9 a-z A-Z  (62 chars total)

Number → Base62:
    0     → "0"
    9     → "9"
    10    → "a"
    35    → "z"
    36    → "A"
    61    → "Z"
    62    → "10"
    123456 → "W7e"
```

**Why Base62?**
- **Deterministic**: Same ID always → same code (unlike random)
- **Compact**: 6 chars can represent 62^6 = 56 billion URLs
- **No collisions**: Each ID is unique, so each code is unique
- **URL-safe**: No special characters

---

### `app/cache.py` — Redis Caching

**What**: Stores `short_code → long_url` mappings in Redis for fast lookups.

**Why?**
- PostgreSQL query: ~5-10ms
- Redis lookup: ~0.5ms  (10-20x faster)
- A viral link gets millions of clicks — every millisecond matters

**Cache Pattern**: Cache-Aside (Lazy Loading)
```
GET /{short_code}
    → Check Redis
         HIT → Return cached URL (fast!)
         MISS → Query PostgreSQL → Store in Redis → Return URL
```

**Graceful Degradation**: If Redis is down, the app still works — just slower (all queries hit PostgreSQL).

---

### `app/service.py` — Business Logic (THE CORE)

**What**: All the important logic lives here. Routes are thin wrappers.

**Why separate from routes?**
1. **Testable**: You can test logic without HTTP
2. **Reusable**: Multiple routes can call the same logic
3. **Clean**: Routes stay simple, logic stays organized

**Key Functions**:
| Function | Purpose |
|----------|---------|
| `create_short_url()` | Deduplicate → Validate alias → Insert → Base62 → Cache |
| `get_long_url()` | Cache check → DB lookup → Expiry check → Click++ → Return |
| `get_url_stats()` | Simple DB lookup |
| `_retry_create()` | Handle collision (max 5 retries with random codes) |

---

### `app/routes.py` — API Endpoints

**What**: Defines 3 HTTP endpoints. Uses FastAPI decorators.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/shorten` | POST | Create a short URL |
| `/{short_code}` | GET | Redirect to original URL |
| `/stats/{short_code}` | GET | Get click statistics |

**Rate Limiting**: `POST /shorten` is limited to 10 requests/minute per IP using `slowapi`.

---

### `app/main.py` — Application Entry Point

**What**: Creates the FastAPI app and wires everything together.

**What it does on startup**:
1. Configures logging
2. Creates database tables (if they don't exist)
3. Sets up rate limiting middleware
4. Registers the global error handler
5. Adds request logging middleware
6. Includes all routes

**Endpoints auto-available**:
- `/docs` — Swagger UI (interactive API testing)
- `/redoc` — ReDoc (alternative docs)
- `/health` — Health check

---

## 🐳 Docker Setup

### What Docker Does for This Project

```
WITHOUT Docker:                           WITH Docker:
1. Install Python 3.11                    1. docker-compose up --build
2. Install PostgreSQL                     ← That's it!
3. Create database                        
4. Install Redis                          
5. pip install requirements               
6. Set environment variables              
7. Run the app                            
```

### Docker Compose Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `api` | Built from Dockerfile | 8000 | FastAPI application |
| `db` | postgres:16-alpine | 5432 | PostgreSQL database |
| `redis` | redis:7-alpine | 6379 | Redis cache |

### Running

```bash
# Start everything (first time takes ~2 min to download images)
docker-compose up --build

# Stop everything
docker-compose down

# Stop and DELETE all data
docker-compose down -v
```

---

## 🚀 How to Run

### Option 1: Docker (Recommended)
```bash
cd url-shortener
docker-compose up --build
```

### Option 2: Local (Without Docker)
```bash
# Prerequisites: Python 3.11+, PostgreSQL running, Redis running

cd url-shortener
pip install -r requirements.txt

# Create the database
psql -U postgres -c "CREATE DATABASE urlshortener;"

# Run the app
uvicorn app.main:app --reload --port 8000
```

### Verify it's working
```bash
# Health check
curl http://localhost:8000/health

# Open Swagger docs in browser
http://localhost:8000/docs
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_shorten.py -v

# Run with output
pytest tests/ -v -s
```

### Test Setup
Tests use **SQLite in-memory** (no PostgreSQL needed). The `conftest.py` overrides the DB dependency to use a temporary SQLite database that's created before each test and destroyed after.

---

## 🔌 API Usage Examples

### 1. Shorten a URL
```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://www.google.com/search?q=python"}'
```
**Response** (201):
```json
{
  "short_url": "http://localhost:8000/000W7e",
  "short_code": "000W7e",
  "long_url": "https://www.google.com/search?q=python",
  "created_at": "2026-03-05T12:00:00",
  "expiry_date": null
}
```

### 2. Shorten with Custom Alias
```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://github.com/vivek", "custom_alias": "vivek"}'
```

### 3. Shorten with Expiry
```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://temp-link.com", "expiry_date": "2026-12-31T23:59:59"}'
```

### 4. Redirect
```bash
curl -L http://localhost:8000/vivek
# → Redirects to https://github.com/vivek
```

### 5. Get Stats
```bash
curl http://localhost:8000/stats/vivek
```
**Response** (200):
```json
{
  "short_code": "vivek",
  "long_url": "https://github.com/vivek",
  "click_count": 42,
  "created_at": "2026-03-05T12:00:00",
  "expiry_date": null
}
```

---

## 🔑 Key Concepts to Understand for Interview

### 1. Why Base62?
- 62 chars (0-9, a-z, A-Z) → URL-safe
- 6 chars = 62^6 = **56.8 billion** unique URLs
- Deterministic: same ID → same code (no collisions)
- Better than UUID (shorter, predictable)

### 2. Why Redis Cache?
- Redirect is the most common operation (100x more than create)
- DB query ~5ms vs Redis ~0.5ms
- Cache-aside pattern: check cache → miss → DB → fill cache

### 3. Why 3-Layer Architecture?
```
Routes (routes.py)    → Handles HTTP, validation, response format
Service (service.py)  → Business logic, rules, operations
Database (models.py)  → Data persistence, schema
```
This is how real companies structure code. Shows engineering maturity.

### 4. Collision Handling
- Primary: Base62(auto_increment_id) → **mathematically impossible to collide**
- Fallback: Random code + retry up to 5 times
- Safety: UNIQUE constraint in DB catches any edge case

### 5. HTTP Status Codes Used
| Code | Meaning | When |
|------|---------|------|
| 201 | Created | URL shortened successfully |
| 302 | Found (Redirect) | Redirect to original URL |
| 400 | Bad Request | Invalid input |
| 404 | Not Found | Short code doesn't exist |
| 409 | Conflict | Custom alias already taken |
| 410 | Gone | URL has expired |
| 422 | Unprocessable | Pydantic validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Error | Unexpected server error |

### 6. Rate Limiting
- Prevents abuse (someone creating millions of URLs)
- 10 requests/minute per IP address
- Uses `slowapi` library (built on `limits`)

---

## 📊 Database Design Decisions

### Why `BIGINT` for ID?
- `INT` max = ~2 billion → might run out
- `BIGINT` max = 9.2 quintillion → never runs out
- Base62 works with any integer size

### Why index `long_url`?
- Duplicate detection needs: `WHERE long_url = 'https://...'`
- Without index: O(n) full table scan
- With index: O(log n) fast lookup

### Why UNIQUE on `short_code`?
- Even if code has a bug, the DB enforces uniqueness
- Defense in depth: app logic + DB constraint

---

## 🛡️ Error Handling Strategy

```
Layer 1: Pydantic        → Catches invalid JSON, wrong types, bad URLs
Layer 2: Service Logic   → Catches duplicates, expired URLs, conflicts
Layer 3: DB Constraints  → Catches any remaining uniqueness violations
Layer 4: Global Handler  → Catches unhandled exceptions → returns 500
```

---

## 📈 Scalability Discussion (Interview Talking Points)

### Current Design (Single Server)
- Handles ~1000 req/sec easily
- PostgreSQL + Redis on same machine

### How to Scale (If Asked)
1. **Read replicas** — Route redirect queries to read-only DB replicas
2. **Redis cluster** — Distribute cache across multiple nodes
3. **Load balancer** — Run multiple API instances behind Nginx
4. **CDN** — Cache redirects at edge locations
5. **Sharding** — Split DB by short_code prefix (a-m → DB1, n-z → DB2)

### Bottleneck Analysis
- **Write**: Rare (~1% of traffic) → PostgreSQL handles fine
- **Read/Redirect**: ~99% of traffic → Redis absorbs most of it
- **Hot URLs**: Viral links get cached → Redis serves instantly

---

## ✅ Feature Checklist

| # | Feature | Status | File |
|---|---------|--------|------|
| 1 | Create Short URL | ✅ | service.py |
| 2 | Redirect (302) | ✅ | routes.py |
| 3 | Database Storage | ✅ | models.py |
| 4 | URL Validation | ✅ | schemas.py (Pydantic) |
| 5 | Collision Handling | ✅ | service.py |
| 6 | Duplicate URL Handling | ✅ | service.py |
| 7 | Click Tracking | ✅ | service.py |
| 8 | Expiry Support | ✅ | service.py |
| 9 | Custom Alias | ✅ | service.py |
| 10 | Redis Cache | ✅ | cache.py |
| 11 | Rate Limiting | ✅ | routes.py |
| 12 | Docker Support | ✅ | Dockerfile |
| 13 | Proper HTTP Codes | ✅ | routes.py |
| 14 | Logging | ✅ | main.py |
| 15 | Tests | ✅ | tests/ |
| 16 | Clean Architecture | ✅ | 3-layer |

**Resume Impact: 9/10** ⭐

---

## 🔍 Learning Path (Recommended Order)

1. **Day 1**: Read `schemas.py` + `models.py` — understand data structures
2. **Day 1**: Read `utils.py` — understand Base62 (try it on paper!)
3. **Day 2**: Read `service.py` — understand the core logic flows
4. **Day 2**: Read `routes.py` — understand how HTTP maps to logic
5. **Day 3**: Read `cache.py` — understand caching strategy
6. **Day 3**: Read `main.py` — understand how the app starts
7. **Day 4**: Run it with Docker, test every endpoint
8. **Day 5**: Read tests, run them, understand edge cases
9. **Day 6-7**: Modify something (add a feature, break something, fix it)

> **The best way to understand code is to break it and fix it.**
