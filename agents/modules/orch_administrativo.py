"""
Orquestrador Administrativo.
Coordena 3 agentes: reembolsos, notificações e CCT admin.
Monitora reembolsos pendentes, notificações push e convenção coletiva.
"""
import sys

sys.path.insert(0, "/opt/conecta-pro/agents/core")
sys.path.insert(0, "/opt/conecta-pro/agents/modules")
from base_orchestrator import BaseOrchestrator  # noqa: E402
from extra_agentes import (  # noqa: E402
    AgenteCCTAdmin,
    AgenteNotificacoesAdmin,
    AgenteReembolsos,
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "administrativo"
    DESCRICAO = "Reembolsos, notificações, CCT e configurações admin"
    AGENTES = [
        AgenteReembolsos,
        AgenteNotificacoesAdmin,
        AgenteCCTAdmin,
    ]
