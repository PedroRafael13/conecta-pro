"""Repositories do modulo de licitacoes."""

from modules.bidding.repositories.contract_repository import ContractRepository
from modules.bidding.repositories.document_repository import DocumentRepository
from modules.bidding.repositories.proposal_repository import ProposalRepository
from modules.bidding.repositories.tender_repository import TenderRepository

__all__ = [
    "TenderRepository",
    "DocumentRepository",
    "ProposalRepository",
    "ContractRepository",
]
