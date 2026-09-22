"""Context Retrieval Layer (Layer 2 in Architecture Diagram).

Provides semantic context retrieval via Moss and local SQLite/demo fallback.
"""

from src.retrieval.local_retrieval import local_demo_search, moss_error_result
from src.retrieval.moss_client import (
    MossIntegrationError,
    MossNotConfigured,
    initialize_moss_index,
    moss_configuration,
    search_moss,
)
from src.retrieval.retrieval_models import RetrievalResult
from src.retrieval.retrieval_service import retrieve_context

__all__ = [
    "MossIntegrationError",
    "MossNotConfigured",
    "initialize_moss_index",
    "moss_configuration",
    "RetrievalResult",
    "local_demo_search",
    "moss_error_result",
    "retrieve_context",
    "search_moss",
]
