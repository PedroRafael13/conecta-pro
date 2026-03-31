"""Orquestrador Negócios — Conecta PRO."""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
sys.path.insert(0, '/opt/conecta-pro/agents/modules')
from base_orchestrator import BaseOrchestrator
from outros_agentes import (
    AgenteCRM,
    AgenteFunilVendas,
    AgenteLicitacoes,
    AgenteServicos,
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "negocios"
    DESCRICAO = (
        "CRM, funil de vendas, "
        "licitações e serviços"
    )
    AGENTES = [
        AgenteCRM,
        AgenteFunilVendas,
        AgenteLicitacoes,
        AgenteServicos,
    ]
