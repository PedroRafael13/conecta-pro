"""Orquestrador Saúde Ocupacional — Conecta PRO."""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
sys.path.insert(0, '/opt/conecta-pro/agents/modules')
from base_orchestrator import BaseOrchestrator
from outros_agentes import (
    AgenteExamesASOs,
    AgenteEPIs,
    AgenteRiscos,
    AgenteAfastamentos,
    AgenteCAT,
    AgenteNRs,
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "saude_ocupacional"
    DESCRICAO = (
        "ASOs, EPIs, riscos PPRA/PCMSO, "
        "afastamentos, CAT e NRs"
    )
    AGENTES = [
        AgenteExamesASOs,
        AgenteEPIs,
        AgenteRiscos,
        AgenteAfastamentos,
        AgenteCAT,
        AgenteNRs,
    ]
