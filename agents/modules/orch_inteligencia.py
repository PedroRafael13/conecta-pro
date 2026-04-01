"""
Orquestrador Inteligência Artificial.
Coordena 3 agentes: Bartolo core, módulos e aprendizado.
Monitora saúde do assistente IA e learning service.
"""
import sys

sys.path.insert(0, "/opt/conecta-pro/agents/core")
sys.path.insert(0, "/opt/conecta-pro/agents/modules")
from base_orchestrator import BaseOrchestrator  # noqa: E402
from extra_agentes import (  # noqa: E402
    AgenteAIAprendizado,
    AgenteAIBartolo,
    AgenteAIModulos,
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "inteligencia"
    DESCRICAO = "Bartolo IA, wizards, aprendizado e command center"
    AGENTES = [
        AgenteAIBartolo,
        AgenteAIModulos,
        AgenteAIAprendizado,
    ]
