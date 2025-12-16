# 🚀 DEPLOY IN 10 MINUTES - QUICK GUIDE

## Option 1: Render.com (RECOMMENDED - FREE)

### Steps:
1. **Push to GitHub:**
   ```bash
   git push origin main
   ```

2. **Go to Render.com:**
   - Sign up: https://render.com/ (use GitHub login)
   - Click "New +" → "Web Service"
   - Connect your repo: `Final_Project_Alikhan_alikhan4`

3. **Configure:**
   - **Name:** `stock-cards`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn appserver.wsgi:application`
   - **Instance Type:** FREE

4. **Add Environment Variables:**
   ```
   SECRET_KEY = (generate with command below)
   DEBUG = False
   ALLOWED_HOSTS = .onrender.com
   ```
   
   Generate secret key:
   ```bash
   python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

5. **Add PostgreSQL Database:**
   - Click "Add Database" → PostgreSQL (free)
   - Render auto-sets DATABASE_URL

6. **Deploy!**
   - Click "Create Web Service"
   - Wait 5-10 minutes
   - Live at: `https://stock-cards.onrender.com`

**Admin:** `infoadmins` / `uiucinfo` (auto-created)

---

## Option 2: Railway.app (FASTEST - $5 FREE CREDIT)

### Steps:
1. **Push to GitHub:**
   ```bash
   git push origin main
   ```

2. **Go to Railway:**
   - https://railway.app/
   - "Start a New Project" → "Deploy from GitHub"
   - Select your repo

3. **Auto-Deploy:**
   - Railway detects Django automatically
   - Adds PostgreSQL automatically

4. **Add Environment Variables:**
   ```
   SECRET_KEY = (generate one)
   DEBUG = False
   ALLOWED_HOSTS = .railway.app
   ```

5. **Done!**
   - Deploys in 3-5 minutes
   - Live at: `https://your-app.railway.app`

**Admin:** `mohitg2` / `graingerlibrary` (auto-created)

## Comparison

| Platform | Cost | Speed | Ease |
|----------|------|-------|------|
| **Render** | FREE (750hr/mo) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Railway** | $5 credit/mo | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Heroku | $5+/month | ⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## What I Did for You

✅ Created `Procfile` - Run configuration
✅ Created `build.sh` - Build script  
✅ Updated `settings.py` - Production config
✅ Updated `requirements.txt` - Added gunicorn, whitenoise, psycopg2
✅ Added `runtime.txt` - Python version
✅ Created `DEPLOYMENT.md` - Full guide

**Everything is ready! Just push and deploy.**

---

## After Deployment

**Your app will be at:** `https://your-app-name.onrender.com`

**Admin panel:** `https://your-app-name.onrender.com/admin/`

**Login:** `mohitg2` / `graingerlibrary`

---

## Next Steps RIGHT NOW:

```bash
# 1. Push to GitHub
cd /Users/alikhan/Documents/GitHub/Final_Project_Alikhan_alikhan4
git push origin main

# 2. Go to render.com
# 3. Follow steps above
# 4. Done in 10 minutes!
```

**You're ready to deploy! 🎉**

