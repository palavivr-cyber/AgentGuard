import time

from src.policy.context_normalizer import normalize_context
from src.retrieval.local_retrieval import local_demo_search, moss_error_result
from src.retrieval.moss_client import MossIntegrationError, MossNotConfigured, search_moss
from src.retrieval.retrieval_models import RetrievalResult


def retrieve_context(doc_hash):
    """Retrieve and normalize context before policy evaluation."""
    start = time.perf_counter_ns()
    try:
        context = search_moss(doc_hash)
    except MossNotConfigured:
        context = local_demo_search(doc_hash)
    except MossIntegrationError:
        latency = round((time.perf_counter_ns() - start) / 1_000_000, 4)
        context = moss_error_result(latency)
    except Exception:
        latency = round((time.perf_counter_ns() - start) / 1_000_000, 4)
        context = moss_error_result(latency)

    return RetrievalResult.model_validate(normalize_context(context))
