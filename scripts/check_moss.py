"""Verify that AgentGuard can load and query its configured Moss index.

This command never creates, updates, or deletes cloud data.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.retrieval.moss_client import MossIntegrationError, MossNotConfigured, moss_configuration, search_moss


def main() -> int:
    config = moss_configuration()
    if not config["configured"]:
        print(
            "Moss is not configured. Add MOSS_PROJECT_ID and MOSS_PROJECT_KEY "
            "to .streamlit/secrets.toml (see .streamlit/secrets.toml.example)."
        )
        return 2

    try:
        result = search_moss("a1b2c3d4e5f6g7h8")
    except MossIntegrationError as error:
        print(f"Moss connectivity failed for index {config['index_name']!r}: {error.__cause__ or error}")
        return 1
    except MossNotConfigured:
        print("Moss configuration became unavailable.")
        return 2

    if not result["found"]:
        print(
            f"Moss connected to {config['index_name']!r}, but the AgentGuard corpus is missing. "
            "Run scripts/seed_moss.py with the same index name."
        )
        return 1

    print(
        f"Moss connected: index={config['index_name']!r}, mode={result['retrieval_mode']}, "
        f"latency={result['latency']} ms, status={result['status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
