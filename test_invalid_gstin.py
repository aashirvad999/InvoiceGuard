"""
Unit Test Suite for GSTIN Validation & Risk Flagging
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from engine.deterministic import (
    validate_gstin_format,
    detect_vendor_behavioral_anomalies,
    calculate_risk_score
)

class TestGSTINValidation(unittest.TestCase):

    def test_valid_gstin(self):
        """Valid 15-character statutory GSTIN."""
        res = validate_gstin_format("27AAACA1234A1Z5")
        self.assertTrue(res["valid"])
        self.assertEqual(res["status"], "Passed")

    def test_short_gstin(self):
        """Short GSTIN (11 chars instead of 15)."""
        res = validate_gstin_format("27AAACA1234")
        self.assertFalse(res["valid"])
        self.assertEqual(res["status"], "Invalid length")

        inv = {"gstin": "27AAACA1234", "line_items": []}
        signals, _ = detect_vendor_behavioral_anomalies(
            vendor_id="VEN-001",
            vendor_name="Test Vendor",
            vendor_data={},
            current_invoice=inv,
            all_user_invoices=[],
            known_trusted_vendors=[]
        )
        gst_sig = next((s for s in signals if s["type"] == "invalid_gstin"), None)
        self.assertIsNotNone(gst_sig, "Short GSTIN must generate an invalid_gstin signal")
        self.assertIn("11 characters long", gst_sig["description"])

    def test_long_gstin(self):
        """Long GSTIN (18 chars instead of 15)."""
        res = validate_gstin_format("27AAACA1234A1Z5EXTRA")
        self.assertFalse(res["valid"])
        self.assertEqual(res["status"], "Invalid length")

        inv = {"gstin": "27AAACA1234A1Z5EXTRA", "line_items": []}
        signals, _ = detect_vendor_behavioral_anomalies(
            vendor_id="VEN-001",
            vendor_name="Test Vendor",
            vendor_data={},
            current_invoice=inv,
            all_user_invoices=[],
            known_trusted_vendors=[]
        )
        gst_sig = next((s for s in signals if s["type"] == "invalid_gstin"), None)
        self.assertIsNotNone(gst_sig, "Long GSTIN must generate an invalid_gstin signal")

    def test_malformed_format_gstin(self):
        """Malformed regex structure GSTIN."""
        res = validate_gstin_format("99INVALIDGSTIN")
        self.assertFalse(res["valid"])

        inv = {"gstin": "99INVALIDGSTIN", "line_items": []}
        signals, _ = detect_vendor_behavioral_anomalies(
            vendor_id="VEN-001",
            vendor_name="Test Vendor",
            vendor_data={},
            current_invoice=inv,
            all_user_invoices=[],
            known_trusted_vendors=[]
        )
        gst_sig = next((s for s in signals if s["type"] == "invalid_gstin"), None)
        self.assertIsNotNone(gst_sig)

    def test_invalid_state_code_gstin(self):
        """Invalid state code GSTIN (99 is not a valid state code 01-38)."""
        res = validate_gstin_format("99AAACA1234A1Z5")
        self.assertFalse(res["valid"])
        self.assertEqual(res["status"], "Invalid state code")

        inv = {"gstin": "99AAACA1234A1Z5", "line_items": []}
        signals, _ = detect_vendor_behavioral_anomalies(
            vendor_id="VEN-001",
            vendor_name="Test Vendor",
            vendor_data={},
            current_invoice=inv,
            all_user_invoices=[],
            known_trusted_vendors=[]
        )
        gst_sig = next((s for s in signals if s["type"] == "invalid_gstin"), None)
        self.assertIsNotNone(gst_sig)


if __name__ == "__main__":
    unittest.main()
