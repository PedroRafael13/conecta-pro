"""
GUARDIAN UNIFIED v3.0.0 - Módulo 9 do ERP Conecta Mais
======================================================

Sistema Guardian Unificado combinando:
- Segurança Física (Portaria Remota)  
- Segurança Cibernética (Auditorias, SSH, Vulnerabilidades)
- Suporte CAMPO (Técnicos em campo)
- Monitoramento Unificado

Este módulo absorve e expande todas as funcionalidades do
antigo remote_gatehouse, adicionando capacidades completas
de segurança cibernética e suporte técnico.
"""

__version__ = "3.0.0"
__module_name__ = "Guardian Unified"
__module_number__ = 9

MODULE_CONFIG = {
    "name": "guardian",
    "version": __version__,
    "description": "Sistema Guardian Unificado - Segurança Física e Cibernética",
    "category": "security",
    "module_number": 9,
    "legacy_name": "remote_gatehouse", 
    "endpoints_prefix": "/api/v1/guardian",
    "components": {
        "physical_security": {
            "enabled": True,
            "legacy_controllers": ["guardian_sync", "guardian_occurrence", "access_log", "equipment_status"]
        },
        "cyber_security": {
            "enabled": True,
            "new_features": ["vulnerability_scanner", "ssh_gateway", "audit_service"]
        },
        "campo_service": {
            "enabled": True,
            "field_support": True
        },
        "unified_monitoring": {
            "enabled": True,
            "prometheus_metrics": True
        }
    }
}
