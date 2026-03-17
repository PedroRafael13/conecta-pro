"""
Aggregator GED — registra todos os routers do modulo GED.

Combina os controllers de clientes, kits e documentos em um
unico router com prefixo /ged para registro no app principal.
"""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ged", tags=["GED - Kits Documentais"])

try:
    from modules.people_management.ged.controllers.client_controller import router as client_router

    router.include_router(client_router)
    logger.info("GED: client_controller registrado")
except ImportError as e:
    logger.warning("GED: falha ao importar client_controller: %s", e)

try:
    from modules.people_management.ged.controllers.kit_controller import router as kit_router

    router.include_router(kit_router)
    logger.info("GED: kit_controller registrado")
except ImportError as e:
    logger.warning("GED: falha ao importar kit_controller: %s", e)

try:
    from modules.people_management.ged.controllers.document_controller import router as document_router

    router.include_router(document_router)
    logger.info("GED: document_controller registrado")
except ImportError as e:
    logger.warning("GED: falha ao importar document_controller: %s", e)

__all__ = ["router"]
