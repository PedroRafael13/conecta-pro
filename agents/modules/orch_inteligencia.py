"""Orquestrador Inteligência — Conecta PRO."""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
sys.path.insert(0, '/opt/conecta-pro/agents/modules')
from base_orchestrator import BaseOrchestrator
from outros_agentes import (
    AgenteDashboardsExecutivos,
    AgenteRelatoriosOperacionais,
    AgenteAnalytics,
    AgenteBartolo,
    AgenteMonitoramento,
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "inteligencia"
    DESCRICAO = (
        "Dashboards executivos, analytics, "
        "IA Bartolo e monitoramento"
    )
    AGENTES = [
        AgenteDashboardsExecutivos,
        AgenteRelatoriosOperacionais,
        AgenteAnalytics,
        AgenteBartolo,
        AgenteMonitoramento,
    ]
