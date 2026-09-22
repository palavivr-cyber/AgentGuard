"""Backward-compatibility shim for src.security_service."""
import sys
from src.audit_security import security_service as _target

sys.modules[__name__] = _target
