# ═══════════════════════════════════════════════════════════
#  GITHUB PUSH SCRIPT — Push your URL Shortener to GitHub
# ═══════════════════════════════════════════════════════════
# 
# Prerequisites:
# 1. Git installed (download from https://git-scm.com)
# 2. GitHub account created
# 3. GitHub repository created (https://github.com/new)
#
# Usage:
#   1. Edit line 18 below with YOUR GitHub username
#   2. Run this script: .\push-to-github.ps1
#
# ═══════════════════════════════════════════════════════════

# ── CONFIGURATION ──────────────────────────────────────────
$GITHUB_USERNAME = "YOUR_USERNAME_HERE"  # ⚠️ EDIT THIS!
$REPO_NAME = "url-shortener"

# ── COLORS ─────────────────────────────────────────────────
$GREEN = "Green"
$YELLOW = "Yellow"
$RED = "Red"
$CYAN = "Cyan"

# ═══════════════════════════════════════════════════════════
#  MAIN SCRIPT
# ═══════════════════════════════════════════════════════════

Write-Host ""
Write-Host "════════════════════════════════════════════════════" -ForegroundColor $CYAN
Write-Host "   🚀 GitHub Push Script — URL Shortener" -ForegroundColor $CYAN
Write-Host "════════════════════════════════════════════════════" -ForegroundColor $CYAN
Write-Host ""

# ── Step 0: Check if Git is installed ──────────────────────
Write-Host "🔍 Checking if Git is installed..." -ForegroundColor $YELLOW
try {
    $gitVersion = git --version
    Write-Host "✅ Git found: $gitVersion" -ForegroundColor $GREEN
} catch {
    Write-Host "❌ Git is NOT installed!" -ForegroundColor $RED
    Write-Host "   Download from: https://git-scm.com/download/win" -ForegroundColor $YELLOW
    Write-Host ""
    exit 1
}

# ── Step 1: Validate username ──────────────────────────────
if ($GITHUB_USERNAME -eq "YOUR_USERNAME_HERE") {
    Write-Host "❌ ERROR: You need to edit this script!" -ForegroundColor $RED
    Write-Host "   Open push-to-github.ps1 and change line 18:" -ForegroundColor $YELLOW
    Write-Host '   $GITHUB_USERNAME = "your_actual_github_username"' -ForegroundColor $CYAN
    Write-Host ""
    exit 1
}

Write-Host "📝 GitHub Username: $GITHUB_USERNAME" -ForegroundColor $GREEN
Write-Host "📁 Repository Name: $REPO_NAME" -ForegroundColor $GREEN
Write-Host ""

# ── Step 2: Ask for confirmation ───────────────────────────
Write-Host "⚠️  BEFORE RUNNING THIS SCRIPT:" -ForegroundColor $YELLOW
Write-Host "   1. Created GitHub repo: https://github.com/$GITHUB_USERNAME/$REPO_NAME" -ForegroundColor $YELLOW
Write-Host "   2. Make sure the repo is EMPTY (no README.md initialized)" -ForegroundColor $YELLOW
Write-Host ""

