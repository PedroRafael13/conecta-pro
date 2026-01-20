"""
Controllers do modulo de Medidas Administrativas.
"""

from .disciplinary_controller import router as disciplinary_router

__all__ = [
    "disciplinary_router",
]
