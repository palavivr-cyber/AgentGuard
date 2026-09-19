# 🛡️ AgentGuard

AgentGuard is a lightweight demo project for an AI agent firewall. It simulates a real-time guardrail system that blocks risky or tampered documents before an agent can act on them.

## What this project does

- Validates document trust using a simulated Moss-style check
- Blocks risky actions like payment or file deletion when trust is too low
- Detects known attack patterns such as injection, tampered amounts, and stale reuse
- Triggers a honeypot trap to mislead bad actors
- Stores a blockchain-like audit ledger for evidence and traceability
- Shows everything in a Streamlit dashboard

## Key demo features

- Runtime guardrail decisions before agent execution
- Trust scoring and latency tracking
- Honeypot-style attacker baiting
- Immutable-looking audit block chain
- Interactive UI for testing attack patterns

## Requirements

- Python 3.10+
- pip
- A virtual environment is recommended

## Run locally

From the project root:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown in the terminal, typically:

```text
http://localhost:8501
```

## Example test inputs

The app includes a few sample hashes and attack values:

- Trusted document: `a1b2c3d4e5f6g7h8`
- Risky injection case: `hacker_inject_999`
- Reuse or stale case: `stale_reuse_001`
- Tampered amount example: `tampered_amt_1`

## Project structure

- `app.py` — Streamlit UI and firewall logic
- `src/` — supporting modules for blockchain, evaluation, honeypot, and validation
- `requirements.txt` — Python dependencies

## Notes

This is a demo/prototype designed for credibility and product storytelling, not a production-grade security system. It simulates the core concepts in a fast, visual way for presentations and demos.