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
    commission_router,
    contract_router,
    dashboard_router,
    lead_router,
    opportunity_router,
    proposal_router,
)

# Importa models principais
from .models import (
    AddendumType,
    AdjustmentIndex,
    ApprovalAction,
    # Commission
    Commission,
    CommissionPayment,
    CommissionRule,
    CommissionStatus,
    CommissionSummary,
    CommissionTrigger,
    CommissionType,
    # Contract
    Contract,
    ContractAddendum,
    ContractItem,
    ContractSLAReport,
    ContractStatus,
    ContractTemplate,
    ContractType,
    DiscountType,
    # Lead
    Lead,
    LeadSource,
    LeadStatus,
    LossReason,
    # Opportunity
    Opportunity,
    OpportunityPriority,
    OpportunityStage,
    PaymentMethod,
    # Proposal
    Proposal,
    ProposalApproval,
    ProposalItem,
    ProposalStatus,
    ProposalTemplate,
    ProposalType,
    SellerCommissionRule,
    ServiceType,
)

# Importa repositories
from .repositories import (
    CommissionRepository,
    ContractRepository,
    LeadRepository,
    OpportunityRepository,
    ProposalRepository,
)

# Importa services principais
from .services import (
    CommissionService,
    ContractService,
    DashboardService,
    LeadScoringEngine,
    LeadService,
    PipelineService,
    commission_service,
    contract_service,
    dashboard_service,
    lead_service,
    pipeline_service,
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
