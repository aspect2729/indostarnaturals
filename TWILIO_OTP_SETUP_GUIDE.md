# Twilio OTP Setup Guide

This guide will help you set up Twilio for sending OTP (One-Time Password) SMS messages in the IndoStar Naturals application.

## Prerequisites

- A Twilio account (sign up at https://www.twilio.com/try-twilio)
- Python 3.11+ installed
- Redis server running (for OTP storage)

## Step 1: Create a Twilio Account

1. Go to https://www.twilio.com/try-twilio
2. Sign up for a free trial account
3. Verify your email and phone number
4. You'll receive $15 in trial credit

## Step 2: Get Your Twilio Credentials

After signing up, you'll need three pieces of information:

### 2.1 Account SID and Auth Token

1. Log in to your Twilio Console: https://console.twilio.com/
2. On the dashboard, you'll see:
   - **Account SID**: A string starting with "AC..."
   - **Auth Token**: Click "Show" to reveal it
3. Copy both values - you'll need them for your `.env` file

### 2.2 Get a Twilio Phone Number

1. In the Twilio Console, go to **Phone Numbers** → **Manage** → **Buy a number**
2. Select your country (India for this project)
3. Check the **SMS** capability
4. Search for available numbers
5. Purchase a number (free with trial credit)
6. Copy the phone number in E.164 format (e.g., `+15551234567`)

**Note for India**: Twilio has specific requirements for sending SMS to India:
- You need to register your use case
- You may need to use Twilio's Messaging Service
- See: https://www.twilio.com/docs/sms/send-messages-india

## Step 3: Install Twilio Python SDK

The Twilio SDK should already be in your `requirements.txt`. If not, add it:

```bash
cd backend
pip install twilio
```

Or add to `requirements.txt`:
```
twilio>=8.10.0
```

## Step 4: Configure Environment Variables

Update your `backend/.env` file with your Twilio credentials:

```env
# SMS Provider (Twilio)
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+15551234567
```

Replace:
- `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` with your actual Account SID
- `your_auth_token_here` with your actual Auth Token
- `+15551234567` with your Twilio phone number

## Step 5: Verify the Implementation

The OTP service is already implemented in `backend/app/services/otp_service.py`. Here's how it works:

### OTP Flow

1. **Generate OTP**: Creates a 6-digit random code
2. **Store in Redis**: Saves OTP with 10-minute expiration
3. **Send via Twilio**: Sends SMS to user's phone
4. **Verify OTP**: Checks if entered OTP matches stored value

### Code Structure

```python
# Generate and send OTP
otp_service.create_and_send_otp(phone="+919876543210")

# Verify OTP
is_valid = otp_service.verify_otp(phone="+919876543210", otp="123456")
```

## Step 6: Test the OTP Service

### 6.1 Test with Development Mode

For testing without sending real SMS, set:

```env
SMS_PROVIDER=development
```

This will print OTPs to the console instead of sending SMS.

### 6.2 Test with Twilio Trial Account

With a trial account, you can only send SMS to verified phone numbers:

1. Go to **Phone Numbers** → **Manage** → **Verified Caller IDs**
2. Add and verify your test phone number
3. Now you can send OTP to that number

### 6.3 Test the API Endpoint

```bash
# Send OTP
curl -X POST http://localhost:8000/api/v1/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'

# Verify OTP
curl -X POST http://localhost:8000/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210", "otp": "123456"}'
```

## Step 7: Customize SMS Message

The default message is:
```
Your IndoStar Naturals verification code is: {otp}. Valid for 10 minutes.
```

To customize, edit `backend/app/services/otp_service.py`:

```python
message = client.messages.create(
    body=f"Your custom message: {otp}",
    from_=settings.TWILIO_PHONE_NUMBER,
    to=phone
)
```

## Step 8: Production Considerations

### 8.1 Upgrade from Trial Account

Trial accounts have limitations:
- Can only send to verified numbers
- Messages include "Sent from your Twilio trial account"
- Limited to $15 credit

To upgrade:
1. Go to **Billing** in Twilio Console
2. Add payment method
3. Upgrade account

### 8.2 Register for India SMS

For sending SMS to India in production:

1. Go to **Messaging** → **Regulatory Compliance**
2. Complete the registration for India
3. Provide business details and use case
4. Wait for approval (usually 1-2 business days)

### 8.3 Use Messaging Service (Recommended for India)

Instead of a single phone number, use a Messaging Service:

1. Create a Messaging Service in Twilio Console
2. Add your phone number to the service
3. Update code to use Messaging Service SID:

```python
message = client.messages.create(
    body=f"Your IndoStar Naturals verification code is: {otp}",
    messaging_service_sid=settings.TWILIO_MESSAGING_SERVICE_SID,
    to=phone
)
```

Add to `.env`:
```env
TWILIO_MESSAGING_SERVICE_SID=MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 8.4 Monitor Usage and Costs

- SMS to India costs approximately $0.0075 per message
- Monitor usage in Twilio Console → **Monitor** → **Logs**
- Set up usage alerts to avoid unexpected charges

### 8.5 Implement Rate Limiting

The application already has rate limiting for auth endpoints:
- 5 attempts per 15 minutes per IP address
- Configured in `backend/app/services/rate_limiter.py`

### 8.6 Security Best Practices

1. **Never commit credentials**: Keep `.env` in `.gitignore`
2. **Use environment variables**: Never hardcode credentials
3. **Rotate tokens**: Regularly rotate Auth Token in production
4. **Monitor for abuse**: Set up alerts for unusual SMS volume
5. **Implement CAPTCHA**: Add CAPTCHA before OTP request to prevent abuse

## Step 9: Alternative SMS Providers

If you want to use MSG91 (popular in India) instead:

### 9.1 Update Configuration

```env
SMS_PROVIDER=msg91
MSG91_AUTH_KEY=your_msg91_auth_key
MSG91_SENDER_ID=your_sender_id
MSG91_ROUTE=4
```

### 9.2 Implement MSG91 Service

Update `backend/app/services/otp_service.py`:

```python
@staticmethod
def _send_via_msg91(phone: str, otp: str) -> bool:
    """Send OTP via MSG91"""
    import requests
    
    url = "https://api.msg91.com/api/v5/otp"
    
    payload = {
        "template_id": settings.MSG91_TEMPLATE_ID,
        "mobile": phone,
        "authkey": settings.MSG91_AUTH_KEY,
        "otp": otp
    }
    
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending OTP via MSG91: {e}")
        return False
```

## Troubleshooting

### Issue: "Unable to create record: The 'To' number is not a valid phone number"

**Solution**: Ensure phone numbers are in E.164 format: `+[country code][number]`
- Example: `+919876543210` (India)
- Example: `+15551234567` (US)

### Issue: "The number is unverified. Trial accounts cannot send messages to unverified numbers"

**Solution**: 
1. Verify the phone number in Twilio Console
2. Or upgrade from trial account

### Issue: "Authentication Error"

**Solution**: 
1. Check Account SID and Auth Token are correct
2. Ensure no extra spaces in `.env` file
3. Restart the backend server after updating `.env`

### Issue: Redis Connection Error

**Solution**: 
1. Ensure Redis is running: `redis-cli ping` should return `PONG`
2. Check Redis URL in `.env`
3. See `REDIS_SETUP_GUIDE.md` for Redis setup

### Issue: SMS not received

**Solution**:
1. Check Twilio Console → **Monitor** → **Logs** for delivery status
2. Verify phone number format
3. Check if number is blocked or invalid
4. For India, ensure regulatory compliance is complete

## Testing Checklist

- [ ] Twilio account created and verified
- [ ] Phone number purchased
- [ ] Credentials added to `.env`
- [ ] Redis server running
- [ ] Backend server restarted
- [ ] Test phone number verified (for trial)
- [ ] OTP sent successfully
- [ ] OTP received on phone
- [ ] OTP verification works
- [ ] Rate limiting tested
- [ ] Error handling tested

## Cost Estimation

For 1000 users per month with 2 OTP requests each:
- 2000 SMS × $0.0075 = **$15/month**

For 10,000 users per month:
- 20,000 SMS × $0.0075 = **$150/month**

## Support Resources

- Twilio Documentation: https://www.twilio.com/docs/sms
- Twilio Python SDK: https://www.twilio.com/docs/libraries/python
- Twilio Support: https://support.twilio.com/
- India SMS Guide: https://www.twilio.com/docs/sms/send-messages-india

## Next Steps

1. Set up Twilio account and get credentials
2. Update `.env` with your credentials
3. Test OTP flow in development
4. Complete India regulatory compliance (for production)
5. Upgrade from trial account when ready
6. Monitor usage and costs
7. Implement additional security measures (CAPTCHA, etc.)

---

**Need Help?** Check the Twilio Console logs or contact Twilio support for assistance.
