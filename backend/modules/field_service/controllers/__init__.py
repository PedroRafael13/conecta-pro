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

# ===================================================================
# SISTEMA DE MONITORAMENTO
# ===================================================================
from .monitoring_controller import router as monitoring_router

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
    # Monitoring
    "monitoring_router",
]

# Configuração dos routers
GUARDIAN_ROUTERS = [
    # Segurança Física (Legacy)
    {"router": sync_router, "prefix": "/guardian/sync", "tags": ["Physical Sync"]},
    {"router": access_log_router, "prefix": "/guardian/access", "tags": ["Access"]},
    {"router": occurrence_router, "prefix": "/guardian/occurrences", "tags": ["Events"]},
    {"router": equipment_status_router, "prefix": "/guardian/equipment", "tags": ["Equip"]},
    # Segurança Cibernética
    {"router": security_audit_router, "prefix": "/guardian/cyber", "tags": ["Cyber"]},
    {"router": ssh_gateway_router, "prefix": "/guardian/cyber", "tags": ["SSH"]},
    # CAMPO Service
    {"router": campo_service_router, "prefix": "/guardian/campo", "tags": ["Campo"]},
    # System Monitoring
    {"router": monitoring_router, "prefix": "", "tags": ["Monitoring"]},
]
