"""Schemas do módulo CRM."""

from .lead import (
    LeadCreate,
    LeadFilter,
    LeadListResponse,
    LeadResponse,
    LeadScoreUpdate,
    LeadStats,
    LeadStatusUpdate,
    LeadUpdate,
)

__all__ = [
    "LeadCreate",
    "LeadUpdate",
    "LeadResponse",
    "LeadListResponse",
    "LeadFilter",
    "LeadScoreUpdate",
    "LeadStatusUpdate",
    "LeadStats",
]
