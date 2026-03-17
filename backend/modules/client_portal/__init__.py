"""
Portal do Cliente — Acesso externo para clientes de condominios.

Permite que clientes acessem seus kits documentais, abram tickets
de suporte e gerenciem suas sessoes atraves de um portal autenticado
separado do sistema interno.
"""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/portal", tags=["Client Portal"])

try:
    from .controllers.auth_controller import router as auth_router

    router.include_router(auth_router)
    logger.info("Portal: auth_controller registrado")
except ImportError as e:
    logger.warning("Portal: falha ao importar auth_controller: %s", e)

try:
    from .controllers.kit_controller import router as kit_router

    router.include_router(kit_router)
    logger.info("Portal: kit_controller registrado")
except ImportError as e:
    logger.warning("Portal: falha ao importar kit_controller: %s", e)

try:
    from .controllers.ticket_controller import router as ticket_router

    router.include_router(ticket_router)
    logger.info("Portal: ticket_controller registrado")
except ImportError as e:
    logger.warning("Portal: falha ao importar ticket_controller: %s", e)

__all__ = ["router"]
