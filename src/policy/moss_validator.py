from src.audit_security.security_analysis import analyze_request, security_block_result
from src.policy.policy_engine import evaluate_policy


def runtime_guard(doc_hash, action, context_text=None, transaction=None):
    from src.retrieval.retrieval_service import retrieve_context

    context = retrieve_context(doc_hash)
    result = evaluate_policy(action, context).as_legacy_result()
    findings = analyze_request(context_text, transaction)
    if findings:
        return security_block_result(result, findings)
    return {**result, "security_findings": []}
