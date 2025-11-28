# Quick Fix Steps - Cart 403 Error

## Current Status
✅ Redis is now running
✅ Code fixes are in place
❌ Backend needs to be restarted to connect to Redis

## Steps to Fix

### Step 1: Stop the Current Backend
In the terminal where the backend is running, press `Ctrl+C` to stop it.

### Step 2: Restart the Backend
Run one of these commands:

**Option A: Using the updated script**
```powershell
.\start-backend.ps1
```

**Option B: Manual start**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Verify Backend Health
Open a new terminal and run:
```powershell
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

### Step 4: Test Login
1. Go to http://localhost:5173/login
2. Enter a phone number (e.g., +919876543210)
3. Click "Send OTP"
4. Should work without 500 errors!

### Step 5: Test Cart
1. After logging in, go to http://localhost:5173/products
2. Click "Add to Cart" on any product
3. Should work without 403 errors!

## Debug Page
Visit http://localhost:5173/test to see:
- Authentication status
- Redis connection status
- Test cart functionality

## If Issues Persist

### Redis Not Connecting
```powershell
# Check Redis
.\check-redis.ps1

# Restart Redis if needed
docker restart indostar_redis
```

### Backend Still Shows Redis Unhealthy
Make sure you restarted the backend AFTER starting Redis.

### Still Getting 403 on Cart
Make sure you're logged in. Check the test page at /test to verify authentication.

## Summary of What Was Fixed

1. **Frontend**: Added authentication checks before cart operations
2. **Backend**: Added better error handling for Redis connection
3. **Redis**: Started the Redis container
4. **Scripts**: Updated start-backend.ps1 to use Docker Redis

All code changes are complete. You just need to restart the backend!
