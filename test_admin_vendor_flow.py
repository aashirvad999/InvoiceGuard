import requests
import os
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
from engine.pdf_generator import generate_sample_pdf

BASE_URL = "http://127.0.0.1:8000"

def test_admin_vendor_flow():
    print("=== Testing Automatic Vendor Sharing & Admin Verification Flow ===")

    user_headers = {"X-User-UID": "usr_demo1_alex"}
    admin_headers = {"X-User-UID": "admin_root_001"}

    # 1. Upload an invoice for a brand new vendor as Alex
    new_inv = {
        "invoice_number": "INV-TESLA-001",
        "vendor_name": "Tesla India Motors",
        "gstin": "27AABCT9999P1Z1",
        "issue_date": "Oct 24, 2026",
        "total_amount": 100000.0,
        "taxable_amount": 100000.0,
        "cgst_amount": 0.0,
        "sgst_amount": 0.0,
        "igst_amount": 0.0,
        "line_items": [
            {"description": "EV Charging Station", "qty": 1, "unit_price": 100000.0, "amount": 100000.0}
        ]
    }
    pdf_path = os.path.abspath("test_tesla.pdf")
    generate_sample_pdf(new_inv, pdf_path)

    with open(pdf_path, "rb") as f:
        r_up = requests.post(f"{BASE_URL}/api/user/invoices/upload", headers=user_headers, files={'file': ('test_tesla.pdf', f.read(), 'application/pdf')})
    assert r_up.status_code == 200, f"Upload failed: {r_up.text}"
    inv_res = r_up.json()["invoice"]
    vendor_id = inv_res["vendor_id"]
    print(f"[PASS] User uploaded invoice. Vendor ID: {vendor_id}, Vendor Name: {inv_res['vendor_name']}")

    # 2. Admin fetches all vendors across tenants
    r_adm_v = requests.get(f"{BASE_URL}/api/admin/vendors", headers=admin_headers)
    assert r_adm_v.status_code == 200
    adm_vendors = r_adm_v.json()["vendors"]
    
    tesla_vendor = next((v for v in adm_vendors if "tesla" in v["name"].lower()), None)
    assert tesla_vendor is not None, f"Expected Tesla India Motors in admin vendor list, found: {[v['name'] for v in adm_vendors]}"
    assert tesla_vendor["verified"] is False
    assert tesla_vendor["owner_name"] == "Alex Vance"
    print(f"[PASS] Vendor automatically shared with Admin Sentinel Queue: {tesla_vendor['name']} (Uploaded by: {tesla_vendor['owner_name']})")

    # 3. Admin verifies vendor KYC
    r_verify = requests.post(f"{BASE_URL}/api/admin/vendors/{tesla_vendor['id']}/verify", headers=admin_headers)
    assert r_verify.status_code == 200
    verify_res = r_verify.json()["vendor"]
    assert verify_res["verified"] is True
    print(f"[PASS] Admin approved verification for {verify_res['name']} ({verify_res['verified_by']})")

    # 4. User inspects invoice and confirms vendor_verified is updated
    r_user_invs = requests.get(f"{BASE_URL}/api/user/invoices", headers=user_headers)
    user_invs = r_user_invs.json()["invoices"]
    updated_inv = next(i for i in user_invs if i["id"] == inv_res["id"])
    assert updated_inv["vendor_verified"] is True
    print(f"[PASS] Cascaded verification confirmed on User's invoice #{updated_inv['invoice_number']}: vendor_verified = True")

    # Clean up
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    print("\nALL ADMIN VENDOR SHARING & VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_admin_vendor_flow()
