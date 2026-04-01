"""Controllers do modulo de licitacoes."""

from modules.bidding.controllers.agent_controller import router as agent_router
from modules.bidding.controllers.certificate_controller import router as certificate_router
from modules.bidding.controllers.contract_controller import router as contract_router
from modules.bidding.controllers.document_controller import router as document_router
from modules.bidding.controllers.erp_controller import router as erp_router
from modules.bidding.controllers.proposal_controller import router as proposal_router
from modules.bidding.controllers.sync_controller import router as sync_router
from modules.bidding.controllers.tender_controller import router as tender_router

__all__ = [
    "tender_router",
    "document_router",
    "proposal_router",
    "contract_router",
    "certificate_router",
    "agent_router",
    "sync_router",
    "erp_router",
]
