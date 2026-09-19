# AgentGuard Product Requirements

## Problem

AI agents can act on stale, tampered, injected, or unauthorized context. A payment or file operation performed without a fast safety check can create financial and operational damage.

## Target user

Teams deploying transaction-oriented AI agents, initially accounts-payable workflows that review invoices and initiate payments.

## Product promise

Before an agent performs a sensitive action, AgentGuard retrieves relevant context, evaluates the action against policy, returns an explainable decision, and records evidence.

## Primary workflow

1. An agent submits a tool request with an action and document or transaction identifier.
2. AgentGuard retrieves relevant context through the configured retrieval adapter.
3. The policy evaluator calculates trust and checks the requested action.
4. AgentGuard returns `ALLOW`, `BLOCK`, or `REVIEW` with a reason and evidence.
5. The guarded tool executes only for `ALLOW`; `BLOCK` and `REVIEW` prevent autonomous execution.
6. The application audit chain records the decision, latency, and previous block reference.
7. Suspicious blocked inputs may activate a honeypot trace for investigation.

## Security requirements

- Unknown or low-trust context must be blocked for sensitive actions.
- Payment actions require a higher trust threshold than low-risk reads.
- Decisions must include an explanation and evidence fields.
- Audit entries must preserve ordering through a previous-hash reference.
- Secrets must be supplied through environment configuration and never committed.

## Evaluation requirements

The demo must cover trusted input, prompt injection, tampered amount, stale or duplicate reuse, unauthorized action, and an ambiguous case. Each case must report expected decision, actual decision, pass/fail status, and measured latency.

## Latency requirement

Moss is intended to provide sub-10ms semantic retrieval for the production path. The current local demo reports measured local lookup latency and labels it `LOCAL_DEMO`; it must not be described as a Moss benchmark until a real Moss path is configured.

## Non-goals for the sprint

- Building a real cryptocurrency or external blockchain network
- Supporting every agent framework
- Replacing a complete identity and access management system
- Claiming production reliability from a small demo corpus

## Success criteria

- A judge can run the demo from the README.
- A judge can see an allow and block decision in under two minutes.
- The Moss retrieval role is visible and technically honest.
- Evaluation results and latency are reproducible.
- The repository includes architecture, PRD, tests, and deployment instructions.
