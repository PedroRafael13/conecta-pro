"""
Orquestrador Recursos Humanos.
Coordena 5 agentes: carreira, clima, turnover,
time-tracking e payroll RH.
"""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
sys.path.insert(0, '/opt/conecta-pro/agents/modules')
from base_orchestrator import BaseOrchestrator
from dp_agentes import (
    AgenteCarreira,
    AgenteClima,
    AgenteTurnover,
    AgenteTimeTracking,
    AgentePayroll,
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "recursos_humanos"
    DESCRICAO = (
        "Carreira, clima organizacional, turnover, "
        "time-tracking e payroll"
    )
    AGENTES = [
        AgenteCarreira,
        AgenteClima,
        AgenteTurnover,
        AgenteTimeTracking,
        AgentePayroll,
    ]
