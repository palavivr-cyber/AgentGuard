"""Backward-compatibility shim for src.moss_client."""
import sys
from src.retrieval import moss_client as _target

sys.modules[__name__] = _target
