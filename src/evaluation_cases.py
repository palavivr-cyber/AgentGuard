"""Backward-compatibility shim for src.evaluation_cases."""
import sys
from src.policy import evaluation_cases as _target

sys.modules[__name__] = _target
