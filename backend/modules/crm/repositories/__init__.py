"""Repositories do módulo CRM."""

from .lead_repository import LeadRepository
from .opportunity_repository import OpportunityRepository
from .proposal_repository import ProposalRepository

__all__ = ["LeadRepository", "OpportunityRepository", "ProposalRepository"]
