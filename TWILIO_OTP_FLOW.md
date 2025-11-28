# Twilio OTP Flow Diagram

## Complete Authentication Flow

```
┌─────────────┐
│   User      │
│  (Frontend) │
└──────┬──────┘
       │
       │ 1. Enter phone number
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  POST /api/v1/auth/send-otp                            │
│  { "phone": "+919876543210" }                          │
└──────┬──────────────────────────────────────────────────┘
       │
       │ 2. Validate phone format
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  Rate Limiter Check                                     │
│  - Max 5 attempts per 15 minutes                        │
│  - Per IP address                                       │
└──────┬──────────────────────────────────────────────────┘
       │
       │ 3. Check rate limit
       │
       ├─── ❌ Limit exceeded ──→ Return 429 Too Many Requests
       │
       │ ✅ Within limit
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  OTP Service                                            │
│  1. Generate 6-digit OTP                                │
│  2. Store in Redis (10 min TTL)                         │
│     Key: "otp:+919876543210"                            │
│     Value: "123456"                                     │
└──────┬──────────────────────────────────────────────────┘
       │
       │ 4. OTP stored
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  Twilio API                                             │
│  client.messages.create(                                │
│    body="Your code is: 123456",                         │
│    from_="+15551234567",                                │
│    to="+919876543210"                                   │
│  )                                                      │
└──────┬──────────────────────────────────────────────────┘
       │
       │ 5. Send SMS
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  Twilio Infrastructure                                  │
│  - Routes message                                       │
│  - Handles delivery                                     │
│  - Logs status                                          │
└──────┬──────────────────────────────────────────────────┘
       │
       │ 6. SMS delivered
       │
       ▼
┌─────────────┐
│   User's    │
│   Phone     │  📱 "Your code is: 123456"
└──────┬──────┘
       │
       │ 7. User receives SMS
       │
       │ 8. User enters OTP
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  POST /api/v1/auth/verify-otp                          │
│  { "phone": "+919876543210", "otp": "123456" }         │
└──────┬──────────────────────────────────────────────────┘
       │
       │ 9. Verify OTP
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  Redis Lookup                                           │
│  Key: "otp:+919876543210"                               │
│  Stored: "123456"                                       │
│  Provided: "123456"                                     │
└──────┬──────────────────────────────────────────────────┘
       │
       ├─── ❌ Not found/expired ──→ Return 401 Invalid OTP
       │
       ├─── ❌ Mismatch ──→ Return 401 Invalid OTP
       │
       │ ✅ Match
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  Delete OTP from Redis                                  │
│  (Prevent reuse)                                        │
└──────┬──────────────────────────────────────────────────┘
       │
       │ 10. OTP verified
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  User Service                                           │
│  - Find user by phone                                   │
│  - If not exists: create new user (consumer role)       │
│  - Mark phone as verified                               │
└──────┬──────────────────────────────────────────────────┘
       │
       │ 11. User ready
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  JWT Token Service                                      │
│  - Generate access token (1 hour)                       │
│  - Generate refresh token (7 days)                      │
│  - Include user_id, phone, role                         │
└──────┬──────────────────────────────────────────────────┘
       │
       │ 12. Tokens created
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  Response                                               │
│  {                                                      │
│    "access_token": "eyJ0eXAi...",                       │
│    "refresh_token": "eyJ0eXAi...",                      │
│    "user": {                                            │
│      "id": 1,                                           │
│      "phone": "+919876543210",                          │
│      "role": "consumer",                                │
│      "is_phone_verified": true                          │
│    }                                                    │
│  }                                                      │
└──────┬──────────────────────────────────────────────────┘
       │
       │ 13. Return to frontend
       │
       ▼
┌─────────────┐
│   User      │
│  (Frontend) │  ✅ Logged in!
└─────────────┘
```

## Error Scenarios

### Scenario 1: Rate Limit Exceeded

```
User → Send OTP Request
     → Rate Limiter: 6th attempt in 15 min
     → ❌ 429 Too Many Requests
     → User: "Too many attempts. Try again in X minutes"
```

### Scenario 2: Invalid Phone Number

```
User → Send OTP: "9876543210" (missing +91)
     → Validation: Invalid format
     → ❌ 400 Bad Request
     → User: "Please enter phone in format: +919876543210"
```

### Scenario 3: Twilio Error

```
User → Send OTP Request
     → OTP Generated & Stored
     → Twilio API: Connection error
     → ❌ 500 Internal Server Error
     → User: "Failed to send OTP. Please try again"
     → Admin: Check Twilio Console logs
```

### Scenario 4: Expired OTP

```
User → Receives OTP: "123456"
     → Waits 11 minutes
     → Enters OTP: "123456"
     → Redis: Key expired (10 min TTL)
     → ❌ 401 Unauthorized
     → User: "OTP expired. Request a new one"
```

