# 🔗 URL Shortener API

> **A production-ready URL shortener built with Python, FastAPI, PostgreSQL, and Redis**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-red.svg)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

## 🎯 What is This?

A **professional URL shortener** that converts long URLs into short, shareable links. Perfect for:
- 📱 Sharing links on social media (Twitter, Instagram)
- 📊 Tracking click analytics
- 🔗 Creating memorable branded links
- 💼 Enterprise link management

**Example:**
```
Long:  https://www.youtube.com/watch?v=dQw4w9WgXcQ
Short: http://localhost:8000/abc123
```

**Try it now:** Once running, visit http://localhost:8000/docs for interactive API playground!

---

## ✨ Features

- ✅ **Shorten URLs** with Base62 encoding (deterministic, no collisions)
- ✅ **Custom Aliases** (e.g., `/vivek` instead of `/abc123`)
- ✅ **Click Tracking** with detailed analytics
- ✅ **Expiry Support** (URLs can auto-expire)
- ✅ **Redis Caching** for blazing-fast redirects (<1ms)
- ✅ **Rate Limiting** to prevent abuse
- ✅ **Duplicate Detection** (same URL → same short code)
- ✅ **Docker Support** (one command to run everything)
- ✅ **Comprehensive Tests** (15+ test cases)
- ✅ **Auto-generated API Docs** (Swagger + ReDoc)

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** installed
- **Git** (optional, for cloning)
- **Docker Desktop** (for Docker method only)

---

## 🎯 Three Ways to Run

### Method 1: Local Development (SQLite - No Database Setup Required) ⚡

**Perfect for:** Quick testing, development, demos

```bash
# 1. Clone or download the repository
git clone https://github.com/krvivek19/URL-Shortener.git
cd url-shortener

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# On Windows:
.\.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**✅ Done!** Open http://localhost:8000/docs

**Features:**
- ✅ Uses SQLite (no PostgreSQL needed)
- ✅ Works without Redis (slight performance impact)
- ⚠️ Data stored in `urlshortener.db` file

---

### Method 2: Docker (Full Production Stack) 🐳

**Perfect for:** Production-like environment, PostgreSQL + Redis

**Prerequisites:** Docker Desktop installed and running

```bash
# 1. Clone the repository
git clone https://github.com/krvivek19/URL-Shortener.git
cd url-shortener

# 2. Start all services (API + PostgreSQL + Redis)
docker-compose up --build

# Wait for: "Application startup complete"
```

**✅ Done!** Open http://localhost:8000/docs

**What's running:**
- 🟢 FastAPI server on port 8000
- 🟢 PostgreSQL database on port 5432
- 🟢 Redis cache on port 6379

**Stop the services:**
```bash
# Press Ctrl+C, then:
docker-compose down
```

---

### Method 3: Local with PostgreSQL + Redis (Advanced) 🛠️

**Perfect for:** Developers who want full control

**Prerequisites:**
- PostgreSQL 16+ installed and running
- Redis 7+ installed and running

```bash
# 1. Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE urlshortener;"

# 2. Set environment variables
# On Windows PowerShell:
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5432/urlshortener"
$env:REDIS_URL="redis://localhost:6379/0"
$env:BASE_URL="http://localhost:8000"

# On macOS/Linux:
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/urlshortener"
export REDIS_URL="redis://localhost:6379/0"
export BASE_URL="http://localhost:8000"

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**✅ Done!** Open http://localhost:8000/docs

---

## 📖 User Guide

### Accessing the API

Once the server is running, you have **three ways** to interact with it:

#### 1. Swagger UI (Interactive Documentation) 🎨
Open http://localhost:8000/docs in your browser
- Click on any endpoint to expand
- Click "Try it out" to test directly
- No coding required!

#### 2. ReDoc (Alternative Documentation) 📚
Open http://localhost:8000/redoc
- Clean, searchable documentation
- See all schemas and examples

#### 3. Command Line (curl/PowerShell) 💻
See examples below

---

### API Usage Examples

#### 📝 Create Short URL (Basic)

**Using Swagger UI:**
1. Open http://localhost:8000/docs
2. Click **POST /shorten** → **Try it out**
3. Replace the request body:
   ```json
   {
     "long_url": "https://www.google.com/search?q=fastapi"
   }
   ```
4. Click **Execute**

