"""AgentGuard: Runtime safety gateway for transaction-oriented AI agents.

Structured into 5 architectural layers matching architecture.pdf:
1. Gateway Layer (src.gateway)
2. Context Retrieval Layer (src.retrieval)
3. Policy Evaluation Layer (src.policy)
4. Execution & Review Layer (src.execution_review)
5. Audit & Security Layer (src.audit_security)
"""

from src import audit_security, execution_review, gateway, policy, retrieval
from src.agent import guarded_tool_call
from src.audit_security import (
    get_audit_events,
    honeypot_trap,
    record_audit_event,
    verify_audit_chain,
)
from src.execution_review import (
    create_pending_review,
    decide_review,
    execute_tool,
    get_review,
    list_reviews,
)
from src.gateway import GuardResponse, HealthResponse, ToolRequest
from src.policy import (
    EVALUATION_CASES,
    evaluate_batch,
    evaluate_policy,
    runtime_guard,
)
from src.retrieval import (
    local_demo_search,
    retrieve_context,
    search_moss,
)

__all__ = [
    # Architectural Layers
    "gateway",
    "retrieval",
    "policy",
    "execution_review",
    "audit_security",
    # Primary API & Agent entrypoints
    "guarded_tool_call",
    "runtime_guard",
    "evaluate_policy",
    "evaluate_batch",
    "retrieve_context",
    "search_moss",
    "local_demo_search",
    "execute_tool",
    "create_pending_review",
    "list_reviews",
    "get_review",
    "decide_review",
    "record_audit_event",
    "get_audit_events",
    "verify_audit_chain",
    "honeypot_trap",
    "ToolRequest",
    "GuardResponse",
    "HealthResponse",
    "EVALUATION_CASES",
]
