from src.audit_security.security_service import security_trace
import os
import json
from src.audit_security.otel_formatter import to_otel_format

def honeypot_trap(doc_hash, is_blocked, security_findings=None):
    result = security_trace(doc_hash, is_blocked, security_findings)

    try:
        honeypot_event = {
            "attack_type": "Data Exfiltration Attempt",
            "severity": "critical" if is_blocked else "low",
            "payload": f"Accessing document hash: {doc_hash}",
            "is_blocked": is_blocked
        }
        otel_data = to_otel_format(honeypot_event)
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "honeypot_otel_traces.jsonl")
        with open(os.path.abspath(log_path), "a") as f:
            f.write(json.dumps(otel_data) + "\n")
    except Exception:
        pass

    return result
