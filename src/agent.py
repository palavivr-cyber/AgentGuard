from src.moss_validator import runtime_guard
from src.review import create_review_request


def guarded_tool_call(action, doc_hash):
    """Evaluate an agent tool request before allowing the tool to execute."""
    guard_result = runtime_guard(doc_hash, action)
    executed = guard_result["decision"] == "ALLOW"
    review_request = None
    if guard_result["decision"] == "REVIEW":
        review_request = create_review_request(action, doc_hash, guard_result)
    return {
        "tool": action,
        "executed": executed,
        "decision": guard_result["decision"],
        "reason": guard_result["reason"],
        "review_request": review_request,
        "guard": guard_result,
    }
