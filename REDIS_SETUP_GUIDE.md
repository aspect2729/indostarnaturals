# Redis Setup Guide

## Problem
The backend requires Redis for:
- OTP storage and verification
- Rate limiting
- Session management
- Token cleanup

Without Redis, you'll get 500 errors when trying to log in.

## Solution Options

### Option 1: Start Docker Desktop (Recommended)
1. Start Docker Desktop
2. Run Redis container:
   ```powershell
   # If container doesn't exist:
   docker run -d -p 6379:6379 --name indostar_redis redis:7-alpine
   
   # If container exists but is stopped:
   docker start indostar_redis
   ```
3. Verify Redis is running:
   ```powershell
   docker ps
   # Or use our check script:
   .\check-redis.ps1
   ```

### Option 2: Use Docker Compose
1. Start Docker Desktop
2. Run the full stack:
   ```powershell
   docker-compose up redis -d
   ```

### Option 3: Install Redis for Windows
1. Download Redis for Windows from: https://github.com/microsoftarchive/redis/releases
2. Install and start the Redis service
3. Verify it's running on port 6379

## Verify Redis is Working

After starting Redis, check the backend health:
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

## Current Status

Based on the error logs:
- ✅ Backend is running on port 8000
- ✅ PostgreSQL is running
- ❌ Redis is NOT running (causing 500 errors)
- ❌ Docker Desktop is NOT running

## Quick Fix

Run these commands to start Redis:
```powershell
# Start Docker Desktop first, then:

# If container exists (most common):
docker start indostar_redis

# If container doesn't exist:
docker run -d -p 6379:6379 --name indostar_redis redis:7-alpine
```

**Important**: After starting Redis, you MUST restart your backend server:
```powershell
# Stop the backend (Ctrl+C in the terminal where it's running)
# Then restart it:
.\start-backend.ps1
```
