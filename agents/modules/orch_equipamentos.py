"""Orquestrador equipamentos."""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
sys.path.insert(0, '/opt/conecta-pro/agents/modules')
from base_orchestrator import BaseOrchestrator
from outros_agentes import *

_AGENTES_MAP = {
    'inteligencia': [
        AgenteDashboardsExecutivos,
        AgenteRelatoriosOperacionais,
        AgenteAnalytics
    ],
    'negocios': [
        AgenteCRM,
        AgenteFunilVendas,
        AgenteLicitacoes
    ],
    'saude_ocupacional': [
        AgenteExamesASOs, AgenteEPIs,
        AgenteRiscos, AgenteAfastamentos,
        AgenteCAT
    ],
    'portais': [
        AgentePortalFuncionario,
        AgenteAreaCliente
    ],
    'equipamentos': [
        AgentePatrimonio,
        AgenteComodatos,
        AgenteManutencoes
    ],
    'administrativo': [
        AgenteIntegracoes, AgenteLGPD,
        AgenteWorkflows, AgenteConfiguracoes
    ]
}

class OrchestratorClass(BaseOrchestrator):
    MODULO = "equipamentos"
    AGENTES = _AGENTES_MAP['equipamentos']
