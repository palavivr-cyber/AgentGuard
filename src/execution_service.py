"""Backward-compatibility shim for src.execution_service."""
import sys
from src.execution_review import execution_service as _target

sys.modules[__name__] = _target