"""
Direct backend endpoint test for /api/ai/chat
Sends: 'Hello. Reply with exactly: Gemini connection successful.'
"""

import os
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_direct_chatbot():
    query = "Hello. Reply with exactly: Gemini connection successful."
    print(f"--- Sending query to backend: '{query}' ---")
    
    payload = {
        "query": query,
        "invoice_id": "INV-2026-0918"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/api/ai/chat", json=payload, headers={"X-User-UID": "usr_demo1_alex"})
        print("HTTP Status Code:", res.status_code)
        print("Response Payload:")
        print(json.dumps(res.json(), indent=2))
        return res.json()
    except Exception as e:
        print("Request failed:", type(e).__name__, str(e))
        return None

if __name__ == "__main__":
    test_direct_chatbot()
