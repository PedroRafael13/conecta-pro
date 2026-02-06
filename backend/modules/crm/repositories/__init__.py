"""Repositories do módulo CRM."""

from .commission_repository import CommissionRepository
from .contract_repository import ContractRepository
from .lead_repository import LeadRepository
from .opportunity_repository import OpportunityRepository
from .proposal_repository import ProposalRepository

__all__ = [
    "LeadRepository",
    "OpportunityRepository",
    "ProposalRepository",
    "CommissionRepository",
    "ContractRepository",
]