### Scenario 5: Wrong OTP

```
User → Receives OTP: "123456"
     → Enters OTP: "654321"
     → Redis: Mismatch
     → ❌ 401 Unauthorized
     → User: "Invalid OTP. Please try again"
```

### Scenario 6: Redis Down

```
User → Send OTP Request
     → OTP Generated
     → Redis: Connection refused
     → ❌ 500 Internal Server Error
     → User: "Service temporarily unavailable"
     → Admin: Start Redis server
```

## Data Flow

### Redis Storage

```
Key Format: "otp:{phone_number}"
Example: "otp:+919876543210"

Value: "123456"
TTL: 600 seconds (10 minutes)

After 10 minutes:
- Key automatically deleted
- User must request new OTP
```

### Rate Limiting Storage

```
Key Format: "rate_limit:{ip_address}"
Example: "rate_limit:192.168.1.1"

Value: 5 (attempt count)
TTL: 900 seconds (15 minutes)

After 5 attempts:
- Further requests blocked
- Returns 429 status
- Resets after 15 minutes
```

## Security Measures

```
┌─────────────────────────────────────────────────────────┐
│  Security Layer 1: Rate Limiting                        │
│  - Prevents brute force attacks                         │
│  - 5 attempts per 15 minutes                            │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Security Layer 2: OTP Expiration                       │
│  - OTP valid for only 10 minutes                        │
│  - Reduces window for attacks                           │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Security Layer 3: Single Use                           │
│  - OTP deleted after verification                       │
│  - Cannot be reused                                     │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Security Layer 4: Phone Verification                   │
│  - User must have access to phone                       │
│  - SMS sent to verified number                          │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Security Layer 5: JWT Tokens                           │
│  - Short-lived access tokens (1 hour)                   │
│  - Refresh tokens for extended sessions                 │
└─────────────────────────────────────────────────────────┘
```

## Performance Considerations

### Typical Response Times

```
Send OTP Request:
├─ Validation: ~5ms
├─ Rate limit check: ~10ms
├─ OTP generation: ~1ms
├─ Redis storage: ~5ms
├─ Twilio API call: ~200-500ms
└─ Total: ~220-520ms

Verify OTP Request:
├─ Validation: ~5ms
├─ Redis lookup: ~5ms
├─ User lookup/create: ~20-50ms
├─ JWT generation: ~10ms
└─ Total: ~40-70ms
```

### Scalability

```
Redis:
- Can handle 100,000+ ops/sec
- OTP storage is lightweight
- Automatic expiration reduces memory

Twilio:
- Handles high volume
- Automatic scaling
- Global infrastructure

Backend:
- Stateless design
- Horizontal scaling ready
- Load balancer compatible
```

## Monitoring Points

```
1. OTP Generation Rate
   └─ Track: requests/minute
   └─ Alert: Unusual spikes

2. SMS Delivery Rate
   └─ Track: success/failure ratio
   └─ Alert: High failure rate

3. Verification Success Rate
   └─ Track: valid/invalid attempts
   └─ Alert: High invalid rate

4. Rate Limit Triggers
   └─ Track: blocked requests
   └─ Alert: Potential attack

5. Twilio Costs
   └─ Track: SMS count
   └─ Alert: Budget threshold
```

## Testing Flow

```
Development Mode:
User → Send OTP
     → OTP printed to console
     → Copy OTP from logs
     → Verify OTP
     → ✅ Success

Trial Account:
User → Send OTP to verified number
     → SMS sent via Twilio
     → Receive SMS on phone
     → Verify OTP
     → ✅ Success

Production:
User → Send OTP to any number
     → SMS sent via Twilio
     → Receive SMS on phone
     → Verify OTP
     → ✅ Success
```

## Quick Reference

| Action | Endpoint | Method | Auth Required |
|--------|----------|--------|---------------|
| Send OTP | `/api/v1/auth/send-otp` | POST | No |
| Verify OTP | `/api/v1/auth/verify-otp` | POST | No |
| Refresh Token | `/api/v1/auth/refresh` | POST | Yes (Refresh Token) |

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 400 | Invalid request (bad phone format) |
| 401 | Invalid/expired OTP |
| 429 | Rate limit exceeded |
| 500 | Server error (Redis/Twilio down) |

| Configuration | Value | Purpose |
|---------------|-------|---------|
| OTP Length | 6 digits | Balance security/usability |
| OTP Expiry | 10 minutes | Security window |
| Rate Limit | 5 attempts | Prevent abuse |
| Rate Window | 15 minutes | Reset period |
| Access Token | 1 hour | Session duration |
| Refresh Token | 7 days | Extended session |
