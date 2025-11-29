# Fix: Database Tables Missing on Render

## Problem
Your backend is deployed and running on Render, but database tables don't exist:
```
relation "categories" does not exist
relation "products" does not exist
```

## Root Cause
Database migrations haven't been run on the production PostgreSQL database.

## Solution

### Method 1: Run Migrations via Render Shell (Quickest)

1. **Go to Render Dashboard**
   - Navigate to: https://dashboard.render.com
   - Select your backend service: `indostar-naturals-backend`

2. **Open Shell**
   - Click on the "Shell" tab in the left sidebar
   - Wait for shell to connect

3. **Run Migrations**
   ```bash
   alembic upgrade head
   ```

4. **Verify Success**
   - You should see output like:
   ```
   INFO  [alembic.runtime.migration] Running upgrade -> 001_initial_schema
   INFO  [alembic.runtime.migration] Running upgrade 001 -> 002_create_users_table
   ...
   ```

5. **Test Your API**
   - Visit: https://indostarnaturals.onrender.com/api/v1/categories
   - Should now return `[]` instead of 500 error

### Method 2: Update Build Command (Automatic for Future Deploys)

1. **Go to Render Dashboard**
   - Select your backend service

2. **Update Settings**
   - Click "Settings" in left sidebar
   - Scroll to "Build & Deploy" section

3. **Update Build Command**
   - Change from:
   ```bash
   pip install -r requirements.txt
   ```
   - To:
   ```bash
   pip install -r requirements.txt && alembic upgrade head
   ```

4. **Save Changes**
   - Click "Save Changes"
   - This will trigger a new deployment

5. **Wait for Deployment**
   - Migrations will run automatically
   - Check logs to verify success

### Method 3: Use Migration Script

If you prefer a Python script:

1. **In Render Shell, run:**
   ```bash
   python run_migrations.py
   ```

## After Migrations: Seed Initial Data

Once migrations are complete, you may want to add initial data:

### 1. Create Owner Account

```bash
python -c "
from app.models.user import User
from app.core.database import SessionLocal
from app.core.security import get_password_hash

db = SessionLocal()
try:
    # Check if owner exists
    existing = db.query(User).filter(User.email == 'owner@indostarnaturals.com').first()
    if not existing:
        owner = User(
            name='IndoStar Owner',
            email='owner@indostarnaturals.com',
            phone='+919876543210',
            password_hash=get_password_hash('ChangeMe123!'),
            role='owner',
            is_active=True
        )
        db.add(owner)
        db.commit()
        print('✅ Owner account created')
    else:
        print('ℹ️  Owner account already exists')
finally:
    db.close()
"
```

### 2. Seed Sample Products (Optional)

```bash
python seed_products.py
```

Or use the add_sample_products script:
```bash
python add_sample_products.py
```

## Verification Steps

### 1. Check Database Tables

In Render Shell:
```bash
python -c "
from app.core.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
print('📋 Database tables:')
for table in sorted(tables):
    print(f'  ✓ {table}')
"
```

Expected tables:
- users
- addresses
- categories
- products
- product_images
- carts
- cart_items
- orders
- order_items
- subscriptions
- subscription_payments
- payments
- bulk_discount_rules
- audit_logs
- alembic_version

### 2. Test API Endpoints

```bash
# Health check
curl https://indostarnaturals.onrender.com/health

# Categories (should return empty array)
curl https://indostarnaturals.onrender.com/api/v1/categories

# Products (should return empty array)
curl https://indostarnaturals.onrender.com/api/v1/products
```

### 3. Check Frontend

Visit your Vercel frontend:
- https://indostar.vercel.app (or your custom domain)
- Products page should load without errors
- Check browser console for any API errors

## Common Issues

### Issue: "alembic: command not found"

**Solution:** Alembic might not be in PATH. Try:
```bash
python -m alembic upgrade head
```

### Issue: "Can't locate revision identified by 'head'"

**Solution:** Alembic version table might be corrupted. Reset it:
```bash
# Check current version
python -c "from app.core.database import engine; from sqlalchemy import text; with engine.connect() as conn: result = conn.execute(text('SELECT * FROM alembic_version')); print(list(result))"

# If empty or wrong, stamp to latest
alembic stamp head
```

### Issue: "Target database is not up to date"

**Solution:** Run migrations step by step:
```bash
# See current version
alembic current

# See pending migrations
alembic history

# Upgrade one step at a time
alembic upgrade +1
```

### Issue: Migration fails with constraint errors

**Solution:** Database might have partial data. You may need to:
1. Backup any important data
2. Drop all tables
3. Re-run migrations

```bash
# CAUTION: This drops all data!
python -c "
from app.core.database import Base, engine
Base.metadata.drop_all(bind=engine)
print('All tables dropped')
"

# Then run migrations
alembic upgrade head
```

## Prevention: Automated Migrations

To prevent this in the future, update your Render configuration:

### Option A: Build Command (Recommended)
```bash
pip install -r requirements.txt && alembic upgrade head
```

### Option B: Pre-Deploy Hook

Create `backend/render-build.sh`:
```bash
#!/bin/bash
set -e

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🔄 Running database migrations..."
alembic upgrade head

echo "✅ Build complete!"
```

Make it executable:
```bash
chmod +x render-build.sh
```

Update Render Build Command to:
```bash
./render-build.sh
```

## Monitoring

After fixing, monitor your logs:

1. **Render Dashboard → Logs**
   - Watch for any database errors
   - Verify migrations ran successfully

2. **Check Application Logs**
   ```bash
   # In Render Shell
   tail -f /var/log/app.log
   ```

3. **Set Up Alerts**
   - Render → Settings → Notifications
   - Enable email alerts for deployment failures

## Next Steps

1. ✅ Run migrations (Method 1 or 2)
2. ✅ Verify tables exist
3. ✅ Test API endpoints
4. ✅ Create owner account
5. ✅ Seed sample data (optional)
6. ✅ Test frontend
7. ✅ Set up automated migrations
8. ✅ Monitor logs

## Need Help?

If you're still having issues:

1. **Check Render Logs:**
   - Dashboard → Your Service → Logs
   - Look for specific error messages

2. **Verify Environment Variables:**
   - Dashboard → Your Service → Environment
   - Ensure `DATABASE_URL` is set correctly

3. **Test Database Connection:**
   ```bash
   python -c "from app.core.database import engine; engine.connect(); print('✅ Database connected')"
   ```

4. **Check PostgreSQL Status:**
   - Dashboard → Your Database
   - Ensure it's running and healthy

## Summary

The fix is simple: **run `alembic upgrade head` in your Render shell**. This will create all the necessary database tables and your API will start working immediately.
