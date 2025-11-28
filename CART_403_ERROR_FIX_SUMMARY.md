# Cart 403 Error - Root Cause and Fix

## Problem Summary
Users were getting a 403 Forbidden error when trying to add items to cart.

## Root Causes Identified

### 1. Authentication Required (Primary Issue)
- Cart endpoints require user authentication (`get_current_active_user` dependency)
- Users must be logged in before adding items to cart
- Frontend was not checking authentication status before attempting to add items

### 2. Redis Not Running (Blocking Login)
- Redis is required for OTP storage and verification
- Without Redis, users cannot log in (500 error on `/api/v1/auth/send-otp`)
- CORS errors appear because the backend returns 500 before CORS headers are added

## Changes Made

### Frontend Changes

#### 1. CartContext.tsx
- Added authentication check before adding items to cart
- Improved error message handling to show backend error details
- Better error messages for all cart operations

#### 2. ProductCatalogPage.tsx
- Added authentication check before allowing "Add to Cart"
- Redirects to login page if user is not authenticated
- Shows user-friendly toast messages

#### 3. TestPage.tsx
- Added authentication and cart debugging information
- Shows current auth status, user info, and token
- Provides test button to diagnose cart issues

### Backend Changes

#### 1. redis_client.py
- Added graceful handling of Redis connection failures
- Provides clear error messages when Redis is unavailable
- Added `is_redis_available()` helper function

#### 2. otp_service.py
- Added proper error handling for Redis connection errors
- Raises ConnectionError with helpful message when Redis is unavailable

#### 3. auth.py
- Added try-catch for ConnectionError in send-otp endpoint
- Returns 503 Service Unavailable with clear message when Redis is down

### Documentation

#### 1. REDIS_SETUP_GUIDE.md
- Comprehensive guide for setting up Redis
- Multiple options (Docker, Docker Compose, Windows install)
- Troubleshooting steps

#### 2. check-redis.ps1
- PowerShell script to check if Redis is running
- Provides clear instructions if Redis is not running

## How to Fix

### Step 1: Start Redis
```powershell
# Check if Redis is running
.\check-redis.ps1

# If not running, start Docker Desktop and run:
docker run -d -p 6379:6379 --name indostar_redis redis:7-alpine
```

### Step 2: Verify Backend Health
```powershell
curl http://localhost:8000/health
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

### Step 3: Test Login
1. Navigate to http://localhost:5173/login
2. Enter phone number and request OTP
3. Should work without 500 errors

### Step 4: Test Cart
1. Log in successfully
2. Navigate to http://localhost:5173/products
3. Click "Add to Cart" on any product
4. Should work without 403 errors

## Testing

### Debug Page
Navigate to http://localhost:5173/test to see:
- Authentication status
- User information
- Token status
- Cart status
- Test "Add to Cart" button

## Error Messages

### Before Fix
- "Failed to add item to cart: AxiosError"
- 403 Forbidden (confusing)
- No indication that login is required

### After Fix
- "Please log in to add items to cart" (clear message)
- Automatic redirect to login page
- Better error details from backend

## Current Status

✅ Frontend authentication checks added
✅ Better error messages implemented
✅ Redis error handling improved
✅ Documentation created
❌ Redis needs to be started (see REDIS_SETUP_GUIDE.md)

## Next Steps

1. Start Redis using the guide
2. Test the login flow
3. Test adding items to cart
4. Verify all cart operations work correctly
