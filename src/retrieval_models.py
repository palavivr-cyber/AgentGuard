"""Backward-compatibility shim for src.retrieval_models."""
import sys
from src.retrieval import retrieval_models as _target

sys.modules[__name__] = _target
