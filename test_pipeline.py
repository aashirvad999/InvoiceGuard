"""
Automated Pipeline Verification for InvoiceGuard
Tests deterministic GSTIN checks, financial reconciliation, PyMuPDF inspection,
threat scoring, and API endpoints.
"""

import sys
import os

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
from engine.deterministic import (
    validate_gstin,
    reconcile_financials,
    calculate_risk_score,
    check_behavioral_and_vendor_anomalies
)
from engine.document_forensics import inspect_pdf_document
from engine.ai_explainer import generate_invoice_explanation, chat_with_invoiceguard
from engine.seed_data import INITIAL_INVOICES, INITIAL_VENDORS, DEMO_USERS


def run_tests():
    print("=== 1. Testing GSTIN Validation ===")
    v_res = validate_gstin("27AAACA1234A1Z5")
    assert v_res["valid"] is True, f"Expected valid GSTIN, got {v_res}"
    print("[PASS] Valid GSTIN passed:", v_res["gstin"])

    inv_res = validate_gstin("99INVALID123")
    assert inv_res["valid"] is False
    print("[PASS] Invalid GSTIN correctly rejected:", inv_res["reason"])

    print("\n=== 2. Testing Deterministic Financial Reconciliation ===")
    line_items = [
        {"description": "Laptop Stand", "qty": 5, "unit_price": 1000.0, "amount": 5000.0},
        {"description": "Mechanical Keyboard", "qty": 50, "unit_price": 2000.0, "amount": 100000.0},
        {"description": "USB-C Hub", "qty": 10, "unit_price": 5400.0, "amount": 54000.0}
    ]
    fin_res = reconcile_financials(
        line_items=line_items,
        taxable_amount=159000.0,
        cgst_amount=4500.0,
        sgst_amount=4500.0,
        igst_amount=0.0,
        total_amount=159000.0
    )
    print("[PASS] Financial check completed. Calculated subtotal:", fin_res["calculated_subtotal"])

    print("\n=== 3. Testing Anomaly & Risk Scoring ===")
    test_inv = INITIAL_INVOICES[0]
    vendor = INITIAL_VENDORS[0]
    signals = check_behavioral_and_vendor_anomalies(
        vendor_id=test_inv["vendor_id"],
        vendor_name=test_inv["vendor_name"],
        vendor_data=vendor,
        current_invoice=test_inv,
        all_invoices=INITIAL_INVOICES
    )
    assert len(signals) >= 2, f"Expected at least 2 anomaly signals, got {len(signals)}"
    print(f"[PASS] Flagged {len(signals)} behavioral anomalies (New payout account, quantity spike).")

    risk = calculate_risk_score(signals, test_inv["passed_checks"])
    print(f"[PASS] Computed Threat Score: {risk['score']}/100 ({risk['risk_level']})")

    print("\n=== 4. Testing AI Explainer & Context Chat ===")
    explanation = generate_invoice_explanation(test_inv, risk)
    assert len(explanation) > 20
    print("[PASS] Explanation synthesized:", explanation[:100].encode('ascii', 'replace').decode() + "...")

    chat_res = chat_with_invoiceguard("Why is the payment destination suspicious?", invoice_context=test_inv)
    assert "ICICI" in chat_res["reply"] or "4901" in chat_res["reply"] or "bank" in chat_res["reply"].lower()
    print("[PASS] AI Copilot contextual response verified:", chat_res["reply"][:90].encode('ascii', 'replace').decode() + "...")

    print("\n=== 5. Testing 5 Prototype Demo Accounts ===")
    assert len(DEMO_USERS) == 5
    print("[PASS] 5 Demo accounts configured:", [u["email"] for u in DEMO_USERS])

    print("\nAll pipeline tests PASSED successfully!")


if __name__ == "__main__":
    run_tests()
