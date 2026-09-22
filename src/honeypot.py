"""Backward-compatibility shim for src.honeypot."""
import sys
from src.audit_security import honeypot as _target

sys.modules[__name__] = _target
