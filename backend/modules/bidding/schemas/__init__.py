"""Schemas Pydantic do modulo de licitacoes."""

from modules.bidding.schemas.analysis import (
    AnalysisCreate,
    AnalysisResponse,
    AnalystRequest,
)
from modules.bidding.schemas.assessment import (
    AssessmentCreate,
    AssessmentResponse,
    AssessorRequest,
)
from modules.bidding.schemas.certificate import (
    CertificateBase,
    CertificateBulkStatusResponse,
    CertificateCreate,
    CertificateRenewRequest,
    CertificateResponse,
    CertificateUpdate,
)
from modules.bidding.schemas.contract import (
    ContractAddendumCreate,
    ContractReadjustRequest,
    ContractReadjustResponse,
    PublicContractBase,
    PublicContractCreate,
    PublicContractResponse,
    PublicContractUpdate,
)
from modules.bidding.schemas.dispute import (
    DisputeCreate,
    DisputeResponse,
)
from modules.bidding.schemas.document import (
    CompanyDocumentBase,
    CompanyDocumentCreate,
    CompanyDocumentResponse,
    CompanyDocumentUpdate,
    DocumentExpiringResponse,
)
from modules.bidding.schemas.opportunity import (
    OpportunityCreate,
    OpportunityListResponse,
    OpportunityResponse,
    ScoutRequest,
)
from modules.bidding.schemas.pipeline import (
    PipelineRequest,
    PipelineResult,
    PipelineStepResult,
)
from modules.bidding.schemas.pricing import (
    PricerRequest,
    PricingCreate,
    PricingResponse,
)
from modules.bidding.schemas.proposal import (
    ProposalBase,
    ProposalCalculateBDI,
    ProposalCreate,
    ProposalItemBase,
    ProposalItemCreate,
    ProposalResponse,
    ProposalUpdate,
)
from modules.bidding.schemas.tender import (
    TenderBase,
    TenderCreate,
    TenderDocumentBase,
    TenderDocumentCreate,
    TenderDocumentResponse,
    TenderListResponse,
    TenderResponse,
    TenderSearchParams,
    TenderUpdate,
)

__all__ = [
    # Tender
    "TenderBase",
    "TenderCreate",
    "TenderUpdate",
    "TenderResponse",
    "TenderListResponse",
    "TenderDocumentBase",
    "TenderDocumentCreate",
    "TenderDocumentResponse",
    "TenderSearchParams",
    # Document
    "CompanyDocumentBase",
    "CompanyDocumentCreate",
    "CompanyDocumentUpdate",
    "CompanyDocumentResponse",
    "DocumentExpiringResponse",
    # Proposal
    "ProposalBase",
    "ProposalCreate",
    "ProposalUpdate",
    "ProposalResponse",
    "ProposalItemBase",
    "ProposalItemCreate",
    "ProposalCalculateBDI",
    # Contract
    "PublicContractBase",
    "PublicContractCreate",
    "PublicContractUpdate",
    "PublicContractResponse",
    "ContractAddendumCreate",
    "ContractReadjustRequest",
    "ContractReadjustResponse",
    # Certificate
    "CertificateBase",
    "CertificateCreate",
    "CertificateUpdate",
    "CertificateResponse",
    "CertificateRenewRequest",
    "CertificateBulkStatusResponse",
    # Opportunity (Scout)
    "ScoutRequest",
    "OpportunityCreate",
    "OpportunityResponse",
    "OpportunityListResponse",
    # Analysis (Analyst)
    "AnalystRequest",
    "AnalysisCreate",
    "AnalysisResponse",
    # Assessment (Assessor)
    "AssessorRequest",
    "AssessmentCreate",
    "AssessmentResponse",
    # Pricing (Pricer)
    "PricerRequest",
    "PricingCreate",
    "PricingResponse",
    # Dispute (Warrior)
    "DisputeCreate",
    "DisputeResponse",
    # Pipeline
    "PipelineRequest",
    "PipelineResult",
    "PipelineStepResult",
]
