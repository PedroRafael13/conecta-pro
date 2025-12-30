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
from .opportunity import (
    OpportunityClose,
    OpportunityCreate,
    OpportunityCreateFromLead,
    OpportunityFilter,
    OpportunityListResponse,
    OpportunityResponse,
    OpportunityStageUpdate,
    OpportunityUpdate,
    PipelineForecast,
    PipelineStats,
)

__all__ = [
    # Lead
    "LeadCreate",
    "LeadUpdate",
    "LeadResponse",
    "LeadListResponse",
    "LeadFilter",
    "LeadScoreUpdate",
    "LeadStatusUpdate",
    "LeadStats",
    # Opportunity
    "OpportunityCreate",
    "OpportunityCreateFromLead",
    "OpportunityUpdate",
    "OpportunityStageUpdate",
    "OpportunityClose",
    "OpportunityResponse",
    "OpportunityListResponse",
    "OpportunityFilter",
    "PipelineStats",
    "PipelineForecast",
]
