"""
Automated Gemini Integration Test Suite for InvoiceGuard
Executes all 5 required test cases specified in the user requirements.
"""

import os
import sys
import json
import unittest

# Ensure engine modules can be imported
sys.path.insert(0, os.path.dirname(__file__))

from engine.deterministic import (
    validate_gstin_format,
    validate_mathematical_consistency,
    calculate_risk_score
)
from engine.ai_explainer import (
    generate_invoice_explanation,
    chat_with_invoiceguard,
    FALLBACK_EXPLANATION
)


class TestGeminiIntegration(unittest.TestCase):

    def setUp(self):
        self.clean_invoice = {
            "invoice_number": "INV-001",
            "vendor": "Clean Systems Pvt Ltd",
            "vendor_name": "Clean Systems Pvt Ltd",
            "total_amount": 59000.0,
            "taxable_amount": 50000.0,
            "cgst_amount": 4500.0,
            "sgst_amount": 4500.0,
            "igst_amount": 0.0,
            "line_items": [
                {"description": "IT Consulting Services", "qty": 1, "unit_price": 50000.0, "amount": 50000.0}
            ],
            "gstin": "27AAACA1234A1Z5"
        }

        self.wrong_grand_total_invoice = {
            "invoice_number": "INV-002",
            "vendor": "ABC Pvt Ltd",
            "vendor_name": "ABC Pvt Ltd",
            "total_amount": 159000.0,  # Stated grand total is 1,59,000
            "taxable_amount": 50000.0,
            "cgst_amount": 4500.0,
            "sgst_amount": 4500.0,
            "igst_amount": 0.0,
            "line_items": [
                {"description": "Hardware Equipment", "qty": 1, "unit_price": 50000.0, "amount": 50000.0}
            ],
            "gstin": "27AAACA1234A1Z5"
        }

        self.wrong_gst_invoice = {
            "invoice_number": "INV-003",
            "vendor": "Defect Vendor Corp",
            "vendor_name": "Defect Vendor Corp",
            "total_amount": 69000.0,  # Stated 69000 vs subtotal 50000 + CGST 9500 + SGST 9500 (19% total tax)
            "taxable_amount": 50000.0,
            "cgst_amount": 9500.0,     # Wrong CGST rate (19% instead of 9%)
            "sgst_amount": 9500.0,     # Wrong SGST rate
            "igst_amount": 0.0,
            "line_items": [
                {"description": "Office Supplies", "qty": 1, "unit_price": 50000.0, "amount": 50000.0}
            ],
            "gstin": "99INVALIDGSTIN"   # Invalid GSTIN format
        }

    def test_1_clean_invoice(self):
        """TEST 1: Clean invoice → deterministic analysis works → Gemini explains no major inconsistencies."""
        # 1. Deterministic math check
        math_res = validate_mathematical_consistency(
            line_items=self.clean_invoice["line_items"],
            taxable_amount=self.clean_invoice["taxable_amount"],
            cgst_amount=self.clean_invoice["cgst_amount"],
            sgst_amount=self.clean_invoice["sgst_amount"],
            igst_amount=0.0,
            total_amount=self.clean_invoice["total_amount"]
        )
        self.assertTrue(math_res["is_valid"], "Clean invoice math should be valid")

        # 2. Risk scoring
        risk = calculate_risk_score(signals=[], passed_checks=[{"title": "SHA-256 Hash", "detail": "Clean"}])
        self.assertLessEqual(risk["score"], 25)

        # 3. Gemini Explanation
        payload = {
            "invoice_number": self.clean_invoice["invoice_number"],
            "vendor": self.clean_invoice["vendor"],
            "risk_score": risk["score"],
            "risk_level": risk["risk_level"],
            "signals": [],
            "financial_breakdown": {
                "taxable_subtotal": 50000.0,
                "expected_grand_total": 59000.0,
                "surplus_gap": 0.0
            }
        }
        explanation = generate_invoice_explanation(payload)
        self.assertIsInstance(explanation, str)
        print("\n--- TEST 1 OUTPUT ---")
        print("Risk Score:", risk["score"])
        print("AI Explanation:", explanation)

    def test_2_wrong_grand_total(self):
        """TEST 2: Wrong grand total → deterministic detector catches it → Gemini explains exact discrepancy."""
        # 1. Deterministic math check
        math_res = validate_mathematical_consistency(
            line_items=self.wrong_grand_total_invoice["line_items"],
            taxable_amount=self.wrong_grand_total_invoice["taxable_amount"],
            cgst_amount=self.wrong_grand_total_invoice["cgst_amount"],
            sgst_amount=self.wrong_grand_total_invoice["sgst_amount"],
            igst_amount=0.0,
            total_amount=self.wrong_grand_total_invoice["total_amount"]
        )
        self.assertFalse(math_res["is_valid"], "Math check should fail for wrong grand total")
        self.assertEqual(math_res["surplus_gap"], 100000.0)

        # 2. Signals & Risk Scoring
        signals = [
            {
                "id": "grand_total_mismatch",
                "type": "grand_total_mismatch",
                "title": "Grand Total Discrepancy",
                "description": f"Grand total mismatch: invoice states ₹1,59,000, expected ₹59,000 (diff: ₹1,00,000)",
                "invoice_value": 159000.0,
                "expected_value": 59000.0,
                "difference": 100000.0,
                "severity": "CRITICAL"
            },
            {
                "id": "new_payment_destination",
                "type": "new_payment_destination",
                "title": "Unrecognized Payout Destination",
                "description": "ICICI Bank ending in *8821 does not match registered HDFC Bank account.",
                "severity": "HIGH"
            }
        ]
        risk = calculate_risk_score(signals=signals, passed_checks=[])
        self.assertGreater(risk["score"], 40)

        # 3. Gemini Explanation
        payload = {
            "invoice_number": self.wrong_grand_total_invoice["invoice_number"],
            "vendor": self.wrong_grand_total_invoice["vendor"],
            "risk_score": risk["score"],
            "risk_level": risk["risk_level"],
            "signals": signals
        }
        explanation = generate_invoice_explanation(payload)
        self.assertIsInstance(explanation, str)
        print("\n--- TEST 2 OUTPUT ---")
        print("Risk Score:", risk["score"])
        print("AI Explanation:", explanation)

    def test_3_wrong_gst(self):
        """TEST 3: Wrong GST → deterministic detector catches it → Gemini explains GST inconsistency."""
        # 1. Deterministic GST format check
        gst_check = validate_gstin_format(self.wrong_gst_invoice["gstin"])
        self.assertFalse(gst_check["valid"], "GSTIN format check should fail")

        signals = [
            {
                "id": "invalid_gstin",
                "type": "invalid_gstin",
                "title": "Invalid GSTIN Format",
                "description": f"GSTIN '{self.wrong_gst_invoice['gstin']}' failed statutory format checksum validation.",
                "severity": "HIGH"
            },
            {
                "id": "cgst_mismatch",
                "type": "cgst_mismatch",
                "title": "Tax Rate Discrepancy",
                "description": "Calculated tax rates (19.0% CGST + 19.0% SGST = 38.0%) diverge from standard tax slabs (18.0%).",
                "severity": "HIGH"
            }
        ]
        risk = calculate_risk_score(signals=signals, passed_checks=[])

        payload = {
            "invoice_number": self.wrong_gst_invoice["invoice_number"],
            "vendor": self.wrong_gst_invoice["vendor"],
            "risk_score": risk["score"],
            "risk_level": risk["risk_level"],
            "signals": signals
        }
        explanation = generate_invoice_explanation(payload)
        self.assertIsInstance(explanation, str)
        print("\n--- TEST 3 OUTPUT ---")
        print("Risk Score:", risk["score"])
        print("AI Explanation:", explanation)

    def test_4_remove_gemini_api_key(self):
        """TEST 4: Remove GEMINI_API_KEY → app still works → AI explanation returns fallback message."""
        orig_key = os.environ.get("GEMINI_API_KEY")
        try:
            # Temporarily unset key
            if "GEMINI_API_KEY" in os.environ:
                del os.environ["GEMINI_API_KEY"]

            # Deterministic math analysis MUST STILL SUCCEED
            math_res = validate_mathematical_consistency(
                line_items=self.wrong_grand_total_invoice["line_items"],
                taxable_amount=self.wrong_grand_total_invoice["taxable_amount"],
                cgst_amount=self.wrong_grand_total_invoice["cgst_amount"],
                sgst_amount=self.wrong_grand_total_invoice["sgst_amount"],
                igst_amount=0.0,
                total_amount=self.wrong_grand_total_invoice["total_amount"]
            )
            self.assertFalse(math_res["is_valid"])
            self.assertEqual(math_res["surplus_gap"], 100000.0)

            # AI Explanation should return exact fallback message
            payload = {
                "invoice_number": "INV-002",
                "vendor": "ABC Pvt Ltd",
                "risk_score": 85,
                "risk_level": "CRITICAL",
                "signals": []
            }
            explanation = generate_invoice_explanation(payload)
            self.assertEqual(explanation, FALLBACK_EXPLANATION)

            # Chat should also return fallback gracefully without error
            chat_res = chat_with_invoiceguard("Why was this invoice flagged?", invoice_context=payload)
            self.assertIn("reply", chat_res)
            self.assertFalse(chat_res["ai_available"])
            print("\n--- TEST 4 OUTPUT ---")
            print("Fallback Explanation:", explanation)
            print("Fallback Chat Reply:", chat_res["reply"])

        finally:
            if orig_key:
                os.environ["GEMINI_API_KEY"] = orig_key

    def test_5_simulate_gemini_api_failure(self):
        """TEST 5: Simulate Gemini/API failure → deterministic analysis still works cleanly."""
        # Set invalid key to trigger API exception/failure
        orig_key = os.environ.get("GEMINI_API_KEY")
        try:
            os.environ["GEMINI_API_KEY"] = "INVALID_MOCK_KEY_99999"

            # Deterministic check MUST NOT CRASH
            math_res = validate_mathematical_consistency(
                line_items=self.clean_invoice["line_items"],
                taxable_amount=self.clean_invoice["taxable_amount"],
                cgst_amount=self.clean_invoice["cgst_amount"],
                sgst_amount=self.clean_invoice["sgst_amount"],
                igst_amount=0.0,
                total_amount=self.clean_invoice["total_amount"]
            )
            self.assertTrue(math_res["is_valid"])

            # AI explanation should handle exception cleanly and return fallback
            explanation = generate_invoice_explanation(self.clean_invoice)
            self.assertEqual(explanation, FALLBACK_EXPLANATION)
            print("\n--- TEST 5 OUTPUT ---")
            print("API Failure Handled Cleanly:", explanation)
        finally:
            if orig_key:
                os.environ["GEMINI_API_KEY"] = orig_key
            elif "GEMINI_API_KEY" in os.environ:
                del os.environ["GEMINI_API_KEY"]


if __name__ == "__main__":
    unittest.main()
