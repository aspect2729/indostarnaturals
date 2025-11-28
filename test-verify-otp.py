"""Test verify-otp endpoint"""
import requests
import json

# Test phone number
phone = "+1234567890"

# Step 1: Send OTP
print("Step 1: Sending OTP...")
response = requests.post(
    "http://localhost:8000/api/v1/auth/send-otp",
    json={"phone": phone}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 200:
    # Get OTP from backend logs (in development mode it's printed)
    otp = input("\nEnter the OTP from backend console: ")
    
    # Step 2: Verify OTP
    print(f"\nStep 2: Verifying OTP {otp}...")
    response = requests.post(
        "http://localhost:8000/api/v1/auth/verify-otp",
        json={"phone": phone, "otp": otp}
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"Success! Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
else:
    print("Failed to send OTP")
