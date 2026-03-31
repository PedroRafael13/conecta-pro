"""Orquestrador GED."""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
sys.path.insert(0, '/opt/conecta-pro/agents/modules')
from base_orchestrator import BaseOrchestrator
from op_ged_agentes import (
    AgenteDashboardGED,
    AgenteClientesCondominios,
    AgenteKitsDocumentais,
    AgenteDocumentosGED,
    AgenteCertidoesEmpresa,
    AgenteEnviosGED,
    AgenteAssinaturasGED
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "ged"
    DESCRICAO = (
        "Gestão eletrônica de documentos "
        "e kits para clientes"
    )
    AGENTES = [
        AgenteDashboardGED,
        AgenteClientesCondominios,
        AgenteKitsDocumentais,
        AgenteDocumentosGED,
        AgenteCertidoesEmpresa,
        AgenteEnviosGED,
        AgenteAssinaturasGED
    ]


if __name__ == '__main__':
    import json
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(message)s'
    )
    orch = OrchestratorClass()
    resultado = orch.executar()
    print(json.dumps(resultado, indent=2,
                     default=str, ensure_ascii=False))
