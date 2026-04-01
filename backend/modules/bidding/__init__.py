"""
Modulo de Licitacoes - Conecta PRO

DEPRECATED: Use 'modules.comercial' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.
"""

import warnings

warnings.warn(
    "Importing from 'modules.bidding' is deprecated. "
    "Use 'modules.comercial' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from modules.bidding.controllers import (  # noqa: E402
    agent_router,
    certificate_router,
    contract_router,
    document_router,
    erp_router,
    proposal_router,
    sync_router,
    tender_router,
)
from modules.bidding.models import (  # noqa: E402
    BiddingProposal,
    BiddingProposalItem,
    Certificate,
    CertificateStatus,
    CertificateType,
    CompanyDocument,
    ContractStatus,
    DocumentStatus,
    DocumentType,
    Measurement,
    MeasurementStatus,
    ProposalStatus,
    PublicContract,
    Tender,
    TenderDocument,
    TenderStatus,
)
from modules.bidding.services import (  # noqa: E402
    CertificateService,
    ContractService,
    DocumentService,
    ERPIntegrationService,
    PNCPService,
    ProposalService,
    TenderService,
)

__all__ = [
    # Models
    "Tender",
    "TenderDocument",
    "TenderStatus",
    "CompanyDocument",
    "DocumentType",
    "DocumentStatus",
    "BiddingProposal",
    "ProposalStatus",
    "BiddingProposalItem",
    "PublicContract",
    "ContractStatus",
    "Measurement",
    "MeasurementStatus",
    "Certificate",
    "CertificateType",
    "CertificateStatus",
    # Routers
    "tender_router",
    "document_router",
    "proposal_router",
    "contract_router",
    "certificate_router",
    "agent_router",
    "sync_router",
    "erp_router",
    # Services
    "TenderService",
    "DocumentService",
    "ProposalService",
    "ContractService",
    "CertificateService",
    "PNCPService",
    "ERPIntegrationService",
]
