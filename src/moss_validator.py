import time

TRUSTED_DB = {
    "a1b2c3d4e5f6g7h8": {"name": "Invoice INV100 - HAL Vendor ABC - $5000", "trust": 0.95, "vendor": "HAL"},
    "b2c3d4e5f6g7h8i9": {"name": "PO #PO2024 - Verified Supplier", "trust": 0.93, "vendor": "SafeCorp"},
    "d4e5f6g7h8i9j0k1": {"name": "Invoice INV104 - New Vendor - $1200", "trust": 0.82, "vendor": "NewVendor"},
}

def moss_fast_search(doc_hash):
    start = time.perf_counter_ns()
    data = TRUSTED_DB.get(doc_hash)
    latency = round((time.perf_counter_ns() - start) / 1_000_000, 4)
    if data:
        return {
            "found": True,
            "trust": data["trust"],
            "latency": latency,
            "doc": data["name"],
            "status": "VERIFIED",
            "vendor": data["vendor"],
            "retrieval_mode": "LOCAL_DEMO",
        }
    return {
        "found": False,
        "trust": 0.12,
        "latency": latency,
        "doc": "UNKNOWN / TAMPERED",
        "status": "UNTRUSTED",
        "vendor": "UNKNOWN",
        "retrieval_mode": "LOCAL_DEMO",
    }

def runtime_guard(doc_hash, action):
    moss = moss_fast_search(doc_hash)
    if moss["trust"] < 0.7:
        return {
            **moss,
            "allow": False,
            "decision": "BLOCK",
            "action": "🚫 BLOCKED",
            "alert": "🚨 REAL-TIME GUARDRAIL TRIGGERED",
            "reason": "Retrieved context is below the minimum trust threshold.",
            "color": "red",
        }
    if action == "payment" and moss["trust"] < 0.9:
        return {
            **moss,
            "allow": False,
            "decision": "BLOCK",
            "action": "🚫 BLOCKED",
            "alert": "⚠️ HIGH-RISK NEEDS 0.9+ TRUST",
            "reason": "Payment actions require at least 0.90 trust.",
            "color": "orange",
        }
    if moss["trust"] < 0.85:
        return {
            **moss,
            "allow": False,
            "decision": "REVIEW",
            "action": "🟡 REVIEW",
            "alert": "🟡 HUMAN REVIEW REQUIRED",
            "reason": "Context is plausible but not strong enough for autonomous execution.",
            "color": "yellow",
        }
    return {
        **moss,
        "allow": True,
        "decision": "ALLOW",
        "action": "✅ ALLOWED",
        "alert": "✅ SAFE - TRUSTED CONTEXT",
        "reason": "Retrieved context satisfies the action policy.",
        "color": "green",
    }