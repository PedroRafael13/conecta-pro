"""Schemas Pydantic do modulo de licitacoes."""

from modules.bidding.schemas.tender import (
    TenderBase,
    TenderCreate,
    TenderUpdate,
    TenderResponse,
    TenderListResponse,
    TenderDocumentBase,
    TenderDocumentCreate,
    TenderDocumentResponse,
    TenderSearchParams,
)
from modules.bidding.schemas.document import (
    CompanyDocumentBase,
    CompanyDocumentCreate,
    CompanyDocumentUpdate,
    CompanyDocumentResponse,
    DocumentExpiringResponse,
)
from modules.bidding.schemas.proposal import (
    ProposalBase,
    ProposalCreate,
    ProposalUpdate,
    ProposalResponse,
    ProposalItemBase,
    ProposalItemCreate,
    ProposalCalculateBDI,
)
from modules.bidding.schemas.contract import (
    PublicContractBase,
    PublicContractCreate,
    PublicContractUpdate,
    PublicContractResponse,
    ContractAddendumCreate,
    ContractReadjustRequest,
    ContractReadjustResponse,
)
from modules.bidding.schemas.certificate import (
    CertificateBase,
    CertificateCreate,
    CertificateUpdate,
    CertificateResponse,
    CertificateRenewRequest,
    CertificateBulkStatusResponse,
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
