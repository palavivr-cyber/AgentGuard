from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from src.retrieval_models import RetrievalResult


SupportedAction = Literal[
    "payment",
    "read_email",
    "delete_file",
    "send_contract",
    "approve_po",
]


class ToolRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: SupportedAction
    doc_hash: str = Field(min_length=1, max_length=256)


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str


class GuardResponse(BaseModel):
    decision: Literal["ALLOW", "BLOCK", "REVIEW"]
    executed: bool
    reason: str
    guard: dict[str, Any]
    retrieval: RetrievalResult
    review_request: dict[str, Any] | None = None
    honeypot: dict[str, Any]
    audit: dict[str, Any]
