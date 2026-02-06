"""
Module: crm
Description: Modulo de CRM - Customer Relationship Management
Author: Conecta PRO Team
Date: 2026-01-10
Quality Score Target: 99+/100

Este modulo fornece:
- Gestao de Leads e scoring automatizado
- Pipeline de Oportunidades
- Geracao e gestao de Propostas
- Contratos e aditivos
- Comissoes de vendedores
- Dashboard e metricas de vendas

Estrutura modular:
- models/: Modelos SQLAlchemy para persistencia
- schemas/: Schemas Pydantic para validacao
- services/: Logica de negocio
- controllers/: Endpoints FastAPI
- repositories/: Acesso a dados
"""

from fastapi import APIRouter

# Importa routers dos controllers
from .controllers import (
    lead_router,
    opportunity_router,
    proposal_router,
    contract_router,
    commission_router,
    dashboard_router,
)

# Importa models principais
from .models import (
    # Lead
    Lead,
    LeadStatus,
    LeadSource,
    # Opportunity
    Opportunity,
    OpportunityStage,
    OpportunityPriority,
    LossReason,
    # Proposal
    Proposal,
    ProposalItem,
    ProposalTemplate,
    ProposalApproval,
    ProposalStatus,
    ProposalType,
    DiscountType,
    ApprovalAction,
    # Commission
    Commission,
    CommissionRule,
    CommissionPayment,
    CommissionSummary,
    SellerCommissionRule,
    CommissionType,
    CommissionTrigger,
    CommissionStatus,
    PaymentMethod,
    # Contract
    Contract,
    ContractItem,
    ContractTemplate,
    ContractAddendum,
    ContractSLAReport,
    ContractType,
    ContractStatus,
    AdjustmentIndex,
    AddendumType,
    ServiceType,
)

# Importa services principais
from .services import (
    LeadService,
    LeadScoringEngine,
    lead_service,
    PipelineService,
    pipeline_service,
    CommissionService,
    commission_service,
    DashboardService,
    dashboard_service,
    ContractService,
    contract_service,
)

# Importa repositories
from .repositories import (
    LeadRepository,
    OpportunityRepository,
    ProposalRepository,
    CommissionRepository,
    ContractRepository,
)

# Cria router principal que agrega todos os sub-routers
crm_router = APIRouter(prefix="/crm", tags=["CRM"])

# Inclui todos os sub-routers
crm_router.include_router(lead_router)
crm_router.include_router(opportunity_router)
crm_router.include_router(proposal_router)
crm_router.include_router(contract_router)
crm_router.include_router(commission_router)
crm_router.include_router(dashboard_router)

# Exporta tambem o router antigo para compatibilidade
router = crm_router

__all__ = [
    # Router principal
    "crm_router",
    "router",
    # Routers individuais
    "lead_router",
    "opportunity_router",
    "proposal_router",
    "contract_router",
    "commission_router",
    "dashboard_router",
    # Models - Lead
    "Lead",
    "LeadStatus",
    "LeadSource",
    # Models - Opportunity
    "Opportunity",
    "OpportunityStage",
    "OpportunityPriority",
    "LossReason",
    # Models - Proposal
    "Proposal",
    "ProposalItem",
    "ProposalTemplate",
    "ProposalApproval",
    "ProposalStatus",
    "ProposalType",
    "DiscountType",
    "ApprovalAction",
    # Models - Commission
    "Commission",
    "CommissionRule",
    "CommissionPayment",
    "CommissionSummary",
    "SellerCommissionRule",
    "CommissionType",
    "CommissionTrigger",
    "CommissionStatus",
    "PaymentMethod",
    # Models - Contract
    "Contract",
    "ContractItem",
    "ContractTemplate",
    "ContractAddendum",
    "ContractSLAReport",
    "ContractType",
    "ContractStatus",
    "AdjustmentIndex",
    "AddendumType",
    "ServiceType",
    # Services
    "LeadService",
    "LeadScoringEngine",
    "lead_service",
    "PipelineService",
    "pipeline_service",
    "CommissionService",
    "commission_service",
    "DashboardService",
    "dashboard_service",
    "ContractService",
    "contract_service",
    # Repositories
    "LeadRepository",
    "OpportunityRepository",
    "ProposalRepository",
    "CommissionRepository",
    "ContractRepository",
]

__version__ = "1.0.0"
