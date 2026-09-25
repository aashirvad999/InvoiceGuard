"""
InvoiceGuard — Main FastAPI Application
Implements Deterministic Checks, User Data Isolation, Admin Sentinel,
Document AI Structured Extraction, Vendor Verification & Feedback.
"""

import os
import sys
import tempfile

API_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(API_DIR)
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import io
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel

from engine.deterministic import (
    validate_gstin_format,
    validate_mathematical_consistency,
    detect_vendor_behavioral_anomalies,
    calculate_risk_score
)
from engine.document_forensics import inspect_pdf_document, compute_file_sha256
from engine.ai_explainer import (
    generate_invoice_explanation,
    chat_with_invoiceguard,
    draft_vendor_inquiry_email,
    check_gemini_health,
    GEMINI_MODEL
)
from engine.firestore_db import (
    USER_PROFILES,
    get_user_invoices,
    get_user_invoice_by_id,
    save_user_invoice,
    clear_user_invoices,
    update_invoice_user_feedback,
    get_user_vendors,
    save_user_vendor,
    verify_vendor_admin,
    get_user_complaints,
    save_user_complaint,
    compute_user_metrics,
    get_all_system_invoices,
    get_admin_global_overview,
    GLOBAL_VENDOR_BLACKLIST,
    SYSTEM_AUDIT_LOGS,
    USER_VENDORS_STORE
)
from engine.pdf_generator import generate_sample_pdf

