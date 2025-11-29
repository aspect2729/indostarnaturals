# Render Free Tier Setup (No Shell Access)

Since you're on Render's free tier without shell access, we'll configure automatic migrations through the build process.

## Step 1: Update Render Build Command

1. **Go to Render Dashboard**
   - Navigate to: https://dashboard.render.com
   - Select your backend service: `indostar-naturals-backend`

2. **Go to Settings**
   - Click "Settings" in the left sidebar
   - Scroll to "Build & Deploy" section

3. **Update Build Command**
   
   Change the **Build Command** to:
   ```bash
   chmod +x render-build.sh && ./render-build.sh
   ```
   
   OR if that doesn't work, use this single-line command:
   ```bash
   pip install --upgrade pip && pip install -r requirements.txt && alembic upgrade head
   ```

4. **Save Changes**
   - Click "Save Changes" button
   - This will trigger a new deployment automatically

## Step 2: Wait for Deployment

1. **Monitor Deployment**
   - Go to "Events" tab
   - Watch the build logs
   - Look for:
     ```
     📦 Installing Python dependencies...
     🔄 Running database migrations...
     INFO  [alembic.runtime.migration] Running upgrade -> 001_initial_schema
     INFO  [alembic.runtime.migration] Running upgrade 001 -> 002_create_users_table
     ...
     ✅ Build completed successfully!
     ```

2. **Deployment Time**
   - Free tier deployments take 2-5 minutes
   - Be patient, migrations might take a minute

## Step 3: Verify Migrations Ran

Once deployment completes, test your API:

### Test 1: Health Check
```bash
curl https://indostarnaturals.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy"
}
```

### Test 2: Categories Endpoint
```bash
curl https://indostarnaturals.onrender.com/api/v1/categories
```

Expected response (empty array, not 500 error):
```json
[]
```

### Test 3: Products Endpoint
```bash
curl https://indostarnaturals.onrender.com/api/v1/products
```

Expected response:
```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

## Step 4: Check Logs

1. **Go to Logs Tab**
   - Dashboard → Your Service → Logs
   - Look for any errors
   - Should see successful startup messages

2. **Look for Migration Success**
   - In the deployment logs, you should see:
   ```
   INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
   INFO  [alembic.runtime.migration] Will assume transactional DDL.
   INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial_schema
   ...
   ```

## Troubleshooting

### Issue: Build Command Not Found

If you get "render-build.sh: not found", use the inline command instead:

**Build Command:**
```bash
pip install --upgrade pip && pip install -r requirements.txt && alembic upgrade head
```

### Issue: Permission Denied

If you get permission errors, the script isn't executable. Use the inline command above.

### Issue: Alembic Not Found

If you get "alembic: command not found":

**Build Command:**
```bash
pip install --upgrade pip && pip install -r requirements.txt && python -m alembic upgrade head
```

### Issue: Database Connection Failed

Check your environment variables:

1. Go to Settings → Environment
2. Verify `DATABASE_URL` is set correctly
3. It should look like: `postgresql://user:password@host/database`
4. Make sure it's the **Internal Database URL** from your Render PostgreSQL instance

### Issue: Migration Already Applied

If you see "Target database is not up to date" or similar:

This is actually good! It means migrations ran before. Just verify the API works.

### Issue: Still Getting 500 Errors

1. **Check Logs** for specific errors
2. **Verify Environment Variables** are all set
3. **Check Database** is running (Dashboard → Your Database)
4. **Try Manual Redeploy**: Settings → Manual Deploy → Deploy latest commit

## Alternative: Create Migration Endpoint (Temporary)

If the build command approach doesn't work, we can create a temporary endpoint to run migrations:

<function_calls>
<invoke name="readFile">
<parameter name="path">backend/app/main.py