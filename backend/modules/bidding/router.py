"""
Router Agregador — Modulo de Licitacoes
========================================
Importa todos os controller routers e monta um router combinado
com prefixo /licitacoes para uso direto no app principal.

Inclui routers de:
- tender (editais)
- proposal (propostas)
- contract (contratos publicos)
- certificate (certidoes)
- document (documentos)
- agent (agentes IA)
- sync (sincronizacao de portais)
- erp (integracao ERP)
- opportunity (oportunidades do Scout)
- dispute (disputas/pregoes)
"""

import logging

from fastapi import APIRouter

from modules.bidding.controllers.agent_controller import router as agent_router
from modules.bidding.controllers.certificate_controller import router as certificate_router
from modules.bidding.controllers.contract_controller import router as contract_router
from modules.bidding.controllers.dispute_controller import router as dispute_router
from modules.bidding.controllers.document_controller import router as document_router
from modules.bidding.controllers.erp_controller import router as erp_router
from modules.bidding.controllers.opportunity_controller import router as opportunity_router
from modules.bidding.controllers.proposal_controller import router as proposal_router
from modules.bidding.controllers.sync_controller import router as sync_router
from modules.bidding.controllers.tender_controller import router as tender_router
from modules.bidding.websockets.dispute_ws import router as dispute_ws_router

logger = logging.getLogger(__name__)

# Router principal do modulo de licitacoes
router = APIRouter(prefix="/licitacoes", tags=["Licitacoes"])

# Registrar todos os sub-routers
_sub_routers = [
    (tender_router, "tender"),
    (proposal_router, "proposal"),
    (contract_router, "contract"),
    (certificate_router, "certificate"),
    (document_router, "document"),
    (agent_router, "agent"),
    (sync_router, "sync"),
    (erp_router, "erp"),
    (opportunity_router, "opportunity"),
    (dispute_router, "dispute"),
]

# WebSocket para disputas em tempo real
router.include_router(dispute_ws_router, tags=["Disputas WebSocket"])

for sub_router, name in _sub_routers:
    try:
        router.include_router(sub_router)
        logger.debug("Licitacoes: router '%s' registrado com sucesso", name)
    except Exception as e:
        logger.error("Licitacoes: falha ao registrar router '%s': %s", name, e)


def get_router() -> APIRouter:
    """Retorna o router agregador do modulo de licitacoes."""
    return router


__all__ = [
    "router",
    "get_router",
]
