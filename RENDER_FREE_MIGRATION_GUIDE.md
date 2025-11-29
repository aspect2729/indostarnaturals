# Complete Guide: Running Migrations on Render Free Tier

Since you don't have shell access on Render's free tier, here are **3 methods** to run migrations:

## 🚀 Method 1: Build Command (Recommended)

This runs migrations automatically on every deployment.

### Steps:

1. **Commit the new build script**
   ```bash
   git add backend/render-build.sh
   git commit -m "Add Render build script with migrations"
   git push
   ```

2. **Update Render Settings**
   - Go to: https://dashboard.render.com
   - Select your backend service
   - Click "Settings" → "Build & Deploy"
   - Change **Build Command** to:
   ```bash
   pip install --upgrade pip && pip install -r requirements.txt && alembic upgrade head
   ```

3. **Save and Deploy**
   - Click "Save Changes"
   - Render will automatically redeploy
   - Watch the logs for migration output

4. **Verify**
   ```bash
   curl https://indostarnaturals.onrender.com/api/v1/categories
   ```
   Should return `[]` instead of 500 error

---

## 🔧 Method 2: HTTP Endpoint (Quick Fix)

Use the temporary admin endpoint to trigger migrations via HTTP.

### Steps:

1. **Commit and push the new code**
   ```bash
   git add backend/app/api/admin_migrations.py backend/app/main.py
   git commit -m "Add temporary migration endpoint"
   git push
   ```

2. **Wait for Render to deploy** (2-5 minutes)
   - Watch deployment in Render dashboard

3. **Get your JWT_SECRET_KEY**
   - Go to Render → Your Service → Environment
   - Copy the value of `JWT_SECRET_KEY`

4. **Run migrations via HTTP**
   
   **Windows PowerShell:**
   ```powershell
   $headers = @{
       "X-Admin-Secret" = "YOUR_JWT_SECRET_KEY_HERE"
   }
   Invoke-RestMethod -Uri "https://indostarnaturals.onrender.com/admin/run-migrations" -Method Post -Headers $headers
   ```

   **Windows CMD:**
   ```cmd
   curl -X POST https://indostarnaturals.onrender.com/admin/run-migrations -H "X-Admin-Secret: YOUR_JWT_SECRET_KEY_HERE"
   ```

   **Git Bash / WSL:**
   ```bash
   curl -X POST https://indostarnaturals.onrender.com/admin/run-migrations \
        -H "X-Admin-Secret: YOUR_JWT_SECRET_KEY_HERE"
   ```

5. **Check response**
   Should return:
   ```json
   {
     "status": "success",
     "message": "Database migrations completed successfully",
     "output": "...",
     "warning": "IMPORTANT: Remove this endpoint after deployment!"
   }
   ```

6. **Verify migrations worked**
   ```bash
   curl https://indostarnaturals.onrender.com/api/v1/categories
   ```

7. **IMPORTANT: Remove the endpoint after success**
   ```bash
   # Remove the admin endpoint for security
   git rm backend/app/api/admin_migrations.py
   
   # Remove from main.py
   # Edit backend/app/main.py and remove:
   # - The import: admin_migrations
   # - The router: app.include_router(admin_migrations.router)
   
   git commit -m "Remove temporary migration endpoint"
   git push
   ```

---

## 🔄 Method 3: Manual Redeploy with Updated Start Command

Modify the start command to run migrations before starting the server.

### Steps:

1. **Go to Render Settings**
   - Dashboard → Your Service → Settings

2. **Update Start Command**
   - Change from:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
   - To:
   ```bash
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Save and Deploy**
   - Click "Save Changes"
   - Service will restart with migrations

⚠️ **Warning:** This runs migrations on every restart, which is not ideal but works for free tier.

---

## ✅ Verification Checklist

After running migrations, verify everything works:

### 1. Check Health Endpoint
```bash
curl https://indostarnaturals.onrender.com/health
```
Expected:
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

### 2. Check Categories
```bash
curl https://indostarnaturals.onrender.com/api/v1/categories
```
Expected: `[]` (empty array, not 500 error)

### 3. Check Products
```bash
curl https://indostarnaturals.onrender.com/api/v1/products
```
Expected:
```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

### 4. Check Frontend
- Visit: https://indostar.vercel.app
- Open browser DevTools → Console
- Should see no 500 errors
- Products page should load (even if empty)

---

## 🐛 Troubleshooting

### Issue: "alembic: command not found"

**Solution:** Use Python module syntax:
```bash
python -m alembic upgrade head
```

Update your Build Command to:
```bash
pip install --upgrade pip && pip install -r requirements.txt && python -m alembic upgrade head
```

### Issue: "Can't locate revision identified by 'head'"

**Solution:** Alembic version table is missing or corrupted.

Use Method 2 (HTTP endpoint) and run:
```bash
curl -X POST https://indostarnaturals.onrender.com/admin/run-migrations \
     -H "X-Admin-Secret: YOUR_JWT_SECRET_KEY"
```

### Issue: "Target database is not up to date"

**Good news!** This means migrations already ran. Just verify the API works.

### Issue: Database connection failed

**Check:**
1. Render Dashboard → Your Database → Status (should be "Available")
2. Environment variable `DATABASE_URL` is set correctly
3. Database is in the same region as your backend service

**Fix:**
- Go to Settings → Environment
- Verify `DATABASE_URL` matches your PostgreSQL Internal URL
- Format: `postgresql://user:password@host/database`

### Issue: Still getting 500 errors after migrations

**Debug steps:**
1. Check Render Logs (Dashboard → Logs tab)
2. Look for specific error messages
3. Verify all environment variables are set
4. Try manual redeploy: Settings → Manual Deploy

---

## 📝 Recommended Approach

**For your situation (free tier, no shell):**

1. ✅ **Use Method 1** (Build Command) - Most reliable
2. ✅ **Use Method 2** (HTTP Endpoint) - If Method 1 fails
3. ❌ **Avoid Method 3** - Runs migrations on every restart

**Best practice:**
- Method 1 for automatic migrations on deploy
- Method 2 as backup for one-time fixes
- Remove Method 2 endpoint after successful migration

---

## 🔐 Security Notes

- The HTTP endpoint requires your `JWT_SECRET_KEY` for authentication
- Never commit secrets to Git
- Remove the admin endpoint after migrations complete
- Don't share your JWT_SECRET_KEY publicly

---

## 📊 Next Steps After Migrations

Once migrations are successful:

1. **Create owner account** (if not exists)
2. **Seed sample products** (optional)
3. **Test authentication flow**
4. **Verify frontend integration**
5. **Remove temporary endpoints**
6. **Set up monitoring**

---

## 🆘 Still Need Help?

If none of these methods work:

1. **Check Render Status**: https://status.render.com
2. **Review Render Logs**: Dashboard → Your Service → Logs
3. **Check Database Logs**: Dashboard → Your Database → Logs
4. **Verify Environment Variables**: Settings → Environment
5. **Try Manual Deploy**: Settings → Manual Deploy → Deploy latest commit

---

## 💡 Pro Tip

For future deployments, Method 1 (Build Command) will automatically run migrations, so you won't face this issue again!
