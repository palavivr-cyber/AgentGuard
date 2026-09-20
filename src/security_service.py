import hashlib


SUSPICIOUS_MARKERS = ("hacker", "tamper", "stale", "fake")


def security_trace(doc_hash, is_blocked):
    if not is_blocked or not any(marker in doc_hash.lower() for marker in SUSPICIOUS_MARKERS):
        return {"activated": False}

    trace_id = hashlib.sha256(doc_hash.encode()).hexdigest()[:8].upper()
    return {
        "activated": True,
        "trace_id": f"TRACE-{trace_id}",
        "trigger": "SUSPICIOUS_BLOCKED_REQUEST",
        "telemetry_mode": "DEMO",
        "message": f"Suspicious request trace {trace_id} recorded.",
    }