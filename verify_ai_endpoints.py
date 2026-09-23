"""
API Endpoint Verification Script for InvoiceGuard AI Endpoints
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_explain_endpoint():
    payload = {
        "invoice_number": "INV-001",
        "vendor": "ABC Pvt Ltd",
        "risk_score": 85,
        "risk_level": "HIGH",
        "signals": [
            {
                "type": "mathematical_inconsistency",
                "description": "Grand total does not match independently calculated total",
                "invoice_value": 159000,
                "expected_value": 59000,
                "difference": 100000
            }
        ]
    }
    res = requests.post(f"{BASE_URL}/api/ai/explain", json=payload)
    print("POST /api/ai/explain status:", res.status_code)
    print("Response JSON:", json.dumps(res.json(), indent=2))
    assert res.status_code == 200

def test_chat_endpoint():
    payload = {
        "query": "Why was this invoice flagged?",
        "invoice_id": "INV-2026-0918"
    }
    res = requests.post(f"{BASE_URL}/api/ai/chat", json=payload, headers={"X-User-UID": "usr_demo1_alex"})
    print("\nPOST /api/ai/chat status:", res.status_code)
    print("Response JSON:", json.dumps(res.json(), indent=2))
    assert res.status_code == 200

if __name__ == "__main__":
    test_explain_endpoint()
    test_chat_endpoint()
