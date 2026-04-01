"""
Controllers do modulo GED — Gestao Eletronica de Documentos.

Exporta todos os routers para registro no aggregator.
"""

from modules.people_management.ged.controllers.client_controller import router as client_router
from modules.people_management.ged.controllers.document_controller import router as document_router
from modules.people_management.ged.controllers.kit_controller import router as kit_router

__all__ = [
    "client_router",
    "document_router",
    "kit_router",
]
