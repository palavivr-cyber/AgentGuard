"""Backward-compatibility shim for src.security_analysis."""
import sys
from src.audit_security import security_analysis as _target

sys.modules[__name__] = _target
