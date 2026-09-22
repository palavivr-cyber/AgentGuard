"""Backward-compatibility shim for src.policy_models."""
import sys
from src.policy import policy_models as _target

sys.modules[__name__] = _target