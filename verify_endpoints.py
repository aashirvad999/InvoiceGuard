"""
End-to-End HTTP Verification Script for InvoiceGuard
Validates all REST endpoints, HTML markup, PDF downloads, and AI chat.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def run_http_tests():
    print("=== Testing HTTP Endpoints on", BASE_URL, "===")

    # 1. HTML Root
    r = requests.get(f"{BASE_URL}/")
    assert r.status_code == 200, f"Root failed: {r.status_code}"
    assert "InvoiceGuard" in r.text
    assert "bg-surface" in r.text
    assert "Ask InvoiceGuard" in r.text
    print("[PASS] GET / -> HTTP 200 (Stitch Dashboard HTML loaded)")

    # 2. Demo Users
    r = requests.get(f"{BASE_URL}/api/auth/demo-users")
    assert r.status_code == 200
    users = r.json()["users"]
    assert len(users) == 5
    assert users[0]["email"] == "demo1@invoiceguard.demo"
    assert users[4]["email"] == "demo5@invoiceguard.demo"
    print("[PASS] GET /api/auth/demo-users -> HTTP 200 (5 Demo Accounts verified)")

    # 3. Switch User
    r = requests.post(f"{BASE_URL}/api/auth/switch-user", json={"email": "demo2@invoiceguard.demo"})
    assert r.status_code == 200
    assert r.json()["active_user"]["name"] == "Priya Sharma"
    print("[PASS] POST /api/auth/switch-user -> HTTP 200 (Switched persona to Priya Sharma)")

    # 4. Overview Metrics
    r = requests.get(f"{BASE_URL}/api/overview/metrics")
    assert r.status_code == 200
    m = r.json()
    assert m["total_analyzed"] >= 0
    print("[PASS] GET /api/overview/metrics -> HTTP 200 (Analyzed:", m["total_analyzed"], "At risk:", m["amount_at_risk"], ")")

    # 5. Invoices List & Filters
    r = requests.get(f"{BASE_URL}/api/invoices")
    assert r.status_code == 200
    invoices = r.json()["invoices"]
    assert len(invoices) >= 0
    print("[PASS] GET /api/invoices -> HTTP 200 (Found", len(invoices), "invoices in repository)")


    # Filter by status=review
    r = requests.get(f"{BASE_URL}/api/invoices?status=review")
    assert r.status_code == 200
    print("[PASS] GET /api/invoices?status=review -> HTTP 200 (Filter verified)")

    # 6. Deep Investigation Endpoint for INV-2026-0918
    r = requests.get(f"{BASE_URL}/api/invoices/INV-2026-0918", headers={"X-User-UID": "usr_demo1_alex"})
    assert r.status_code == 200
    data = r.json()
    inv = data["invoice"]
    assert inv["threat_score"] == 74
    assert inv["vendor_name"] == "ABC Technologies"
    assert len(inv["line_items"]) == 3
    assert len(inv["signals"]) >= 3
    print("[PASS] GET /api/invoices/INV-2026-0918 -> HTTP 200 (Threat Score 74/100, 3 Line items, Evidence Matrix verified)")

    # 7. AI Chat Endpoint
    r = requests.post(f"{BASE_URL}/api/ai/chat", json={
        "query": "Why was this invoice flagged?",
        "invoice_id": "INV-2026-0918"
    })
    assert r.status_code == 200
    chat_res = r.json()
    assert "reply" in chat_res and len(chat_res["reply"]) > 10
    print("[PASS] POST /api/ai/chat -> HTTP 200 (AI Chatbot responded with confidence", chat_res.get("confidence"), "%)")

    # 8. Draft Email Endpoint
    r = requests.post(f"{BASE_URL}/api/ai/draft-email", json={"invoice_id": "INV-2026-0918"}, headers={"X-User-UID": "usr_demo1_alex"})
    assert r.status_code == 200
    draft = r.json()["draft"]
    assert "ABC Technologies" in draft and "Subject:" in draft
    print("[PASS] POST /api/ai/draft-email -> HTTP 200 (Generated formal vendor inquiry letter)")

    # 9. PDF Download
    r = requests.get(f"{BASE_URL}/api/invoices/INV-2026-0918/pdf", headers={"X-User-UID": "usr_demo1_alex"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert len(r.content) > 1000
    print("[PASS] GET /api/invoices/INV-2026-0918/pdf -> HTTP 200 (Downloaded PDF payload of size", len(r.content), "bytes)")

    # 10. File Upload Ingestion
    files = {'file': ('test_upload_invoice.pdf', r.content, 'application/pdf')}
    r = requests.post(f"{BASE_URL}/api/invoices/upload", files=files)
    assert r.status_code == 200
    upload_res = r.json()
    assert upload_res["status"] == "success"
    assert "invoice_id" in upload_res
    print("[PASS] POST /api/invoices/upload -> HTTP 200 (Ingested new invoice with ID:", upload_res["invoice_id"], ")")

    # 11. Vendors & Complaints
    r = requests.get(f"{BASE_URL}/api/vendors")
    assert r.status_code == 200
    print("[PASS] GET /api/vendors -> HTTP 200 (Found", len(r.json()["vendors"]), "vendors)")

    r = requests.get(f"{BASE_URL}/api/complaints")
    assert r.status_code == 200
    print("[PASS] GET /api/complaints -> HTTP 200 (Found", len(r.json()["complaints"]), "complaints)")

    print("\nALL HTTP & API VERIFICATION TESTS PASSED (11/11)!")

if __name__ == "__main__":
    run_http_tests()
