import hashlib

def honeypot_trap(doc_hash, is_blocked):
    if is_blocked and ("hacker" in doc_hash or "tamper" in doc_hash or "stale" in doc_hash or "fake" in doc_hash):
        trace_id = hashlib.sha256(doc_hash.encode()).hexdigest()[:8].upper()
        return {
            "activated": True,
            "trace_id": f"TRACE-{trace_id}",
            "fake_account": "XXXX-XXXX-1234 (Fake Honeypot Account)",
            "attacker_ip": "192.168.1.105 [LOGGED]",
            "message": f"Attacker deceived with fake data. Trace ID {trace_id} logged."
        }
    return {"activated": False}