$confirm = Read-Host "Ready to push? (y/n)"
if ($confirm -ne "y") {
    Write-Host "❌ Aborted by user." -ForegroundColor $RED
    exit 0
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════" -ForegroundColor $CYAN
Write-Host "   Starting Git Operations..." -ForegroundColor $CYAN
Write-Host "════════════════════════════════════════════════════" -ForegroundColor $CYAN
Write-Host ""

# ── Step 3: Initialize Git (if not already) ────────────────
Write-Host "[1/6] Initializing Git repository..." -ForegroundColor $YELLOW
if (Test-Path ".git") {
    Write-Host "✅ Git already initialized (skipping)" -ForegroundColor $GREEN
} else {
    git init
    Write-Host "✅ Git initialized" -ForegroundColor $GREEN
}

# ── Step 4: Add all files ──────────────────────────────────
Write-Host ""
Write-Host "[2/6] Adding all files to Git..." -ForegroundColor $YELLOW
git add .
Write-Host "✅ Files added" -ForegroundColor $GREEN

# ── Step 5: Check if already committed ─────────────────────
Write-Host ""
Write-Host "[3/6] Creating initial commit..." -ForegroundColor $YELLOW
$hasCommits = git rev-parse HEAD 2>$null
if ($hasCommits) {
    Write-Host "✅ Commits already exist (skipping)" -ForegroundColor $GREEN
} else {
    git commit -m "Initial commit: URL shortener with FastAPI + PostgreSQL + Redis"
    Write-Host "✅ Commit created" -ForegroundColor $GREEN
}

# ── Step 6: Check if remote exists ─────────────────────────
Write-Host ""
Write-Host "[4/6] Setting up GitHub remote..." -ForegroundColor $YELLOW
$remoteUrl = "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
$existingRemote = git remote get-url origin 2>$null

if ($existingRemote) {
    Write-Host "⚠️  Remote 'origin' already exists: $existingRemote" -ForegroundColor $YELLOW
    $overwrite = Read-Host "Overwrite with new URL? (y/n)"
    if ($overwrite -eq "y") {
        git remote set-url origin $remoteUrl
        Write-Host "✅ Remote URL updated" -ForegroundColor $GREEN
    } else {
        Write-Host "⏭️  Keeping existing remote" -ForegroundColor $YELLOW
    }
} else {
    git remote add origin $remoteUrl
    Write-Host "✅ Remote added: $remoteUrl" -ForegroundColor $GREEN
}

# ── Step 7: Set main branch ────────────────────────────────
Write-Host ""
Write-Host "[5/6] Setting branch to 'main'..." -ForegroundColor $YELLOW
git branch -M main
Write-Host "✅ Branch set to 'main'" -ForegroundColor $GREEN

# ── Step 8: Push to GitHub ─────────────────────────────────
Write-Host ""
Write-Host "[6/6] Pushing to GitHub..." -ForegroundColor $YELLOW
Write-Host "⚠️  You may be prompted for GitHub credentials..." -ForegroundColor $YELLOW
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "════════════════════════════════════════════════════" -ForegroundColor $GREEN
    Write-Host "   ✅ SUCCESS! Your code is on GitHub!" -ForegroundColor $GREEN
    Write-Host "════════════════════════════════════════════════════" -ForegroundColor $GREEN
    Write-Host ""
    Write-Host "🔗 View your repo:" -ForegroundColor $CYAN
    Write-Host "   https://github.com/$GITHUB_USERNAME/$REPO_NAME" -ForegroundColor $CYAN
    Write-Host ""
    Write-Host "📚 Next Steps:" -ForegroundColor $CYAN
    Write-Host "   1. Open DEPLOYMENT.md for deployment instructions" -ForegroundColor $YELLOW
    Write-Host "   2. Deploy on Render.com (free tier)" -ForegroundColor $YELLOW
    Write-Host "   3. Share your project!" -ForegroundColor $YELLOW
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "════════════════════════════════════════════════════" -ForegroundColor $RED
    Write-Host "   ❌ Push Failed" -ForegroundColor $RED
    Write-Host "════════════════════════════════════════════════════" -ForegroundColor $RED
    Write-Host ""
    Write-Host "Common Issues:" -ForegroundColor $YELLOW
    Write-Host "   1. GitHub repo doesn't exist yet" -ForegroundColor $YELLOW
    Write-Host "      → Create it at: https://github.com/new" -ForegroundColor $CYAN
    Write-Host ""
    Write-Host "   2. GitHub credentials not configured" -ForegroundColor $YELLOW
    Write-Host "      → Set up: https://docs.github.com/en/get-started/quickstart/set-up-git" -ForegroundColor $CYAN
    Write-Host ""
    Write-Host "   3. Need a Personal Access Token (PAT)" -ForegroundColor $YELLOW
    Write-Host "      → Generate at: https://github.com/settings/tokens" -ForegroundColor $CYAN
    Write-Host "      → Use token as password when prompted" -ForegroundColor $CYAN
    Write-Host ""
    exit 1
}
