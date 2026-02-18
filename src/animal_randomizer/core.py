"""Backward-compatible exports for core modules."""

from .randomization import randomize
from .service import RandomizerService

__all__ = ["randomize", "RandomizerService"]
