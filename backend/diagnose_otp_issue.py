"""
Diagnostic script to identify OTP sending issues
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings


def main():
    print("\n" + "=" * 70)
    print("  OTP ISSUE DIAGNOSTIC TOOL")
    print("=" * 70)
    
    # Check 1: Twilio Configuration
    print("\n1. TWILIO CONFIGURATION")
    print("-" * 70)
    print(f"   SMS Provider: {settings.SMS_PROVIDER}")
    print(f"   Account SID: {settings.TWILIO_ACCOUNT_SID[:10]}...{settings.TWILIO_ACCOUNT_SID[-4:]}")
    print(f"   Auth Token: {'*' * 20} (configured)")
    print(f"   Phone Number: {settings.TWILIO_PHONE_NUMBER}")
    
    # Check 2: Account Type
    print("\n2. TWILIO ACCOUNT STATUS")
    print("-" * 70)
    
    try:
        from twilio.rest import Client
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        account = client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
        
        print(f"   Account Status: {account.status}")
        print(f"   Account Type: {account.type}")
        
        if account.type == "Trial":
            print("\n   ⚠️  TRIAL ACCOUNT DETECTED")
            print("   Trial accounts can ONLY send SMS to verified numbers!")
            print("\n   To verify a phone number:")
            print("   1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
            print("   2. Click 'Add a new number'")
            print("   3. Enter and verify your phone number")
            
    except Exception as e:
        print(f"   ❌ Error checking account: {e}")
    
    # Check 3: Recent Messages
    print("\n3. RECENT SMS MESSAGES (Last 5)")
    print("-" * 70)
    
    try:
        messages = client.messages.list(limit=5)
        
        if not messages:
            print("   No messages found. Have you tried sending an OTP yet?")
        else:
            for msg in messages:
                status_icon = "✅" if msg.status == "delivered" else "❌"
                print(f"\n   {status_icon} To: {msg.to}")
                print(f"      Status: {msg.status}")
                print(f"      Date: {msg.date_created}")
                
                if msg.status == "failed":
                    print(f"      Error Code: {msg.error_code}")
                    print(f"      Error Message: {msg.error_message}")
                elif msg.status == "undelivered":
                    print(f"      ⚠️  Message was not delivered")
                    print(f"      Error Code: {msg.error_code}")
                    
    except Exception as e:
        print(f"   ❌ Error fetching messages: {e}")
    
    # Check 4: Common Issues
    print("\n4. COMMON ISSUES & SOLUTIONS")
    print("-" * 70)
    
    issues = [
        {
            "issue": "Trial account sending to unverified number",
            "solution": "Verify your phone number in Twilio Console",
            "link": "https://console.twilio.com/us1/develop/phone-numbers/manage/verified"
        },
        {
            "issue": "Invalid phone number format",
            "solution": "Use E.164 format: +[country code][number] (e.g., +919876543210)",
            "link": None
        },
        {
            "issue": "India SMS regulatory requirements",
            "solution": "Complete India registration in Twilio Console for production",
            "link": "https://console.twilio.com/us1/develop/sms/regulatory-compliance"
        },
        {
            "issue": "Phone carrier blocking international SMS",
            "solution": "Check with your mobile carrier if they block international SMS",
            "link": None
        }
    ]
    
    for i, item in enumerate(issues, 1):
        print(f"\n   {i}. {item['issue']}")
        print(f"      Solution: {item['solution']}")
        if item['link']:
            print(f"      Link: {item['link']}")
    
    # Check 5: Test Phone Number
    print("\n5. TEST WITH YOUR PHONE NUMBER")
    print("-" * 70)
    
    phone = input("\n   Enter your phone number to test (or press Enter to skip): ").strip()
    
    if phone:
        print(f"\n   Testing OTP send to {phone}...")
        
        try:
            from app.services.otp_service import otp_service
            
            # Generate OTP
            otp = otp_service.generate_otp()
            print(f"   Generated OTP: {otp}")
            
            # Try to send
            print(f"   Attempting to send SMS...")
            
            message = client.messages.create(
                body=f"Your IndoStar Naturals verification code is: {otp}. Valid for 10 minutes.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone
            )
            
            print(f"\n   ✅ Message sent!")
            print(f"   Message SID: {message.sid}")
            print(f"   Status: {message.status}")
            print(f"\n   Check your phone for the SMS!")
            print(f"\n   Track delivery: https://console.twilio.com/us1/monitor/logs/sms/{message.sid}")
            
        except Exception as e:
            print(f"\n   ❌ Error sending SMS: {e}")
            
            error_str = str(e)
            
            if "unverified" in error_str.lower():
                print("\n   SOLUTION: Verify your phone number in Twilio Console")
                print("   Link: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
            elif "not a valid phone number" in error_str.lower():
                print("\n   SOLUTION: Use E.164 format: +[country code][number]")
                print(f"   Example: +919876543210 (not 9876543210)")
            else:
                print("\n   Check Twilio Console logs for more details:")
                print("   https://console.twilio.com/us1/monitor/logs/sms")
    
    print("\n" + "=" * 70)
    print("  DIAGNOSTIC COMPLETE")
    print("=" * 70)
    print("\n  Next Steps:")
    print("  1. Verify your phone number in Twilio Console (if trial account)")
    print("  2. Check Twilio SMS logs for delivery status")
    print("  3. Ensure phone number is in E.164 format")
    print("  4. Contact Twilio support if issues persist")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