**Using curl (Windows PowerShell):**
```powershell
$body = '{"long_url":"https://www.google.com/search?q=fastapi"}'
Invoke-RestMethod -Uri "http://localhost:8000/shorten" -Method Post -Body $body -ContentType "application/json"
```

**Using curl (Linux/macOS):**
```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://www.google.com/search?q=fastapi"}'
```

**Response:**
```json
{
  "short_url": "http://localhost:8000/000002",
  "short_code": "000002",
  "long_url": "https://www.google.com/search?q=fastapi",
  "created_at": "2026-03-21T03:00:00",
  "expiry_date": null
}
```

---

#### 🎯 Create Short URL with Custom Alias

**Request:**
```json
{
  "long_url": "https://github.com/krvivek19/URL-Shortener",
  "custom_alias": "my-project"
}
```

**Response:**
```json
{
  "short_url": "http://localhost:8000/my-project",
  "short_code": "my-project",
  "long_url": "https://github.com/krvivek19/URL-Shortener",
  "created_at": "2026-03-21T03:00:00",
  "expiry_date": null
}
```

---

#### ⏰ Create Short URL with Expiry Date

**Request:**
```json
{
  "long_url": "https://example.com/limited-offer",
  "expiry_date": "2026-12-31T23:59:59"
}
```

**Response:**
```json
{
  "short_url": "http://localhost:8000/000003",
  "short_code": "000003",
  "long_url": "https://example.com/limited-offer",
  "created_at": "2026-03-21T03:00:00",
  "expiry_date": "2026-12-31T23:59:59"
}
```

---

#### 🔗 Use the Short URL (Redirect)

Simply open the short URL in a browser or click it:
```
http://localhost:8000/000002
```

**Or test via PowerShell:**
```powershell
# Check redirect (won't follow it)
Invoke-WebRequest -Uri "http://localhost:8000/000002" -MaximumRedirection 0 -UseBasicParsing -ErrorAction SilentlyContinue
```

**cURL:**
```bash
# Follow the redirect
curl -L http://localhost:8000/000002
```

---

#### 📊 Get Statistics

**Using Swagger:**
1. Click **GET /stats/{short_code}** → **Try it out**
2. Enter short code: `000002`
3. Click **Execute**

**Using PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/stats/000002"
```

**Response:**
```json
{
  "short_code": "000002",
  "long_url": "https://www.google.com/search?q=fastapi",
  "click_count": 5,
  "created_at": "2026-03-21T03:00:00",
  "expiry_date": null
}
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root or set environment variables:

```bash
# Base URL for short links (change when deployed)
BASE_URL=http://localhost:8000

# Database connection (SQLite by default for local dev)
DATABASE_URL=sqlite:///./urlshortener.db

# For PostgreSQL:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/urlshortener

# Redis cache (optional, app works without it)
REDIS_URL=redis://localhost:6379/0

# Cache time-to-live (seconds)
CACHE_TTL=3600

# Rate limiting (requests per minute per IP)
RATE_LIMIT=10/minute

# Length of auto-generated short codes
SHORT_CODE_LENGTH=6
```

### Configuration for Different Environments

**Local Development (SQLite):**
```env
DATABASE_URL=sqlite:///./urlshortener.db
REDIS_URL=redis://localhost:6379/0
BASE_URL=http://localhost:8000
```

**Production (Render/Heroku):**
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=rediss://user:pass@host:6380
BASE_URL=https://your-app.onrender.com
```

---

## 📖 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/shorten` | Create a short URL |
| `GET` | `/{short_code}` | Redirect to original URL |
| `GET` | `/stats/{short_code}` | Get click statistics |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Interactive API documentation |

### Example Usage

**1. Shorten a URL**
```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://www.google.com"}'
```

**Response:**
```json
{
  "short_url": "http://localhost:8000/000W7e",
  "short_code": "000W7e",
  "long_url": "https://www.google.com",
  "created_at": "2026-03-05T12:00:00",
  "expiry_date": null
}
```

**2. Redirect**
```bash
curl -L http://localhost:8000/000W7e
# → Redirects to https://www.google.com
```

**3. Get Statistics**
```bash
curl http://localhost:8000/stats/000W7e
```

**Response:**
```json
{
  "short_code": "000W7e",
  "long_url": "https://www.google.com",
  "click_count": 42,
  "created_at": "2026-03-05T12:00:00",
  "expiry_date": null
}
```

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### 1. Server Won't Start

