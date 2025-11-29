# Google OAuth Owner Email Configuration

## What Was Done

Added support for authorizing specific email addresses to automatically receive the **OWNER** role when signing in with Google OAuth.

## Configuration

The email `chandra.gudodagi@gmail.com` has been added as an authorized owner email.

### Backend Configuration

**File: `backend/.env`**
```env
GOOGLE_OAUTH_OWNER_EMAILS=chandra.gudodagi@gmail.com
```

You can add multiple emails by separating them with commas:
```env
GOOGLE_OAUTH_OWNER_EMAILS=chandra.gudodagi@gmail.com,another@example.com
```

## How It Works

1. When a user signs in with Google OAuth, the system checks their email address
2. If the email matches one in the `GOOGLE_OAUTH_OWNER_EMAILS` list, they are assigned the **OWNER** role
3. If not, they receive the default **CONSUMER** role

## Testing

1. **Restart the backend** to load the new environment variable:
   ```powershell
   .\restart-backend.ps1
   ```

2. **Sign in with Google** using `chandra.gudodagi@gmail.com`

3. **Verify owner access** - you should have access to:
   - Product management
   - Order management
   - User management
   - Analytics dashboard
   - All owner-level features

## Important Notes

- Email matching is **case-insensitive** (CHANDRA.GUDODAGI@GMAIL.COM = chandra.gudodagi@gmail.com)
- Changes to the `.env` file require a backend restart
- This only affects **new users** created via Google OAuth
- Existing users will keep their current role (you may need to manually update their role in the database)

## Updating Existing User Role

If the user already exists in the database with a different role, you'll need to update it manually:

```sql
UPDATE users 
SET role = 'owner' 
WHERE email = 'chandra.gudodagi@gmail.com';
```

Or use the admin interface to change the user's role.

## Production Setup

For production, make sure to:
1. Add the production owner emails to the production `.env` file
2. Keep this list secure and limited to trusted administrators
3. Consider using a secrets manager instead of plain text in `.env`

## Files Modified

- `backend/app/core/config.py` - Added `GOOGLE_OAUTH_OWNER_EMAILS` setting
- `backend/app/services/oauth_service.py` - Added logic to check owner emails and assign role
- `backend/.env` - Added the authorized owner email
- `backend/.env.example` - Documented the new setting
