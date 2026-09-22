"""Backward-compatibility shim for src.review."""
import sys
from src.execution_review import review as _target

sys.modules[__name__] = _target