**Error:** `Address already in use`

**Solution:** Port 8000 is occupied. Use a different port:
```bash
python -m uvicorn app.main:app --reload --port 8001
```

Or kill the existing process:
```powershell
# Windows
Get-Process python | Stop-Process -Force

# Linux/macOS
lsof -ti:8000 | xargs kill -9
```

---

#### 2. Redis Warning

**Message:** `⚠️ Redis not available, running without cache`

**Impact:** App still works! Redirects will be slightly slower (~50-100ms vs ~1ms)

**Solution (Optional):**
- Install Redis locally, OR
- Use Docker method, OR
- Ignore it (SQLite-only mode works fine)

---

#### 3. Database Connection Error

**Error:** `connection refused` or `password authentication failed`

**Solutions:**

**For SQLite (default):**
- No action needed! Database file auto-created

**For PostgreSQL:**
```bash
# Check PostgreSQL is running
# Windows:
Get-Service postgresql*

# Linux:
sudo systemctl status postgresql

# Start PostgreSQL if stopped
# Windows: Start-Service postgresql
# Linux: sudo systemctl start postgresql

# Verify connection
psql -U postgres -c "SELECT version();"
```

---

#### 4. Module Not Found Error

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Make sure virtual environment is activated
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # Linux/macOS

# Reinstall dependencies
pip install -r requirements.txt
```

---

#### 5. Docker Build Fails

**Error:** `failed to resolve reference "docker.io/library/postgres"`

**Cause:** Corporate proxy or network restrictions

**Solution:**
1. Open Docker Desktop → Settings → Resources → Proxies
2. Uncheck "Use system proxy settings"
3. Clear all proxy fields
4. Click "Apply & Restart"
5. Try again: `docker-compose up --build`

**Alternative:** Use Method 1 (Local SQLite) instead

---

#### 6. Permission Denied on Linux

**Error:** `Permission denied: 'urlshortener.db'`

**Solution:**
```bash
# Give write permissions to current directory
chmod 777 .

# Or run with sudo (not recommended for production)
sudo python -m uvicorn app.main:app
```

---

#### 7. Custom Alias Already Taken

**Error:** `409 - Custom alias 'my-link' is already taken`

**Cause:** That short code exists in the database

**Solutions:**
- Choose a different alias, OR
- Delete the database file and restart (dev only):
  ```bash
  rm urlshortener.db
  python -m uvicorn app.main:app
  ```

---

## ✅ Verification Steps

Test if everything works:

```powershell
# 1. Check server is running
Invoke-RestMethod -Uri "http://localhost:8000/docs"

# 2. Create a short URL
$body = '{"long_url":"https://www.google.com"}'
$result = Invoke-RestMethod -Uri "http://localhost:8000/shorten" -Method Post -Body $body -ContentType "application/json"
Write-Host "Short URL created: $($result.short_url)"

# 3. Test redirect
Invoke-WebRequest -Uri $result.short_url -MaximumRedirection 0 -UseBasicParsing -ErrorAction SilentlyContinue

# 4. Check stats
Invoke-RestMethod -Uri "http://localhost:8000/stats/$($result.short_code)"
```

**Expected Output:**
```
Short URL created: http://localhost:8000/000001
StatusCode: 302 (Redirect)
click_count: 1
```

---

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│      FastAPI (routes.py)        │  ← Rate Limiting
├─────────────────────────────────┤
│   Business Logic (service.py)   │  ← Deduplication, Base62
├─────────────────────────────────┤
│   Cache Layer (cache.py)        │  ← Redis
├─────────────────────────────────┤
│   Database (models.py)          │  ← PostgreSQL
└─────────────────────────────────┘
```

**3-Layer Architecture:**
- **Routes**: HTTP handling, validation, responses
- **Service**: Business logic, deduplication, click tracking
- **Database**: Data persistence with SQLAlchemy ORM

---

## 🧪 Testing

### Running Tests

**Install test dependencies first:**
```bash
# Should already be installed from requirements.txt
pip install pytest pytest-asyncio httpx
```

**Run all tests:**
```bash
# Basic run
pytest tests/ -v

# With detailed output
pytest tests/ -vv

# With coverage report
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_shorten.py -v

# Run specific test function
pytest tests/test_shorten.py::test_shorten_url_success -v
```

