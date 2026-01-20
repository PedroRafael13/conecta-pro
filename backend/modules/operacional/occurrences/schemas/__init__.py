"""Schemas do modulo de Ocorrencias."""

from .occurrence_schemas import (
    # Base
    OccurrenceBase,
    # Create
    OccurrenceCreate,
    OccurrenceUpdate,
    AttachmentCreate,
    CommentCreate,
    CategoryConfigCreate,
    CategoryConfigUpdate,
    # Response
    OccurrenceResponse,
    OccurrenceListResponse,
    OccurrenceSummaryResponse,
    AttachmentResponse,
    CommentResponse,
    CategoryConfigResponse,
    # Filter
    OccurrenceFilter,
    # Actions
    EscalateRequest,
    ResolveRequest,
    ReopenRequest,
    # Dashboard
    DashboardStats,
    SLABreachItem,
    PendingOccurrenceItem,
)

__all__ = [
    # Base
    "OccurrenceBase",
    # Create
    "OccurrenceCreate",
    "OccurrenceUpdate",
    "AttachmentCreate",
    "CommentCreate",
    "CategoryConfigCreate",
    "CategoryConfigUpdate",
    # Response
    "OccurrenceResponse",
    "OccurrenceListResponse",
    "OccurrenceSummaryResponse",
    "AttachmentResponse",
    "CommentResponse",
    "CategoryConfigResponse",
    # Filter
    "OccurrenceFilter",
    # Actions
    "EscalateRequest",
    "ResolveRequest",
    "ReopenRequest",
    # Dashboard
    "DashboardStats",
    "SLABreachItem",
    "PendingOccurrenceItem",
]
