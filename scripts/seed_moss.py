"""Create the AgentGuard Moss index from the committed demo corpus.

Requires MOSS_PROJECT_ID and MOSS_PROJECT_KEY. This is an explicit operator
step because it creates cloud state; it never runs during application startup.
"""

from __future__ import annotations

import asyncio
import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from moss import DocumentInfo, MossClient

CORPUS_PATH = PROJECT_ROOT / "agentguard-context.json"


async def main() -> None:
    parser = argparse.ArgumentParser(description="Create an AgentGuard Moss index.")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Explicitly download and load the index after creation (uses additional cloud work).",
    )
    args = parser.parse_args()
    project_id = os.getenv("MOSS_PROJECT_ID")
    project_key = os.getenv("MOSS_PROJECT_KEY")
    if not project_id or not project_key:
        raise SystemExit("Set MOSS_PROJECT_ID and MOSS_PROJECT_KEY before seeding Moss.")

    index_name = os.getenv("MOSS_INDEX_NAME", "agentguard-context")
    records = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    docs = [
        DocumentInfo(
            id=record["id"],
            text=record["text"],
            metadata={key: str(value) for key, value in record.get("metadata", {}).items()},
        )
        for record in records
    ]
    client = MossClient(project_id, project_key)
    try:
        await client.create_index(index_name, docs, "moss-minilm")
        print(f"Created {index_name!r} with {len(docs)} documents.")
    except Exception as error:
        # An existing index is safe to use. Do not delete or overwrite cloud
        # data implicitly; create a new name instead when a fresh corpus is needed.
        if "INDEX_EXISTS" not in str(error):
            raise
        print(f"Index {index_name!r} already exists; leaving it unchanged.")
    if args.verify:
        await client.load_index(index_name)
        print(f"Loaded {index_name!r} successfully.")
    else:
        print("Skipped index download verification. Use --verify only when needed.")


if __name__ == "__main__":
    asyncio.run(main())
