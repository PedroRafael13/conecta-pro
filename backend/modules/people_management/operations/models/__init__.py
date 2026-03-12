"""
Operations Models — Re-export dos models do modulo operacional.
"""

import contextlib

with contextlib.suppress(ImportError):
    from modules.operacional.models import (
        Allocation,
        AllocationStatus,
        Post,
        PostStatus,
        PostType,
        Scale,
        ScaleStatus,
        ScaleTemplate,
        ScaleType,
        Shift,
        ShiftStatus,
        ShiftType,
        Substitution,
        SubstitutionReason,
        SubstitutionStatus,
        TimeBank,
        TimeBankEntryType,
        TimeBankStatus,
    )

with contextlib.suppress(ImportError):
    from modules.operacional.models.employee import Employee

__all__ = [
    "Employee",
    "Post",
    "PostType",
    "PostStatus",
    "Scale",
    "ScaleType",
    "ScaleStatus",
    "ScaleTemplate",
    "Shift",
    "ShiftType",
    "ShiftStatus",
    "Allocation",
    "AllocationStatus",
    "Substitution",
    "SubstitutionStatus",
    "SubstitutionReason",
    "TimeBank",
    "TimeBankEntryType",
    "TimeBankStatus",
]
