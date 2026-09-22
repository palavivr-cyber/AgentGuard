"""Backward-compatibility shim for src.moss_validator."""
import sys
from src.policy import moss_validator as _target

sys.modules[__name__] = _target
