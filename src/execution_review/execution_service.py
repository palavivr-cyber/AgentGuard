from src.execution_review.execution_models import ExecutionResult


def execute_tool(action, request_id, policy_decision):
    """Execute the prototype tool boundary only after an ALLOW decision."""
    decision = policy_decision["decision"]
    if decision != "ALLOW":
        return ExecutionResult(
            request_id=request_id,
            action=action,
            decision=decision,
            executed=False,
            status="PREVENTED",
            result=f"Tool execution prevented by {decision} policy decision.",
        )

    return ExecutionResult(
        request_id=request_id,
        action=action,
        decision="ALLOW",
        executed=True,
        status="EXECUTED",
        result=f"Prototype execution completed for {action}.",
    )
