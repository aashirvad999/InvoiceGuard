"""
Centralized Risk Engine & Weighted Scoring for InvoiceGuard (Req 27)
Maintains transparent, configurable weights and deterministic scoring boundaries.
Does NOT rely on LLMs for final risk score calculation.
"""

from typing import Dict, List, Any, Optional

# Centralized, configurable weights dictionary
SIGNAL_WEIGHTS: Dict[str, Dict[str, Any]] = {
    "math_inconsistency": {
        "weight": 40,
        "severity": "CRITICAL",
        "category": "Financial",
        "title": "🔴 Mathematical inconsistency"
    },
    "grand_total_mismatch": {
        "weight": 40,
        "severity": "CRITICAL",
        "category": "Financial",
        "title": "🔴 Grand total mismatch"
    },
    "taxable_amount_mismatch": {
        "weight": 30,
        "severity": "HIGH",
        "category": "Financial",
        "title": "⚠ Taxable amount mismatch"
    },
    "line_total_mismatch": {
        "weight": 25,
        "severity": "HIGH",
        "category": "Financial",
        "title": "⚠ Line item calculation mismatch"
    },
    "cgst_mismatch": {
        "weight": 25,
        "severity": "HIGH",
        "category": "Financial",
        "title": "⚠ CGST calculation mismatch"
    },
    "sgst_mismatch": {
        "weight": 25,
        "severity": "HIGH",
        "category": "Financial",
        "title": "⚠ SGST calculation mismatch"
    },
    "igst_mismatch": {
        "weight": 25,
        "severity": "HIGH",
        "category": "Financial",
        "title": "⚠ IGST calculation mismatch"
    },
    "gst_total_mismatch": {
        "weight": 25,
        "severity": "HIGH",
        "category": "Financial",
        "title": "⚠ GST total mismatch"
    },
    "duplicate_invoice": {
        "weight": 35,
        "severity": "HIGH",
        "category": "Document",
        "title": "Potential Duplicate"
    },
    "new_payment_destination": {
        "weight": 30,
        "severity": "HIGH",
        "category": "Payment Destination",
        "title": "⚠ New payment destination"
    },
    "font_inconsistency": {
        "weight": 28,
        "severity": "HIGH",
        "category": "Document",
        "title": "Potential document tampering signal (Potential font inconsistency)"
    },
    "vendor_spoofing": {
        "weight": 35,
        "severity": "HIGH",
        "category": "Vendor Identity",
        "title": "Potential vendor name spoofing"
    },
    "invalid_gstin": {
        "weight": 30,
        "severity": "HIGH",
        "category": "Tax & Compliance",
        "title": "⚠ Invalid GSTIN Statutory Format"
    },
    "gstin_format_invalid": {
        "weight": 30,
        "severity": "HIGH",
        "category": "Tax & Compliance",
        "title": "GSTIN format ⚠ Invalid format"
    },
    "gst_calculation_mismatch": {
        "weight": 25,
        "severity": "HIGH",
        "category": "Financial",
        "title": "GST calculation mismatch"
    },
    "unusual_quantity": {
        "weight": 25,
        "severity": "HIGH",
        "category": "Behavioral",
        "title": "⚠ Unusual quantity"
    },
    "unusual_price": {
        "weight": 20,
        "severity": "MEDIUM",
        "category": "Behavioral",
        "title": "⚠ Unusual price"
    },
    "unusual_item": {
        "weight": 20,
        "severity": "MEDIUM",
        "category": "Behavioral",
        "title": "⚠ Unusual item"
    },
    "suspicious_metadata": {
        "weight": 22,
        "severity": "MEDIUM",
        "category": "Document",
        "title": "Potential document modification signal"
    },
    "unusual_vendor_frequency": {
        "weight": 20,
        "severity": "MEDIUM",
        "category": "Behavioral",
        "title": "⚠ Unusual vendor frequency"
    },
    "numbering_pattern_deviation": {
        "weight": 18,
        "severity": "MEDIUM",
        "category": "Document",
        "title": "Invoice numbering pattern deviation"
    },
    "vendor_unverified": {
        "weight": 10,
        "severity": "LOW",
        "category": "Vendor Identity",
        "title": "Unverified vendor ledger"
    }
}

# Risk Threshold Boundaries
# 0–30: Low Risk | 31–70: Review Required | 71–100: High Risk
RISK_THRESHOLDS = {
    "low_max": 30,
    "review_max": 70
}


def calculate_deterministic_risk_score(
    detected_signals: List[Dict[str, Any]],
    passed_checks: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Computes explainable, deterministic weighted threat score (0-100).
    """
    base_score = 4 if not detected_signals else 0
    calculated_score = base_score
    formatted_signals = []

    for sig in detected_signals:
        sig_type = sig.get("id") or sig.get("type", "custom_signal")
        cfg = SIGNAL_WEIGHTS.get(sig_type, {})
        weight = sig.get("score_impact", cfg.get("weight", 15))
        severity = sig.get("severity", cfg.get("severity", "MEDIUM"))
        
        calculated_score += weight
        
        formatted_signals.append({
            "id": sig_type,
            "type": sig_type,
            "severity": severity,
            "category": sig.get("category", cfg.get("category", "General")),
            "title": sig.get("title", cfg.get("title", sig_type)),
            "description": sig.get("description", ""),
            "evidence": sig.get("evidence", sig.get("description", "")),
            "expected_value": sig.get("expected_value", sig.get("expected", "Historical baseline")),
            "actual_value": sig.get("actual_value", sig.get("actual", "Extracted invoice value")),
            "why_it_matters": sig.get("why_it_matters", sig.get("why", "Impacts financial authorization & anti-fraud safeguards.")),
            "recommended_action": sig.get("recommended_action", sig.get("protocol", "Verify through independent secondary channel.")),
            "score_impact": weight
        })

    # Clamp score to [0, 100]
    final_score = min(100, max(0, calculated_score))

    # Determine risk level based on standard thresholds
    if final_score <= RISK_THRESHOLDS["low_max"]:
        level = "low"
        risk_level = "Low Risk"
        badge_status = "Safe"
        theme = "secondary"
    elif final_score <= RISK_THRESHOLDS["review_max"]:
        level = "review"
        risk_level = "Review Required"
        badge_status = "Review"
        theme = "tertiary"
    else:
        level = "high"
        risk_level = "High Risk"
        badge_status = "High Risk"
        theme = "error"

    return {
        "score": final_score,
        "level": level,
        "risk_level": risk_level,
        "badge_status": badge_status,
        "theme": theme,
        "signals": formatted_signals,
        "passed_checks": passed_checks or []
    }
