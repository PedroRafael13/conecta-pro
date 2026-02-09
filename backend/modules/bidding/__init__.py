"""
Modulo de Licitacoes - Conecta PRO
==================================
Gestao completa de licitacoes publicas com foco no Estado do Amazonas.

Funcionalidades:
- Gestao de Editais
- Documentacao Exigida (certidoes, atestados)
- Propostas Publicas
- Contratos Publicos
- Integracao PNCP
- Compliance Lei 14.133/2021
"""

from modules.bidding.controllers import (
    certificate_router,
    contract_router,
    document_router,
    proposal_router,
    tender_router,
)
from modules.bidding.models import (
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
from modules.bidding.services import (
    CertificateService,
    ContractService,
    DocumentService,
    PNCPService,
    # BiddingAIService,  # Removido temporariamente (deps: spacy, selenium)
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
    # Services
    "TenderService",
    "DocumentService",
    "ProposalService",
    "ContractService",
    "CertificateService",
    "PNCPService",
    # "BiddingAIService",  # Removido temporariamente
]
