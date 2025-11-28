# Owner Login Credentials

## Method 1: Phone + OTP (Recommended)

Since you're in development mode, here's how to log in:

### Step 1: Request OTP
1. Go to http://localhost:5173
2. Click "Login" or the user icon
3. Enter phone: `+919999999999`
4. Click "Send OTP"

### Step 2: Get OTP from Backend Console
The OTP will be printed in your backend console/terminal where you ran `uvicorn`. Look for:
```
[DEV] OTP for +919999999999: 123456
```

### Step 3: Enter OTP
1. Copy the 6-digit OTP from the backend console
2. Enter it in the login form
3. Click "Verify" or "Login"

## Method 2: Direct API Test

You can test the login flow using PowerShell:

```powershell
# Step 1: Send OTP
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/send-otp" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"phone":"+919999999999"}' `
    -UseBasicParsing

# Step 2: Check backend console for OTP (e.g., 123456)

# Step 3: Verify OTP (replace 123456 with actual OTP)
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/verify-otp" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"phone":"+919999999999","otp":"123456"}' `
    -UseBasicParsing
```

## Owner Account Details

- **Phone:** `+919999999999`
- **Email:** `owner@indostarnaturals.com`
- **Name:** System Owner
- **Role:** owner
- **Status:** Active

## Troubleshooting

### "OTP not found" or "Invalid OTP"
- Make sure Redis is running: `docker ps` (should show redis container)
- Check backend console for the actual OTP code
- OTP expires after 10 minutes - request a new one if needed

### Backend not showing OTP
- Verify `SMS_PROVIDER=development` in `backend/.env`
- Check backend console/terminal output
- Restart backend if needed

### Redis not running
```powershell
docker start redis
# or
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

### Backend not running
```powershell
cd backend
uvicorn app.main:app --reload
```

## Alternative: Create Test Script

If you want to automate this, check your backend console after running:
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/send-otp" -Method POST -ContentType "application/json" -Body '{"phone":"+919999999999"}' -UseBasicParsing
```

Then look at the terminal where your backend is running for the OTP code.
