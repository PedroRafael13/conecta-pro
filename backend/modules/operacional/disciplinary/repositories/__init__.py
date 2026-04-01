"""
Repositories do modulo de Medidas Administrativas.
"""

from .disciplinary_repository import (
    DisciplinaryRepository,
    SignatureRepository,
    TemplateRepository,
)

__all__ = [
    "DisciplinaryRepository",
    "TemplateRepository",
    "SignatureRepository",
]
