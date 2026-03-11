"""
Módulo TÉCNICO — Agregador
Unifica: equipment_management + document_kits

Routers re-exportados dos módulos de implementação.
API URLs inalteradas.
Data migração: 2026-03-11
"""

# --- Equipment Management ---
# --- Document Kits ---
from modules.document_kits.controllers import router as document_kit_router
from modules.equipment_management.controllers import (
    comodato_router,
    equipment_router,
    installation_router,
)
from modules.equipment_management.controllers import (
    maintenance_router as equipment_maintenance_router,
)

__all__ = [
    "equipment_router",
    "installation_router",
    "equipment_maintenance_router",
    "comodato_router",
    "document_kit_router",
]
