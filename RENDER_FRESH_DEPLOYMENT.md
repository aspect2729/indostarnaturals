# Fresh Render Deployment Guide (From Scratch)

This guide walks you through deploying to Render from scratch with automatic migrations.

## 🗑️ Step 1: Delete Existing Services

### Delete Backend Service
1. Go to https://dashboard.render.com
2. Click on your backend service (indostarnaturals-backend)
3. Click **Settings** (left sidebar)
4. Scroll to bottom → Click **"Delete Web Service"**
5. Type the service name to confirm
6. Click **Delete**

### Keep Database & Redis
**DON'T delete these!** They contain your data and are free to keep.
- PostgreSQL database
- Redis instance

---

## 📝 Step 2: Create render.yaml (Automatic Configuration)

This file tells Render how to deploy your app automatically.

Create `render.yaml` in your project root with this content:

```yaml
services:
  # Backend Web Service
  - type: web
    name: indostarnaturals-backend
    env: python
    region: oregon
    plan: free
    branch: master
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt && alembic upgrade head
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: indostar-naturals-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: indostar-naturals-redis
          property: connectionString
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: JWT_ALGORITHM
        value: HS256
      - key: ACCESS_TOKEN_EXPIRE_MINUTES
        value: 60
      - key: REFRESH_TOKEN_EXPIRE_DAYS
        value: 7
      - key: ENVIRONMENT
        value: production
      - key: FRONTEND_URL
        value: https://indostar.vercel.app
```

**Important:** This `buildCommand` includes `alembic upgrade head` which runs migrations automatically!

---

## 🚀 Step 3: Deploy New Backend Service

### Option A: Using render.yaml (Recommended)

1. **Commit the render.yaml:**
   ```bash
   git add render.yaml
   git commit -m "Add Render configuration with auto-migrations"
   git push
   ```

2. **Create New Service:**
   - Go to https://dashboard.render.com
   - Click **"New +"** → **"Blueprint"**
   - Connect your GitHub repository
   - Select your repo: `indostarnaturals`
   - Render will detect `render.yaml`
   - Click **"Apply"**

3. **Wait for deployment** (3-5 minutes)

### Option B: Manual Setup (If Blueprint doesn't work)

1. **Create New Web Service:**
   - Dashboard → **"New +"** → **"Web Service"**
   - Connect GitHub repository
   - Select: `indostarnaturals`

2. **Configure Service:**
   - **Name:** `indostarnaturals-backend`
   - **Region:** Oregon (Free)
   - **Branch:** `master`
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:**
     ```
     pip install --upgrade pip && pip install -r requirements.txt && alembic upgrade head
     ```
   - **Start Command:**
     ```
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan:** Free

3. **Add Environment Variables:**
   Click "Advanced" → Add these:

   ```
   DATABASE_URL = <your-postgres-internal-url>
   REDIS_URL = <your-redis-internal-url>
   JWT_SECRET_KEY = <generate-random-string>
   JWT_ALGORITHM = HS256
   ACCESS_TOKEN_EXPIRE_MINUTES = 60
   REFRESH_TOKEN_EXPIRE_DAYS = 7
   ENVIRONMENT = production
   FRONTEND_URL = https://indostar.vercel.app
   
   # Optional (add if you have them):
   RAZORPAY_KEY_ID = <your-key>
   RAZORPAY_KEY_SECRET = <your-secret>
   TWILIO_ACCOUNT_SID = <your-sid>
   TWILIO_AUTH_TOKEN = <your-token>
   TWILIO_PHONE_NUMBER = <your-number>
   SENDGRID_API_KEY = <your-key>
   SENDGRID_FROM_EMAIL = noreply@yourdomain.com
   GOOGLE_OAUTH_CLIENT_ID = <your-client-id>
   GOOGLE_OAUTH_CLIENT_SECRET = <your-secret>
   ```

4. **Get Database & Redis URLs:**
   - Dashboard → Your PostgreSQL → Connection String (Internal)
   - Dashboard → Your Redis → Connection String (Internal)

5. **Click "Create Web Service"**

---

## ✅ Step 4: Verify Deployment

### Watch the Logs
1. Go to your service → **Logs** tab
2. Look for:
   ```
   📦 Installing Python dependencies...
   🔄 Running database migrations...
   INFO  [alembic.runtime.migration] Running upgrade -> 001_initial_schema
   INFO  [alembic.runtime.migration] Running upgrade 001 -> 002_create_users_table
   ...
   ✅ Build completed successfully!
   ==> Your service is live 🎉
   ```

### Test the API
Once deployed, test these URLs:

**1. Health Check:**
```
https://indostarnaturals-backend.onrender.com/health
```
Should return:
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

**2. Categories:**
```
https://indostarnaturals-backend.onrender.com/api/v1/categories
```
Should return: `[]` (not 500 error!)

**3. Products:**
```
https://indostarnaturals-backend.onrender.com/api/v1/products
```
Should return:
```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

