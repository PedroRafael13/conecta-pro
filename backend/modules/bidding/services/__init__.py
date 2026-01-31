"""Services do modulo de licitacoes."""

from modules.bidding.services.tender_service import TenderService
from modules.bidding.services.document_service import DocumentService
from modules.bidding.services.proposal_service import ProposalService
from modules.bidding.services.contract_service import ContractService
from modules.bidding.services.certificate_service import CertificateService
from modules.bidding.services.pncp_service import PNCPService

# BiddingAIService removido temporariamente (dependencias: spacy, selenium, nltk)
# from modules.bidding.services.bidding_ai_service import BiddingAIService

__all__ = [
    "TenderService",
    "DocumentService",
    "ProposalService",
    "ContractService",
    "CertificateService",
    "PNCPService",
    # "BiddingAIService",
]
