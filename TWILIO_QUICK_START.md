# Twilio OTP Quick Start

Quick reference for setting up Twilio OTP in 5 minutes.

## 1. Get Twilio Credentials (2 minutes)

1. Sign up at https://www.twilio.com/try-twilio
2. Get from Console (https://console.twilio.com/):
   - **Account SID** (starts with "AC...")
   - **Auth Token** (click "Show")
3. Buy a phone number:
   - Go to **Phone Numbers** → **Buy a number**
   - Select country and SMS capability
   - Purchase (free with trial credit)

## 2. Update .env File (1 minute)

Edit `backend/.env`:

```env
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+15551234567
```

## 3. Test Setup (2 minutes)

```bash
cd backend

# Test configuration
python test_twilio_otp.py

# Test with your phone (must be verified for trial accounts)
python test_twilio_otp.py +919876543210
```

## 4. Verify Phone Number (Trial Accounts Only)

For trial accounts, verify your test number:
1. Go to **Phone Numbers** → **Verified Caller IDs**
2. Click **Add a new number**
3. Enter your phone and verify with code

## 5. Test API

```bash
# Start backend
python -m uvicorn app.main:app --reload

# Send OTP
curl -X POST http://localhost:8000/api/v1/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'

# Verify OTP (use code from SMS)
curl -X POST http://localhost:8000/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210", "otp": "123456"}'
```

## Common Issues

### "The 'To' number is not a valid phone number"
- Use E.164 format: `+919876543210` (not `9876543210`)

### "Trial accounts cannot send to unverified numbers"
- Verify number in Twilio Console
- Or upgrade from trial account

### "Authentication Error"
- Check Account SID and Auth Token
- Remove extra spaces from .env
- Restart backend server

### Redis Connection Error
- Start Redis: `redis-server`
- Check: `redis-cli ping` → should return `PONG`

## Phone Number Format

Always use E.164 format:
- India: `+919876543210`
- US: `+15551234567`
- UK: `+447911123456`

## Development Mode

To test without sending real SMS:

```env
SMS_PROVIDER=development
```

OTPs will print to console instead.

## Cost

- Trial: $15 free credit
- SMS to India: ~$0.0075 per message
- 1000 users/month ≈ $15/month

## Production Checklist

- [ ] Upgrade from trial account
- [ ] Complete India regulatory compliance
- [ ] Use Messaging Service (recommended)
- [ ] Set up usage alerts
- [ ] Implement CAPTCHA
- [ ] Monitor Twilio Console logs

## Need More Help?

See `TWILIO_OTP_SETUP_GUIDE.md` for detailed instructions.