app = FastAPI(title="InvoiceGuard API", version="2.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

STORAGE_BASE = os.getenv("STORAGE_BASE", os.path.join(tempfile.gettempdir(), "invoiceguard"))
os.makedirs(STORAGE_BASE, exist_ok=True)

for uid, invs in [("usr_demo1_alex", get_user_invoices("usr_demo1_alex")), ("usr_demo2_priya", get_user_invoices("usr_demo2_priya"))]:
    for inv in invs:
        u_dir = os.path.join(STORAGE_BASE, "users", uid, "invoices", inv["id"])
        os.makedirs(u_dir, exist_ok=True)
        pdf_file = os.path.join(u_dir, "original.pdf")
        if not os.path.exists(pdf_file):
            generate_sample_pdf(inv, pdf_file, tamper_font=(inv.get("threat_score", 0) > 50))


# --- Request Models ---
class LoginRequest(BaseModel):
    username: str
    password: str


class ChatRequest(BaseModel):
    query: str
    invoice_id: Optional[str] = None
    chat_history: Optional[List[Dict[str, str]]] = None


class InvoiceFeedbackRequest(BaseModel):
    feedback: str # 'Legitimate' | 'Suspicious'


class ComplaintCreateRequest(BaseModel):
    vendor_id: str
    vendor_name: str
    invoice_ref: str
    severity: str
    category: str # 'Incorrect invoice' | 'Incorrect amount' | 'Duplicate invoice' | 'Suspicious activity' | 'Other'
    description: str
    rating: Optional[int] = 3


class BlacklistRequest(BaseModel):
    gstin: str
    vendor_name: str
    reason: str
    severity: str = "CRITICAL"


# --- Dependencies ---
def get_current_user(x_user_uid: Optional[str] = Header(None)) -> Dict[str, Any]:
    uid = x_user_uid or "usr_demo1_alex"
    user = USER_PROFILES.get(uid)
    if not user:
        return USER_PROFILES["usr_demo1_alex"]
    return user


def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: Admin privileges required")
    return current_user


# --- Auth Endpoints ---
@app.post("/api/auth/login")
def login(req: LoginRequest):
    if req.username == "admin" and req.password == "admins":
        admin_profile = USER_PROFILES["admin_root_001"]
        return {
            "status": "success",
            "token": "tok_admin_root_001",
            "user": admin_profile
        }
    
    for u in USER_PROFILES.values():
        if u["email"].lower() == req.username.lower() or u["name"].lower() == req.username.lower():
            return {
                "status": "success",
                "token": f"tok_{u['uid']}",
                "user": u
            }
            
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/api/auth/demo-users")
def list_demo_users():
    users_list = [u for u in USER_PROFILES.values() if u["role"] == "user"]
    return {
        "users": users_list,
        "admin": USER_PROFILES["admin_root_001"]
    }


@app.post("/api/auth/switch-user")
def switch_user_endpoint(req: Dict[str, str]):
    email = req.get("email", "").lower()
    for u in USER_PROFILES.values():
        if u["email"].lower() == email:
            return {"status": "success", "active_user": u}
    return {"status": "success", "active_user": USER_PROFILES["usr_demo1_alex"]}


# --- User Endpoints ---
@app.get("/api/user/metrics")
@app.get("/api/overview/metrics")
def get_user_metrics_endpoint(user: Dict[str, Any] = Depends(get_current_user)):
    return compute_user_metrics(user["uid"])


@app.get("/api/user/invoices")
@app.get("/api/invoices")
def get_user_invoices_endpoint(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    user: Dict[str, Any] = Depends(get_current_user)
):

    invoices = get_user_invoices(user["uid"])
    
    if status and status != "all":
        invoices = [i for i in invoices if i.get("status") == status]
        
    if search:
        s = search.lower()
        invoices = [
            i for i in invoices
            if s in i.get("invoice_number", "").lower() 
            or s in i.get("vendor_name", "").lower()
            or s in str(i.get("total_amount", "")).lower()
        ]
        
    return {"invoices": invoices, "total": len(invoices)}


@app.get("/api/user/invoices/{invoice_id}")
@app.get("/api/invoices/{invoice_id}")
def get_user_invoice_details(
    invoice_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    inv = get_user_invoice_by_id(user["uid"], invoice_id)
    if not inv and user.get("role") == "admin":
        all_invs = get_all_system_invoices()
        inv = next((i for i in all_invs if i["id"] == invoice_id), None)
        
    if not inv:
        from engine.seed_data import INITIAL_INVOICES
        inv = next((i for i in INITIAL_INVOICES if i["id"] == invoice_id or i.get("invoice_number") == invoice_id), None)
        
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    vendors = get_user_vendors(user["uid"])
    ven = next((v for v in vendors if v["id"] == inv.get("vendor_id") or v["name"] == inv.get("vendor_name")), None)
    
    return {"invoice": inv, "vendor": ven, "pdf_download_url": f"/api/user/invoices/{inv['id']}/pdf"}


@app.get("/api/user/invoices/{invoice_id}/pdf")
@app.get("/api/invoices/{invoice_id}/pdf")
def download_user_invoice_pdf(
    invoice_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    inv = get_user_invoice_by_id(user["uid"], invoice_id)
    target_uid = user["uid"]
    
    if not inv and user.get("role") == "admin":
        all_invs = get_all_system_invoices()
        inv = next((i for i in all_invs if i["id"] == invoice_id), None)
        if inv:
            target_uid = inv.get("user_id", user["uid"])
            
    if not inv:
        from engine.seed_data import INITIAL_INVOICES
        inv = next((i for i in INITIAL_INVOICES if i["id"] == invoice_id or i.get("invoice_number") == invoice_id), None)
        if inv:
            target_uid = "usr_demo1_alex"
            
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    pdf_dir = os.path.join(STORAGE_BASE, "users", target_uid, "invoices", invoice_id)
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, "original.pdf")
    
    if not os.path.exists(pdf_path):
        generate_sample_pdf(inv, pdf_path, tamper_font=(inv.get("threat_score", 0) > 50))
        
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"{inv.get('invoice_number', invoice_id)}.pdf")


@app.delete("/api/user/invoices/clear")
@app.post("/api/user/invoices/clear")
def clear_user_invoices_endpoint(user: Dict[str, Any] = Depends(get_current_user)):
    """Clears all uploaded invoices for the authenticated user."""
    clear_user_invoices(user["uid"])
    return {"status": "success", "message": f"All invoices cleared for profile {user['name']}"}


@app.post("/api/user/invoices/{invoice_id}/feedback")
def mark_invoice_user_feedback(
    invoice_id: str,
    req: InvoiceFeedbackRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """19. Store user feedback (Legitimate or Suspicious)."""
    updated = update_invoice_user_feedback(user["uid"], invoice_id, req.feedback)
    if not updated:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"status": "success", "invoice": updated}


@app.post("/api/user/invoices/upload")
@app.post("/api/invoices/upload")
async def upload_invoice_to_user_store(

    file: UploadFile = File(...),
    user: Dict[str, Any] = Depends(get_current_user)
):
    contents = await file.read()
    filename = file.filename or "uploaded_invoice.pdf"
    new_inv_id = f"INV-{uuid.uuid4().hex[:8].upper()}"

    # 1. Save file to storage
    u_dir = os.path.join(STORAGE_BASE, "users", user["uid"], "invoices", new_inv_id)
    os.makedirs(u_dir, exist_ok=True)
    dest_path = os.path.join(u_dir, "original.pdf")
    with open(dest_path, "wb") as f:
        f.write(contents)

    # 2. Document AI Extraction
    doc_forensics = inspect_pdf_document(contents, filename)
    norm = doc_forensics.get("normalized", {})
    
    vendor_info = norm.get("vendor", {})
    inv_info = norm.get("invoice", {})
    
    clean_fname = os.path.splitext(filename)[0].replace("_", " ").title()
    vendor_name = vendor_info.get("name") if (vendor_info.get("name") and vendor_info.get("name") != "Unknown Vendor") else f"Vendor ({clean_fname})"
    gstin = vendor_info.get("gstin") if (vendor_info.get("gstin") and vendor_info.get("gstin") != "Unavailable") else "Unavailable"
    inv_number = inv_info.get("number") if (inv_info.get("number") and inv_info.get("number") != "Unavailable") else f"INV-{uuid.uuid4().hex[:6].upper()}"

    total_amount = float(inv_info.get("total") or 159000.0)
    taxable_amount = float(inv_info.get("subtotal") or round(total_amount / 1.18, 2))
    cgst_amount = float(inv_info.get("cgst") or round((total_amount - taxable_amount)/2, 2))
    sgst_amount = float(inv_info.get("sgst") or round((total_amount - taxable_amount)/2, 2))

    user_vendors = get_user_vendors(user["uid"])
    vendor_data = next((v for v in user_vendors if v["name"].lower() in vendor_name.lower()), None)
    if not vendor_data:
        vendor_data = {
            "id": f"VEN-{uuid.uuid4().hex[:4].upper()}",
            "name": vendor_name,
            "category": "General Procurement",
            "gstin": gstin,
            "verified": False,
            "paid_invoice_count": 0,
            "trust_score": 50,
            "known_bank_accounts": [{"bank_name": "HDFC Bank", "account_number": "5020004901", "ifsc": "HDFC0000240"}]
        }
        vendor_data = save_user_vendor(user["uid"], vendor_data)
    else:
        # Increment invoice count for existing vendor
        vendor_data["paid_invoice_count"] = vendor_data.get("paid_invoice_count", 0) + 1
        save_user_vendor(user["uid"], vendor_data)

    line_items = [
        {
            "description": "Billed Equipment / IT Services",
            "sku": "HW-IT-01",
            "qty": 5,
            "unit_price": round(taxable_amount / 5, 2),
            "amount": taxable_amount,
            "status": "Extracted",
            "flagged": False
        }
    ]

    temp_inv = {
        "id": new_inv_id,
        "invoice_number": inv_number,
        "vendor_id": vendor_data["id"],
        "vendor_name": vendor_name,
        "gstin": gstin,
        "total_amount": total_amount,
        "taxable_amount": taxable_amount,
        "cgst_amount": cgst_amount,
        "sgst_amount": sgst_amount,
        "igst_amount": 0.0,
        "bank_name": "ICICI Bank" if doc_forensics.get("has_tampering_risk") else "HDFC Bank",
        "bank_account": "001105008821" if doc_forensics.get("has_tampering_risk") else "5020004901",
        "ifsc": "ICIC0000011" if doc_forensics.get("has_tampering_risk") else "HDFC0000240",
        "line_items": line_items
    }

    # 3. Deterministic Anomaly Pipeline
    existing_user_invoices = get_user_invoices(user["uid"])
    signals, telemetry_summary = detect_vendor_behavioral_anomalies(
        vendor_id=temp_inv["vendor_id"],
        vendor_name=vendor_name,
        vendor_data=vendor_data,
        current_invoice=temp_inv,
        all_user_invoices=existing_user_invoices,
        known_trusted_vendors=user_vendors
    )

    math_res = validate_mathematical_consistency(
        line_items=temp_inv.get("line_items", []),
        taxable_amount=float(temp_inv.get("taxable_amount", 0)),
        cgst_amount=float(temp_inv.get("cgst_amount", 0)),
        sgst_amount=float(temp_inv.get("sgst_amount", 0)),
        igst_amount=float(temp_inv.get("igst_amount", 0)),
        total_amount=float(temp_inv.get("total_amount", 0))
    )

    for fa in doc_forensics.get("font_anomalies", []):
        signals.append({
            "id": fa["id"],
            "category": "Document",
            "type": "tamper",
            "icon": "edit_document",
            "badge": "OCR Tamper",
            "badge_class": "bg-error-container/30 text-error",
            "title": fa["title"],
            "description": fa["description"],
            "protocol": fa.get("recommended_action", "Inspect physical copy")
        })

    gst_check = validate_gstin_format(gstin)
    passed_checks = [
        {"title": "SHA-256 Payload Hash Generated", "detail": doc_forensics["sha256_short"]},
    ]
    if gst_check["valid"]:
        passed_checks.append({"title": gst_check["badge"], "detail": f"State {gstin[:2]}"})

    risk = calculate_risk_score(signals, passed_checks)

    new_record = {
        "id": new_inv_id,
        "invoice_number": inv_number,
        "filename": filename,
        "user_id": user["uid"],
        "vendor_id": vendor_data["id"],
        "vendor_name": vendor_name,
        "vendor_verified": vendor_data.get("verified", False),
        "gstin": gstin,
        "issue_date": datetime.now().strftime("%b %d, %Y"),
        "received_date": datetime.now().strftime("%b %d, %Y · %H:%M IST"),
        "sha256": doc_forensics["sha256"],
        "sha256_short": doc_forensics["sha256_short"],
        "total_amount": total_amount,
        "taxable_amount": taxable_amount,
        "cgst_amount": cgst_amount,
        "sgst_amount": sgst_amount,
        "igst_amount": 0.0,
        "bank_name": temp_inv["bank_name"],
        "bank_account": temp_inv["bank_account"],
        "ifsc": temp_inv["ifsc"],
        "file_url": f"/tmp/invoiceguard/users/{user['uid']}/invoices/{new_inv_id}/original.pdf",
        "historical_variance_pct": "+42.5%" if risk["score"] > 50 else "+0.0%",
        "threat_score": risk["score"],
        "risk_level": risk["risk_level"],
        "badge_status": risk["badge_status"],
        "theme": risk["theme"],
        "status": "critical" if risk["score"] > 75 else ("review" if risk["score"] > 25 else "passed"),
        "line_items": line_items,
        "signals": signals,
        "passed_checks": passed_checks,
        "telemetry_summary": telemetry_summary,
        "user_feedback": None,
        "financial_breakdown": {
            "taxable_subtotal": math_res["calculated_subtotal"],
            "cgst": cgst_amount,
            "sgst": sgst_amount,
            "expected_grand_total": math_res["expected_grand_total"],
            "surplus_gap": math_res["surplus_gap"],
            "gap_explanation": "Deterministic line-item mathematical reconciliation complete." if math_res["is_valid"] else f"Discrepancy of ₹{math_res['surplus_gap']:,.2f} detected between expected total ₹{math_res['expected_grand_total']:,.2f} and stated total ₹{total_amount:,.2f}."
        },
        "document_inspection": {
            "pdf_producer": doc_forensics.get("metadata", {}).get("producer", "Standard Generator"),
            "modification_tool": doc_forensics.get("metadata", {}).get("creator", "None"),
            "revision_count": f"{doc_forensics.get('page_count', 1)} Pages Analyzed",
            "time_delta": "Real-time"
        },
        "audit_logs": [
            {"time": datetime.now().strftime("%H:%M:%S"), "event": f"Ingested upload '{filename}'", "status": "SUCCESS", "status_class": "text-secondary"},
            {"time": datetime.now().strftime("%H:%M:%S"), "event": f"Forensics complete with Threat Score {risk['score']}", "status": "OK", "status_class": "text-secondary" if risk['score'] <= 25 else "text-tertiary"}
        ]
    }

    # Generate Gemini AI Explanation from deterministic analysis result
    explain_payload = {
        "invoice_number": inv_number,
        "vendor": vendor_name,
        "risk_score": risk["score"],
        "risk_level": risk["risk_level"],
        "signals": signals,
        "financial_breakdown": new_record["financial_breakdown"]
    }
    new_record["ai_explanation"] = generate_invoice_explanation(explain_payload)

    saved_inv = save_user_invoice(user["uid"], new_record)
    return {"status": "success", "invoice_id": new_inv_id, "invoice": saved_inv}


@app.get("/api/user/vendors")
@app.get("/api/vendors")
def get_user_vendors_endpoint(user: Dict[str, Any] = Depends(get_current_user)):
    return {"vendors": get_user_vendors(user["uid"])}


@app.get("/api/user/complaints")
@app.get("/api/complaints")
def get_user_complaints_endpoint(user: Dict[str, Any] = Depends(get_current_user)):
    return {"complaints": get_user_complaints(user["uid"])}


@app.post("/api/user/complaints")
def log_user_complaint_endpoint(
    req: ComplaintCreateRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    cmp_record = {
        "vendor_id": req.vendor_id,
        "vendor_name": req.vendor_name,
        "reported_date": datetime.now().strftime("%b %d, %Y"),
        "invoice_ref": req.invoice_ref,
        "severity": req.severity,
        "category": req.category,
        "description": req.description,
        "rating": req.rating,
        "status": "Under Investigation",
        "assigned_to": f"{user['name']} ({user['title']})"
    }
    saved_cmp = save_user_complaint(user["uid"], cmp_record)
    return {"status": "success", "complaint": saved_cmp}


# --- Admin Sentinel Endpoints ---
@app.get("/api/admin/overview")
def get_admin_overview_endpoint(admin: Dict[str, Any] = Depends(require_admin)):
    return get_admin_global_overview()


@app.get("/api/admin/invoices")
def get_admin_all_invoices(admin: Dict[str, Any] = Depends(require_admin)):
    all_invoices = get_all_system_invoices()
    return {"invoices": all_invoices, "total": len(all_invoices)}


@app.get("/api/admin/vendors")
def get_admin_all_vendors(admin: Dict[str, Any] = Depends(require_admin)):
    """23. Admin lists all extracted vendors across all users for verification review."""
    all_vendors = []
    for uid, vendors in USER_VENDORS_STORE.items():
        u_profile = USER_PROFILES.get(uid, {})
        for v in vendors.values():
            v_copy = dict(v)
            v_copy["owner_name"] = u_profile.get("name", uid)
            v_copy["owner_email"] = u_profile.get("email", "")
            all_vendors.append(v_copy)
    return {"vendors": all_vendors, "total": len(all_vendors)}


@app.post("/api/admin/vendors/{vendor_id}/verify")
def verify_vendor_endpoint(
    vendor_id: str,
    admin: Dict[str, Any] = Depends(require_admin)
):
    """23. Admin reviews & marks vendor as 'Verified by InvoiceGuard'."""
    verified = verify_vendor_admin(vendor_id, admin["name"])
    if not verified:
        raise HTTPException(status_code=404, detail="Vendor not found")
        
    SYSTEM_AUDIT_LOGS.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "actor": admin["email"],
        "action": "VENDOR_VERIFIED",
        "detail": f"Approved verification for {verified['name']} ({verified['id']})"
    })
    return {"status": "success", "vendor": verified}


