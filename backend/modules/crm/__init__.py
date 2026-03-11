"""
Module: crm
Description: Modulo de CRM - Customer Relationship Management
Author: Conecta PRO Team
Date: 2026-01-10

DEPRECATED: Use 'modules.comercial' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.
"""

import warnings

warnings.warn(
    "Importing from 'modules.crm' is deprecated. "
    "Use 'modules.comercial' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from fastapi import APIRouter  # noqa: E402

# Importa routers dos controllers
from .controllers import (  # noqa: E402
    commission_router,
    contract_router,
    dashboard_router,
    lead_router,
    opportunity_router,
    proposal_router,
)

# Importa models principais
from .models import (  # noqa: E402
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
from .repositories import (  # noqa: E402
    CommissionRepository,
    ContractRepository,
    LeadRepository,
    OpportunityRepository,
    ProposalRepository,
)

# Importa services principais
from .services import (  # noqa: E402
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
