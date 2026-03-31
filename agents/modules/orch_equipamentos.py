"""Orquestrador Equipamentos — Conecta PRO."""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
sys.path.insert(0, '/opt/conecta-pro/agents/modules')
from base_orchestrator import BaseOrchestrator
from outros_agentes import (
    AgentePatrimonio,
    AgenteComodatos,
    AgenteManutencoes,
    AgenteDocumentKits,
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "equipamentos"
    DESCRICAO = (
        "Patrimônio, comodatos, "
        "manutenções e document kits"
    )
    AGENTES = [
        AgentePatrimonio,
        AgenteComodatos,
        AgenteManutencoes,
        AgenteDocumentKits,
    ]