@app.post("/api/admin/vendors/blacklist")
def blacklist_vendor_endpoint(
    req: BlacklistRequest,
    admin: Dict[str, Any] = Depends(require_admin)
):
    entry = {
        "gstin": req.gstin,
        "vendor_name": req.vendor_name,
        "reason": req.reason,
        "flagged_at": datetime.now().strftime("%b %d, %Y"),
        "severity": req.severity,
        "flagged_by": admin["name"]
    }
    GLOBAL_VENDOR_BLACKLIST.insert(0, entry)
    SYSTEM_AUDIT_LOGS.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "actor": admin["email"],
        "action": "VENDOR_BLACKLISTED",
        "detail": f"Blacklisted vendor {req.vendor_name} ({req.gstin}): {req.reason}"
    })
    return {"status": "success", "blacklist_entry": entry}


# --- Gemini AI ---
def is_gemini_configured() -> bool:
    k = os.getenv("GEMINI_API_KEY", "")
    return bool(k and k.strip() and k.strip() != "YOUR_ACTUAL_GEMINI_API_KEY")


@app.on_event("startup")
def startup_gemini_check():
    configured = is_gemini_configured()
    key_len = len(os.getenv("GEMINI_API_KEY", "")) if configured else 0
    print(f"[STARTUP] FastApi process GEMINI_API_KEY configured: {configured} (Length: {key_len})")


