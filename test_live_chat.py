"""
Test script for verifying live Gemini chatbot response through InvoiceGuard backend.
Sends query: "Say hello and tell me which model you are."
"""

import os
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def run_chat_test():
    query = "Say hello and tell me which model you are."
    print(f"Sending query: '{query}'")
    
    payload = {
        "query": query,
        "invoice_id": "INV-2026-0918"
    }
    
    res = requests.post(f"{BASE_URL}/api/ai/chat", json=payload, headers={"X-User-UID": "usr_demo1_alex"})
    print("HTTP Status:", res.status_code)
    data = res.json()
    print("Response JSON:")
    print(json.dumps(data, indent=2))
    
    return data

if __name__ == "__main__":
    run_chat_test()
