# 🚀 Deployment Guide — URL Shortener

This guide covers:
1. **GitHub Setup** — Push your code to GitHub
2. **Render Deployment** — Free tier, supports Docker (RECOMMENDED)
3. **Railway Deployment** — Alternative with $5 free credit
4. **Other Options** — Heroku, AWS, GCP, Azure

---

## 📦 STEP 1: Push to GitHub

### 1.1 Create GitHub Repository

1. Go to [github.com](https://github.com) and log in
2. Click the **"+"** icon (top right) → **New repository**
3. Repository settings:
   - **Name**: `url-shortener`
   - **Description**: `Production-ready URL shortener with FastAPI, PostgreSQL, Redis`
   - **Visibility**: Public (or Private)
   - **DO NOT** initialize with README (we already have one)
4. Click **Create repository**

### 1.2 Initialize Git and Push

Open PowerShell in your project directory:

```powershell
# Navigate to project
cd C:\Users\dubeyviv\url-shortener

# Initialize Git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: URL shortener with FastAPI + PostgreSQL + Redis"

# Add GitHub as remote (REPLACE with your username)
git remote add origin https://github.com/YOUR_USERNAME/url-shortener.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME`** with your actual GitHub username!

### 1.3 Verify

Visit `https://github.com/YOUR_USERNAME/url-shortener` in your browser — you should see all your files!

---

## 🌐 STEP 2: Deploy on Render (RECOMMENDED)

**Why Render?**
- ✅ Free tier (750 hours/month per service)
- ✅ Native Docker support
- ✅ Managed PostgreSQL + Redis
- ✅ Auto-deploy on git push
- ✅ HTTPS included

### 2.1 Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with your **GitHub account** (easy linking)

### 2.2 Create PostgreSQL Database

1. In Render Dashboard → Click **New** → **PostgreSQL**
2. Settings:
   - **Name**: `url-shortener-db`
   - **Database**: `urlshortener`
   - **User**: (auto-generated)
   - **Region**: Choose closest to your location
   - **Plan**: **Free**
3. Click **Create Database**
4. **Copy the Internal Database URL** (starts with `postgresql://...`)
   - You'll need this in Step 2.4

### 2.3 Create Redis Instance

1. In Render Dashboard → Click **New** → **Redis**
2. Settings:
   - **Name**: `url-shortener-redis`
   - **Region**: Same as your PostgreSQL
   - **Plan**: **Free** (25 MB)
3. Click **Create Redis**
4. **Copy the Internal Redis URL** (starts with `redis://...`)

### 2.4 Create Web Service

1. In Render Dashboard → Click **New** → **Web Service**
2. Connect your GitHub repository:
   - Click **Connect account** → Authorize Render
   - Search for `url-shortener` → Click **Connect**
3. Settings:
   - **Name**: `url-shortener-api`
   - **Region**: Same as DB/Redis
   - **Branch**: `main`
   - **Runtime**: **Docker**
   - **Plan**: **Free**
4. **Environment Variables** (click "Advanced"):
   ```
   DATABASE_URL = <paste Internal Database URL from Step 2.2>
   REDIS_URL = <paste Internal Redis URL from Step 2.3>
   BASE_URL = https://url-shortener-api.onrender.com
   ```
   *(Replace the BASE_URL with your actual Render URL after creation)*

5. Click **Create Web Service**

### 2.5 Wait for Deployment

- First deploy takes ~5-10 minutes (Docker image build)
- Watch the logs in Render dashboard
- When you see "✅ Database tables created/verified" → SUCCESS!

### 2.6 Test Your Deployment

```bash
# Health check (replace with your Render URL)
curl https://url-shortener-api.onrender.com/health

# Open Swagger docs
https://url-shortener-api.onrender.com/docs

# Shorten a URL
curl -X POST https://url-shortener-api.onrender.com/shorten \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://www.google.com"}'
```

### 2.7 Update BASE_URL (Important!)

1. Go to Render Dashboard → Your web service
2. Click **Environment** tab
3. Edit `BASE_URL` to your actual Render URL:
   ```
   BASE_URL = https://url-shortener-api.onrender.com
   ```
4. Save → Service will auto-redeploy

**🎉 You're live!** Share your short URLs like:
```
https://url-shortener-api.onrender.com/abc123
```

---

## 🚂 ALTERNATIVE: Deploy on Railway

**Why Railway?**
- $5 free credit (no credit card for trial)
- Very simple setup
- Great developer experience

### Railway Steps

1. Go to [railway.app](https://railway.app) → Sign up with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your `url-shortener` repository
4. Railway auto-detects Docker! 
5. Add **PostgreSQL** plugin (from Railway marketplace)
6. Add **Redis** plugin
7. Environment variables (auto-configured by Railway):
   ```
   DATABASE_URL = ${{Postgres.DATABASE_URL}}
   REDIS_URL = ${{Redis.REDIS_URL}}
   BASE_URL = https://<your-app>.up.railway.app
   ```
8. Deploy!

**Cost:** Free for first $5 usage, then ~$5-10/month

---

## 🔧 Other Deployment Options

### Heroku

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
cd url-shortener
heroku create your-url-shortener

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Add Redis addon
heroku addons:create heroku-redis:mini

# Set environment variables
heroku config:set BASE_URL=https://your-url-shortener.herokuapp.com

# Deploy
git push heroku main

# Open
heroku open
```

**Cost:** PostgreSQL Mini ($5/month), Redis Mini ($3/month)

### AWS (EC2 + RDS)

1. Launch EC2 instance (t2.micro free tier)
2. Create RDS PostgreSQL instance
3. Create ElastiCache Redis instance
4. Install Docker on EC2
5. SCP your code to EC2
6. Run `docker-compose up -d`

**Good for:** Learning AWS, full control  
**Cost:** Free tier eligible (12 months)

### DigitalOcean App Platform

1. Connect GitHub repo
2. Detects Dockerfile automatically
3. Add PostgreSQL + Redis managed databases
4. Set environment variables
5. Deploy

**Cost:** $5/month for basic app + $15/month for databases

### Google Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/url-shortener

# Deploy
gcloud run deploy url-shortener \
  --image gcr.io/PROJECT_ID/url-shortener \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Add Cloud SQL (PostgreSQL) and Memorystore (Redis)
```

**Good for:** Auto-scaling, pay-per-request  
**Cost:** Free tier (2 million requests/month)

---

## 🔐 Production Best Practices

### 1. Environment Variables (Security)

**Never commit secrets!** Use environment variables for:
- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY` (if you add auth later)

Check `.gitignore` includes:
```
.env
*.env
```

### 2. Database Migrations (Using Alembic)

```bash
# Install alembic
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial tables"

# Apply migration
alembic upgrade head
```

For Render/Railway, add to your Dockerfile:
```dockerfile
# Run migrations on startup
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. HTTPS (SSL)

- ✅ Render: Automatic
- ✅ Railway: Automatic
- ✅ Heroku: Automatic
- ⚠️ AWS EC2: Use CloudFront or ALB with ACM certificate

### 4. Custom Domain

**Render:**
1. Go to your service → Settings → Custom Domain
2. Add your domain (e.g., `short.yourdomain.com`)
3. Update DNS with provided CNAME

**Cloudflare (free SSL + CDN):**
1. Add your domain to Cloudflare
2. Point to your Render/Railway URL
3. Enable SSL (Full mode)
4. Enable caching for `/{short_code}` routes

### 5. Monitoring

**Free Tools:**
- [Sentry](https://sentry.io) — Error tracking
- [Logtail](https://logtail.com) — Log aggregation
- [UptimeRobot](https://uptimerobot.com) — Uptime monitoring

Add to your code:
```python
# app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    traces_sample_rate=1.0,
)
```

### 6. Rate Limiting (Production)

Current: 10 req/min per IP (in-memory)

**For multi-instance deployments**, use Redis-backed rate limiting:

```python
# app/routes.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL  # Use Redis instead of in-memory
)
```

### 7. Backup Strategy

**PostgreSQL:**
- Render: Automatic daily backups on paid plans
- Manual: `pg_dump` → store in S3/Google Cloud Storage

**Redis:**
- Redis is a cache — OK to lose (data is in PostgreSQL)
- For persistence: enable RDB snapshots

---

## 📊 Deployment Comparison

| Platform | Setup Time | Free Tier | Docker | Auto-Deploy | Best For |
|----------|------------|-----------|--------|-------------|----------|
| **Render** | 10 min | ✅ 750h/mo | ✅ | ✅ | **Beginners** |
| **Railway** | 5 min | $5 credit | ✅ | ✅ | Fast prototyping |
| Heroku | 15 min | ❌ ($7/mo) | ✅ | ✅ | Established projects |
| AWS EC2 | 30 min | ✅ 12 months | ✅ | ❌ | Learning AWS |
| Google Cloud Run | 20 min | ✅ 2M req/mo | ✅ | ✅ | High traffic |
| DigitalOcean | 15 min | ❌ ($5/mo) | ✅ | ✅ | Simple VPS |

**Recommendation:** Start with **Render** (free + easy)

---

## 🐛 Common Deployment Issues

### Issue 1: Database connection timeout

**Solution:**
```python
# app/database.py
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Keep connections alive
    pool_recycle=3600,   # Recycle connections every hour
)
```

### Issue 2: Redis not connecting

**Check:**
- Is `REDIS_URL` set correctly?
- Is Redis instance running?

**Graceful fallback** (already implemented in `cache.py`):
```python
if not REDIS_AVAILABLE:
    logger.warning("Redis not available, running without cache")
```

### Issue 3: Port binding error

**Fix in Dockerfile:**
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Render/Railway automatically set `$PORT` environment variable.

### Issue 4: CORS errors (if building a frontend)

**Add CORS middleware** in `app/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourfrontend.com"],  # or ["*"] for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ✅ Post-Deployment Checklist

- [ ] Health check endpoint works: `/health`
- [ ] Swagger docs accessible: `/docs`
- [ ] Can shorten a URL: `POST /shorten`
- [ ] Redirect works: `GET /{short_code}`
- [ ] Stats endpoint works: `GET /stats/{short_code}`
- [ ] Custom alias works
- [ ] Expiry returns 410 after expiry date
- [ ] Rate limiting prevents spam
- [ ] Logs are visible in platform dashboard
- [ ] Updated `BASE_URL` to production URL
- [ ] Added custom domain (optional)
- [ ] Set up monitoring (optional)

---

## 🚀 Auto-Deploy on Git Push

**GitHub Actions** (add `.github/workflows/deploy.yml`):

```yaml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Render Deploy
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

**Render automatically deploys on push** (no GitHub Actions needed!)

---

## 📞 Support

**Render Issues:**
- [Render Community](https://community.render.com/)
- [Render Status](https://status.render.com/)

**Railway Issues:**
- [Railway Discord](https://discord.gg/railway)

**Your Project Issues:**
- Open a GitHub Issue in your repo

---

## 🎯 Next Steps After Deployment

1. **Share your project**:
   - Add to your resume
   - Post on LinkedIn
   - Share on Twitter with #buildinpublic

2. **Add features**:
   - User authentication (JWT)
   - QR code generation
   - Analytics dashboard
   - Link preview

3. **Optimize**:
   - Add caching headers
   - Use CDN for redirects
   - Implement database read replicas

4. **Monitor**:
   - Set up error alerts
   - Track response times
   - Monitor database size

---

**🎉 Congratulations!** Your URL shortener is now live and accessible to the world!

**Your GitHub URL:** `https://github.com/YOUR_USERNAME/url-shortener`  
**Your Live API:** `https://your-app.onrender.com`  
**API Docs:** `https://your-app.onrender.com/docs`