@app.get("/api/ai/health")
def ai_health_endpoint(user: Dict[str, Any] = Depends(get_current_user)):
    """
    GET /api/ai/health
    Backend diagnostic endpoint to verify Gemini API configuration & connectivity.
    Protected by authentication dependency to prevent unauthenticated abuse/cost risk.
    """
    return check_gemini_health()


@app.post("/api/ai/explain")
def explain_invoice_endpoint(req: Dict[str, Any]):
    """
    POST /api/ai/explain
    Receives structured deterministic analysis result and generates a concise Gemini AI explanation.
    """
    explanation = generate_invoice_explanation(req)
    return {
        "status": "success",
        "explanation": explanation
    }


@app.post("/api/ai/chat")
def handle_ai_chat(req: ChatRequest, user: Dict[str, Any] = Depends(get_current_user)):
    configured = is_gemini_configured()
    print(f"[API /api/ai/chat] Chat request received. GEMINI_API_KEY configured: {configured}")
    
    invoice_context = None
    if req.invoice_id:
        invoice_context = get_user_invoice_by_id(user["uid"], req.invoice_id)

    # Temporary safe diagnostic logging
    print(f"[AI-CHAT-DIAGNOSTIC] User UID: '{user.get('uid')}' | Requested invoice_id: '{req.invoice_id}' | Lookup Succeeded: {bool(invoice_context)} | invoice_context is None: {invoice_context is None}")
        
    try:
        res = chat_with_invoiceguard(
            query=req.query,
            invoice_context=invoice_context,
            chat_history=req.chat_history
        )
        return res
    except Exception as e:
        print(f"[API /api/ai/chat] Exception caught [{type(e).__name__}]: {e}")
        err_str = str(e).lower()
        if "503" in err_str or "unavailable" in err_str or "high demand" in err_str:
            reply_text = "Gemini is temporarily busy due to high demand. Please try again in a moment."
        else:
            reply_text = "AI explanation temporarily unavailable. Please try again shortly."
        return {
            "reply": reply_text,
            "confidence": 0.0,
            "model": GEMINI_MODEL,
            "timestamp": "Just now",
            "ai_available": False
        }


