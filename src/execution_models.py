"""Backward-compatibility shim for src.execution_models."""
import sys
from src.execution_review import execution_models as _target

sys.modules[__name__] = _target