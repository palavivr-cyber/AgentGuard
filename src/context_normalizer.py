"""Backward-compatibility shim for src.context_normalizer."""
import sys
from src.policy import context_normalizer as _target

sys.modules[__name__] = _target