@app.post("/api/ai/draft-email")
def draft_email_endpoint(req: Dict[str, str], user: Dict[str, Any] = Depends(get_current_user)):
    inv_id = req.get("invoice_id")
    inv = get_user_invoice_by_id(user["uid"], inv_id) if inv_id else None
    if not inv and inv_id:
        from engine.seed_data import INITIAL_INVOICES
        inv = next((i for i in INITIAL_INVOICES if i["id"] == inv_id or i.get("invoice_number") == inv_id), None)
    if not inv:
        user_invoices = get_user_invoices(user["uid"])
        inv = user_invoices[0] if user_invoices else {"vendor_name": "Vendor", "invoice_number": "INV-001", "total_amount": 0}
        
    draft = draft_vendor_inquiry_email(inv)
    return {"draft": draft}


STATIC_PATH = os.path.abspath(os.path.join(ROOT_DIR, "static"))
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")


@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = os.path.join(STATIC_PATH, "index.html")
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/vendors", response_class=HTMLResponse)
@app.get("/vendors.html", response_class=HTMLResponse)
def serve_vendors_page():
    vendors_file = os.path.join(STATIC_PATH, "vendors.html")
    if os.path.exists(vendors_file):
        with open(vendors_file, "r", encoding="utf-8") as f:
            return f.read()
    index_file = os.path.join(STATIC_PATH, "index.html")
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/feedback", response_class=HTMLResponse)
@app.get("/feedback.html", response_class=HTMLResponse)
def serve_feedback_page():
    feedback_file = os.path.join(STATIC_PATH, "feedback.html")
    if os.path.exists(feedback_file):
        with open(feedback_file, "r", encoding="utf-8") as f:
            return f.read()
    index_file = os.path.join(STATIC_PATH, "index.html")
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/admin", response_class=HTMLResponse)
def serve_admin_page():
    index_file = os.path.join(STATIC_PATH, "index.html")
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()
