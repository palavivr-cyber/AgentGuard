"""Backward-compatibility shim for src.policy_engine."""
import sys
from src.policy import policy_engine as _target

sys.modules[__name__] = _target