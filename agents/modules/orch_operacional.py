"""Orquestrador Operacional."""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
sys.path.insert(0, '/opt/conecta-pro/agents/modules')
from base_orchestrator import BaseOrchestrator
from op_ged_agentes import (
    AgentePostos, AgenteEscalas,
    AgenteAlocacoes, AgenteSubstituicoes,
    AgenteOcorrencias, AgenteProcessosDisciplinares,
    AgenteRondas, AgenteDiaristas,
    AgenteComunicados, AgenteCheckInOut,
    AgenteMonitoramentoCampo,
    AgenteKPITendencias, AgenteAICommandCenter
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "operacional"
    DESCRICAO = (
        "Postos, escalas, campo "
        "e inteligência operacional"
    )
    AGENTES = [
        AgentePostos, AgenteEscalas,
        AgenteAlocacoes, AgenteSubstituicoes,
        AgenteOcorrencias,
        AgenteProcessosDisciplinares,
        AgenteRondas, AgenteDiaristas,
        AgenteComunicados, AgenteCheckInOut,
        AgenteMonitoramentoCampo,
        AgenteKPITendencias, AgenteAICommandCenter
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
