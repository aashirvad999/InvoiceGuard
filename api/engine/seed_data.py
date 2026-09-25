"""
Seed Database and Sample Generator for InvoiceGuard Prototype
Includes 5 Demo Accounts, realistic B2B invoices matching the Stitch design,
trusted vendor records, complaints, and test PDF generation.
"""

import os
from datetime import datetime
from typing import Dict, List, Any

DEMO_USERS = [
    {
        "email": "demo1@invoiceguard.demo",
        "name": "Alex Vance",
        "initials": "AV",
        "role": "Finance Sec"
    },
    {
        "email": "demo2@invoiceguard.demo",
        "name": "Priya Sharma",
        "initials": "PS",
        "role": "Senior Controller"
    },
    {
        "email": "demo3@invoiceguard.demo",
        "name": "Marcus Thorne",
        "initials": "MT",
        "role": "Fraud Risk Officer"
    },
    {
        "email": "demo4@invoiceguard.demo",
        "name": "Elena Rostova",
        "initials": "ER",
        "role": "Head of Treasury"
    },
    {
        "email": "demo5@invoiceguard.demo",
        "name": "Arjun Mehta",
        "initials": "AM",
        "role": "Compliance Auditor"
    }
]

INITIAL_VENDORS = [
    {
        "id": "VEN-001",
        "name": "ABC Technologies",
        "category": "Hardware & IT Peripherals",
        "gstin": "27AAACA1234A1Z5",
        "pan": "AAACA1234A",
        "state": "Maharashtra (27)",
        "verified": True,
        "verified_phone": "+91 22 4920 1100",
        "verified_email": "accounts@abctech.in",
        "paid_invoice_count": 32,
        "total_disbursed": 4280000.0,
        "trust_score": 92,
        "known_invoice_patterns": ["INV-2026-", "INV-2025-"],
        "known_bank_accounts": [
            {"bank_name": "HDFC Bank", "account_number": "5020004901", "ifsc": "HDFC0000240", "status": "primary"}
        ],
        "typical_items": {
            "Laptop Stand": {"avg_qty": 5, "min_qty": 2, "max_qty": 10, "typical_price": 1000.0},
            "Mechanical Keyboard": {"avg_qty": 6, "min_qty": 5, "max_qty": 10, "typical_price": 2000.0},
            "USB-C Dual 4K Display Hub": {"avg_qty": 8, "min_qty": 4, "max_qty": 12, "typical_price": 5400.0}
        },
        "complaints": []
    },
    {
        "id": "VEN-002",
        "name": "Cloudflare India Ltd",
        "category": "Cloud Infrastructure & CDN",
        "gstin": "27AABCC5544R1ZM",
        "pan": "AABCC5544R",
        "state": "Maharashtra (27)",
        "verified": True,
        "verified_phone": "+91 80 6123 4567",
        "verified_email": "billing@cloudflare.in",
        "paid_invoice_count": 28,
        "total_disbursed": 3840000.0,
        "trust_score": 99,
        "known_invoice_patterns": ["INV-88", "INV-"],
        "known_bank_accounts": [
            {"bank_name": "Citibank N.A.", "account_number": "0029384910", "ifsc": "CITI0000002", "status": "primary"}
        ],
        "typical_items": {
            "Enterprise CDN": {"avg_qty": 1, "min_qty": 1, "max_qty": 1, "typical_price": 42800.0}
        },
        "complaints": []
    },
    {
        "id": "VEN-003",
        "name": "Zenith Office Supplies",
        "category": "Office Furnishing & Stationery",
        "gstin": "29AABCZ9988P1ZR",
        "pan": "AABCZ9988P",
        "state": "Karnataka (29)",
        "verified": False,
        "verified_phone": "+91 80 4499 8877",
        "verified_email": "orders@zenithsupplies.co",
        "paid_invoice_count": 3,
        "total_disbursed": 145000.0,
        "trust_score": 38,
        "known_invoice_patterns": ["INV-77", "INV-"],
        "known_bank_accounts": [
            {"bank_name": "Axis Bank", "account_number": "9180200112", "ifsc": "UTIB0000040", "status": "disputed"}
        ],
        "typical_items": {
            "Ergonomic Task Chairs": {"avg_qty": 4, "min_qty": 2, "max_qty": 8, "typical_price": 12000.0}
        },
        "complaints": [
            {"id": "CMP-101", "date": "Oct 12, 2026", "issue": "IBAN mismatch reported by Treasury", "status": "open"}
        ]
    },
    {
        "id": "VEN-004",
        "name": "AWS Cloud Services",
        "category": "Cloud Compute & AI Servers",
        "gstin": "27AAACA9999Q1Z1",
        "pan": "AAACA9999Q",
        "state": "Maharashtra (27)",
        "verified": True,
        "verified_phone": "+91 22 6789 0000",
        "verified_email": "aws-india-pay@amazon.com",
        "paid_invoice_count": 45,
        "total_disbursed": 18900000.0,
        "trust_score": 99,
        "known_invoice_patterns": ["INV-60", "INV-"],
        "known_bank_accounts": [
            {"bank_name": "HSBC India", "account_number": "0401128394", "ifsc": "HSBC0560002", "status": "primary"}
        ],
        "typical_items": {
            "EC2 / Vertex AI Compute": {"avg_qty": 1, "min_qty": 1, "max_qty": 1, "typical_price": 210400.0}
        },
        "complaints": []
    },
    {
        "id": "VEN-005",
        "name": "Tata Communications",
        "category": "Dedicated Leased Line & Fiber",
        "gstin": "27AAACT2233M1Z8",
        "pan": "AAACT2233M",
        "state": "Maharashtra (27)",
        "verified": True,
        "verified_phone": "+91 22 6655 8899",
        "verified_email": "enterprise@tatacommunications.com",
        "paid_invoice_count": 38,
        "total_disbursed": 3400000.0,
        "trust_score": 96,
        "known_invoice_patterns": ["INV-59", "INV-"],
        "known_bank_accounts": [
            {"bank_name": "State Bank of India", "account_number": "3092819283", "ifsc": "SBIN0000300", "status": "primary"}
        ],
        "typical_items": {
            "10Gbps Dark Fiber Uplink": {"avg_qty": 1, "min_qty": 1, "max_qty": 1, "typical_price": 68000.0}
        },
        "complaints": []
    }
]

