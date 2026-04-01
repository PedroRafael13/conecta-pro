"""
Orquestrador Portais.
Coordena 3 agentes: portal clientes, governo/eSocial e CCT.
Monitora conformidade legal, gaps eSocial e portal do cliente.
"""
import sys

sys.path.insert(0, "/opt/conecta-pro/agents/core")
sys.path.insert(0, "/opt/conecta-pro/agents/modules")
from base_orchestrator import BaseOrchestrator  # noqa: E402
from extra_agentes import (  # noqa: E402
    AgenteCCTPortal,
    AgenteGovESocial,
    AgentePortalClientes,
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "portais"
    DESCRICAO = "Portal clientes, eSocial, CCT SINDECOMPRESTS e conformidade"
    AGENTES = [
        AgentePortalClientes,
        AgenteGovESocial,
        AgenteCCTPortal,
    ]
