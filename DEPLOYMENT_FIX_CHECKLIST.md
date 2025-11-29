# Deployment Fix Checklist

## Problem
Frontend on Vercel is trying to call `localhost:8000` instead of the Render backend URL, causing OTP and all API calls to fail.

## Solution Steps

### 1. Get Your Backend URL from Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click on your backend service
3. Copy the URL at the top (e.g., `https://indostar-naturals-backend.onrender.com`)

### 2. Configure Vercel Environment Variable

**Option A: Via Vercel Dashboard (Recommended)**

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Click **Add New**
5. Enter:
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: `https://your-backend-name.onrender.com` (paste your Render URL)
   - **Environment**: Check **Production** (and Preview if needed)
6. Click **Save**
7. Go to **Deployments** tab
8. Click the three dots (...) on the latest deployment
9. Click **Redeploy**

**Option B: Via Vercel CLI**

```powershell
# Install Vercel CLI (if not installed)
npm i -g vercel

# Login to Vercel
vercel login

# Link your project (run in project root)
vercel link

# Add environment variable
vercel env add VITE_API_BASE_URL production
# When prompted, enter: https://your-backend-name.onrender.com

# Deploy
vercel --prod
```

### 3. Configure Backend CORS on Render

1. Go to Render Dashboard → Your Backend Service
2. Go to **Environment** tab
3. Find or add `FRONTEND_URL` variable
4. Set value to your Vercel URL (e.g., `https://your-app.vercel.app`)
5. Click **Save Changes**
6. Backend will automatically redeploy

### 4. Verify Backend is Running

Test your backend health endpoint:
```
https://your-backend-name.onrender.com/health
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

### 5. Check Required Backend Environment Variables

Make sure these are set in Render:

**Database & Redis:**
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

**Security:**
- `JWT_SECRET_KEY` - Random secure string
- `JWT_ALGORITHM` - `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES` - `60`

**Twilio (for OTP):**
- `SMS_PROVIDER` - `twilio`
- `TWILIO_ACCOUNT_SID` - From Twilio console
- `TWILIO_AUTH_TOKEN` - From Twilio console
- `TWILIO_PHONE_NUMBER` - Your Twilio phone number

**Application URLs:**
- `FRONTEND_URL` - Your Vercel URL
- `BACKEND_URL` - Your Render URL
- `ENVIRONMENT` - `production`

### 6. Test the Deployment

1. Visit your Vercel URL
2. Open browser DevTools (F12) → Network tab
3. Try to send OTP
4. Check that API calls go to your Render backend (not localhost)
5. Verify no CORS errors in console

### 7. Common Issues & Fixes

**Issue: Still seeing localhost:8000**
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+F5)
- Check Vercel deployment logs to confirm env var is set

**Issue: CORS errors**
- Verify `FRONTEND_URL` in Render matches your Vercel URL exactly
- No trailing slashes in URLs
- Redeploy backend after changing CORS settings

**Issue: OTP not sending**
- Check Twilio credentials in Render
- Verify phone number format: `+919876543210`
- Check Render logs for errors

**Issue: 503 Service Unavailable**
- Backend might be sleeping (Render free tier)
- Wait 30-60 seconds for it to wake up
- Consider upgrading to paid plan for always-on service

## Quick Reference

### Your URLs (Fill these in):
- **Render Backend**: `https://_____________________.onrender.com`
- **Vercel Frontend**: `https://_____________________.vercel.app`

### Environment Variables Summary:

**Vercel (Frontend):**
```
VITE_API_BASE_URL=https://your-backend.onrender.com
VITE_GOOGLE_CLIENT_ID=574241104738-9mb6p11q060t44ilq5ft9hbkpkialtfg.apps.googleusercontent.com
```

**Render (Backend):**
```
FRONTEND_URL=https://your-app.vercel.app
BACKEND_URL=https://your-backend.onrender.com
DATABASE_URL=<from-render-postgres>
REDIS_URL=<from-render-redis>
JWT_SECRET_KEY=<generate-secure-random-string>
TWILIO_ACCOUNT_SID=<from-twilio>
TWILIO_AUTH_TOKEN=<from-twilio>
TWILIO_PHONE_NUMBER=<from-twilio>
SMS_PROVIDER=twilio
ENVIRONMENT=production
```

## Next Steps After Fix

1. Test all authentication flows (OTP, Google OAuth)
2. Test product browsing and cart functionality
3. Test checkout flow
4. Monitor Render logs for any errors
5. Set up monitoring/alerting (optional)

## Need Help?

- Check Vercel deployment logs: Dashboard → Deployments → Click deployment → View Function Logs
- Check Render logs: Dashboard → Your Service → Logs
- Test API directly: Use Postman or curl to test backend endpoints
