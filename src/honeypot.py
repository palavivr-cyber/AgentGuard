from src.security_service import security_trace

def honeypot_trap(doc_hash, is_blocked):
    return security_trace(doc_hash, is_blocked)