---

## 🎨 Step 5: Update Frontend (Vercel)

Your frontend might need the new backend URL.

1. **Go to Vercel Dashboard**
2. Select your project
3. **Settings** → **Environment Variables**
4. Update `VITE_API_BASE_URL`:
   ```
   https://indostarnaturals-backend.onrender.com
   ```
5. **Deployments** → Click "..." → **Redeploy**

---

## 🔐 Step 6: Update CORS (If needed)

If you get CORS errors:

1. **Check backend logs** for CORS messages
2. **Verify FRONTEND_URL** environment variable matches your Vercel URL exactly
3. **Redeploy** if you changed it

---

## 📊 Step 7: Seed Initial Data (Optional)

Once everything works, you can add initial data.

### Create Owner Account

Use the HTTP endpoint (it's still in your code):

```powershell
$headers = @{"X-Admin-Secret" = "YOUR_JWT_SECRET_KEY"}
$body = @{
    email = "owner@indostarnaturals.com"
    password = "ChangeMe123!"
    name = "IndoStar Owner"
    phone = "+919876543210"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://indostarnaturals-backend.onrender.com/api/v1/auth/register" -Method Post -Headers @{"Content-Type"="application/json"} -Body $body
```

Or just register through the frontend!

---

## 🎯 Why This Works Better

**Automatic Migrations:**
- ✅ Migrations run on every deployment
- ✅ No manual intervention needed
- ✅ No shell access required
- ✅ Works on free tier

**Clean Start:**
- ✅ No leftover configuration issues
- ✅ Fresh environment variables
- ✅ Proper build command from the start

---

## 🐛 Troubleshooting

### Build fails with "alembic: command not found"

**Fix:** Update Build Command to:
```
pip install --upgrade pip && pip install -r requirements.txt && python -m alembic upgrade head
```

### Database connection failed

**Check:**
1. DATABASE_URL is set correctly
2. It's the **Internal** URL (not External)
3. Database is in same region as backend
4. Database is running (check status)

### Migrations fail

**Check logs for specific error:**
- Missing environment variables?
- Database permissions?
- Syntax errors in migration files?

### Still getting 500 errors

1. Check Logs tab for specific errors
2. Verify all environment variables are set
3. Test database connection
4. Check Redis connection

---

## 📝 Summary

**What you did:**
1. ✅ Deleted old backend service
2. ✅ Created render.yaml with auto-migrations
3. ✅ Deployed fresh backend service
4. ✅ Migrations ran automatically
5. ✅ Verified API works
6. ✅ Updated frontend

**Result:**
- Backend deployed with all database tables
- Migrations run automatically on every deploy
- No more 500 errors
- Frontend can fetch data

---

## 🚀 Next Steps

1. Register owner account
2. Add products
3. Test the full flow
4. Configure external services (Razorpay, Twilio, etc.)
5. Set up custom domain (optional)

---

## 💡 Pro Tips

- **Free tier** spins down after 15 minutes of inactivity
- **First request** after spin-down takes 30-60 seconds
- **Migrations** run automatically on every deploy
- **Logs** are your friend - check them often!

Good luck! 🎉
