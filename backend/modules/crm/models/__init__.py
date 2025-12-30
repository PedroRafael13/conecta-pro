"""Modelos do módulo CRM."""

from .lead import Lead, LeadSource, LeadStatus
from .opportunity import (
    LossReason,
    Opportunity,
    OpportunityPriority,
    OpportunityStage,
)

__all__ = [
    "Lead",
    "LeadStatus",
    "LeadSource",
    "Opportunity",
    "OpportunityStage",
    "OpportunityPriority",
    "LossReason",
]
