# CORS Fix for Vercel + Render Deployment

## Problem
The frontend on Vercel cannot access the backend on Render due to CORS errors.

## Solution Applied

### 1. Backend Code Changes
Updated `backend/app/main.py` to:
- Allow all Vercel preview deployment URLs (pattern: `https://indostarnaturals-*.vercel.app`)
- Added custom CORS middleware to handle dynamic origin checking
- Maintains security by only allowing known patterns

### 2. Environment Variable Fix on Render

You need to update the `FRONTEND_URL` environment variable on Render:

**Current (incorrect):**
```
FRONTEND_URL=http://indostarnaturals.vercel.app
```

**Should be:**
```
FRONTEND_URL=https://indostarnaturals.vercel.app
```

### Steps to Fix on Render:

1. Go to https://dashboard.render.com
2. Select your backend service: `indostarnaturals`
3. Click on "Environment" in the left sidebar
4. Find `FRONTEND_URL` and update it to: `https://indostarnaturals.vercel.app`
5. Click "Save Changes"
6. Render will automatically redeploy your service

### 3. Deploy the Code Changes

After updating the environment variable, deploy the updated code:

```powershell
# Commit the changes
git add backend/app/main.py
git commit -m "Fix CORS to allow Vercel preview deployments"
git push origin main
```

Render will automatically detect the push and redeploy.

### 4. Verify the Fix

After deployment completes (usually 2-3 minutes):

1. Open your Vercel frontend: https://indostarnaturals-qrsek0y16-adviks-projects-996cbcc2.vercel.app
2. Open browser DevTools (F12)
3. Try to load products or login
4. Check the Console - CORS errors should be gone

### What Changed

The new CORS configuration now allows:
- ✅ `http://localhost:5173` (local development)
- ✅ `https://indostarnaturals.vercel.app` (production)
- ✅ `https://indostarnaturals-*.vercel.app` (all Vercel preview deployments)

This means any Vercel preview deployment will work without needing to update the backend.

### Google OAuth 403 Error

The error `[GSI_LOGGER]: The given origin is not allowed for the given client ID` is separate from CORS.

To fix this:
1. Go to https://console.cloud.google.com/apis/credentials
2. Select your OAuth 2.0 Client ID
3. Under "Authorized JavaScript origins", add:
   - `https://indostarnaturals-qrsek0y16-adviks-projects-996cbcc2.vercel.app`
   - Or use a wildcard if Google supports it for your domain
4. Under "Authorized redirect URIs", add:
   - `https://indostarnaturals-qrsek0y16-adviks-projects-996cbcc2.vercel.app`

Note: For production, you should use a custom domain instead of Vercel's preview URLs.
