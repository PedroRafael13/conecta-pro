"""
Orquestrador Negócios.
Coordena 3 agentes: leads, oportunidades/propostas e contratos/comissões.
Monitora pipeline CRM e licitações.
"""
import sys

sys.path.insert(0, "/opt/conecta-pro/agents/core")
sys.path.insert(0, "/opt/conecta-pro/agents/modules")
from base_orchestrator import BaseOrchestrator  # noqa: E402
from extra_agentes import (  # noqa: E402
    AgenteCRMContratos,
    AgenteCRMLeads,
    AgenteCRMOportunidades,
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "negocios"
    DESCRICAO = "CRM, leads, propostas, contratos e comissões"
    AGENTES = [
        AgenteCRMLeads,
        AgenteCRMOportunidades,
        AgenteCRMContratos,
    ]
