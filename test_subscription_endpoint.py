"""Test subscription endpoint directly"""
import requests
import json

# Test data
url = "http://localhost:8000/api/v1/subscriptions"
headers = {
    "Content-Type": "application/json",
    # You'll need to add your auth token here
    # "Authorization": "Bearer YOUR_TOKEN_HERE"
}

data = {
    "product_id": 1,
    "plan_frequency": "daily",
    "start_date": "2025-12-01",
    "delivery_address_id": 1
}

print("Testing subscription creation endpoint...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"\nError: {e}")
    if hasattr(e, 'response'):
        print(f"Response text: {e.response.text}")
