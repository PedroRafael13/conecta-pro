"""Controllers do modulo Campo v3.0.0."""

# ===================================================================
# CONTROLLERS HERDADOS (Portaria Remota / Seguranca Fisica)
# ===================================================================
from .access_log_controller import router as access_log_router
from .equipment_status_controller import router as equipment_status_router
from .guardian_occurrence_controller import router as occurrence_router
from .guardian_sync_controller import router as sync_router

# ===================================================================
# CONTROLLERS DE SEGURANCA CIBERNETICA
# ===================================================================
from .security_audit_controller import router as security_audit_router
from .ssh_gateway_controller import router as ssh_gateway_router
from .campo_service_controller import router as campo_service_router

# ===================================================================
# SISTEMA DE MONITORAMENTO
# ===================================================================
from .monitoring_controller import router as monitoring_router

# ===================================================================
# NOVOS CONTROLLERS - CAMPO (OS, Visitas, Checklists)
# ===================================================================
from .ordem_servico_controller import router as ordem_servico_router
from .visita_controller import router as visita_router
from .checklist_controller import router as checklist_router
from .roteirizacao_controller import router as roteirizacao_router
from .estoque_controller import router as estoque_router

__all__ = [
    # Legacy controllers (Portaria Remota)
    "sync_router",
    "access_log_router",
    "occurrence_router",
    "equipment_status_router",
    # Cyber Security controllers
    "security_audit_router",
    "ssh_gateway_router",
    "campo_service_router",
    # Monitoring
    "monitoring_router",
    # CAMPO - OS, Visitas, Checklists
    "ordem_servico_router",
    "visita_router",
    "checklist_router",
    "roteirizacao_router",
    "estoque_router",
]

# Configuracao dos routers
GUARDIAN_ROUTERS = [
    # Seguranca Fisica (Legacy)
    {"router": sync_router, "prefix": "/guardian/sync", "tags": ["Physical Sync"]},
    {"router": access_log_router, "prefix": "/guardian/access", "tags": ["Access"]},
    {"router": occurrence_router, "prefix": "/guardian/occurrences", "tags": ["Events"]},
    {"router": equipment_status_router, "prefix": "/guardian/equipment", "tags": ["Equip"]},
    # Seguranca Cibernetica
    {"router": security_audit_router, "prefix": "/guardian/cyber", "tags": ["Cyber"]},
    {"router": ssh_gateway_router, "prefix": "/guardian/cyber", "tags": ["SSH"]},
    # CAMPO Service (legado)
    {"router": campo_service_router, "prefix": "/guardian/campo", "tags": ["Campo"]},
    # System Monitoring
    {"router": monitoring_router, "prefix": "", "tags": ["Monitoring"]},
]

# Routers do novo CAMPO
CAMPO_ROUTERS = [
    {"router": ordem_servico_router, "prefix": "/campo/os", "tags": ["Campo - Ordens de Servico"]},
    {"router": visita_router, "prefix": "/campo/visitas", "tags": ["Campo - Visitas"]},
    {"router": checklist_router, "prefix": "/campo/checklists", "tags": ["Campo - Checklists"]},
    {"router": roteirizacao_router, "prefix": "/campo/rotas", "tags": ["Campo - Roteirizacao"]},
    {"router": estoque_router, "prefix": "/campo/estoque", "tags": ["Campo - Estoque"]},
]
