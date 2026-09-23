"""
Targeted Unit & Integration Tests for InvoiceGuard Deterministic Math & GST Validation
Covers Scenarios 1 to 10 as specified in prompt.
"""

import sys
import os

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
from engine.deterministic import validate_mathematical_consistency, detect_vendor_behavioral_anomalies
from engine.risk_engine import calculate_deterministic_risk_score


def run_math_tests():
    print("=== Running Deterministic Math & GST Validation Tests ===")

    # Test 1 — Completely correct invoice
    print("\n--- Test 1: Completely correct invoice ---")
    line_items_1 = [
        {"description": "Item 1", "qty": 5, "unit_price": 1000.0, "amount": 5000.0},
        {"description": "Item 2", "qty": 2, "unit_price": 2000.0, "amount": 4000.0}
    ]
    res_1 = validate_mathematical_consistency(
        line_items=line_items_1,
        taxable_amount=9000.0,
        cgst_amount=810.0,
        sgst_amount=810.0,
        igst_amount=0.0,
        total_amount=10620.0
    )
    assert res_1["is_valid"] is True, f"Expected valid, got signals: {res_1['signals']}"
    assert len(res_1["signals"]) == 0
    print("[PASS] Correct invoice passed without signals.")

    # Test 2 — Wrong line total
    print("\n--- Test 2: Wrong line total ---")
    line_items_2 = [
        {"description": "Item 1", "qty": 5, "unit_price": 1000.0, "amount": 7000.0}  # Reported 7000 vs 5000
    ]
    res_2 = validate_mathematical_consistency(
        line_items=line_items_2,
        taxable_amount=5000.0,
        cgst_amount=450.0,
        sgst_amount=450.0,
        igst_amount=0.0,
        total_amount=5900.0
    )
    assert res_2["is_valid"] is False
    line_sigs = [s for s in res_2["signals"] if s["type"] == "line_total_mismatch"]
    assert len(line_sigs) == 1, f"Expected 1 line_total_mismatch, got: {res_2['signals']}"
    sig2 = line_sigs[0]
    assert sig2["evidence"]["expected"] == 5000.0
    assert sig2["evidence"]["invoice"] == 7000.0
    assert sig2["evidence"]["difference"] == 2000.0
    print("[PASS] Wrong line total detected with accurate evidence:", sig2["evidence"])

    # Test 3 — Wrong taxable amount
    print("\n--- Test 3: Wrong taxable amount ---")
    line_items_3 = [
        {"description": "Item 1", "qty": 5, "unit_price": 1000.0, "amount": 5000.0},
        {"description": "Item 2", "qty": 2, "unit_price": 2000.0, "amount": 4000.0}
    ]  # Sum = 9000
    res_3 = validate_mathematical_consistency(
        line_items=line_items_3,
        taxable_amount=19000.0,  # Reported 19000 vs 9000
        cgst_amount=810.0,
        sgst_amount=810.0,
        igst_amount=0.0,
        total_amount=10620.0
    )
    assert res_3["is_valid"] is False
    tax_sigs = [s for s in res_3["signals"] if s["type"] == "taxable_amount_mismatch"]
    assert len(tax_sigs) == 1
    assert tax_sigs[0]["evidence"]["expected"] == 9000.0
    assert tax_sigs[0]["evidence"]["invoice"] == 19000.0
    assert tax_sigs[0]["evidence"]["difference"] == 10000.0
    print("[PASS] Wrong taxable amount detected:", tax_sigs[0]["evidence"])

    # Test 4 — Wrong CGST
    print("\n--- Test 4: Wrong CGST ---")
    res_4 = validate_mathematical_consistency(
        line_items=line_items_1,
        taxable_amount=9000.0,
        cgst_amount=910.0,  # Reported 910 vs 810
        sgst_amount=810.0,
        igst_amount=0.0,
        total_amount=10620.0
    )
    assert res_4["is_valid"] is False
    cgst_sigs = [s for s in res_4["signals"] if s["type"] == "cgst_mismatch"]
    assert len(cgst_sigs) == 1
    assert cgst_sigs[0]["evidence"]["expected"] == 810.0
    assert cgst_sigs[0]["evidence"]["invoice"] == 910.0
    assert cgst_sigs[0]["evidence"]["difference"] == 100.0
    print("[PASS] Wrong CGST detected:", cgst_sigs[0]["evidence"])

    # Test 5 — Wrong SGST
    print("\n--- Test 5: Wrong SGST ---")
    res_5 = validate_mathematical_consistency(
        line_items=line_items_1,
        taxable_amount=9000.0,
        cgst_amount=810.0,
        sgst_amount=710.0,  # Reported 710 vs 810
        igst_amount=0.0,
        total_amount=10620.0
    )
    assert res_5["is_valid"] is False
    sgst_sigs = [s for s in res_5["signals"] if s["type"] == "sgst_mismatch"]
    assert len(sgst_sigs) == 1
    assert sgst_sigs[0]["evidence"]["expected"] == 810.0
    assert sgst_sigs[0]["evidence"]["invoice"] == 710.0
    assert sgst_sigs[0]["evidence"]["difference"] == 100.0
    print("[PASS] Wrong SGST detected:", sgst_sigs[0]["evidence"])

    # Test 6 — Wrong IGST
    print("\n--- Test 6: Wrong IGST ---")
    line_items_6 = [
        {"description": "Item 1", "qty": 10, "unit_price": 1000.0, "amount": 10000.0}
    ]
    res_6 = validate_mathematical_consistency(
        line_items=line_items_6,
        taxable_amount=10000.0,
        cgst_amount=0.0,
        sgst_amount=0.0,
        igst_amount=2200.0,  # Expected 1800 vs reported 2200
        total_amount=11800.0
    )
    assert res_6["is_valid"] is False
    igst_sigs = [s for s in res_6["signals"] if s["type"] == "igst_mismatch"]
    assert len(igst_sigs) == 1
    assert igst_sigs[0]["evidence"]["expected"] == 1800.0
    assert igst_sigs[0]["evidence"]["invoice"] == 2200.0
    print("[PASS] Wrong IGST detected:", igst_sigs[0]["evidence"])

    # Test 7 — Correct GST but wrong grand total
    print("\n--- Test 7: Correct GST but wrong grand total ---")
    res_7 = validate_mathematical_consistency(
        line_items=line_items_1,
        taxable_amount=9000.0,
        cgst_amount=810.0,
        sgst_amount=810.0,
        igst_amount=0.0,
        total_amount=20620.0  # Reported 20620 vs expected 10620
    )
    assert res_7["is_valid"] is False
    gt_sigs = [s for s in res_7["signals"] if s["type"] == "grand_total_mismatch"]
    assert len(gt_sigs) == 1
    sig7 = gt_sigs[0]
    assert sig7["evidence"]["expected"] == 10620.0
    assert sig7["evidence"]["invoice"] == 20620.0
    assert sig7["evidence"]["difference"] == 10000.0
    print("[PASS] Grand total mismatch detected:", sig7["evidence"])

    # Test 8 — Multiple simultaneous errors
    print("\n--- Test 8: Multiple simultaneous errors ---")
    res_8 = validate_mathematical_consistency(
        line_items=line_items_1,
        taxable_amount=9000.0,
        cgst_amount=910.0,   # Wrong CGST (+100)
        sgst_amount=710.0,   # Wrong SGST (-100)
        igst_amount=0.0,
        total_amount=20620.0 # Wrong Grand Total (+10000)
    )
    assert res_8["is_valid"] is False
    sig_types = [s["type"] for s in res_8["signals"]]
    assert "cgst_mismatch" in sig_types
    assert "sgst_mismatch" in sig_types
    assert "grand_total_mismatch" in sig_types
    print(f"[PASS] Multiple simultaneous signals returned: {sig_types}")

    # Test 9 — No historical data
    print("\n--- Test 9: No historical data ---")
    test_inv_9 = {
        "vendor_id": "VEN-NEW-01",
        "vendor_name": "Brand New Corp",
        "gstin": "27AAACA1234A1Z5",
        "line_items": line_items_1,
        "taxable_amount": 9000.0,
        "cgst_amount": 810.0,
        "sgst_amount": 810.0,
        "igst_amount": 0.0,
        "total_amount": 10620.0
    }
    sigs_9, summary_9 = detect_vendor_behavioral_anomalies(
        vendor_id="VEN-NEW-01",
        vendor_name="Brand New Corp",
        vendor_data=None,  # No history
        current_invoice=test_inv_9,
        all_user_invoices=[],
        known_trusted_vendors=[]
    )
    assert summary_9["baseline_status"] == "Insufficient historical data"
    # No math signals since math is valid
    math_sigs_9 = [s for s in sigs_9 if "mismatch" in s.get("type", "")]
    assert len(math_sigs_9) == 0
    print("[PASS] Baseline status set to 'Insufficient historical data', math checks pass.")

    # Test 10 — Normal rounding
    print("\n--- Test 10: Normal rounding tolerance ---")
    # Small rounding differences (e.g. subtotal 100.00, tax 18.00, total 118.20 where total is within currency tolerance 1.00)
    res_10 = validate_mathematical_consistency(
        line_items=[{"description": "Item", "qty": 1, "unit_price": 100.0, "amount": 100.0}],
        taxable_amount=100.0,
        cgst_amount=9.0,
        sgst_amount=9.0,
        igst_amount=0.0,
        total_amount=118.20  # ₹0.20 difference due to minor rounding
    )
    assert res_10["is_valid"] is True
    assert len(res_10["signals"]) == 0
    print("[PASS] Normal rounding tolerance (INR 0.20) passed without false positive.")

    print("\nALL 10 DETERMINISTIC MATH & GST TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    run_math_tests()
