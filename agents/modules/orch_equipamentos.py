"""
Orquestrador Equipamentos.
Coordena 2 agentes: inventário e manutenção.
Monitora equipamentos em estoque e pendentes de manutenção.
Bug conhecido: GET /equipment/stats retorna 500 (model/DB divergência).
"""
import sys

sys.path.insert(0, "/opt/conecta-pro/agents/core")
sys.path.insert(0, "/opt/conecta-pro/agents/modules")
from base_orchestrator import BaseOrchestrator  # noqa: E402
from extra_agentes import (  # noqa: E402
    AgenteEquipamentos,
    AgenteEquipamentosManutencao,
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "equipamentos"
    DESCRICAO = "Equipamentos, instalações, manutenção e comodato"
    AGENTES = [
        AgenteEquipamentos,
        AgenteEquipamentosManutencao,
    ]
