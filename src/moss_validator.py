from src.retrieval_service import retrieve_context
from src.policy_engine import evaluate_policy

def runtime_guard(doc_hash, action):
    context = retrieve_context(doc_hash)
    return evaluate_policy(action, context).as_legacy_result()