"""
Repositories do modulo de Medidas Administrativas.
"""

from .disciplinary_repository import (
    DisciplinaryRepository,
    TemplateRepository,
    SignatureRepository,
)

__all__ = [
    "DisciplinaryRepository",
    "TemplateRepository",
    "SignatureRepository",
]
