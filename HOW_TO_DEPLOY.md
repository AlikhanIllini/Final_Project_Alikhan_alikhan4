# How to Deploy/Update Stock Cards

## ✅ **Your Code is Now Pushed to GitHub!**

All your latest changes (improved price adapter, admin credentials, etc.) are now on GitHub.

---

## 🚀 **OPTION 1: Deploy to Render.com (RECOMMENDED - FREE)**

### **First Time Setup:**

1. **Go to Render.com**
   - Visit: https://render.com/
   - Sign up with your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Select "Connect a repository"
   - Choose: `Final_Project_Alikhan_alikhan4`

3. **Configure the Service**
   ```
   Name: stock-cards (or any name you want)
   Region: Oregon (or closest to you)
   Branch: main
   Root Directory: (leave blank)
   Environment: Python 3
   Build Command: ./build.sh
   Start Command: gunicorn appserver.wsgi:application
   Instance Type: Free
   ```

4. **Add Environment Variables**
   Click "Advanced" → "Add Environment Variable"
   
   Add these:
   ```
   SECRET_KEY = [generate one - see below]
   DEBUG = False
   ALLOWED_HOSTS = .onrender.com
   ```
   
   **Generate SECRET_KEY:**
   ```bash
   python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```
   Copy the output and paste as SECRET_KEY value

5. **Add PostgreSQL Database**
   - In the same setup page, scroll down
   - Click "Add Database" → "PostgreSQL"
   - Name: `stock-cards-db`
   - Render will auto-populate `DATABASE_URL`

6. **Deploy!**
   - Click "Create Web Service"
   - Wait 5-10 minutes for first deployment
   - Your app will be live at: `https://stock-cards.onrender.com` (or your chosen name)

---

### **To UPDATE Already Deployed App:**

**It's automatic!** Render watches your GitHub repo.

Every time you push to `main` branch:
```bash
git add -A
git commit -m "Your update message"
git push origin main
```

Render will automatically:
1. Detect the push
2. Run `build.sh` (installs dependencies, runs migrations, creates admin)
3. Restart your app with new code
4. Takes ~2-5 minutes

**Check deployment status:**
- Go to Render dashboard
- Click on your service
- Watch the "Events" tab for deployment progress

---

## 🚂 **OPTION 2: Deploy to Railway.app (FAST - $5 FREE CREDIT)**

### **First Time Setup:**

1. **Go to Railway**
   - Visit: https://railway.app/
   - Sign up with GitHub

2. **Create New Project**
   - Click "Start a New Project"
   - Choose "Deploy from GitHub repo"
   - Select `Final_Project_Alikhan_alikhan4`

3. **Railway Auto-Detects Django!**
   - It automatically adds PostgreSQL
   - Sets up environment

4. **Add Environment Variables**
   - Click on your service → "Variables" tab
   - Add:
   ```
   SECRET_KEY = [your generated key]
   DEBUG = False
   ALLOWED_HOSTS = .railway.app
   ```

5. **Deploy!**
   - Railway deploys automatically
   - Live in 3-5 minutes
   - URL: `https://your-app.railway.app`

### **To UPDATE:**
Same as Render - just push to GitHub:
```bash
git push origin main
```
Railway auto-deploys!

---

## 💻 **OPTION 3: Run Locally (For Testing)**

If you just want to test locally:

1. **Make sure virtual environment is active**
   ```bash
   cd /Users/alikhan/Documents/GitHub/Final_Project_Alikhan_alikhan4
   # Virtual env should auto-activate, or run: source .venv/bin/activate
   ```

2. **Install any new dependencies**
   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   python3 manage.py migrate
   ```

4. **Start server**
   ```bash
   python3 manage.py runserver
   ```

5. **Access at:**
   - http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/
   - Login: `mohitg2` / `graingerlibrary`

---

## 🔄 **Quick Update Workflow**

Whenever you make changes:

```bash
# 1. Make your code changes

# 2. Test locally
python3 manage.py runserver

# 3. If good, commit and push
git add -A
git commit -m "Description of changes"
git push origin main

# 4. Wait 2-5 minutes
# Render/Railway auto-deploys!

# 5. Check your deployed URL
# Your changes are live!
```

---

## 📋 **After First Deployment**

### **Access Your Deployed App:**
- **URL:** `https://your-app-name.onrender.com` (or `.railway.app`)
- **Admin:** `https://your-app-name.onrender.com/admin/`
- **Credentials:** `mohitg2` / `graingerlibrary`

### **Verify Everything Works:**
1. ✅ Homepage loads
2. ✅ Can register new user
3. ✅ Can login
4. ✅ Dashboard shows
5. ✅ Can create stock card
6. ✅ Admin panel works

---

## 🐛 **Troubleshooting**

### **Deployment Failed?**
- Check Render/Railway logs
- Common issues:
  - Missing environment variables
  - Database not connected
  - Build script permissions (make sure `build.sh` is executable)

### **App Crashes on Start?**
- Check `ALLOWED_HOSTS` includes your domain
- Verify `DATABASE_URL` is set
- Check logs for Python errors

### **Static Files Not Loading?**
- Already handled with WhiteNoise!
- `build.sh` runs `collectstatic`

### **Admin User Doesn't Exist?**
Run in Render/Railway shell:
```bash
python manage.py shell
```
Then:
```python
from django.contrib.auth.models import User
User.objects.create_superuser('mohitg2', 'mohitg2@example.com', 'graingerlibrary')
```

---

## 🎯 **For Your Presentation**

If you want to show the live deployed version:

1. **Deploy NOW** (takes 10 mins)
2. **Add a few stock cards** with data
3. **Create 2-3 tags** (Tech, Growth, Watch)
4. **Use the deployed URL** in your demo

**Benefits:**
- ✅ Shows production deployment skills
- ✅ No localhost issues during presentation
- ✅ Real URL to share with judges
- ✅ Proves it's a real application

---

## 📞 **Quick Links**

- **Your GitHub:** https://github.com/AlikhanIllini/Final_Project_Alikhan_alikhan4
- **Render:** https://render.com/
- **Railway:** https://railway.app/

---

## ✅ **Next Steps RIGHT NOW:**

```bash
# Your code is already pushed! ✓

# Now choose:
# Option A: Deploy to Render (10 minutes) - FREE
# Option B: Deploy to Railway (5 minutes) - $5 credit
# Option C: Just run locally - EASIEST

# For presentation, I recommend deploying to Render or Railway!
```

**Everything is ready for deployment! 🚀**

