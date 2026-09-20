import hashlib
import time

REVIEW_QUEUE = []


def create_review_request(action, doc_hash, guard_result):
    review_id = hashlib.sha256(
        f"{action}:{doc_hash}:{time.time_ns()}".encode()
    ).hexdigest()[:12].upper()
    request = {
        "review_id": f"REVIEW-{review_id}",
        "action": action,
        "doc_hash": doc_hash,
        "decision": guard_result["decision"],
        "reason": guard_result["reason"],
        "reason_code": guard_result.get("reason_code"),
        "policy_version": guard_result.get("policy_version"),
        "trust": guard_result["trust"],
        "status": "PENDING",
    }
    REVIEW_QUEUE.append(request)
    return request


def get_review_queue():
    return REVIEW_QUEUE


def get_review_request(review_id):
    return next((request for request in REVIEW_QUEUE if request["review_id"] == review_id), None)


def resolve_review(review_id, status):
    request = get_review_request(review_id)
    if request is None or request["status"] != "PENDING":
        return None
    request["status"] = status
    return request
