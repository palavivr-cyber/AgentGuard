from src.retrieval_service import retrieve_context

def runtime_guard(doc_hash, action):
    moss = retrieve_context(doc_hash).model_dump()
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