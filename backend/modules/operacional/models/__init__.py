"""Modelos do módulo Operations - Postos e Escalas."""

# Post deve ser importado primeiro (dependência de Allocation e Scale)
from .post import Post, PostStatus, PostType, ShiftType
from .scale import Scale, ScaleStatus, ScaleType
from .shift import Shift, ShiftStatus
from .allocation import Allocation, AllocationStatus
from .substitution import Substitution, SubstitutionReason, SubstitutionStatus
from .time_bank import TimeBank, TimeBankEntryType, TimeBankStatus

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
]
