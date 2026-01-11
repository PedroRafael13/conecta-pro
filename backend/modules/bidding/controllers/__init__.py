"""Controllers do modulo de licitacoes."""

from modules.bidding.controllers.tender_controller import router as tender_router
from modules.bidding.controllers.document_controller import router as document_router
from modules.bidding.controllers.proposal_controller import router as proposal_router
from modules.bidding.controllers.contract_controller import router as contract_router
from modules.bidding.controllers.certificate_controller import router as certificate_router

__all__ = [
    "tender_router",
    "document_router",
    "proposal_router",
    "contract_router",
    "certificate_router",
]
