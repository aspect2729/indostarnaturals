"""Debug OTP flow to see what's happening"""
import sys
sys.path.insert(0, 'backend')

from app.services.otp_service import otp_service
from app.core.validators import validate_phone_with_country_code

# Test phone number
phone_input = "+911234567890"

print(f"1. Input phone: {phone_input}")

# Validate and clean phone
phone_cleaned = validate_phone_with_country_code(phone_input)
print(f"2. Cleaned phone: {phone_cleaned}")

# Generate OTP
otp = otp_service.generate_otp()
print(f"3. Generated OTP: {otp}")

# Store OTP
try:
    otp_service.store_otp(phone_cleaned, otp)
    print(f"4. Stored OTP for: {phone_cleaned}")
except Exception as e:
    print(f"4. ERROR storing OTP: {e}")
    sys.exit(1)

# Verify OTP
result = otp_service.verify_otp(phone_cleaned, otp)
print(f"5. Verification result: {result}")

if result:
    print("\n✓ OTP flow works correctly!")
else:
    print("\n✗ OTP verification failed!")
    
    # Check what's in Redis
    from app.core.redis_client import get_redis
    redis = get_redis()
    key = f"otp:{phone_cleaned}"
    stored = redis.get(key)
    print(f"   Stored value in Redis: {stored}")
