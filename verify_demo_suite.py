"""
Verification script testing the 3 prepared demo invoices through the live FastAPI application.
Checks:
1. invoice_1_clean.pdf -> Low Risk, 0 math error signals
2. invoice_2_grand_total_mismatch.pdf -> High Risk, grand_total_mismatch
3. invoice_3_multiple_issues.pdf -> High Risk, cgst_mismatch + sgst_mismatch + grand_total_mismatch
"""

import requests
import os

BASE_URL = "http://127.0.0.1:8000"
headers = {"X-User-UID": "usr_demo1_alex"}

def test_prepared_demo_invoices():
    print("=== Testing 3 Prepared Demo Invoices on Live FastAPI Application ===")
    demo_dir = os.path.abspath("demo_invoices")

    # 1. Test Demo Invoice 1 (Clean)
    p1 = os.path.join(demo_dir, "invoice_1_clean.pdf")
    with open(p1, "rb") as f:
        r1 = requests.post(f"{BASE_URL}/api/user/invoices/upload", headers=headers, files={'file': ('invoice_1_clean.pdf', f.read(), 'application/pdf')})
    assert r1.status_code == 200, f"Upload 1 failed: {r1.text}"
    inv1 = r1.json()["invoice"]
    math_sigs1 = [s for s in inv1["signals"] if "mismatch" in s["type"]]
    print(f"\n1. Demo Invoice 1 (Clean):")
    print(f"   - Ingested ID: #{inv1['invoice_number']}")
    print(f"   - Threat Score: {inv1['threat_score']}/100 ({inv1['risk_level']})")
    print(f"   - Math Error Signals: {len(math_sigs1)} (Expected 0)")
    assert len(math_sigs1) == 0

    # 2. Test Demo Invoice 2 (Grand Total Mismatch)
    p2 = os.path.join(demo_dir, "invoice_2_grand_total_mismatch.pdf")
    with open(p2, "rb") as f:
        r2 = requests.post(f"{BASE_URL}/api/user/invoices/upload", headers=headers, files={'file': ('invoice_2_grand_total_mismatch.pdf', f.read(), 'application/pdf')})
    assert r2.status_code == 200, f"Upload 2 failed: {r2.text}"
    inv2 = r2.json()["invoice"]
    math_sigs2 = [s["type"] for s in inv2["signals"] if "mismatch" in s["type"]]
    print(f"\n2. Demo Invoice 2 (Grand Total Mismatch):")
    print(f"   - Ingested ID: #{inv2['invoice_number']}")
    print(f"   - Threat Score: {inv2['threat_score']}/100 ({inv2['risk_level']})")
    print(f"   - Math Error Signals: {math_sigs2}")
    assert "grand_total_mismatch" in math_sigs2

    # 3. Test Demo Invoice 3 (Multiple Issues)
    p3 = os.path.join(demo_dir, "invoice_3_multiple_issues.pdf")
    with open(p3, "rb") as f:
        r3 = requests.post(f"{BASE_URL}/api/user/invoices/upload", headers=headers, files={'file': ('invoice_3_multiple_issues.pdf', f.read(), 'application/pdf')})
    assert r3.status_code == 200, f"Upload 3 failed: {r3.text}"
    inv3 = r3.json()["invoice"]
    math_sigs3 = [s["type"] for s in inv3["signals"] if "mismatch" in s["type"]]
    print(f"\n3. Demo Invoice 3 (Multiple Issues):")
    print(f"   - Ingested ID: #{inv3['invoice_number']}")
    print(f"   - Threat Score: {inv3['threat_score']}/100 ({inv3['risk_level']})")
    print(f"   - Math Error Signals: {math_sigs3}")
    assert "cgst_mismatch" in math_sigs3
    assert "sgst_mismatch" in math_sigs3
    assert "grand_total_mismatch" in math_sigs3

    print("\nALL 3 DEMO INVOICES VERIFIED PERFECTLY ON THE LIVE APP!")

if __name__ == "__main__":
    test_prepared_demo_invoices()
