"""
Test script for Twilio OTP functionality

This script helps you test your Twilio OTP setup without running the full application.

Usage:
    python test_twilio_otp.py
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.services.otp_service import otp_service


def test_twilio_configuration():
    """Test if Twilio is properly configured"""
    print("=" * 60)
    print("TWILIO OTP CONFIGURATION TEST")
    print("=" * 60)
    
    print("\n1. Checking configuration...")
    print(f"   SMS Provider: {settings.SMS_PROVIDER}")
    
    if settings.SMS_PROVIDER != "twilio":
        print("   ⚠️  SMS_PROVIDER is not set to 'twilio'")
        print("   Update your .env file: SMS_PROVIDER=twilio")
        return False
    
    print(f"   Twilio Account SID: {settings.TWILIO_ACCOUNT_SID[:10]}..." if settings.TWILIO_ACCOUNT_SID else "   ❌ Not configured")
    print(f"   Twilio Auth Token: {'*' * 20}" if settings.TWILIO_AUTH_TOKEN else "   ❌ Not configured")
    print(f"   Twilio Phone Number: {settings.TWILIO_PHONE_NUMBER}" if settings.TWILIO_PHONE_NUMBER else "   ❌ Not configured")
    
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
        print("\n   ❌ Twilio credentials are not fully configured!")
        print("   Please update your .env file with:")
        print("   - TWILIO_ACCOUNT_SID")
        print("   - TWILIO_AUTH_TOKEN")
        print("   - TWILIO_PHONE_NUMBER")
        return False
    
    print("   ✅ Configuration looks good!")
    return True


def test_twilio_connection():
    """Test connection to Twilio API"""
    print("\n2. Testing Twilio API connection...")
    
    try:
        from twilio.rest import Client
        
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        
        # Fetch account details to verify credentials
        account = client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
        
        print(f"   ✅ Connected to Twilio!")
        print(f"   Account Status: {account.status}")
        print(f"   Account Type: {account.type}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to connect to Twilio: {e}")
        print("\n   Troubleshooting:")
        print("   - Verify your Account SID and Auth Token are correct")
        print("   - Check your internet connection")
        print("   - Ensure credentials don't have extra spaces")
        return False


def test_otp_generation():
    """Test OTP generation"""
    print("\n3. Testing OTP generation...")
    
    try:
        otp = otp_service.generate_otp()
        print(f"   ✅ Generated OTP: {otp}")
        
        if len(otp) != 6:
            print(f"   ⚠️  OTP length is {len(otp)}, expected 6")
            return False
        
        if not otp.isdigit():
            print("   ⚠️  OTP contains non-digit characters")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to generate OTP: {e}")
        return False


def test_redis_connection():
    """Test Redis connection for OTP storage"""
    print("\n4. Testing Redis connection...")
    
    try:
        from app.core.redis_client import get_redis
        
        redis = get_redis()
        redis.ping()
        
        print("   ✅ Redis is connected!")
        
        # Test OTP storage
        test_phone = "+919999999999"
        test_otp = "123456"
        
        otp_service.store_otp(test_phone, test_otp)
        print(f"   ✅ Stored test OTP for {test_phone}")
        
        # Verify storage
        is_valid = otp_service.verify_otp(test_phone, test_otp)
        if is_valid:
            print("   ✅ OTP verification works!")
        else:
            print("   ⚠️  OTP verification failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Redis connection failed: {e}")
        print("\n   Troubleshooting:")
        print("   - Ensure Redis server is running")
        print("   - Check REDIS_URL in .env file")
        print("   - See REDIS_SETUP_GUIDE.md for setup instructions")
        return False


def test_send_otp(phone_number: str = None):
    """Test sending OTP via Twilio"""
    print("\n5. Testing OTP sending...")
    
    if not phone_number:
        print("   ⚠️  No phone number provided")
        print("   To test SMS sending, run:")
        print("   python test_twilio_otp.py +919876543210")
        return True
    
    print(f"   Sending OTP to {phone_number}...")
    
    try:
        success = otp_service.create_and_send_otp(phone_number)
        
        if success:
            print(f"   ✅ OTP sent successfully to {phone_number}!")
            print("   Check your phone for the SMS")
            print("\n   Note: If using a trial account, the number must be verified in Twilio Console")
        else:
            print(f"   ❌ Failed to send OTP to {phone_number}")
            print("\n   Troubleshooting:")
            print("   - Verify phone number format: +[country code][number]")
            print("   - For trial accounts, verify the number in Twilio Console")
            print("   - Check Twilio Console logs for details")
        
        return success
        
    except Exception as e:
        print(f"   ❌ Error sending OTP: {e}")
        return False


def main():
    """Run all tests"""
    print("\n🚀 Starting Twilio OTP Tests...\n")
    
    # Get phone number from command line if provided
    phone_number = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run tests
    tests = [
        ("Configuration", test_twilio_configuration),
        ("Twilio Connection", test_twilio_connection),
        ("OTP Generation", test_otp_generation),
        ("Redis Connection", test_redis_connection),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            
            # Stop if critical test fails
            if not result and test_name in ["Configuration", "Redis Connection"]:
                print(f"\n❌ Critical test '{test_name}' failed. Stopping tests.")
                break
        except Exception as e:
            print(f"\n❌ Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
            break
    
    # Test SMS sending if phone number provided and previous tests passed
    if phone_number and all(result for _, result in results):
        test_send_otp(phone_number)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Your Twilio OTP setup is working correctly.")
        
        if not phone_number:
            print("\n💡 To test SMS sending, run:")
            print("   python test_twilio_otp.py +919876543210")
            print("   (Replace with your verified phone number)")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("   See TWILIO_OTP_SETUP_GUIDE.md for detailed setup instructions.")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
