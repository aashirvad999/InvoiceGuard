import requests
import os
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
from engine.pdf_generator import generate_sample_pdf

BASE_URL = "http://127.0.0.1:8000"
headers = {"X-User-UID": "usr_demo1_alex"}

def test_varied_scores():
    print("=== Testing Upload Risk Score Variation ===")

    # 1. Completely valid invoice
    valid_inv = {
        "invoice_number": "INV-2026-9901",
        "vendor_name": "ABC Technologies",
        "gstin": "27AAACA1234A1Z5",
        "bank_name": "HDFC Bank",
        "bank_account": "5020004901",
        "ifsc": "HDFC0000240",
        "issue_date": "Oct 24, 2026",
        "total_amount": 5900.0,
        "taxable_amount": 5000.0,
        "cgst_amount": 450.0,
        "sgst_amount": 450.0,
        "igst_amount": 0.0,
        "threat_score": 4,
        "line_items": [
            {"description": "Paper Reams", "qty": 5, "unit_price": 1000.0, "amount": 5000.0}
        ]
    }
    path_valid = os.path.abspath("test_valid.pdf")
    generate_sample_pdf(valid_inv, path_valid)
    
    with open(path_valid, "rb") as f:
        r1 = requests.post(f"{BASE_URL}/api/user/invoices/upload", headers=headers, files={'file': ('test_valid.pdf', f.read(), 'application/pdf')})
    res1 = r1.json()["invoice"]
    print(f"1. Valid Invoice Threat Score: {res1['threat_score']}/100 ({res1['risk_level']}) - Signals: {[s['type'] for s in res1['signals']]}")
    assert res1["threat_score"] <= 30, f"Expected low score <= 30, got {res1['threat_score']}"

    # 2. Tampered Grand Total Invoice
    tampered_inv = {
        "invoice_number": "INV-BADTOTAL-002",
        "vendor_name": "Cloudflare India Ltd",
        "gstin": "27AAACA1234A1Z5",
        "issue_date": "Oct 24, 2026",
        "total_amount": 25900.0,  # Expected 5900 vs 25900 (+20000)
        "taxable_amount": 5000.0,
        "cgst_amount": 450.0,
        "sgst_amount": 450.0,
        "igst_amount": 0.0,
        "threat_score": 80,
        "line_items": [
            {"description": "CDN Enterprise", "qty": 5, "unit_price": 1000.0, "amount": 5000.0}
        ]
    }
    path_bad = os.path.abspath("test_badtotal.pdf")
    generate_sample_pdf(tampered_inv, path_bad)

    with open(path_bad, "rb") as f:
        r2 = requests.post(f"{BASE_URL}/api/user/invoices/upload", headers=headers, files={'file': ('test_badtotal.pdf', f.read(), 'application/pdf')})
    res2 = r2.json()["invoice"]
    print(f"2. Tampered Total Invoice Threat Score: {res2['threat_score']}/100 ({res2['risk_level']}) - Signals: {[s['type'] for s in res2['signals']]}")
    assert res2["threat_score"] >= 40, f"Expected high score >= 40, got {res2['threat_score']}"
    assert "grand_total_mismatch" in [s['type'] for s in res2['signals']]

    # Clean up
    if os.path.exists(path_valid): os.remove(path_valid)
    if os.path.exists(path_bad): os.remove(path_bad)

    print("\n[SUCCESS] Upload risk score varies dynamically based on actual document content!")

if __name__ == "__main__":
    test_varied_scores()
