"""Backward-compatibility shim for src.audit_service."""
import sys
from src.audit_security import audit_service as _target

sys.modules[__name__] = _target