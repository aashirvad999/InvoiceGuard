"""
Generator script to build 3 ready-to-upload demo PDF invoices for hackathon presentation.
Outputs:
- demo_invoices/invoice_1_clean.pdf (Low Risk, 0 errors)
- demo_invoices/invoice_2_grand_total_mismatch.pdf (High Risk, Grand Total Mismatch)
- demo_invoices/invoice_3_multiple_issues.pdf (High Risk, CGST + SGST + Grand Total Mismatches)
"""

import os
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
from engine.pdf_generator import generate_sample_pdf

def create_demo_suite():
    out_dir = os.path.abspath("demo_invoices")
    os.makedirs(out_dir, exist_ok=True)

    # 1. Clean Invoice
    inv1 = {
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
        "line_items": [
            {"description": "Standard Ergonomic Keyboard", "qty": 5, "unit_price": 1000.0, "amount": 5000.0}
        ]
    }
    p1 = os.path.join(out_dir, "invoice_1_clean.pdf")
    generate_sample_pdf(inv1, p1)
    print(f"[CREATED] Demo Invoice 1 (Clean): {p1}")

    # 2. Grand Total Mismatch
    inv2 = {
        "invoice_number": "INV-2026-9902",
        "vendor_name": "ABC Technologies",
        "gstin": "27AAACA1234A1Z5",
        "bank_name": "HDFC Bank",
        "bank_account": "5020004901",
        "ifsc": "HDFC0000240",
        "issue_date": "Oct 24, 2026",
        "total_amount": 20620.0,  # Printed 20,620 vs Calculated 10,620 (+10,000)
        "taxable_amount": 9000.0,
        "cgst_amount": 810.0,
        "sgst_amount": 810.0,
        "igst_amount": 0.0,
        "line_items": [
            {"description": "Laptop Stand Riser", "qty": 5, "unit_price": 1000.0, "amount": 5000.0},
            {"description": "USB-C Multiport Hub", "qty": 2, "unit_price": 2000.0, "amount": 4000.0}
        ]
    }
    p2 = os.path.join(out_dir, "invoice_2_grand_total_mismatch.pdf")
    generate_sample_pdf(inv2, p2)
    print(f"[CREATED] Demo Invoice 2 (Grand Total Mismatch): {p2}")

    # 3. Multiple Issues (Wrong CGST + Wrong SGST + Wrong Grand Total)
    inv3 = {
        "invoice_number": "INV-2026-9903",
        "vendor_name": "ABC Technologies",
        "gstin": "27AAACA1234A1Z5",
        "bank_name": "HDFC Bank",
        "bank_account": "5020004901",
        "ifsc": "HDFC0000240",
        "issue_date": "Oct 24, 2026",
        "total_amount": 20620.0,  # Printed 20,620 vs Calculated 10,620 (+10,000)
        "taxable_amount": 9000.0,
        "cgst_amount": 910.0,     # Wrong CGST (Expected 810)
        "sgst_amount": 710.0,     # Wrong SGST (Expected 810)
        "igst_amount": 0.0,
        "line_items": [
            {"description": "Laptop Stand Riser", "qty": 5, "unit_price": 1000.0, "amount": 5000.0},
            {"description": "USB-C Multiport Hub", "qty": 2, "unit_price": 2000.0, "amount": 4000.0}
        ]
    }
    # 4. Invalid GSTIN (14 chars: 22AAAAA0000A1Z)
    inv4 = {
        "invoice_number": "INV-2026-9904",
        "vendor_name": "ABC Technologies",
        "gstin": "22AAAAA0000A1Z",
        "bank_name": "HDFC Bank",
        "bank_account": "5020004901",
        "ifsc": "HDFC0000240",
        "issue_date": "Oct 24, 2026",
        "total_amount": 5900.0,
        "taxable_amount": 5000.0,
        "cgst_amount": 450.0,
        "sgst_amount": 450.0,
        "igst_amount": 0.0,
        "line_items": [
            {"description": "Standard Ergonomic Keyboard", "qty": 5, "unit_price": 1000.0, "amount": 5000.0}
        ]
    }
    p4 = os.path.join(out_dir, "invoice_4_invalid_gstin.pdf")
    generate_sample_pdf(inv4, p4)
    print(f"[CREATED] Demo Invoice 4 (Invalid 14-char GSTIN): {p4}")

    print("\nALL 4 DEMO INVOICES GENERATED SUCCESSFULLY!")

if __name__ == "__main__":
    create_demo_suite()

