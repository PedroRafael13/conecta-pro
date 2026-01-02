"""
FIELD SERVICE v3.0.0 - Módulo de Serviço de Campo do ERP Conecta Mais
=====================================================================

Sistema de Serviço de Campo combinando:
- Suporte Técnico em Campo (Técnicos, Tickets, Atendimentos)
- Monitoramento de Status de Equipamentos Instalados
- Logs de Acesso e Ocorrências de Campo
- Sincronização com Sistemas Externos

Este módulo gerencia todas as operações de campo da empresa,
incluindo instalações, manutenções e suporte técnico.
"""

__version__ = "3.0.0"
__module_name__ = "Field Service"
__module_number__ = 21

MODULE_CONFIG = {
    "name": "field_service",
    "version": __version__,
    "description": "Sistema de Serviço de Campo - Suporte Técnico e Atendimentos",
    "category": "operations",
    "module_number": 21,
    "endpoints_prefix": "/api/v1/field-service",
    "components": {
        "campo_service": {
            "enabled": True,
            "description": "Gestão de técnicos em campo",
            "features": ["technicians", "tickets", "scheduling"]
        },
        "equipment_monitoring": {
            "enabled": True,
            "description": "Status de equipamentos instalados",
            "features": ["status_tracking", "alerts", "reports"]
        },
        "access_logs": {
            "enabled": True,
            "description": "Logs de acesso e operações",
            "features": ["access_log", "occurrence_log", "sync_log"]
        },
        "external_sync": {
            "enabled": True,
            "description": "Sincronização com sistemas externos",
            "features": ["data_sync", "api_integration"]
        }
    }
}
