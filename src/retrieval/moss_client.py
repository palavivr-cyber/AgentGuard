import asyncio
import json
import os
import time
from functools import lru_cache
from pathlib import Path

try:
    import streamlit as st
except ModuleNotFoundError:
    st = None

try:
    from moss import DocumentInfo, MossClient, QueryOptions
except ModuleNotFoundError:
    DocumentInfo = None
    MossClient = None
    QueryOptions = None


class MossNotConfigured(Exception):
    pass


class MossIntegrationError(Exception):
    pass


_client = None
_loaded_client_settings = None
_moss_failure = False
_moss_failure_reason = None


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
    # A configured project is the normal production signal that Moss should be
    # used. Requiring a second opt-in made deployments with valid secrets
    # silently use the SQLite demo provider instead.
    try:
        moss_enabled = _get_setting("MOSS_ENABLED")
    except MossNotConfigured:
        moss_enabled = None
    if moss_enabled is not None and str(moss_enabled).lower() in {"0", "false", "no", "off"}:
        raise MossNotConfigured
    
    return _get_setting("MOSS_PROJECT_ID"), _get_setting("MOSS_PROJECT_KEY")


def _get_index_name():
    try:
        return _get_setting("MOSS_INDEX_NAME")
    except MossNotConfigured:
        return "agentguard-context"


async def _query_index(project_id, project_key, query, index_name):
    global _client, _loaded_client_settings
    settings = (project_id, project_key, index_name)
    if _client is None or _loaded_client_settings != settings:
        _client = MossClient(project_id, project_key)
        _loaded_client_settings = None
    if _loaded_client_settings != settings:
        # The low-latency path runs against this locally loaded Moss index.
        # A load failure must fail closed, never be shown as a Moss success.
        await _client.load_index(index_name)
        _loaded_client_settings = settings
    return await _client.query(index_name, query, QueryOptions(top_k=1))


def search_moss(doc_hash):
    global _moss_failure, _moss_failure_reason
    project_id, project_key = _get_credentials()
    if _moss_failure:
        raise MossIntegrationError("Moss retrieval is disabled after an earlier failure; restart after fixing the index.")
    try:
        return _search_moss_cached(doc_hash, project_id, project_key, _get_index_name())
    except MossIntegrationError as error:
        # Do not repeatedly call a broken or unavailable cloud index in a
        # batch evaluation. A restart is an explicit retry after remediation.
        _moss_failure = True
        cause = error.__cause__ or error
        _moss_failure_reason = f"{type(cause).__name__}: {str(cause)[:300]}"
        raise


@lru_cache(maxsize=256)
def _search_moss_cached(doc_hash, project_id, project_key, index_name):
    """Cache immutable document-hash retrieval after Moss is configured."""
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


def moss_configuration():
    """Return non-secret Moss configuration for health checks and the UI."""
    try:
        project_id, _ = _get_credentials()
        configuration = {
            "configured": True,
            "index_name": _get_index_name(),
            "project_id_suffix": project_id[-4:] if len(project_id) >= 4 else "configured",
        }
        if _moss_failure_reason:
            configuration["error"] = _moss_failure_reason
        return configuration
    except MossNotConfigured:
        return {"configured": False, "index_name": _get_index_name()}


async def _create_agentguard_index(project_id, project_key, index_name):
    corpus_path = Path(__file__).resolve().parents[2] / "agentguard-context.json"
    records = json.loads(corpus_path.read_text(encoding="utf-8"))
    documents = [
        DocumentInfo(
            id=record["id"],
            text=record["text"],
            metadata={key: str(value) for key, value in record.get("metadata", {}).items()},
        )
        for record in records
    ]
    client = MossClient(project_id, project_key)
    await client.create_index(index_name, documents, "moss-minilm")
    return len(documents)


def initialize_moss_index():
    """Create the configured AgentGuard index once, without overwriting data.

    Operators must select this explicitly from the Streamlit repair control.
    Use a new MOSS_INDEX_NAME when repairing a corrupt cloud artifact; an
    existing index is never updated, deleted, or replaced.
    """
    if DocumentInfo is None:
        raise MossIntegrationError("The Moss SDK is not installed.")

    project_id, project_key = _get_credentials()
    index_name = _get_index_name()
    try:
        document_count = asyncio.run(_create_agentguard_index(project_id, project_key, index_name))
    except Exception as error:
        if "INDEX_EXISTS" in str(error):
            raise MossIntegrationError(
                f"Index {index_name!r} already exists. Choose a new MOSS_INDEX_NAME to repair it."
            ) from error
        raise MossIntegrationError from error

    reset_moss_session()
    return {"index_name": index_name, "document_count": document_count}


def reset_moss_session():
    """Clear process-local Moss state after an operator changes cloud state."""
    global _client, _loaded_client_settings, _moss_failure, _moss_failure_reason
    _client = None
    _loaded_client_settings = None
    _moss_failure = False
    _moss_failure_reason = None
    _search_moss_cached.cache_clear()
