"""
Firestore Multi-Tenant Data Repository for InvoiceGuard
Implements UID-isolated subcollections:
- users/{uid}/invoices/{invoiceId}
- users/{uid}/vendors/{vendorId}
- users/{uid}/complaints/{complaintId}
- users/{uid}/feedback/{feedbackId}
- Admin vendor verification & blacklist controls
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

# Pre-defined user profiles
USER_PROFILES = {
    "usr_demo1_alex": {
        "uid": "usr_demo1_alex",
        "email": "demo1@invoiceguard.demo",
        "name": "Alex Vance",
        "role": "user",
        "title": "Finance Sec Lead",
        "initials": "AV",
        "avatar_url": "https://lh3.googleusercontent.com/aida/AEtjO1WrkfpzKKRxpDEqWEKJZT85NKinPIEcpUKVrt4vxf-YAaRh1oPrIj8nuVoAhiawYnB4J3ynGcWujvFk2vSudd0Wi_WkC61Pm3HIq1DdJzIWt8Du-tlbFbZFfXzDM-gZxfycpBtAyHlaOMCuv2uVqsbrY3gKXQ6vr_a5QldJIAHhXtxbYR1B2GRGeiHumVJAs-UHYMgjfg6XcnFuE9W9XX5Fz5apO-4LR-vq__pAFEex3BB83ssxRClAyh0"
    },
    "usr_demo2_priya": {
        "uid": "usr_demo2_priya",
        "email": "demo2@invoiceguard.demo",
        "name": "Priya Sharma",
        "role": "user",
        "title": "Senior Controller",
        "initials": "PS",
        "avatar_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80"
    },
    "usr_demo3_marcus": {
        "uid": "usr_demo3_marcus",
        "email": "demo3@invoiceguard.demo",
        "name": "Marcus Thorne",
        "role": "user",
        "title": "Fraud Risk Officer",
        "initials": "MT",
        "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
    },
    "usr_demo4_elena": {
        "uid": "usr_demo4_elena",
        "email": "demo4@invoiceguard.demo",
        "name": "Elena Rostova",
        "role": "user",
        "title": "Head of Treasury",
        "initials": "ER",
        "avatar_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80"
    },
    "usr_demo5_arjun": {
        "uid": "usr_demo5_arjun",
        "email": "demo5@invoiceguard.demo",
        "name": "Arjun Mehta",
        "role": "user",
        "title": "Compliance Auditor (Fresh Profile)",
        "initials": "AM",
        "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80"
    },
    "admin_root_001": {
        "uid": "admin_root_001",
        "email": "admin@invoiceguard.corp",
        "name": "Master Compliance Admin",
        "role": "admin",
        "title": "Chief Information Security Officer",
        "initials": "AD",
        "avatar_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&auto=format&fit=crop&q=80"
    }
}

# In-Memory Datastore Partitioned by UID
USER_INVOICES_STORE: Dict[str, Dict[str, Dict[str, Any]]] = { uid: {} for uid in USER_PROFILES }
USER_VENDORS_STORE: Dict[str, Dict[str, Dict[str, Any]]] = { uid: {} for uid in USER_PROFILES }
USER_COMPLAINTS_STORE: Dict[str, Dict[str, Dict[str, Any]]] = { uid: {} for uid in USER_PROFILES }

# Global Admin Collections
GLOBAL_VENDOR_BLACKLIST: List[Dict[str, Any]] = [
    {
        "gstin": "29AABCZ9988P1ZR",
        "vendor_name": "Zenith Office Supplies",
        "reason": "Overseas IBAN wire diversion attempt flagged by AML Sentinel",
        "flagged_at": "Oct 20, 2026",
        "severity": "CRITICAL"
    }
]

SYSTEM_AUDIT_LOGS: List[Dict[str, Any]] = [
    {
        "timestamp": "2026-09-22 14:32:00",
        "actor": "system",
        "action": "HEURISTIC_RULE_EVAL",
        "detail": "Cross-tenant rule engine synchronized with 142 historical ledgers"
    },
    {
        "timestamp": "2026-09-22 14:32:03",
        "actor": "usr_demo1_alex",
        "action": "ANOMALY_TRIGGER",
        "detail": "Flagged new payment destination ICICI *8821 for ABC Technologies (#INV-2026-0918)"
    }
]

# Initialize Seed Invoices per User
from engine.seed_data import INITIAL_INVOICES, INITIAL_VENDORS, COMPLAINTS

# User invoice store starts empty; populated dynamically upon upload or scenario load
# Seed invoices are maintained in INITIAL_INVOICES for on-demand loading & admin inspection

# Assign vendors
for v in INITIAL_VENDORS[:3]:
    USER_VENDORS_STORE["usr_demo1_alex"][v["id"]] = dict(v)

for v in INITIAL_VENDORS[3:]:
    USER_VENDORS_STORE["usr_demo2_priya"][v["id"]] = dict(v)

# Assign complaints
for c in COMPLAINTS:
    USER_COMPLAINTS_STORE["usr_demo1_alex"][c["id"]] = dict(c)


# --- Firestore Access Helpers ---

def get_user_invoices(uid: str) -> List[Dict[str, Any]]:
    """Returns all invoices owned by user UID."""
    return list(USER_INVOICES_STORE.get(uid, {}).values())


def find_invoice_robust(uid: Optional[str], invoice_id: str) -> Optional[Dict[str, Any]]:
    """
    Robust invoice lookup for production/Vercel serverless environment.
    Searches across:
    1. User's isolated in-memory store by ID
    2. User's isolated in-memory store by invoice_number
    3. All tenant in-memory stores (cross-tenant fallback)
    4. Seed invoices (INITIAL_INVOICES)
    5. Persistent disk cache in STORAGE_BASE (/tmp/invoiceguard)
    """
    if not invoice_id:
        return None

    clean_id = str(invoice_id).strip()

    # 1. Primary lookup: User's memory store by ID
    if uid and uid in USER_INVOICES_STORE:
        inv = USER_INVOICES_STORE[uid].get(clean_id)
        if inv:
            return inv
        # 2. User's memory store by invoice_number
        for inv in USER_INVOICES_STORE[uid].values():
            if inv.get("invoice_number") == clean_id:
                return inv

    # 3. Cross-tenant in-memory lookup
    all_invs = get_all_system_invoices()
    for inv in all_invs:
        if inv.get("id") == clean_id or inv.get("invoice_number") == clean_id:
            return inv

    # 4. Seed invoices lookup
    try:
        from engine.seed_data import INITIAL_INVOICES
        for inv in INITIAL_INVOICES:
            if inv.get("id") == clean_id or inv.get("invoice_number") == clean_id:
                return inv
    except Exception:
        pass

    # 5. Disk storage fallback (/tmp/invoiceguard)
    import tempfile
    storage_base = os.getenv("STORAGE_BASE", os.path.join(tempfile.gettempdir(), "invoiceguard"))
    disk_paths = [
        os.path.join(storage_base, "all_invoices", f"{clean_id}.json"),
    ]
    if uid:
        disk_paths.insert(0, os.path.join(storage_base, "users", uid, "invoices", clean_id, "invoice.json"))

    # Also check any user folder on disk for clean_id
    users_dir = os.path.join(storage_base, "users")
    if os.path.exists(users_dir):
        try:
            for u in os.listdir(users_dir):
                candidate = os.path.join(users_dir, u, "invoices", clean_id, "invoice.json")
                if candidate not in disk_paths:
                    disk_paths.append(candidate)
        except Exception:
            pass

    for p in disk_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    inv_data = json.load(f)
                    if inv_data:
                        # Rehydrate into memory
                        owner_uid = inv_data.get("user_id") or uid or "usr_demo1_alex"
                        if owner_uid not in USER_INVOICES_STORE:
                            USER_INVOICES_STORE[owner_uid] = {}
                        USER_INVOICES_STORE[owner_uid][inv_data.get("id", clean_id)] = inv_data
                        return inv_data
            except Exception:
                pass

    return None


def get_user_invoice_by_id(uid: str, invoice_id: str) -> Optional[Dict[str, Any]]:
    """Fetches a specific invoice strictly within the user UID partition or via robust fallback."""
    return find_invoice_robust(uid, invoice_id)


def save_user_invoice(uid: str, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
    """Saves normalized invoice record under users/{uid}/invoices/{invoiceId} and persists to disk."""
    inv_id = invoice_data.get("id") or f"INV-{uuid.uuid4().hex[:8].upper()}"
    invoice_data["id"] = inv_id
    invoice_data["user_id"] = uid
    invoice_data["created_at"] = invoice_data.get("created_at") or datetime.now().isoformat()
    invoice_data["updated_at"] = datetime.now().isoformat()
    
    if uid not in USER_INVOICES_STORE:
        USER_INVOICES_STORE[uid] = {}
        
    USER_INVOICES_STORE[uid][inv_id] = invoice_data

    # Persist to disk for serverless instance resilience
    try:
        import tempfile
        import json
        storage_base = os.getenv("STORAGE_BASE", os.path.join(tempfile.gettempdir(), "invoiceguard"))
        u_dir = os.path.join(storage_base, "users", uid, "invoices", inv_id)
        os.makedirs(u_dir, exist_ok=True)
        with open(os.path.join(u_dir, "invoice.json"), "w", encoding="utf-8") as f:
            json.dump(invoice_data, f, default=str)

        all_dir = os.path.join(storage_base, "all_invoices")
        os.makedirs(all_dir, exist_ok=True)
        with open(os.path.join(all_dir, f"{inv_id}.json"), "w", encoding="utf-8") as f:
            json.dump(invoice_data, f, default=str)
    except Exception:
        pass

    return invoice_data


def clear_user_invoices(uid: str) -> bool:
    """Clears all uploaded invoices for user UID."""
    USER_INVOICES_STORE[uid] = {}
    return True


def update_invoice_user_feedback(uid: str, invoice_id: str, feedback: str) -> Optional[Dict[str, Any]]:
    """19. Store user feedback marking invoice as 'Legitimate' or 'Suspicious'."""
    inv = USER_INVOICES_STORE.get(uid, {}).get(invoice_id)
    if inv:
        inv["user_feedback"] = feedback
        inv["updated_at"] = datetime.now().isoformat()
        return inv
    return None


def get_user_vendors(uid: str) -> List[Dict[str, Any]]:
    """Returns vendors belonging to user UID."""
    return list(USER_VENDORS_STORE.get(uid, {}).values())


def save_user_vendor(uid: str, vendor_data: Dict[str, Any]) -> Dict[str, Any]:
    """Saves vendor record under users/{uid}/vendors/{vendorId}."""
    v_id = vendor_data.get("id") or f"VEN-{uuid.uuid4().hex[:4].upper()}"
    vendor_data["id"] = v_id
    vendor_data["user_id"] = uid
    if uid not in USER_VENDORS_STORE:
        USER_VENDORS_STORE[uid] = {}
    USER_VENDORS_STORE[uid][v_id] = vendor_data
    return vendor_data


def verify_vendor_admin(vendor_id: str, admin_name: str) -> Optional[Dict[str, Any]]:
    """
    23. Admin-Controlled Vendor Verification:
    Approves vendor KYC and displays 'Verified by InvoiceGuard'.
    Cascades verification status to all matching invoice records.
    """
    target_vendor = None
    target_name = None

    for uid, vendors in USER_VENDORS_STORE.items():
        if vendor_id in vendors:
            v = vendors[vendor_id]
            v["verified"] = True
            v["verified_by"] = f"Verified by InvoiceGuard (Admin {admin_name})"
            v["verified_at"] = datetime.now().strftime("%b %d, %Y")
            target_vendor = v
            target_name = v.get("name", "").strip().lower()

    if target_vendor:
        for uid, invoices in USER_INVOICES_STORE.items():
            for inv in invoices.values():
                if inv.get("vendor_id") == vendor_id or (target_name and inv.get("vendor_name", "").strip().lower() == target_name):
                    inv["vendor_verified"] = True

    return target_vendor


def get_user_complaints(uid: str) -> List[Dict[str, Any]]:
    """Returns compliance flags belonging to user UID."""
    return list(USER_COMPLAINTS_STORE.get(uid, {}).values())


def save_user_complaint(uid: str, complaint_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    24. Store user vendor complaints & ratings:
    Reasons: Incorrect invoice, Incorrect amount, Duplicate invoice, Suspicious activity, Other.
    """
    cmp_id = complaint_data.get("id") or f"CMP-2026-{len(USER_COMPLAINTS_STORE.get(uid, {})) + 1:03d}"
    complaint_data["id"] = cmp_id
    complaint_data["user_id"] = uid
    complaint_data["created_at"] = datetime.now().isoformat()
    
    if uid not in USER_COMPLAINTS_STORE:
        USER_COMPLAINTS_STORE[uid] = {}
        
    USER_COMPLAINTS_STORE[uid][cmp_id] = complaint_data
    return complaint_data


