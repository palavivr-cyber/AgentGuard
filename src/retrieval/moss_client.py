import asyncio
import os
import time
from functools import lru_cache

try:
    import streamlit as st
except ModuleNotFoundError:
    st = None

try:
    from moss import MossClient, QueryOptions
except ModuleNotFoundError:
    MossClient = None
    QueryOptions = None


class MossNotConfigured(Exception):
    pass


class MossIntegrationError(Exception):
    pass


INDEX_NAME = os.getenv("MOSS_INDEX_NAME", "agentguard-context")
_client = None
_loaded_client_settings = None
_moss_failure = False


def _get_setting(name):
    value = os.getenv(name)
    if value:
        return value
    if st is not None:
        try:
            return st.secrets[name]
        except (KeyError, FileNotFoundError):
            pass
    raise MossNotConfigured from None


def _get_credentials():
    if MossClient is None or QueryOptions is None:
        raise MossNotConfigured
    # Credentials alone never enable cloud retrieval. This prevents surprise
    # usage while developing locally or running the deterministic evaluation.
    try:
        moss_enabled = _get_setting("MOSS_ENABLED")
        if str(moss_enabled).lower() not in {"1", "true", "yes"}:
            raise MossNotConfigured
    except MossNotConfigured:
        raise MossNotConfigured from None
    
    return _get_setting("MOSS_PROJECT_ID"), _get_setting("MOSS_PROJECT_KEY")


async def _query_index(project_id, project_key, query, index_name):
    global _client, _loaded_client_settings
    settings = (project_id, project_key, index_name)
    if _client is None or _loaded_client_settings != settings:
        _client = MossClient(project_id, project_key)
        _loaded_client_settings = None
    if _loaded_client_settings != settings:
        # load_index downloads the full corpus locally for session caching.
        # The Moss cloud occasionally returns a response body that the current
        # SDK cannot deserialise (encoding mismatch). We attempt load_index
        # for the cache benefit but tolerate the failure: the cloud query
        # endpoint works independently and does not require a prior load.
        try:
            await _client.load_index(index_name)
            _loaded_client_settings = settings
        except Exception:
            # Mark as loaded anyway so we don't retry on every call.
            _loaded_client_settings = settings
    return await _client.query(index_name, query, QueryOptions(top_k=1))


def search_moss(doc_hash):
    global _moss_failure
    project_id, project_key = _get_credentials()
    if _moss_failure:
        raise MossIntegrationError("Moss retrieval is disabled after an earlier failure; restart after fixing the index.")
    try:
        return _search_moss_cached(doc_hash, project_id, project_key, INDEX_NAME)
    except MossIntegrationError:
        # Do not repeatedly call a broken or unavailable cloud index in a
        # batch evaluation. A restart is an explicit retry after remediation.
        _moss_failure = True
        raise


@lru_cache(maxsize=256)
def _search_moss_cached(doc_hash, project_id, project_key, index_name):
    """Cache immutable document-hash retrieval only after Moss is explicitly enabled."""
    start = time.perf_counter_ns()

    try:
        results = asyncio.run(_query_index(project_id, project_key, doc_hash, index_name))
    except Exception as error:
        raise MossIntegrationError from error

    latency = round((time.perf_counter_ns() - start) / 1_000_000, 4)
    if not results.docs:
        return {
            "found": False,
            "trust": 0.0,
            "latency": latency,
            "doc": "NO MOSS MATCH",
            "status": "UNTRUSTED",
            "vendor": "UNKNOWN",
            "retrieval_mode": "MOSS",
        }

    match = results.docs[0]
    metadata = match.metadata or {}
    try:
        trust = float(metadata.get("trust", match.score))
    except (TypeError, ValueError):
        trust = float(match.score)

    return {
        "found": True,
        "trust": trust,
        "latency": latency,
        "doc": match.text,
        "status": str(metadata.get("status", "MATCHED")),
        "vendor": str(metadata.get("vendor", "UNKNOWN")),
        "retrieval_mode": "MOSS",
    }
