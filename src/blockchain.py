"""Backward-compatibility shim for src.blockchain."""
import sys
from src.audit_security import blockchain as _target

sys.modules[__name__] = _target