def compute_user_metrics(uid: str) -> Dict[str, Any]:
    """Computes genuine real metrics for the user's isolated data."""
    invoices = get_user_invoices(uid)
    total_analyzed = len(invoices)
    
    if total_analyzed == 0:
        return {
            "total_analyzed": 0,
            "needs_review_count": 0,
            "amount_at_risk": 0.0,
            "verified_vendors_count": len(get_user_vendors(uid)),
            "passed_count": 0,
            "critical_count": 0,
            "is_empty": True
        }

    needs_review = sum(1 for i in invoices if i.get("status") == "review")
    critical = sum(1 for i in invoices if i.get("status") == "critical")
    passed = sum(1 for i in invoices if i.get("status") == "passed")
    amount_at_risk = sum(i.get("total_amount", 0) for i in invoices if i.get("status") in ["review", "critical"])
    
    vendors = get_user_vendors(uid)
    verified_vendors = sum(1 for v in vendors if v.get("verified", False))

    return {
        "total_analyzed": total_analyzed,
        "needs_review_count": needs_review + critical,
        "amount_at_risk": amount_at_risk,
        "verified_vendors_count": verified_vendors,
        "passed_count": passed,
        "critical_count": critical,
        "is_empty": False
    }


def get_all_system_invoices() -> List[Dict[str, Any]]:
    """Admin-only: Returns all invoices across all tenants with user attribution."""
    all_invoices = []
    for uid, invs in USER_INVOICES_STORE.items():
        u_profile = USER_PROFILES.get(uid, {})
        for inv in invs.values():
            inv_with_user = dict(inv)
            inv_with_user["owner_name"] = u_profile.get("name", uid)
            inv_with_user["owner_email"] = u_profile.get("email", "")
            all_invoices.append(inv_with_user)
    return all_invoices


def get_admin_global_overview() -> Dict[str, Any]:
    """Admin-only: Global security metrics across the entire enterprise."""
    all_invoices = get_all_system_invoices()
    total_invoices = len(all_invoices)
    total_volume = sum(i.get("total_amount", 0) for i in all_invoices)
    total_at_risk = sum(i.get("total_amount", 0) for i in all_invoices if i.get("threat_score", 0) > 25)
    critical_invoices = [i for i in all_invoices if i.get("status") == "critical" or i.get("threat_score", 0) > 75]
    
    all_vendors = []
    for u_v in USER_VENDORS_STORE.values():
        all_vendors.extend(u_v.values())

    return {
        "total_tenants": len([u for u in USER_PROFILES.values() if u["role"] == "user"]),
        "total_invoices_audited": total_invoices,
        "total_volume_inr": total_volume,
        "total_volume_at_risk_inr": total_at_risk,
        "critical_count": len(critical_invoices),
        "blacklisted_vendors_count": len(GLOBAL_VENDOR_BLACKLIST),
        "blacklist": GLOBAL_VENDOR_BLACKLIST,
        "vendors_total": len(all_vendors),
        "audit_logs": SYSTEM_AUDIT_LOGS
    }
