from src.moss_validator import runtime_guard


def guarded_tool_call(action, doc_hash):
    """Evaluate an agent tool request before allowing the tool to execute."""
    guard_result = runtime_guard(doc_hash, action)
    executed = guard_result["decision"] == "ALLOW"
    return {
        "tool": action,
        "executed": executed,
        "decision": guard_result["decision"],
        "reason": guard_result["reason"],
        "guard": guard_result,
    }
