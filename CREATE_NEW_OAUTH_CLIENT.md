# Create New Google OAuth Client (Quick Guide)

If you're still having issues, create a fresh OAuth client:

## Step 1: Create New OAuth Client

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click **+ CREATE CREDENTIALS**
3. Select **OAuth client ID**
4. Application type: **Web application**
5. Name: `IndoStar Naturals Local Dev`

## Step 2: Configure Origins

**Authorized JavaScript origins:**
```
http://localhost:5173
http://localhost:8000
```

**Authorized redirect URIs:**
```
http://localhost:5173
```

## Step 3: Get Credentials

After clicking CREATE, you'll see:
- Client ID (starts with numbers, ends with .apps.googleusercontent.com)
- Client Secret (starts with GOCSPX-)

Copy both!

## Step 4: Update Your .env Files

### Frontend: `frontend/.env`
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=YOUR_NEW_CLIENT_ID_HERE
```

### Backend: `backend/.env`
```env
# ... other settings ...

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=YOUR_NEW_CLIENT_ID_HERE
GOOGLE_OAUTH_CLIENT_SECRET=YOUR_NEW_CLIENT_SECRET_HERE

# ... rest of settings ...
```

## Step 5: Restart Everything

```powershell
# Stop backend
Get-Process -Name python | Where-Object {$_.Path -like "*backend*"} | Stop-Process -Force

# Start backend
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# In another terminal, restart frontend
cd frontend
npm run dev
```

## Step 6: Test

1. Open **NEW incognito window**
2. Go to `http://localhost:5173`
3. Click Sign In
4. Try Google Sign-In button
5. Should work immediately!

## Why Create a New One?

- Fresh start with no cached issues
- Ensures correct configuration
- Takes only 2 minutes
- Old client might have permission issues

## Keep the Old Client

Don't delete your old OAuth client - you might need it for production or other environments.
