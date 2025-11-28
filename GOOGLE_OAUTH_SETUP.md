# Google OAuth Setup Guide

## Current Issue

You're seeing a 403 error: "The given origin is not allowed for the given client ID"

This happens because your Google OAuth client isn't configured to allow requests from `http://localhost:5173`.

## Solution: Configure Google Cloud Console

### Step 1: Access Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Select your project (or the project associated with client ID `574241104738-58rv0c6t3v8520fv8hlubirctj9ekqur`)

### Step 2: Navigate to Credentials

1. In the left sidebar, click **APIs & Services**
2. Click **Credentials**
3. Find your OAuth 2.0 Client ID in the list
4. Click the **Edit** (pencil) icon

### Step 3: Add Authorized Origins

Under **Authorized JavaScript origins**, add these URLs:
- `http://localhost:5173` (your frontend)
- `http://localhost:8000` (your backend)
- `http://localhost:5174` (backup frontend port)

### Step 4: Add Authorized Redirect URIs (Optional)

Under **Authorized redirect URIs**, you can add:
- `http://localhost:5173`
- `http://localhost:8000`

### Step 5: Save Changes

Click **Save** at the bottom of the page.

**Note:** Changes may take a few minutes to propagate.

## Testing

After configuring:

1. Clear your browser cache or open an incognito window
2. Navigate to `http://localhost:5173`
3. Try the Google Sign-In button
4. You should no longer see the 403 error

## Alternative: Use OTP Authentication

If you don't want to configure Google OAuth right now, you can use the OTP (One-Time Password) authentication method instead:

1. Click "Sign In" on the homepage
2. Enter your phone number
3. Click "Send OTP"
4. Enter the OTP code received
5. Click "Verify"

## Current Configuration

**Frontend (.env):**
```
VITE_GOOGLE_CLIENT_ID=574241104738-58rv0c6t3v8520fv8hlubirctj9ekqur
```

**Backend (.env):**
```
GOOGLE_OAUTH_CLIENT_ID=574241104738-58rv0c6t3v8520fv8hlubirctj9ekqur
GOOGLE_OAUTH_CLIENT_SECRET=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
```

## Troubleshooting

### Still seeing 403 errors?

1. **Wait a few minutes** - Google's changes can take time to propagate
2. **Clear browser cache** - Old credentials may be cached
3. **Check the correct project** - Make sure you're editing the right OAuth client
4. **Verify the Client ID** - Ensure the client ID in your `.env` files matches the one in Google Cloud Console

### Backend 500 errors?

Check the backend logs for detailed error messages:
```powershell
# View backend logs
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Common issues:
- Missing `google-auth` package (should be in requirements.txt)
- Invalid client secret
- Database connection issues

## Production Setup

For production, you'll need to:

1. Add your production domain to authorized origins
2. Use HTTPS (required by Google)
3. Store credentials securely (environment variables, secrets manager)
4. Consider using a different OAuth client for production

Example production origins:
- `https://yourdomain.com`
- `https://www.yourdomain.com`
- `https://api.yourdomain.com`
