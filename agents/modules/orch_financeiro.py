"""Orquestrador Financeiro."""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
sys.path.insert(0, '/opt/conecta-pro/agents/modules')
from base_orchestrator import BaseOrchestrator
from fin_fiscal_agentes import (
    AgenteDashboardFinanceiro, AgenteContratos,
    AgenteContasPagar, AgenteContasReceber,
    AgenteFluxoCaixa, AgenteConciliacaoBancaria,
    AgenteBoletos, AgenteFornecedores,
    AgenteContabilidade, AgenteFaturamento,
    AgentePrecificacao, AgenteRelatoriosFinanceiros
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "financeiro"
    DESCRICAO = (
        "Contas, fluxo de caixa, "
        "compras e estoque"
    )
    AGENTES = [
        AgenteDashboardFinanceiro,
        AgenteContratos,
        AgenteContasPagar,
        AgenteContasReceber,
        AgenteFluxoCaixa,
        AgenteConciliacaoBancaria,
        AgenteBoletos,
        AgenteFornecedores,
        AgenteContabilidade,
        AgenteFaturamento,
        AgentePrecificacao,
        AgenteRelatoriosFinanceiros,
    ]