**View coverage report:**
```bash
# After running with --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Structure

```
tests/
├── conftest.py          # Test fixtures and setup
├── test_shorten.py      # URL shortening tests
├── test_redirect.py     # Redirect functionality tests
├── test_stats.py        # Statistics endpoint tests
└── test_utils.py        # Utility function tests
```

### Test Coverage

**15+ test cases covering:**

✅ **URL Shortening (`test_shorten.py`):**
- Valid URL with auto-generated code
- Custom alias creation
- URL with expiry date
- Invalid URL format
- Duplicate URL detection
- Alias conflict (409 error)

✅ **Redirects (`test_redirect.py`):**
- Successful redirect (302)
- Short code not found (404)
- Expired URL (410)
- Click count increment

✅ **Statistics (`test_stats.py`):**
- Get stats for existing URL
- Stats for non-existent URL (404)
- Click count accuracy

✅ **Utilities (`test_utils.py`):**
- Base62 encoding/decoding
- Random code generation
- Edge cases (zero, large numbers)

### Manual Testing Checklist

```bash
# 1. Start the server
python -m uvicorn app.main:app --port 8000

# 2. Test basic shortening
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://www.example.com"}'

# 3. Test redirect (should return 302)
curl -I http://localhost:8000/[SHORT_CODE]

# 4. Test stats
curl http://localhost:8000/stats/[SHORT_CODE]

# 5. Test custom alias
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://www.example.com", "custom_alias": "test"}'

# 6. Test duplicate (should return same short code)
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://www.example.com"}'

# 7. Test expiry
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://www.example.com", "expiry_date": "2020-01-01T00:00:00"}'
# Then try to access it (should return 410)
curl -I http://localhost:8000/[SHORT_CODE]
```

---

## 🛠️ Tech Stack

| Component | Technology | Why? |
|-----------|-----------|------|
| **Framework** | FastAPI | Async, auto-docs, type-safe |
| **Database** | PostgreSQL | ACID, constraints, proven at scale |
| **Cache** | Redis | Sub-millisecond lookups |
| **ORM** | SQLAlchemy 2.0 | Clean models, migrations |
| **Validation** | Pydantic | Auto-validation, zero boilerplate |
| **Rate Limiting** | slowapi | Prevent abuse |
| **Containerization** | Docker Compose | One-command setup |
| **Testing** | pytest + httpx | Fast, reliable tests |

---

## 📂 Project Structure

```
url-shortener/
├── app/
│   ├── main.py          # FastAPI app entry point
│   ├── config.py        # Settings (env variables)
│   ├── database.py      # SQLAlchemy setup
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic models
│   ├── routes.py        # API endpoints
│   ├── service.py       # Business logic
│   ├── utils.py         # Base62 encoding
│   └── cache.py         # Redis cache layer
├── tests/               # Test suite
├── Dockerfile           # Container image
├── docker-compose.yml   # Multi-service orchestration
├── requirements.txt     # Python dependencies
└── DOCS.md             # Detailed documentation
```

---

## 🔑 Key Concepts

### Base62 Encoding
- Converts database IDs to short, URL-safe strings
- Character set: `0-9a-zA-Z` (62 characters)
- 6 characters = 62^6 = **56.8 billion** unique URLs
- Example: ID `123456` → `W7e`

### Caching Strategy
- **Cache-Aside Pattern**: Check cache → miss → DB → fill cache
- Redis stores `short_code → long_url` mappings
- 10-20x faster than database queries
- Graceful degradation if Redis is down

### Collision Handling
- **Primary**: Base62 of auto-increment ID → mathematically guaranteed unique
- **Fallback**: Random code + retry (up to 5 attempts)
- **Safety**: `UNIQUE` constraint in database

---

## 📋 Quick Reference

### Common Commands

**Starting the Server:**
```bash
# Local with SQLite (simplest)
python -m uvicorn app.main:app --reload --port 8000

# With Docker (full stack)
docker-compose up --build

# Stop Docker
docker-compose down
```

**Creating Short URLs:**
```powershell
# Windows PowerShell
$body = '{"long_url":"https://example.com"}'
Invoke-RestMethod -Uri "http://localhost:8000/shorten" -Method Post -Body $body -ContentType "application/json"

# Linux/macOS bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"long_url":"https://example.com"}'
```

**Testing Redirects:**
```bash
# Windows
Invoke-WebRequest -Uri "http://localhost:8000/SHORT_CODE" -MaximumRedirection 0 -UseBasicParsing

