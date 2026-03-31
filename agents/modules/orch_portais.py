"""Orquestrador Portais — Conecta PRO."""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
sys.path.insert(0, '/opt/conecta-pro/agents/modules')
from base_orchestrator import BaseOrchestrator
from outros_agentes import (
    AgentePortalFuncionario,
    AgenteAreaCliente,
    AgenteMobile,
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "portais"
    DESCRICAO = (
        "Portal do funcionário, "
        "área do cliente e mobile API"
    )
    AGENTES = [
        AgentePortalFuncionario,
        AgenteAreaCliente,
        AgenteMobile,
    ]
