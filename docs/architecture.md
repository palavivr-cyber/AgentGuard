# AgentGuard Architecture

## Product goal

AgentGuard is a runtime safety gateway for transaction-oriented AI agents. It evaluates an action against retrieved context before the action is executed and records explainable evidence.

## Current runtime implementation

```mermaid
flowchart LR
    A[Agent tool request] --> B[FastAPI AgentGuard gateway]
    B --> C[Pydantic request validation]
    C --> D[Guarded tool boundary]
    D --> E[Retrieval service]
    E --> F[Local demo provider]
    E --> G[Moss integration boundary]
    F --> H[Trust and context normalizer]
    G --> H
    H --> I[Deterministic policy evaluation engine]
    I --> J{Decision}
    J -->|ALLOW| K[Python execution service]
    J -->|BLOCK| L[Prevent execution]
    J -->|REVIEW| M[In-memory review service]
    K --> N[Security trace when applicable]
    L --> N
    M --> O[Application hash-chain audit]
    N --> O
```

The Streamlit application is the visual demonstration client. The FastAPI service in `api.py` is the gateway layer for programmatic agent requests. Both paths use the same retrieval, policy, execution, review, security, and audit services.

The current execution service is a deterministic prototype boundary: it marks an approved action as executed but does not call an external payment, email, file, or contract system. The review service is in-memory and keeps `REVIEW` non-executable. The audit service uses an application-level verifiable hash chain.

## Moss role

The retrieval adapter is the boundary where Moss should provide fast semantic context retrieval. The current repository runs in `LOCAL_DEMO` mode because Moss credentials or SDK access are not configured. The UI and result payload expose this mode explicitly so local measurements are not presented as Moss measurements.

`src/moss_client.py` is the provider-specific boundary. It reads `MOSS_PROJECT_ID` and `MOSS_PROJECT_KEY` only at runtime from environment configuration or Streamlit Secrets and does not expose either value to the UI, audit ledger, or decision payload. When Moss access is available, the adapter returns the retrieved policy or transaction context, match metadata, and measured retrieval latency. The policy evaluator uses that result in the same decision path.

Missing configuration falls back to `LOCAL_DEMO` for the public demonstration. A configured-but-failing or unimplemented Moss request returns `MOSS_ERROR` with zero trust, so sensitive actions fail closed rather than being allowed on missing evidence.

## Implemented service boundaries

- `src/moss_client.py` — Moss provider boundary and server-side secret lookup
- `src/retrieval_service.py` — retrieval orchestration and provider selection
- `src/retrieval_models.py` — normalized retrieval response contract
- `src/local_retrieval.py` — explicitly labeled local demo provider
- `src/moss_validator.py` — compatibility wrapper from retrieval to policy
- `src/policy_models.py` — typed policy request and decision contracts
- `src/policy_engine.py` — deterministic policy rules and reason codes
- `src/context_normalizer.py` — stable, bounded context contract
- `src/review.py` and `src/review_service.py` — pending human-review service
- `src/execution_service.py` — ALLOW-only prototype execution boundary
- `src/honeypot.py` and `src/security_service.py` — suspicious blocked-request trace
- `src/audit_service.py` and `src/blockchain.py` — verifiable application hash-chain audit

The review queue is currently in-memory for the prototype. A production deployment should replace it with a durable review service while keeping `REVIEW` non-executable by default.

## Decision contract

Every guard result should expose:

- `decision`: `ALLOW`, `BLOCK`, or `REVIEW`
- `reason`: human-readable policy explanation
- `reason_code`: machine-readable policy outcome
- `policy_name` and `policy_version`: rule-set provenance
- `retrieval_mode`: active retrieval implementation
- `latency`: measured retrieval latency in milliseconds
- `trust`: normalized context trust score
- `doc` and `vendor`: retrieved evidence

The ledger is an application-level hash chain for audit evidence. It is not an external blockchain.

## Reference production architecture

The supplied architecture image is treated as a target, not a claim about the current runtime. PostgreSQL could replace the in-memory review and audit stores; OPA could become a policy adapter that consumes the existing policy contract; LangGraph could orchestrate genuinely multi-step agent workflows; OpenTelemetry could provide real instrumentation; and React/Node.js could provide a dedicated reviewer interface. Rust and external tool adapters are also future options. None of these are current dependencies unless separately implemented and tested.