# Linux/macOS
curl -I http://localhost:8000/SHORT_CODE
```

**Getting Stats:**
```bash
# Windows
Invoke-RestMethod -Uri "http://localhost:8000/stats/SHORT_CODE"

# Linux/macOS
curl http://localhost:8000/stats/SHORT_CODE
```

**Database Management:**
```bash
# Reset SQLite database (dev only)
rm urlshortener.db
python -m uvicorn app.main:app

# View SQLite contents
sqlite3 urlshortener.db "SELECT * FROM urls;"

# PostgreSQL: Connect to database
psql -U postgres -d urlshortener
```

**Running Tests:**
```bash
pytest tests/ -v                     # All tests
pytest tests/test_shorten.py -v     # Specific file
pytest tests/ --cov=app              # With coverage
```

**Troubleshooting:**
```bash
# Kill server on port 8000
Get-Process python | Stop-Process -Force  # Windows
lsof -ti:8000 | xargs kill -9             # Linux/macOS

# Check if server is running
Invoke-RestMethod http://localhost:8000/docs  # Windows
curl http://localhost:8000/docs               # Linux/macOS

# View logs (Docker)
docker-compose logs -f api
```

### Environment Variables Quick Setup

**Create `.env` file:**
```bash
# Quick SQLite setup (no database installation needed)
echo "DATABASE_URL=sqlite:///./urlshortener.db" > .env
echo "BASE_URL=http://localhost:8000" >> .env
echo "REDIS_URL=redis://localhost:6379/0" >> .env
```

**Set in PowerShell (temporary):**
```powershell
$env:DATABASE_URL="sqlite:///./urlshortener.db"
$env:BASE_URL="http://localhost:8000"
```

**Set in Bash (temporary):**
```bash
export DATABASE_URL="sqlite:///./urlshortener.db"
export BASE_URL="http://localhost:8000"
```

---

## 🌍 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on deploying to:
- ✅ Render (recommended - free tier available)
- ✅ Railway
- ✅ Heroku
- ✅ AWS/GCP/Azure

---

## 📊 Performance

| Operation | Latency | Notes |
|-----------|---------|-------|
| Shorten URL | ~10-20ms | Includes DB write |
| Redirect (cached) | <1ms | Redis lookup |
| Redirect (uncached) | ~5-10ms | PostgreSQL query |
| Stats lookup | ~5-10ms | PostgreSQL query |

**Scalability:**
- Single instance: ~1,000 req/sec
- With Redis cluster + read replicas: 10,000+ req/sec

---

## 🐛 Troubleshooting

**Port already in use:**
```bash
docker-compose down
docker-compose up --build
```

**Database connection error:**
```bash
# Check PostgreSQL is running
docker-compose ps

# Recreate containers
docker-compose down -v
docker-compose up --build
```

**Redis not connecting:**
```bash
# Check Redis is running
docker-compose logs redis

# The app works without Redis (just slower)
```

---

## 📚 Documentation

- **[DOCS.md](DOCS.md)** — Complete system design, flows, interview prep
- **[DEPLOYMENT.md](DEPLOYMENT.md)** — Deployment guide
- **Swagger Docs** — http://localhost:8000/docs (when running)

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

```bash
# Fork the repo, clone it, create a branch
git checkout -b feature/amazing-feature

# Make changes, test them
pytest tests/ -v

# Commit and push
git commit -m "Add amazing feature"
git push origin feature/amazing-feature

# Open a Pull Request on GitHub
```

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👨‍💻 Author

**Vivek Dubey**

Built as a portfolio project demonstrating:
- Clean architecture (3-layer separation)
- Production-ready code (error handling, logging, tests)
- Modern Python ecosystem (FastAPI, Pydantic, SQLAlchemy 2.0)
- DevOps practices (Docker, CI/CD ready)

---

## ⭐ Show Your Support

If this project helped you, give it a ⭐ on GitHub!

---

## 🔗 Related Projects

- [bitly/shorturl](https://github.com/bitly/shorturl) - URL shortening library
- [fastapi/fastapi](https://github.com/tiangolo/fastapi) - FastAPI framework

---

**Status**: ✅ Production Ready | 🧪 Well Tested | 📦 Docker Ready | 🚀 Deploy Anywhere
