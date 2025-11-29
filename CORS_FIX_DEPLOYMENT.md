# CORS Fix - Deployment Instructions

## What Was Fixed

Updated `backend/app/main.py` to explicitly allow your Vercel domain:
- Added `https://indostarnaturals.vercel.app` to allowed origins
- Added `https://indostarnaturals-git-main.vercel.app` for git branch deployments
- Fixed wildcard pattern issue (FastAPI doesn't support `*.vercel.app`)

## Deploy to Render

### Option 1: Git Push (Recommended)

```powershell
# Stage the changes
git add backend/app/main.py

# Commit
git commit -m "Fix CORS for Vercel deployment"

# Push to your repository
git push origin main
```

Render will automatically detect the push and redeploy your backend.

### Option 2: Manual Redeploy

If you don't want to commit yet:

1. Go to Render Dashboard
2. Select your backend service
3. Click "Manual Deploy" → "Deploy latest commit"

## Verify Environment Variables in Render

Make sure these are set in Render → Your Service → Environment:

```
FRONTEND_URL=https://indostarnaturals.vercel.app
BACKEND_URL=https://indostarnaturals.onrender.com
ENVIRONMENT=production
```

## After Deployment

1. Wait for Render to finish deploying (2-3 minutes)
2. Check the logs in Render dashboard for: `CORS allowed origins: [...]`
3. Test your Vercel app: https://indostarnaturals.vercel.app
4. Try sending OTP - it should work now!

## Testing

Open browser console on your Vercel app and try:
1. Click "Send OTP"
2. Check Network tab - should see successful POST to `/api/v1/auth/send-otp`
3. No CORS errors in console

## Troubleshooting

**If CORS error persists:**
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+F5)
- Check Render logs for "CORS allowed origins" message
- Verify FRONTEND_URL is set correctly in Render

**If backend is slow to respond:**
- Render free tier spins down after 15 minutes
- First request may take 30-60 seconds to wake up
- Consider upgrading to paid plan for always-on service

## Additional Vercel Domains

If you have preview deployments or other Vercel URLs, add them to the `allowed_origins` list in `backend/app/main.py`:

```python
allowed_origins.extend([
    "https://indostarnaturals.vercel.app",
    "https://indostarnaturals-git-main.vercel.app",
    "https://your-preview-url.vercel.app",  # Add more as needed
])
```
