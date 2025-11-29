# Quick Fix: Run Migrations on Render (Free Tier)

## Problem
Your backend is deployed but database tables don't exist.

## Solution (Choose One)

### Option A: Automatic (Recommended)

1. **Update Render Build Command:**
   - Go to: https://dashboard.render.com
   - Select your backend service
   - Settings → Build & Deploy
   - Change Build Command to:
   ```
   pip install --upgrade pip && pip install -r requirements.txt && alembic upgrade head
   ```
   - Save Changes (will auto-deploy)

2. **Wait 2-5 minutes** for deployment

3. **Test:**
   ```
   https://indostarnaturals.onrender.com/api/v1/categories
   ```
   Should return `[]` instead of 500 error

---

### Option B: HTTP Endpoint (If Option A fails)

1. **Commit and push new code:**
   ```bash
   git add .
   git commit -m "Add migration endpoint"
   git push
   ```

2. **Wait for Render to deploy** (2-5 minutes)

3. **Run PowerShell script:**
   ```powershell
   .\run-render-migrations.ps1
   ```
   
   OR manually:
   ```powershell
   $headers = @{"X-Admin-Secret" = "YOUR_JWT_SECRET_KEY"}
   Invoke-RestMethod -Uri "https://indostarnaturals.onrender.com/admin/run-migrations" -Method Post -Headers $headers
   ```

4. **Get JWT_SECRET_KEY from:**
   - Render Dashboard → Your Service → Environment → JWT_SECRET_KEY

5. **After success, remove endpoint:**
   ```bash
   git rm backend/app/api/admin_migrations.py
   # Also remove from backend/app/main.py
   git commit -m "Remove migration endpoint"
   git push
   ```

---

## Verification

Test these URLs:
- Health: https://indostarnaturals.onrender.com/health
- Categories: https://indostarnaturals.onrender.com/api/v1/categories
- Products: https://indostarnaturals.onrender.com/api/v1/products

All should return 200 (not 500).

---

## Need More Help?

See: `RENDER_FREE_MIGRATION_GUIDE.md` for detailed troubleshooting.
