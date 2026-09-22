"""Backward-compatibility shim for src.review_service."""
import sys
from src.execution_review import review_service as _target

sys.modules[__name__] = _target