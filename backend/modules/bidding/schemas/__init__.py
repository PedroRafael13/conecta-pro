"""Schemas Pydantic do modulo de licitacoes."""

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
from modules.bidding.schemas.document import (
    CompanyDocumentBase,
    CompanyDocumentCreate,
    CompanyDocumentResponse,
    CompanyDocumentUpdate,
    DocumentExpiringResponse,
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
]
