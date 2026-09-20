from fastapi import FastAPI

from src.agent import guarded_tool_call
from src.api_models import GuardResponse, HealthResponse, ToolRequest
from src.blockchain import add_to_ledger
from src.honeypot import honeypot_trap
from src.retrieval_models import RetrievalResult


app = FastAPI(
    title="AgentGuard Gateway",
    description="Runtime safety gateway for transaction-oriented AI agents.",
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "ok",
        "service": "agentguard-gateway",
        "version": app.version,
    }


@app.post("/v1/guard/tool-request", response_model=GuardResponse)
def guard_tool_request(request: ToolRequest):
    agent_request = guarded_tool_call(request.action, request.doc_hash)
    guard_result = agent_request["guard"]
    retrieval = RetrievalResult.model_validate(
        {
            field: guard_result[field]
            for field in RetrievalResult.model_fields
        }
    )
    honeypot = honeypot_trap(request.doc_hash, not guard_result["allow"])
    audit = add_to_ledger(request.doc_hash, guard_result, request.action)

    return {
        "decision": agent_request["decision"],
        "executed": agent_request["executed"],
        "reason": agent_request["reason"],
        "guard": guard_result,
        "retrieval": retrieval,
        "review_request": agent_request["review_request"],
        "honeypot": honeypot,
        "audit": audit,
    }
