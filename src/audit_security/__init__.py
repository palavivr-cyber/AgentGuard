"""Audit & Security Layer (Layer 5 in Architecture Diagram).

Provides the verifiable hash-chain audit ledger, content security analysis, and honeypot security tracing.
"""

from src.audit_security.audit_service import (
    get_audit_events,
    record_audit_event,
    verify_audit_chain,
)
from src.audit_security.blockchain import (
    LEDGER,
    add_to_ledger,
    get_ledger,
    verify_ledger,
)
from src.audit_security.honeypot import honeypot_trap
from src.audit_security.security_analysis import (
    analyze_request,
    security_block_result,
)
from src.audit_security.security_service import security_trace

__all__ = [
    "LEDGER",
    "add_to_ledger",
    "analyze_request",
    "get_audit_events",
    "get_ledger",
    "honeypot_trap",
    "record_audit_event",
    "security_block_result",
    "security_trace",
    "verify_audit_chain",
    "verify_ledger",
]
