# 🛡️ AgentGuard

AgentGuard is a runtime safety gateway for transaction-oriented AI agents. It validates context before an agent can act, returns an explainable allow or block decision, and records audit evidence.

## What this project does

- Validates document trust through a retrieval adapter with an explicit local demo mode
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
- `src/agent.py` — guarded agent-tool boundary
- `src/evaluation_cases.py` — shared 12-case security evaluation corpus
- `src/` — supporting modules for blockchain, evaluation, honeypot, and validation
- `docs/architecture.md` — system architecture and Moss integration boundary
- `docs/PRD.md` — product requirements and evaluation criteria
- `tests/` — focused behavioral tests
- `requirements.txt` — Python dependencies

## Notes

The current repository runs in `LOCAL_DEMO` retrieval mode because Moss credentials or SDK access are not configured. Local latency is measured and labeled as local; it must not be presented as a Moss benchmark. Configure the Moss adapter before making production or sub-10ms Moss claims.

The audit ledger is an application-level hash chain, not an external blockchain. This is a prototype for product evaluation and hackathon demonstration, not a production security system.

The demo models an agent tool call: a request is evaluated before the tool is marked as executed. `ALLOW` executes the request; `BLOCK` and `REVIEW` prevent autonomous execution.

The Evaluation tab runs 12 deterministic cases across trusted actions, ambiguous context, prompt injection, tampering, stale context, unknown vendors, and unauthorized actions. It reports per-case results, category accuracy, median latency, and p95 latency.

## Run tests

```bash
python -m unittest discover -s tests -v
```