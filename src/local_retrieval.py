"""Backward-compatibility shim for src.local_retrieval."""
import sys
from src.retrieval import local_retrieval as _target

sys.modules[__name__] = _target