INITIAL_INVOICES = [
    {
        "id": "INV-2026-0918",
        "invoice_number": "INV-2026-0918",
        "filename": "abc_tech_hardware_oct2026.pdf",
        "vendor_id": "VEN-001",
        "vendor_name": "ABC Technologies",
        "vendor_verified": True,
        "gstin": "27AAACA1234A1Z5",
        "issue_date": "Oct 24, 2026",
        "received_date": "Oct 24, 2026 · 14:32 IST",
        "sha256": "7f8b9d3e8a1c4b72e0915f2a93c71e8460d21a95bf08412e697a2cb184a12",
        "sha256_short": "7f8b9d...4a12",
        "total_amount": 159000.0,
        "taxable_amount": 150000.0,
        "cgst_amount": 4500.0,
        "sgst_amount": 4500.0,
        "igst_amount": 0.0,
        "bank_name": "ICICI Bank",
        "bank_account": "001105008821",
        "ifsc": "ICIC0000011",
        "historical_variance_pct": "+169.5%",
        "threat_score": 74,
        "risk_level": "Review Required",
        "badge_status": "Review",
        "theme": "tertiary",
        "confidence_pct": 98.4,
        "status": "review",
        "line_items": [
            {
                "description": "Laptop Stand (Ergonomic Pro)",
                "sku": "LS-902-AL",
                "qty": 5,
                "unit_price": 1000.0,
                "amount": 5000.0,
                "status": "Verified Regular",
                "flagged": False
            },
            {
                "description": "Mechanical Keyboard (Tenkeyless)",
                "sku": "KB-84-MXB",
                "qty": 50,
                "unit_price": 2000.0,
                "amount": 100000.0,
                "status": "Anomaly (Qty 50 vs Hist 5–10)",
                "flagged": True,
                "flag_reason": "Statistical quantity anomaly (+500%)"
            },
            {
                "description": "USB-C Dual 4K Display Hub",
                "sku": "HUB-8K-DUAL",
                "qty": 10,
                "unit_price": 5400.0,
                "amount": 54000.0,
                "status": "Verified Regular",
                "flagged": False
            }
        ],
        "signals": [
            {
                "id": "ev-1",
                "category": "Behavioral",
                "type": "warning",
                "icon": "account_balance",
                "badge": "High Risk",
                "badge_class": "bg-tertiary-container/30 text-tertiary",
                "title": "New payment destination account",
                "description": "Previous 14 invoices from this vendor used HDFC Bank ending in ...4901. Current invoice requests transfer to ICICI Bank ending in ...8821 registered 3 days ago.",
                "protocol": "Verify payment details with vendor through an out-of-band verified phone channel (+91 22 4920 1100). Do not approve automated ACH without signed change-of-banking affidavit."
            },
            {
                "id": "ev-2",
                "category": "Behavioral",
                "type": "warning",
                "icon": "inventory_2",
                "badge": "Volume Alert",
                "badge_class": "bg-tertiary-container/30 text-tertiary",
                "title": "Statistical quantity anomaly (+500%)",
                "description": "Historical keyboard order quantity: 5–10 units. Current invoice quantity: 50 units (500% spike over 90-day moving average).",
                "protocol": "90d Historical Baseline: 6.2 units / mo · PO Authorization Cap: 15 units."
            },
            {
                "id": "ev-3",
                "category": "Document",
                "type": "tamper",
                "icon": "edit_document",
                "badge": "OCR Tamper",
                "badge_class": "bg-error-container/30 text-error",
                "title": "Potential document tampering (Font glyph mismatch)",
                "description": "Font glyph metadata mismatch: A character within the quantity field has different bounding box font rendering properties compared to adjacent typography.",
                "protocol": "Font stream: Arial-BoldMT embedded (vector) vs. Raster overlay glyph detected at coordinate [X: 412.4, Y: 188.0]."
            }
        ],
        "passed_checks": [
            {"title": "GST Calculation & Tax ID Valid", "detail": "GSTIN 27AAACA1234A1Z5"},
            {"title": "DKIM & Domain Authenticity", "detail": "Pass (d=abctech.in)"}
        ],
        "financial_breakdown": {
            "taxable_subtotal": 50000.0,
            "cgst": 4500.0,
            "sgst": 4500.0,
            "expected_grand_total": 59000.0,
            "surplus_gap": 100000.0,
            "gap_explanation": "Exact delta directly corresponds to the 50x Mechanical Keyboard insertion (₹1,00,000) not matching Purchase Order PO-2026-441."
        },
        "document_inspection": {
            "authentic_glyph": "5",
            "authentic_font": "Helvetica Bold",
            "injected_glyph": "0",
            "injected_font": "Roboto Medium",
            "divergence": "Coordinate Bounding Box: [412.4 x 188.0] · Kerning compression divergence: -14%",
            "pdf_producer": "Skia/PDF m122",
            "modification_tool": "iText® 5.5.10 (Modified)",
            "revision_count": "2 Incremental Saves",
            "time_delta": "+18m 22s after creation"
        },
        "audit_logs": [
            {"time": "14:32:01", "event": "Invoice ingested via inbox daemon (invoice-inbound@guard.corp)", "status": "SUCCESS", "status_class": "text-secondary"},
            {"time": "14:32:02", "event": "DeepOCR glyph extraction finished in 420ms", "status": "OK", "status_class": "text-secondary"},
            {"time": "14:32:03", "event": "Anomaly trigger: GraphAudit flagged new unverified payout destination", "status": "FLAGGED", "status_class": "text-tertiary"}
        ]
    },
    {
        "id": "INV-8831",
        "invoice_number": "INV-8831",
        "filename": "cloudflare_enterprise_cdn.pdf",
        "vendor_id": "VEN-002",
        "vendor_name": "Cloudflare India Ltd",
        "vendor_verified": True,
        "gstin": "27AABCC5544R1ZM",
        "issue_date": "Oct 22, 2026",
        "received_date": "Oct 22, 2026 · 11:15 IST",
        "sha256": "4b19e2f89c0a1b2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d",
        "sha256_short": "4b19e2...5c6d",
        "total_amount": 42800.0,
        "taxable_amount": 36271.19,
        "cgst_amount": 3264.41,
        "sgst_amount": 3264.41,
        "igst_amount": 0.0,
        "bank_name": "Citibank N.A.",
        "bank_account": "0029384910",
        "ifsc": "CITI0000002",
        "historical_variance_pct": "+0.0%",
        "threat_score": 4,
        "risk_level": "Low Risk",
        "badge_status": "Safe",
        "theme": "secondary",
        "confidence_pct": 99.8,
        "status": "passed",
        "line_items": [
            {"description": "Enterprise CDN & Security Gateway (Oct 2026)", "sku": "CF-ENT-MO", "qty": 1, "unit_price": 36271.19, "amount": 36271.19, "status": "Verified Contract", "flagged": False}
        ],
        "signals": [],
        "passed_checks": [
            {"title": "GST Calculation & Tax ID Valid", "detail": "GSTIN 27AABCC5544R1ZM"},
            {"title": "Vendor Cryptographic Signature", "detail": "Verified RSA-2048"},
            {"title": "Known Bank Destination", "detail": "Matched Citibank Account *4910"},
            {"title": "Price Baseline Reconciled", "detail": "Matches Contract Schedule A"}
        ],
        "financial_breakdown": {
            "taxable_subtotal": 36271.19,
            "cgst": 3264.41,
            "sgst": 3264.41,
            "expected_grand_total": 42800.0,
            "surplus_gap": 0.0,
            "gap_explanation": "Zero variance detected against Master Subscription Agreement."
        },
        "document_inspection": {
            "authentic_glyph": "A",
            "authentic_font": "Inter Regular",
            "injected_glyph": None,
            "pdf_producer": "Adobe PDF Library 15.0",
            "modification_tool": "None (Direct Output)",
            "revision_count": "1 Save (Original)",
            "time_delta": "Synchronous"
        },
        "audit_logs": [
            {"time": "11:15:02", "event": "Ingested via API Webhook", "status": "SUCCESS", "status_class": "text-secondary"},
            {"time": "11:15:03", "event": "All 7 safety checkpoints passed", "status": "VERIFIED", "status_class": "text-secondary"}
        ]
    },
    {
        "id": "INV-7729",
        "invoice_number": "INV-7729",
        "filename": "zenith_stationery_supplies.pdf",
        "vendor_id": "VEN-003",
        "vendor_name": "Zenith Office Supplies",
        "vendor_verified": False,
        "gstin": "29AABCZ9988P1ZR",
        "issue_date": "Oct 20, 2026",
        "received_date": "Oct 20, 2026 · 09:40 IST",
        "sha256": "9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b",
        "sha256_short": "9a8b7c...9a8b",
        "total_amount": 84200.0,
        "taxable_amount": 71355.93,
        "cgst_amount": 0.0,
        "sgst_amount": 0.0,
        "igst_amount": 12844.07,
        "bank_name": "Federal Bank (Overseas Node)",
        "bank_account": "18293049182",
        "ifsc": "FDRL0001829",
        "historical_variance_pct": "+240.0%",
        "threat_score": 88,
        "risk_level": "High Risk",
        "badge_status": "High Risk",
        "theme": "error",
        "confidence_pct": 97.2,
        "status": "critical",
        "line_items": [
            {"description": "Executive Leather Task Chairs", "sku": "CHR-EXE-BLK", "qty": 8, "unit_price": 8919.49, "amount": 71355.93, "status": "Rate Card Divergence", "flagged": True, "flag_reason": "Unit price divergence (+48%)"}
        ],
        "signals": [
            {
                "id": "ev-z1",
                "category": "Behavioral",
                "type": "critical",
                "icon": "warning",
                "badge": "IBAN Mismatch",
                "badge_class": "bg-error-container/30 text-error",
                "title": "IBAN / Overseas Wire Route Mismatch",
                "description": "Invoice specifies wire payment to offshore beneficiary account differing from domestic vendor registration.",
                "protocol": "Halt payment immediately. Forward to Fraud & Anti-Money Laundering response unit."
            },
            {
                "id": "ev-z2",
                "category": "Vendor",
                "type": "warning",
                "icon": "flag",
                "badge": "Dispute Flag",
                "badge_class": "bg-error-container/30 text-error",
                "title": "Active Compliance Disputes",
                "description": "Vendor has unresolved complaints regarding previous duplicate billings.",
                "protocol": "Escalate to Senior Controller for vendor suspension review."
            }
        ],
        "passed_checks": [
            {"title": "GSTIN Structure Valid", "detail": "State 29 Karnataka"}
        ],
        "financial_breakdown": {
            "taxable_subtotal": 71355.93,
            "cgst": 0.0,
            "sgst": 0.0,
            "expected_grand_total": 84200.0,
            "surplus_gap": 0.0,
            "gap_explanation": "Tax arithmetic reconciles with 18% IGST; however banking destination is critical threat."
        },
        "document_inspection": {
            "authentic_glyph": None,
            "pdf_producer": "Canva PDF Exporter",
            "modification_tool": "Ghostscript v9.50",
            "revision_count": "3 Incremental Saves",
            "time_delta": "+2h 14m"
        },
        "audit_logs": [
            {"time": "09:40:11", "event": "Ingested via Vendor Portal", "status": "WARNING", "status_class": "text-error"},
            {"time": "09:40:12", "event": "Overseas routing node flagged by AML Sentinel", "status": "BLOCKED", "status_class": "text-error"}
        ]
    },
    {
        "id": "INV-6012",
        "invoice_number": "INV-6012",
        "filename": "aws_compute_vertex_sep2026.pdf",
        "vendor_id": "VEN-004",
        "vendor_name": "AWS Cloud Services",
        "vendor_verified": True,
        "gstin": "27AAACA9999Q1Z1",
        "issue_date": "Oct 18, 2026",
        "received_date": "Oct 18, 2026 · 16:05 IST",
        "sha256": "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b",
        "sha256_short": "1a2b3c...1a2b",
        "total_amount": 210400.0,
        "taxable_amount": 178305.08,
        "cgst_amount": 16047.46,
        "sgst_amount": 16047.46,
        "igst_amount": 0.0,
        "bank_name": "HSBC India",
        "bank_account": "0401128394",
        "ifsc": "HSBC0560002",
        "historical_variance_pct": "+2.4%",
        "threat_score": 2,
        "risk_level": "Low Risk",
        "badge_status": "Safe",
        "theme": "secondary",
        "confidence_pct": 99.9,
        "status": "passed",
        "line_items": [
            {"description": "AWS Compute & Database Cluster (Mumbai Region)", "sku": "AWS-MUM-PRD", "qty": 1, "unit_price": 178305.08, "amount": 178305.08, "status": "Verified Regular", "flagged": False}
        ],
        "signals": [],
        "passed_checks": [
            {"title": "Cryptographic Signature Pass", "detail": "Amazon Web Services Trust CA"},
            {"title": "GSTIN Validated", "detail": "27AAACA9999Q1Z1"},
            {"title": "Account Matches Master Agreement", "detail": "HSBC *8394"}
        ],
        "financial_breakdown": {
            "taxable_subtotal": 178305.08,
            "cgst": 16047.46,
            "sgst": 16047.46,
            "expected_grand_total": 210400.0,
            "surplus_gap": 0.0,
            "gap_explanation": "Full automated reconciliation against AWS Cost Management API."
        },
        "document_inspection": {
            "authentic_glyph": "W",
            "pdf_producer": "AWS Invoice Engine v2",
            "modification_tool": "None",
            "revision_count": "1 Save",
            "time_delta": "Instant"
        },
        "audit_logs": [
            {"time": "16:05:00", "event": "Automated ingestion via AWS B2B Gateway", "status": "SUCCESS", "status_class": "text-secondary"}
        ]
    },
    {
        "id": "INV-5902",
        "invoice_number": "INV-5902",
        "filename": "tata_fiber_darklink.pdf",
        "vendor_id": "VEN-005",
        "vendor_name": "Tata Communications",
        "vendor_verified": True,
        "gstin": "27AAACT2233M1Z8",
        "issue_date": "Oct 15, 2026",
        "received_date": "Oct 15, 2026 · 10:20 IST",
        "sha256": "5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d",
        "sha256_short": "5c6d7e...5c6d",
        "total_amount": 68000.0,
        "taxable_amount": 57627.12,
        "cgst_amount": 5186.44,
        "sgst_amount": 5186.44,
        "igst_amount": 0.0,
        "bank_name": "State Bank of India",
        "bank_account": "3092819283",
        "ifsc": "SBIN0000300",
        "historical_variance_pct": "-1.2%",
        "threat_score": 11,
        "risk_level": "Low Risk",
        "badge_status": "Safe",
        "theme": "secondary",
        "confidence_pct": 98.9,
        "status": "passed",
        "line_items": [
            {"description": "10Gbps Dedicated Dark Fiber Uplink", "sku": "TATA-FIB-10G", "qty": 1, "unit_price": 57627.12, "amount": 57627.12, "status": "Verified Regular", "flagged": False}
        ],
        "signals": [],
        "passed_checks": [
            {"title": "GSTIN Active & Verified", "detail": "27AAACT2233M1Z8"},
            {"title": "SBI Account Verified", "detail": "SBIN *9283"}
        ],
        "financial_breakdown": {
            "taxable_subtotal": 57627.12,
            "cgst": 5186.44,
            "sgst": 5186.44,
            "expected_grand_total": 68000.0,
            "surplus_gap": 0.0,
            "gap_explanation": "Reconciled with telecom SLA agreement."
        },
        "document_inspection": {
            "authentic_glyph": "T",
            "pdf_producer": "Tata Systems SAP Spool",
            "modification_tool": "None",
            "revision_count": "1 Save",
            "time_delta": "Instant"
        },
        "audit_logs": [
            {"time": "10:20:05", "event": "Ingested via Electronic EDI", "status": "SUCCESS", "status_class": "text-secondary"}
        ]
    }
]

COMPLAINTS = [
    {
        "id": "CMP-2026-001",
        "vendor_id": "VEN-003",
        "vendor_name": "Zenith Office Supplies",
        "reported_date": "Oct 12, 2026",
        "invoice_ref": "INV-7729",
        "severity": "CRITICAL",
        "category": "Payment Routing & Overseas Wire Mismatch",
        "description": "Invoice requested wire transfer to unverified overseas beneficiary account instead of registered domestic Bangalore branch.",
        "status": "Under Investigation",
        "assigned_to": "Marcus Thorne (Fraud Risk Officer)"
    },
    {
        "id": "CMP-2026-002",
        "vendor_id": "VEN-001",
        "vendor_name": "ABC Technologies",
        "reported_date": "Oct 24, 2026",
        "invoice_ref": "INV-2026-0918",
        "severity": "MEDIUM",
        "category": "Unverified Payout Account Update",
        "description": "Change in bank account destination from HDFC *4901 to ICICI *8821 without attached change-of-banking affidavit.",
        "status": "Pending Vendor Affidavit",
        "assigned_to": "Alex Vance (Finance Sec)"
    }
]
