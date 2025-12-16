# Stock Cards - Render.com Deployment Guide

## Quick Deploy to Render.com (FREE) - 10 Minutes

### Step 1: Push to GitHub

```bash
cd /Users/alikhan/Documents/GitHub/Final_Project_Alikhan_alikhan4
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Create Render Account

1. Go to https://render.com/
2. Click "Get Started for Free"
3. Sign up with GitHub (easiest option)

### Step 3: Create Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository: `Final_Project_Alikhan_alikhan4`
3. Fill in the details:

**Basic Settings:**
- **Name:** `stock-cards` (or any name)
- **Region:** Choose closest to you
- **Branch:** `main`
- **Root Directory:** (leave empty)
- **Environment:** `Python 3`
- **Build Command:** `./build.sh`
- **Start Command:** `gunicorn appserver.wsgi:application`

**Instance Type:**
- Select **"Free"** (750 hours/month free)

### Step 4: Add Environment Variables

Click "Advanced" → "Add Environment Variable" and add these:

```
SECRET_KEY = your-secret-key-here-make-it-long-and-random
DEBUG = False
ALLOWED_HOSTS = .onrender.com
DATABASE_URL = (This will be auto-populated by Render when you add PostgreSQL)
```

**Generate a secret key:**
```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Step 5: Add PostgreSQL Database

1. While still in the web service creation:
2. Scroll down to "Environment" section
3. Click "Add Database" → "Create Database"
4. Choose **PostgreSQL** (Free tier)
5. Name it: `stock-cards-db`
6. Render will automatically populate `DATABASE_URL`

### Step 6: Deploy!

1. Click "Create Web Service"
2. Wait 5-10 minutes for deployment
3. Your app will be live at: `https://stock-cards.onrender.com` (or your chosen name)

---

## Alternative: Railway.app (Even Faster!)

### Railway Deployment (5 minutes)

1. Go to https://railway.app/
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects Django and sets everything up
6. Add environment variables in the dashboard:
   - `SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=.railway.app`
7. Click "Deploy"

**You get $5 free credit per month - enough for this project!**

---

## Alternative: PythonAnywhere (Django-Specific)

1. Go to https://www.pythonanywhere.com/
2. Create free account
3. Upload your code or clone from GitHub
4. Follow their Django deployment wizard
5. Free tier is always free but limited

---

## After Deployment

### Create Admin User on Production

1. Go to your Render dashboard
2. Click on your web service
3. Go to "Shell" tab
4. Run:
```bash
python manage.py createsuperuser
```
Enter: `mohitg2` / `graingerlibrary`

Or the build.sh script already does this automatically!

### Access Your App

- **Main App:** `https://your-app-name.onrender.com/`
- **Admin:** `https://your-app-name.onrender.com/admin/`
- **Login:** `mohitg2` / `graingerlibrary`

---

## Troubleshooting

### Build Failed?

Check the logs in Render dashboard. Common issues:
- Missing dependencies in requirements.txt (already fixed)
- Wrong Python version (we're using 3.14 locally, Render uses 3.11+ - that's fine)
- Build script not executable (already fixed with chmod +x)

### App Won't Start?

- Check if `ALLOWED_HOSTS` includes your domain
- Verify `DATABASE_URL` is set
- Check logs for errors

### Static Files Not Loading?

Already handled with WhiteNoise! Just run:
```bash
python manage.py collectstatic
```
(build.sh does this automatically)

---

## Cost Comparison

| Platform | Free Tier | Pros | Cons |
|----------|-----------|------|------|
| **Render** | 750 hrs/mo | Easy, PostgreSQL included, No CC | Sleeps after inactivity |
| **Railway** | $5 credit/mo | Fastest, Best DX | Needs CC for verification |
| **PythonAnywhere** | Always free | Django-optimized | Limited features |
| **Heroku** | ❌ No free tier | (Used to be best) | Now costs $5+/month |

---

## Recommended: Use Render.com

**Why?**
- ✅ True free tier (no credit card)
- ✅ PostgreSQL included
- ✅ Auto-deploys from GitHub
- ✅ Easy setup
- ✅ Good for presentations/demos

**The only downside:** Free tier sleeps after 15 minutes of inactivity (takes ~30 seconds to wake up on first request)

For a college project presentation, this is perfect!

---

## Files I Created for Deployment

1. **Procfile** - Tells Render how to run the app
2. **build.sh** - Build script (installs deps, runs migrations, creates admin)
3. **Updated settings.py** - Environment-based config
4. **Updated requirements.txt** - Added production dependencies

**All ready to go - just push to GitHub and connect to Render!**

---

## Quick Start Commands

```bash
# 1. Commit and push
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Go to render.com and follow Step 3-6 above

# 3. Your app will be live in ~10 minutes!
```

**Good luck with deployment! 🚀**

