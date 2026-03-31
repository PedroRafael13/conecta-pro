"""
Orquestrador Ponto Eletrônico.
Coordena 3 agentes: dashboard, justificativas e fechamento mensal.
Monitora inconsistências, colaboradores sem escala e banco de horas.
"""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
sys.path.insert(0, '/opt/conecta-pro/agents/modules')
from base_orchestrator import BaseOrchestrator
from dp_agentes import (
    AgenteDashboardPonto,
    AgenteJustificativas,
    AgenteFechamentoMensal,
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "ponto_eletronico"
    DESCRICAO = (
        "Batida de ponto, espelho, inconsistências, "
        "justificativas e fechamento mensal"
    )
    AGENTES = [
        AgenteDashboardPonto,
        AgenteJustificativas,
        AgenteFechamentoMensal,
    ]
