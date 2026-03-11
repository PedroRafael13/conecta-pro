"""
Módulo COMERCIAL — Agregador
Unifica: crm + clients + bidding (licitações) + services

Routers re-exportados dos módulos de implementação.
API URLs inalteradas.
Data migração: 2026-03-11
Aliases válidos por 60 dias até 2026-05-10

Nota: bidding_certificate_router movido para fiscal_contabil (2026-03-11)
"""

# --- CRM (leads, oportunidades, propostas, contratos, comissões, dashboard) ---
# --- Bidding / Licitações (sem certidões — movidas para fiscal_contabil) ---
from modules.bidding import contract_router as bidding_contract_router
from modules.bidding import document_router as bidding_document_router
from modules.bidding import proposal_router as bidding_proposal_router
from modules.bidding import (
    tender_router as bidding_tender_router,
)

# --- Clients ---
from modules.clients.controllers import router as client_router
from modules.crm.controllers import (
    commission_router as crm_commission_router,
)
from modules.crm.controllers import (
    contract_router as crm_contract_router,
)
from modules.crm.controllers import (
    dashboard_router as crm_dashboard_router,
)
from modules.crm.controllers import (
    lead_router as crm_lead_router,
)
from modules.crm.controllers import (
    opportunity_router as crm_opportunity_router,
)
from modules.crm.controllers import (
    proposal_router as crm_proposal_router,
)

# --- Services ---
from modules.services.controllers import router as service_router

__all__ = [
    "crm_lead_router",
    "crm_opportunity_router",
    "crm_proposal_router",
    "crm_contract_router",
    "crm_commission_router",
    "crm_dashboard_router",
    "client_router",
    "bidding_tender_router",
    "bidding_document_router",
    "bidding_proposal_router",
    "bidding_contract_router",
    "service_router",
]
