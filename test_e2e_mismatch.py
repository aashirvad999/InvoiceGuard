"""
E2E Application Pipeline Test for InvoiceGuard
Tests uploading an invoice with an intentionally wrong grand total to verify backend analysis and frontend-facing response payload.
"""

import requests
import json
import os
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
from engine.pdf_generator import generate_sample_pdf

BASE_URL = "http://127.0.0.1:8000"

def test_e2e_grand_total_mismatch():
    print("=== Testing E2E Pipeline for Intentionally Manipulated Grand Total ===")

    # 1. Create a sample invoice payload with mismatched total
    # Expected grand total: Subtotal 9000 + CGST 810 + SGST 810 = 10620
    # Printed grand total: 20620 (Tampered total)
    inv_data = {
        "id": "INV-TEST-E2E-001",
        "invoice_number": "INV-2026-9999",
        "vendor_name": "ABC Technologies",
        "gstin": "27AAACA1234A1Z5",
        "issue_date": "Oct 24, 2026",
        "total_amount": 20620.0,   # Tampered printed total! (Expected 10620)
        "taxable_amount": 9000.0,
        "cgst_amount": 810.0,
        "sgst_amount": 810.0,
        "igst_amount": 0.0,
        "threat_score": 85,
        "line_items": [
            {"description": "Laptop Stand", "qty": 5, "unit_price": 1000.0, "amount": 5000.0},
            {"description": "USB-C Cable", "qty": 2, "unit_price": 2000.0, "amount": 4000.0}
        ]
    }

    # Generate PDF
    pdf_path = os.path.abspath("scratch_test_e2e.pdf")
    generate_sample_pdf(inv_data, pdf_path, tamper_font=True)

    # 2. Upload via API endpoint
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    files = {'file': ('test_mismatched_invoice.pdf', file_bytes, 'application/pdf')}
    headers = {"X-User-UID": "usr_demo1_alex"}

    r = requests.post(f"{BASE_URL}/api/user/invoices/upload", headers=headers, files=files)
    assert r.status_code == 200, f"Upload failed: {r.text}"
    
    resp_data = r.json()
    invoice = resp_data["invoice"]

    print("[PASS] API Response returned HTTP 200 OK.")
    print(f"Ingested Invoice ID: {invoice['id']}")
    print(f"Calculated Threat Score: {invoice['threat_score']}/100 ({invoice['risk_level']})")

    # 3. Verify grand_total_mismatch signal
    signals = invoice.get("signals", [])
    gt_signals = [s for s in signals if s["type"] == "grand_total_mismatch"]
    
    assert len(gt_signals) >= 1, f"Expected grand_total_mismatch signal, found signals: {[s['type'] for s in signals]}"
    sig = gt_signals[0]

    print("\n--- Detected Signal Details ---")
    print(f"Title: {sig['title'].encode('ascii', 'replace').decode()}")
    print(f"Severity: {sig['severity']}")
    print(f"Description: {sig['description'].encode('ascii', 'replace').decode()}")
    print(f"Evidence: Expected = INR {sig['evidence']['expected']:,.2f}, Invoice = INR {sig['evidence']['invoice']:,.2f}, Difference = INR {sig['evidence']['difference']:,.2f}")

    assert sig["evidence"]["expected"] == 10620.0
    assert sig["evidence"]["invoice"] == 20620.0
    assert sig["evidence"]["difference"] == 10000.0

    # 4. Verify Financial Breakdown payload for Frontend
    fb = invoice["financial_breakdown"]
    assert fb["expected_grand_total"] == 10620.0
    assert fb["surplus_gap"] == 10000.0
    print(f"\n[PASS] Financial Breakdown Gap: INR {fb['surplus_gap']:,.2f}")
    print(f"[PASS] Gap Explanation: {fb['gap_explanation'].encode('ascii', 'replace').decode()}")

    # Clean up scratch PDF
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    print("\nE2E APPLICATION PIPELINE TEST PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_e2e_grand_total_mismatch()
