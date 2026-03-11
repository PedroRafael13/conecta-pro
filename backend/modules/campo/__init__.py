"""
CAMPO v3.0.0 - Modulo de Servico de Campo do ERP Conecta PRO

DEPRECATED: Use 'modules.operacoes' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.
"""

import warnings

warnings.warn(
    "Importing from 'modules.campo' is deprecated. "
    "Use 'modules.operacoes' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

__version__ = "3.0.0"
__module_name__ = "Campo"
__module_number__ = 21

# Imports dos controllers legados
# Imports dos novos controllers CAMPO
from modules.campo.controllers import (  # noqa: E402
    CAMPO_ROUTERS,
    access_log_router,
    campo_service_router,
    checklist_router,
    equipment_status_router,
    estoque_router,
    monitoring_router,
    ordem_servico_router,
    roteirizacao_router,
    security_audit_router,
    visita_router,
)

MODULE_CONFIG = {
    "name": "campo",
    "version": __version__,
    "description": "Sistema de Servico de Campo - Equipes Externas, Visitas, OS e Checklists",
    "category": "operations",
    "module_number": 21,
    "endpoints_prefix": "/api/v1/campo",
    "components": {
        "ordens_servico": {
            "enabled": True,
            "description": "Gestao de Ordens de Servico",
            "features": ["criar", "agendar", "executar", "concluir", "avaliar"],
        },
        "visitas": {
            "enabled": True,
            "description": "Visitas Tecnicas e Comerciais",
            "features": ["agendamento", "checkin", "checkout", "conversao"],
        },
        "checklists": {
            "enabled": True,
            "description": "Checklists Dinamicos",
            "features": ["templates", "preenchimento", "validacao", "alertas"],
        },
        "campo_service": {
            "enabled": True,
            "description": "Gestao de tecnicos e equipes em campo",
            "features": ["technicians", "tickets", "scheduling", "visits"],
        },
        "equipment_monitoring": {
            "enabled": True,
            "description": "Status de equipamentos nos clientes",
            "features": ["status_tracking", "alerts", "reports"],
        },
        "access_logs": {
            "enabled": True,
            "description": "Logs de acesso e operacoes",
            "features": ["access_log", "occurrence_log", "sync_log"],
        },
        "external_sync": {
            "enabled": True,
            "description": "Sincronizacao com sistemas externos",
            "features": ["data_sync", "api_integration"],
        },
        "roteirizacao": {
            "enabled": True,
            "description": "Roteirizacao inteligente de rotas",
            "features": ["otimizacao", "reotimizacao", "analise_equipe", "redistribuicao"],
        },
        "estoque": {
            "enabled": True,
            "description": "Integracao com estoque para materiais",
            "features": ["requisicao", "baixa_automatica", "alertas", "relatorios"],
        },
    },
}

__all__ = [
    # Legado
    "campo_service_router",
    "access_log_router",
    "equipment_status_router",
    "security_audit_router",
    "monitoring_router",
    # Novos CAMPO
    "ordem_servico_router",
    "visita_router",
    "checklist_router",
    "roteirizacao_router",
    "estoque_router",
    "CAMPO_ROUTERS",
    # Config
    "MODULE_CONFIG",
]
