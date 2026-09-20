import asyncio
import os
import time

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


INDEX_NAME = "agentguard-context"


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
    return _get_setting("MOSS_PROJECT_ID"), _get_setting("MOSS_PROJECT_KEY")


async def _query_index(project_id, project_key, query):
    client = MossClient(project_id, project_key)
    await client.load_index(INDEX_NAME)
    return await client.query(INDEX_NAME, query, QueryOptions(top_k=1))


def search_moss(doc_hash):
    project_id, project_key = _get_credentials()
    start = time.perf_counter_ns()

    try:
        results = asyncio.run(_query_index(project_id, project_key, doc_hash))
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