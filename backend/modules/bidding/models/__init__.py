"""Models do modulo de licitacoes."""

from modules.bidding.models.analysis import BiddingAnalysis
from modules.bidding.models.assessment import BiddingAssessment
from modules.bidding.models.certificate import Certificate, CertificateStatus, CertificateType
from modules.bidding.models.company_document import CompanyDocument, DocumentStatus, DocumentType
from modules.bidding.models.dispute import BiddingDispute
from modules.bidding.models.measurement import Measurement, MeasurementStatus
from modules.bidding.models.opportunity import BiddingOpportunity
from modules.bidding.models.price_history import BiddingPriceHistory
from modules.bidding.models.pricing import BiddingPricing
from modules.bidding.models.proposal import BiddingProposal, BiddingProposalItem, ProposalStatus
from modules.bidding.models.public_contract import ContractStatus, PublicContract
from modules.bidding.models.sync_job import BiddingSyncJob
from modules.bidding.models.tender import Tender, TenderDocument, TenderStatus

__all__ = [
    # Tender
    "Tender",
    "TenderStatus",
    "TenderDocument",
    # Company Document
    "CompanyDocument",
    "DocumentType",
    "DocumentStatus",
    # Proposal
    "BiddingProposal",
    "ProposalStatus",
    "BiddingProposalItem",
    # Contract
    "PublicContract",
    "ContractStatus",
    # Measurement
    "Measurement",
    "MeasurementStatus",
    # Certificate
    "Certificate",
    "CertificateType",
    "CertificateStatus",
    # AI Agents - Opportunity
    "BiddingOpportunity",
    # AI Agents - Analysis
    "BiddingAnalysis",
    # AI Agents - Assessment
    "BiddingAssessment",
    # AI Agents - Pricing
    "BiddingPricing",
    # AI Agents - Dispute
    "BiddingDispute",
    # AI Agents - Price History
    "BiddingPriceHistory",
    # AI Agents - Sync Job
    "BiddingSyncJob",
]
