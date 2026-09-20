# 🛡️ AgentGuard

AgentGuard is a runtime safety gateway for transaction-oriented AI agents. It validates context before an agent can act, returns an explainable allow or block decision, and records audit evidence.

## What this project does

- Validates document trust through a retrieval adapter with an explicit local demo mode
- Provides a server-side Moss adapter boundary with fail-closed error handling
- Blocks risky actions like payment or file deletion when trust is too low
- Detects known attack patterns such as injection, tampered amounts, and stale reuse
- Triggers a honeypot trap to mislead bad actors
- Stores an application-level hash-chain audit ledger for evidence and traceability
- Shows everything in a Streamlit dashboard

## Key demo features

- Runtime guardrail decisions before agent execution
- Trust scoring and latency tracking
- Honeypot-style attacker baiting
- Explainable audit chain with linked evidence
- Interactive UI for testing attack patterns

## Requirements

- Python 3.12 recommended
- pip
- A virtual environment is recommended

## Run locally

From the project root:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\.venv\Scripts\streamlit.exe run app.py
```

Then open the local URL shown in the terminal, typically:

```text
http://localhost:8501
```

## Example test inputs

The app includes a few sample hashes and attack values:

- Trusted document: `a1b2c3d4e5f6g7h8`
- Medium-trust review case: `d4e5f6g7h8i9j0k1`
- Risky injection case: `hacker_inject_999`
- Reuse or stale case: `stale_reuse_001`
- Tampered amount example: `tampered_amt_1`

## Project structure

- `app.py` — Streamlit UI and firewall logic
- `api.py` — FastAPI gateway entry point for agent tool requests
- `src/agent.py` — guarded agent-tool boundary
- `src/api_models.py` — Pydantic request and response models
- `src/retrieval_service.py` — retrieval orchestration used by the gateway and policy engine
- `src/retrieval_models.py` — normalized retrieval result contract
- `src/local_retrieval.py` — explicitly labeled local demo provider
- `src/evaluation_cases.py` — shared 12-case security evaluation corpus
- `src/moss_client.py` — server-side Moss client boundary and secret lookup
- `src/context_normalizer.py` — normalized retrieval contract for policy evaluation
- `src/review.py` — human-review queue for ambiguous decisions
- `src/` — supporting modules for blockchain, evaluation, honeypot, and validation
- `docs/architecture.md` — system architecture and Moss integration boundary
- `docs/PRD.md` — product requirements and evaluation criteria
- `tests/` — focused behavioral tests
- `requirements.txt` — Python dependencies

## Moss integration

Moss integration is implemented in `src/moss_client.py` using the official Python SDK.

The adapter:

- Loads the `agentguard-context` index
- Queries Moss with `MossClient` and `QueryOptions(top_k=1)`
- Maps Moss score and metadata into AgentGuard trust evidence
- Reports successful retrieval as `MOSS`
- Uses `LOCAL_DEMO` only when Moss is not configured
- Returns `MOSS_ERROR` with zero trust when Moss fails

Configure these values only through Streamlit Cloud Secrets or local `.streamlit/secrets.toml`:

```toml
MOSS_PROJECT_ID = "your-project-id"
MOSS_PROJECT_KEY = "your-project-key"
```

The application reads these settings only at runtime. Credentials are never returned in decision payloads or audit entries.

The `REVIEW` path creates a pending in-memory human-review request and prevents tool execution. The review queue is intentionally a prototype service boundary; production use requires durable storage and authenticated reviewer actions.

The audit ledger is an application-level hash chain, not an external blockchain. This is a prototype for product evaluation and hackathon demonstration, not a production security system.

The demo models an agent tool call: a request is evaluated before the tool is marked as executed. `ALLOW` executes the request; `BLOCK` and `REVIEW` prevent autonomous execution.

The Evaluation tab runs 12 deterministic cases across trusted actions, ambiguous context, prompt injection, tampering, stale context, unknown vendors, and unauthorized actions. It reports per-case results, category accuracy, median latency, and p95 latency.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Run the gateway API

Install the dependencies, then start FastAPI with Uvicorn:

```bash
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

OpenAPI documentation:

```text
http://127.0.0.1:8000/docs
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/v1/guard/tool-request \
	-H "Content-Type: application/json" \
	-d '{"action":"payment","doc_hash":"a1b2c3d4e5f6g7h8"}'
```

The API returns `ALLOW`, `BLOCK`, or `REVIEW` in the response body. Only `ALLOW` can execute a tool. Invalid requests return `422`. The Streamlit app and FastAPI gateway are separate runtime surfaces; deploying the Streamlit demo does not automatically deploy the API.

The gateway connects to retrieval through `src/retrieval_service.py`. That service selects the Moss adapter when configured, uses the `LOCAL_DEMO` provider only when Moss is not configured, normalizes the result, and fails closed with `MOSS_ERROR` when a configured provider fails. Retrieval evidence is returned separately from the policy decision; retrieval alone never authorizes a tool.