# Render Redeploy Checklist

## ✅ Pre-Deployment

- [ ] Commit and push all code
  ```bash
  git add .
  git commit -m "Prepare for fresh Render deployment"
  git push
  ```

## 🗑️ Delete Old Service

- [ ] Go to https://dashboard.render.com
- [ ] Select backend service
- [ ] Settings → Delete Web Service
- [ ] **DON'T delete Database or Redis!**

## 📝 Get Required Info

Before creating new service, gather these:

- [ ] **Database URL:** Dashboard → PostgreSQL → Connection String (Internal)
  ```
  Copy this: postgresql://user:pass@host/db
  ```

- [ ] **Redis URL:** Dashboard → Redis → Connection String (Internal)
  ```
  Copy this: redis://red-xxxxx:6379
  ```

- [ ] **Generate JWT Secret:** Run this in PowerShell:
  ```powershell
  -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
  ```

- [ ] **Vercel URL:** Your frontend URL
  ```
  Example: https://indostar.vercel.app
  ```

## 🚀 Create New Service

- [ ] Dashboard → New + → Web Service
- [ ] Connect GitHub → Select repository
- [ ] Configure:
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

## 🔐 Add Environment Variables

Click "Advanced" and add these:

### Required (Must Have)
- [ ] `DATABASE_URL` = (paste from above)
- [ ] `REDIS_URL` = (paste from above)
- [ ] `JWT_SECRET_KEY` = (paste generated secret)
- [ ] `JWT_ALGORITHM` = `HS256`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` = `60`
- [ ] `REFRESH_TOKEN_EXPIRE_DAYS` = `7`
- [ ] `ENVIRONMENT` = `production`
- [ ] `FRONTEND_URL` = (your Vercel URL)

### Optional (Add if you have them)
- [ ] `RAZORPAY_KEY_ID`
- [ ] `RAZORPAY_KEY_SECRET`
- [ ] `RAZORPAY_WEBHOOK_SECRET`
- [ ] `TWILIO_ACCOUNT_SID`
- [ ] `TWILIO_AUTH_TOKEN`
- [ ] `TWILIO_PHONE_NUMBER`
- [ ] `SMS_PROVIDER` = `twilio`
- [ ] `SENDGRID_API_KEY`
- [ ] `SENDGRID_FROM_EMAIL`
- [ ] `EMAIL_PROVIDER` = `sendgrid`
- [ ] `GOOGLE_OAUTH_CLIENT_ID`
- [ ] `GOOGLE_OAUTH_CLIENT_SECRET`

## 🎬 Deploy

- [ ] Click "Create Web Service"
- [ ] Wait 3-5 minutes
- [ ] Watch Logs tab for migration messages

## ✅ Verify

Test these URLs (replace with your actual URL):

- [ ] Health: `https://indostarnaturals-backend.onrender.com/health`
  - Should return: `{"status": "healthy"}`

- [ ] Categories: `https://indostarnaturals-backend.onrender.com/api/v1/categories`
  - Should return: `[]` (not 500!)

- [ ] Products: `https://indostarnaturals-backend.onrender.com/api/v1/products`
  - Should return: `{"items": [], "total": 0, ...}`

## 🎨 Update Frontend

- [ ] Go to Vercel Dashboard
- [ ] Select your project
- [ ] Settings → Environment Variables
- [ ] Update `VITE_API_BASE_URL` to new backend URL
- [ ] Deployments → Redeploy

## 🧪 Test Frontend

- [ ] Visit your Vercel URL
- [ ] Open DevTools (F12) → Console
- [ ] Check for errors
- [ ] Try browsing products
- [ ] Verify no CORS errors

## 🎉 Done!

Your app should now be fully deployed with:
- ✅ Backend running on Render
- ✅ Database tables created (migrations ran)
- ✅ Frontend connected to backend
- ✅ No 500 errors

## 📝 Notes

**Save these for future reference:**
- Backend URL: ___________________________
- Database URL: ___________________________
- Redis URL: ___________________________
- JWT Secret: ___________________________
- Frontend URL: ___________________________

## 🆘 If Something Goes Wrong

1. **Check Logs:** Dashboard → Your Service → Logs
2. **Check Environment Variables:** Settings → Environment
3. **Verify Database:** Dashboard → PostgreSQL → Status
4. **Verify Redis:** Dashboard → Redis → Status
5. **See:** `RENDER_FRESH_DEPLOYMENT.md` for detailed troubleshooting
