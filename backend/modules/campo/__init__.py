"""
CAMPO v3.0.0 - Modulo de Servico de Campo do ERP Conecta PRO
============================================================

Sistema de Servico de Campo (estilo Auvo) para:
- Gestao de Equipes Tecnicas em Campo
- Visitas Tecnicas e Comerciais
- Ordens de Servico (OS)
- Tickets e Atendimentos
- Monitoramento de Equipamentos Instalados
- Sincronizacao com Sistemas Externos
- Checklists Dinamicos

Uso: Equipes externas trabalhando em clientes (condominios/empresas)
"""

__version__ = "3.0.0"
__module_name__ = "Campo"
__module_number__ = 21

# Imports dos controllers legados
# Imports dos novos controllers CAMPO
from modules.campo.controllers import (
    CAMPO_ROUTERS,
    access_log_router,
    campo_service_router,
    checklist_router,
    equipment_status_router,
    estoque_router,
    monitoring_router,
    occurrence_router,
    ordem_servico_router,
    roteirizacao_router,
    security_audit_router,
    sync_router,
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
    "occurrence_router",
    "equipment_status_router",
    "sync_router",
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
