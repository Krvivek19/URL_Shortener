# 🚀 QUICK START — Push to GitHub & Deploy

**Time Required:** 15-20 minutes  
**Cost:** $0 (completely free)

---

## 📋 Prerequisites Checklist

- [ ] Git installed ([download here](https://git-scm.com/download/win))
- [ ] GitHub account ([sign up here](https://github.com/join))
- [ ] Project files in `C:\Users\dubeyviv\url-shortener`

---

## ⚡ FASTEST PATH: 3 Steps to Live Deployment

### STEP 1: Create GitHub Repository (2 minutes)

1. Go to **https://github.com/new**
2. Fill in:
   - **Repository name:** `url-shortener`
   - **Description:** `Production-ready URL shortener with FastAPI, PostgreSQL, Redis`
   - **Visibility:** Public
   - **⚠️ IMPORTANT:** DO NOT check "Add a README file"
3. Click **Create repository**
4. **Leave the page open** — you'll need the URL

---

### STEP 2: Push to GitHub (5 minutes)

**Option A: Automated Script (Easiest)**

1. Edit `push-to-github.ps1`:
   - Right-click the file → Edit
   - Line 18: Change `YOUR_USERNAME_HERE` to your **actual GitHub username**
   - Save and close

2. Run the script:
   ```powershell
   cd C:\Users\dubeyviv\url-shortener
   .\push-to-github.ps1
   ```

3. If you get "execution policy" error:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\push-to-github.ps1
   ```

4. Follow the prompts

**Option B: Manual Commands**

```powershell
cd C:\Users\dubeyviv\url-shortener

# Initialize Git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: URL shortener project"

# Add GitHub remote (REPLACE with your username!)
git remote add origin https://github.com/YOUR_USERNAME/url-shortener.git

# Push
git branch -M main
git push -u origin main
```

**Authentication Notes:**
- If prompted for username/password:
  - Username: Your GitHub username
  - Password: Use a **Personal Access Token** (NOT your GitHub password)
  - [Generate token here](https://github.com/settings/tokens) → Select "repo" scope

✅ **Verify:** Visit `https://github.com/YOUR_USERNAME/url-shortener` — you should see all files!

---

### STEP 3: Deploy on Render (10 minutes)

#### 3.1 Create Render Account

1. Go to **https://render.com**
2. Click **Get Started for Free**
3. Sign up with **GitHub** (easiest)
4. Authorize Render to access your repositories

#### 3.2 Create PostgreSQL Database

1. In Render Dashboard → Click **New +** → **PostgreSQL**
2. Settings:
   - **Name:** `url-shortener-db`
   - **Region:** Select **Oregon (US West)** or closest to you
   - **PostgreSQL Version:** 16
   - **Plan:** **Free**
3. Click **Create Database**
4. **Wait ~2 minutes** for it to provision
5. **Copy the "Internal Database URL"** (it starts with `postgresql://...`)
   - You'll need this in Step 3.4

#### 3.3 Create Redis Instance

1. In Render Dashboard → Click **New +** → **Redis**
2. Settings:
   - **Name:** `url-shortener-redis`
   - **Region:** **Same as your PostgreSQL** (e.g., Oregon)
   - **Plan:** **Free** (25 MB)
3. Click **Create Redis**
4. **Copy the "Internal Redis URL"** (it starts with `redis://...`)

#### 3.4 Create Web Service (Your API)

1. In Render Dashboard → Click **New +** → **Web Service**
2. Click **Connect a repository**
   - If needed: Authorize Render to see your repos
3. Find and click **Connect** next to `url-shortener`
4. Settings:
   - **Name:** `url-shortener-api` (or choose your own)
   - **Region:** **Same as DB/Redis** (e.g., Oregon)
   - **Branch:** `main`
   - **Runtime:** **Docker** (auto-detected!)
   - **Plan:** **Free**
5. **Environment Variables** — click "Advanced" and add these:

   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | Paste the Internal Database URL from Step 3.2 |
   | `REDIS_URL` | Paste the Internal Redis URL from Step 3.3 |
   | `BASE_URL` | `https://url-shortener-api.onrender.com` |
   
   ⚠️ **Important:** The `BASE_URL` value above is a placeholder. After your service is created, you'll get the actual URL and need to update it.

6. Click **Create Web Service**

#### 3.5 Wait for Build (5-10 minutes)

- Watch the logs in real-time
- First build takes ~5-10 minutes (downloading Docker images, building)
- Look for these success messages:
  ```
  ✅ Database tables created/verified
  🚀 Starting URL Shortener...
  ```
- When status shows "Live" (green) → SUCCESS!

#### 3.6 Update BASE_URL (IMPORTANT!)

1. Copy your actual Render URL (e.g., `https://url-shortener-api-abcd.onrender.com`)
2. In your service → Click **Environment** tab
3. Find `BASE_URL` → Click **Edit**
4. Update to your actual URL: `https://url-shortener-api-abcd.onrender.com`
5. Click **Save Changes**
6. Service will auto-redeploy (~1 minute)

---

## ✅ Testing Your Deployment

### Test 1: Health Check
```bash
# In browser or PowerShell:
curl https://your-app.onrender.com/health
```
Expected: `{"status":"ok","service":"URL Shortener"}`

### Test 2: Open API Docs
Open in browser:
```
https://your-app.onrender.com/docs
```
You should see interactive Swagger documentation!

### Test 3: Shorten a URL
```powershell
curl -X POST https://your-app.onrender.com/shorten `
  -H "Content-Type: application/json" `
  -d '{"long_url": "https://www.google.com"}'
```

Expected response:
```json
{
  "short_url": "https://your-app.onrender.com/abc123",
  "short_code": "abc123",
  "long_url": "https://www.google.com",
  "created_at": "2026-03-05T...",
  "expiry_date": null
}
```

### Test 4: Redirect
Open in browser:
```
https://your-app.onrender.com/abc123
```
Should redirect to Google!

### Test 5: Get Stats
```powershell
curl https://your-app.onrender.com/stats/abc123
```

---

## 🎉 You're Live!

**Your Links:**
- 🌐 **Live API:** https://your-app.onrender.com
- 📚 **API Docs:** https://your-app.onrender.com/docs
- 💾 **GitHub Repo:** https://github.com/YOUR_USERNAME/url-shortener

**Share Your Work:**
1. Add to your resume under "Projects"
2. Share on LinkedIn: "Built a production-ready URL shortener using FastAPI, PostgreSQL, Redis, and Docker"
3. Add the GitHub link to your portfolio

---

## 📊 Free Tier Limits (Render)

| Resource | Free Tier Limit | Notes |
|----------|----------------|-------|
| **Web Service** | 750 hours/month | Sleeps after 15 min of inactivity |
| **PostgreSQL** | 90 days, then archived | Enough for demo/portfolio |
| **Redis** | 25 MB storage | Sufficient for caching |
| **Bandwidth** | 100 GB/month | More than enough |

**⚠️ Free services sleep after 15 minutes of inactivity:**
- First request after sleep takes ~30 seconds to wake up
- Subsequent requests are instant
- **Solution:** Use [UptimeRobot](https://uptimerobot.com) to ping `/health` every 5 minutes

---

## 🐛 Troubleshooting

### "Deploy failed" in Render

**Check the logs:**
1. Go to your service in Render
2. Click **Logs** tab
3. Look for error messages

**Common issues:**
- Missing environment variable → Add it in Environment tab
- Wrong Docker command → Check Dockerfile (line 28)
- Database connection error → Verify `DATABASE_URL` is correct

### Git push rejected

**Error:** `remote: Permission denied`

**Solution:** Use Personal Access Token:
1. Go to https://github.com/settings/tokens
2. Click **Generate new token (classic)**
3. Name: "URL Shortener Deploy"
4. Select scope: **repo** (all checkboxes)
5. Click **Generate**
6. Copy the token (you won't see it again!)
7. When pushing, use token as password

### PowerShell script won't run

**Error:** `running scripts is disabled on this system`

**Solution:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\push-to-github.ps1
```

---

## 📝 Next Steps

### Short Term (Today)
- [x] Push to GitHub
- [x] Deploy on Render
- [ ] Test all endpoints
- [ ] Add project to resume
- [ ] Share on LinkedIn

### Medium Term (This Week)
- [ ] Add custom domain (optional)
- [ ] Set up monitoring with UptimeRobot
- [ ] Read DOCS.md to understand architecture
- [ ] Practice explaining the project (mock interview)

### Long Term (Next Month)
- [ ] Add a feature:
  - QR code generation
  - User authentication
  - Analytics dashboard
  - Link preview with Open Graph
- [ ] Write a blog post about building it
- [ ] Contribute to open source (practice with your own code first)

---

## 📚 Additional Resources

- **Full Documentation:** [DOCS.md](DOCS.md)
- **Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Render Docs:** https://render.com/docs
- **PostgreSQL Docs:** https://www.postgresql.org/docs

---

## 🆘 Need Help?

1. **Check DEPLOYMENT.md** — Detailed troubleshooting section
2. **Render Community:** https://community.render.com
3. **GitHub Issues:** Open an issue in your repo
4. **Stack Overflow:** Tag `fastapi`, `postgresql`, `docker`

---

**⏱️ Average completion time:** 15-20 minutes  
**💰 Total cost:** $0  
**📈 Resume impact:** High (production-ready, Docker, clean code)

**Good luck! 🚀**
