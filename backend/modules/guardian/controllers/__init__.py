"""Controllers do Guardian Unified v3.0.0 - Módulo 9."""

# ===================================================================
# CONTROLLERS HERDADOS (Portaria Remota / Segurança Física) 
# ===================================================================
from .access_log_controller import router as access_log_router
from .equipment_status_controller import router as equipment_status_router
from .guardian_occurrence_controller import router as occurrence_router
from .guardian_sync_controller import router as sync_router

# ===================================================================
# NOVOS CONTROLLERS (Segurança Cibernética + CAMPO)
# ===================================================================
from .security_audit_controller import router as security_audit_router
from .ssh_gateway_controller import router as ssh_gateway_router
from .campo_service_controller import router as campo_service_router

__all__ = [
    # Legacy controllers (Portaria Remota)
    "sync_router",
    "access_log_router", 
    "occurrence_router",
    "equipment_status_router",
    # New controllers (Cyber Security + CAMPO)
    "security_audit_router",
    "ssh_gateway_router",
    "campo_service_router",
]

# Configuração dos routers
GUARDIAN_ROUTERS = [
    # Segurança Física (Legacy)
    {"router": sync_router, "prefix": "/guardian/sync", "tags": ["Guardian - Physical Sync"]},
    {"router": access_log_router, "prefix": "/guardian/access", "tags": ["Guardian - Physical Access"]},
    {"router": occurrence_router, "prefix": "/guardian/occurrences", "tags": ["Guardian - Physical Events"]},
    {"router": equipment_status_router, "prefix": "/guardian/equipment", "tags": ["Guardian - Equipment Status"]},
    # Segurança Cibernética
    {"router": security_audit_router, "prefix": "/guardian/cyber", "tags": ["Guardian - Cyber Security"]},
    {"router": ssh_gateway_router, "prefix": "/guardian/cyber", "tags": ["Guardian - SSH Gateway"]},
    # CAMPO Service
    {"router": campo_service_router, "prefix": "/guardian/campo", "tags": ["Guardian - Field Service"]},
]
