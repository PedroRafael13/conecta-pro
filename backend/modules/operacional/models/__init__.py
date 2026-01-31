"""Modelos do módulo Operations - Postos e Escalas."""

# Post deve ser importado primeiro (dependência de Allocation e Scale)
from .post import Post, PostStatus, PostType, ShiftType
from .scale import Scale, ScaleStatus, ScaleType
from .scale_template import ScaleTemplate
from .shift import Shift, ShiftStatus
from .allocation import Allocation, AllocationStatus
from .substitution import Substitution, SubstitutionReason, SubstitutionStatus
from .time_bank import TimeBank, TimeBankEntryType, TimeBankStatus
# Importar Occurrence para registrar no SQLAlchemy (necessário para relacionamentos)
from modules.operacional.occurrences.models import Occurrence

__all__ = [
    # Post
    "Post",
    "PostType",
    "PostStatus",
    "ShiftType",
    # Scale
    "Scale",
    "ScaleType",
    "ScaleStatus",
    # ScaleTemplate
    "ScaleTemplate",
    # Shift
    "Shift",
    "ShiftStatus",
    # Allocation
    "Allocation",
    "AllocationStatus",
    # Substitution
    "Substitution",
    "SubstitutionStatus",
    "SubstitutionReason",
    # TimeBank
    "TimeBank",
    "TimeBankEntryType",
    "TimeBankStatus",
    # Occurrence (movido para occurrences/models/)
]
