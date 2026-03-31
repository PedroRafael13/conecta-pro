"""Orquestrador Administrativo — Conecta PRO."""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
sys.path.insert(0, '/opt/conecta-pro/agents/modules')
from base_orchestrator import BaseOrchestrator
from outros_agentes import (
    AgenteIntegracoes,
    AgenteLGPD,
    AgenteWorkflows,
    AgenteConfiguracoes,
    AgenteAuditoria,
    AgenteNotificacoes,
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "administrativo"
    DESCRICAO = (
        "Integrações, LGPD, workflows, "
        "configurações, auditoria e notificações"
    )
    AGENTES = [
        AgenteIntegracoes,
        AgenteLGPD,
        AgenteWorkflows,
        AgenteConfiguracoes,
        AgenteAuditoria,
        AgenteNotificacoes,
    ]
