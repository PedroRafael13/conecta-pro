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

from modules.bidding.models import (
    Tender,
    TenderDocument,
    TenderStatus,
    CompanyDocument,
    DocumentType,
    DocumentStatus,
    BiddingProposal,
    ProposalStatus,
    BiddingProposalItem,
    PublicContract,
    ContractStatus,
    Measurement,
    MeasurementStatus,
    Certificate,
    CertificateType,
    CertificateStatus,
)
from modules.bidding.controllers import (
    tender_router,
    document_router,
    proposal_router,
    contract_router,
    certificate_router,
)
from modules.bidding.services import (
    TenderService,
    DocumentService,
    ProposalService,
    ContractService,
    CertificateService,
    PNCPService,
    # BiddingAIService,  # Removido temporariamente (deps: spacy, selenium)
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
