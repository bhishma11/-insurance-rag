# test_n8n.py
import requests
import json

# Test 1: Claim Processing
print("🚀 Testing Claim Processing...")
response = requests.post(
    "http://localhost:8001/api/n8n/trigger/claim-processing",
    json={
        "action": "process_claim",
        "data": {
            "claim_id": "CL-999",
            "amount": 3000,
            "email": "test@example.com"
        }
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")

# Test 2: Email Notification
print("📧 Testing Email Notification...")
response = requests.post(
    "http://localhost:8001/api/n8n/trigger/email-notification",
    json={
        "action": "send_email",
        "data": {
            "to": "khettrib@gmail.com",
            "subject": "Test from n8n",
            "message": "Hello! This is a test from n8n integration."
        }
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")

# Test 3: Ticket Email
print("🎫 Testing Ticket Email...")
response = requests.post(
    "http://localhost:8001/api/n8n/trigger/ticket-email",
    json={
        "action": "send_ticket",
        "data": {
            "to": "khettrib@gmail.com",
            "user_id": "user-123"
        }
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")