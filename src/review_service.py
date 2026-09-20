from src.review import create_review_request, get_review_request, get_review_queue, resolve_review


def create_pending_review(action, doc_hash, guard_result):
    return create_review_request(action, doc_hash, guard_result)


def list_reviews():
    return get_review_queue()


def get_review(review_id):
    return get_review_request(review_id)


def decide_review(review_id, decision):
    return resolve_review(review_id, decision)