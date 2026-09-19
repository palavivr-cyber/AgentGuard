import time

TRUSTED_DB = {
    "a1b2c3d4e5f6g7h8": {"name": "Invoice INV100 - HAL Vendor ABC - $5000", "trust": 0.95, "vendor": "HAL"},
    "b2c3d4e5f6g7h8i9": {"name": "PO #PO2024 - Verified Supplier", "trust": 0.93, "vendor": "SafeCorp"},
}

def moss_fast_search(doc_hash):
    start = time.time()
    time.sleep(0.007) # Moss <10ms
    data = TRUSTED_DB.get(doc_hash)
    latency = round((time.time() - start)*1000, 2)
    if data:
        return {"found": True, "trust": data["trust"], "latency": latency, "doc": data["name"], "status": "VERIFIED", "vendor": data["vendor"]}
    return {"found": False, "trust": 0.12, "latency": latency, "doc": "UNKNOWN / TAMPERED", "status": "UNTRUSTED", "vendor": "UNKNOWN"}

def runtime_guard(doc_hash, action):
    moss = moss_fast_search(doc_hash)
    if moss["trust"] < 0.7:
        return {**moss, "allow": False, "action": "🚫 BLOCKED", "alert": "🚨 REAL-TIME GUARDRAIL TRIGGERED", "color": "red"}
    if action == "payment" and moss["trust"] < 0.9:
        return {**moss, "allow": False, "action": "🚫 BLOCKED", "alert": "⚠️ HIGH-RISK NEEDS 0.9+ TRUST", "color": "orange"}
    return {**moss, "allow": True, "action": "✅ ALLOWED", "alert": "✅ SAFE - TRUSTED CONTEXT", "color": "green"}