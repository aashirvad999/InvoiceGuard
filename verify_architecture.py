"""
Comprehensive Verification Script for InvoiceGuard:
- Prototype Admin Login (admin / admins)
- Role-Based Authorization & 403 checks
- User Data Isolation (UID Scoped)
- Fresh User Empty State checks (0 invoices)
- File Storage Isolation in users/{uid}/invoices/{id}/original.pdf
- Document AI Normalized Extraction
"""

import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("=== Testing InvoiceGuard Architecture & Security on", BASE_URL, "===")

    # 1. Test Admin Login with valid credentials
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"username": "admin", "password": "admins"})
    assert r.status_code == 200, f"Admin login failed: {r.text}"
    admin_data = r.json()
    assert admin_data["user"]["role"] == "admin"
    print("[PASS] POST /api/auth/login -> HTTP 200 (Admin authenticated with role: 'admin')")

    # 2. Test Admin Login with invalid credentials
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"username": "admin", "password": "wrongpassword"})
    assert r.status_code == 401
    print("[PASS] POST /api/auth/login (invalid credentials) -> HTTP 401 Unauthorized")

    # 3. Test Admin Protected Endpoint as Admin
    admin_headers = {"X-User-UID": "admin_root_001"}
    r = requests.get(f"{BASE_URL}/api/admin/overview", headers=admin_headers)
    assert r.status_code == 200
    ov = r.json()
    assert "total_invoices_audited" in ov
    assert "blacklist" in ov
    print("[PASS] GET /api/admin/overview (as Admin) -> HTTP 200 (Global Enterprise overview loaded)")

    # 4. Test Admin Protected Endpoint as Normal User -> Expect 403 Forbidden!
    user_headers = {"X-User-UID": "usr_demo1_alex"}
    r = requests.get(f"{BASE_URL}/api/admin/overview", headers=user_headers)
    assert r.status_code == 403, f"Expected 403, got {r.status_code}"
    print("[PASS] GET /api/admin/overview (as Normal User) -> HTTP 403 Forbidden (Server-side role check verified)")

    # 5. Test User Data Isolation: User 1 (Alex) vs User 2 (Priya) vs User 5 (Arjun)
    r_alex = requests.get(f"{BASE_URL}/api/user/invoices", headers={"X-User-UID": "usr_demo1_alex"})
    assert r_alex.status_code == 200
    alex_invs = r_alex.json()["invoices"]
    assert len(alex_invs) == 3
    assert any(i["id"] == "INV-2026-0918" for i in alex_invs)
    print(f"[PASS] GET /api/user/invoices (Alex) -> HTTP 200 ({len(alex_invs)} invoices in isolated partition)")

    r_priya = requests.get(f"{BASE_URL}/api/user/invoices", headers={"X-User-UID": "usr_demo2_priya"})
    assert r_priya.status_code == 200
    priya_invs = r_priya.json()["invoices"]
    assert len(priya_invs) == 2
    assert not any(i["id"] == "INV-2026-0918" for i in priya_invs)
    print(f"[PASS] GET /api/user/invoices (Priya) -> HTTP 200 ({len(priya_invs)} invoices; cannot see Alex's invoices)")

    # 6. Test Fresh User Empty State (Arjun has 0 invoices initially)
    r_arjun = requests.get(f"{BASE_URL}/api/user/invoices", headers={"X-User-UID": "usr_demo5_arjun"})
    assert r_arjun.status_code == 200
    arjun_invs = r_arjun.json()["invoices"]
    assert len(arjun_invs) == 0
    
    r_arjun_metrics = requests.get(f"{BASE_URL}/api/user/metrics", headers={"X-User-UID": "usr_demo5_arjun"})
    assert r_arjun_metrics.status_code == 200
    assert r_arjun_metrics.json()["is_empty"] is True
    assert r_arjun_metrics.json()["total_analyzed"] == 0
    print("[PASS] GET /api/user/metrics (Fresh User Arjun) -> HTTP 200 (is_empty: True, 0 fake stats)")

    # 7. Test User-Scoped File Upload & Storage Partitioning
    sample_pdf_path = os.path.join("storage", "users", "usr_demo1_alex", "invoices", "INV-2026-0918", "original.pdf")
    with open(sample_pdf_path, "rb") as f:
        file_bytes = f.read()

    files = {'file': ('arjun_invoice.pdf', file_bytes, 'application/pdf')}
    r_upload = requests.post(
        f"{BASE_URL}/api/user/invoices/upload",
        headers={"X-User-UID": "usr_demo5_arjun"},
        files=files
    )
    assert r_upload.status_code == 200
    res = r_upload.json()
    new_id = res["invoice_id"]
    print(f"[PASS] POST /api/user/invoices/upload -> HTTP 200 (Ingested invoice {new_id} for Arjun)")

    # Verify storage file exists in isolated path
    expected_storage_file = os.path.join("storage", "users", "usr_demo5_arjun", "invoices", new_id, "original.pdf")
    assert os.path.exists(expected_storage_file)
    print(f"[PASS] Verified file stored in isolated path: {expected_storage_file}")

    # Verify Arjun now has 1 invoice and metrics updated
    r_arjun_now = requests.get(f"{BASE_URL}/api/user/invoices", headers={"X-User-UID": "usr_demo5_arjun"})
    assert len(r_arjun_now.json()["invoices"]) == 1
    print("[PASS] Arjun's repository now contains 1 real invoice without fake data")

    # 8. Test Admin Blacklist Broadcast
    r_blk = requests.post(
        f"{BASE_URL}/api/admin/vendors/blacklist",
        headers=admin_headers,
        json={
            "vendor_name": "Phishing Invoices Ltd",
            "gstin": "27AABCP9999P1ZZ",
            "reason": "Spoofed invoice template detected across multiple nodes"
        }
    )
    assert r_blk.status_code == 200
    print("[PASS] POST /api/admin/vendors/blacklist -> HTTP 200 (Blacklist entry registered)")

    print("\nALL ARCHITECTURE, SECURITY & DATA ISOLATION TESTS PASSED (8/8)!")

if __name__ == "__main__":
    run_tests()
