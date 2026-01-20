"""Schemas Pydantic do módulo Operations - Postos e Escalas."""

from .allocation import (
    AllocationCreate,
    AllocationFilter,
    AllocationListResponse,
    AllocationResponse,
    AllocationUpdate,
)
from .post import PostCreate, PostFilter, PostListResponse, PostResponse, PostStats, PostUpdate
from .scale import (
    ScaleCreate,
    ScaleFilter,
    ScaleGenerateRequest,
    ScaleListResponse,
    ScaleResponse,
    ScaleUpdate,
)
from .shift import ShiftCreate, ShiftFilter, ShiftListResponse, ShiftResponse, ShiftUpdate
from .substitution import (
    SubstitutionCreate,
    SubstitutionFilter,
    SubstitutionListResponse,
    SubstitutionResponse,
    SubstitutionUpdate,
)
from .time_bank import (
    TimeBankCreate,
    TimeBankFilter,
    TimeBankListResponse,
    TimeBankResponse,
    TimeBankSummary,
    TimeBankUpdate,
)

__all__ = [
    # Post
    "PostCreate",
    "PostUpdate",
    "PostResponse",
    "PostListResponse",
    "PostFilter",
    "PostStats",
    # Scale
    "ScaleCreate",
    "ScaleUpdate",
    "ScaleResponse",
    "ScaleListResponse",
    "ScaleFilter",
    "ScaleGenerateRequest",
    # Shift
    "ShiftCreate",
    "ShiftUpdate",
    "ShiftResponse",
    "ShiftListResponse",
    "ShiftFilter",
    # Allocation
    "AllocationCreate",
    "AllocationUpdate",
    "AllocationResponse",
    "AllocationListResponse",
    "AllocationFilter",
    # Substitution
    "SubstitutionCreate",
    "SubstitutionUpdate",
    "SubstitutionResponse",
    "SubstitutionListResponse",
    "SubstitutionFilter",
    # TimeBank
    "TimeBankCreate",
    "TimeBankUpdate",
    "TimeBankResponse",
    "TimeBankListResponse",
    "TimeBankFilter",
    "TimeBankSummary",
]
