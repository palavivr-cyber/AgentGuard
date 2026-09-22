"""Backward-compatibility shim for src.retrieval_service."""
import sys
from src.retrieval import retrieval_service as _target

sys.modules[__name__] = _target
