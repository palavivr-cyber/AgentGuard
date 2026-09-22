import uuid

from src.execution_review.execution_service import execute_tool
from src.execution_review.review_service import create_pending_review
from src.policy.moss_validator import runtime_guard


def guarded_tool_call(action, doc_hash, context_text=None, transaction=None):
    """Evaluate an agent tool request before allowing the tool to execute."""
    request_id = f"REQ-{uuid.uuid4().hex[:12].upper()}"
    guard_result = runtime_guard(doc_hash, action, context_text, transaction)
    execution = execute_tool(action, request_id, guard_result)
    review_request = None
    if guard_result["decision"] == "REVIEW":
        review_request = create_pending_review(action, doc_hash, guard_result)
    return {
        "request_id": request_id,
        "tool": action,
        "executed": execution.executed,
        "execution": execution.model_dump(),
        "decision": guard_result["decision"],
        "reason": guard_result["reason"],
        "review_request": review_request,
        "guard": guard_result,
    }
