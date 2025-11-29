# 🚀 START HERE - Complete Fresh Deployment

You don't have a database yet, so let's create everything from scratch!

## ✅ Quick Checklist

### Step 1: Create Database (2 min)
- [ ] Go to https://dashboard.render.com
- [ ] New + → PostgreSQL
- [ ] Name: `indostar-naturals-db`
- [ ] Region: Oregon (Free)
- [ ] Create Database
- [ ] **Copy Internal Database URL** and save it

### Step 2: Create Redis (2 min)
- [ ] New + → Redis
- [ ] Name: `indostar-naturals-redis`
- [ ] Region: Oregon (Free)
- [ ] Create Redis
- [ ] **Copy Internal Redis URL** and save it

### Step 3: Generate JWT Secret (30 sec)
Run in PowerShell:
```powershell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```
- [ ] **Copy the output** and save it

### Step 4: Create Backend Service (5 min)
- [ ] New + → Web Service
- [ ] Connect GitHub → Select `indostarnaturals`
- [ ] Name: `indostarnaturals-backend`
- [ ] Region: Oregon (Free)
- [ ] Branch: `master`
- [ ] Root Directory: `backend`
- [ ] Build Command:
  ```
  pip install --upgrade pip && pip install -r requirements.txt && alembic upgrade head
  ```
- [ ] Start Command:
  ```
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
- [ ] Click "Advanced" → Add environment variables:
  - `DATABASE_URL` = (paste from Step 1)
  - `REDIS_URL` = (paste from Step 2)
  - `JWT_SECRET_KEY` = (paste from Step 3)
  - `JWT_ALGORITHM` = `HS256`
  - `ACCESS_TOKEN_EXPIRE_MINUTES` = `60`
  - `REFRESH_TOKEN_EXPIRE_DAYS` = `7`
  - `ENVIRONMENT` = `production`
  - `FRONTEND_URL` = `https://indostar.vercel.app`
- [ ] Create Web Service

### Step 5: Wait & Watch (3-5 min)
- [ ] Go to Logs tab
- [ ] Watch for "Running database migrations..."
- [ ] Wait for "Your service is live 🎉"

### Step 6: Test (1 min)
Open these URLs:
- [ ] https://indostarnaturals-backend.onrender.com/health
  - Should show: `"status": "healthy"`
- [ ] https://indostarnaturals-backend.onrender.com/api/v1/categories
  - Should show: `[]` (not 500 error!)

### Step 7: Update Frontend (2 min)
- [ ] Go to Vercel Dashboard
- [ ] Settings → Environment Variables
- [ ] Update `VITE_API_BASE_URL` to:
  ```
  https://indostarnaturals-backend.onrender.com
  ```
- [ ] Deployments → Redeploy

## ✅ Done!

Your app is now fully deployed!

---

## 📚 Detailed Guide

For step-by-step instructions with screenshots and troubleshooting:
👉 **See: `RENDER_COMPLETE_FRESH_START.md`**

---

## 🆘 Need Help?

**Common Issues:**
- Build fails → Check Logs tab for specific error
- 500 errors → Verify all environment variables are set
- Database connection failed → Check DATABASE_URL is Internal URL
- Migrations failed → Check Logs for specific migration error

**Get Help:**
- Check `RENDER_COMPLETE_FRESH_START.md` for detailed troubleshooting
- Review Logs tab in Render dashboard
- Verify all environment variables are correct

---

## ⏱️ Total Time: ~15 minutes
## 💰 Total Cost: $0/month (free tier)

Let's go! 🚀
