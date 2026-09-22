"""Content-level security checks performed before a tool can execute.

These checks deliberately inspect the untrusted request payload, rather than
relying on demo document identifiers. They are deterministic and explainable
so a reviewer can see exactly why an action was stopped.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation


INJECTION_PATTERNS = (
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"system\s+prompt",
    r"disregard\s+(the\s+)?(policy|rules|guardrail)",
    r"override\s+(the\s+)?(approval|safety|policy)",
    r"do\s+not\s+tell\s+(the\s+)?user",
)


def _amount(value: object) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None


def analyze_request(context_text: str | None = None, transaction: dict | None = None) -> list[dict[str, str]]:
    """Return sanitized, explainable findings from untrusted request content."""
    findings: list[dict[str, str]] = []
    text = (context_text or "").lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            findings.append({
                "code": "PROMPT_INJECTION",
                "message": "Untrusted context contains an instruction-override pattern.",
            })
            break

    transaction = transaction or {}
    invoice_amount = _amount(transaction.get("invoice_amount"))
    approved_amount = _amount(transaction.get("approved_amount"))
    if invoice_amount is not None and approved_amount is not None and invoice_amount != approved_amount:
        findings.append({
            "code": "AMOUNT_MISMATCH",
            "message": "Invoice amount does not match the approved amount.",
        })
    if transaction.get("is_duplicate"):
        findings.append({
            "code": "DUPLICATE_INVOICE",
            "message": "Transaction is marked as a duplicate or previously paid invoice.",
        })
    if transaction.get("approval_expired"):
        findings.append({
            "code": "EXPIRED_APPROVAL",
            "message": "The approval attached to this transaction has expired.",
        })
    return findings


def security_block_result(result: dict, findings: list[dict[str, str]]) -> dict:
    """Convert a normal policy result into a fail-closed content-security block."""
    if not findings:
        return result
    primary = findings[0]
    return {
        **result,
        "allow": False,
        "decision": "BLOCK",
        "action": "BLOCKED",
        "alert": "CONTENT SECURITY CHECK FAILED",
        "reason": primary["message"],
        "reason_code": primary["code"],
        "color": "red",
        "security_findings": findings,
    }
