"""
Orquestrador Saúde Ocupacional.
Coordena 2 agentes: health-occupational status e PCMSO/ASO/SST.
Monitora ASOs vencidos, afastamentos e exames periódicos.
"""
import sys

sys.path.insert(0, "/opt/conecta-pro/agents/core")
sys.path.insert(0, "/opt/conecta-pro/agents/modules")
from base_orchestrator import BaseOrchestrator  # noqa: E402
from extra_agentes import AgentePCMSO, AgenteSaudeOcupacional  # noqa: E402


class OrchestratorClass(BaseOrchestrator):
    MODULO = "saude_ocupacional"
    DESCRICAO = "PCMSO, ASO, afastamentos, EPI e saúde do trabalhador"
    AGENTES = [
        AgenteSaudeOcupacional,
        AgentePCMSO,
    ]
