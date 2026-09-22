"""Backward-compatibility shim for src.evaluator."""
import sys
from src.policy import evaluator as _target

sys.modules[__name__] = _target
