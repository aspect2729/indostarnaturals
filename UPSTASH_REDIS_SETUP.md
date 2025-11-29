# Upstash Redis Setup for Render

## Step 1: Create Upstash Redis Database

1. Go to **https://upstash.com/**
2. Click **"Sign Up"** or **"Login"** (use GitHub for quick signup)
3. Once logged in, click **"Create Database"**
4. Configure your database:
   - **Name:** `indostar-naturals-redis`
   - **Type:** Select **Regional** (faster, free tier)
   - **Region:** Choose closest to your Render region (e.g., `us-east-1` if Render is in Ohio)
   - **TLS:** Keep enabled (recommended)
5. Click **"Create"**

## Step 2: Get Redis Connection URL

After creating the database, you'll see the dashboard with connection details:

1. Look for **"REST API"** section or **"Redis Connect"** tab
2. Copy the **UPSTASH_REDIS_REST_URL** - it looks like:
   ```
   redis://default:YOUR_PASSWORD@us1-example-12345.upstash.io:6379
   ```
   OR the newer format:
   ```
   rediss://default:YOUR_PASSWORD@us1-example-12345.upstash.io:6379
   ```

**Important:** Copy the full URL including the password!

## Step 3: Add Redis URL to Render

1. Go to **https://dashboard.render.com/**
2. Click on your **Backend Service** (the Python/FastAPI service)
3. Go to **"Environment"** tab on the left
4. Click **"Add Environment Variable"**
5. Add the Redis URL:
   - **Key:** `REDIS_URL`
   - **Value:** Paste the Upstash Redis URL you copied
   
   Example:
   ```
   redis://default:AbCdEf123456@us1-example-12345.upstash.io:6379
   ```

6. Click **"Save Changes"**

## Step 4: Verify Deployment

After saving, Render will automatically redeploy your backend with the new Redis connection.

1. Wait for deployment to complete (2-3 minutes)
2. Check your backend logs in Render:
   - Look for: `✅ Redis connection successful`
   - No more Redis warnings!

## Step 5: Test Redis Connection

Test that Redis is working by checking your API:

```powershell
# Test health endpoint
curl https://your-backend.onrender.com/health
```

You should see Redis status as healthy!

## Upstash Free Tier Limits

- **10,000 commands per day** (resets daily)
- **256 MB storage**
- **TLS encryption included**
- **No credit card required**

This is perfect for development and small production apps!

## Troubleshooting

### Issue: "Connection refused" or "Connection timeout"

**Solution:** Make sure you copied the full URL including:
- Protocol: `redis://` or `rediss://`
- Username: `default`
- Password: The long string after `default:`
- Host and port

### Issue: "SSL/TLS error"

**Solution:** Use `rediss://` (with double 's') for TLS connections

### Issue: Still seeing Redis warnings

**Solution:** 
1. Check that `REDIS_URL` environment variable is set in Render
2. Restart your Render service manually
3. Check logs for connection errors

## Alternative: Redis Labs (RedisCloud)

If Upstash doesn't work, try Redis Labs:

1. Go to **https://redis.com/try-free/**
2. Sign up for free account
3. Create new database (30MB free)
4. Copy connection URL
5. Add to Render as `REDIS_URL`

---

## Quick Summary

✅ Create Upstash account
✅ Create Redis database
✅ Copy Redis URL
✅ Add to Render environment variables
✅ Wait for auto-redeploy
✅ Check logs - no more warnings!
