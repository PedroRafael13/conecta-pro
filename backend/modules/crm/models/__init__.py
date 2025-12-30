"""Modelos do módulo CRM."""

from .lead import Lead, LeadSource, LeadStatus
from .opportunity import (
    LossReason,
    Opportunity,
    OpportunityPriority,
    OpportunityStage,
)
from .proposal import (
    ApprovalAction,
    DiscountType,
    Proposal,
    ProposalApproval,
    ProposalItem,
    ProposalStatus,
    ProposalTemplate,
    ProposalType,
)

__all__ = [
    # Lead
    "Lead",
    "LeadStatus",
    "LeadSource",
    # Opportunity
    "Opportunity",
    "OpportunityStage",
    "OpportunityPriority",
    "LossReason",
    # Proposal
    "Proposal",
    "ProposalItem",
    "ProposalTemplate",
    "ProposalApproval",
    "ProposalStatus",
    "ProposalType",
    "DiscountType",
    "ApprovalAction",
]
