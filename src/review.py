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
        "trust": guard_result["trust"],
        "status": "PENDING",
    }
    REVIEW_QUEUE.append(request)
    return request


def get_review_queue():
    return REVIEW_QUEUE
