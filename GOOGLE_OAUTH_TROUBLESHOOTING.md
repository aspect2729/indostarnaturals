# Google OAuth Troubleshooting Checklist

## Step 1: Verify Google Cloud Console Configuration

Go to [Google Cloud Console Credentials](https://console.cloud.google.com/apis/credentials)

### Check Your OAuth 2.0 Client ID

1. Find client ID: `574241104738-58rv0c6t3v8520fv8hlubirctj9ekqur`
2. Click the **Edit** (pencil) icon

### Verify Authorized JavaScript Origins

Make sure these EXACT URLs are listed (no trailing slashes):
```
http://localhost:5173
http://localhost:8000
```

**Common Mistakes:**
- ❌ `http://localhost:5173/` (trailing slash)
- ❌ `https://localhost:5173` (https instead of http)
- ❌ `http://127.0.0.1:5173` (use localhost, not 127.0.0.1)

### Verify Authorized Redirect URIs (Optional but recommended)

Add these:
```
http://localhost:5173
http://localhost:8000
```

## Step 2: Clear Browser Cache

After updating Google Cloud Console:

1. **Hard Refresh:** Press `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
2. **Or use Incognito Mode:** Open a new incognito/private window
3. **Or Clear Cookies:**
   - Open DevTools (F12)
   - Go to Application tab
   - Clear cookies for `localhost` and `accounts.google.com`

## Step 3: Wait for Propagation

Google changes can take **5-10 minutes** to propagate. Be patient!

## Step 4: Check Backend Logs

The 500 error suggests a backend issue. Let's check what's happening:

### Option A: Check Running Backend Logs

If backend is running, check the terminal where it's running for error messages.

### Option B: Test Backend Directly

```powershell
# Test if backend is running
curl http://localhost:8000/docs

# Or in PowerShell
Invoke-WebRequest -Uri http://localhost:8000/docs
```

## Step 5: Temporary Workaround - Disable Google Sign-In

If you need to continue development, you can temporarily hide the Google Sign-In button:

### Edit `frontend/src/components/AuthModal.tsx`

Comment out the GoogleSignInButton:

```tsx
{/* Temporarily disabled Google Sign-In */}
{/* <GoogleSignInButton onSuccess={onClose} /> */}
```

Then use OTP authentication instead.

## Step 6: Alternative - Use OTP Authentication

The OTP (phone) authentication should work without any Google configuration:

1. Click "Sign In"
2. Enter phone number (format: +919876543210)
3. Click "Send OTP"
4. Enter the OTP code
5. Click "Verify"

**Note:** In development, check your backend logs for the OTP code since SMS might not be configured.

## Common Issues & Solutions

### Issue: "The given origin is not allowed"

**Solution:**
- Double-check the URLs in Google Cloud Console
- Make sure there are NO trailing slashes
- Use `http://localhost:5173` not `http://127.0.0.1:5173`
- Wait 5-10 minutes after making changes
- Clear browser cache

### Issue: Backend 500 Error

**Possible Causes:**
1. Backend not running
2. Database connection issue
3. Missing environment variables
4. Google token verification failing

**Check:**
```powershell
# Check if backend is running
netstat -ano | findstr :8000

# Check backend logs
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Issue: Cross-Origin-Opener-Policy Error

This is a warning from Google's iframe and won't prevent authentication if the 403 is fixed.

## Testing After Fixes

1. Clear browser cache completely
2. Open incognito window
3. Navigate to `http://localhost:5173`
4. Try Google Sign-In
5. Check browser console for errors
6. Check backend terminal for logs

## Still Not Working?

### Create a New OAuth Client

If nothing works, create a fresh OAuth client:

1. Go to [Google Cloud Console Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. Application type: **Web application**
4. Name: `IndoStar Naturals Dev`
5. Authorized JavaScript origins:
   - `http://localhost:5173`
   - `http://localhost:8000`
6. Click **CREATE**
7. Copy the new Client ID
8. Update your `.env` files with the new Client ID

### Update Frontend `.env`:
```
VITE_GOOGLE_CLIENT_ID=YOUR_NEW_CLIENT_ID
```

### Update Backend `.env`:
```
GOOGLE_OAUTH_CLIENT_ID=YOUR_NEW_CLIENT_ID
GOOGLE_OAUTH_CLIENT_SECRET=YOUR_NEW_CLIENT_SECRET
```

### Restart Both Servers:
```powershell
# Stop backend
.\stop-backend.ps1

# Start backend
.\restart-backend.ps1

# In another terminal, restart frontend
cd frontend
npm run dev
```

## For Production

Remember to:
1. Create a separate OAuth client for production
2. Add your production domain (must use HTTPS)
3. Never commit OAuth secrets to git
4. Use environment variables or secrets manager
