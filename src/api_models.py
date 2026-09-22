"""Backward-compatibility shim for src.api_models."""
import sys
from src.gateway import api_models as _target

sys.modules[__name__] = _target
