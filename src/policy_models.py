from typing import Literal

from pydantic import BaseModel, ConfigDict

from src.retrieval_models import RetrievalResult


PolicyDecisionName = Literal["ALLOW", "BLOCK", "REVIEW"]


class PolicyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str
    context: RetrievalResult


class PolicyDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: PolicyDecisionName
    allow: bool
    action: str
    alert: str
    reason: str
    reason_code: str
    color: str
    policy_name: str
    policy_version: str
    retrieval: RetrievalResult

    def as_legacy_result(self) -> dict:
        return {
            **self.retrieval.model_dump(),
            "allow": self.allow,
            "decision": self.decision,
            "action": self.action,
            "alert": self.alert,
            "reason": self.reason,
            "reason_code": self.reason_code,
            "color": self.color,
            "policy_name": self.policy_name,
            "policy_version": self.policy_version,
        }